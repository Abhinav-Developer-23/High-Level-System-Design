#!/usr/bin/env python3
"""Zenduty MCP server (tsp) — STRICTLY READ-ONLY incident inspection.

Zenduty (https://www.zenduty.com) is the incident/alert-calling vendor for the
TSP UPI teams: Prometheus Alertmanager fires into it, it pages the on-call
engineer, and the on-call agent acknowledges the incident.

Tools (ALL read-only):
  - check_connection   — verify the API token, report how many teams it can see
  - list_teams         — Zenduty teams (name + unique_id) for the team filter
  - list_incidents     — incidents in a time window, by status / team / title
  - get_incident       — one incident with its alerts (+ Alertmanager payload), timeline
  - get_alert_payload  — the raw Alertmanager webhook body of one alert: labels,
                         annotations (fired value), startsAt, fingerprint, PromQL expr
  - get_incident_stats — account/team incident analytics for a date range
  - list_read_endpoints — every GET route zenduty_get may call
  - zenduty_get        — generic GET on any allowlisted read route (schedules,
                         on-call, escalation policies, services, notes, ...)

=== WHY THIS SERVER CANNOT CHANGE ANYTHING ===

Every request goes through _request(), which accepts only:

    GET  <one of _GET_ROUTES>  — the 58 read routes of Zenduty's OpenAPI spec
                                 (apidocs.zenduty.com, v1.1.0) plus three
                                 undocumented reads the Zenduty UI uses
    POST /api/incidents/filter/                   — incident search
    POST /api/v2/account/analytics/incident_stats/ — incident counts

Both POSTs are searches that mutate nothing. The on-call agent acknowledges
with PATCH /api/incidents/<unique_id>/; PATCH, PUT and DELETE are refused
outright. Every route is an anchored fullmatch whose path parameters admit only
[A-Za-z0-9_-], so no argument can smuggle in '/', '..', '?' or another route.
Redirects are disabled. Secret-looking keys (integration keys, tokens) are
redacted from every response.

Credentials come from Agent-debugger/.env (TSP_ZENDUTY_URL, TSP_ZENDUTY_API_TOKEN).
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
from urllib.parse import parse_qs, urlparse

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


BASE_URL = os.getenv("TSP_ZENDUTY_URL", "https://www.zenduty.com").rstrip("/")
API_TOKEN = os.getenv("TSP_ZENDUTY_API_TOKEN", "")

if not API_TOKEN:
    _log(f"[tsp_zenduty] WARNING: TSP_ZENDUTY_API_TOKEN not set in {_ENV_PATH} — every call will fail.")

TIMEOUT = 30.0
# OS trust store, not certifi: Zscaler re-signs zenduty.com with its own root,
# which is only in the macOS keychain.
_TLS = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
IST = timezone(timedelta(hours=5, minutes=30))
_PAGE_SIZE = 50
_MAX_PAGES_PER_STATUS = 10
_MAX_WINDOW = timedelta(days=31)
_MAX_PAYLOAD_ALERTS = 20
_MAX_RESPONSE_CHARS = 150_000
_RATE_LIMIT_RETRIES = 2

STATUS_CODES = {"triggered": 1, "acknowledged": 2, "resolved": 3}
STATUS_LABELS = {v: k for k, v in STATUS_CODES.items()}
# From the IncidentAlert schema in Zenduty's OpenAPI spec.
ALERT_TYPE_LABELS = {"0": "info", "1": "warning", "2": "error", "3": "critical",
                     "4": "acknowledged", "5": "resolved"}
# Observed on live timelines; other codes are passed through as numbers.
TIMELINE_ACTION_LABELS = {1: "status_change", 2: "notification"}
_MAX_TIMELINE_PAGES = 10

# Read routes: Zenduty OpenAPI v1.1.0 GET paths, minus
# /api/account/integration-metadata/{integration_key}/ (takes a secret as input),
# plus the undocumented reads marked (UI).
_GET_ROUTES: tuple[tuple[str, str], ...] = (
    ("/api/account/members/", "Account members"),
    ("/api/account/members/{username}/", "One account member"),
    ("/api/account/customroles/", "Custom roles"),
    ("/api/account/customroles/{custom_role_id}/", "One custom role"),
    ("/api/account/users/{username}/customroles/", "A user's custom roles"),
    ("/api/account/users/{username}/notification_rules/", "A user's notification rules"),
    ("/api/account/users/{username}/notification_rules/{notification_rule_id}/", "One notification rule"),
    ("/api/account/users/{username}/forwarding_rules/", "A user's forwarding rules"),
    ("/api/account/users/{username}/forwarding_rules/{forwarding_rule_id}/", "One forwarding rule"),
    ("/api/account/users/{username}/contacts/", "A user's contact methods"),
    ("/api/account/users/{username}/contacts/{contact_id}/", "One contact method"),
    ("/api/account/teams/", "Teams"),
    ("/api/account/teams/{team_id}/", "One team"),
    ("/api/account/teams/{team_id}/members/", "Team members"),
    ("/api/account/teams/{team_id}/members/{member_id}/", "One team member"),
    ("/api/account/teams/{team_id}/permissions/", "Team permissions"),
    ("/api/account/teams/{team_id}/schedules/", "Team on-call schedules"),
    ("/api/account/teams/{team_id}/schedules/{schedule_id}/", "One schedule (layers, users)"),
    ("/api/v2/account/teams/{team_id}/schedules/{schedule_id}/overrides/", "Schedule overrides"),
    ("/api/account/teams/{team_id}/escalation_policies/", "Escalation policies"),
    ("/api/account/teams/{team_id}/escalation_policies/{escalation_policy_id}/", "One escalation policy"),
    ("/api/account/teams/{team_id}/services/", "Services"),
    ("/api/account/teams/{team_id}/services/{service_id}/", "One service"),
    ("/api/account/teams/{team_id}/services/{service_id}/integrations/", "A service's integrations"),
    ("/api/account/teams/{team_id}/services/{service_id}/integrations/{integration_id}/", "One integration"),
    ("/api/account/teams/{team_id}/services/{service_id}/integrations/{integration_id}/transformers/", "Alert rules of an integration"),
    ("/api/account/teams/{team_id}/services/{service_id}/integrations/{integration_id}/transformers/{transformer_id}/", "One alert rule"),
    ("/api/account/teams/{team_id}/roles/", "Incident roles"),
    ("/api/account/teams/{team_id}/roles/{incident_role_id}/", "One incident role"),
    ("/api/account/teams/{team_id}/tags/", "Tags"),
    ("/api/account/teams/{team_id}/tags/{tag_id}/", "One tag"),
    ("/api/account/teams/{team_id}/task_templates/", "Task templates"),
    ("/api/account/teams/{team_id}/task_templates/{task_template_id}/", "One task template"),
    ("/api/account/teams/{team_id}/priority/", "Priorities"),
    ("/api/account/teams/{team_id}/priority/{priority_id}/", "One priority"),
    ("/api/account/teams/{team_id}/sla/", "SLAs"),
    ("/api/account/teams/{team_id}/sla/{sla_id}/", "One SLA"),
    ("/api/account/teams/{team_id}/maintenance/", "Maintenance windows"),
    ("/api/account/teams/{team_id}/maintenance/{maintenance_id}/", "One maintenance window"),
    ("/api/account/teams/{team_id}/postmortem/", "Postmortems"),
    ("/api/account/teams/{team_id}/postmortem/{postmortem_id}/", "One postmortem"),
    ("/api/account/teams/{team_id}/oncall/", "Who is on call now, per escalation policy (v1)"),
    ("/api/v2/account/teams/{team_id}/oncall/", "Who is on call now, per escalation policy (v2)"),
    ("/api/v2/account/teams/{team_id}/escalation_policies/{escalation_policy_id}/oncall/", "On call for one escalation policy"),
    ("/api/v2/account/teams/{team_id}/services/{service_id}/oncall/", "On call for one service"),
    ("/api/v2/account/events/router/", "Global event routers"),
    ("/api/v2/account/events/router/{router_id}/", "One global router"),
    ("/api/v2/account/events/router/{router_id}/rulesets/", "Router rulesets"),
    ("/api/v2/account/events/router/{router_id}/rulesets/{ruleset_id}/", "One router ruleset"),
    ("/api/incidents/{incident}/", "One incident"),
    ("/api/incidents/{incident}/alerts/", "Alerts of an incident"),
    ("/api/incidents/{incident}/timeline/", "(UI) Incident action timeline"),
    ("/api/incidents/{incident}/note/", "Incident notes"),
    ("/api/incidents/{incident}/note/{note_id}/", "One incident note"),
    ("/api/incidents/{incident}/tags/", "Incident tags"),
    ("/api/incidents/{incident}/tags/{tag_id}/", "One incident tag"),
    ("/api/v2/incidents/{incident}/responders/", "Incident responders"),
    ("/api/incidents/{incident}/responders/{responder_id}/", "One incident responder"),
    ("/api/incidents/alerts/{alert_id}/", "(UI) One alert"),
    ("/api/incidents/alerts/{alert_id}/payload/", "(UI) Raw Alertmanager payload of one alert"),
    ("/api/alert/status/{trace_id}/", "Ingestion status of an event trace id"),
)
_PARAM = r"[A-Za-z0-9_-]{1,64}"


def _route_regex(template: str) -> str:
    parts = re.split(r"\{[a-z_]+\}", template)
    return _PARAM.join(re.escape(p) for p in parts)


_GET_RE = re.compile("|".join(f"(?:{_route_regex(tpl)})" for tpl, _ in _GET_ROUTES))
_POST_RE = re.compile(r"/api/incidents/filter/|/api/v2/account/analytics/incident_stats/")

_ID_RE = re.compile(r"\d{1,12}|[A-Za-z0-9]{10,40}")
_RELATIVE_RE = re.compile(r"now(?:-(\d+)([mhd]))?")
_QUERY_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,40}")
_SECRET_KEY_RE = re.compile(r"(?i)^(integration_key|integration_keys|api_key|api_token|token|"
                            r"access_token|refresh_token|secret|password|signing_secret)$")

_teams_cache: list[dict] = []


class ZendutyError(RuntimeError):
    """A refused request, bad argument, or vendor-side failure."""


def _request(method: str, path: str, *, params: dict | None = None,
             json_body: dict | None = None) -> httpx.Response:
    """The ONLY outbound call in this module, gated by _GET_RE / _POST_RE."""
    method = method.upper()
    rx = {"GET": _GET_RE, "POST": _POST_RE}.get(method)
    if rx is None or not rx.fullmatch(path):
        raise ZendutyError(
            f"refusing {method} {path}: tsp_zenduty is read-only (allowlisted GET routes, "
            f"plus POST incident filter / incident_stats searches)"
        )
    if not API_TOKEN:
        raise ZendutyError(f"TSP_ZENDUTY_API_TOKEN missing in {_ENV_PATH}")
    headers = {"Authorization": f"Token {API_TOKEN}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=TIMEOUT, verify=_TLS, follow_redirects=False) as client:
            for attempt in range(_RATE_LIMIT_RETRIES + 1):
                r = client.request(method, f"{BASE_URL}{path}", params=params,
                                   json=json_body, headers=headers)
                if r.status_code != 429 or attempt == _RATE_LIMIT_RETRIES:
                    return r
                time.sleep(min(float(r.headers.get("Retry-After") or 2), 5))
    except httpx.HTTPError as e:
        raise ZendutyError(f"{method} {path}: network error {type(e).__name__}: {e}") from e
    return r


def _json_or_raise(r: httpx.Response, what: str):
    if r.status_code == 401:
        raise ZendutyError(f"{what}: HTTP 401 — token rejected; check TSP_ZENDUTY_API_TOKEN")
    if r.status_code == 403:
        raise ZendutyError(f"{what}: HTTP 403 — token lacks permission for this read")
    if r.status_code == 404:
        raise ZendutyError(f"{what}: HTTP 404 — not found")
    if r.status_code == 429:
        raise ZendutyError(f"{what}: HTTP 429 — Zenduty rate limit; retry shortly")
    if r.status_code != 200:
        raise ZendutyError(f"{what}: HTTP {r.status_code}: {r.text[:200]}")
    try:
        return r.json()
    except ValueError as e:
        raise ZendutyError(f"{what}: non-JSON response: {r.text[:200]}") from e


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
                         "Narrow it with page / page_size or a more specific route.",
            "partial": text[:_MAX_RESPONSE_CHARS],
        }, indent=2)
    return text


def _parse_time(value: str, default: datetime) -> datetime:
    """ISO-8601 (naive = IST) or relative 'now' / 'now-30m' / 'now-6h' / 'now-2d'."""
    v = (value or "").strip()
    if not v:
        return default
    m = _RELATIVE_RE.fullmatch(v)
    if m:
        now = datetime.now(timezone.utc)
        if not m.group(1):
            return now
        n, unit = int(m.group(1)), m.group(2)
        return now - {"m": timedelta(minutes=n), "h": timedelta(hours=n), "d": timedelta(days=n)}[unit]
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError as e:
        raise ZendutyError(f"bad time {value!r} — use ISO-8601 or now-<N>m|h|d") from e
    return dt if dt.tzinfo else dt.replace(tzinfo=IST)


def _ist(iso: str | None) -> str | None:
    if not iso or iso.startswith("0001-"):
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return iso
    return dt.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S IST")


def _teams() -> list[dict]:
    if not _teams_cache:
        data = _json_or_raise(_request("GET", "/api/account/teams/"), "list teams")
        _teams_cache.extend({"name": t.get("name"), "unique_id": t.get("unique_id")}
                            for t in data if isinstance(t, dict))
    return _teams_cache


def _resolve_team(team: str) -> tuple[str, str]:
    wanted = team.strip().lower()
    for t in _teams():
        if wanted in ((t["name"] or "").lower(), (t["unique_id"] or "").lower()):
            return t["unique_id"], t["name"]
    raise ZendutyError(f"unknown team {team!r}; known: {[t['name'] for t in _teams()]}")


def _slim(inc: dict) -> dict:
    svc = inc.get("service_object") or {}
    status = inc.get("status")
    return {
        "incident_number": inc.get("incident_number"),
        "unique_id": inc.get("unique_id"),
        "title": inc.get("title"),
        "status": STATUS_LABELS.get(status, status),
        "urgency": inc.get("urgency"),
        "service": svc.get("name"),
        "team": svc.get("team_name"),
        "assigned_to": inc.get("assigned_to_name"),
        "created_ist": _ist(inc.get("creation_date")),
        "acknowledged_ist": _ist(inc.get("acknowledged_date")),
        "resolved_ist": _ist(inc.get("resolved_date")),
        "url": f"{BASE_URL}/dashboard/incidents/{inc.get('incident_number')}",
    }


def _promql_from(generator_url: str | None) -> list[str]:
    if not generator_url:
        return []
    qs = parse_qs(urlparse(generator_url).query)
    return [v for k in sorted(qs) if re.fullmatch(r"g\d+\.expr", k) for v in qs[k]]


def _summarize_payload(payload) -> dict:
    """Pull the debugging fields out of an Alertmanager webhook body."""
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except ValueError:
            return {"raw": payload}
    if not isinstance(payload, dict) or not payload:
        return {"empty": True, "note": "Zenduty stored no payload for this alert — fall back to the rule repo"}
    if not isinstance(payload.get("alerts"), list):
        return {"format": "non-alertmanager", "raw": _redact(payload)}
    return {
        "receiver": payload.get("receiver"),
        "status": payload.get("status"),
        "group_labels": payload.get("groupLabels"),
        "alertmanager": payload.get("externalURL"),
        "alerts": [
            {
                "status": a.get("status"),
                "labels": a.get("labels"),
                "annotations": a.get("annotations"),
                "starts_ist": _ist(a.get("startsAt")),
                "ends_ist": _ist(a.get("endsAt")),
                "starts_at_utc": a.get("startsAt"),
                "fingerprint": a.get("fingerprint"),
                "promql": _promql_from(a.get("generatorURL")),
                "generator_url": a.get("generatorURL"),
            }
            for a in payload["alerts"] if isinstance(a, dict)
        ],
    }


def _fetch_payload(alert_id: str) -> dict:
    data = _json_or_raise(_request("GET", f"/api/incidents/alerts/{alert_id}/payload/"),
                          f"payload of alert {alert_id}")
    return data


def _error(e: Exception) -> str:
    return json.dumps({"error": str(e)}, indent=2)


mcp = FastMCP(
    "tsp_zenduty",
    instructions=(
        "Read-only Zenduty access for TSP UPI incidents (https://www.zenduty.com). Use it "
        "to check whether an alert paged, when, whether it was acknowledged/resolved and "
        "by whom, and the raw Alertmanager payload (labels, fired value, PromQL expr) of "
        "each alert. The token sees every Zenduty team, so pass team='tsp-txn' (or another "
        "name from list_teams) to cut out other teams' noise. For anything else read-only "
        "(schedules, on-call, escalation policies, services, notes), use list_read_endpoints "
        "then zenduty_get. This server cannot acknowledge, resolve, reassign or otherwise "
        "change anything — if that is needed, tell the user to do it in the Zenduty UI."
    ),
)


@mcp.tool()
def check_connection() -> str:
    """
    Verify the configured Zenduty API token and report how many teams it can see.
    Use this first when incident lookups start failing.
    """
    _teams_cache.clear()
    try:
        teams = _teams()
    except ZendutyError as e:
        return _error(e)
    return json.dumps({
        "zenduty_url": BASE_URL,
        "token_ok": True,
        "teams_visible": len(teams),
        "read_routes": len(_GET_ROUTES),
        "server_mode": "READ-ONLY — allowlisted GETs + incident search/stats; cannot change anything",
    }, indent=2)


@mcp.tool()
def list_teams() -> str:
    """List the Zenduty teams this token can see (name + unique_id), for list_incidents' team filter."""
    try:
        return json.dumps({"teams": _teams()}, indent=2)
    except ZendutyError as e:
        return _error(e)


