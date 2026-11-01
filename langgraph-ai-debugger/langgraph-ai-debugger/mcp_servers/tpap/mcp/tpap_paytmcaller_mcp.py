#!/usr/bin/env python3
"""PaytmCaller MCP server (tpap) — STRICTLY READ-ONLY alert inspection.

PaytmCaller (https://paytmcaller-api.mypaytm.com) is the alert-calling vendor
for the TPAP UPI transactional team: Alertmanager fires into it, it phones /
emails the on-call engineer, and the on-call agent marks the alert in progress.

Tools (ALL read-only):
  - check_connection         — log in, report which account the credentials belong to
  - list_alerts              — alerts for an IST date range, filterable by state/title/priority
  - get_alert                — one alert's full row (+ optional call analytics)
  - get_alert_call_analytics — who was called, who picked up / pressed 1, per escalation stage
  - get_on_calls             — on-call users per day for a tech team
  - list_read_endpoints      — every GET route paytmcaller_get may call
  - paytmcaller_get          — generic GET on any allowlisted read route (alert metrics,
                               team config, billing, usage, schedule groups, schedules)

=== WHY THIS SERVER CANNOT CHANGE ANYTHING ===

_request() accepts only exact (method, path) pairs:

    POST /api/users/login              — exchanges the credentials for an access token
    POST /api/tech_teams/on_calls      — on-call lookup; a fetch that happens to use POST
    GET  <one of _GET_ROUTES>          — the read APIs documented on the TPAP wiki

Neither POST mutates anything. The write routes — mark_alert_as_in_progress,
acknowledge / resolve / snooze / bulk actions, PUT /api/schedules,
POST /api/tech_teams/techteamconfig — are not on the allowlist, so no tool,
argument or crafted path can reach them. The allowlist is exact, never a prefix
match. Redirects are disabled. user_email and the org id are always injected by
the server and cannot be overridden. Secret-looking keys (integration keys,
tokens) are redacted from every response.

Credentials come from Agent-debugger/.env (TPAP_PAYTMCALLER_URL,
TPAP_PAYTMCALLER_USER_EMAIL_B64, TPAP_PAYTMCALLER_PASSWORD_B64,
TPAP_PAYTMCALLER_ORG_ID). The email and password are the vendor's encrypted
b64 form, not plain text — copy them verbatim from the on-call agent config.
"""

import json
import logging
import os
import re
import ssl
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import truststore
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Cursor treats MCP stderr INFO as errors and may hide the server from the agent.
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.disable(logging.INFO)

# Explicit path: the MCP host launches this with an arbitrary cwd.
_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


def _log(msg: str) -> None:
    print(f"\033[96m{msg}\033[0m", file=sys.stderr, flush=True)


BASE_URL = os.getenv("TPAP_PAYTMCALLER_URL", "https://paytmcaller-api.mypaytm.com").rstrip("/")
USER_EMAIL_B64 = os.getenv("TPAP_PAYTMCALLER_USER_EMAIL_B64", "")
PASSWORD_B64 = os.getenv("TPAP_PAYTMCALLER_PASSWORD_B64", "")
ORG_ID = os.getenv("TPAP_PAYTMCALLER_ORG_ID", "")

if not (USER_EMAIL_B64 and PASSWORD_B64 and ORG_ID):
    _log(
        f"[tpap_paytmcaller] WARNING: TPAP_PAYTMCALLER_USER_EMAIL_B64 / _PASSWORD_B64 / "
        f"_ORG_ID not set in {_ENV_PATH} — every call will fail until they're filled in."
    )

TIMEOUT = 60.0
# OS trust store, not certifi: Zscaler re-signs vendor TLS with its own root,
# which is only in the macOS keychain.
_TLS = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
IST = timezone(timedelta(hours=5, minutes=30))
# The vendor issues ~1h tokens; refresh a little early.
_TOKEN_TTL_SECONDS = 50 * 60
# Vendor limit for /api/alerts/ and get_alert_metrics.
_MAX_RANGE_DAYS = 90
_MAX_ON_CALL_DAYS = 31
_MAX_RESPONSE_CHARS = 150_000
DEFAULT_TECH_TEAM = "tpap-transactional"

