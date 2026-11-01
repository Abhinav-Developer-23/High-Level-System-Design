
# Elasticsearch / Kibana Debugging Rules

**Elasticsearch, Kibana, ES, and ELK** mean the same thing here — use `tpap_elk` / `tsp_elk` MCP tools for the correct system.

Use **`tsp_elk`** tools (`search_logs`, `search_logs_dsl`, `list_indices`, `get_index_mapping`) for all tsp Elasticsearch/Kibana queries.

## Transaction debugging — DB + applicable log store in parallel

When the user gives a txnId to debug, run DB and the applicable log-store query in parallel. Never only one.

- DB: `SELECT *` on txn record **and** participants — full rows.
- Within ELK retention: use Kibana with a plain txnId query (no field prefix), always `now-3d` to `now`.
- Older than 3 days on TPAP: use `tpap_archival_logs` after obtaining mandatory partition inputs. Do not query ELK outside retention.

Correlate both before concluding.

### Kibana log search priority for txnId

**Start with primary switch indices only** — do not query every service on the first pass.

User specifies **tpap or tsp** — never both for the same txn.

**Highest priority:** If the user names a cluster (c2/c3/c6) or a specific service, query **only** that — no expansion.

**Default first-pass** (only txnId + system, no cluster/service):

- **tpap:** `prod-tpap-transactional-switch-*,prod-tpap-transactional-switch_exchange*`
- **tsp:** all three clusters, all log types, **in parallel:**
  - App: `prod-paytmybl-tsp-switchc2-*`, `prod-paytmybl-tsp-switchc3-*`, `prod-paytmybl-tsp-switchc6-*`
  - Exchange: `prod-paytmybl-tsp-switchc2_exchange*`, `prod-paytmybl-tsp-switchc3_exchange*`, `prod-paytmybl-tsp-switchc6_exchange-*`
  - Access: `prod-paytmybl-tsp-switchc2_access*`, `prod-paytmybl-tsp-switchc3_access*`, `prod-paytmybl-tsp-switchc6_access-*`

**Expand** beyond primary switch (consumers, BFF, recon, GWTS) **only if** txnId is not found in the first pass or the user asks.

**Timing in every txn debug response:** first event (earliest DB `created_on` or first log), last event (latest log or DB `updated_on`), total duration; format `Total time: Xms (HH:MM:SS.mmm → HH:MM:SS.mmm IST)`.

## tpap — team-owned indices (ONLY these for tpap ES/Kibana)

| Index pattern | Service |
|---------------|---------|
| `prod-tpap-transactional-switch-*,prod-tpap-transactional-switch_exchange*` | Transactional switch (combined) — primary app logs |
| `prod-tpap-transactional-switch_access-*` | Switch access logs (HTTP access) |
| `prod-tpap-transactional-bff-*` | Transactional BFF app logs |
| `prod-tpap-transactional-bff_access-*` | BFF access logs (HTTP access) |
| `prod-tpap-consumers-set1-switch-*` | Kafka consumers set1 — receivers, risk, notifications |
| `prod-tpap_gwts_mindgate-hdfc-*` | GWTS Mindgate HDFC gateway |
| `prod-tpap_gwts_mindgate-sbi-*` | GWTS Mindgate SBI gateway |
| `prod-tpap-gwts-ocil-switch-yes-*` | GWTS OCIL Yes Bank switch |
| `prod-tpap_gwts_juspay-axis-*` | GWTS Juspay Axis gateway |

**Never query other indices** unless the user explicitly requests it.

## tsp — team-owned indices (ONLY these for tsp ES/Kibana)

| Index pattern | Service |
|---------------|---------|
| `prod-paytmybl-tsp-switchc2-*` | Switch cluster 2 — primary app logs |
| `prod-paytmybl-tsp-switchc3-*` | Switch cluster 3 — primary app logs |
| `prod-paytmybl-tsp-switchc6-*` | Switch cluster 6 — primary app logs |
| `prod-paytmybl-tsp-switchc2_exchange*` | Switch c2 exchange logs (NPCI XML) |
| `prod-paytmybl-tsp-switchc3_exchange*` | Switch c3 exchange logs (NPCI XML) |
| `prod-paytmybl-tsp-switchc6_exchange-*` | Switch c6 exchange logs (NPCI XML) |
| `prod-paytmybl-tsp-switchc2_access*` | Switch c2 HTTP access logs |
| `prod-paytmybl-tsp-switchc3_access*` | Switch c3 HTTP access logs |
| `prod-paytmybl-tsp-switchc6_access-*` | Switch c6 HTTP access logs |
| `prod-paytmybl-tsp-stream-recon-c1-*` | Stream recon — **all clusters** (C1/C2/C3/C6 data; index name contains `c1` but is not c1-only) |