@mcp.tool()
def list_incidents(
    status: str = "all",
    from_time: str = "now-24h",
    to_time: str = "now",
    team: str = "",
    title_contains: str = "",
    limit: int = 50,
) -> str:
    """
    List Zenduty incidents created in a time window, newest first.

    Args:
        status: "triggered", "acknowledged", "resolved", or "all" (default).
        from_time: ISO-8601 or relative now-<N>m|h|d. Naive ISO is read as IST.
            Default "now-24h". Max window 31 days.
        to_time: Same format. Default "now".
        team: Zenduty team name or unique_id, e.g. "tsp-txn". Empty = every team.
        title_contains: Case-insensitive substring of the incident title — pass
            an Alertmanager alertname to find the incident it paged.
        limit: Max incidents returned (default 50, max 500). Counts cover all matches.
    """
    try:
        start = _parse_time(from_time, datetime.now(timezone.utc) - timedelta(hours=24))
        end = _parse_time(to_time, datetime.now(timezone.utc))
        if end <= start:
            raise ZendutyError("to_time must be after from_time")
        if end - start > _MAX_WINDOW:
            raise ZendutyError("window exceeds 31 days")

        wanted = status.strip().lower()
        if wanted == "all":
            codes = list(STATUS_CODES.values())
        elif wanted in STATUS_CODES:
            codes = [STATUS_CODES[wanted]]
        else:
            raise ZendutyError(f"bad status {status!r}; use {list(STATUS_CODES)} or 'all'")

        body_base = {
            "team_ids": [], "all_teams": 0, "service_ids": [], "user_ids": [],
            "priority_name": "", "priority_ids": [], "tag_ids": [], "sla_ids": [],
            "postmortem_filter": -1, "escalation_policy_ids": [],
            "current_user_responder": False,
            "from_date": start.astimezone(timezone.utc).isoformat(),
            "to_date": end.astimezone(timezone.utc).isoformat(),
        }
        team_name = None
        if team.strip():
            team_id, team_name = _resolve_team(team)
            body_base["team_ids"] = [team_id]

        rows: dict[str, dict] = {}
        truncated = False
        for code in codes:
            for page in range(1, _MAX_PAGES_PER_STATUS + 1):
                data = _json_or_raise(
                    _request("POST", "/api/incidents/filter/",
                             params={"page": page, "page_size": _PAGE_SIZE},
                             json_body={**body_base, "status": code}),
                    f"filter incidents status={STATUS_LABELS[code]}",
                )
                for inc in data.get("results") or []:
                    rows.setdefault(inc.get("unique_id") or str(inc.get("incident_number")), inc)
                if not data.get("next"):
                    break
            else:
                truncated = True
    except ZendutyError as e:
        return _error(e)

    incidents = list(rows.values())
    if team_name:
        # Belt-and-braces: keep only the requested team even if the API ignored team_ids.
        incidents = [i for i in incidents if (i.get("service_object") or {}).get("team_name") == team_name]
    needle = " ".join(title_contains.split()).lower()
    if needle:
        incidents = [i for i in incidents if needle in " ".join((i.get("title") or "").split()).lower()]
    incidents.sort(key=lambda i: i.get("creation_date") or "", reverse=True)
    cap = max(1, min(int(limit), 500))

    by_status: dict[str, int] = {}
    for i in incidents:
        label = STATUS_LABELS.get(i.get("status"), str(i.get("status")))
        by_status[label] = by_status.get(label, 0) + 1

    return json.dumps({
        "window_utc": f"{start.astimezone(timezone.utc).isoformat()} .. {end.astimezone(timezone.utc).isoformat()}",
        "window_ist": f"{start.astimezone(IST).strftime('%Y-%m-%d %H:%M')} .. {end.astimezone(IST).strftime('%Y-%m-%d %H:%M')} IST",
        "team": team_name or "all",
        "matched": len(incidents),
        "returned": min(len(incidents), cap),
        "matched_by_status": by_status,
        **({"truncated": f"stopped after {_MAX_PAGES_PER_STATUS * _PAGE_SIZE} incidents per status — narrow the window or add a team"} if truncated else {}),
        "incidents": [_slim(i) for i in incidents[:cap]],
    }, indent=2)


