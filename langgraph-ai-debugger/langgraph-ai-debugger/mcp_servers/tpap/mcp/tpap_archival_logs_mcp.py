#!/usr/bin/env python3
"""MCP server for long-running TPAP archival log searches.

Authentication uses TECHOPS_AGENT_PASSWORD from Agent-debugger/.env. The
resulting session cookie is kept only in this process's httpx cookie jar.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import sys
import threading
import time
from datetime import date as Date
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

# Cursor treats MCP stderr INFO as errors and may hide the server.
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.disable(logging.INFO)

_WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
_ENV_PATH = _WORKSPACE_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

BASE_URL = os.getenv("TECHOPS_AGENT_URL", "https://upi-ai-agent.paytm.com").rstrip("/")
EMAIL = os.getenv("TECHOPS_AGENT_EMAIL", "abhinav.anand@finmate.tech")
PASSWORD = os.getenv("TECHOPS_AGENT_PASSWORD", "")
DOWNLOAD_DIR = _WORKSPACE_ROOT / "tmp" / "logs" / "archival"
JOB_MANIFEST_DIR = DOWNLOAD_DIR / "jobs"

DEFAULT_BUCKET = "tpap-log-prod-211125458732-v2"
DEFAULT_PROJECT = "default"
MAX_PARALLEL_SEARCHES = 5
PROVIDER_ADMISSION_VERIFIED_AT_LEAST = 7
PROVIDER_EXECUTION_SLOTS_OBSERVED = 5
MAX_BATCH_SEARCHES = 10
MIN_POLL_SECONDS = 2.0
MAX_POLL_SECONDS = 60.0
MAX_WAIT_SECONDS = 4 * 60 * 60

_LOGIN_TIMEOUT = httpx.Timeout(30.0, connect=15.0)
_API_TIMEOUT = httpx.Timeout(60.0, connect=15.0)
_DOWNLOAD_TIMEOUT = httpx.Timeout(10 * 60.0, connect=15.0)
_USER_AGENT = "Agent-Debugger-Archival-Logs-MCP/1.0"

_client = httpx.Client(
    base_url=BASE_URL,
    follow_redirects=True,
    headers={
        "Accept": "application/json, */*",
        "User-Agent": _USER_AGENT,
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/tpap_archival_logs",
    },
)
_auth_lock = threading.RLock()
_jobs_lock = threading.Lock()
_job_started_at: dict[str, float] = {}

mcp = FastMCP("tpap_archival_logs")


class ArchivalSearchRequest(BaseModel):
    """One fully specified search in a bounded parallel batch."""

    pattern: str
    service: str
    date: str
    hour: str
    log_type: str
    bucket: str = DEFAULT_BUCKET
    project: str = DEFAULT_PROJECT
    pods: list[str] = Field(default_factory=list)
    result_filter_regex: str | None = None
    max_filtered_lines: int = 100
    stop_after_matches: int | None = None


def _log(message: str) -> None:
    """Log operational metadata only; never credentials, cookies, or patterns."""
    print(f"[tpap_archival_logs] {message}", file=sys.stderr, flush=True)


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def _error(message: str, **extra: Any) -> str:
    return _json({"error": message, **extra})


def _validate_search_input(date: str, hour: str) -> tuple[str, str]:
    try:
        parsed_date = Date.fromisoformat(date)
    except ValueError as exc:
        raise ValueError("date must use YYYY-MM-DD format") from exc

    normalized_hour = str(hour).strip().zfill(2)
    if not normalized_hour.isdigit() or not 0 <= int(normalized_hour) <= 23:
        raise ValueError("hour must be between 00 and 23")
    return parsed_date.isoformat(), normalized_hour


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
                    "Archival login was rejected: invalid email or password. "
                    "Update TECHOPS_AGENT_PASSWORD in the workspace .env file."
                )
            raise RuntimeError(
                "Login did not return a session cookie. Check "
                "TECHOPS_AGENT_EMAIL and TECHOPS_AGENT_PASSWORD."
            )
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
    endpoint: str,
    payload: dict[str, Any],
    *,
    timeout: httpx.Timeout = _API_TIMEOUT,
) -> httpx.Response:
    """Make one authenticated request, refreshing an expired session once."""
    _login()
    response = _client.post(
        endpoint,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=timeout,
    )
    if _looks_unauthenticated(response):
        with _auth_lock:
            _client.cookies.clear()
        _login()
        response = _client.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )

    if _looks_unauthenticated(response):
        raise RuntimeError("Authentication failed after refreshing the session")
    response.raise_for_status()
    return response


def _get(endpoint: str) -> httpx.Response:
    """Make one authenticated GET, refreshing an expired session once."""
    _login()
    response = _client.get(endpoint, timeout=_API_TIMEOUT)
    if _looks_unauthenticated(response):
        with _auth_lock:
            _client.cookies.clear()
        _login()
        response = _client.get(endpoint, timeout=_API_TIMEOUT)
    response.raise_for_status()
    return response


def _search_option_tree() -> dict[str, dict[str, list[str]]]:
    """Read the portal's current TPAP log-type/project/service option tree."""
    response = _get("/tpap_archival_logs")
    match = re.search(
        r"const BUCKET_CONFIGS\s*=\s*(\[.*?\]);\s*const JOB_STORAGE_KEY",
        response.text,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError("The archival portal did not expose its search options")
    configs = json.loads(match.group(1))
    for config in configs:
        if config.get("bucket") == DEFAULT_BUCKET:
            tree = config.get("tree")
            if isinstance(tree, dict):
                return tree
    raise RuntimeError("The TPAP archival bucket is missing from the portal options")


def _response_json(response: httpx.Response, endpoint: str) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"{endpoint} returned non-JSON content ({response.headers.get('content-type')})"
        ) from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{endpoint} returned an unexpected JSON value")
    return data


