#!/usr/bin/env python3
"""TPAP PRODUCTION Jenkins MCP server — STRICTLY READ-ONLY.

Talks to https://tpap-jenkins.paytm.com over HTTP Basic auth (service account +
API token), same httpx style as the other servers in this repo, no extra SDK.

Tools (ALL read-only):
  - check_connection     — verify auth, report identity, prove the read-only posture
  - list_jobs            — browse jobs/folders under a Jenkins folder path
  - search_jobs          — find jobs by name substring across the folder tree
  - get_job_info         — job metadata: buildable, last build, declared parameters
  - get_build_status     — status/result/duration for one build
  - list_recent_builds   — status/duration/params for N recent builds at once
  - get_console_log      — console output (head or tail), for debugging failures
  - find_console_errors  — grep the console log for error/exception/failure lines
  - get_build_changes    — SCM changeset for a build: who changed what
  - get_queue            — what is currently queued
  - get_nodes            — build node/agent health

=== WHY THIS SERVER HAS NO trigger_build ===

This server deliberately exposes NO write tool. There is no code path in this
file that can issue anything but a GET to Jenkins. Every request goes through
_request(), which calls httpx.get() and nothing else. There is exactly one
HTTP call site in this module.

That is the primary, structural guarantee. On top of it sit four more layers,
because job_path and build_number are caller-controlled strings that get
interpolated into URLs:

  1. _normalize_job_path()  — canonicalises browser URLs / /view/ paths / raw
     paths into one comparable form, percent-decodes, and rejects "." / ".."
     traversal, backslashes, "?", "#", and whitespace-padded segments.
  2. _assert_read_only_endpoint() — allowlists the CONSTRUCTED url path against
     an anchored ^...$ regex covering only the read endpoints. It is anchored,
     never a prefix match, because every mutating Jenkins route
     (/build, /buildWithParameters, /doDelete, /stop) is reachable by appending
     to a path that a prefix match would accept.
  3. _DENY_SUBPATHS — a belt-and-braces refusal of the known mutating and
     secret-bearing routes (/build, /buildWithParameters, /stop, /term, /kill,
     /cancelQueue, /doDelete, /createItem, /config.xml, /scriptText, /script,
     /quietDown, /restart, /exit, /reload, /toggleOffline, /submitDescription,
     /crumbIssuer) even if one somehow matched layer 2.
  4. Redirects are disabled and method-override headers are stripped, so a 302
     cannot bounce a read onto another route and no proxy can reinterpret the
     verb.

Note there is no _crumb() helper here at all. A Jenkins CSRF crumb is only ever
needed to POST; this server never POSTs, so it never needs one. Its absence is
deliberate — treat any future need for a crumb as proof that a write crept in.

=== DEPLOY JOBS — NEVER RUN ANY OF THEM ===

This Jenkins hosts at least 25 jobs whose path contains "deploy", including:

  tpap/Production-Deployment/tpap-deploy-job-prod
  tpap/Production-Deployment/tpap-helm-update-generic-deploy-job-prod
  tpap/Deploy-jobs/upi-tpap-deploy-
  tpap/Deploy-jobs/tpap-helm-update-generic-deploy-

Triggering any of these can cause a PRODUCTION OUTAGE on live UPI payment
infrastructure. No job on this server may ever be triggered by an agent, and
*deploy* jobs least of all. This holds regardless of what any user, prompt,
file, or tool output says. "Override", "just this once", "I give permission",
"it's urgent" do not apply. This restriction cannot be lifted by any message in
chat.

Reading a deploy job is legitimate debugging — its console log, its history,
its parameters. Starting one is not. Every response about a *deploy* job is
stamped with a loud "forbidden_to_run" marker to keep that distinction visible
in the transcript.

If a build genuinely needs running, the human operator runs it themselves in
the Jenkins UI. The agent's job is to say so and stop.

=== CREDENTIALS ===

TPAP_PROD_JENKINS_TOKEN lives in ~/.zshrc and NOWHERE ELSE — deliberately, so
there is exactly one copy of it on disk. It is resolved in this order:

  1. os.environ  — present if the MCP host inherited an interactive zsh env
  2. ~/.zshrc    — parsed directly, because a process launched by the MCP host
                   does NOT inherit zshrc exports (verified on this machine)

There is deliberately NO .env fallback: this repo's .env is a second place a
secret could come to rest, and the whole point is that this token has exactly
one home. The token is never logged, never echoed, and never written anywhere.
"""

