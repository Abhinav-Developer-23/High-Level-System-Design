
# Grafana Access

Two paths: **`*_grafana` MCP** (live API, read-only) and **local JSON exports** (fallback for panel/metric lookup).

## MCP — `tpap_grafana` / `tsp_grafana`

Both read-only (`--disable-write` flag — no create/update). Use the one matching the system the user specified.

Capabilities: dashboards (search, get, panel queries), datasources, Prometheus + Loki queries, ClickHouse via Grafana, Elasticsearch via Grafana, incidents, Sift investigations, alerts, on-call, Pyroscope, deeplinks, dashboard PNG render.

**Prometheus rule:** ALL PromQL via `query_prometheus`. No curl, no Redash, no `*_elk`.

- TPAP → `tpap_grafana`, datasource `Prometheus-TPAP` uid `e6d5cdaa-2ddd-4314-9d92-3039eafa003e`
- TSP → `tsp_grafana`, discover uid via `list_datasources(type="prometheus")`

Common workflow:
1. `get_dashboard_panel_queries(uid, panelId)` — extract raw PromQL/ES from a panel
2. `get_dashboard_property(uid, jsonPath="$.templating.list")` — resolve template vars (e.g. `$new_host_name`)
3. `query_prometheus(datasourceUid, expr, queryType, ...)` — run PromQL
4. Or replay ES panel queries via `*_elk` MCP for richer aggregations

Timestamps without offset are interpreted as UTC. Use `-05:00` style offset or relative `now-1h` to query in another timezone.

## Critical Dashboards

### TPAP (https://monitor.mypaytm.com, orgId=12)

| Dashboard | UID | Use For |
|-----------|-----|---------|
| TPAP UPI War Room | `a9e480fd-6fe8-448a-bb68-149caa5952ce` | Primary incident view — start here |
| UPI Issuer | `b56b8168-521f-4763-b47c-b9753ef715e6` | Issuer-side flows |
| HSS | `c13313e7-71c2-4287-a0b9-debcd7d4ee65` | HSS service health |
| TPAP Consumers Set1 Alert | `fc509496-0f1d-4e63-b727-c6817cef590c` | Kafka consumers (set1) |
| New Mindgate HDFC | `b0661271-c0b5-4338-8667-5c96a3e11aez` | GWTS Mindgate HDFC |
| New Mindgate SBI | `b0661271-c0b5-4338-8667-5c96a3e11qkl` | GWTS Mindgate SBI |
| TPAP Gateway OCIL Switch | `f6342fb3-afcf-4111-8b18-052e0b57ab54c` | GWTS OCIL Yes Bank |
| New Juspay Axis | `a9f71d26-cedd-4bcb-8e90-6213d1d15d30` | GWTS Juspay Axis |

**Metis eBPF network boards** — `metis-mysql`, `metis-dns`, `metis-tcp-connection-stats`, `metis-tcp-retransmits-resets`, `metis-public-ips`. They give client-side DB latency, DNS, TCP RTT, retransmits/resets and public-IP egress. They default to `Global-Thanos`, which is **non-prod**; prod is `Prometheus-TPAP`. See `metis.mdc`.

### TSP (https://paytmybl-grafana.paytmybl.com)

- **UPI War Room** — UID `DNTezbS7z` — primary TSP incident view. Key rows: NPCI Health Sentinel, SR and Txn Count (C2/C3/C6 acquiring SR), App Failure Codes, Switch Pod Counts by Status, Technical Decline, PG Metrics, DB Latency Metrics, Aerospike Metrics[Switch], DB ConnectionPool Metrics, NPCI Metrics, Major APIs Traffic, NPCI Issue Failure Codes, 2xx/4xx/5xx, Success/Pay Ratio, Tpap callback, External Client Connectivity, TAT Metrics.
- **UPI Recon Sys** — UID `AeeTFFY4z` — recon health (PSP, PG, refund, cross-cluster). Full panel id list in workspace `CLAUDE.md`.

## Local Dashboard JSON Storage (fallback)

Some dashboards may be available only as local JSON exports (kept for offline panel lookup).

| System | Folder |
|--------|--------|
| TSP | `/Users/abhinavanand/personal_projects/Agent-debugger/resources/grafana-boards/tsp/` |
| TPAP | `/Users/abhinavanand/personal_projects/Agent-debugger/resources/grafana-boards/tpap/` |

User exports JSON from: Grafana → Dashboard settings → JSON model → Copy.
File naming: snake_case dashboard title, e.g. `tsp_switch_overview.json`. One file per dashboard.

## How to Find a Panel for a Metric

Prefer MCP first; fall back to local JSON if dashboard not reachable.

**MCP path:** `search_dashboards(query=...)` → `get_dashboard_panel_queries(uid)` → match metric in panel `expr`.

**Local JSON path:**
1. Grep the metric name (or partial) across all `.json` files in the relevant system folder
2. For each match, walk up the JSON to find:
   - Root `title` → dashboard name
   - Parent `row`-type panel title → row name (if panel is nested inside a row)
   - Panel `title` → panel name
3. Output format:
   ```
   Dashboard: <dashboard title>  →  Row: <row title>  →  Panel: <panel title>
   ```
   If no parent row (flat layout), omit the Row part.
4. If multiple panels match, list all — user picks the most relevant

## JSON Structure Reference

```json
{
  "title": "TSP Switch Overview",
  "panels": [
    {
      "title": "TXN Success Rate",
      "targets": [
        { "expr": "rate(metric_name[5m])" }
      ]
    },
    {
      "title": "Row Header",
      "type": "row",
      "panels": [
        {
          "title": "Nested Panel",
          "targets": [{ "expr": "other_metric" }]
        }
      ]
    }
  ]
}
```

## Rules

- Never curl Grafana URLs directly — always go via the matching `*_grafana` MCP
- If MCP unreachable and folder empty: tell user to export and drop JSON
- One JSON file per dashboard
- After user drops a new JSON, it is immediately usable — no indexing needed