def _nested_values(data: Any) -> list[tuple[str, Any]]:
    values: list[tuple[str, Any]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                values.append((str(key).lower(), nested))
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(data)
    return values


def _first_field(data: dict[str, Any], names: set[str]) -> Any:
    for key, value in _nested_values(data):
        if key in names and value is not None:
            return value
    return None


def _extract_job_id(data: dict[str, Any]) -> str | None:
    value = _first_field(data, {"job_id", "jobid", "id"})
    return str(value) if value is not None else None


def _status_text(data: dict[str, Any]) -> str:
    value = _first_field(
        data,
        {"status", "state", "job_status", "search_status"},
    )
    return str(value).strip().lower() if value is not None else "unknown"


def _progress_percent(data: dict[str, Any], status: str) -> float | None:
    value: Any = None
    for key, candidate in _nested_values(data):
        if key not in {
            "progress",
            "percentage",
            "percent",
            "progress_percent",
            "progress_percentage",
            "completion_percentage",
        }:
            continue
        if isinstance(candidate, dict):
            current = candidate.get(
                "current",
                candidate.get(
                    "processed",
                    candidate.get("completed", candidate.get("scanned")),
                ),
            )
            total = candidate.get("total")
            if (
                isinstance(current, (int, float))
                and not isinstance(current, bool)
                and isinstance(total, (int, float))
                and not isinstance(total, bool)
                and total > 0
            ):
                value = float(current) / float(total) * 100.0
                break
            continue
        value = candidate
        break

    if isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value)
        value = float(match.group()) if match else None
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        value = float(value)
    else:
        value = None

    if value is not None:
        return max(0.0, min(100.0, value))
    if _is_complete(status):
        return 100.0
    return None


def _is_complete(status: str) -> bool:
    return status in {
        "completed",
        "complete",
        "success",
        "succeeded",
        "done",
        "finished",
    }


def _is_terminal_failure(status: str) -> bool:
    return status in {
        "failed",
        "failure",
        "error",
        "stopped",
        "cancelled",
        "canceled",
    }


def _remember_job(job_id: str) -> None:
    with _jobs_lock:
        _job_started_at.setdefault(job_id, time.monotonic())


def _elapsed_seconds(job_id: str) -> float:
    with _jobs_lock:
        started = _job_started_at.setdefault(job_id, time.monotonic())
    return max(0.0, time.monotonic() - started)