**Default query behavior:** Unless the user specifies a cluster (c2/c3/c6), query **all** owned switch clusters in parallel. Stream-recon for all clusters is in `prod-paytmybl-tsp-stream-recon-c1-*` (name is misleading).

**Never query other indices** unless the user explicitly requests it.

## TPAP archival logs (older than ELK retention)

- For TPAP logs older than 3 days, or when the user explicitly asks for archival logs, use `tpap_archival_logs` instead of `tpap_elk`.
- Before any archival search, obtain all mandatory inputs from the user: search identifier/pattern (prefer txn ID or RRN), exact timestamp with timezone, `service`, and `log_type` (for example `application-logs`). Convert the timestamp to archive `date` (`YYYY-MM-DD`) and `hour` (`00`–`23`); ask about any ambiguity instead of guessing. TPAP archive paths observed so far use IST hours.
- If the service or log type is unknown, call `list_search_options`, present the relevant current choices, and ask the user to select them. Do not start a search or infer a service from the transaction ID.
- Prefer `search_archival_logs` so the MCP starts, polls, and downloads the job while emitting percentage and elapsed-time progress.
- **Before starting:** tell the user the archival query is running and may take a long time. While it runs, keep the user informed with the reported percentage and elapsed time.
- If the `tpap_archival_logs` MCP is unavailable because its process, transport, or tool registration is broken, call the same HTTPS API directly instead of abandoning the investigation. Use a short-lived Python/httpx process: form-login to `/login` with `TECHOPS_AGENT_EMAIL` and `TECHOPS_AGENT_PASSWORD`, keep its session cookie only in memory, then use `/api/search-logs`, `/api/check-search-status`, `/api/download-search-results`, and `/api/stop-search`. Never print or persist the cookie/password. Preserve all mandatory-input, progress-reporting, five-slot parallelism, cancellation, and `tmp/logs/archival/` download rules.
- Direct API access is not a workaround for a definitive API authentication, authorization, or provider failure. Confirm such a failure once, report it, and stop. Do not repeatedly retry credentials.
- Use `start_search` only when asynchronous/manual control is needed; then use `check_search_status`, `download_search_results`, or `stop_search` with its `job_id`.
- For multiple txn IDs/RRNs, use `search_archival_logs_parallel`. A batch contains at most 10 searches, runs at most 5 concurrently, and queues the remainder client-side while reporting aggregate percentage, finished count, and elapsed time. Every batch item still requires its own mandatory pattern, timestamp, service, and log type.
- A live probe on 2026-09-11 showed that the API admits at least 7 jobs with status `in_progress`, but only jobs 1–5 advanced; jobs 6–7 stayed at 0% for over 4 minutes. Treat 5 as the observed execution-slot limit and queue excess work client-side. The provider's exact account-wide maximum is not publicly documented. Do not launch direct searches alongside a full 5-job batch.
- Never equate an accepted or `in_progress` job with active execution. When validating concurrency, poll repeatedly for several minutes and compare changes in `files_processed` and `progress_percent`; report admitted jobs and demonstrably advancing jobs separately.
- For a **full archived transaction debug**, call `search_archival_logs_parallel` with `full_transaction_trace=true` and search the same exact txn ID across every user-confirmed relevant archive target. Confirmed portal targets include `tpap-transactional-switch` with `application-logs`, that same service with `exchange-logs`, and `tpap-consumers` with `application-logs`; include any other user-selected service. Each service/log-type combination is a separate batch item.
- Full-debug searches must run to completion and download every matching txn line. Do not use `stop_after_matches` or `result_filter_regex`, because either can omit later stages of the transaction.
- "Full txn logs" means all lines matching that txn ID across the selected services—not unfiltered hourly logs containing unrelated transactions. Only download an entire raw hourly service archive if the user explicitly asks for that much broader data.
- If the transaction is near an hour boundary or evidence shows processing in another hour, add each relevant date/hour partition as a separate batch item.
- The archive backend's `pattern` is a **literal substring**, not a regex. Verified on 2026-09-11: an exact txn string produced 6 matches by file 6, while the equivalent character-class pattern processed through file 18 with 0 matches. Search the backend with an exact txn ID, RRN, or distinctive literal log fragment. For regex matching, let the backend search finish and use `result_filter_regex` or `filter_search_results` locally afterward. Example: `(?i)sending\s+(?:generic\s+)?promo\s+data`.
- For fast early-stop, use a distinctive literal backend pattern plus `stop_after_matches`. Local regex cannot trigger server early-stop because it runs only after download.
- `stop_after_matches` uses the status API's verified `match_count` field. Do not use it with a broad txn-ID search when a later specific log line is required, because the first txn match may occur before that line.
- Archive retention is not established. Do not claim an older date is unavailable without querying it.
- Downloads default to the workspace's gitignored `tmp/logs/archival/` directory with user-only permissions. Never persist session cookies. Log contents are reported in full — no masking of VPA/account/mobile; they stay local and are never published or uploaded.