# /api/alerts/ returns only the tech teams the AUTHENTICATED account belongs to.
# There is no tech_team query parameter to widen it — the PaytmCaller UI does not
# send one either (verified against the UI's own XHR). So an empty result means
# "nothing visible to this account", NOT "no alert fired".
# Verified 2026-09-28: eight P0 "DBA tpapDB Switch Master Low Disk Space" pages on
# the Upi-Transactional-Switch team were plainly visible in the UI for the same org
# and date range, while this server returned total_for_range=0 for 27-28 Sep.
_VISIBILITY_NOTE = (
    "/api/alerts/ is scoped to the tech teams this account belongs to, and the vendor exposes "
    "no tech_team filter to widen it. An empty or short result is NOT proof that no alert fired. "
    "Known blind spot: the 'Upi-Transactional-Switch' team (DBA P0 pages). Cross-check with the "
    "gmail_readonly MCP - search_messages(query='label:paytm-caller newer_than:3d'), optionally "
    "adding subject:\"<TechTeam>\" - or open the PaytmCaller UI."
)

# path -> (org-id query key the vendor expects, description). From the TPAP wiki
# PaytmCaller API pages; every one is a GET that reads.
_GET_ROUTES: dict[str, tuple[str, str]] = {
    "/api/alerts/": ("organization_id", "Alerts for start_date..end_date (DD-MM-YYYY, <=90 days)"),
    "/api/alerts/get_alert_metrics": ("organization_id", "Org-wide noisy alerts, ack/resolution rates, "
                                      "fatigue — last_n_days or start_date/end_date. Heavy; cached daily"),
    "/api/alerts/get_alert_analytics": ("organization_id", "One alert's call summary — alert_id, tech_team"),
    "/api/alerts/full_detailed_analytics": ("organization_id", "One alert's per-stage call tree — alert_id, tech_team"),
    "/api/tech_teams": ("org_uuid", "Tech team config: escalation stages, schedule groups — tech_team"),
    "/api/tech_teams/team_billing": ("org_uuid", "Call/SMS billing — filter_type: last_day|last_7|last_14|"
                                     "last_30|last_month"),
    "/api/tech_teams/daily_usage_stats": ("org_uuid", "Daily usage — stat_date YYYY-MM-DD (default T-1)"),
    "/api/schedule_groups": ("organization_id", "Schedule groups (on-call rosters)"),
    "/api/schedules": ("organization_id", "Schedules — schedule_ids (comma-separated), individual_schedule=true"),
}
_POST_ROUTES = frozenset({"/api/users/login", "/api/tech_teams/on_calls"})
_INJECTED_KEYS = frozenset({"user_email", "organization_id", "org_uuid"})

_SORT_KEY_RE = re.compile(r"(ALT_[A-Za-z0-9]+)")
_TECH_TEAM_RE = re.compile(r":TT:([A-Za-z0-9_-]+)")
_SAFE_TOKEN_RE = re.compile(r"[A-Za-z0-9_-]{1,80}")
_QUERY_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,40}")
_SECRET_KEY_RE = re.compile(r"(?i)^(integration_key|integration_keys|api_key|api_token|token|"
                            r"access_token|refresh_token|auth_token|secret|password)$")

_token: dict = {"value": None, "expires_at": 0.0}


class PaytmCallerError(RuntimeError):
    """A refused request, bad argument, or vendor-side failure."""