def _format_elapsed(seconds: float) -> str:
    whole = int(seconds)
    hours, remainder = divmod(whole, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _matches_found(data: dict[str, Any]) -> int | None:
    value = _first_field(
        data,
        {
            "matches",
            "matches_found",
            "match_count",
            "matched_lines",
            "lines_found",
            "result_count",
            "results_count",
            "total_matches",
        },
    )
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return max(0, int(value))
    if isinstance(value, list):
        return len(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _status_result(job_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    status = _status_text(raw)
    progress = _progress_percent(raw, status)
    if status == "unknown" and progress == 100.0:
        status = "completed"
    elapsed = _elapsed_seconds(job_id)
    files_processed = raw.get("files_processed")
    execution_progress_observed = bool(
        (isinstance(files_processed, (int, float)) and files_processed > 0)
        or (progress is not None and progress > 0)
    )
    return {
        "job_id": job_id,
        "status": status,
        "progress_percent": progress,
        "files_processed": files_processed,
        "files_total": raw.get("files_total"),
        "execution_progress_observed": execution_progress_observed,
        "execution_note": (
            "The provider's in_progress status means admitted, not necessarily "
            "executing. Verify that files_processed or progress_percent "
            "advances across multiple polls before claiming an active slot."
            if status == "in_progress"
            else None
        ),
        "matches_found": _matches_found(raw),
        "elapsed_seconds": round(elapsed, 1),
        "elapsed": _format_elapsed(elapsed),
        "raw": {
            key: value
            for key, value in raw.items()
            if key not in {"preview_content", "preview_lines"}
        },
        "preview_available": bool(
            raw.get("preview_content") or raw.get("preview_lines")
        ),
    }


def _check_status(job_id: str) -> dict[str, Any]:
    response = _request("/api/check-search-status", {"job_id": job_id})
    raw = _response_json(response, "/api/check-search-status")
    return _status_result(job_id, raw)


async def _stop_and_wait(
    job_id: str,
    *,
    timeout_seconds: float = 90.0,
) -> dict[str, Any]:
    """Request cancellation and wait so a client slot is not released early."""
    stop_raw = _stop(job_id)
    deadline = time.monotonic() + timeout_seconds
    final_status: dict[str, Any] | None = None

    while time.monotonic() < deadline:
        await asyncio.sleep(MIN_POLL_SECONDS)
        final_status = _check_status(job_id)
        status = str(final_status["status"])
        if _is_complete(status) or _is_terminal_failure(status):
            break

    return {
        "stop_response": stop_raw,
        "final_status": final_status,
        "stop_wait_timed_out": not (
            final_status
            and (
                _is_complete(str(final_status["status"]))
                or _is_terminal_failure(str(final_status["status"]))
            )
        ),
    }


def _safe_filename(value: str) -> str:
    name = Path(value).name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name[:180] or "results"


def _write_job_manifest(job_id: str, payload: dict[str, Any]) -> str:
    """Persist resumable non-credential job metadata in the ignored tmp tree."""
    JOB_MANIFEST_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    JOB_MANIFEST_DIR.chmod(0o700)
    target = JOB_MANIFEST_DIR / f"{_safe_filename(job_id)}.json"
    manifest = {
        "job_id": job_id,
        "started_at_epoch": time.time(),
        "pattern_fingerprint": hashlib.sha256(
            payload["pattern"].encode("utf-8")
        ).hexdigest()[:16],
        "pattern_length": len(payload["pattern"]),
        "bucket": payload["bucket"],
        "log_type": payload["log_type"],
        "project": payload["project"],
        "service": payload["service"],
        "date": payload["date"],
        "hour": payload["hour"],
        "pods": payload["pods"],
        "contains_credentials": False,
    }
    target.write_text(_json(manifest) + "\n", encoding="utf-8")
    target.chmod(0o600)
    return str(target.resolve())


def _download_filename(response: httpx.Response, job_id: str) -> str:
    disposition = response.headers.get("content-disposition", "")
    encoded_match = re.search(r"filename\*=UTF-8''([^;]+)", disposition, re.IGNORECASE)
    plain_match = re.search(r'filename="?([^";]+)"?', disposition, re.IGNORECASE)
    if encoded_match:
        from urllib.parse import unquote

        return _safe_filename(unquote(encoded_match.group(1)))
    if plain_match:
        return _safe_filename(plain_match.group(1))

    content_type = response.headers.get("content-type", "").lower()
    suffix = ".zip" if "zip" in content_type else ".json" if "json" in content_type else ".log"
    return f"{_safe_filename(job_id)}{suffix}"


def _download(job_id: str) -> dict[str, Any]:
    response = _request(
        "/api/download-search-results",
        {"job_id": job_id},
        timeout=_DOWNLOAD_TIMEOUT,
    )
    content_type = response.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict) and body.get("error"):
            raise RuntimeError(str(body["error"]))

    target_dir = DOWNLOAD_DIR
    target_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = target_dir / _download_filename(response, job_id)
    if target.exists():
        stem, suffix = target.stem, target.suffix
        counter = 1
        while target.exists():
            target = target_dir / f"{stem}-{counter}{suffix}"
            counter += 1
    target.write_bytes(response.content)
    target.chmod(0o600)
    return {
        "job_id": job_id,
        "output_path": str(target.resolve()),
        "size_bytes": len(response.content),
        "content_type": response.headers.get("content-type"),
    }


def _unique_filtered_path(source: Path) -> Path:
    target_dir = DOWNLOAD_DIR
    target_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = target_dir / f"{_safe_filename(source.stem)}.filtered.txt"
    counter = 1
    while target.exists():
        target = target_dir / f"{_safe_filename(source.stem)}.filtered-{counter}.txt"
        counter += 1
    return target


def _filter_result_file(
    input_path: str,
    result_filter_regex: str,
    max_lines: int = 100,
) -> dict[str, Any]:
    source = Path(input_path).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"input_path is not a file: {source}")
    try:
        line_pattern = re.compile(result_filter_regex)
    except re.error as exc:
        raise ValueError(f"Invalid result_filter_regex: {exc}") from exc

    limit = max(1, min(10_000, int(max_lines)))
    target = _unique_filtered_path(source)
    matched = 0
    truncated = False
    with source.open("r", encoding="utf-8", errors="replace") as source_file:
        with target.open("x", encoding="utf-8") as target_file:
            for line in source_file:
                if not line_pattern.search(line):
                    continue
                if matched >= limit:
                    truncated = True
                    break
                target_file.write(line)
                matched += 1
    target.chmod(0o600)
    return {
        "input_path": str(source),
        "output_path": str(target.resolve()),
        "regex": result_filter_regex,
        "matched_lines": matched,
        "max_lines": limit,
        "truncated": truncated,
    }


def _stop(job_id: str) -> dict[str, Any]:
    return _response_json(
        _request("/api/stop-search", {"job_id": job_id}),
        "/api/stop-search",
    )


class _ParallelProgress:
    def __init__(self, ctx: Context, total_searches: int) -> None:
        self.ctx = ctx
        self.total_searches = total_searches
        self.started_at = time.monotonic()
        self.percentages = [0.0] * total_searches
        self.finished = [False] * total_searches
        self.lock = asyncio.Lock()

    async def update(
        self,
        index: int,
        progress: float,
        total: float | None,
        message: str | None,
    ) -> None:
        if total and total > 0:
            percent = float(progress) / float(total) * 100.0
        else:
            percent = float(progress)
        async with self.lock:
            self.percentages[index] = max(0.0, min(100.0, percent))
            await self._report(index, message)

    async def complete(self, index: int, succeeded: bool) -> None:
        async with self.lock:
            self.percentages[index] = 100.0
            self.finished[index] = True
            outcome = "finished" if succeeded else "ended with an error"
            await self._report(index, f"search {index + 1} {outcome}")

    async def _report(self, index: int, child_message: str | None) -> None:
        aggregate = sum(self.percentages) / self.total_searches
        completed = sum(self.finished)
        elapsed = _format_elapsed(time.monotonic() - self.started_at)
        suffix = f"; search {index + 1}: {child_message}" if child_message else ""
        await self.ctx.report_progress(
            progress=aggregate,
            total=100,
            message=(
                f"Parallel archival batch — {aggregate:.1f}% aggregate, "
                f"{completed}/{self.total_searches} finished, elapsed {elapsed}"
                f"{suffix}"
            ),
        )


class _ParallelChildContext:
    """Forward one managed search's notifications into aggregate batch progress."""

    def __init__(self, tracker: _ParallelProgress, index: int) -> None:
        self.tracker = tracker
        self.index = index

    async def report_progress(
        self,
        progress: float,
        total: float | None = None,
        message: str | None = None,
    ) -> None:
        await self.tracker.update(self.index, progress, total, message)

    async def info(self, message: str, **extra: Any) -> None:
        await self.tracker.ctx.info(
            f"[archival search {self.index + 1}/{self.tracker.total_searches}] {message}",
            **extra,
        )

    async def warning(self, message: str, **extra: Any) -> None:
        await self.tracker.ctx.warning(
            f"[archival search {self.index + 1}/{self.tracker.total_searches}] {message}",
            **extra,
        )


@mcp.tool()
def list_search_options() -> str:
    """List current TPAP archival log types, projects, and services.

    Use this before asking the user to choose mandatory ``log_type`` and
    ``service`` values. It reads the portal's current option tree and does not
    start a search.
    """
    try:
        tree = _search_option_tree()
        targets = [
            {
                "log_type": log_type,
                "project": project,
                "services": services,
            }
            for log_type, projects in tree.items()
            for project, services in projects.items()
        ]
        return _json(
            {
                "bucket": DEFAULT_BUCKET,
                "archive_time_zone": "Asia/Kolkata (IST; observed)",
                "targets": targets,
                "required_before_search": [
                    "exact txn ID, RRN, or search pattern",
                    "exact timestamp with timezone",
                    "service",
                    "log_type",
                ],
            }
        )
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))