### Long-running archival bug workflow

Archival scans commonly take 15–60+ minutes. Do not spend that time waiting idly, abandon the investigation, or start duplicate searches.

1. After obtaining every mandatory input, start archival work at the beginning of the investigation. For a long RCA, prefer immediate `start_search` calls over one blocking call; start no more than 5 targets and queue the rest locally.
2. Record every job ID and its target metadata in a user-only (`0600`) case manifest under `tmp/logs/archival/jobs/`. Never store a password or session cookie there.
3. While the server scans, continue independent evidence gathering: query the DB, inspect source flow, check applicable metrics, and prepare the transaction timeline. Do not wait vacuously.
4. Poll with `check_search_status` while doing other work, normally every 30–60 seconds. Report to the user at meaningful changes (approximately every 5 percentage points or 5 minutes), and immediately for matches, restore prompts, failures, completion, or cancellation. Do not invent an ETA from early progress.
5. Use `wait_for_search(job_id, ...)` to reattach and monitor without launching another job. A monitoring timeout pauses only the MCP call; the server job continues. Resume with the same job ID. If the MCP transport fails, use the direct API fallback with that same job ID.
6. If progress remains at 0%, inspect `archive_state`, `restore_prompt`, and `progress_message`; an archive restore or provider queue is not automatically a hung job. Do not restart merely because progress is slow.
7. On completion, download into `tmp/logs/archival/`, apply local regex filtering when appropriate, then correlate logs with DB/source/metrics. If the local download fails, keep the completed job ID, fix the local problem, and retry `download_search_results`; never rescan. Full transaction traces must complete all selected service/log-type targets and must not use early-stop or result filtering.
8. Stop a job only when the requested distinctive literal line has been found, the user cancels it, or continuing is definitively unsafe/useless. After stopping, confirm a terminal state. Never leave an untracked server job running.

## ELK retention and windows

- **ELK max is 3 days.** Never query ELK beyond `now-3d`. For older TPAP logs, use `tpap_archival_logs`; no archival MCP exists for TSP.
- **Default** (non-txnId): last **1h** unless an incident window is known.
- **txnId searches:** always **`now-3d` to `now`**.
- **Error spike / RCA at a specific time:** use **`[T−30min, T+30min]`** (1h centered on T). If the user gives two timestamps, run both windows in parallel and diff counts, messages, stack traces.

## Production log levels

Only **INFO, WARN, ERROR**. Do not query `log.level:DEBUG` or `TRACE` — they do not exist in prod.

## Log sort order

Always fetch logs in **ascending** order (`sort_desc: false`) for chronological timelines. Sort field: **`@timestamp`** (UTC). Do **not** sort by `log.instant` (string with offset — not reliably sortable in ES).

## Source repos — log correlation

**Monorepo, six services only (debugging checkout):** `/Users/abhinavanand/personal_projects/Agent-debugger/repos/upi-tpap-transactional-monorepo`

`tpap-reporting`, `tpap-transactional-jobs`, `tpap-archiver`, `tpap-stream-recon`, `tpap-consumers` (was `tpap-consumers_java_17`), `tpap-compliance`. Debug them from this `repos/` checkout only. It stays on `main`; the `~/Finmate_Projects` checkouts are dev copies, often on a feature branch. Read-only, and search it by explicit path (`repos/` is gitignored). Full rule: `tpap-monorepo.mdc`.