@mcp.tool()
def get_incident(incident: str, include_alerts: bool = True, include_payload: bool = True,
                 include_timeline: bool = False) -> str:
    """
    Get one Zenduty incident: status, service, assignee, summary, its alerts, and
    for each alert the Alertmanager payload — labels (e.g. current_cluster, host),
    annotations with the fired value, startsAt, fingerprint and the PromQL expr
    decoded from generatorURL. Optionally the action timeline (acks, notifications).

    Args:
        incident: Incident number (e.g. "382325") or Zenduty unique_id.
        include_alerts: Include the incident's alerts (default True).
        include_payload: Fetch each alert's Alertmanager payload (default True; first 20 alerts).
        include_timeline: Include the action timeline (default False).
    """
    ref = (incident or "").strip().lstrip("#")
    if not _ID_RE.fullmatch(ref):
        return _error(ZendutyError(f"bad incident reference {incident!r} — use the incident number or unique_id"))
    try:
        inc = _json_or_raise(_request("GET", f"/api/incidents/{ref}/"), f"incident {ref}")
        out = {"incident": {**_slim(inc), "summary": inc.get("summary"),
                            "incident_key": inc.get("incident_key"),
                            "escalation_policy": (inc.get("escalation_policy_object") or {}).get("name")}}
        if include_alerts:
            alerts = _json_or_raise(_request("GET", f"/api/incidents/{ref}/alerts/"), f"alerts of {ref}")
            rows = alerts.get("results") if isinstance(alerts, dict) else alerts
            out["alerts"] = []
            for n, a in enumerate(rows or []):
                row = {
                    "alert_unique_id": a.get("unique_id"),
                    "created_ist": _ist(a.get("creation_date")),
                    "alert_type": ALERT_TYPE_LABELS.get(str(a.get("alert_type")), a.get("alert_type")),
                    "message": a.get("message"),
                    "summary": a.get("summary"),
                    "entity_id": a.get("entity_id"),
                    "suppressed": a.get("suppressed"),
                    "integration": (a.get("integration_object") or {}).get("name"),
                    "urls": a.get("urls"),
                }
                if include_payload and n < _MAX_PAYLOAD_ALERTS and a.get("unique_id"):
                    try:
                        row["payload"] = _summarize_payload(_fetch_payload(a["unique_id"]))
                    except ZendutyError as e:
                        row["payload"] = {"error": str(e)}
                out["alerts"].append(row)
        if include_timeline:
            entries: list[dict] = []
            for page in range(1, _MAX_TIMELINE_PAGES + 1):
                tl = _json_or_raise(_request("GET", f"/api/incidents/{ref}/timeline/", params={"page": page}),
                                    f"timeline of {ref}")
                entries.extend(tl.get("results") or [])
                if not tl.get("next"):
                    break
            out["timeline"] = [
                {"at_ist": _ist(t.get("action_date")),
                 "action": TIMELINE_ACTION_LABELS.get(t.get("action"), t.get("action")),
                 "value": t.get("action_value"), "user": (t.get("user_name") or "").strip()}
                for t in sorted(entries, key=lambda t: t.get("action_date") or "")
            ]
            out["status_changes"] = [e for e in out["timeline"] if e["action"] == "status_change"]
    except ZendutyError as e:
        return _error(e)
    return _dump(out)