@mcp.tool()
def start_search(
    pattern: str,
    service: str,
    date: str,
    hour: str,
    log_type: str,
    bucket: str = DEFAULT_BUCKET,
    project: str = DEFAULT_PROJECT,
    pods: list[str] | None = None,
) -> str:
    """Start one TPAP archival-log search and return its job ID immediately.

    Use search_archival_logs instead when the caller can wait; it reports
    percentage and elapsed time until completion. Archival searches can take
    a long time. Tell the user before starting one.

    Args:
        pattern: Exact transaction ID, RRN, or literal substring passed to
            the archive backend. Regex metacharacters are treated literally.
        service: Archive service name, for example "tpap-consumers".
        date: Archive partition date in YYYY-MM-DD format.
        hour: Archive partition hour, 00 through 23.
        log_type: Archive log type, for example "application-logs".
        bucket: Archive bucket. Defaults to the TPAP production archive.
        project: Archive project. Defaults to "default".
        pods: Optional pod-name filters. Empty means all pods.
    """
    try:
        normalized_date, normalized_hour = _validate_search_input(date, hour)
        normalized_bucket = _require_text("bucket", bucket)
        if normalized_bucket != DEFAULT_BUCKET:
            raise ValueError(
                "This MCP is restricted to the configured TPAP archival bucket"
            )
        payload = {
            "pattern": _require_text("pattern", pattern),
            "bucket": normalized_bucket,
            "log_type": _require_text("log_type", log_type),
            "project": _require_text("project", project),
            "service": _require_text("service", service),
            "date": normalized_date,
            "hour": normalized_hour,
            "pods": pods or [],
        }
        raw = _response_json(
            _request("/api/search-logs", payload),
            "/api/search-logs",
        )
        job_id = _extract_job_id(raw)
        if not job_id:
            return _error("Search started but the response contained no job_id", raw=raw)
        _remember_job(job_id)
        manifest_path: str | None = None
        manifest_error: str | None = None
        try:
            manifest_path = _write_job_manifest(job_id, payload)
        except OSError as exc:
            manifest_error = (
                "Search started, but its local resumability manifest could "
                f"not be written: {exc}"
            )
        _log(f"started job {job_id}")
        return _json(
            {
                "job_id": job_id,
                "status": _status_text(raw),
                "elapsed_seconds": 0,
                "raw": raw,
                "job_manifest_path": manifest_path,
                "job_manifest_error": manifest_error,
                "next": (
                    "Poll check_search_status or call wait_for_search with "
                    "this job_id. Do not call search_archival_logs, which "
                    "would start a duplicate."
                ),
                "execution_note": (
                    "An in_progress response confirms admission only. Poll "
                    "files_processed/progress_percent for several minutes to "
                    "verify actual execution."
                ),
            }
        )
    except Exception as exc:  # noqa: BLE001 - return actionable MCP error
        return _error(str(exc))


