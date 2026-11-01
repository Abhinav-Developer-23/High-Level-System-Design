#!/usr/bin/env python3
"""Gmail MCP server — STRICTLY READ-ONLY.

Reads the mailbox of the signed-in Google Workspace user
(abhinav.anand@finmate.tech) through the OAuth client "agent-debugger-readonly"
(GCP project lofty-flare-497007-c9, audience Internal).

Tools (ALL read-only):
  - check_connection  — mailbox address, message/thread totals, granted scope
  - list_labels       — labels with unread/total counts
  - search_messages   — Gmail search syntax (from:, subject:, newer_than:, label:, has:attachment …)
  - get_message       — one message: headers, plain-text body, attachment list
  - get_thread        — every message of a thread, oldest first
  - get_attachment    — download one attachment into tmp/gmail_attachments/

=== WHY THIS SERVER CANNOT CHANGE ANYTHING ===

1. The OAuth token carries exactly one scope, gmail.readonly, so Google itself
   rejects send, modify (mark read, label), trash, delete, drafts and settings.
   A token carrying any other scope is refused at load time and never saved.
2. Every API call goes through _get(): HTTP GET only, the URL must fullmatch an
   anchored allowlist of read endpoints under users/me, path IDs admit only
   [A-Za-z0-9_-], redirects are disabled. The only POST in the file is to
   Google's OAuth token endpoint (code exchange / refresh).

Credentials come from Agent-debugger/.env (gitignored, 0600):
  GOOGLE_WORKSPACE_CLIENT_ID, GOOGLE_WORKSPACE_CLIENT_SECRET — shared OAuth desktop client
  GMAIL_READONLY_REFRESH_TOKEN, GMAIL_READONLY_SCOPES        — written by `auth`

One-time sign-in (opens a browser consent page, writes the refresh token into .env):

    .venv/bin/python3 src/shared/mcp/gmail_readonly_mcp.py auth
"""

import base64
import hashlib
import html
import http.server
import json
import logging
import os
import re
import secrets
import ssl
import sys
import threading
import time
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, quote, urlencode, urlparse

import httpx
import truststore
from dotenv import dotenv_values
from mcp.server.fastmcp import FastMCP

logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.disable(logging.INFO)

_ROOT = Path(__file__).resolve().parents[3]
# Explicit path: the MCP host launches this with an arbitrary cwd.
ENV_PATH = _ROOT / ".env"
ATTACH_DIR = _ROOT / "tmp" / "gmail_attachments"

SCOPES = ("https://www.googleapis.com/auth/gmail.readonly",)
# Google adds these identity scopes on its own when they were granted earlier.
_HARMLESS_SCOPES = {"openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"}

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://gmail.googleapis.com/gmail/v1/users/me"
TIMEOUT = 60.0
MAX_CHARS = 150_000
MAX_BODY_CHARS = 40_000
# Zscaler re-signs googleapis.com; its root is only in the macOS keychain.
_TLS = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


# ---------------------------------------------------------------------------
# Read-only allowlist
# ---------------------------------------------------------------------------

# Message/thread ids are hex, so words like "send" or "trash" can never pass as an id.
_HEX = r"[0-9a-fA-F]{8,32}"
_LABEL = r"[A-Za-z0-9_-]{1,200}"
_ATT = r"[A-Za-z0-9_-]{1,4000}"
_API_RE = re.escape(API)
_GET_RE = re.compile(
    "|".join(
        f"(?:{_API_RE}{p})"
        for p in (
            r"/profile",
            r"/labels",
            rf"/labels/{_LABEL}",
            r"/messages",
            rf"/messages/{_HEX}",
            rf"/messages/{_HEX}/attachments/{_ATT}",
            r"/threads",
            rf"/threads/{_HEX}",
        )
    )
)


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

def _env() -> dict:
    """.env re-read on every token refresh, so a fresh `auth` needs no MCP restart."""
    values = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}
    return {k: os.environ.get(k) or values.get(k) or "" for k in (
        "GOOGLE_WORKSPACE_CLIENT_ID", "GOOGLE_WORKSPACE_CLIENT_SECRET",
        "GMAIL_READONLY_REFRESH_TOKEN", "GMAIL_READONLY_SCOPES",
    )}