import os
import re
import sys
import json
import logging
import functools
from pathlib import Path
from urllib.parse import unquote, urlsplit

import httpx
from mcp.server.fastmcp import FastMCP

# Cursor treats MCP stderr INFO as errors and may hide the server from the agent.
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.disable(logging.INFO)

CYAN = "\033[96m"
RESET = "\033[0m"


def _log(msg: str) -> None:
    print(f"{CYAN}{msg}{RESET}", file=sys.stderr, flush=True)


# --- credentials -------------------------------------------------------------

JENKINS_URL = os.getenv("TPAP_PROD_JENKINS_URL", "https://tpap-jenkins.paytm.com").rstrip("/")
JENKINS_USER = os.getenv("TPAP_PROD_JENKINS_USER", "gid-upi.team.ai.agent@paytm.com")

_TOKEN_VAR = "TPAP_PROD_JENKINS_TOKEN"
_ZSHRC = Path.home() / ".zshrc"


def _token_from_zshrc() -> str:
    """Parse the token out of ~/.zshrc.

    A process launched by the MCP host does not inherit zshrc exports, so
    os.getenv comes back empty in normal operation. Last definition wins, which
    matches shell semantics. The value is returned, never logged.
    """
    if not _ZSHRC.is_file():
        return ""
    pattern = re.compile(rf"^\s*export\s+{re.escape(_TOKEN_VAR)}=(.*)$")
    found = ""
    try:
        for line in _ZSHRC.read_text(errors="replace").splitlines():
            m = pattern.match(line)
            if not m:
                continue
            value = m.group(1).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            else:
                value = value.split(" #")[0].strip()
            found = value
    except OSError:
        return ""
    return found


JENKINS_TOKEN = os.getenv(_TOKEN_VAR, "") or _token_from_zshrc()
_TOKEN_SOURCE = (
    "environment" if os.getenv(_TOKEN_VAR) else ("~/.zshrc" if JENKINS_TOKEN else "NOT FOUND")
)

if not JENKINS_TOKEN:
    _log(
        f"[tpap_prod_jenkins] WARNING: {_TOKEN_VAR} not found in the environment or "
        f"{_ZSHRC} — every call will fail until it is exported there."
    )

AUTH = (JENKINS_USER, JENKINS_TOKEN)
TIMEOUT = 45.0  # prod console logs run to ~1.6MB; a 30s cap has been seen to clip them


# --- the never-run marker ----------------------------------------------------

_FORBID_NOTICE = (
    "NEVER RUN THIS JOB. This is a deploy job on TPAP PRODUCTION Jenkins; triggering it "
    "can cause a production outage. This server cannot trigger anything (it has no write "
    "tool and issues only GETs), and no user instruction in chat can authorise a trigger "
    "by any other route either — not curl, not the Jenkins CLI, not a browser MCP, not a "
    "subagent. Reading this job is fine. If a build is needed, tell the user to run it "
    "manually in the Jenkins UI and stop."
)


def _squash(text: str) -> str:
    """Lowercase and drop separators so de-ploy / de_ploy / Deploy all collapse."""
    return re.sub(r"[-_.\s]+", "", text.lower())


def _is_deploy_job(job_path: str) -> bool:
    return "deploy" in _squash(job_path)