@mcp.tool()
def check_search_status(job_id: str) -> str:
    """Check an archival search and include normalized percent and elapsed time.

    Elapsed time is measured from when this MCP process first saw the job.
    ``in_progress`` confirms admission only; actual execution requires
    advancement across multiple polls.
    """
    try:
        _remember_job(job_id)
        return _json(_check_status(job_id))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc), job_id=job_id)


@mcp.tool()
def download_search_results(
    job_id: str,
) -> str:
    """Download completed archival results to a private local file.

    By default files go under the workspace's gitignored tmp/logs/archival
    directory with user-only permissions.

    Args:
        job_id: Completed archival search job ID.
    """
    try:
        return _json(_download(job_id))
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc), job_id=job_id)


@mcp.tool()
def filter_search_results(
    input_path: str,
    result_filter_regex: str,
    max_lines: int = 100,
) -> str:
    """Extract only required lines from downloaded results into tmp/.

    This is a local Python regular expression applied after the archive
    service finishes. It works even if the archive backend treats its search
    pattern literally. For a promo line from a transaction search, use a
    filter such as ``(?i)sending\\s+(?:generic\\s+)?promo\\s+data``.

    Args:
        input_path: Downloaded archival result file.
        result_filter_regex: Python regular expression required on each line.
        max_lines: Maximum matching lines to write, capped at 10,000.
    """
    try:
        return _json(
            _filter_result_file(
                input_path=input_path,
                result_filter_regex=result_filter_regex,
                max_lines=max_lines,
            )
        )
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc), input_path=input_path)


@mcp.tool()
def stop_search(job_id: str) -> str:
    """Stop a running archival search job."""
    try:
        raw = _stop(job_id)
        return _json({"job_id": job_id, "status": _status_text(raw), "raw": raw})
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc), job_id=job_id)


def _validate_monitor_options(
    result_filter_regex: str | None,
    download_when_complete: bool,
    stop_after_matches: int | None,
) -> None:
    if result_filter_regex:
        try:
            re.compile(result_filter_regex)
        except re.error as exc:
            raise ValueError(f"Invalid result_filter_regex: {exc}") from exc
        if not download_when_complete:
            raise ValueError(
                "result_filter_regex requires download_when_complete=true"
            )
    if stop_after_matches is not None and int(stop_after_matches) < 1:
        raise ValueError("stop_after_matches must be at least 1")