def _load_client() -> dict:
    env = _env()
    if not env["GOOGLE_WORKSPACE_CLIENT_ID"] or not env["GOOGLE_WORKSPACE_CLIENT_SECRET"]:
        raise RuntimeError(f"GOOGLE_WORKSPACE_CLIENT_ID / GOOGLE_WORKSPACE_CLIENT_SECRET not set in {ENV_PATH}")
    return {"client_id": env["GOOGLE_WORKSPACE_CLIENT_ID"], "client_secret": env["GOOGLE_WORKSPACE_CLIENT_SECRET"]}


def _check_scopes(scope_str: str) -> list[str]:
    granted = set(scope_str.split())
    extra = granted - set(SCOPES) - _HARMLESS_SCOPES
    if extra:
        raise RuntimeError(f"Refusing token: it carries non-read-only scopes {sorted(extra)}")
    if not granted & set(SCOPES):
        raise RuntimeError("Refusing token: gmail.readonly was not granted")
    return sorted(granted)


def _set_env_keys(updates: dict[str, str]) -> None:
    """Replace or append KEY=value lines in .env, keeping every other line and mode 0600."""
    lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
    pending = dict(updates)
    for i, line in enumerate(lines):
        key = line.split("=", 1)[0].strip().removeprefix("export ").strip()
        if key in pending:
            lines[i] = f"{key}={pending.pop(key)}"
    lines.extend(f"{k}={v}" for k, v in pending.items())
    fd = os.open(ENV_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(ENV_PATH, 0o600)


def _token_post(data: dict) -> dict:
    """The only POST in this server: Google's OAuth token endpoint."""
    with httpx.Client(timeout=TIMEOUT, verify=_TLS, follow_redirects=False) as c:
        r = c.post(TOKEN_URL, data=data)
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    if r.status_code != 200:
        raise RuntimeError(f"OAuth token endpoint HTTP {r.status_code}: {body.get('error')} {body.get('error_description', '')}".strip())
    return body


class _Creds:
    def __init__(self) -> None:
        self._access: str | None = None
        self._expiry = 0.0
        self._lock = threading.Lock()
        self.scopes: list[str] = []

    def access_token(self, force: bool = False) -> str:
        with self._lock:
            if self._access and not force and time.time() < self._expiry - 60:
                return self._access
            env = _env()
            if not env["GMAIL_READONLY_REFRESH_TOKEN"]:
                raise RuntimeError(
                    f"Not signed in (GMAIL_READONLY_REFRESH_TOKEN missing in {ENV_PATH}). Run once: "
                    ".venv/bin/python3 src/shared/mcp/gmail_readonly_mcp.py auth"
                )
            _check_scopes(env["GMAIL_READONLY_SCOPES"])
            client = _load_client()
            body = _token_post({
                "client_id": client["client_id"],
                "client_secret": client["client_secret"],
                "refresh_token": env["GMAIL_READONLY_REFRESH_TOKEN"],
                "grant_type": "refresh_token",
            })
            self.scopes = _check_scopes(body.get("scope", env["GMAIL_READONLY_SCOPES"]))
            self._access = body["access_token"]
            self._expiry = time.time() + int(body.get("expires_in", 3600))
            return self._access


_CREDS = _Creds()


# ---------------------------------------------------------------------------
# HTTP — GET only
# ---------------------------------------------------------------------------

def _get(url: str, params=None) -> dict:
    if not _GET_RE.fullmatch(url):
        raise PermissionError(f"Refused: {url} is not an allowlisted Gmail read endpoint")
    for attempt in range(2):
        headers = {"Authorization": f"Bearer {_CREDS.access_token(force=attempt > 0)}"}
        with httpx.Client(timeout=TIMEOUT, verify=_TLS, follow_redirects=False) as c:
            r = c.get(url, params=params, headers=headers)
        if r.status_code == 401 and attempt == 0:
            continue
        break
    if r.status_code >= 300:
        try:
            err = r.json().get("error", {})
            msg = err.get("message") if isinstance(err, dict) else str(err)
        except Exception:
            msg = r.text[:500]
        raise RuntimeError(f"Gmail API HTTP {r.status_code}: {msg}")
    return r.json()


def _cap(obj) -> str:
    text = obj if isinstance(obj, str) else json.dumps(obj, indent=2, ensure_ascii=False, default=str)
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS] + f"\n... [truncated {len(text) - MAX_CHARS} chars — narrow the search or lower limit]"
    return text


def _err(e: Exception) -> str:
    return json.dumps({"error": f"{type(e).__name__}: {e}"})


def _check_id(value: str, what: str) -> str:
    value = value.strip()
    if not re.fullmatch(_LABEL if what == "label" else _HEX, value):
        raise ValueError(f"Not a Gmail {what} id: {value!r}")
    return value


