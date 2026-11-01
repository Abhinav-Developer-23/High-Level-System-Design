
# Metrics Debugging Rules

Correlate with the debugging protocol: metrics are step 4 after logs and DB when forming a full RCA.

## Routing — always via Grafana MCP

ALL PromQL queries MUST go through the `*_grafana` MCP `query_prometheus` tool. No curl to Prometheus, no Redash, no `*_elk`.

- TPAP → `tpap_grafana`, datasource `Prometheus-TPAP` uid `e6d5cdaa-2ddd-4314-9d92-3039eafa003e`
- TSP → `tsp_grafana`, discover uid at runtime via `list_datasources(type="prometheus")`

Common workflow:
1. `get_dashboard_panel_queries(uid, panelId)` — extract raw PromQL/ES from a panel
2. `get_dashboard_property(uid, jsonPath="$.templating.list")` — resolve template variables (e.g. `$new_host_name`)
3. `query_prometheus(datasourceUid, expr, queryType, ...)` — run PromQL

ES queries from Grafana panels can be replayed via `*_elk` MCP for richer aggregations.

## Critical dashboards

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

### TSP (https://paytmybl-grafana.paytmybl.com)

- **UPI War Room** — UID `DNTezbS7z` — primary TSP incident view (NPCI, PG, switch, DB, pods, traffic, SR, failure codes). Key rows: NPCI Health Sentinel, SR and Txn Count, App Failure Codes, Switch Pod Counts, Technical Decline, PG Metrics, DB Latency, Aerospike, NPCI Metrics, Major APIs Traffic, NPCI Issue Failure Codes, 2xx/4xx/5xx, Success/Pay Ratio, Tpap callback, External Client Connectivity, TAT Metrics.
- **UPI Recon Sys** — UID `AeeTFFY4z` — recon health (PSP, PG, refund, cross-cluster). See workspace `CLAUDE.md` for full panel id list.

## Investigation Order
1. Error rate — is error % elevated?
2. Latency (p50, p95, p99) — where is slowness?
3. Throughput — traffic spike or drop?
4. Resource: CPU, memory, DB connections, disk I/O
5. Downstream: dependency latency, error rate

## Key Signals by Symptom

### Slow responses
- p95/p99 latency spike
- DB query time (slow query log)
- Downstream service latency
- Thread pool / connection pool exhaustion

### 5xx errors
- Error rate by endpoint
- Exception type distribution in logs
- Dependency health (DB, cache, external APIs)

### Memory / CPU spike
- GC pressure (JVM) or memory leak pattern
- Unusual traffic pattern
- Recent deploy (check deploy timestamp vs spike)

## Correlation Rule
Always note the **exact timestamp** of metric anomaly, then search logs in ±5min window around it.

## Prometheus / Grafana PromQL Patterns

### Error rate
```promql
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

### p95 latency
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Memory usage
```promql
container_memory_usage_bytes{pod=~"payment.*"} / container_spec_memory_limit_bytes
```

## Output Format
- State: metric name, current value, baseline, delta
- Example: "p95 latency: 2.3s (baseline 200ms) — 11x spike starting 14:32 UTC"