async def _monitor_existing_search(
    job_id: str,
    ctx: Context,
    *,
    poll_interval_seconds: float,
    timeout_seconds: float,
    download_when_complete: bool,
    result_filter_regex: str | None,
    max_filtered_lines: int,
    stop_after_matches: int | None,
    resumed: bool,
) -> str:
    """Monitor an existing job without starting a duplicate server search."""
    _remember_job(job_id)
    interval = max(
        MIN_POLL_SECONDS,
        min(MAX_POLL_SECONDS, float(poll_interval_seconds)),
    )
    timeout = max(interval, min(MAX_WAIT_SECONDS, float(timeout_seconds)))
    wait_started_at = time.monotonic()
    last_reported_percent: float | None = None
    last_notification_at = 0.0
    consecutive_errors = 0
    action = "Reattached to" if resumed else "Started"

    await ctx.info(
        f"{action} archival search {job_id}; this may take a long time. "
        "Progress will include elapsed time."
    )

    while True:
        try:
            status_result = _check_status(job_id)
            consecutive_errors = 0
        except Exception as exc:  # noqa: BLE001 - retry transient poll failures
            consecutive_errors += 1
            elapsed = _elapsed_seconds(job_id)
            elapsed_text = _format_elapsed(elapsed)
            await ctx.warning(
                f"Archival status check failed ({consecutive_errors}/3) after "
                f"{elapsed_text}: {exc}"
            )
            if consecutive_errors >= 3:
                return _error(
                    "Three consecutive archival status checks failed; the "
                    "server-side job was not stopped.",
                    job_id=job_id,
                    elapsed_seconds=round(elapsed, 1),
                    elapsed=elapsed_text,
                    next=(
                        "Retry wait_for_search with this job_id, or use the "
                        "direct API fallback with the same job_id."
                    ),
                )
            await asyncio.sleep(interval)
            continue

        status = str(status_result["status"])
        percent = status_result["progress_percent"]
        matches_found = status_result["matches_found"]
        elapsed = float(status_result["elapsed_seconds"])
        elapsed_text = str(status_result["elapsed"])
        display_percent = (
            percent if percent is not None else (last_reported_percent or 0.0)
        )
        message = (
            f"Archival search {status} — {display_percent:.1f}% complete, "
            f"elapsed {elapsed_text}"
        )

        await ctx.report_progress(
            progress=display_percent,
            total=100,
            message=message,
        )
        last_reported_percent = percent
        if elapsed - last_notification_at >= 60.0:
            await ctx.info(message)
            last_notification_at = elapsed

        if _is_complete(status):
            result: dict[str, Any] = status_result
            if download_when_complete:
                try:
                    result["download"] = _download(job_id)
                    if result_filter_regex:
                        result["filtered"] = _filter_result_file(
                            result["download"]["output_path"],
                            result_filter_regex,
                            max_filtered_lines,
                        )
                except Exception as exc:  # noqa: BLE001
                    result["download_pending"] = True
                    result["download_error"] = str(exc)
                    result["next"] = (
                        "The server search is complete. Free local space or "
                        "resolve the download error, then retry "
                        "download_search_results with this same job_id. Do "
                        "not start another search."
                    )
            if stop_after_matches is not None and matches_found is None:
                result["early_stop_supported_by_status"] = False
            await ctx.info(
                f"Archival search {job_id} completed in {elapsed_text}"
            )
            return _json(result)

        if (
            stop_after_matches is not None
            and matches_found is not None
            and matches_found >= int(stop_after_matches)
        ):
            stop_result = await _stop_and_wait(job_id)
            await ctx.info(
                f"Archival search {job_id} reported {matches_found} matches; "
                f"stopping early after {elapsed_text}"
            )
            result = {
                **status_result,
                "stopped_early": True,
                **stop_result,
            }
            if download_when_complete:
                try:
                    result["download"] = _download(job_id)
                    if result_filter_regex:
                        result["filtered"] = _filter_result_file(
                            result["download"]["output_path"],
                            result_filter_regex,
                            max_filtered_lines,
                        )
                except Exception as exc:  # noqa: BLE001
                    result["download_error"] = str(exc)
                    result["next"] = (
                        "The job was stopped after reaching the requested "
                        "match count. Retry download_search_results shortly."
                    )
            return _json(result)

        if _is_terminal_failure(status):
            await ctx.warning(
                f"Archival search {job_id} ended with status {status} "
                f"after {elapsed_text}"
            )
            return _json(status_result)

        wait_elapsed = time.monotonic() - wait_started_at
        if wait_elapsed >= timeout:
            await ctx.warning(
                f"Paused monitoring archival search {job_id} after "
                f"{_format_elapsed(wait_elapsed)}; the server-side job "
                "continues running."
            )
            return _json(
                {
                    **status_result,
                    "timed_out_waiting": True,
                    "monitoring_wait_seconds": round(wait_elapsed, 1),
                    "next": (
                        "Do not start a duplicate. Resume with wait_for_search "
                        "using this same job_id."
                    ),
                }
            )

        await asyncio.sleep(interval)


