
# Database Debugging Rules

## Rows vs the database itself — two different tools

| You want | Use |
|---|---|
| **Table ROWS** — txn records, participants, config | `*_redash` / `tpap_trino` (SQL) — this file |
| **The DATABASE ITSELF** — is MySQL healthy, slow, saturated, locking, lagging; DB-host CPU/mem/disk | **`tpap_percona_cursor` / `tsp_percona_cursor`** — see the `percona` rule |

When an investigation shows slow queries, connection-pool exhaustion, lock waits or
timeouts, go to the **Percona MCP** — the engine-level cause is invisible in row data, in ELK,
and in the application Prometheus.

## Safety

- Read-only by default. Never `UPDATE`/`DELETE`/`DROP` without explicit user confirmation.
- Always `WHERE` by time range or primary key — no unbounded scans.
- Use `LIMIT` on exploratory/list queries (e.g. 100).

## Redash `run_sql` — 20s timeout, always

`run_sql` on `tpap_redash` / `tsp_redash` takes a `timeout_sec` argument. **It defaults to 20
and should stay there.** A Redash query that has not returned in 20s is almost always an
unbounded scan, and waiting it out stalls the debugging session for nothing.

**Not found in 20s means not found in 5 minutes.** If a lookup has not returned in 20s, a
longer wait will not change that. Do not retry it unchanged and do not just raise
`timeout_sec`. Do one of these instead:

- **Use an index.** Rewrite on the primary key, `txn_id`, or a tight `created_on` /
  `system_timestamp` range. Run `EXPLAIN` first: a `type: ALL` or `key: NULL` plan is a full
  scan and will time out again.
- **Use another tool.** ELK for recent logs (`tpap_archival_logs` for older TPAP logs),
  Grafana/Prometheus for counts and rates, PMM (`*_percona_cursor`) for DB health.
- **Check the age.** `txn_info` and `txn_participants` keep only ~7 days on **both TPAP and
  TSP** (see *Retention* below). An older txn is purged, not slow.

- On timeout the tool returns `{"timed_out": true, "timeout_sec": 20, "hint": ...}` — a normal
  result, not a crash.
- Raise `timeout_sec` only for a query already known to be heavy (multi-hour `COUNT(*)`, wide
  `GROUP BY`), and say why you raised it. Cap 120; values outside 1–120 are clamped.
- **TSP: the budget is per shard.** An all-shard `run_sql` (empty `db_name`) hits
  C1/C2/C3/C6 sequentially — worst case 4 x `timeout_sec`. Pass `db_name` once the cluster is
  known.
- Client-side only: **the query keeps running on Redash**, nothing is cancelled. Re-firing the
  same heavy query just piles load on prod.

## Txn investigation

For txn debugging by `txn_id`, use **`SELECT *`** on the txn table **and** participants — all columns.

TSP — always together:

```sql
SELECT * FROM txn_info WHERE txn_id = '<id>';
SELECT * FROM txn_participants WHERE txn_id = '<id>';
```

## Retention — 7 days, TPAP and TSP

`txn_info` and `txn_participants` keep only the **last ~7 days** on both systems. Older rows
are purged. No rows for an older txn means it was purged, not that it never existed. Don't
scan the table looking for it; go to logs (ELK within 3 days, `tpap_archival_logs` for older
TPAP) or another source.

TPAP `switchv2.txn_info` also keeps a thin tail of unpurged 2024 rows, so `MIN(created_on)`
misleadingly reports 2024.

### TSP purge mechanics

`txn_info` and `txn_participants` keep **~7 days** on every TSP shard. Older data is purged by:

- **`tsp-archiver`** (`TxnInfoArchiveTask`) — deletes `txn_info` rows past the cutoff by `updated_on`,
  plus their participants. It **skips DEEMED/PENDING PAY txns**, which stay in `txn_info`.
- **Partition drop on `txn_participants`** — daily partitions (`pYYMMDD`, `system_timestamp`),
  whole day, **regardless of status**.

So:
- A txn older than 7 days with no rows was purged, not missing.
- An old DEEMED/PENDING PAY txn can have **zero participant rows**. That is expected.
- When recon settles such a txn to SUCCESS, `each_txn_must_have_payer_participant` and
  `each_txn_must_have_payee_participant` fire together, raising `Txn table Recon Discrepancy`.
  Verified on Zenduty #381614 (25 Sep 2026, C2).
- Bound `txn_participants` queries by `system_timestamp` so partitions get pruned. Unbounded
  `txn_id` anti-joins time out.

## Schema

- Confirm table/column names before querying
- Do not assume shared schema between tpap and tsp
- Schemas: `src/tpap/db_schema/schema.md`, `src/tsp/db_schema/schema.md`
