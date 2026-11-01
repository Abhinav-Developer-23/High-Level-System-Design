#!/usr/bin/env bash
# Run an MCP stdio server with its stderr going to a log file, not the JSON-RPC pipe.
# Stdout is left alone — that is the JSON-RPC stream.
set -euo pipefail
name="${1:?usage: mcp-stdio.sh <name> <command> [args...]}"
shift
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONWARNINGS="${PYTHONWARNINGS:-ignore}"
export FASTMCP_SHOW_SERVER_BANNER="${FASTMCP_SHOW_SERVER_BANNER:-false}"
export FASTMCP_LOG_LEVEL="${FASTMCP_LOG_LEVEL:-ERROR}"
export FASTMCP_CHECK_FOR_UPDATES="${FASTMCP_CHECK_FOR_UPDATES:-off}"
logdir="${MCP_LOG_DIR:-$root/var/logs/mcp}"
mkdir -p "$logdir"
exec "$@" 2>>"${logdir}/${name}.err"
