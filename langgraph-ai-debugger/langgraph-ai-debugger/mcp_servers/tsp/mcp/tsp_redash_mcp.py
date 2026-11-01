#!/usr/bin/env python3
"""Redash MCP server for tsp — sharded switchv2 (C1/C2/C3/C6), SQL execution and schema exploration."""

import os
import sys
import time
import json
import logging
import httpx
from mcp.server.fastmcp import FastMCP

# Cursor treats MCP stderr INFO as errors and may hide the server from the agent.
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.disable(logging.INFO)

MAGENTA = "\033[95m"
RESET = "\033[0m"

def _log(msg: str) -> None:
    print(f"{MAGENTA}{msg}{RESET}", file=sys.stderr, flush=True)

REDASH_BASE_URL = os.environ.get("TSP_REDASH_URL", "https://paytmybl-redash.paytmybl.com")
REDASH_API_KEY = os.environ.get("TSP_REDASH_API_KEY", "")  # from .env, never hard-coded

HEADERS = {"Authorization": f"Key {REDASH_API_KEY}", "Content-Type": "application/json"}
DEFAULT_MAX_ROWS = 100
POLL_INTERVAL_SEC = 1.5

# run_sql waits this long for a query to EXECUTE before giving up. Redash queries can hang
# for minutes on an unbounded scan, which stalls a debugging session — fail fast by default
# and let the caller opt into a longer wait for a query known to be heavy.
DEFAULT_TIMEOUT_SEC = 20
MAX_TIMEOUT_SEC = 120

# db_name → Redash data_source_id
DB_NAME_TO_ID: dict[str, int] = {
    "switchv2_C1": 22,
    "switchv2_C2": 21,
    "switchv2_C3": 19,
    "switchv2_C6": 14,
    "Config_UPI_Jobs": 16,
}

# Shards to fan-out to when no specific shard requested (excludes non-sharded DBs)
ALL_SHARDS = ["switchv2_C1", "switchv2_C2", "switchv2_C3", "switchv2_C6"]

mcp = FastMCP("tsp_redash")


def _resolve_db(db_name: str) -> int:
    ds_id = DB_NAME_TO_ID.get(db_name)
    if ds_id is None:
        available = ", ".join(DB_NAME_TO_ID.keys())
        raise ValueError(f"Unknown db_name '{db_name}'. Available: {available}")
    return ds_id


class RedashTimeout(Exception):
    """Query outlived the caller's timeout_sec budget. It keeps running on Redash."""


def _clamp_timeout(timeout_sec) -> int:
    try:
        timeout_sec = int(timeout_sec)
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT_SEC
    return max(1, min(timeout_sec, MAX_TIMEOUT_SEC))


def _timeout_payload(timeout_sec: int) -> dict:
    return {
        "error": f"Query did not finish within timeout_sec={timeout_sec}s.",
        "timed_out": True,
        "timeout_sec": timeout_sec,
        "hint": (
            "If it is not found in 20s it will not be found in 5 minutes — do not retry "
            "unchanged or just raise timeout_sec. Rewrite it on an indexed key (primary key, "
            "txn_id, or a tight created_on/system_timestamp range — check with EXPLAIN), add "
            "LIMIT, or switch tools: ELK logs, Grafana metrics, PMM for DB health. "
            "txn_info and txn_participants keep only ~7 days; older rows are purged, not missing. "
            f"Raise timeout_sec (cap {MAX_TIMEOUT_SEC}) only for a query known to be heavy. "
            "The query is still running on Redash — it was not cancelled."
        ),
        "columns": [],
        "rows": [],
        "row_count": 0,
    }