@mcp.tool()
def get_alert_payload(alert_unique_id: str, raw: bool = False) -> str:
    """
    Get the Alertmanager webhook body Zenduty stored for one alert: labels, annotations
    (fired value), startsAt/endsAt, fingerprint, and the PromQL expr decoded from
    generatorURL. Replay that expr with the tsp_grafana MCP (Thanos datasource for ALERTS).

    Args:
        alert_unique_id: The alert's unique_id (get_incident -> alerts[].alert_unique_id).
        raw: Also return the full stored body (default False).
    """
    ref = (alert_unique_id or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9]{10,40}", ref):
        return _error(ZendutyError(f"bad alert id {alert_unique_id!r} — use alerts[].alert_unique_id"))
    try:
        body = _fetch_payload(ref)
    except ZendutyError as e:
        return _error(e)
    out = {"alert_unique_id": ref, "payload": _summarize_payload(body)}
    if raw:
        out["raw"] = _redact(body)
    return _dump(out)


@mcp.tool()
def get_incident_stats(from_date: str, to_date: str, team: str = "tsp-txn") -> str:
    """
    Zenduty incident analytics (counts for the account and the requesting user)
    over a date range — POST /api/v2/account/analytics/incident_stats/, a search.

    Args:
        from_date: YYYY-MM-DD.
        to_date: YYYY-MM-DD.
        team: Team name or unique_id (default "tsp-txn"); empty = every team.
    """
    try:
        for d in (from_date, to_date):
            datetime.strptime((d or "").strip(), "%Y-%m-%d")
        body = {"from_date": from_date.strip(), "to_date": to_date.strip(), "team_ids": [],
                "service_ids": [], "user_ids": [], "priority_ids": [], "sla_ids": [],
                "escalation_policy_ids": [], "tag_ids": [], "urgency": "", "child_incident": "include"}
        if team.strip():
            body["team_ids"] = [_resolve_team(team)[0]]
        data = _json_or_raise(_request("POST", "/api/v2/account/analytics/incident_stats/", json_body=body),
                              "incident stats")
    except ValueError:
        return _error(ZendutyError("dates must be YYYY-MM-DD"))
    except ZendutyError as e:
        return _error(e)
    return _dump(_redact(data))