# ---------------------------------------------------------------------------
# Message decoding
# ---------------------------------------------------------------------------

_SUMMARY_HEADERS = ("From", "To", "Cc", "Subject", "Date")


def _headers(payload: dict, names=_SUMMARY_HEADERS) -> dict:
    wanted = {n.lower(): n for n in names}
    out = {}
    for h in payload.get("headers", []):
        key = wanted.get(h.get("name", "").lower())
        if key:
            out[key] = h.get("value", "")
    return out


def _b64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def _walk(part: dict):
    yield part
    for p in part.get("parts", []) or []:
        yield from _walk(p)


def _html_to_text(s: str) -> str:
    s = re.sub(r"(?is)<(script|style|head).*?</\1>", "", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</li>|</h\d>", "\n", s)
    s = re.sub(r"(?i)</td>|</th>", " | ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", re.sub(r"[ \t\r\f\v]+", " ", s)).strip()


def _body_and_attachments(payload: dict) -> tuple[str, str, list[dict]]:
    plain, htmls, attachments = [], [], []
    for p in _walk(payload):
        mime = p.get("mimeType", "")
        body = p.get("body", {}) or {}
        if p.get("filename"):
            attachments.append({
                "filename": p["filename"],
                "mime_type": mime,
                "size": body.get("size"),
                "attachment_id": body.get("attachmentId"),
            })
        elif body.get("data") and mime == "text/plain":
            plain.append(_b64(body["data"]).decode("utf-8", errors="replace"))
        elif body.get("data") and mime == "text/html":
            htmls.append(_b64(body["data"]).decode("utf-8", errors="replace"))
    if plain:
        text, source = "\n".join(plain), "text/plain"
    elif htmls:
        text, source = _html_to_text("\n".join(htmls)), "text/html (converted)"
    else:
        text, source = "", "none"
    if len(text) > MAX_BODY_CHARS:
        text = text[:MAX_BODY_CHARS] + f"\n... [body truncated, {len(text) - MAX_BODY_CHARS} more chars]"
    return text, source, attachments


def _message_view(msg: dict, include_body: bool = True) -> dict:
    payload = msg.get("payload", {})
    out = {
        "id": msg.get("id"),
        "thread_id": msg.get("threadId"),
        "labels": msg.get("labelIds", []),
        **_headers(payload),
        "snippet": html.unescape(msg.get("snippet", "")),
    }
    if include_body:
        body, source, attachments = _body_and_attachments(payload)
        out.update({"body_source": source, "body": body, "attachments": attachments})
    return out


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

mcp = FastMCP("gmail_readonly")


@mcp.tool()
def check_connection() -> str:
    """Verify the Gmail sign-in: mailbox address, message/thread totals, granted (read-only) scope."""
    try:
        profile = _get(f"{API}/profile")
        return _cap({"ok": True, **profile, "scopes": _CREDS.scopes, "read_only": True, "credentials": str(ENV_PATH)})
    except Exception as e:
        return _err(e)


@mcp.tool()
def list_labels(include_counts: bool = False) -> str:
    """Gmail labels (system + user). include_counts=True adds total/unread message counts (one call per label)."""
    try:
        labels = _get(f"{API}/labels").get("labels", [])
        if include_counts:
            labels = [_get(f"{API}/labels/{_check_id(l['id'], 'label')}") for l in labels]
        keep = ("id", "name", "type", "messagesTotal", "messagesUnread", "threadsTotal", "threadsUnread")
        return _cap(sorted(({k: l[k] for k in keep if k in l} for l in labels), key=lambda l: (l.get("type") != "system", l.get("name", ""))))
    except Exception as e:
        return _err(e)


@mcp.tool()
def search_messages(query: str = "", limit: int = 20, label: str = "", include_spam_trash: bool = False) -> str:
    """Search the mailbox with Gmail search syntax, newest first; returns headers + snippet per message.

    query examples: "from:alerts@zenduty.com newer_than:2d", "subject:(on-call) is:unread",
                    "has:attachment filename:pdf after:2026/09/01".
    label: restrict to one label id (e.g. INBOX, SENT, IMPORTANT, or a Label_… id from list_labels).
    Use get_message / get_thread for full bodies.
    """
    try:
        params = [("maxResults", max(1, min(limit, 100))), ("includeSpamTrash", str(include_spam_trash).lower())]
        if query:
            params.append(("q", query))
        if label:
            params.append(("labelIds", _check_id(label, "label")))
        listing = _get(f"{API}/messages", params)
        refs = listing.get("messages", [])
        meta = [("format", "metadata")] + [("metadataHeaders", h) for h in _SUMMARY_HEADERS]
        messages = [
            _message_view(_get(f"{API}/messages/{_check_id(m['id'], 'message')}", meta), include_body=False)
            for m in refs
        ]
        return _cap({
            "count": len(messages),
            "result_size_estimate": listing.get("resultSizeEstimate"),
            "more_results": bool(listing.get("nextPageToken")),
            "messages": messages,
        })
    except Exception as e:
        return _err(e)


@mcp.tool()
def get_message(message_id: str, include_all_headers: bool = False) -> str:
    """One message: From/To/Cc/Subject/Date, labels, plain-text body (HTML converted when no text part),
    and attachment list (use get_attachment to download one). Reading does not mark it read."""
    try:
        msg = _get(f"{API}/messages/{_check_id(message_id, 'message')}", {"format": "full"})
        out = _message_view(msg)
        if include_all_headers:
            out["all_headers"] = msg.get("payload", {}).get("headers", [])
        return _cap(out)
    except Exception as e:
        return _err(e)


@mcp.tool()
def get_thread(thread_id: str, max_messages: int = 25) -> str:
    """Every message of a thread (oldest first) with bodies. max_messages keeps the newest N when the thread is long."""
    try:
        thread = _get(f"{API}/threads/{_check_id(thread_id, 'thread')}", {"format": "full"})
        msgs = thread.get("messages", [])
        shown = msgs[-max(1, max_messages):]
        return _cap({
            "thread_id": thread.get("id"),
            "message_count": len(msgs),
            "omitted_older": len(msgs) - len(shown),
            "messages": [_message_view(m) for m in shown],
        })
    except Exception as e:
        return _err(e)


@mcp.tool()
def get_attachment(message_id: str, attachment_id: str, filename: str = "") -> str:
    """Download one attachment (ids from get_message) to Agent-debugger/tmp/gmail_attachments/ (0600). Returns the path."""
    try:
        mid = _check_id(message_id, "message")
        if not re.fullmatch(_ATT, attachment_id.strip()):
            raise ValueError("Not a Gmail attachment id")
        data = _get(f"{API}/messages/{mid}/attachments/{attachment_id.strip()}")
        raw = _b64(data.get("data", ""))
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(filename).name).strip("._") or "attachment"
        ATTACH_DIR.mkdir(parents=True, exist_ok=True)
        path = ATTACH_DIR / f"{mid}_{safe}"
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
        return _cap({"saved_to": str(path), "bytes": len(raw)})
    except Exception as e:
        return _err(e)


