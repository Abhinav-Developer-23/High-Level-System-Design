"""MCP servers → LangGraph tools, via `langchain-mcp-adapters`.

The read-only MCP servers in `mcp_servers/` (ELK, archival logs, PMM, alerts, Jenkins, ArgoCD…)
and the external ones (Grafana, Jira/Confluence, Bitbucket) are reused as they are:

    client = MultiServerMCPClient({"tsp_elk": {"transport": "stdio", "command": ..., "args": [...]}},
                                  tool_name_prefix=True)
    tools = await client.get_tools()     # → BaseTool objects named "tsp_elk_<tool>"

`get_tools()` starts the server once to list its tools. Each later tool call opens a fresh
session (starts the server process, calls the tool, stops it). That costs a process start per
call but keeps nothing running between calls; a long-lived session per server would be faster.

The Redash servers are skipped: the native DB tools in `db.py` replace them.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from .. import mcp_config
from ..config import ROOT, get_settings
from ..mcp_probe import _flatten

log = logging.getLogger(__name__)

# Covered by the native DB tools (db.py), so not loaded over MCP.
REPLACED_BY_NATIVE = {"tpap_redash", "tsp_redash"}
# Anthropic's rule for tool names.
_TOOL_NAME = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def connection(name: str) -> dict:
    """The adapter's stdio connection for one server, secrets filled from .env (in memory only)."""
    spec, _missing = mcp_config.rendered_spec(name)
    return {"transport": "stdio", "command": spec["command"], "args": spec.get("args", []),
            "env": {**os.environ, **(spec.get("env") or {})}, "cwd": str(ROOT)}


async def load_server(srv: mcp_config.ServerInfo, timeout_s: float) -> list[BaseTool]:
    """Start one server, list its tools, drop the denied ones and any with an invalid name."""
    client = MultiServerMCPClient({srv.name: connection(srv.name)}, tool_name_prefix=True)
    tools = await asyncio.wait_for(client.get_tools(server_name=srv.name), timeout_s)
    prefix = f"{srv.name}_"
    keep = []
    for t in tools:
        original = t.name.removeprefix(prefix)
        if original in srv.deny:           # write tools (Grafana silences, Notion edits…)
            continue
        if not _TOOL_NAME.match(t.name):   # e.g. longer than 64 characters
            log.warning("skipping MCP tool with invalid name %r", t.name)
            continue
        keep.append(t)
    return keep


async def load_all() -> tuple[dict[str, list[BaseTool]], dict[str, str]]:
    """Load every enabled server concurrently. Returns (tools per server, error per failed server).

    A server that fails to start (missing .env value, binary not installed) is reported and
    skipped; the rest still load.
    """
    s = get_settings()
    servers = [srv for srv in mcp_config.catalogue()
               if srv.name not in REPLACED_BY_NATIVE and srv.name not in s.disabled_servers and not srv.default_off]

    async def one(srv: mcp_config.ServerInfo) -> tuple[str, list[BaseTool] | None, str | None]:
        try:
            return srv.name, await load_server(srv, s.mcp_load_timeout_s), None
        except BaseException as e:  # noqa: BLE001 — anyio raises ExceptionGroups
            if isinstance(e, asyncio.CancelledError):
                raise
            return srv.name, None, _flatten(e)[:300]

    tools: dict[str, list[BaseTool]] = {}
    errors: dict[str, str] = {}
    for name, got, err in await asyncio.gather(*(one(srv) for srv in servers)):
        if err is not None:
            errors[name] = err
            log.warning("MCP server %s not loaded: %s", name, err)
        else:
            tools[name] = got or []
    return tools, errors
