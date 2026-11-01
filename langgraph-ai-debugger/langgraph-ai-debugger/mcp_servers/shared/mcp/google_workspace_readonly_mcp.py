#!/usr/bin/env python3
"""Google Docs / Sheets / Drive MCP server — STRICTLY READ-ONLY.

Reads Google Docs, Google Sheets and Drive file metadata for the signed-in
Google Workspace user (abhinav.anand@finmate.tech, OAuth client
"agent-debugger-readonly" in GCP project lofty-flare-497007-c9, audience Internal).

Tools (ALL read-only):
  - check_connection   — who is signed in, which scopes the token holds
  - search_files       — find Docs/Sheets/files by name or full text
  - get_file_metadata  — one file's metadata (owner, modified, link, mime type)
  - list_sheet_tabs    — tabs of a spreadsheet: title, gid, row/column count
  - read_sheet         — cell values of one or more A1 ranges / whole tabs
  - read_doc           — plain text of a Google Doc (all document tabs, tables flattened)
  - export_file        — Drive export: Doc → txt/md/html, Sheet → csv (one tab), optionally saved under tmp/

=== WHY THIS SERVER CANNOT CHANGE ANYTHING ===

1. The OAuth token is minted with exactly three scopes —
   drive.readonly, spreadsheets.readonly, documents.readonly — so Google itself
   rejects any write. A token carrying any other scope is refused at load time
   and is never saved by the auth flow.
2. Every API call goes through _get(): HTTP GET only, the URL must fullmatch an
   anchored allowlist of read endpoints, path IDs admit only [A-Za-z0-9_-],
   redirects are disabled. The only POST in the file is to Google's OAuth token
   endpoint (code exchange / refresh).

Credentials come from Agent-debugger/.env (gitignored, 0600):
  GOOGLE_WORKSPACE_CLIENT_ID, GOOGLE_WORKSPACE_CLIENT_SECRET — OAuth desktop client
  GOOGLE_WORKSPACE_REFRESH_TOKEN, GOOGLE_WORKSPACE_SCOPES     — written by `auth`

One-time sign-in (opens a browser consent page, writes the refresh token into .env):

    .venv/bin/python3 src/shared/mcp/google_workspace_readonly_mcp.py auth
"""

import base64
import hashlib
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
from datetime import datetime, timezone
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
EXPORT_DIR = _ROOT / "tmp" / "google_exports"

SCOPES = (
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
)
# Google adds these identity scopes on its own when they were granted earlier.
_HARMLESS_SCOPES = {"openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"}

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
TIMEOUT = 60.0
MAX_CHARS = 150_000
# Zscaler re-signs googleapis.com; its root is only in the macOS keychain.
_TLS = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