@mcp.tool()
async def search_archival_logs(
    pattern: str,
    service: str,
    date: str,
    hour: str,
    log_type: str,
    ctx: Context,
    bucket: str = DEFAULT_BUCKET,
    project: str = DEFAULT_PROJECT,
    pods: list[str] | None = None,
    poll_interval_seconds: float = 10.0,
    timeout_seconds: float = 3600.0,
    download_when_complete: bool = True,
    result_filter_regex: str | None = None,
    max_filtered_lines: int = 100,
    stop_after_matches: int | None = None,
) -> str:
    """Start, monitor, and optionally download one archival-log search.

    This can take a long time. Before calling, tell the user the archival
    search is starting. While it runs, MCP progress notifications include the
    server-reported percentage and elapsed time.

    Args:
        pattern: Exact transaction ID, RRN, or literal substring passed to
            the archive backend. Regex metacharacters are treated literally.
        service: Archive service name, for example "tpap-consumers".
        date: Archive partition date in YYYY-MM-DD format.
        hour: Archive partition hour, 00 through 23.
        log_type: Archive log type, for example "application-logs".
        bucket: Archive bucket.
        project: Archive project.
        pods: Optional pod-name filters.
        poll_interval_seconds: Status poll interval, clamped to 2-60 seconds.
        timeout_seconds: Stop waiting after this many seconds, max four hours.
        download_when_complete: Download completed results when true.
        result_filter_regex: Optional local Python regex used to extract only
            required lines from the downloaded file.
        max_filtered_lines: Maximum locally filtered lines to keep.
        stop_after_matches: Stop the server job once its status reports at
            least this many matches. This only works if the API exposes a
            match count; otherwise the search safely runs to completion.
    """
    try:
        _validate_monitor_options(
            result_filter_regex,
            download_when_complete,
            stop_after_matches,
        )
    except ValueError as exc:
        return _error(str(exc))

    started = start_search(
        pattern=pattern,
        service=service,
        date=date,
        hour=hour,
        bucket=bucket,
        log_type=log_type,
        project=project,
        pods=pods,
    )
    try:
        start_data = json.loads(started)
    except ValueError:
        return _error("Unexpected response while starting archival search")
    if start_data.get("error"):
        return started

    return await _monitor_existing_search(
        str(start_data["job_id"]),
        ctx,
        poll_interval_seconds=poll_interval_seconds,
        timeout_seconds=timeout_seconds,
        download_when_complete=download_when_complete,
        result_filter_regex=result_filter_regex,
        max_filtered_lines=max_filtered_lines,
        stop_after_matches=stop_after_matches,
        resumed=False,
    )


@mcp.tool()
async def wait_for_search(
    job_id: str,
    ctx: Context,
    poll_interval_seconds: float = 30.0,
    timeout_seconds: float = 3600.0,
    download_when_complete: bool = True,
    result_filter_regex: str | None = None,
    max_filtered_lines: int = 100,
    stop_after_matches: int | None = None,
) -> str:
    """Reattach to an existing archival job and monitor it without duplication.

    Use this for long-running bug investigations after ``start_search`` has
    returned a job ID. A monitoring timeout pauses only this MCP call; it does
    not stop the server job. Call this tool again with the same job ID to
    continue waiting. Progress includes percentage and elapsed time.

    Args:
        job_id: Existing server-side archival search job.
        poll_interval_seconds: Status poll interval, clamped to 2-60 seconds.
        timeout_seconds: Duration of this monitoring slice, max four hours.
        download_when_complete: Download completed results when true.
        result_filter_regex: Optional local Python regex applied after download.
        max_filtered_lines: Maximum locally filtered lines to keep.
        stop_after_matches: Stop once the literal backend search reports at
            least this many matches. Do not use for a full transaction trace.
    """
    try:
        normalized_job_id = _require_text("job_id", job_id)
        _validate_monitor_options(
            result_filter_regex,
            download_when_complete,
            stop_after_matches,
        )
    except ValueError as exc:
        return _error(str(exc), job_id=job_id)

    return await _monitor_existing_search(
        normalized_job_id,
        ctx,
        poll_interval_seconds=poll_interval_seconds,
        timeout_seconds=timeout_seconds,
        download_when_complete=download_when_complete,
        result_filter_regex=result_filter_regex,
        max_filtered_lines=max_filtered_lines,
        stop_after_matches=stop_after_matches,
        resumed=True,
    )


