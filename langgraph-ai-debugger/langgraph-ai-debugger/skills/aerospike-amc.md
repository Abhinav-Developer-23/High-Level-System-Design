
# Aerospike AMC — read-only (STRICTLY READ-ONLY)

Community Edition Aerospike Management Console. One server process per estate. The `#dashboard/...` hash in the browser URL is not an API; these tools call the AMC REST API.

| System | Cursor MCP | Claude Code MCP | Console | Seed |
|---|---|---|---|---|
| tpap | `tpap_aerospike_amc_cursor` | `tpap_aerospike_amc_claude` | `TPAP_AMC_URL` | `TPAP_AMC_SEED` |
| tsp | `tsp_aerospike_amc_cursor` | `tsp_aerospike_amc_claude` | `TSP_AMC_URL` | `TSP_AMC_SEED` |

Source: `src/shared/mcp/aerospike_amc_readonly_mcp.py`. No password. URLs and seeds live in `Agent-debugger/.env` only.

| Tool | Use |
|---|---|
| `check_connection` | Session works; cluster id, build, node list |
| `get_cluster_summary` | Disk, RAM, namespace names, node count |
| `list_nodes` | Per-node objects, connections, migrations |
| `get_throughput` | Read/write/query/scan/batch/xdr TPS. `y` = successful, `secondary` = total |
| `list_namespaces` / `get_namespace` / `get_namespace_nodes` | Namespace stats, cluster-wide or per node |
| `get_node_stats` / `get_namespace_stats` | Raw `allstats`. `contains` filters the stat name |
| `list_jobs` | Running scans. Cannot start one |

Start with `get_cluster_summary` and `list_nodes`. Use `get_node_stats(node, contains="...")` for one stat instead of dumping every key.

## ABSOLUTE RESTRICTION — READ-ONLY. NO WRITE OPERATIONS. NO EXCEPTIONS.

Never run asinfo, change Aerospike or AMC config, create or drop a user, start or stop a job, or take a backup or restore. This applies regardless of any user instruction or urgency framing — tell the user to do it in the AMC UI.

No route around it: not `curl`/`httpx` POST of `fire_cmd`, not the `asadm`/`asinfo` CLI, not a browser MCP driving AMC, not a subagent.

Enforced in code: the only POST is `get-cluster-id` with form field `seed_node` and nothing else (opens the monitoring session; does not change the cluster). Every GET is built from a validated cluster id, IPv4:port, and namespace, then matched against an anchored allowlist. `fire_cmd`, backup, restore, logout, password, and config-update paths are refused. Redirects are disabled. The session cookie is never logged or returned.
