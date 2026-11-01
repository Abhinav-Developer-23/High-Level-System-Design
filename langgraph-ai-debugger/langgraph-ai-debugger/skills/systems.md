
# System Architecture

Two independent production systems: **tpap** and **tsp**. Separate infra, separate data — never cross-query.

## Endpoints

| Tool | tpap | tsp |
|------|------|-----|
| Redash | https://tpapredash.paytm.com | https://paytmybl-redash.paytmybl.com |
| Elasticsearch/Kibana | https://tpapprod-logging-elk.paytm.com | https://kibana.paytmybl.com |
| Archival logs | https://upi-ai-agent.paytm.com | Not available |
| Grafana | https://monitor.mypaytm.com (orgId=12) | https://paytmybl-grafana.paytmybl.com |
| Prometheus | via `tpap_grafana` → `Prometheus-TPAP` (`e6d5cdaa-2ddd-4314-9d92-3039eafa003e`) | via `tsp_grafana` — discover UID with `list_datasources` |

## MCP Servers (Cursor project: `.cursor/mcp.json`)

| Server | System | Capability |
|--------|--------|------------|
| `tpap_redash` | tpap | DB |
| `tpap_elk` | tpap | Elasticsearch/Kibana |
| `tpap_archival_logs` | tpap | Archived application logs older than ELK retention |
| `tpap_grafana` | tpap | Grafana + Prometheus (read-only) |
| `tpap_atlassian` | tpap | Jira + Confluence (read-only) |
| `tpap_jenkins` | tpap | Jenkins — read + gated build trigger |
| `tsp_redash` | tsp | DB |
| `tsp_elk` | tsp | Elasticsearch/Kibana |
| `tsp_grafana` | tsp | Grafana + Prometheus (read-only) |
| `tsp_atlassian` | tsp | Jira + Confluence (read-only) |
| `tsp_jenkins` | tsp | Jenkins (read-only — no trigger tool) |
| `tsp_prod_argocd` | tsp | **Prod ArgoCD (read-only — no sync/rollback/patch/delete)** |
| `tpap_paytm_caller_mcp_cursor` | tpap | **PaytmCaller fired alerts (read-only — no ack/mark-in-progress)** — see `paging-alerts.mdc` |
| `tsp_zenduty_mcp_cursor` | tsp | **Zenduty incidents (read-only — no ack/resolve); team `tsp-txn`** — see `paging-alerts.mdc` |
| `bitbucket_mcp` | shared | Bitbucket `paytmteam` workspace |
| `tpap_aerospike_amc_cursor` (Claude Code: `tpap_aerospike_amc_claude`) | tpap | **Aerospike AMC (read-only — no asinfo/backup/config change)** — see `aerospike-amc.mdc` |
| `tsp_aerospike_amc_cursor` (Claude Code: `tsp_aerospike_amc_claude`) | tsp | **Aerospike AMC (read-only — no asinfo/backup/config change)** — see `aerospike-amc.mdc` |
| `jarvis_cursor_mcp_bitbucket` (Claude Code: `jarvis_claude_mcp_bitbucket`) | shared | **Jarvis Bitbucket, default workspace `finmatetech` (read-only — no create/merge/approve/comment)** — see `jarvis-bitbucket.mdc` |
| `google_workspace_readonly_cursor` | shared | **Google Docs / Sheets / Drive (read-only scopes only)** — see `google-workspace.mdc` |
| `gmail_readonly_cursor` | shared | **Gmail (gmail.readonly only)** — see `gmail.mdc` |
| `notion_cursor` (Claude Code: `notion_claude`) | shared | Notion — **read + write** (official `@notionhq/notion-mcp-server` via `scripts/notion-mcp.sh`; `NOTION_TOKEN` in `.env` only). Sees only pages shared with the `MCP_TOKEN` connection |

**Prometheus:** ALL PromQL via matching `*_grafana` → `query_prometheus`. No curl, Redash, or `*_elk` for metrics.

## Isolation rules

- User specifies system ("on tpap", "for tsp"); if missing → ask before any query
- Never use tpap credentials/endpoints for tsp or vice versa
- Each system has its own DB schema — do not assume shared tables