# ---------------------------------------------------------------------------
# One-time sign-in (CLI only — never reachable from an MCP tool)
# ---------------------------------------------------------------------------

def _auth(open_browser: bool = True) -> None:
    client = _load_client()
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(24)
    result: dict = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            qs = parse_qs(urlparse(self.path).query)
            if (qs.get("state") or [None])[0] != state:
                self.send_response(400); self.end_headers(); self.wfile.write(b"State mismatch."); return
            result["code"] = (qs.get("code") or [None])[0]
            result["error"] = (qs.get("error") or [None])[0]
            self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
            self.wfile.write(b"<h3>Agent-debugger Gmail read-only sign-in complete. You can close this tab.</h3>")

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    redirect_uri = f"http://127.0.0.1:{server.server_port}"
    url = AUTH_URL + "?" + urlencode({
        "client_id": client["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }, quote_via=quote)
    print(f"Open this URL to sign in (gmail.readonly only):\n{url}\n", flush=True)
    if open_browser:
        webbrowser.open(url)
    server.timeout = 600
    while "code" not in result and "error" not in result:
        server.handle_request()
    server.server_close()
    if result.get("error") or not result.get("code"):
        raise SystemExit(f"Sign-in failed: {result.get('error')}")
    body = _token_post({
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "code": result["code"],
        "code_verifier": verifier,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    })
    scopes = _check_scopes(body.get("scope", ""))
    if not body.get("refresh_token"):
        raise SystemExit("Google returned no refresh token; rerun auth.")
    _set_env_keys({
        "GMAIL_READONLY_REFRESH_TOKEN": body["refresh_token"],
        "GMAIL_READONLY_SCOPES": f'"{" ".join(scopes)}"',
    })
    print(f"Signed in. Scopes: {scopes}\nRefresh token saved to {ENV_PATH} (0600).", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        _auth(open_browser="--no-browser" not in sys.argv)
    else:
        mcp.run()