def _get(path: str, params: dict | None = None, timeout: float = 30) -> dict:
    r = httpx.get(f"{REDASH_BASE_URL}{path}", headers=HEADERS, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict, timeout: float = 30) -> dict:
    r = httpx.post(f"{REDASH_BASE_URL}{path}", headers=HEADERS, json=body, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _poll_job(job_id: str, deadline: float) -> dict:
    while True:
        remaining = deadline - time.time()
        if remaining <= 0:
            raise RedashTimeout(job_id)
        data = _get(f"/api/jobs/{job_id}", timeout=min(30, max(1.0, remaining)))
        job = data.get("job", {})
        status = job.get("status")
        if status == 3:
            return job
        if status == 4:
            raise RuntimeError(f"Redash job failed: {job.get('error', 'unknown error')}")
        time.sleep(max(0.0, min(POLL_INTERVAL_SEC, deadline - time.time())))


def _extract_result(resp: dict, max_rows: int, deadline: float) -> dict:
    if "query_result" in resp:
        result = resp["query_result"]["data"]
    elif "job" in resp:
        job = _poll_job(resp["job"]["id"], deadline)
        qr_id = job.get("query_result_id")
        if not qr_id:
            raise RuntimeError("Job completed but no query_result_id returned")
        # The query finished inside the budget; downloading the stored result is not part of it.
        result = _get(f"/api/query_results/{qr_id}")["query_result"]["data"]
    else:
        return {"error": "Unexpected Redash response", "raw": resp}

    columns = [c["name"] for c in result.get("columns", [])]
    rows = result.get("rows", [])[:max_rows]
    return {"columns": columns, "rows": rows, "row_count": len(rows)}


def _run_on_shard(sql: str, db_name: str, max_rows: int, timeout_sec: int) -> dict:
    """Run sql on one shard. timeout_sec is the budget for THIS shard, not the fan-out."""
    ds_id = _resolve_db(db_name)
    _log(f"[tsp] shard={db_name} | timeout={timeout_sec}s | {sql.strip()}")
    deadline = time.time() + timeout_sec
    resp = _post("/api/query_results", {
        "query": sql,
        "data_source_id": ds_id,
        "max_age": 0,
    }, timeout=timeout_sec)
    result = _extract_result(resp, max_rows, deadline)
    result["shard"] = db_name
    return result


@mcp.tool()
def list_data_sources() -> str:
    """List all available shard names and their Redash IDs."""
    return json.dumps([
        {"db_name": name, "data_source_id": ds_id}
        for name, ds_id in DB_NAME_TO_ID.items()
    ], indent=2)


@mcp.tool()
def run_sql(sql: str, db_name: str = "", max_rows: int = DEFAULT_MAX_ROWS,
            timeout_sec: int = DEFAULT_TIMEOUT_SEC) -> str:
    """
    Execute a read-only SQL query on tsp sharded switchv2.

    Shards: switchv2_C1, switchv2_C2, switchv2_C3, switchv2_C6.
    Non-sharded: Config_UPI_Jobs (application_properties, business_properties).
    If db_name is omitted or empty, query runs on ALL switchv2 shards and results are merged.
    For Config_UPI_Jobs, specify db_name explicitly.
    See src/tsp/db_schema/schema.md for tables.

    Args:
        sql: SQL query. SELECT/SHOW/EXPLAIN/DESCRIBE/WITH only.
        db_name: Specific shard name. Leave empty to query all shards.
        max_rows: Max rows per shard (default 100, cap 500).
        timeout_sec: Seconds to wait for the query to execute, PER SHARD (default 20, cap 120).
            Leave at the default. Raise it only for a query known to be heavy, and say why.
            A lookup that finds nothing in 20s will not find it in 5 minutes either — rewrite
            it on an indexed key, or switch to logs/metrics. txn_info and txn_participants
            hold only ~7 days; older rows are purged.
    """
    sql_lower = sql.strip().lower()
    allowed = ("select", "show", "explain", "describe", "with")
    if not any(sql_lower.startswith(kw) for kw in allowed):
        return json.dumps({"error": "Only SELECT/SHOW/EXPLAIN/DESCRIBE/WITH queries allowed."})

    max_rows = min(max_rows, 500)
    timeout_sec = _clamp_timeout(timeout_sec)
    target_shards = [db_name] if db_name else ALL_SHARDS

    results = []
    for shard in target_shards:
        try:
            results.append(_run_on_shard(sql, shard, max_rows, timeout_sec))
        except (RedashTimeout, httpx.TimeoutException):
            results.append({**_timeout_payload(timeout_sec), "shard": shard})
        except Exception as e:
            results.append({"shard": shard, "error": str(e), "row_count": 0})

    if len(target_shards) == 1:
        return json.dumps(results[0], indent=2, default=str)

    return json.dumps({"shards": results}, indent=2, default=str)


@mcp.tool()
def list_queries(search: str = "", page: int = 1, page_size: int = 25) -> str:
    """
    List saved Redash queries. Optionally filter by name.

    Args:
        search: Filter queries by name substring (case-insensitive).
        page: Page number (1-indexed).
        page_size: Results per page (max 50).
    """
    page_size = min(page_size, 50)
    params = {"page": page, "page_size": page_size}
    if search:
        params["q"] = search
    data = _get("/api/queries", params)
    results = data.get("results", data) if isinstance(data, dict) else data
    rows = [
        {
            "id": q["id"],
            "name": q.get("name", ""),
            "db_name": next((n for n, i in DB_NAME_TO_ID.items() if i == q.get("data_source_id")), q.get("data_source_id")),
            "tags": q.get("tags", []),
            "updated_at": q.get("updated_at", ""),
        }
        for q in results
    ]
    return json.dumps(rows, indent=2)


@mcp.tool()
def get_query(query_id: int) -> str:
    """
    Get full details of a saved query including its SQL.

    Args:
        query_id: Redash query ID.
    """
    q = _get(f"/api/queries/{query_id}")
    ds_id = q.get("data_source_id")
    return json.dumps({
        "id": q["id"],
        "name": q.get("name"),
        "query": q.get("query"),
        "db_name": next((n for n, i in DB_NAME_TO_ID.items() if i == ds_id), ds_id),
        "tags": q.get("tags", []),
        "description": q.get("description"),
        "updated_at": q.get("updated_at"),
    }, indent=2)


@mcp.tool()
def get_table_schema(db_name: str = "switchv2_C1") -> str:
    """
    Get tables and columns for a named shard.

    Args:
        db_name: Shard name (default: switchv2_C1). All shards share the same schema.
    """
    try:
        ds_id = _resolve_db(db_name)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    data = _get(f"/api/data_sources/{ds_id}/schema")
    schema = data.get("schema", [])
    tables = [
        {"table": t.get("name"), "columns": [c.get("name") for c in t.get("columns", [])]}
        for t in schema
    ]
    return json.dumps(tables, indent=2)


if __name__ == "__main__":
    mcp.run()