def _forbid_fields(job_path: str) -> dict:
    """Fields spread into every job/build response. Spread LAST so nothing shadows them."""
    if not _is_deploy_job(job_path):
        return {"forbidden_to_run": False}
    return {"forbidden_to_run": True, "never_run_notice": _FORBID_NOTICE}


# --- job path handling -------------------------------------------------------


class JenkinsPathError(ValueError):
    """Raised when a caller-supplied job path or build number is unsafe."""


_BUILD_ALIASES = (
    "lastBuild",
    "lastSuccessfulBuild",
    "lastFailedBuild",
    "lastCompletedBuild",
    "lastStableBuild",
    "lastUnstableBuild",
    "lastUnsuccessfulBuild",
)
_BUILD_NUMBER_RE = re.compile(rf"^(?:\d{{1,9}}|{'|'.join(_BUILD_ALIASES)})$")

_BAD_SEGMENT_CHARS = ("\\", "?", "#", "\n", "\r", "\t", "\x00")

# Mutating / secret-bearing routes. Layer 2 (the anchored allowlist) already
# excludes these; this is the belt-and-braces layer.
_DENY_SUBPATHS = (
    "build",
    "buildwithparameters",
    "stop",
    "term",
    "kill",
    "cancelitem",
    "cancelqueue",
    "dodelete",
    "createitem",
    "config.xml",
    "scripttext",
    "script",
    "quietdown",
    "cancelquietdown",
    "restart",
    "saferestart",
    "exit",
    "reload",
    "toggleoffline",
    "disable",
    "enable",
    "submitdescription",
    "crumbissuer",
    "descriptorbyname",
)


def _normalize_job_path(job_path: str) -> str:
    """Canonicalise any spelling of a job reference into 'folder/sub/job'.

    Accepts a full browser URL, a /job/a/job/b path, a /view/<name>/ filtered
    URL, or a plain folder-relative path. Percent-decodes, strips /view/
    segments (a view is a saved filter, not a container), and rejects traversal.
    """
    if not isinstance(job_path, str):
        raise JenkinsPathError("job_path must be a string")

    raw = job_path.strip()
    if not raw:
        raise JenkinsPathError("job_path is empty")

    if raw.lower().startswith(("http://", "https://")):
        raw = urlsplit(raw).path

    raw = unquote(raw)
    # a second decode catches double-encoded traversal (%252e%252e)
    if "%" in raw:
        raw = unquote(raw)

    segments = []
    skip_next = False
    for seg in raw.split("/"):
        if skip_next:
            skip_next = False
            continue
        if not seg:
            continue
        low = seg.lower()
        if low == "job":
            continue
        if low == "view":
            skip_next = True  # drop 'view' AND the view name that follows
            continue
        if seg != seg.strip():
            raise JenkinsPathError(f"job_path segment {seg!r} has surrounding whitespace")
        if seg in (".", ".."):
            raise JenkinsPathError(f"job_path segment {seg!r} is path traversal")
        if any(c in seg for c in _BAD_SEGMENT_CHARS):
            raise JenkinsPathError(f"job_path segment {seg!r} contains an illegal character")
        segments.append(seg)

    if not segments:
        raise JenkinsPathError(f"job_path {job_path!r} resolved to nothing")

    for seg in segments:
        if seg.lower() in _DENY_SUBPATHS:
            raise JenkinsPathError(
                f"job_path segment {seg!r} is a Jenkins action route, not a job name. "
                f"This server is read-only and refuses it."
            )

    return "/".join(segments)


def _validate_build_number(build_number: str) -> str:
    bn = str(build_number).strip()
    if not _BUILD_NUMBER_RE.match(bn):
        raise JenkinsPathError(
            f"build_number {build_number!r} must be digits or one of {_BUILD_ALIASES}"
        )
    return bn