def _log(msg: str) -> None:
    print(f"\033[96m{msg}\033[0m", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Read-only allowlist
# ---------------------------------------------------------------------------

_ID = r"[A-Za-z0-9_-]{10,200}"
_RANGE = r"[A-Za-z0-9%._~-]{1,500}"  # percent-encoded A1 range
_GET_RE = re.compile(
    "|".join(
        f"(?:{p})"
        for p in (
            r"https://www\.googleapis\.com/drive/v3/about",
            r"https://www\.googleapis\.com/drive/v3/files",
            rf"https://www\.googleapis\.com/drive/v3/files/{_ID}",
            rf"https://www\.googleapis\.com/drive/v3/files/{_ID}/export",
            rf"https://sheets\.googleapis\.com/v4/spreadsheets/{_ID}",
            rf"https://sheets\.googleapis\.com/v4/spreadsheets/{_ID}/values:batchGet",
            rf"https://sheets\.googleapis\.com/v4/spreadsheets/{_ID}/values/{_RANGE}",
            rf"https://docs\.googleapis\.com/v1/documents/{_ID}",
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
        "GOOGLE_WORKSPACE_REFRESH_TOKEN", "GOOGLE_WORKSPACE_SCOPES",
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
        raise RuntimeError("Refusing token: none of the read-only scopes were granted")
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
            if not env["GOOGLE_WORKSPACE_REFRESH_TOKEN"]:
                raise RuntimeError(
                    f"Not signed in (GOOGLE_WORKSPACE_REFRESH_TOKEN missing in {ENV_PATH}). Run once: "
                    ".venv/bin/python3 src/shared/mcp/google_workspace_readonly_mcp.py auth"
                )
            _check_scopes(env["GOOGLE_WORKSPACE_SCOPES"])
            client = _load_client()
            body = _token_post({
                "client_id": client["client_id"],
                "client_secret": client["client_secret"],
                "refresh_token": env["GOOGLE_WORKSPACE_REFRESH_TOKEN"],
                "grant_type": "refresh_token",
            })
            self.scopes = _check_scopes(body.get("scope", env["GOOGLE_WORKSPACE_SCOPES"]))
            self._access = body["access_token"]
            self._expiry = time.time() + int(body.get("expires_in", 3600))
            return self._access


_CREDS = _Creds()


# ---------------------------------------------------------------------------
# HTTP — GET only
# ---------------------------------------------------------------------------

def _get(url: str, params: dict | None = None, *, raw: bool = False):
    if not _GET_RE.fullmatch(url):
        raise PermissionError(f"Refused: {url} is not an allowlisted read endpoint")
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
        raise RuntimeError(f"Google API HTTP {r.status_code}: {msg}")
    return r if raw else r.json()


def _cap(obj) -> str:
    text = obj if isinstance(obj, str) else json.dumps(obj, indent=2, ensure_ascii=False, default=str)
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS] + f"\n... [truncated {len(text) - MAX_CHARS} chars — narrow the range or use export_file(save_to_tmp=True)]"
    return text


def _err(e: Exception) -> str:
    return json.dumps({"error": f"{type(e).__name__}: {e}"})


_ID_IN_URL = re.compile(r"/d/(?:e/)?([A-Za-z0-9_-]{10,200})")


def _parse_ref(ref: str) -> tuple[str, int | None]:
    """File ID (or Docs/Sheets/Drive URL) → (file_id, gid from the URL if any)."""
    ref = ref.strip()
    gid = None
    if ref.startswith("http"):
        u = urlparse(ref)
        m = _ID_IN_URL.search(u.path)
        qs = parse_qs(u.query)
        frag = parse_qs(u.fragment)
        file_id = m.group(1) if m else (qs.get("id") or [None])[0]
        g = (frag.get("gid") or qs.get("gid") or [None])[0]
        gid = int(g) if g and g.isdigit() else None
    else:
        file_id = ref
    if not file_id or not re.fullmatch(_ID, file_id):
        raise ValueError(f"Not a Google file ID or URL: {ref!r}")
    return file_id, gid


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

mcp = FastMCP("google_workspace_readonly")

_FILE_FIELDS = "id,name,mimeType,modifiedTime,createdTime,owners(displayName,emailAddress),lastModifyingUser(displayName,emailAddress),webViewLink,size,driveId,parents,shared"
_MIME = {
    "doc": "application/vnd.google-apps.document",
    "sheet": "application/vnd.google-apps.spreadsheet",
    "slides": "application/vnd.google-apps.presentation",
    "folder": "application/vnd.google-apps.folder",
    "pdf": "application/pdf",
}


@mcp.tool()
def check_connection() -> str:
    """Verify the Google sign-in: signed-in user and the (read-only) scopes the token holds."""
    try:
        about = _get("https://www.googleapis.com/drive/v3/about", {"fields": "user(displayName,emailAddress)"})
        return _cap({
            "ok": True,
            "user": about.get("user"),
            "scopes": _CREDS.scopes,
            "read_only": True,
            "credentials": str(ENV_PATH),
        })
    except Exception as e:
        return _err(e)


def _q_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


@mcp.tool()
def search_files(
    query: str = "",
    file_type: str = "any",
    full_text: bool = False,
    modified_after: str = "",
    limit: int = 25,
    drive_query: str = "",
) -> str:
    """Search Drive (My Drive + shared drives + shared with me), newest modified first.

    query: words matched against the file name (or full content when full_text=True).
    file_type: any | doc | sheet | slides | folder | pdf.
    modified_after: ISO date/time, e.g. 2026-09-01.
    drive_query: raw Drive `q` expression (advanced), ANDed with the above.
    """
    try:
        clauses = ["trashed = false"]
        if query:
            field = "fullText" if full_text else "name"
            clauses.append(f"{field} contains '{_q_escape(query)}'")
        if file_type != "any":
            if file_type not in _MIME:
                return _err(ValueError(f"file_type must be one of any, {', '.join(_MIME)}"))
            clauses.append(f"mimeType = '{_MIME[file_type]}'")
        if modified_after:
            ts = modified_after if "T" in modified_after else modified_after + "T00:00:00"
            clauses.append(f"modifiedTime > '{_q_escape(ts)}'")
        if drive_query:
            clauses.append(f"({drive_query})")
        params = {
            "q": " and ".join(clauses),
            "pageSize": max(1, min(limit, 100)),
            "fields": f"files({_FILE_FIELDS})",
            "includeItemsFromAllDrives": "true",
            "supportsAllDrives": "true",
            "corpora": "allDrives",
        }
        if not full_text:
            params["orderBy"] = "modifiedTime desc"
        data = _get("https://www.googleapis.com/drive/v3/files", params)
        files = data.get("files", [])
        return _cap({"count": len(files), "q": params["q"], "files": files})
    except Exception as e:
        return _err(e)


@mcp.tool()
def get_file_metadata(file: str) -> str:
    """Metadata of one Drive file. `file` = file ID or any Docs/Sheets/Drive URL."""
    try:
        file_id, _ = _parse_ref(file)
        return _cap(_get(
            f"https://www.googleapis.com/drive/v3/files/{file_id}",
            {"fields": _FILE_FIELDS, "supportsAllDrives": "true"},
        ))
    except Exception as e:
        return _err(e)


def _sheet_props(spreadsheet_id: str) -> dict:
    return _get(
        f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}",
        {"fields": "properties(title,locale,timeZone),sheets(properties(sheetId,title,index,sheetType,hidden,gridProperties(rowCount,columnCount)))"},
    )


@mcp.tool()
def list_sheet_tabs(spreadsheet: str) -> str:
    """Tabs of a Google Sheet: title, gid, index, hidden, row/column count. `spreadsheet` = ID or URL."""
    try:
        sid, _ = _parse_ref(spreadsheet)
        meta = _sheet_props(sid)
        tabs = [s["properties"] for s in meta.get("sheets", [])]
        return _cap({"spreadsheet_id": sid, "title": meta.get("properties", {}).get("title"), "tabs": tabs})
    except Exception as e:
        return _err(e)


def _quote_tab(title: str) -> str:
    return "'" + title.replace("'", "''") + "'"


@mcp.tool()
def read_sheet(
    spreadsheet: str,
    ranges: list[str] | None = None,
    value_render: str = "FORMATTED_VALUE",
    max_rows: int = 2000,
    as_records: bool = False,
) -> str:
    """Read cell values from a Google Sheet.

    spreadsheet: ID or URL (a URL's #gid=N selects that tab when ranges is empty).
    ranges: A1 ranges, e.g. ["Sheet1!A1:F200", "'My Tab'"]. A bare tab name reads the whole tab.
            Empty → the tab from the URL gid, else the first tab.
    value_render: FORMATTED_VALUE | UNFORMATTED_VALUE | FORMULA.
    max_rows: rows returned per range (the rest are counted, not returned).
    as_records: first row as header → list of {header: value} dicts.
    """
    try:
        if value_render not in ("FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"):
            return _err(ValueError("value_render must be FORMATTED_VALUE, UNFORMATTED_VALUE or FORMULA"))
        sid, gid = _parse_ref(spreadsheet)
        if not ranges:
            tabs = [s["properties"] for s in _sheet_props(sid).get("sheets", [])]
            if not tabs:
                return _err(RuntimeError("Spreadsheet has no tabs"))
            tab = next((t for t in tabs if gid is not None and t["sheetId"] == gid), tabs[0])
            ranges = [_quote_tab(tab["title"])]
        data = _get(
            f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values:batchGet",
            [("ranges", r) for r in ranges] + [("valueRenderOption", value_render), ("majorDimension", "ROWS")],
        )
        out = []
        for vr in data.get("valueRanges", []):
            rows = vr.get("values", [])
            shown = rows[:max_rows] if not as_records else rows[: max_rows + 1]
            entry = {"range": vr.get("range"), "total_rows": len(rows)}
            if as_records and shown:
                header = [str(h) for h in shown[0]]
                entry["records"] = [
                    {header[i] if i < len(header) else f"col_{i + 1}": v for i, v in enumerate(row)}
                    for row in shown[1:]
                ]
            else:
                entry["values"] = shown
            if len(rows) > len(shown):
                entry["truncated_rows"] = len(rows) - len(shown)
            out.append(entry)
        return _cap({"spreadsheet_id": sid, "ranges": out})
    except Exception as e:
        return _err(e)


def _doc_text(elements: list) -> list[str]:
    lines: list[str] = []
    for el in elements or []:
        if "paragraph" in el:
            p = el["paragraph"]
            text = "".join(r.get("textRun", {}).get("content", "") for r in p.get("elements", []))
            style = p.get("paragraphStyle", {}).get("namedStyleType", "")
            if style.startswith("HEADING_") and text.strip():
                text = "#" * int(style[-1]) + " " + text
            elif style == "TITLE" and text.strip():
                text = "# " + text
            if "bullet" in p and text.strip():
                text = "  " * p["bullet"].get("nestingLevel", 0) + "- " + text
            lines.append(text.rstrip("\n"))
        elif "table" in el:
            for row in el["table"].get("tableRows", []):
                cells = [" ".join(_doc_text(c.get("content", []))).strip() for c in row.get("tableCells", [])]
                lines.append("| " + " | ".join(cells) + " |")
            lines.append("")
        elif "tableOfContents" in el:
            lines.extend(_doc_text(el["tableOfContents"].get("content", [])))
    return lines


def _walk_tabs(tabs: list, depth: int = 0):
    for t in tabs or []:
        yield depth, t
        yield from _walk_tabs(t.get("childTabs", []), depth + 1)


@mcp.tool()
def read_doc(document: str, tab: str = "") -> str:
    """Plain text (markdown-ish headings, bullets, tables as | rows) of a Google Doc.

    document: ID or URL. tab: only this document tab (title or tab ID); empty = all tabs.
    """
    try:
        did, _ = _parse_ref(document)
        doc = _get(f"https://docs.googleapis.com/v1/documents/{did}", {"includeTabsContent": "true"})
        parts = []
        tabs = list(_walk_tabs(doc.get("tabs", [])))
        for depth, t in tabs:
            props = t.get("tabProperties", {})
            if tab and tab not in (props.get("title"), props.get("tabId")):
                continue
            body = t.get("documentTab", {}).get("body", {}).get("content", [])
            header = f"{'=' * (depth + 1)} Tab: {props.get('title')} ({props.get('tabId')})"
            parts.append((header if len(tabs) > 1 else "") + "\n" + "\n".join(_doc_text(body)))
        if tab and not parts:
            return _err(ValueError(f"No tab {tab!r}; tabs: {[t.get('tabProperties', {}).get('title') for _, t in tabs]}"))
        return _cap(f"Title: {doc.get('title')}\nDocument ID: {did}\n\n" + "\n\n".join(parts).strip())
    except Exception as e:
        return _err(e)


_EXPORT = {
    "txt": ("text/plain", ".txt"),
    "md": ("text/markdown", ".md"),
    "html": ("text/html", ".html"),
    "csv": ("text/csv", ".csv"),
    "tsv": ("text/tab-separated-values", ".tsv"),
}


@mcp.tool()
def export_file(file: str, format: str = "txt", save_to_tmp: bool = False) -> str:
    """Export a Google Doc (txt | md | html) or Sheet (csv | tsv — first tab only; use read_sheet for others).

    save_to_tmp=True writes the full export to Agent-debugger/tmp/google_exports/ (0600) and returns the path
    plus a preview, for files too large to return inline.
    """
    try:
        if format not in _EXPORT:
            return _err(ValueError(f"format must be one of {', '.join(_EXPORT)}"))
        file_id, _ = _parse_ref(file)
        mime, ext = _EXPORT[format]
        r = _get(f"https://www.googleapis.com/drive/v3/files/{file_id}/export", {"mimeType": mime}, raw=True)
        text = r.content.decode("utf-8", errors="replace")
        if not save_to_tmp:
            return _cap(text)
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = EXPORT_DIR / f"{file_id}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}{ext}"
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(r.content)
        return _cap({"saved_to": str(path), "bytes": len(r.content), "preview": text[:5000]})
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
            self.wfile.write(b"<h3>Agent-debugger Google read-only sign-in complete. You can close this tab.</h3>")

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
    print(f"Open this URL to sign in (read-only scopes only):\n{url}\n", flush=True)
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
        "GOOGLE_WORKSPACE_REFRESH_TOKEN": body["refresh_token"],
        "GOOGLE_WORKSPACE_SCOPES": f'"{" ".join(scopes)}"',
    })
    print(f"Signed in. Scopes: {scopes}\nRefresh token saved to {ENV_PATH} (0600).", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        _auth(open_browser="--no-browser" not in sys.argv)
    else:
        mcp.run()
