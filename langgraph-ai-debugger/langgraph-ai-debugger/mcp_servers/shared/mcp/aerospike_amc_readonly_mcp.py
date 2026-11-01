#!/usr/bin/env python3
"""Aerospike Management Console (AMC) MCP — STRICTLY READ-ONLY.

Community Edition AMC for one estate, chosen by argv[1] ("tpap" or "tsp"):

    python3 aerospike_amc_readonly_mcp.py tpap
    python3 aerospike_amc_readonly_mcp.py tsp

The browser URL hash (#dashboard/<seed>/60/<nodes>) is not an API. This server
talks to the AMC REST API the page uses:

    POST /aerospike/service/clusters/get-cluster-id   form seed_node=<ip:port>
    GET  /aerospike/service/clusters/<uuid>/basic
    GET  /aerospike/service/clusters/<uuid>/nodes/<ip:port>,...
    GET  /aerospike/service/clusters/<uuid>/throughput
    GET  /aerospike/service/clusters/<uuid>/namespaces/<name>[/nodes/<ip:port>,...]
    GET  /aerospike/service/clusters/<uuid>/nodes/<ip:port>/allstats
    GET  /aerospike/service/clusters/<uuid>/namespaces/<name>/nodes/<ip:port>/allstats
    GET  /aerospike/service/clusters/<uuid>/jobs/nodes/<ip:port>,...

These consoles are community edition and do not require a username or password.
The POST only opens an in-memory monitoring session (amc_session cookie). It
does not change the Aerospike cluster.

=== WHY THIS SERVER CANNOT WRITE ===

AMC also exposes fire_cmd (asinfo, including sets), backups, restores, user
admin, and config update. None of those tools exist here.

  1. The only POST is _open_session(), and its URL and body are constants:
     path /aerospike/service/clusters/get-cluster-id, form field seed_node
     only. No tool can add a password, a command, or another field.
  2. Every GET is built from validated pieces (uuid, IPv4:port, namespace),
     then matched against an anchored allowlist. Never a prefix match.
  3. _DENY_SUBSTRINGS refuses fire_cmd, backup, restore, logout, password,
     user admin, and config-update words anywhere in a decoded path.
  4. follow_redirects=False. No tool accepts a method, header map, or body.
  5. The session cookie stays in the httpx client. It is never logged or
     returned.

Credentials: none. URLs and seed nodes live in Agent-debugger/.env only
(TPAP_AMC_URL, TPAP_AMC_SEED, TSP_AMC_URL, TSP_AMC_SEED).
"""
from __future__ import annotations

import functools
import json
import logging
import os
import re
import sys
import threading
from pathlib import Path
from urllib.parse import unquote

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.disable(logging.INFO)

_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

_SYSTEMS = {
    "tpap": {
        "url_env": "TPAP_AMC_URL",
        "seed_env": "TPAP_AMC_SEED",
        "label": "TPAP",
    },
    "tsp": {
        "url_env": "TSP_AMC_URL",
        "seed_env": "TSP_AMC_SEED",
        "label": "TSP",
    },
}

SYSTEM = (sys.argv[1] if len(sys.argv) > 1 else os.getenv("AMC_SYSTEM", "")).strip().lower()
if SYSTEM not in _SYSTEMS:
    sys.stderr.write(
        f"aerospike_amc_readonly_mcp: first argument must be one of {sorted(_SYSTEMS)}, got {SYSTEM!r}\n"
    )
    sys.exit(2)

_CFG = _SYSTEMS[SYSTEM]
AMC_URL = (os.getenv(_CFG["url_env"]) or "").rstrip("/")
AMC_SEED = (os.getenv(_CFG["seed_env"]) or "").strip()
TIMEOUT = 25.0
MAX_BODY = 250_000

_SESSION_PATH = "/aerospike/service/clusters/get-cluster-id"
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_NS = re.compile(r"^[A-Za-z0-9_]{1,31}$")
_NODE = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})$")

# Refused anywhere in a decoded GET path. fire_cmd runs asinfo (including
# sets). The others create backups, users, or change AMC/cluster config.
_DENY_SUBSTRINGS = (
    "fire_cmd", "backup", "restore", "logout", "password", "add_user",
    "add_role", "drop_role", "drop_user", "get_all_users", "get_all_roles",
    "initiate", "session-terminate", "set-update-interval", "/update",
    "/remove", "change_password",
)