@mcp.tool()
async def search_archival_logs_parallel(
    searches: list[ArchivalSearchRequest],
    ctx: Context,
    max_parallel: int = MAX_PARALLEL_SEARCHES,
    poll_interval_seconds: float = 10.0,
    timeout_seconds: float = 3600.0,
    download_when_complete: bool = True,
    full_transaction_trace: bool = False,
) -> str:
    """Run multiple fully specified archival searches with bounded parallelism.

    The MCP permits at most five simultaneous searches. A live probe admitted
    seven jobs as in_progress, but only the first five advanced while jobs six
    and seven remained at 0%, showing that excess jobs are server-queued.
    Extra batch items are therefore queued client-side and start as slots
    become free. Aggregate progress includes percentage, completed item count,
    and elapsed time.

    Before calling, obtain every item's identifier/pattern, exact timestamp
    with timezone, service, and log type from the user. Tell the user that a
    parallel archival batch is starting and may take a long time.

    For a complete historical transaction trace, submit the same exact txn ID
    once per relevant service/log-type combination (for example switch
    application, switch exchange, consumers, and other named services). Leave
    result_filter_regex and stop_after_matches unset so every matching txn line
    is collected. Add separate items for adjacent hours when needed.

    Args:
        searches: One to 10 searches. Each item requires pattern, service,
            date, hour, and log_type; txn IDs and RRNs are supported.
        max_parallel: Requested concurrency. Values above five are capped at
            five; extra searches remain queued.
        poll_interval_seconds: Per-search status poll interval.
        timeout_seconds: Per-search wait timeout, capped at four hours.
        download_when_complete: Download each completed result under the
            workspace's gitignored tmp/logs/archival directory.
        full_transaction_trace: Enforce one txn ID across all items, complete
            downloads, and prohibit filters/early-stop options that could omit
            later transaction stages.
    """
    if not searches:
        return _error("At least one archival search is required")
    if len(searches) > MAX_BATCH_SEARCHES:
        return _error(
            f"A batch can contain at most {MAX_BATCH_SEARCHES} searches",
            requested=len(searches),
        )
    if int(max_parallel) < 1:
        return _error("max_parallel must be at least 1")
    if full_transaction_trace:
        patterns = {request.pattern.strip() for request in searches}
        if len(patterns) != 1 or "" in patterns:
            return _error(
                "full_transaction_trace requires the same non-empty txn ID "
                "pattern in every batch item"
            )
        if not download_when_complete:
            return _error(
                "full_transaction_trace requires download_when_complete=true"
            )
        unsafe_items = [
            index + 1
            for index, request in enumerate(searches)
            if request.result_filter_regex or request.stop_after_matches is not None
        ]
        if unsafe_items:
            return _error(
                "full_transaction_trace does not allow result_filter_regex or "
                "stop_after_matches because they can omit later txn stages",
                request_indices=unsafe_items,
            )

    parallelism = min(
        int(max_parallel),
        MAX_PARALLEL_SEARCHES,
        len(searches),
    )
    tracker = _ParallelProgress(ctx, len(searches))
    semaphore = asyncio.Semaphore(parallelism)
    results: list[dict[str, Any] | None] = [None] * len(searches)

    await ctx.info(
        f"Starting {len(searches)} archival searches with up to "
        f"{parallelism} running in parallel. This may take a long time."
    )
    await ctx.report_progress(
        progress=0,
        total=100,
        message=(
            f"Parallel archival batch queued — 0% aggregate, "
            f"0/{len(searches)} finished, elapsed 00:00:00"
        ),
    )

    async def run_one(index: int, request: ArchivalSearchRequest) -> None:
        async with semaphore:
            child_ctx = _ParallelChildContext(tracker, index)
            try:
                raw = await search_archival_logs(
                    pattern=request.pattern,
                    service=request.service,
                    date=request.date,
                    hour=request.hour,
                    log_type=request.log_type,
                    ctx=child_ctx,  # type: ignore[arg-type] - intentional proxy
                    bucket=request.bucket,
                    project=request.project,
                    pods=request.pods,
                    poll_interval_seconds=poll_interval_seconds,
                    timeout_seconds=timeout_seconds,
                    download_when_complete=download_when_complete,
                    result_filter_regex=request.result_filter_regex,
                    max_filtered_lines=request.max_filtered_lines,
                    stop_after_matches=request.stop_after_matches,
                )
                try:
                    result = json.loads(raw)
                except ValueError:
                    result = {"error": "Managed search returned invalid JSON"}
            except Exception as exc:  # noqa: BLE001 - isolate batch items
                result = {"error": str(exc)}

            job_id = result.get("job_id")
            status = str(result.get("status", "")).lower()
            if (
                job_id
                and not _is_complete(status)
                and not _is_terminal_failure(status)
                and not result.get("stopped_early")
            ):
                try:
                    result["cleanup"] = await _stop_and_wait(str(job_id))
                except Exception as exc:  # noqa: BLE001
                    result["cleanup_error"] = str(exc)

            result["request_index"] = index + 1
            results[index] = result
            succeeded = (
                not result.get("error")
                and not result.get("download_error")
                and (
                    _is_complete(status)
                    or bool(result.get("stopped_early"))
                )
            )
            await tracker.complete(index, succeeded)

    await asyncio.gather(
        *(run_one(index, request) for index, request in enumerate(searches))
    )

    completed_results = [result or {"error": "Search produced no result"} for result in results]
    succeeded_count = sum(
        1
        for result in completed_results
        if not result.get("error")
        and not result.get("download_error")
        and (
            _is_complete(str(result.get("status", "")).lower())
            or bool(result.get("stopped_early"))
        )
    )
    elapsed = time.monotonic() - tracker.started_at
    await ctx.info(
        f"Parallel archival batch finished: {succeeded_count}/{len(searches)} "
        f"succeeded in {_format_elapsed(elapsed)}"
    )
    return _json(
        {
            "search_count": len(searches),
            "succeeded": succeeded_count,
            "failed_or_incomplete": len(searches) - succeeded_count,
            "parallelism_used": parallelism,
            "mcp_parallelism_cap": MAX_PARALLEL_SEARCHES,
            "provider_admission_verified_at_least": (
                PROVIDER_ADMISSION_VERIFIED_AT_LEAST
            ),
            "provider_execution_slots_observed": (
                PROVIDER_EXECUTION_SLOTS_OBSERVED
            ),
            "provider_exact_cap_verified": False,
            "full_transaction_trace": full_transaction_trace,
            "elapsed_seconds": round(elapsed, 1),
            "elapsed": _format_elapsed(elapsed),
            "download_directory": str(DOWNLOAD_DIR),
            "results": completed_results,
        }
    )


if __name__ == "__main__":
    mcp.run()
