"""The tool belt: every tool the investigator can call, and which ones a given run may use.

    native tools   db.py (DB rows via Redash) + files.py (docs)    always loaded, no processes
    MCP tools      mcp.py (ELK, Grafana, PMM, alerts, Jenkins…)     loaded once at startup

`ToolBelt.all()` goes into the graph's `ToolNode` (it must know every tool it might run).
`ToolBelt.for_state(state)` is what the agent node binds to the model: the native tools plus
the MCP tools of the detected system's servers and the shared ones. So a TSP run never even
sees a TPAP tool, and `graph.guard_tool_call` refuses one if the model names it anyway.
"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool

from .. import mcp_config
from ..config import get_settings
from .control import AskUser
from .db import DB_TOOLS
from .files import FILE_TOOLS

NATIVE_TOOLS: list[BaseTool] = [*DB_TOOLS, *FILE_TOOLS]

__all__ = ["AskUser", "NATIVE_TOOLS", "ToolBelt", "load_belt"]


class ToolBelt:
    """Native tools + MCP tools grouped by server name."""

    def __init__(self, mcp_tools: dict[str, list[BaseTool]] | None = None,
                 mcp_errors: dict[str, str] | None = None) -> None:
        self.mcp_tools = mcp_tools or {}
        self.mcp_errors = mcp_errors or {}

    def all(self) -> list[BaseTool]:
        return [*NATIVE_TOOLS, *(t for tools in self.mcp_tools.values() for t in tools)]

    def for_state(self, state: dict[str, Any]) -> list[BaseTool]:
        """Tools this run may use: native + the MCP servers allowed for the state's system."""
        only = (state.get("options") or {}).get("servers")
        servers = mcp_config.servers_for(state.get("system"), only=only)
        return [*NATIVE_TOOLS, *(t for srv in servers for t in self.mcp_tools.get(srv.name, []))]

    def names_for(self, state: dict[str, Any]) -> set[str]:
        return {t.name for t in self.for_state(state)}

    def servers_for(self, state: dict[str, Any]) -> list[str]:
        """MCP servers whose tools this run gets (for the UI and the prompt)."""
        only = (state.get("options") or {}).get("servers")
        return [srv.name for srv in mcp_config.servers_for(state.get("system"), only=only)
                if srv.name in self.mcp_tools]


async def load_belt() -> ToolBelt:
    """Startup: load the MCP tools (unless MCP_LOAD=0) and wrap everything in a ToolBelt."""
    if not get_settings().mcp_enabled:
        return ToolBelt()
    from .mcp import load_all  # imported here so MCP_LOAD=0 never touches the adapter

    tools, errors = await load_all()
    return ToolBelt(tools, errors)
