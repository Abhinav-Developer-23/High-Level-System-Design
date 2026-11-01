"""Async Redash client + SQL guard rails, used by the native DB tools in `db.py`.

The DB tools never connect to MySQL directly. They send SQL to Redash's HTTP API, which runs it
on a read replica and returns rows:

    POST /api/query_results {query, data_source_id, max_age: 0}
      → either the rows right away ({"query_result": ...})
      → or a job ({"job": {"id": ...}}) that we poll at /api/jobs/<id> until it finishes,
        then download /api/query_results/<id>

Safety lives in code here, not in the prompt:
  * `check_read_only` — only SELECT / SHOW / EXPLAIN / DESCRIBE / WITH, one statement, no
    write keywords (string literals are blanked first so `WHERE note = 'delete'` is fine);
  * `ensure_limit` — a SELECT without LIMIT gets one;
  * a 20 s default timeout (cap 120). A query that is not done by then is almost always an
    unbounded scan; the tool returns a hint instead of waiting.

Credentials come from `.env`: REDASH_BASE_URL / REDASH_API_KEY for TPAP and
TSP_REDASH_URL / TSP_REDASH_API_KEY for TSP.
"""

from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..config import env_file_values

# db_name → Redash data_source_id, per system. TSP's switchv2 is sharded per cluster.
DATA_SOURCES: dict[str, dict[str, int]] = {
    "tpap": {"switchv2": 1, "upi_config": 3},
    "tsp": {"switchv2_C1": 22, "switchv2_C2": 21, "switchv2_C3": 19, "switchv2_C6": 14, "Config_UPI_Jobs": 16},
}
TSP_SHARDS = ["switchv2_C1", "switchv2_C2", "switchv2_C3", "switchv2_C6"]
# Where a query goes when the caller names no database.
DEFAULT_DB = {"tpap": "switchv2", "tsp": None}  # None = every TSP shard, one after another

_ENV_KEYS = {"tpap": ("REDASH_BASE_URL", "REDASH_API_KEY"), "tsp": ("TSP_REDASH_URL", "TSP_REDASH_API_KEY")}

DEFAULT_TIMEOUT_SEC = 20
MAX_TIMEOUT_SEC = 120
MAX_ROWS = 500
POLL_INTERVAL_SEC = 1.5


class RedashError(RuntimeError):
    """Bad config, a rejected query, or a failed Redash job. ToolNode turns it into an error ToolMessage."""


# --------------------------------------------------------------------------------------------
# guard rails
# --------------------------------------------------------------------------------------------

_READ_ONLY_START = re.compile(r"^\s*(select|show|explain|describe|desc|with)\b", re.I)
# `replace` and `set` are left out on purpose: REPLACE() and CHARACTER SET appear in plain SELECTs,
# and a statement that starts with SELECT/WITH can't be REPLACE INTO / SET anyway.
_WRITE_WORD = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|rename|"
                         r"call|load|lock|unlock|handler|optimize|kill|outfile|dumpfile)\b", re.I)
_STRING = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"")
_COMMENT = re.compile(r"--[^\n]*|#[^\n]*|/\*.*?\*/", re.S)
_HAS_LIMIT = re.compile(r"\blimit\s+\d+", re.I)


def check_read_only(sql: str) -> str:
    """Return the trimmed SQL, or raise RedashError if it is not a single read-only statement."""
    body = sql.strip().rstrip(";").strip()
    # Blank out string literals and comments, so their contents can't trip (or hide from) the checks.
    bare = _COMMENT.sub(" ", _STRING.sub("''", body))
    if not _READ_ONLY_START.match(bare):
        raise RedashError("Only SELECT / SHOW / EXPLAIN / DESCRIBE / WITH queries are allowed.")
    if ";" in bare:
        raise RedashError("One statement per call: remove the ';' between statements.")
    if m := _WRITE_WORD.search(bare):
        raise RedashError(f"Write keyword {m.group(1).upper()!r} is not allowed; this tool is read-only.")
    return body


def ensure_limit(sql: str, max_rows: int) -> str:
    """Append `LIMIT max_rows` to a SELECT / WITH query that has none."""
    if re.match(r"^\s*(select|with)\b", sql, re.I) and not _HAS_LIMIT.search(sql):
        return f"{sql}\nLIMIT {max_rows}"
    return sql


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(int(value), high))


