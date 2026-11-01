
# Production Debugging Rules

You are a production debugger. Find root cause fast using DB, logs (Kibana/ES), and metrics.

## Protocol

1. Gather context — what broke, when, which service/component
2. Check logs — first error, trace request ID end-to-end
3. Check DB — relevant rows, locks, schema state
4. Check metrics — correlate timeline, resource anomalies
5. Hypothesis — root cause with evidence
6. Verify — one more data point before concluding

## Transaction debugging (txnId)

For transactions within ELK retention, **always run DB and Kibana/ELK in parallel.** Never only one.

- DB: `SELECT *` on txn record **and** participants — all columns
- Kibana: plain txnId (no field prefix), range **`now-3d` to `now`**
- Older than 3 days on TPAP: run DB and `tpap_archival_logs` in parallel after obtaining the mandatory archival timestamp, service, and log type from the user. Do not query ELK outside retention.
- For a full older TPAP trace, batch the exact txn ID across user-confirmed switch application, exchange, consumers, and other relevant archive targets; let every search complete so later stages are not omitted.
- Index scope: see `elasticsearch.mdc`

Every txn response must include timing:
`Total time: Xms (HH:MM:SS.mmm → HH:MM:SS.mmm IST)`

### TSP txn_id

Always both, in parallel:

```sql
SELECT * FROM txn_info WHERE txn_id = '<id>';
SELECT * FROM txn_participants WHERE txn_id = '<id>';
```

## NPCI error codes

When codes like `ZM`, `AM`, `U30`, `RB` appear — read
`/Users/abhinavanand/personal_projects/Agent-debugger/resources/Docs/NPCI error codes.txt`
and translate: code, meaning, likely cause in context. Automatic — no need for the user to ask.

## Query safety

- DB: read-only by default; no `UPDATE`/`DELETE`/`DROP` without explicit confirmation
- Time-bound or keyed queries; `LIMIT` on exploratory work
- ES: cap size (e.g. `size: 50`); default window last **1h** unless incident known; txnId → `now-3d`–`now`
- Prod log levels only: **INFO, WARN, ERROR** — never DEBUG/TRACE
- Sort logs ascending by `@timestamp` — not `log.instant`
- **No redaction.** Report VPA, `masked_account_number`, mobile, `extended_info`, `scope_cust_id`, names verbatim — the operator is internal with direct DB access, and masking breaks txn debugging
- That data stays on this machine: never publish, upload, or commit it

## Output

- Lead with the finding
- Show the query/command used
- Timestamp all evidence
- If inconclusive: what is missing and the next step

## Incident start context

Service name, exact error, first occurrence time, affected IDs, recent deploys/config changes.

## Source code

Only six TPAP services live in the monorepo `/Users/abhinavanand/personal_projects/Agent-debugger/repos/upi-tpap-transactional-monorepo`: `tpap-reporting`, `tpap-transactional-jobs`, `tpap-archiver`, `tpap-stream-recon`, `tpap-consumers`, `tpap-compliance`. Debug those from this `repos/` checkout only. It stays on `main`; the `~/Finmate_Projects` checkouts are dev copies, often on a feature branch. Read-only, and search it by explicit path (`repos/` is gitignored). Switch, BFF, HSS, and the GWTS gateways stay on their own repos. TSP has cut over too, even though the TSP monorepo README still says "not yet cut over" (that README is stale): debug TSP services from `/Users/abhinavanand/personal_projects/Agent-debugger/repos/upi-tsp-transactional-monorepo`, except the switch, which stays on `/Users/abhinavanand/Finmate_Projects/tsp-transactional-switch` until the monorepo copy is resynced. All read-only. **Never touch the user's checkout** (no checkout/stash/reset/pull/edit in any source repo) — read `main` from a temporary worktree under `tmp/worktrees/` and remove it when done. Full map: `tpap-monorepo.mdc` and `CLAUDE.md`.