_GET_PATTERNS = (
    re.compile(r"^/get_amc_version$"),
    re.compile(r"^/get_current_monitoring_clusters$"),
    re.compile(rf"^/aerospike/service/clusters/{_UUID.pattern[1:-1]}/basic$"),
    re.compile(rf"^/aerospike/service/clusters/{_UUID.pattern[1:-1]}/throughput$"),
    re.compile(
        rf"^/aerospike/service/clusters/{_UUID.pattern[1:-1]}/nodes/"
        rf"(?:{_NODE.pattern[1:-1]})(?:,(?:{_NODE.pattern[1:-1]})){{0,31}}$"
    ),
    re.compile(
        rf"^/aerospike/service/clusters/{_UUID.pattern[1:-1]}/nodes/"
        rf"{_NODE.pattern[1:-1]}/allstats$"
    ),
    re.compile(
        rf"^/aerospike/service/clusters/{_UUID.pattern[1:-1]}/namespaces/"
        rf"{_NS.pattern[1:-1]}$"
    ),
    re.compile(
        rf"^/aerospike/service/clusters/{_UUID.pattern[1:-1]}/namespaces/"
        rf"{_NS.pattern[1:-1]}/nodes/"
        rf"(?:{_NODE.pattern[1:-1]})(?:,(?:{_NODE.pattern[1:-1]})){{0,31}}$"
    ),
    re.compile(
        rf"^/aerospike/service/clusters/{_UUID.pattern[1:-1]}/namespaces/"
        rf"{_NS.pattern[1:-1]}/nodes/{_NODE.pattern[1:-1]}/allstats$"
    ),
    re.compile(
        rf"^/aerospike/service/clusters/{_UUID.pattern[1:-1]}/jobs/nodes/"
        rf"(?:{_NODE.pattern[1:-1]})(?:,(?:{_NODE.pattern[1:-1]})){{0,31}}$"
    ),
)


class AmcPathError(ValueError):
    """A path failed validation and was never sent."""


class AmcConfigError(RuntimeError):
    """URL or seed node missing from .env."""


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


if not (AMC_URL and AMC_SEED):
    _log(
        f"[aerospike_amc {SYSTEM}] WARNING: {_CFG['url_env']} / {_CFG['seed_env']} "
        f"missing in {_ENV_PATH}"
    )


def _node(value: str) -> str:
    text = (value or "").strip()
    match = _NODE.match(text)
    if not match:
        raise AmcPathError(f"invalid node {value!r}; expected IPv4:port")
    octets = [int(match.group(i)) for i in range(1, 5)]
    port = int(match.group(5))
    if any(o > 255 for o in octets) or not 1 <= port <= 65535:
        raise AmcPathError(f"invalid node {value!r}")
    return text


def _nodes(values: list[str]) -> str:
    if not values or len(values) > 32:
        raise AmcPathError("node list must contain 1 to 32 addresses")
    return ",".join(_node(v) for v in values)


def _namespace(value: str) -> str:
    text = (value or "").strip()
    if not _NS.match(text):
        raise AmcPathError(f"invalid namespace {value!r}")
    return text


def _uuid(value: str) -> str:
    text = (value or "").strip()
    if not _UUID.match(text):
        raise AmcPathError(f"invalid cluster id {value!r}")
    return text


def _decode(path: str) -> str:
    cur = path
    for _ in range(2):
        nxt = unquote(cur)
        if nxt == cur:
            break
        cur = nxt
    return cur


def _assert_get(path: str) -> str:
    if any(c in path for c in "\r\n?#\\") or "://" in path or path.startswith("//"):
        raise AmcPathError(f"refusing path {path!r}")
    decoded = _decode(path)
    if any(c in decoded for c in "\r\n?#\\") or "://" in decoded or ".." in decoded.split("/"):
        raise AmcPathError(f"refusing decoded path {decoded!r}")
    lowered = decoded.lower()
    if any(word in lowered for word in _DENY_SUBSTRINGS):
        raise AmcPathError(f"refusing {decoded!r}: not a read route")
    if not any(pat.fullmatch(decoded) for pat in _GET_PATTERNS):
        raise AmcPathError(f"refusing {decoded!r}: not on the GET allowlist")
    return decoded


def _json_error(message: str) -> str:
    return json.dumps({"error": message, "system": SYSTEM, "read_only": True}, indent=2)


def _parse(resp: httpx.Response) -> object:
    text = resp.text or ""
    if len(text) > MAX_BODY:
        text = text[:MAX_BODY]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"status_code": resp.status_code, "body": text[:2000]}