@mcp.tool()
def list_read_endpoints() -> str:
    """List every read-only GET route zenduty_get accepts, with what it returns."""
    return json.dumps({
        "note": "Path params ({team_id}, {incident}, ...) take unique_ids / numbers only. "
                "Get team ids from list_teams; service/schedule/policy ids from the list routes.",
        "routes": [{"path": p, "returns": d} for p, d in _GET_ROUTES],
    }, indent=2)


@mcp.tool()
def zenduty_get(path: str, params: dict | None = None) -> str:
    """
    Generic READ-ONLY GET on any Zenduty route from list_read_endpoints — use it for
    schedules, who is on call, escalation policies, services, integrations, notes,
    responders, postmortems, maintenance windows and any other analysis.

    Args:
        path: Concrete path, e.g. "/api/v2/account/teams/<team_id>/oncall/". Must match
            an allowlisted route exactly (trailing slash included).
        params: Optional query parameters, e.g. {"page": 2, "page_size": 50}.
    """
    p = (path or "").strip()
    if p and not p.startswith("/"):
        p = "/" + p
    if not p.endswith("/"):
        p += "/"
    query: dict = {}
    for k, v in (params or {}).items():
        if not _QUERY_KEY_RE.fullmatch(str(k)) or not isinstance(v, (str, int, float, bool)) \
                or len(str(v)) > 200 or any(c in str(v) for c in "\r\n"):
            return _error(ZendutyError(f"bad query parameter {k!r}"))
        query[str(k)] = v
    try:
        data = _json_or_raise(_request("GET", p, params=query or None), f"GET {p}")
    except ZendutyError as e:
        return _error(e)
    return _dump(_redact(data))


if __name__ == "__main__":
    mcp.run()