def _request(method: str, path: str, *, params: dict | None = None,
             json_body: dict | None = None, token: str | None = None) -> httpx.Response:
    """The ONLY outbound call in this module, gated by _GET_ROUTES / _POST_ROUTES."""
    method = method.upper()
    allowed = (method == "GET" and path in _GET_ROUTES) or (method == "POST" and path in _POST_ROUTES)
    if not allowed:
        raise PaytmCallerError(
            f"refusing {method} {path}: tpap_paytmcaller is read-only (documented GET reads, "
            f"plus POST login and the on_calls lookup)"
        )
    headers = {"Content-Type": "application/json"}
    if token:
        headers["auth-token"] = token
    try:
        with httpx.Client(timeout=TIMEOUT, verify=_TLS, follow_redirects=False) as client:
            return client.request(method, f"{BASE_URL}{path}", params=params,
                                  json=json_body, headers=headers)
    except httpx.HTTPError as e:
        raise PaytmCallerError(f"{method} {path}: network error {type(e).__name__}: {e}") from e


def _login(force: bool = False) -> tuple[str, dict]:
    if not force and _token["value"] and time.time() < _token["expires_at"]:
        return _token["value"], _token.get("user", {})
    if not (USER_EMAIL_B64 and PASSWORD_B64):
        raise PaytmCallerError(f"credentials missing — set TPAP_PAYTMCALLER_* in {_ENV_PATH}")
    r = _request("POST", "/api/users/login",
                 json_body={"user_email": USER_EMAIL_B64, "password": PASSWORD_B64})
    if r.status_code != 200:
        raise PaytmCallerError(f"login HTTP {r.status_code}: {r.text[:200]}")
    data = (r.json() or {}).get("data") or {}
    tok = data.get("access_token")
    if not tok:
        raise PaytmCallerError("login response carried no data.access_token")
    _token.update(value=tok, expires_at=time.time() + _TOKEN_TTL_SECONDS,
                  user=data.get("user_details") or {})
    return tok, _token["user"]


def _call(method: str, path: str, *, params: dict | None = None, json_body: dict | None = None):
    """Authenticated call with one re-login on 401/403; returns parsed JSON."""
    tok, _ = _login()
    r = _request(method, path, params=params, json_body=json_body, token=tok)
    if r.status_code in (401, 403):
        tok, _ = _login(force=True)
        r = _request(method, path, params=params, json_body=json_body, token=tok)
    if r.status_code != 200:
        raise PaytmCallerError(f"{method} {path}: HTTP {r.status_code}: {r.text[:300]}")
    try:
        return r.json()
    except ValueError as e:
        raise PaytmCallerError(f"{method} {path}: non-JSON response: {r.text[:200]}") from e


def _get(path: str, params: dict | None = None):
    org_key = _GET_ROUTES[path][0] if path in _GET_ROUTES else "organization_id"
    return _call("GET", path, params={**(params or {}), "user_email": USER_EMAIL_B64, org_key: ORG_ID})