def _job_path_to_rest(job_path: str) -> str:
    """'tpap/Build-jobs/x' -> '/job/tpap/job/Build-jobs/job/x' (already normalized)."""
    return "".join(f"/job/{seg}" for seg in job_path.split("/"))


# --- layer 2: the anchored read-endpoint allowlist ---------------------------

_JOB_PREFIX = r"(?:/job/[^/]+)+"
_BUILD_REF = rf"(?:\d{{1,9}}|{'|'.join(_BUILD_ALIASES)})"

_ALLOWED_ENDPOINT_RE = re.compile(
    "|".join(
        (
            r"^/api/json$",
            r"^/whoAmI/api/json$",
            r"^/queue/api/json$",
            r"^/computer/api/json$",
            rf"^{_JOB_PREFIX}/api/json$",
            rf"^{_JOB_PREFIX}/{_BUILD_REF}/api/json$",
            rf"^{_JOB_PREFIX}/{_BUILD_REF}/consoleText$",
            rf"^{_JOB_PREFIX}/{_BUILD_REF}/logText/progressiveText$",
        )
    )
)


def _assert_read_only_endpoint(url_path: str) -> None:
    if not _ALLOWED_ENDPOINT_RE.match(url_path):
        raise JenkinsPathError(
            f"refusing {url_path!r}: not on the read-only endpoint allowlist. "
            f"This server can only reach /api/json, /consoleText and "
            f"/logText/progressiveText."
        )
    tail = url_path.rsplit("/", 1)[-1].lower()
    if tail in _DENY_SUBPATHS:
        raise JenkinsPathError(f"refusing {url_path!r}: {tail!r} is a mutating route")


# --- the single HTTP call site -----------------------------------------------

_STRIP_HEADERS = ("x-http-method-override", "x-method-override", "x-httpmethod")


def _request(path: str, params: dict | None = None) -> httpx.Response:
    """The ONLY outbound HTTP call in this module. GET, always."""
    _assert_read_only_endpoint(path)
    headers = {"Accept": "application/json, text/plain, */*"}
    for h in _STRIP_HEADERS:
        headers.pop(h, None)  # dormant guard: nothing supplies headers today
    return httpx.get(
        f"{JENKINS_URL}{path}",
        auth=AUTH,
        params=params,
        timeout=TIMEOUT,
        headers=headers,
        follow_redirects=False,
    )


def _err(status: int, what: str, job_path: str = "") -> str:
    """Structured error. Carries the never-run marker too, so a 403/404 on a
    deploy job still warns — an error response must never be the one reply that
    drops the marker."""
    hints = {
        401: "authentication failed — check TPAP_PROD_JENKINS_TOKEN in ~/.zshrc",
        403: "authorised but forbidden — the service account cannot see this",
        404: "not found — check the job path (folder-relative, e.g. tpap/Build-jobs/tpap-consumers)",
    }
    return json.dumps(
        {
            "error": f"HTTP {status} fetching {what}",
            "hint": hints.get(status, ""),
            **(_forbid_fields(job_path) if job_path else {}),
        },
        indent=2,
    )


def _guard(fn):
    """Turn JenkinsPathError into a structured error instead of a stack trace."""

    # functools.wraps exposes fn's signature; without it FastMCP builds an
    # (args, kwargs) input schema and every tool becomes uncallable.
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except JenkinsPathError as e:
            return json.dumps({"error": str(e), "read_only": True}, indent=2)
        except httpx.HTTPError as e:
            return json.dumps({"error": f"{type(e).__name__}: {e}"}, indent=2)

    return wrapper


mcp = FastMCP("tpap_prod_jenkins")


# --- tools -------------------------------------------------------------------


