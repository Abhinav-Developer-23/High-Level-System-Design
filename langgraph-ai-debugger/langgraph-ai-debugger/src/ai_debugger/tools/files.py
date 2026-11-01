"""File tools: read and search the project's docs (DB schemas, flow docs, NPCI guides, skills).

They replace Claude Code's built-in Read / Grep. Paths are confined to `resources/` and
`skills/`: `../.env` or an absolute path is refused.
"""

from __future__ import annotations

import re
from pathlib import Path

from langchain_core.tools import tool

from ..config import RESOURCES_DIR, ROOT, SKILLS_DIR

_ROOTS = (RESOURCES_DIR.resolve(), SKILLS_DIR.resolve())


def _safe(path: str) -> Path:
    """Resolve a project-relative path and refuse anything outside resources/ and skills/."""
    p = (ROOT / path).resolve()
    if not any(p.is_relative_to(r) for r in _ROOTS):
        raise ValueError("Only files under resources/ and skills/ can be read.")
    if not p.is_file():
        raise ValueError(f"No such file: {path}")
    return p


@tool(parse_docstring=True)
def read_resource(path: str, offset: int = 0, limit: int = 200) -> str:
    """Read a text file from resources/ or skills/ (DB schemas, call-flow docs, NPCI error guides).

    Args:
        path: Path from the project root, e.g. "resources/flows/lite_flow.md".
        offset: First line to return, 0-based.
        limit: How many lines to return (max 400).
    """
    lines = _safe(path).read_text(encoding="utf-8", errors="replace").splitlines()
    limit = max(1, min(limit, 400))
    chunk = lines[offset:offset + limit]
    more = f"\n… {len(lines) - offset - limit} more lines (use offset={offset + limit})" if offset + limit < len(lines) else ""
    return "\n".join(f"{offset + i + 1}: {ln}" for i, ln in enumerate(chunk)) + more


@tool(parse_docstring=True)
def search_resources(pattern: str, glob: str = "**/*.md") -> str:
    """Search resources/ and skills/ with a regex and return matching lines as file:line: text (max 50).

    Args:
        pattern: Case-insensitive regular expression, e.g. "U30|ZM" or "check status".
        glob: Which files to search, e.g. "**/*.md" or "db_schema/*.md".
    """
    rx = re.compile(pattern, re.I)
    hits: list[str] = []
    for root in _ROOTS:
        for f in sorted(root.glob(glob)):
            if not f.is_file():
                continue
            for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if rx.search(line):
                    hits.append(f"{f.relative_to(ROOT)}:{n}: {line.strip()[:200]}")
                    if len(hits) >= 50:
                        return "\n".join(hits) + "\n… (first 50 matches)"
    return "\n".join(hits) or "No matches."


FILE_TOOLS = [read_resource, search_resources]
