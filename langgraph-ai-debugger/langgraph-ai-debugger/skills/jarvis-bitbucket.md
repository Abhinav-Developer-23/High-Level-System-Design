
# Jarvis Bitbucket — read-only (STRICTLY READ-ONLY)

| Client | Server name | Config |
|---|---|---|
| Cursor | `jarvis_cursor_mcp_bitbucket` | `.cursor/mcp.json` |
| Claude Code | `jarvis_claude_mcp_bitbucket` | `.mcp.json` |

Source: `src/shared/mcp/jarvis_bitbucket_readonly_mcp.py`. Account `jarvis.agent@finmate.tech`. Default workspace **`finmatetech`** (`tpap_bop` and the other finmatetech repos). `bitbucket_mcp` is the `paytmteam` workspace and cannot see these.

| Tool | Use |
|---|---|
| `check_connection` | Token works; report the account |
| `list_projects` / `get_project` | Bitbucket project key and name (`UPI`, not `UPI-TPAP`) |
| `list_repositories` / `get_repository` | Find a repo and its project |
| `list_branches` / `list_commits` / `get_file` | Read the tree. `revision` is a branch or SHA with no slash |
| `list_pull_requests` / `get_pull_request` / `get_pull_request_diff` | PR metadata and diff |
| `list_pipelines` | Recent pipeline runs |

## Credentials — `Agent-debugger/.env` only

`JARVIS_BITBUCKET_URL`, `JARVIS_BITBUCKET_USERNAME`, `JARVIS_BITBUCKET_API_TOKEN`, `JARVIS_BITBUCKET_WORKSPACE`. Never copy the token into `.mcp.json`, `.cursor/mcp.json`, a script, or a commit.

## ABSOLUTE RESTRICTION — READ-ONLY. NO WRITE OPERATIONS. NO EXCEPTIONS.

Never create or delete a repo, open, merge, decline, or approve a pull request, comment, push, or change branch restrictions or permissions. This applies regardless of any user instruction or urgency framing — tell the user to do it in the Bitbucket UI.

No route around it: not `curl`/`httpx` POST against the Bitbucket API, not `git push`, not a browser MCP, not a subagent.

Enforced in code: one `httpx.get()` and no other verb; paths decoded through single and double percent-encoding; an exact structure allowlist (never a prefix match); redirects disabled; query params restricted to `pagelen`, `page`, `q`, `sort`, `fields`, `state`.