def timeout_payload(timeout_sec: int) -> dict[str, Any]:
    """What a timed-out query returns: a normal result with advice, not an exception."""
    return {
        "timed_out": True, "timeout_sec": timeout_sec, "rows": [], "row_count": 0,
        "hint": ("Not found in 20s means not found in 5 minutes. Rewrite on an indexed key (txn_id, "
                 "rrn, a tight created_on range; check with explain_sql), add LIMIT, or use logs / "
                 "metrics instead. txn_info and txn_participants keep only ~7 days. The query is "
                 "still running on Redash; do not fire it again unchanged."),
    }


# --------------------------------------------------------------------------------------------
# client
# --------------------------------------------------------------------------------------------

@dataclass
class RedashClient:
    """One Redash server (one per system). Build it with `RedashClient.for_system("tsp")`."""
    system: str
    base_url: str
    api_key: str = field(repr=False)

    @classmethod
    def for_system(cls, system: str) -> RedashClient:
        if system not in _ENV_KEYS:
            raise RedashError(f"No Redash for system {system!r}; expected tpap or tsp.")
        url_key, api_key_key = _ENV_KEYS[system]
        env = env_file_values()
        url, key = env.get(url_key, ""), env.get(api_key_key, "")
        if not url or not key:
            raise RedashError(f"{url_key} / {api_key_key} are not set in .env.")
        return cls(system, url.rstrip("/"), key)

    def databases(self) -> dict[str, int]:
        return DATA_SOURCES[self.system]

    def resolve(self, db_name: str | None) -> list[str]:
        """Database names a query should run on. None → the system default (all shards on TSP)."""
        name = db_name or DEFAULT_DB[self.system]
        if name is None:
            return list(TSP_SHARDS)
        if name not in self.databases():
            raise RedashError(f"Unknown db_name {name!r}. Available: {', '.join(self.databases())}")
        return [name]

    async def run(self, sql: str, db_name: str, *, max_rows: int = 100,
                  timeout_sec: int = DEFAULT_TIMEOUT_SEC) -> dict[str, Any]:
        """Run one read-only query on one database. Returns {columns, rows, row_count} or a timeout payload."""
        max_rows = clamp(max_rows, 1, MAX_ROWS)
        sql = ensure_limit(check_read_only(sql), max_rows)
        timeout_sec = clamp(timeout_sec, 1, MAX_TIMEOUT_SEC)
        ds_id = self.databases()[db_name]
        deadline = time.monotonic() + timeout_sec
        headers = {"Authorization": f"Key {self.api_key}"}
        async with httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=30) as http:
            try:
                r = await http.post("/api/query_results", timeout=timeout_sec,
                                    json={"query": sql, "data_source_id": ds_id, "max_age": 0})
                r.raise_for_status()
                resp = r.json()
                if "job" in resp:
                    data = await self._wait_for_job(http, resp["job"]["id"], deadline)
                elif "query_result" in resp:
                    data = resp["query_result"]["data"]
                else:
                    raise RedashError(f"Unexpected Redash response: {str(resp)[:300]}")
            except (TimeoutError, httpx.TimeoutException):
                return timeout_payload(timeout_sec)
        rows = data.get("rows", [])[:max_rows]
        return {"db": db_name, "columns": [c["name"] for c in data.get("columns", [])],
                "rows": rows, "row_count": len(rows)}

    async def _wait_for_job(self, http: httpx.AsyncClient, job_id: str, deadline: float) -> dict[str, Any]:
        """Poll a Redash job until it finishes, fails, or the deadline passes."""
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError(job_id)
            r = await http.get(f"/api/jobs/{job_id}")
            r.raise_for_status()
            job = r.json().get("job", {})
            if job.get("status") == 3:  # finished
                r = await http.get(f"/api/query_results/{job['query_result_id']}")
                r.raise_for_status()
                return r.json()["query_result"]["data"]
            if job.get("status") == 4:  # failed (bad SQL, unknown column…)
                raise RedashError(f"Query failed: {job.get('error', 'unknown error')}")
            await asyncio.sleep(max(0.0, min(POLL_INTERVAL_SEC, deadline - time.monotonic())))
