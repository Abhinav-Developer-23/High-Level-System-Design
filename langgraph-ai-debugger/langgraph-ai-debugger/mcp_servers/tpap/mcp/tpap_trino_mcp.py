#!/usr/bin/env python3
"""Strictly read-only TPAP Trino MCP for historical snapshot data.

This server exposes only saved-query references and the report scheduler's
query-preview endpoint. It intentionally has no report scheduling, editing,
deletion, activation, run-now, correction, or email capabilities.
Use matching TPAP/TSP Redash for ordinary DB work; use this server only when
required historical data is unavailable there or the user explicitly asks.

Results are returned verbatim: no column masking. The row ceiling is whatever
the upstream endpoint serves, reported back as ``preview_row_limit``.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import threading
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

_WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
_ENV_PATH = _WORKSPACE_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

BASE_URL = os.getenv("TECHOPS_AGENT_URL", "https://upi-ai-agent.paytm.com").rstrip("/")
EMAIL = os.getenv("TECHOPS_AGENT_EMAIL", "abhinav.anand@finmate.tech")
PASSWORD = os.getenv("TECHOPS_AGENT_PASSWORD", "")

_EXAMPLES_ENDPOINT = "/trino-report-scheduler/list"
_QUERY_ENDPOINT = "/trino-report-scheduler/test_query"
_ALLOWED_GET_ENDPOINTS = frozenset({_EXAMPLES_ENDPOINT})
_ALLOWED_POST_ENDPOINTS = frozenset({_QUERY_ENDPOINT})
_MAX_QUERY_LENGTH = 200_000


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().casefold() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    try:
        return max(minimum, int((os.getenv(name) or "").strip() or default))
    except ValueError:
        return default


# This MCP serves an authenticated internal operator who already holds direct
# Trino/Redash access to the same tables, so column redaction only breaks txn
# debugging (VPA, masked account, mobile, extended_info, scope_cust_id are
# exactly the fields a UPI investigation needs). Both guards are off/wide by
# default and can be restored per-environment.
_REDACT_SENSITIVE = _env_flag("TPAP_TRINO_REDACT_SENSITIVE", False)
_MAX_PREVIEW_ROWS = _env_int("TPAP_TRINO_MAX_PREVIEW_ROWS", 500)
_EXAMPLE_CACHE_SECONDS = 300.0

_LOGIN_TIMEOUT = httpx.Timeout(30.0, connect=15.0)
_QUERY_TIMEOUT = httpx.Timeout(180.0, connect=15.0)
_USER_AGENT = "Agent-Debugger-TPAP-Trino-Read-Only-MCP/1.0"

_FORBIDDEN_SQL_TOKENS = frozenset(
    {
        "ALTER",
        "ANALYZE",
        "CALL",
        "COMMIT",
        "CREATE",
        "DEALLOCATE",
        "DELETE",
        "DROP",
        "EXECUTE",
        "GRANT",
        "INSERT",
        "MERGE",
        "OPTIMIZE",
        "PREPARE",
        "REFRESH",
        "RENAME",
        "RESET",
        "REVOKE",
        "ROLLBACK",
        "SET",
        "START",
        "TRUNCATE",
        "UPDATE",
        "USE",
        "VACUUM",
    }
)
_ALLOWED_FIRST_TOKENS = frozenset({"SELECT", "WITH"})
_SNAPSHOT_TABLE_PATTERN = re.compile(
    r"\b(?:txn_info|txn_participants|metadata)_snapshot_v\d+\b",
    re.IGNORECASE,
)
_SNAPSHOT_BOUND_PATTERN = re.compile(
    r"\b(?:dl_last_updated|created_on|updated_on)\b|\btxn_id\s*=",
    re.IGNORECASE,
)
_SENSITIVE_COLUMN_PATTERN = re.compile(
    r"(?:account|mobile|phone|email|vpa|customer|cust_?id|device|ip_?address|"
    r"latitude|longitude|card|extended_?info|payload|metadata|detail)",
    re.IGNORECASE,
)

logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.disable(logging.INFO)

_client = httpx.Client(
    base_url=BASE_URL,
    follow_redirects=True,
    headers={
        "Accept": "application/json, */*",
        "User-Agent": _USER_AGENT,
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/trino-report-scheduler/",
    },
)
_auth_lock = threading.RLock()
_example_lock = threading.Lock()
_example_cache: tuple[float, list[dict[str, str]]] | None = None

mcp = FastMCP("tpap_trino")


def _log(message: str) -> None:
    """Log operational metadata only; never SQL, credentials, or query data."""
    print(f"[tpap_trino] {message}", file=sys.stderr, flush=True)


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def _error(message: str, **extra: Any) -> str:
    return _json({"error": message, **extra})


def _require_text(name: str, value: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{name} is required")
    return normalized


def _login() -> None:
    if not PASSWORD:
        raise RuntimeError(
            f"TECHOPS_AGENT_PASSWORD is not set. Add it to {_ENV_PATH}; "
            "the MCP never stores the resulting cookie on disk."
        )

    with _auth_lock:
        if _client.cookies.get("session"):
            return
        response = _client.post(
            "/login",
            data={"email": EMAIL, "password": PASSWORD},
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": f"{BASE_URL}/login",
            },
            timeout=_LOGIN_TIMEOUT,
        )
        response.raise_for_status()
        if not _client.cookies.get("session"):
            if "invalid email or password" in response.text.lower():
                raise RuntimeError(
                    "Trino login was rejected: invalid email or password. "
                    "Update TECHOPS_AGENT_PASSWORD in the workspace .env file."
                )
            raise RuntimeError("Trino login did not return a session cookie")
        _log("authenticated with a fresh in-memory session")


def _looks_unauthenticated(response: httpx.Response) -> bool:
    if response.status_code in (401, 403):
        return True
    content_type = response.headers.get("content-type", "").lower()
    return (
        "text/html" in content_type
        and (
            response.url.path.rstrip("/") == "/login"
            or 'name="password"' in response.text[:10_000].lower()
        )
    )


def _request(
    method: str,
    endpoint: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: httpx.Timeout = _QUERY_TIMEOUT,
) -> httpx.Response:
    normalized_method = method.upper()
    if normalized_method == "GET":
        if endpoint not in _ALLOWED_GET_ENDPOINTS:
            raise RuntimeError("Blocked non-read-only Trino GET endpoint")
    elif normalized_method == "POST":
        if endpoint not in _ALLOWED_POST_ENDPOINTS:
            raise RuntimeError("Blocked non-query Trino POST endpoint")
    else:
        raise RuntimeError(f"Blocked HTTP method: {normalized_method}")

    _login()
    response = _client.request(
        normalized_method,
        endpoint,
        json=payload,
        headers={"Content-Type": "application/json"} if payload is not None else None,
        timeout=timeout,
    )
    if _looks_unauthenticated(response):
        with _auth_lock:
            _client.cookies.clear()
        _login()
        response = _client.request(
            normalized_method,
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"} if payload is not None else None,
            timeout=timeout,
        )
    response.raise_for_status()
    return response


def _response_json(response: httpx.Response, endpoint: str) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(f"{endpoint} returned a non-JSON response") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{endpoint} returned an unexpected JSON value")
    return data


def _load_query_examples(*, refresh: bool = False) -> list[dict[str, str]]:
    global _example_cache
    now = time.monotonic()
    with _example_lock:
        if (
            not refresh
            and _example_cache is not None
            and now - _example_cache[0] < _EXAMPLE_CACHE_SECONDS
        ):
            return list(_example_cache[1])

        data = _response_json(
            _request("GET", _EXAMPLES_ENDPOINT),
            _EXAMPLES_ENDPOINT,
        )
        if not data.get("success"):
            raise RuntimeError(str(data.get("error") or "Could not load query examples"))

        examples: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for report in data.get("reports") or []:
            if not isinstance(report, dict):
                continue
            report_name = str(report.get("report_name") or "").strip()
            for query in report.get("queries") or []:
                if not isinstance(query, dict):
                    continue
                query_name = str(query.get("name") or "").strip()
                sql = str(query.get("query") or "").strip()
                if not query_name or not sql:
                    continue
                key = (query_name.casefold(), sql)
                if key in seen:
                    continue
                seen.add(key)
                examples.append(
                    {
                        "query_name": query_name,
                        "report_name": report_name,
                        "query": sql,
                    }
                )

        if not examples:
            raise RuntimeError("The Trino report list contained no query examples")
        examples.sort(key=lambda item: (item["query_name"].casefold(), item["report_name"]))
        _example_cache = (now, examples)
        return list(examples)


def _resolve_example(reference_query_name: str) -> dict[str, str]:
    wanted = _require_text("reference_query_name", reference_query_name).casefold()
    matches = [
        example
        for example in _load_query_examples()
        if example["query_name"].casefold() == wanted
    ]
    if not matches:
        raise ValueError(
            "reference_query_name was not found. Call list_query_examples and "
            "get_query_example before running Trino SQL."
        )
    if len(matches) > 1:
        unique_sql = {example["query"] for example in matches}
        if len(unique_sql) > 1:
            raise ValueError(
                "reference_query_name is ambiguous. Choose a unique example name."
            )
    return matches[0]


def _strip_literals_and_comments(sql: str) -> str:
    """Replace quoted text and comments while preserving SQL token positions."""
    output: list[str] = []
    index = 0
    state = "normal"
    while index < len(sql):
        char = sql[index]
        next_char = sql[index + 1] if index + 1 < len(sql) else ""

        if state == "normal":
            if char == "'":
                output.append(" ")
                state = "single"
            elif char == '"':
                output.append(" ")
                state = "double"
            elif char == "-" and next_char == "-":
                output.extend((" ", " "))
                index += 1
                state = "line_comment"
            elif char == "/" and next_char == "*":
                output.extend((" ", " "))
                index += 1
                state = "block_comment"
            else:
                output.append(char)
        elif state == "single":
            output.append("\n" if char == "\n" else " ")
            if char == "'" and next_char == "'":
                output.append(" ")
                index += 1
            elif char == "'":
                state = "normal"
        elif state == "double":
            output.append("\n" if char == "\n" else " ")
            if char == '"' and next_char == '"':
                output.append(" ")
                index += 1
            elif char == '"':
                state = "normal"
        elif state == "line_comment":
            output.append("\n" if char == "\n" else " ")
            if char == "\n":
                state = "normal"
        else:
            output.append("\n" if char == "\n" else " ")
            if char == "*" and next_char == "/":
                output.append(" ")
                index += 1
                state = "normal"
        index += 1

    if state in {"single", "double", "block_comment"}:
        raise ValueError("SQL contains an unterminated quote or block comment")
    return "".join(output)


def _validate_read_only_sql(query: str) -> dict[str, Any]:
    sql = _require_text("query", query)
    if len(sql) > _MAX_QUERY_LENGTH:
        raise ValueError(f"query exceeds {_MAX_QUERY_LENGTH} characters")
    if "\x00" in sql:
        raise ValueError("query contains a NUL byte")
    if re.search(r"\$[A-Za-z_0-9]*\$", sql):
        raise ValueError("Dollar-quoted SQL is not supported by the safety parser")

    stripped = _strip_literals_and_comments(sql)
    semicolons = [match.start() for match in re.finditer(";", stripped)]
    if len(semicolons) > 1:
        raise ValueError("Multiple SQL statements are not allowed")
    if semicolons and stripped[semicolons[0] + 1 :].strip():
        raise ValueError("Multiple SQL statements are not allowed")
    statement = stripped[: semicolons[0]] if semicolons else stripped

    tokens = re.findall(r"\b[A-Za-z_][A-Za-z_0-9$]*\b", statement.upper())
    if not tokens or tokens[0] not in _ALLOWED_FIRST_TOKENS:
        raise ValueError("Only SELECT and WITH statements are allowed")
    forbidden = sorted(set(tokens) & _FORBIDDEN_SQL_TOKENS)
    if forbidden:
        raise ValueError(
            "Blocked non-read-only or unsafe SQL token(s): " + ", ".join(forbidden)
        )

    if "FROM" in tokens and "WHERE" not in tokens and "LIMIT" not in tokens:
        raise ValueError("Table queries require a WHERE clause or LIMIT")
    if _SNAPSHOT_TABLE_PATTERN.search(statement):
        if "WHERE" not in tokens or not _SNAPSHOT_BOUND_PATTERN.search(statement):
            raise ValueError(
                "Snapshot-table queries require a WHERE clause plus a "
                "dl_last_updated/created_on/updated_on or txn_id bound"
            )

    return {
        "read_only": True,
        "first_token": tokens[0],
        "statement_count": 1,
        "snapshot_guard_applied": bool(_SNAPSHOT_TABLE_PATTERN.search(statement)),
    }


def _prepare_rows(columns: list[Any], rows: list[Any]) -> tuple[list[Any], list[str]]:
    """Trim rows to the preview cap, returning values verbatim by default.

    Redaction runs only when ``TPAP_TRINO_REDACT_SENSITIVE`` is set truthy.
    """
    trimmed = rows[:_MAX_PREVIEW_ROWS]
    if not _REDACT_SENSITIVE:
        return trimmed, []

    sensitive_indices = [
        index
        for index, column in enumerate(columns)
        if _SENSITIVE_COLUMN_PATTERN.search(str(column))
    ]
    sensitive_names = [str(columns[index]) for index in sensitive_indices]
    redacted: list[Any] = []
    for row in trimmed:
        if not isinstance(row, list):
            redacted.append(row)
            continue
        copy = list(row)
        for index in sensitive_indices:
            if index < len(copy) and copy[index] is not None:
                copy[index] = "[REDACTED]"
        redacted.append(copy)
    return redacted, sensitive_names


@mcp.tool()
def list_query_examples(search: str | None = None) -> str:
    """List saved Trino query examples without report/email/schedule metadata.

    Use Trino only for required historical data unavailable in the matching
    TPAP/TSP Redash, or when explicitly requested. Call this before writing a
    Trino query, then call ``get_query_example`` for the closest SQL pattern.
    """
    try:
        examples = _load_query_examples()
        term = (search or "").strip().casefold()
        if term:
            examples = [
                example
                for example in examples
                if term in example["query_name"].casefold()
                or term in example["report_name"].casefold()
                or term in example["query"].casefold()
            ]
        return _json(
            {
                "count": len(examples),
                "examples": [
                    {
                        "query_name": example["query_name"],
                        "report_name": example["report_name"],
                    }
                    for example in examples
                ],
                "next": "Call get_query_example with the closest query_name.",
            }
        )
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@mcp.tool()
def get_query_example(query_name: str) -> str:
    """Return one saved Trino SQL example, excluding all scheduler metadata."""
    try:
        example = _resolve_example(query_name)
        return _json(
            {
                **example,
                "usage": (
                    "Use this only as a Trino syntax/schema reference. Keep "
                    "partition/time filters when adapting it."
                ),
            }
        )
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc), query_name=query_name)


@mcp.tool()
def validate_query(query: str) -> str:
    """Validate one SQL statement locally against the strict read-only gate."""
    try:
        return _json(_validate_read_only_sql(query))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc), read_only=False)


@mcp.tool()
def run_query(
    query: str,
    query_name: str,
    reference_query_name: str,
) -> str:
    """Run one historical, strictly read-only Trino query.

    Rows are returned verbatim -- no column is masked or redacted, so VPA,
    masked_account_number, mobile, extended_info and scope_cust_id come back
    as stored and can be quoted directly in a debugging answer.

    Before calling, inspect a related saved query with ``list_query_examples``
    and ``get_query_example``. ``reference_query_name`` is mandatory and must
    identify a current saved example. This tool can never schedule, modify,
    run, or email a report; its HTTP allowlist contains only ``test_query``.
    For ordinary or current DB data, use ``tpap_redash`` or ``tsp_redash``
    instead; Trino is the fallback for historical snapshot data.

    Args:
        query: One bounded Trino SELECT or WITH statement.
        query_name: Descriptive label sent only to the preview endpoint.
        reference_query_name: Saved example used as syntax/schema reference.
    """
    try:
        normalized_name = _require_text("query_name", query_name)
        reference = _resolve_example(reference_query_name)
        validation = _validate_read_only_sql(query)
        data = _response_json(
            _request(
                "POST",
                _QUERY_ENDPOINT,
                payload={"query": query.strip(), "query_name": normalized_name},
            ),
            _QUERY_ENDPOINT,
        )
        if not data.get("success"):
            return _error(
                str(data.get("error") or "Trino query failed"),
                query_name=normalized_name,
                reference_query_name=reference["query_name"],
                read_only_enforced=True,
            )

        columns = data.get("columns") if isinstance(data.get("columns"), list) else []
        rows = data.get("data") if isinstance(data.get("data"), list) else []
        preview_rows, redacted_columns = _prepare_rows(columns, rows)
        return _json(
            {
                "success": True,
                "query_name": normalized_name,
                "reference_query_name": reference["query_name"],
                "reference_report_name": reference["report_name"],
                "columns": columns,
                "data": preview_rows,
                "row_count": data.get("row_count"),
                "preview_row_limit": min(
                    int(data.get("preview_row_limit") or _MAX_PREVIEW_ROWS),
                    _MAX_PREVIEW_ROWS,
                ),
                "execution_time_seconds": data.get("execution_time"),
                "redacted_columns": redacted_columns,
                "redaction_enabled": _REDACT_SENSITIVE,
                "read_only_enforced": True,
                "validation": validation,
                "endpoint": _QUERY_ENDPOINT,
            }
        )
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc), read_only_enforced=True)


if __name__ == "__main__":
    mcp.run()