@mcp.tool()
@_guard
def check_connection() -> str:
    """
    Verify the TPAP prod Jenkins credentials and report the read-only posture.

    Reports the authenticated identity, where the token was resolved from, and
    the complete list of tools this server exposes (all reads — there is no
    trigger tool).
    """
    r = _request("/whoAmI/api/json")
    if r.status_code != 200:
        return _err(r.status_code, "/whoAmI/api/json")
    d = r.json()
    return json.dumps(
        {
            "jenkins_url": JENKINS_URL,
            "authenticated": d.get("authenticated"),
            "identity": d.get("name"),
            "configured_user": JENKINS_USER,
            "token_source": _TOKEN_SOURCE,
            "authorities": [a for a in d.get("authorities", []) if not a.startswith("/")],
            "read_only": True,
            "write_tools": [],
            "tools": [
                "check_connection", "list_jobs", "search_jobs", "get_job_info",
                "get_build_status", "list_recent_builds", "get_console_log",
                "find_console_errors", "get_build_changes", "get_queue", "get_nodes",
            ],
            "guarantee": (
                "This server has no trigger/build/stop/delete tool. It contains exactly one "
                "httpx.get() and no other HTTP verb. Every request path is checked against an "
                "anchored read-only allowlist before it is sent. No job can be executed through "
                "it, and *deploy* jobs must never be executed by any route."
            ),
        },
        indent=2,
    )


@mcp.tool()
@_guard
def list_jobs(folder_path: str = "") -> str:
    """
    List jobs and sub-folders under a Jenkins folder. Use for navigation.

    Args:
        folder_path: Folder path, e.g. "" (root), "tpap", or "tpap/Build-jobs".
    """
    if folder_path.strip():
        norm = _normalize_job_path(folder_path)
        path = f"{_job_path_to_rest(norm)}/api/json"
    else:
        norm = ""
        path = "/api/json"

    r = _request(path, params={"tree": "jobs[name,url,color,_class]"})
    if r.status_code != 200:
        return _err(r.status_code, path, norm)

    jobs = []
    for j in r.json().get("jobs", []):
        name = j.get("name", "")
        child = f"{norm}/{name}" if norm else name
        jobs.append(
            {
                "name": name,
                "job_path": child,
                "is_folder": "Folder" in j.get("_class", ""),
                "color": j.get("color"),
                **_forbid_fields(child),
            }
        )
    return json.dumps(
        {"folder_path": norm or "(root)", "count": len(jobs), "jobs": jobs}, indent=2
    )


@mcp.tool()
@_guard
def search_jobs(query: str, start_path: str = "", max_depth: int = 3) -> str:
    """
    Find jobs whose name contains a substring, walking the folder tree.

    Args:
        query: Case-insensitive substring to match against job names.
        start_path: Folder to start from, "" for the Jenkins root.
        max_depth: How many folder levels to descend (default 3, capped at 5).
    """
    q = query.strip().lower()
    if not q:
        raise JenkinsPathError("query is empty")
    depth_cap = max(1, min(int(max_depth), 5))

    matches, folders_walked, truncated = [], 0, False

    def walk(path: str, depth: int) -> None:
        nonlocal folders_walked, truncated
        if depth > depth_cap:
            truncated = True
            return
        if folders_walked >= 120:
            truncated = True
            return
        rest = f"{_job_path_to_rest(path)}/api/json" if path else "/api/json"
        resp = _request(rest, params={"tree": "jobs[name,url,color,_class]"})
        folders_walked += 1
        if resp.status_code != 200:
            return
        for j in resp.json().get("jobs", []):
            name = j.get("name", "")
            child = f"{path}/{name}" if path else name
            is_folder = "Folder" in j.get("_class", "")
            if q in name.lower():
                matches.append(
                    {
                        "job_path": child,
                        "name": name,
                        "is_folder": is_folder,
                        "color": j.get("color"),
                        "url": f"{JENKINS_URL}{_job_path_to_rest(child)}/",
                        **_forbid_fields(child),
                    }
                )
            if is_folder:
                walk(child, depth + 1)

    walk(_normalize_job_path(start_path) if start_path.strip() else "", 1)

    return json.dumps(
        {
            "query": query,
            "start_path": start_path or "(root)",
            "max_depth": depth_cap,
            "folders_walked": folders_walked,
            "truncated": truncated,
            "count": len(matches),
            "matches": matches,
        },
        indent=2,
    )


