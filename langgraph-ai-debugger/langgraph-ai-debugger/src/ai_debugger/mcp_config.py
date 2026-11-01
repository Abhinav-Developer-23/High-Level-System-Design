"""MCP server catalogue: which servers exist, which system each belongs to, and their secrets.

`config/mcp_servers.json` is a template with `${ROOT}` / `${VAR}` placeholders. Values come from
`.env` and are filled in memory only (`rendered_spec`); `tools/mcp.py` hands the result to
`langchain-mcp-adapters`, which starts the server and turns its tools into LangGraph tools.

Each server entry in the template has a `_meta` block that is ours, not part of MCP:
    system       "tpap" | "tsp" | "shared"   → which runs may use it
    label, kind  shown in the UI's MCP panel
    deny         tool names that are never loaded (write tools)
    default_off  only attached when the UI ticks it explicitly
`_meta` is stripped before the spec is used.

Isolation: `servers_for("tsp")` returns only tsp + shared servers, so a TSP run is never given a
TPAP tool (see `ToolBelt.for_state`).

Background for beginners
------------------------
* **MCP (Model Context Protocol)** is a standard way for an AI app to talk to outside tools. An
  "MCP server" is a small program (here: Python scripts in `mcp_servers/`) that the app starts
  and asks things like "run this SQL" or "search these logs". Each server offers named *tools*.
* A **template** is a file with blanks to fill in. Here the blanks look like `${TSP_GRAFANA_URL}`
  and are filled from `.env`, so secrets never live in the template (which is in git).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from .config import MCP_TEMPLATE, ROOT, env_file_values, get_settings

# `${NAME}` inside the template → value of NAME from .env (`${ROOT}` → this project's path).
# Regex: `\$\{` is a literal "${", `([A-Z0-9_]+)` captures the name (group 1), `\}` is the "}".
_PLACEHOLDER = re.compile(r"\$\{([A-Z0-9_]+)\}")

# @dataclass writes __init__ for us; frozen=True makes objects read-only after creation
# (assigning srv.name = "x" raises an error), so nobody changes a server's rules by accident.
@dataclass(frozen=True)
class ServerInfo:
    """One server from the template, as the rest of the app sees it (no secrets in here)."""
    name: str
    system: str
    label: str
    kind: str
    deny: tuple[str, ...]  # `tuple[str, ...]` = a tuple of any number of strings
    default_off: bool = False  # a default value: may be left out when creating a ServerInfo


def _template() -> dict[str, Any]:
    """Read config/mcp_servers.json fresh every time, so edits apply without a restart."""
    return json.loads(MCP_TEMPLATE.read_text(encoding="utf-8"))


def catalogue() -> list[ServerInfo]:
    """Every server in the template, with its `_meta` parsed."""
    s = get_settings()
    out = []
    # `.items()` gives (key, value) pairs: name = "tsp_redash", spec = that server's dict.
    for name, spec in _template()["mcpServers"].items():
        meta = spec.get("_meta", {})  # {} if the server has no _meta block
        deny = tuple(meta.get("deny", []))
        # Notion's write tools are denied unless ALLOW_NOTION_WRITES=true in .env.
        gate = meta.get("deny_unless_env")
        if gate == "ALLOW_NOTION_WRITES" and s.allow_notion_writes:
            deny = ()
        out.append(ServerInfo(name, meta.get("system", "shared"), meta.get("label", name),
                              meta.get("kind", "other"), deny, bool(meta.get("default_off"))))
    return out


def servers_for(system: str | None, only: list[str] | None = None) -> list[ServerInfo]:
    """Servers allowed for a run: the system's own + shared; never the other estate.

    `only` (from the UI) picks a subset; default-off servers need to be named in it.
    """
    disabled = set(get_settings().disabled_servers)
    picked = []
    for srv in catalogue():
        # Each `continue` = "skip this server, go to the next one in the loop".
        if srv.name in disabled:
            continue
        # The isolation rule: a tsp run only gets tsp + shared servers, never tpap (and vice versa).
        if srv.system not in {"shared", system}:
            continue
        if only is not None and srv.name not in only:
            continue
        if only is None and srv.default_off:
            continue
        picked.append(srv)
    return picked


def _substitute(value: Any, env: dict[str, str], missing: set[str]) -> Any:
    """Recursively fill `${NAME}` placeholders; unknown names become "" and go into `missing`.

    "Recursively" = the function calls itself for lists and dicts, so placeholders nested at any
    depth get filled. isinstance(value, str) asks "is value a string?".
    Example: {"env": {"KEY": "${TSP_KEY}"}} → {"env": {"KEY": "abc123"}}
    """
    if isinstance(value, str):
        # rep() is called once per `${...}` match; whatever it returns replaces that match.
        def rep(m: re.Match[str]) -> str:
            key = m.group(1)
            if key == "ROOT":
                return str(ROOT)
            if key not in env:
                missing.add(key)
                return ""
            return env[key]
        return _PLACEHOLDER.sub(rep, value)
    if isinstance(value, list):
        return [_substitute(v, env, missing) for v in value]
    if isinstance(value, dict):
        return {k: _substitute(v, env, missing) for k, v in value.items()}
    return value


def rendered_spec(name: str) -> tuple[dict[str, Any], set[str]]:
    """One server's launch spec with placeholders filled (kept in memory only)."""
    missing: set[str] = set()  # a set = a collection with no duplicates
    # Dict comprehension with a filter: copy every key except "_meta".
    spec = {k: v for k, v in _template()["mcpServers"][name].items() if k != "_meta"}
    return _substitute(spec, env_file_values(), missing), missing


def missing_env(name: str) -> list[str]:
    """.env keys a server needs but that are absent or empty (shown in the MCP panel)."""
    raw = json.dumps({k: v for k, v in _template()["mcpServers"][name].items() if k != "_meta"})
    env = env_file_values()
    return sorted({k for k in _PLACEHOLDER.findall(raw) if k != "ROOT" and not env.get(k)})
