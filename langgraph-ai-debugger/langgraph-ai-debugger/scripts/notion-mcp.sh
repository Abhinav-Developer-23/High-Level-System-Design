#!/usr/bin/env bash
# Launch the official Notion MCP server (read + write) with NOTION_TOKEN from the
# workspace .env. The token must never be copied into .mcp.json / .cursor/mcp.json.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${NOTION_TOKEN:-}" && -f "$root/.env" ]]; then
  NOTION_TOKEN="$(sed -n 's/^NOTION_TOKEN=//p' "$root/.env" | tail -n 1 | tr -d "\"'\r")"
fi
if [[ -z "${NOTION_TOKEN:-}" ]]; then
  echo "notion-mcp: NOTION_TOKEN missing from $root/.env" >&2
  exit 1
fi
export NOTION_TOKEN
export PATH="/opt/homebrew/bin:/usr/bin:/bin:${PATH:-}"
exec npx -y @notionhq/notion-mcp-server@2.5.2