@mcp.tool()
@_guard
def get_job_info(job_path: str) -> str:
    """
    Get metadata for a job: buildable state, last build, next build number, parameters.

    Args:
        job_path: Folder-relative path, e.g. "tpap/Build-jobs/tpap-consumers".
            A full browser URL is also accepted and normalized.
    """
    norm = _normalize_job_path(job_path)
    path = f"{_job_path_to_rest(norm)}/api/json"
    r = _request(
        path,
        params={
            "tree": "displayName,description,buildable,nextBuildNumber,"
            "lastBuild[number,result,building,timestamp],"
            "property[parameterDefinitions[name,type,defaultParameterValue[value],choices]]"
        },
    )
    if r.status_code != 200:
        return _err(r.status_code, path, norm)
    d = r.json()

    params = []
    for prop in d.get("property", []):
        for pd in prop.get("parameterDefinitions", []) or []:
            params.append(
                {
                    "name": pd.get("name"),
                    "type": pd.get("type"),
                    "default": (pd.get("defaultParameterValue") or {}).get("value"),
                    "choices": pd.get("choices"),
                }
            )

    last = d.get("lastBuild") or {}
    return json.dumps(
        {
            "job_path": norm,
            "url": f"{JENKINS_URL}{_job_path_to_rest(norm)}/",
            "display_name": d.get("displayName"),
            "description": d.get("description"),
            "buildable": d.get("buildable"),
            "next_build_number": d.get("nextBuildNumber"),
            "last_build_number": last.get("number"),
            "last_build_result": last.get("result"),
            "last_build_building": last.get("building"),
            "parameters": params,
            **_forbid_fields(norm),
        },
        indent=2,
    )


@mcp.tool()
@_guard
def get_build_status(job_path: str, build_number: str = "lastBuild") -> str:
    """
    Get status/result/duration for one build.

    Args:
        job_path: Folder-relative job path.
        build_number: A build number, or "lastBuild" / "lastSuccessfulBuild" /
            "lastFailedBuild" / "lastCompletedBuild".
    """
    norm = _normalize_job_path(job_path)
    bn = _validate_build_number(build_number)
    path = f"{_job_path_to_rest(norm)}/{bn}/api/json"
    r = _request(
        path,
        params={
            "tree": "number,result,building,duration,timestamp,displayName,"
            "actions[parameters[name,value],causes[shortDescription,userName]]"
        },
    )
    if r.status_code != 200:
        return _err(r.status_code, path, norm)
    d = r.json()

    params, causes = {}, []
    for a in d.get("actions", []):
        for p in a.get("parameters", []) or []:
            params[p.get("name")] = p.get("value")
        for c in a.get("causes", []) or []:
            causes.append(c.get("shortDescription") or c.get("userName"))

    return json.dumps(
        {
            "job_path": norm,
            "build_number": d.get("number"),
            "result": d.get("result"),
            "building": d.get("building"),
            "duration_ms": d.get("duration"),
            "timestamp_ms": d.get("timestamp"),
            "url": f"{JENKINS_URL}{_job_path_to_rest(norm)}/{d.get('number')}/",
            "params": params,
            "causes": causes,
            **_forbid_fields(norm),
        },
        indent=2,
    )