Every other TPAP service stays on its own repo. Do not use a copy inside the monorepo checkout for these:

| Repo | Service |
|------|---------|
| `/Users/abhinavanand/Finmate_Projects/tpap-transactional-switch` | core switch — pay request, check status, callbacks |
| `/Users/abhinavanand/Finmate_Projects/tpap-transactional-bff` | transactional BFF |
| `/Users/abhinavanand/Finmate_Projects/tpap-hss` | HSS |
| `/Users/abhinavanand/Finmate_Projects/tpap_gwts_hdfc` | GWTS Mindgate HDFC gateway |
| `/Users/abhinavanand/Finmate_Projects/tpap_gwts_axis` | GWTS Juspay Axis gateway |
| `/Users/abhinavanand/Finmate_Projects/tpap_gwts_ocil` | GWTS OCIL Yes Bank gateway |
| `/Users/abhinavanand/Finmate_Projects/tpap_gwts_sbi` | GWTS Mindgate SBI gateway |
| `/Users/abhinavanand/Finmate_Projects/paytm-alerts` | Prometheus alert rules |

**TSP monorepo (cut over, read-only, debugging checkout):** TSP has cut over: every service was resynced into the monorepo between 17 and 30 Sep 2026, and work and release branches now merge there. Its README still says "not yet cut over" — that is stale. Same rules as the TPAP checkout: read-only, kept on `main` by the 5-minute cron pull (never pull it yourself), search it by explicit path.

| Directory inside the monorepo | Service |
|------|---------|
| `tsp-stream-recon/` | stream reconciliation |
| `tsp-archiver/` | archiver (`TxnInfoArchiveTask`) |
| `tsp-jobs/` | jobs |
| `tsp-consumers/` | Kafka consumers |
| `tsp_router/` | switch router |
| `tsp_aggregator/` | aggregator |
| `tsp_reporting/` | reporting |
| `tsp_compliance/` | compliance |

**Exception — the TSP switch.** The monorepo's `tsp-transactional-switch/` was last resynced on 17 Sep 2026 and misses `TSP-4926-reland` (merged 25 Sep in the standalone repo). Debug the switch from the standalone repo until the monorepo copy is resynced:

| Repo | Service |
|------|---------|
| `/Users/abhinavanand/Finmate_Projects/tsp-transactional-switch` | tsp core switch |
| `/Users/abhinavanand/Finmate_Projects/TSP-alerts` | tsp Prometheus alert rules |

**Never touch the user's checkout** — read `main` from a temporary worktree under `tmp/worktrees/` and remove it when done. Full rule: `tpap-monorepo.mdc`.

Logger class names in logs map to Java classes. For flows (payment, callback, recon, compliance, etc.), trace across the relevant services (switch → BFF → consumers → recon → HSS → compliance). Use `/graphify` for deep exploration or relationship mapping when needed.

## Kibana URL generation — TSP (kibana.paytmybl.com)

Use **saved index pattern IDs** in Discover URLs — not raw ES index strings (raw strings force manual index selection).

**URL template (Kibana 8.x):**

```
https://kibana.paytmybl.com/app/discover#/?_g=(filters:!(),time:(from:'<UTC_FROM>',to:'<UTC_TO>'))&_a=(columns:!('@timestamp',log.message,log.loggerName),dataSource:(dataViewId:'<PATTERN_ID>',type:dataView),filters:!(),interval:auto,query:(language:kuery,query:'<QUERY>'),sort:!(!('@timestamp',asc)))
```

**Times in URL:** **UTC** only. IST = UTC+5:30 → subtract 5h30m. Add ±2 min buffer on `from`/`to`.

### TSP saved index pattern IDs (team-owned)