class _Amc:
    """One httpx client. The cookie jar is the AMC session."""

    def __init__(self) -> None:
        self._client = httpx.Client(timeout=TIMEOUT, follow_redirects=False)
        self._lock = threading.Lock()
        self.cluster_id: str | None = None
        self.nodes: list[str] = []
        self.build: str | None = None

    def _require_config(self) -> None:
        if not AMC_URL or not AMC_SEED:
            raise AmcConfigError(
                f"set {_CFG['url_env']} and {_CFG['seed_env']} in {_ENV_PATH}"
            )

    def open_session(self) -> dict:
        """The only POST. URL and body are fixed: seed_node and nothing else."""
        self._require_config()
        seed = _node(AMC_SEED)
        resp = self._client.post(
            f"{AMC_URL}{_SESSION_PATH}",
            data={"seed_node": seed},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        payload = _parse(resp)
        if resp.status_code >= 400 or not isinstance(payload, dict) or not payload.get("cluster_id"):
            raise AmcPathError(
                f"session open failed HTTP {resp.status_code}: "
                f"{json.dumps(payload)[:300]}"
            )
        self.cluster_id = _uuid(str(payload["cluster_id"]))
        self.nodes = [_node(n) for n in payload.get("nodes") or []]
        details = payload.get("build_details") or {}
        self.build = details.get("latest_build_no")
        return payload

    def ensure(self) -> None:
        if self.cluster_id and self.nodes:
            return
        self.open_session()

    def get(self, path: str, *, session: bool = True) -> object:
        """The only GET. path must already be an allowlisted AMC read route."""
        self._require_config()
        safe = _assert_get(path)
        with self._lock:
            if session:
                self.ensure()
            resp = self._client.get(f"{AMC_URL}{safe}")
            if session and resp.status_code == 401:
                self.cluster_id = None
                self.nodes = []
                self.open_session()
                safe = _assert_get(path)
                resp = self._client.get(f"{AMC_URL}{safe}")
        if resp.status_code >= 400:
            return {
                "error": f"HTTP {resp.status_code}",
                "path": safe,
                "body": _parse(resp),
            }
        return _parse(resp)

    def cluster_path(self, suffix: str) -> str:
        self.ensure()
        return f"/aerospike/service/clusters/{self.cluster_id}{suffix}"


_AMC = _Amc()


def _guard(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (AmcPathError, AmcConfigError) as exc:
            return _json_error(str(exc))
        except httpx.HTTPError as exc:
            return _json_error(f"{type(exc).__name__}: {exc}")

    return wrapped


def _filter_stats(stats: object, contains: str) -> object:
    if not isinstance(stats, dict) or "error" in stats:
        return stats
    needle = (contains or "").strip()
    if not needle:
        return stats
    if len(needle) > 80 or any(c in needle for c in "\r\n"):
        raise AmcPathError("contains filter is too long")
    matched = {k: v for k, v in stats.items() if needle.lower() in str(k).lower()}
    return {
        "contains": needle,
        "matched": len(matched),
        "stats": matched,
    }


def _throughput(payload: object) -> dict:
    if not isinstance(payload, dict) or "error" in payload:
        return payload if isinstance(payload, dict) else {"error": payload}
    series = {}
    for key, per_node in payload.items():
        if key == "cluster_status" or not isinstance(per_node, dict):
            continue
        total = 0.0
        successful = 0.0
        nodes = {}
        for node, point in per_node.items():
            if not isinstance(point, dict):
                continue
            # AMC plots y as the success series and secondary as the total series.
            successful += float(point.get("y") or 0)
            total += float(point.get("secondary") or 0)
            nodes[node] = {
                "total": float(point.get("secondary") or 0),
                "successful": float(point.get("y") or 0),
            }
        series[key] = {"total": total, "successful": successful, "per_node": nodes}
    return {
        "cluster_status": payload.get("cluster_status"),
        "note": "AMC plots y as successful TPS and secondary as total TPS.",
        "series": series,
    }


mcp = FastMCP(
    f"aerospike_amc_{SYSTEM}",
    instructions=(
        f"Read-only Aerospike Management Console for {_CFG['label']}. "
        f"URL and seed come from {_CFG['url_env']} / {_CFG['seed_env']}. "
        "Use get_cluster_summary and list_nodes first, then get_throughput, "
        "list_namespaces, or get_node_stats. This server cannot run asinfo, "
        "change config, start a job, or take a backup."
    ),
)


@mcp.tool()
@_guard
def check_connection() -> str:
    """Open an AMC session and report version, cluster id, build, and node count.

    Proves the console is reachable. Does not change the Aerospike cluster.
    """
    version = _AMC.get("/get_amc_version", session=False)
    session = _AMC.open_session()
    return json.dumps(
        {
            "ok": True,
            "read_only": True,
            "system": SYSTEM,
            "amc_url": AMC_URL,
            "seed_node": _node(AMC_SEED),
            "amc_type": (version or {}).get("amc_type") if isinstance(version, dict) else None,
            "cluster_id": _AMC.cluster_id,
            "build": _AMC.build,
            "node_count": len(_AMC.nodes),
            "nodes": _AMC.nodes,
            "cluster_id_from_session": session.get("cluster_id"),
            "note": "GET after a session POST of seed_node only. No asinfo, backup, or config change exists.",
        },
        indent=2,
    )


@mcp.tool()
@_guard
def get_cluster_summary() -> str:
    """Cluster overview: build, namespace names, node list, disk and RAM used/free."""
    payload = _AMC.get(_AMC.cluster_path("/basic"))
    return json.dumps({"system": SYSTEM, "cluster_id": _AMC.cluster_id, "basic": payload}, indent=2)


@mcp.tool()
@_guard
def list_nodes() -> str:
    """Per-node dashboard row: status, objects, disk, RAM, client connections, migrations."""
    if not _AMC.nodes:
        _AMC.ensure()
    payload = _AMC.get(_AMC.cluster_path(f"/nodes/{_nodes(_AMC.nodes)}"))
    return json.dumps({"system": SYSTEM, "cluster_id": _AMC.cluster_id, "nodes": payload}, indent=2)


@mcp.tool()
@_guard
def get_throughput() -> str:
    """Current read/write/query/scan/udf/batch/xdr TPS. y is successful, secondary is total."""
    payload = _throughput(_AMC.get(_AMC.cluster_path("/throughput")))
    payload["system"] = SYSTEM
    payload["cluster_id"] = _AMC.cluster_id
    return json.dumps(payload, indent=2)


@mcp.tool()
@_guard
def list_namespaces() -> str:
    """Namespace names plus the cluster-wide stats AMC shows for each."""
    basic = _AMC.get(_AMC.cluster_path("/basic"))
    names = basic.get("namespaces") if isinstance(basic, dict) else None
    if not isinstance(names, list):
        return json.dumps({"system": SYSTEM, "basic": basic}, indent=2)
    out = []
    for name in names:
        ns = _namespace(str(name))
        out.append({"namespace": ns, "stats": _AMC.get(_AMC.cluster_path(f"/namespaces/{ns}"))})
    return json.dumps(
        {"system": SYSTEM, "cluster_id": _AMC.cluster_id, "namespaces": out},
        indent=2,
    )


@mcp.tool()
@_guard
def get_namespace(namespace: str) -> str:
    """Cluster-wide stats for one namespace (objects, disk, RAM, TTL, availability)."""
    ns = _namespace(namespace)
    payload = _AMC.get(_AMC.cluster_path(f"/namespaces/{ns}"))
    return json.dumps({"system": SYSTEM, "namespace": ns, "stats": payload}, indent=2)


@mcp.tool()
@_guard
def get_namespace_nodes(namespace: str) -> str:
    """Per-node stats for one namespace. Use this when one node looks hotter than the others."""
    ns = _namespace(namespace)
    if not _AMC.nodes:
        _AMC.ensure()
    payload = _AMC.get(_AMC.cluster_path(f"/namespaces/{ns}/nodes/{_nodes(_AMC.nodes)}"))
    return json.dumps({"system": SYSTEM, "namespace": ns, "nodes": payload}, indent=2)


@mcp.tool()
@_guard
def get_node_stats(node: str, contains: str = "") -> str:
    """Raw service stats for one node (allstats). contains filters stat names, case-insensitive."""
    address = _node(node)
    payload = _filter_stats(_AMC.get(_AMC.cluster_path(f"/nodes/{address}/allstats")), contains)
    return json.dumps({"system": SYSTEM, "node": address, "stats": payload}, indent=2)


@mcp.tool()
@_guard
def get_namespace_stats(namespace: str, node: str, contains: str = "") -> str:
    """Raw namespace stats for one node. contains filters stat names, case-insensitive."""
    ns = _namespace(namespace)
    address = _node(node)
    payload = _filter_stats(
        _AMC.get(_AMC.cluster_path(f"/namespaces/{ns}/nodes/{address}/allstats")),
        contains,
    )
    return json.dumps(
        {"system": SYSTEM, "namespace": ns, "node": address, "stats": payload},
        indent=2,
    )


@mcp.tool()
@_guard
def list_jobs() -> str:
    """Running AMC jobs (scans). Read-only: this cannot start or stop a job."""
    if not _AMC.nodes:
        _AMC.ensure()
    payload = _AMC.get(_AMC.cluster_path(f"/jobs/nodes/{_nodes(_AMC.nodes)}"))
    return json.dumps({"system": SYSTEM, "cluster_id": _AMC.cluster_id, "jobs": payload}, indent=2)


if __name__ == "__main__":
    mcp.run()