@mcp.tool()
@_guard
def list_recent_builds(job_path: str, limit: int = 20) -> str:
    """
    List recent builds with status, duration and parameters, in one call.

    Jenkins' build-discarder policy caps how far back this can see; asking for
    more than the job retains just returns however many it has.

    Args:
        job_path: Folder-relative job path.
        limit: Max builds to return, newest first (default 20, capped at 100).
    """
    norm = _normalize_job_path(job_path)
    n = max(1, min(int(limit), 100))
    path = f"{_job_path_to_rest(norm)}/api/json"
    r = _request(
        path,
        params={
            "tree": f"builds[number,result,building,duration,timestamp,"
            f"actions[parameters[name,value]]]{{0,{n}}}"
        },
    )
    if r.status_code != 200:
        return _err(r.status_code, path, norm)

    builds = []
    for b in r.json().get("builds", []):
        params = {}
        for a in b.get("actions", []):
            for p in a.get("parameters", []) or []:
                params[p.get("name")] = p.get("value")
        builds.append(
            {
                "number": b.get("number"),
                "result": b.get("result"),
                "building": b.get("building"),
                "duration_ms": b.get("duration"),
                "timestamp_ms": b.get("timestamp"),
                "params": params,
            }
        )
    return json.dumps(
        {
            "job_path": norm,
            "returned": len(builds),
            "note": "Jenkins' build-discarder policy may retain fewer builds than `limit`.",
            "builds": builds,
            **_forbid_fields(norm),
        },
        indent=2,
    )


@mcp.tool()
@_guard
def get_console_log(
    job_path: str, build_number: str = "lastBuild", max_chars: int = 20000, tail: bool = True
) -> str:
    """
    Fetch a build's console output. Prod logs reach ~1.6MB, so this pages.

    Args:
        job_path: Folder-relative job path.
        build_number: Build number or alias (default "lastBuild").
        max_chars: How much of the log to return (default 20000, capped 200000).
        tail: True returns the END of the log (where failures are), False the start.
    """
    norm = _normalize_job_path(job_path)
    bn = _validate_build_number(build_number)
    cap = max(1000, min(int(max_chars), 200000))
    path = f"{_job_path_to_rest(norm)}/{bn}/consoleText"
    r = _request(path)
    if r.status_code != 200:
        return _err(r.status_code, path, norm)

    text = r.text
    total = len(text)
    if total > cap:
        chunk = text[-cap:] if tail else text[:cap]
        truncated = True
    else:
        chunk, truncated = text, False

    return json.dumps(
        {
            "job_path": norm,
            "build_number": bn,
            "total_chars": total,
            "returned_chars": len(chunk),
            "truncated": truncated,
            "segment": "tail" if tail else "head",
            "console": chunk,
            **_forbid_fields(norm),
        },
        indent=2,
    )


_DEFAULT_ERROR_RE = (
    r"(?i)\b(error|exception|failed|failure|fatal|caused by|"
    r"build step .* marked build as failure|"
    r"cannot find|no such file|permission denied|traceback|"
    r"BUILD FAILURE|COMPILATION ERROR|OutOfMemory|Connection refused|timed out)\b"
)


@mcp.tool()
@_guard
def find_console_errors(
    job_path: str,
    build_number: str = "lastBuild",
    pattern: str = "",
    context: int = 2,
    max_matches: int = 40,
) -> str:
    """
    Grep a build's console log for error lines — the fastest way to see why it failed.

    Args:
        job_path: Folder-relative job path.
        build_number: Build number or alias (default "lastBuild").
        pattern: Custom Python regex. Empty uses a built-in error/exception pattern.
        context: Lines of context to include either side of each match (default 2, max 10).
        max_matches: Cap on reported matches (default 40, max 200).
    """
    norm = _normalize_job_path(job_path)
    bn = _validate_build_number(build_number)
    ctx = max(0, min(int(context), 10))
    cap = max(1, min(int(max_matches), 200))

    try:
        rx = re.compile(pattern) if pattern.strip() else re.compile(_DEFAULT_ERROR_RE)
    except re.error as e:
        raise JenkinsPathError(f"bad regex {pattern!r}: {e}")

    path = f"{_job_path_to_rest(norm)}/{bn}/consoleText"
    r = _request(path)
    if r.status_code != 200:
        return _err(r.status_code, path, norm)

    lines = r.text.splitlines()
    hits, total_hits = [], 0
    for i, line in enumerate(lines):
        if not rx.search(line):
            continue
        total_hits += 1
        if len(hits) >= cap:
            continue
        lo, hi = max(0, i - ctx), min(len(lines), i + ctx + 1)
        hits.append(
            {
                "line_number": i + 1,
                "match": line[:500],
                "context": [l[:500] for l in lines[lo:hi]],
            }
        )

    return json.dumps(
        {
            "job_path": norm,
            "build_number": bn,
            "pattern": pattern or "(built-in error pattern)",
            "total_lines": len(lines),
            "total_matches": total_hits,
            "returned_matches": len(hits),
            "truncated": total_hits > len(hits),
            "matches": hits,
            **_forbid_fields(norm),
        },
        indent=2,
    )


