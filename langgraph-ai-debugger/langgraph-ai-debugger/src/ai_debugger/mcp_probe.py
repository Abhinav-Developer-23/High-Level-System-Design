"""Start an MCP server and list its tools (initialize + tools/list).

Health check only — used by `ai-debugger mcp-check` and the UI's "probe" button. Investigations
use the tools loaded at startup by `tools/mcp.py` (langchain-mcp-adapters).

Background for beginners
------------------------
An MCP server over "stdio" is a program that reads JSON requests on its input and writes JSON
replies on its output. "Probing" means: start it, say hello (`initialize`), ask which tools it
has (`tools/list`), then shut it down. If that works, the server is configured correctly.
The `mcp` Python package does the JSON talking for us (`ClientSession`).
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from . import mcp_config
from .config import ROOT

# Last probe result per server, kept in memory so the MCP panel can show it after a reload.
_cache: dict[str, dict[str, Any]] = {}


async def probe(name: str, timeout_s: float = 90.0) -> dict[str, Any]:
    """Launch one server over stdio, do the MCP handshake, return {ok, tools, ms} or {ok, error}."""
    # secrets are filled in memory only; nothing is written to disk here
    spec, missing = mcp_config.rendered_spec(name)
    t0 = time.monotonic()
    # How to start the server: which program, its arguments, environment variables, folder.
    # `{**a, **b}` merges two dicts into a new one; keys in b win over keys in a.
    params = StdioServerParameters(
        command=spec["command"], args=spec.get("args", []),
        env={**os.environ, **(spec.get("env") or {})}, cwd=str(ROOT),
    )
    out: dict[str, Any] = {"name": name, "missing_env": sorted(missing)}
    try:
        # asyncio.timeout: if the block takes longer than timeout_s, it is aborted with TimeoutError.
        async with asyncio.timeout(timeout_s):
            # Two context managers in one `async with`: stdio_client starts the process and gives
            # its (read, write) pipes; ClientSession speaks MCP over them. Leaving the block
            # stops the server process.
            async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
                init = await session.initialize()
                tools = await session.list_tools()
        out.update(ok=True, server=_info(init, "name"), version=_info(init, "version"),
                   tools=sorted(t.name for t in tools.tools))
    except BaseException as e:  # noqa: BLE001 — anyio wraps failures in ExceptionGroups
        # A real cancel (user stopped the server) must keep going up, so re-raise it.
        if isinstance(e, asyncio.CancelledError) and not isinstance(e, TimeoutError):
            raise
        out.update(ok=False, error=_flatten(e)[:600])
    out["ms"] = int((time.monotonic() - t0) * 1000)
    _cache[name] = out
    return out


async def probe_many(names: list[str], concurrency: int = 6) -> list[dict[str, Any]]:
    """Probe several servers, at most `concurrency` at a time."""
    # A semaphore is a counter of free slots: `async with sem` waits for a slot, uses it, gives it back.
    sem = asyncio.Semaphore(concurrency)

    async def one(n: str) -> dict[str, Any]:
        async with sem:
            return await probe(n)

    # gather(*jobs) runs all the jobs at the same time and waits for all of them; results come
    # back in the same order as `names`. The `*` spreads the generator into separate arguments.
    return list(await asyncio.gather(*(one(n) for n in names)))


def cached() -> dict[str, dict[str, Any]]:
    """A copy of the cache, so callers can't change the real one by accident."""
    return dict(_cache)


def _flatten(e: BaseException) -> str:
    """Turn an error into one readable line. An ExceptionGroup holds several errors at once
    (the mcp library raises those), so we flatten them recursively and join with "; "."""
    if isinstance(e, BaseExceptionGroup):
        return "; ".join(_flatten(x) for x in e.exceptions)
    if isinstance(e, TimeoutError):
        return "timed out waiting for initialize/tools/list"
    return f"{type(e).__name__}: {e}"


def _info(init: Any, key: str) -> str:
    """Server name/version from the handshake reply. getattr(obj, "x", default) reads obj.x
    without crashing if it doesn't exist; two spellings are tried across library versions."""
    info = getattr(init, "serverInfo", None) or getattr(init, "server_info", None)
    return str(getattr(info, key, "") or "")
