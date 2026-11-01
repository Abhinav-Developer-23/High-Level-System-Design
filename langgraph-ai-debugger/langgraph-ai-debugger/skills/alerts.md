
# Alert Debugging Workflow

When the user gives an alert name, follow these steps **in order**.

## 0 — Fired alerts (live paging data, read-only)

To see what actually fired — titles, state, who acked, when — use the paging MCPs:

- TPAP → `tpap_paytm_caller_mcp_cursor` (Claude Code: `tpap_paytm_caller_mcp_claude`) — `list_alerts`, `get_alert(include_call_analytics=True)`
- TSP → `tsp_zenduty_mcp_cursor` (Claude Code: `tsp_zenduty_mcp_claude`) — `list_incidents(team="tsp-txn")`, `get_incident`, `get_alert_payload`

**Get the metric directly from the alert first.** A TSP Zenduty alert's payload carries the PromQL `expr` (decoded from `generatorURL`), the fired value and the labels. With that, skip steps 1–3 and go straight to replaying the expr via `tsp_grafana`. Firing window: `ALERTS{alertname="…"}` (TSP on Thanos `cdtc3m6pcvfgge`, TPAP on `Prometheus-TPAP`). Use steps 1–3 only for TPAP alerts (PaytmCaller has no payload) or when the payload is empty.

**Read-only only.** Tools, the absolute no-write restriction, and the read-only `curl` fallback for missing features: see `paging-alerts.mdc`.

## 1 — Find alert in repo

| System | Repo | Key files |
|--------|------|-----------|
| TSP | `/Users/abhinavanand/Finmate_Projects/TSP-alerts/` | `paytmybl-prod-*.rules.yml`, `paytmybl-dr-*.rules.yml`, `paytmybl-upi-*.rules.yml` |
| TPAP | `/Users/abhinavanand/Finmate_Projects/paytm-alerts/` | `tpap.upi.switch.rules.yml`, `tpap.upi.switch.critical.rules.yml`, `bank.upi.switch.rules.yml`, `bank.upi.switch.new.alerts.teams.rules.yml` |

If system not specified, ask before searching.

## 2 — Extract metric from `expr`

Read the `expr` field for the Prometheus metric and threshold.

## 3 — Search source for metric

Convert metric name → code search string:

1. Strip first segment + `_` (service prefix)
2. Strip last segment + `_` (type suffix: `_value`, `_total`, `_count`)
3. Replace remaining `_` with `.`
4. Grep in source repo

Example: `tspupirouter_metric_for_txn_info_participants_value`
→ `metric.for.txn.info.participants`

Sources: tpap switch → `/Users/abhinavanand/Finmate_Projects/tpap-transactional-switch` (own repo). Monorepo `/Users/abhinavanand/personal_projects/Agent-debugger/repos/upi-tpap-transactional-monorepo` is only `tpap-reporting`, `tpap-transactional-jobs`, `tpap-archiver`, `tpap-stream-recon`, `tpap-consumers`, `tpap-compliance`. tsp → `/Users/abhinavanand/Finmate_Projects/tsp-transactional-switch`.

## 4 — Find Grafana panel

Grep metric in local dashboard JSONs:

| System | Folder |
|--------|--------|
| TSP | `resources/grafana-boards/tsp/` |
| TPAP | `resources/grafana-boards/tpap/` |

Output: `Open dashboard **[title]** → row **[row]** → panel **[panel]**` (omit row if flat).

## 5 — Log lines for the user (do not search ELK yourself)

Give: index pattern, exact KQL/Lucene (logger class + keywords), time window, what to look for. User searches Kibana and shares results.

## 6 — RCA (after user shares logs)

Correlate alert `expr` + source + logs. Lead with the finding.