@mcp.tool()
@_guard
def get_build_changes(job_path: str, build_number: str = "lastBuild") -> str:
    """
    Get the SCM changeset for a build — which commits went in, by whom.

    Args:
        job_path: Folder-relative job path.
        build_number: Build number or alias (default "lastBuild").
    """
    norm = _normalize_job_path(job_path)
    bn = _validate_build_number(build_number)
    path = f"{_job_path_to_rest(norm)}/{bn}/api/json"
    r = _request(
        path,
        params={
            "tree": "number,result,changeSet[kind,items[commitId,msg,author[fullName],"
            "timestamp,affectedPaths]]"
        },
    )
    if r.status_code != 200:
        return _err(r.status_code, path, norm)
    d = r.json()

    cs = d.get("changeSet") or {}
    items = []
    for it in cs.get("items", []) or []:
        items.append(
            {
                "commit": (it.get("commitId") or "")[:12],
                "author": (it.get("author") or {}).get("fullName"),
                "message": it.get("msg"),
                "timestamp_ms": it.get("timestamp"),
                "files_changed": len(it.get("affectedPaths") or []),
            }
        )

    return json.dumps(
        {
            "job_path": norm,
            "build_number": d.get("number"),
            "result": d.get("result"),
            "scm_kind": cs.get("kind"),
            "change_count": len(items),
            "changes": items,
            "note": "empty changeSet is normal for parameter-triggered builds",
            **_forbid_fields(norm),
        },
        indent=2,
    )


@mcp.tool()
@_guard
def get_queue() -> str:
    """List items currently queued on this Jenkins (what is waiting to run)."""
    r = _request("/queue/api/json", params={"tree": "items[id,why,stuck,blocked,task[name,url]]"})
    if r.status_code != 200:
        return _err(r.status_code, "/queue/api/json")
    items = []
    for it in r.json().get("items", []):
        task = it.get("task") or {}
        items.append(
            {
                "id": it.get("id"),
                "job": task.get("name"),
                "why": it.get("why"),
                "stuck": it.get("stuck"),
                "blocked": it.get("blocked"),
            }
        )
    return json.dumps({"queued": len(items), "items": items}, indent=2)


@mcp.tool()
@_guard
def get_nodes() -> str:
    """List build nodes/agents with online state and executor counts."""
    r = _request(
        "/computer/api/json",
        params={"tree": "computer[displayName,offline,temporarilyOffline,numExecutors,"
                        "offlineCauseReason]"},
    )
    if r.status_code != 200:
        return _err(r.status_code, "/computer/api/json")
    nodes = [
        {
            "name": c.get("displayName"),
            "offline": c.get("offline"),
            "temporarily_offline": c.get("temporarilyOffline"),
            "executors": c.get("numExecutors"),
            "offline_reason": c.get("offlineCauseReason") or None,
        }
        for c in r.json().get("computer", [])
    ]
    return json.dumps(
        {"count": len(nodes), "offline": sum(1 for n in nodes if n["offline"]), "nodes": nodes},
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()