| Pattern ID | ES index pattern | Use for |
|------------|------------------|---------|
| `7a188ab3-b1a9-4e8b-9d99-49bfd718cc38` | `prod-paytmybl-tsp-switchc2-*` | Switch C2 app logs |
| `3d9f1ba1-eccd-4535-8162-bb705fd0f0be` | `prod-paytmybl-tsp-switchc3-*` | Switch C3 app logs |
| `177a9fbf-4a1e-443c-b766-32fd6b91891f` | `prod-paytmybl-tsp-switchc6-*` | Switch C6 app logs |
| `f55fd150-be7a-41b9-8c35-d1e435214de7` | `prod-paytmybl-tsp-switchc2_exchange*` | Switch C2 exchange (NPCI XML) |
| `5094117f-c791-4243-9452-e5e68c1d1269` | `prod-paytmybl-tsp-switchc3_exchange*` | Switch C3 exchange |
| `005681d7-3c93-4a24-a715-16a4a7ec2582` | `prod-paytmybl-tsp-switchc6_exchange-*` | Switch C6 exchange |
| `c460a9ee-b484-44f8-aafa-a7d8fedd318a` | `prod-paytmybl-tsp-switchc2_access*` | Switch C2 access logs |
| `16685135-6e4d-4551-a67c-d699dfd9091e` | `prod-paytmybl-tsp-switchc3_access*` | Switch C3 access logs |
| `bfeec9a5-6f19-48fa-91db-4f5ef07ab0fb` | `prod-paytmybl-tsp-switchc6_access-*` | Switch C6 access logs |
| `9b7107a2-09e0-4e28-855a-59601f472713` | `prod-paytmybl-tsp-stream-recon-c1-*` | Stream recon — all clusters (C1/C2/C3/C6; `c1` in name is misnomer) |

### TPAP saved index pattern IDs (team-owned, tpapprod-logging-elk.paytm.com)

| Pattern ID | ES index pattern | Use for |
|------------|------------------|---------|
| `d23c8210-a257-11ef-88ef-c15409ce53af` | `prod-tpap-transactional-switch-*,prod-tpap-transactional-switch_exchange*` | Switch app + exchange (combined — txn debugging) |
| `14ecedc0-9169-11ef-9225-716904b7d564` | `prod-tpap-transactional-switch_exchange-*` | Switch exchange only (NPCI XML) |
| `a5968f10-75db-11ef-8647-15d675bf30ca` | `prod-tpap-transactional-switch_access-*` | Switch access logs |
| `fd95be30-7a7b-11ef-8647-15d675bf30ca` | `preprod-tpap-transactional-switch-*` | Switch preprod |
| `1a7ce8d0-e124-11ee-94f6-518759b58d7c` | `prod-tpap-transactional-bff-*` | Transactional BFF |
| `e579f7f0-025b-11ef-bbe4-f92c6625cf56` | `preprod-tpap-transactional-bff-*` | BFF preprod |
| `44802fe0-5115-11f0-a332-fb3c3561c0c0` | `prod-tpap-transactional-bff_access-*` | BFF access logs |
| `ac875dc0-11b5-11ef-bbe4-f92c6625cf56` | `prod-tpap-consumers-set1-switch-*` | Kafka consumers set1 |
| `f9940700-34a9-11ef-b5f6-af31bddbb815` | `prod-tpap_gwts_mindgate-hdfc-*` | GWTS Mindgate HDFC |
| `133f3990-34aa-11ef-b5f6-af31bddbb815` | `prod-tpap_gwts_mindgate-sbi-*` | GWTS Mindgate SBI |
| `aa90b5a0-8a4d-11ef-9225-716904b7d564` | `prod-tpap-gwts-ocil-switch-yes-*` | GWTS OCIL Yes Bank |
| `7fe522a0-1d10-11ef-bbe4-f92c6625cf56` | `prod-tpap_gwts_juspay-axis-*` | GWTS Juspay Axis |

**Pattern selection:** After DB/ELK shows which TSP cluster (C2/C3/C6) holds the txn, use that cluster’s pattern ID in links. Never use raw ES index strings in Kibana URLs.

**Short URL:** After opening a link, user can use **Share → Short URL** in Kibana for a compact internal link.

## Query safety

- Always set a time range — no unbounded queries.
- Cap result size (e.g. `size: 50`, max ~500 as appropriate).
- Inspect index mapping before assuming field names.

## KQL / DSL examples

Use KQL or Lucene as supported by the index. Generic patterns (adapt field names to mapping):

**Errors in a service**

```
service.name: "payment-service" AND log.level: "ERROR"
```

**Trace ID**

```
trace.id: "abc123" OR request_id: "abc123"
```

**DSL sketch — recent errors, capped**

```json
{
  "query": {
    "bool": {
      "must": [
        { "term": { "log.level": "ERROR" } },
        { "range": { "@timestamp": { "gte": "now-1h" } } }
      ]
    }
  },
  "size": 50,
  "sort": [{ "@timestamp": { "order": "asc" } }]
}
```

For txn timelines, prefer **ascending** `@timestamp` sort.