def _redact(obj):
    if isinstance(obj, dict):
        return {k: ("<redacted>" if _SECRET_KEY_RE.match(str(k)) else _redact(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    return obj


def _dump(obj) -> str:
    text = json.dumps(obj, indent=2, default=str)
    if len(text) > _MAX_RESPONSE_CHARS:
        return json.dumps({
            "truncated": f"response was {len(text)} chars; showing the first {_MAX_RESPONSE_CHARS}. "
                         "Narrow the date range or filters.",
            "partial": text[:_MAX_RESPONSE_CHARS],
        }, indent=2)
    return text


def _parse_date(value: str | None, default: datetime) -> datetime:
    """Accept DD-MM-YYYY or YYYY-MM-DD; empty means `default`."""
    if not value:
        return default
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    raise PaytmCallerError(f"bad date {value!r} — use DD-MM-YYYY or YYYY-MM-DD (IST calendar day)")


def _date_range(start_date: str | None, end_date: str | None, max_days: int) -> tuple[str, str]:
    today = datetime.now(IST).replace(tzinfo=None)
    start = _parse_date(start_date, today)
    end = _parse_date(end_date, start)
    if end < start:
        raise PaytmCallerError("end_date is before start_date")
    if (end - start).days > max_days:
        raise PaytmCallerError(f"date range exceeds {max_days} days")
    return start.strftime("%d-%m-%Y"), end.strftime("%d-%m-%Y")


def _fetch_alerts(start_date: str | None, end_date: str | None) -> tuple[list[dict], str, str]:
    s, e = _date_range(start_date, end_date, _MAX_RANGE_DAYS)
    body = _get("/api/alerts/", {"start_date": s, "end_date": e})
    data = body.get("data") if isinstance(body, dict) else body
    rows = data.get("alerts") if isinstance(data, dict) else data
    return [x for x in (rows or []) if isinstance(x, dict)], s, e


def _alert_id(row: dict) -> str | None:
    m = _SORT_KEY_RE.search(row.get("sort_key") or "")
    return m.group(1) if m else None


def _tech_team(row: dict) -> str | None:
    m = _TECH_TEAM_RE.search(row.get("primary_key") or "")
    return m.group(1) if m else None


def _slim(row: dict) -> dict:
    return {
        "alert_id": _alert_id(row),
        "unique_alert_id": row.get("unique_alert_id"),
        "title": row.get("title"),
        "description": row.get("description"),
        "state": row.get("alert_state"),
        "priority": row.get("priority"),
        "fired_at_ist": row.get("timestamp"),
        "fired_at_utc": row.get("timestamp_key"),
        "marked_in_progress_by": row.get("marked_in_progress_by"),
        "marked_completed_by": row.get("marked_completed_by"),
        "auto_resolved": row.get("auto_resolved"),
        "is_snoozed": row.get("is_snoozed"),
        "source": row.get("source"),
        "tech_team": _tech_team(row) or row.get("severity"),
    }


def _call_analytics(alert_id: str, tech_team: str, detailed: bool) -> dict:
    params = {"alert_id": alert_id, "tech_team": tech_team}
    out = {"summary": _redact(_get("/api/alerts/get_alert_analytics", params))}
    if detailed:
        out["per_stage"] = _redact(_get("/api/alerts/full_detailed_analytics", params))
    return out


def _check_token(value: str, what: str) -> str:
    v = (value or "").strip()
    if not _SAFE_TOKEN_RE.fullmatch(v):
        raise PaytmCallerError(f"bad {what} {value!r}")
    return v


def _error(e: Exception) -> str:
    return json.dumps({"error": str(e)}, indent=2)


mcp = FastMCP(
    "tpap_paytmcaller",
    instructions=(
        "Read-only PaytmCaller access for TPAP UPI alerts "
        "(https://paytmcaller-api.mypaytm.com). Use it to check whether an alert fired, "
        "when, its state (e.g. OPEN / IN_PROGRESS / COMPLETED), who was called and who "
        "picked it up, who is on call, and — via list_read_endpoints + paytmcaller_get — "
        "alert metrics, team config, billing, usage and schedules. Dates are IST calendar "
        "days. This server cannot acknowledge, mark in progress, resolve, snooze, edit a "
        "schedule or otherwise change anything — if that is needed, tell the user to do it "
        "in the PaytmCaller UI. IMPORTANT: alert listings are scoped to the tech teams this "
        "account belongs to and there is no tech_team filter, so an empty result never proves "
        "no alert fired — cross-check label:paytm-caller via the gmail_readonly MCP."
    ),
)


@mcp.tool()
def check_connection() -> str:
    """
    Log in with the configured PaytmCaller credentials and report which account
    they belong to. Use this first when alert lookups start failing.
    """
    try:
        _, user = _login(force=True)
    except PaytmCallerError as e:
        return _error(e)
    return json.dumps({
        "paytmcaller_url": BASE_URL,
        "authenticated_as": user.get("name"),
        "email": user.get("email"),
        "organization_id": ORG_ID,
        "read_routes": len(_GET_ROUTES),
        "server_mode": "READ-ONLY — documented reads + on_calls lookup; cannot change anything",
        "alert_visibility": _VISIBILITY_NOTE,
    }, indent=2)


@mcp.tool()
def list_alerts(
    start_date: str = "",
    end_date: str = "",
    state: str = "",
    title_contains: str = "",
    priority: str = "",
    limit: int = 50,
) -> str:
    """
    List PaytmCaller alerts for the TPAP transactional team, newest first.

    Args:
        start_date: IST calendar day, DD-MM-YYYY or YYYY-MM-DD. Default: today (IST).
        end_date: IST calendar day, inclusive. Default: same as start_date. Max span 90 days.
        state: Keep only this alert_state, case-insensitive (e.g. "COMPLETED", "IN_PROGRESS").
        title_contains: Case-insensitive substring match on title or description —
            pass an Alertmanager alertname to find that alert.
        priority: Keep only this priority, e.g. "P0", "P1".
        limit: Max rows returned (default 50, max 500). Counts cover all matches.
    """
    try:
        rows, s, e = _fetch_alerts(start_date, end_date)
    except PaytmCallerError as err:
        return _error(err)

    needle = " ".join(title_contains.split()).lower()
    matched = [
        r for r in rows
        if (not state or (r.get("alert_state") or "").lower() == state.strip().lower())
        and (not priority or (r.get("priority") or "").lower() == priority.strip().lower())
        and (not needle or needle in " ".join(f"{r.get('title') or ''} {r.get('description') or ''}".split()).lower())
    ]
    matched.sort(key=lambda r: r.get("timestamp_key") or "", reverse=True)
    cap = max(1, min(int(limit), 500))

    by_state: dict[str, int] = {}
    for r in matched:
        by_state[r.get("alert_state") or "UNKNOWN"] = by_state.get(r.get("alert_state") or "UNKNOWN", 0) + 1

    out = {
        "date_range_ist": f"{s} .. {e}",
        "total_for_range": len(rows),
        "matched": len(matched),
        "returned": min(len(matched), cap),
        "matched_by_state": by_state,
        "tech_teams_visible": sorted({t for t in (_tech_team(r) for r in rows) if t}),
        "alerts": [_slim(r) for r in matched[:cap]],
    }
    if not matched:
        out["visibility_warning"] = _VISIBILITY_NOTE
    return _dump(out)


@mcp.tool()
def get_alert(alert_id: str, start_date: str = "", end_date: str = "",
              include_call_analytics: bool = False) -> str:
    """
    Get the full PaytmCaller row for one alert. PaytmCaller has no single-alert
    endpoint, so this lists the date range and picks the match.

    Args:
        alert_id: "ALT_..." id (from list_alerts / sort_key) or the 16-char unique_alert_id.
        start_date: IST day the alert fired, DD-MM-YYYY or YYYY-MM-DD. Default: today.
        end_date: Inclusive end day. Default: same as start_date.
        include_call_analytics: Also attach who was called / picked up, per escalation stage.
    """
    wanted = (alert_id or "").strip()
    if wanted.upper().startswith("ALT:"):
        wanted = wanted[4:]
    if not wanted:
        return _error(PaytmCallerError("alert_id is required"))
    try:
        rows, s, e = _fetch_alerts(start_date, end_date)
        for r in rows:
            if wanted in (_alert_id(r), r.get("unique_alert_id")):
                out = {"alert": _slim(r), "raw": _redact(r)}
                if include_call_analytics and _alert_id(r):
                    out["call_analytics"] = _call_analytics(
                        _alert_id(r), _tech_team(r) or DEFAULT_TECH_TEAM, detailed=True)
                return _dump(out)
    except PaytmCallerError as err:
        return _error(err)
    return json.dumps({
        "error": f"alert {wanted!r} not found in {s} .. {e} ({len(rows)} alerts scanned)",
        "hint": "pass start_date/end_date covering the IST day it fired",
        "visibility_warning": _VISIBILITY_NOTE,
    }, indent=2)


@mcp.tool()
def get_alert_call_analytics(alert_id: str, tech_team: str = DEFAULT_TECH_TEAM,
                             detailed: bool = True) -> str:
    """
    Who PaytmCaller phoned for one alert: total calls, who picked up, who acknowledged,
    and (detailed) every call per escalation stage / schedule group with status,
    duration and whether they pressed 1.

    Args:
        alert_id: "ALT_..." id from list_alerts.
        tech_team: PaytmCaller tech team (the "TT:" part of primary_key). Default "tpap-transactional".
        detailed: Include the per-stage call tree (default True).
    """
    try:
        aid = _check_token(alert_id, "alert_id")
        if not aid.startswith("ALT_"):
            raise PaytmCallerError("alert_id must be the ALT_... id from list_alerts")
        return _dump(_call_analytics(aid, _check_token(tech_team, "tech_team"), detailed))
    except PaytmCallerError as e:
        return _error(e)


@mcp.tool()
def get_on_calls(tech_team: str = DEFAULT_TECH_TEAM, start_date: str = "", end_date: str = "") -> str:
    """
    On-call users per day for a PaytmCaller tech team (POST /api/tech_teams/on_calls — a lookup).

    Args:
        tech_team: Default "tpap-transactional".
        start_date: IST day, DD-MM-YYYY or YYYY-MM-DD. Default today.
        end_date: Inclusive. Default same as start_date. Max span 31 days.
    """
    try:
        s, e = _date_range(start_date, end_date, _MAX_ON_CALL_DAYS)
        data = _call("POST", "/api/tech_teams/on_calls", json_body={
            "user_email": USER_EMAIL_B64, "org_uuid": ORG_ID,
            "tech_team": _check_token(tech_team, "tech_team"), "start_date": s, "end_date": e,
        })
    except PaytmCallerError as err:
        return _error(err)
    return _dump({"tech_team": tech_team, "date_range_ist": f"{s} .. {e}", "on_calls": _redact(data)})


@mcp.tool()
def list_read_endpoints() -> str:
    """List every read-only GET route paytmcaller_get accepts, with what it returns."""
    return json.dumps({
        "note": "user_email and organization_id / org_uuid are injected automatically. "
                "Dates are DD-MM-YYYY unless noted.",
        "routes": [{"path": p, "returns": d} for p, (_, d) in _GET_ROUTES.items()],
        "also": "get_on_calls wraps POST /api/tech_teams/on_calls (a lookup).",
    }, indent=2)


@mcp.tool()
def paytmcaller_get(path: str, params: dict | None = None) -> str:
    """
    Generic READ-ONLY GET on a documented PaytmCaller read route (see list_read_endpoints):
    alert metrics, team config, billing, daily usage, schedule groups, schedules.

    Args:
        path: e.g. "/api/alerts/get_alert_metrics". Must match a route exactly.
        params: Query parameters, e.g. {"last_n_days": 7} or {"tech_team": "tpap-transactional"}.
            user_email / organization_id / org_uuid are injected and cannot be set.
    """
    p = "/" + (path or "").strip().lstrip("/")
    if p not in _GET_ROUTES:
        return _error(PaytmCallerError(f"refusing GET {p}: not a documented read route — see list_read_endpoints"))
    query: dict = {}
    for k, v in (params or {}).items():
        if str(k) in _INJECTED_KEYS:
            return _error(PaytmCallerError(f"{k} is injected by the server and cannot be overridden"))
        if not _QUERY_KEY_RE.fullmatch(str(k)) or not isinstance(v, (str, int, float, bool)) \
                or len(str(v)) > 500 or any(c in str(v) for c in "\r\n"):
            return _error(PaytmCallerError(f"bad query parameter {k!r}"))
        query[str(k)] = str(v).lower() if isinstance(v, bool) else v
    try:
        return _dump(_redact(_get(p, query)))
    except PaytmCallerError as e:
        return _error(e)


if __name__ == "__main__":
    mcp.run()
