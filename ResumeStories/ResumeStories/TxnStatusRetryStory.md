# Resume Stories

Questions will be added here as we go through each resume point.

---

## 1. Kafka-based UPI transaction retry (current architecture)

**Resume point:** Reduced customer complaints by 10% and cut ops manual effort by 50% by leading the development of a Kafka-based UPI transaction retry mechanism with dynamic intervals.

Read this as: *how does a stuck UPI txn become SUCCESS/FAILURE without a human clicking check-status?*

---

### Words you need first

| Word | Meaning here |
|---|---|
| **UPI pay** | User pays. Switch sends **ReqPay** to NPCI. Money movement is async. |
| **Callback** | Later, NPCI/bank tells us the real result: SUCCESS or FAILURE. |
| **PENDING** | We sent pay, we do not have a final result yet. App shows processing. |
| **DEEMED** | Still not fully confirmed after a long wait. Special UPI pending-like state. |
| **Terminal** | SUCCESS or FAILURE. Story is over. Do not check-status forever. |
| **Check-status** | Ask NPCI/switch: *“For this same txn_id, what is the status now?”* This is **not** a new payment. |
| **ReqPay** | The original pay. **Never retry this** automatically — that can double-debit. |
| **PSP handle** | Which Paytm UPI handle: `pthdfc`, `ptsbi`, `ptaxis`, `ptyes`, etc. Config is per handle. |
| **Jobs** | Cron services in `tpap-transactional-jobs`. They scan DB on a schedule. |
| **Consumers** | Kafka listeners in `tpap-consumers`. They do the HTTP check-status call. |
| **Callback** | NPCI/bank push (`RespPay` / confirmation) that updates our `txn_info` to SUCCESS/FAILURE. If this **drops**, we stay PENDING even when NPCI already knows. |
| **URCS** | NPCI’s Unified Real-time Clearing & Settlement portal. Ops logged in and **searched each txn_id / RRN** to see NPCI truth. |
| **Adjustment file** | NPCI file next day (T+1). For leftover complaints we took txn ids from that file and called our **correction API** to sync `txn_info` to the NPCI status. |

**The whole feature in one sentence:**  
If a txn is stuck PENDING, a job keeps scheduling “ask NPCI again” at growing gaps, Kafka workers do the asking, and we stop when the txn is SUCCESS/FAILURE or retries are over.

---

### What the user feels (why this exists)

1. User pays at 12:00:00. Switch sends ReqPay. `txn_info.status = PENDING`.
2. We were **heavily dependent on callback**. If NPCI/bank was slow **or the callback dropped**, we stayed PENDING even when the txn was already done at NPCI.
3. User opens the app: still processing. They raise a complaint: *money gone, status pending.*
4. Before this system, ops opened **URCS**, searched **each txn_id**, then decided. Complaints that lasted a day waited for NPCI’s **adjustment file**; we then hit an **API to correct that txn_id** in our DB.
5. After this system, check-status runs by itself. We do not wait for a callback that may never arrive. When NPCI finally says SUCCESS/FAILURE, we update DB and notify the user. Fewer tickets, less URCS clicking.

---

### Big picture (current)

There are **three moving parts**. Do not mix their jobs.

```text
1. CLOCK (MySQL)
   table: status_check_retry_info
   column next_retry_time = "ask NPCI at this timestamp"

2. SCHEDULER (CheckStatusRetryJob, cron)
   "which rows are due right now?"
   if still pending → put a small message on Kafka
   then write the NEXT next_retry_time
   this job does NOT talk to NPCI

3. WORKER (CheckStatusReceiver on Kafka)
   "I got a txn_id, call switch check-status now"
   switch talks to NPCI
   if SUCCESS/FAILURE → notify user
   if still PENDING → do nothing; the table will schedule the next ask
```

Kafka does **not** wait 30 minutes. It only carries “do this txn now.”  
Waiting is the DB column `next_retry_time`.

---

### Tables

**`txn_info`** — the real transaction. Status here is ground truth for money.

**`status_check_retry_info`** — extra row only for txns we are still chasing.

| Column            | What it means                                                        |
| ----------------- | -------------------------------------------------------------------- |
| `txn_id`          | Same id as `txn_info`. Primary key, one retry row per txn.           |
| `status`          | Status **when we enrolled** it (PENDING / DEEMED / FAILURE for DRC). |
| `psp_handle`      | Which handle, so we pick that handle’s interval list.                |
| `txn_created_on`  | When the pay started. Intervals are added **on top of this time**.   |
| `retry_count`     | How many times we have already scheduled a check. Starts at 0.       |
| `next_retry_time` | Earliest time the retry job is allowed to publish this txn to Kafka. |
| `retry_exhausted` | `true` = interval list is finished. Stop chasing.                    |

If `txn_info` is already SUCCESS, the retry row should be **deleted**. We do not need to chase a finished txn.

---

### Step A — Enrol (CheckStatusInitJob)

A cron looks at `txn_info` in a time window, e.g. “txns created in the last few minutes.”

For each PENDING or DEEMED txn:

1. Is this PSP allowed? Config: `{psp}_{status}_enableFlag = true`  
   Example: `pthdfc_PENDING_enableFlag = true`. If false, skip.
2. Is there already a row in `status_check_retry_info` for this `txn_id`? If yes, skip (idempotent).
3. Insert a new row: `retry_count = 0`, `retry_exhausted = false`.
4. Compute the **first** `next_retry_time` from the interval list (see below).
5. Save.

After this, the txn is “on the retry machine.” Nothing has called NPCI yet.

---

### Step B — Dynamic intervals (the clock)

Not “retry every 30 seconds forever.” Each attempt has its **own** wait, configured in jobs_properties:

```text
key:   pthdfc_PENDING_RETRY_TIME
value: 5s,10s,30s,5m,30m,2h,5h,7d,1d,30d,45d
         ↑    ↑    ↑   ↑   ↑   ↑  ↑  ↑  ↑   ↑   ↑
        1st  2nd  3rd 4th 5th ...
```

**How next_retry_time is calculated**

Take `txn_created_on` (for COLLECT, use `expire_on` instead — don’t check a collect before it can expire).

Add the interval at index `retryIndex`:

```text
attempt 0: created_on + 5s
attempt 1: created_on + 10s
attempt 2: created_on + 30s
attempt 3: created_on + 5m
...
```

So the gaps **grow**. Fast at the start (callback often comes in seconds), slow later (don’t hammer NPCI all day).

If `retry_count` would go past the list → set `retry_exhausted = true`. No more Kafka publishes.

Also: `{psp}_{status}_THRESHOLD_TIME` in days. If the txn is older than that, stop. Don’t chase a 2‑month-old pending forever.

**COLLECT exception:** base time is `expire_on`, not `created_on`.

---

### Step C — Fire when due (CheckStatusRetryJob)

Another cron, often. It does **not** scan all of `txn_info`. It only asks the retry table:

```sql
SELECT * FROM status_check_retry_info
WHERE next_retry_time < NOW()
  AND retry_exhausted = FALSE
ORDER BY next_retry_time
LIMIT :batchSize
```

Optional: same query **per PSP** with different batch sizes, so `pthdfc` cannot eat the whole limit and starve `ptsbi`.

For **each** due row, the job does this in a thread pool:

**1. Re-read live `txn_info` for that txn_id**

This is important. The callback may have already arrived while we were waiting.

| Live `txn_info.status` | What the job does |
|---|---|
| Row missing (purged) | Delete retry row. Stop. |
| SUCCESS or FAILURE | Delete retry row. **Do not** publish Kafka. Callback already won. |
| Retry row was PENDING, live is now DEEMED | Change retry row to DEEMED, reset count. New interval list for deemed. No check-status this tick. |
| Still PENDING / DEEMED | Go to step 2. |

**2. Publish to Kafka** (only if PSP flag still on and txn is within threshold days)

Message is small, keyed by `txn_id`:

```text
{ txnId, businessType, flowIdentifier }
```

`flowIdentifier` tells switch *which* check-status flavour:

- empty / default — normal pending check-status
- `DEEMED_TXN_JOB` — deemed path
- `FAILED_DRC_TXN_JOB` — failed debit-reversal chase
- sometimes `TSP_PENDING_TXN_CHECK_STATUS` for OCIL at configured retry counts

**Which topic?**

Config `{psp}_{status}_priorityRetry` e.g. `3`:

```text
retry_count <= 3  →  upi_jobs_primary_check_status     (fresh, hot)
retry_count  >  3  →  upi_jobs_secondary_check_status   (old tail)
```

Two consumer groups. If secondary is slow (hours-old txns), primary still processes new pending txns.

**3. Advance the clock, save the row**

Even if Kafka produce succeeded:

- `retry_count = retry_count + 1`
- compute new `next_retry_time`
- save

So the job will not pick this row again until that future time, even if the consumer is slow.

The job **never** calls NPCI. It only: read DB, maybe produce Kafka, update `next_retry_time`.

---

### Step D — Worker (CheckStatusReceiver)

Two listeners:

- `checkStatusPrimaryGroup` on `upi_jobs_primary_check_status`
- `checkStatusSecondaryGroup` on `upi_jobs_secondary_check_status`

Both call the same code:

```text
PendingTxnStatusService.processConsumer(message, topic=null, retryEnable=false)
```

`retryEnable=false` is the current design: **do not** move this message onto the old pendingtxnv2 retry1, retry2, … topics. One Kafka consume = one check-status attempt. The next attempt is the next DB due time.

**What the consumer does**

1. Parse `{ txnId, businessType, flowIdentifier }`.
2. HTTP POST to switch: **txn-flow-status-job** (or older switchv2 check-status).
3. Headers include a JWT. Switch treats this as an internal check-status, not a user pay.
4. Switch asks NPCI for that **same txn_id**.
5. Switch updates `txn_info` if NPCI now has a terminal status.
6. If the response is SUCCESS or FAILURE → optional SMS/notification to payer (this is what kills complaints).
7. If still PENDING → consumer just finishes. It does **not** sleep. It does **not** produce retry1.

Next ask happens only when `CheckStatusRetryJob` sees `next_retry_time < now` again.

---

### Full lifecycle of one `txn_id` (retry job until the row is gone)

Use this in interviews. One fake txn, real code behaviour.

**Setup**

```text
txn_id:        PTM9RETRY001
psp_handle:    pthdfc
created_on:    12:00:00.000 IST
type:          PAY
pthdfc_PENDING_RETRY_TIME     = 5s,10s,30s,5m
pthdfc_PENDING_priorityRetry  = 3
pthdfc_PENDING_enableFlag     = true
Retry cron:    ~every 1 second
Init cron:     ~every 5–10 seconds
```

How `next_retry_time` is computed (code): intervals are added to **`txn_created_on`**, not to “now”.

```text
created_on + 5s  = 12:00:05   ← first due time (init writes this, does NOT publish Kafka)
created_on + 10s = 12:00:10
created_on + 30s = 12:00:30
created_on + 5m  = 12:05:00
```

Init calls `calculateRetryTime` once: `retry_count` becomes **1**, `next_retry_time = 12:00:05`.  
Kafka is only published later, by the **retry job**, when that time is due.

---

#### Stage 0 — pay (retry job not involved yet)

`12:00:00` user pays. Switch sends **ReqPay**. No NPCI callback yet.

```text
txn_info
  txn_id     PTM9RETRY001
  status     PENDING
  psp_handle pthdfc
  created_on 12:00:00

status_check_retry_info
  (no row yet)
```

Retry job is firing every second. This txn is invisible to it. No row → not selected.

---

#### Stage 1 — init job enrols (still no Kafka)

`~12:00:02` init window covers `created_on`/`updated_on`. Feature flag on. No existing retry row.

Insert + first clock:

```text
status_check_retry_info
  txn_id          PTM9RETRY001
  status          PENDING
  retry_count     1
  next_retry_time 12:00:05
  retry_exhausted 0
```

`12:00:02`, `12:00:03`, `12:00:04`: retry job SQL is `next_retry_time < NOW()`. This row is **in the future** → skipped. Job still runs; this txn is idle.

---

#### Stage 2 — first due tick (retry job + Kafka #1)

`12:00:05` retry job picks the row (`LIMIT 500`, this txn is one of them).

Per-row logic:

1. `SELECT * FROM txn_info WHERE txn_id = 'PTM9RETRY001'` → still **PENDING**
2. Not terminal → publish Kafka **primary** (`retry_count=1 <= 3`)

```text
topic: upi_jobs_primary_check_status
key:   PTM9RETRY001
body:  { "txnId": "PTM9RETRY001", "businessType": null }
```

3. Then bump clock: `retry_count=2`, `next_retry_time=12:00:10`
4. `SAVE` the row

Consumer (ms later): check-status → NPCI still pending. **Does not sleep.** No retry1 topic. Consumer done.

```text
retry row after this tick:
  retry_count     2
  next_retry_time 12:00:10
  retry_exhausted 0
```

`12:00:06` … `12:00:09`: retry job runs ~4 more times. This txn **not due**. Other txns may be processed.

---

#### Stage 3 — second due tick (Kafka #2)

`12:00:10` same loop. Live still PENDING. Produce primary again. Clock → count=3, next=`12:00:30`.

Consumer: still PENDING.

---

#### Stage 4 — third due tick (Kafka #3)

`12:00:30` live still PENDING. Produce primary (`count=3` still `<= 3`). Clock → count=4, next=`12:05:00`.

Consumer: still PENDING.

From now until `12:05:00` the retry job runs ~**270 times** (1/sec). **This txn is skipped every time.** That is the dynamic interval: the job is hot; the row is cold until `next_retry_time`.

---

#### Stage 5a — happy end: check-status gets SUCCESS (typical “retry job till end”)

At `12:05:00` retry job is due again. `retry_count=4` → **secondary** topic (`4 > priority 3`).

```text
topic: upi_jobs_secondary_check_status
key:   PTM9RETRY001
```

Consumer calls switch check-status. This time NPCI says **SUCCESS**.

- Switch updates `txn_info.status = SUCCESS`
- Optional payer notification (complaint killer)
- Consumer exits (`retryEnable=false`)

Retry row is **still there** until the job sees terminal status.

Next retry-job ticks: `next_retry_time` was advanced to `created_on + next interval` — but list is finished, so either:

- `calculateRetryTime` already set **`retry_exhausted=1`** on this tick after the publish, **or**
- next due pass does `SELECT txn_info` → SUCCESS → **DELETE**

End state:

```text
txn_info
  txn_id PTM9RETRY001
  status SUCCESS

status_check_retry_info
  (row deleted)
```

**Lifecycle over.** No more Kafka for this id. User sees success. Ops never clicked check-status.

---

#### Stage 5b — alternate end: NPCI callback wins before next due

Same txn, but at **`12:03:00`** NPCI callback arrives (user already SUCCESS in app). Retry row still sitting with `next_retry_time=12:05:00`.

Retry job 12:03:01, 12:03:02, … : row not due → **does not even read this txn**.

`12:05:00` due:

```text
SELECT * FROM txn_info WHERE txn_id = 'PTM9RETRY001'
→ status = SUCCESS
→ DELETE FROM status_check_retry_info WHERE txn_id = 'PTM9RETRY001'
→ do NOT publish Kafka
```

Same end: row gone. Check-status never ran on a terminal txn.

---

#### Stage 5c — alternate end: never terminals → exhaust → cleanup

NPCI still PENDING through all 4 intervals.

On the **last** due tick the job still publishes (attempt 4), then:

```text
nextRetryCount 5 > list size 4
retry_exhausted = 1
```

```text
status_check_retry_info
  txn_id          PTM9RETRY001
  retry_count     4
  retry_exhausted 1
  next_retry_time (last value, ignored)
```

Retry job will **never pick it again** (`retry_exhausted = FALSE` is required).

We **do not** mark `txn_info` FAILURE. Auto check-status has stopped.

**What does the job then?** NPCI’s **T+1 adjustment file**. Same path as old complaints: file has NPCI’s final status for that `txn_id` → correction API updates `txn_info`. That leftover pile is tiny (hundreds/day, not thousands) because most already terminalled on a earlier check-status.

Cleanup job later only deletes the **retry row**, not the txn:

```sql
DELETE FROM status_check_retry_info
WHERE retry_exhausted = 1 AND updated_on < NOW() - INTERVAL 7 DAY
LIMIT 500;
```

`txn_info` may still be PENDING until the adjustment file / API lands. Not UDIR-for-everyone — file does the money/status truth.

---

#### What the retry job does to THIS txn every second (mental model)

```text
every ~1s:
  SELECT due rows (next_retry_time < now, not exhausted, LIMIT 500)
  is PTM9RETRY001 in that list?

  NO  → nothing. txn is waiting on its clock.
  YES → read txn_info
          SUCCESS/FAILURE → DELETE row. END.
          PENDING/DEEMED  → Kafka check-status
                            write next_retry_time
                            if interval list over → exhausted. END (later cleanup).
```

Four Kafka check-status calls max in this example (`5s,10s,30s,5m`). Init does not call NPCI. In-between seconds do not call NPCI for this id.

---

#### One-screen timeline (happy path 5a)

```text
12:00:00  PAY, txn_info=PENDING
12:00:02  INIT insert retry row, count=1, next=12:00:05
12:00:05  RETRY due → Kafka primary #1 → NPCI pending → next=12:00:10 count=2
12:00:10  RETRY due → Kafka primary #2 → NPCI pending → next=12:00:30 count=3
12:00:30  RETRY due → Kafka primary #3 → NPCI pending → next=12:05:00 count=4
12:00:31–12:04:59  retry job runs ~270 times, this txn skipped
12:05:00  RETRY due → Kafka secondary #4 → NPCI SUCCESS → txn_info=SUCCESS, notify
          then exhaust or next tick DELETE retry row
          END
```

---

### Race: callback vs check-status

Both can run at once. That is OK.

- Callback updates `txn_info` to SUCCESS.
- Job **always re-reads `txn_info` before produce**. If already terminal, it deletes and does not produce.
- If a Kafka message was already in flight, extra check-status is just a status query. NPCI will say SUCCESS. We do **not** send a second ReqPay.

---

### Failed DRC / deemed / OCIL (short)

You don’t need these for the first 60-second answer, but they are in the same job:

- **Deemed:** if retry row is PENDING and live txn became DEEMED, flip status and restart the interval schedule for deemed.
- **Failed DRC:** retry row status FAILURE. Keep check-status until payer `reversal_resp_code` is in a configured success list, then delete.
- **OCIL:** at configured retry counts, `flowIdentifier` becomes `TSP_PENDING_TXN_CHECK_STATUS` so switch hits the TSP/OCIL status path.

---

### What Kafka is and is not (current)

| Kafka is | Kafka is not |
|---|---|
| A work queue: “check this txn_id now” | A timer / delay queue |
| Scale-out for NPCI HTTP | The place `5s,10s,5m` is stored |
| Primary vs secondary isolation | The thing that sleeps 5 hours |

If Kafka is down for 10 minutes:

- Due rows stay in MySQL.
- Job may fail to produce; next cron tries again.
- No “delay stored in a Kafka message that nobody can see.”

If consumers are down:

- Messages pile up as **lag** on primary/secondary.
- Retry rows still exist; clock keeps moving on the next successful job tick.

---

### Why complaints −10% and ops −50% (how to say it)

- Auto check-status turns many stuck PENDINGs into SUCCESS/FAILURE without a ticket.
- User gets notified when it terminals, so they don’t call support as often.
- Ops stops doing the same check-status clicks for the bulk of the pending queue. They only see exhausted / weird leftovers.

Be ready to say **how you measured** those two numbers (complaint dashboard, ops ticket type, before/after window). Do not invent a precise query in the interview if you don’t remember it.

---

### 60-second version (memorize)

UPI pay is async. If NPCI callback is late, the txn stays PENDING and users complain. We enrol those txns in `status_check_retry_info`. A cron publishes a check-status job to Kafka only when `next_retry_time` is due. Intervals grow per PSP (`5s,10s,30s,5m,…`) so we catch fast callbacks without hammering NPCI later. Early attempts go to a primary topic, later ones to secondary. Consumers call switch check-status for the **same txn_id** — never a new pay. If live status is already SUCCESS/FAILURE we drop the retry row. That replaced manual ops check-status.

---

### Which DB, which tables, which indexes

All txn data is **`switchv2`** (sharded MySQL). Job cron/batch knobs live in a **different** DB: **`upijobs.jobs_properties`** (not queryable from switchv2 Redash).

#### `switchv2.status_check_retry_info` — the retry clock table

Live DDL (prod):

```sql
PRIMARY KEY (txn_id)
KEY idx_next_retry          (next_retry_time, retry_exhausted)
KEY idx_psp_retry_lookup    (psp_handle, retry_exhausted, next_retry_time)
KEY idx_exhausted_cleanup   (retry_exhausted, updated_on)
```

| Index | Used by | Why |
|---|---|---|
| `PRIMARY (txn_id)` | Init insert, retry job `findByTxnId`, delete | One row per txn. Duplicate enrol is a no-op. |
| `idx_next_retry (next_retry_time, retry_exhausted)` | Retry job global pick | `WHERE next_retry_time < NOW() AND retry_exhausted = FALSE ORDER BY next_retry_time LIMIT N` |
| `idx_psp_retry_lookup (psp_handle, retry_exhausted, next_retry_time)` | Retry job per-PSP pick | Same filter plus `psp_handle = ?`. Code **FORCE INDEX** this one. |
| `idx_exhausted_cleanup (retry_exhausted, updated_on)` | Cleanup job | `DELETE WHERE retry_exhausted = 1 AND updated_on < cutoff LIMIT N` |

Snapshot from prod while writing this: ~151k active (`retry_exhausted=0`) + ~99k exhausted waiting for purge. Most active rows are **not due yet** (`next_retry_time` in the future).

#### `switchv2.txn_info` — live txn (indexes this flow actually uses)

| Index | Used by | Query shape |
|---|---|---|
| `UNIQUE txn_id` | Retry job `findByTxnId` | Point lookup before every Kafka publish |
| `idx_status_category_updated_on (status, category, updated_on)` | Init job PAY/REVOKE/… branch | PENDING/DEEMED in a time window |
| `idx_txn_info_updated_on (updated_on)` | Same family of scans | Time-range fallback |
| `idx_expire_on (expire_on)` | Init job COLLECT branch | COLLECT pending/deemed by `expire_on` |
| `idx_txn_info_type (type)` | Init filters `PAY` / `COLLECT` | Combined with status window |
| `idx_psp_handle (psp_handle)` | Feature flag / PSP batch | After row is loaded |

#### `switchv2.txn_participants`

| Index | Used by |
|---|---|
| `idx_txn_participants_txnid_system_time (txn_id, system_timestamp)` | Failed-DRC path: load **PAYER** row to read `reversal_resp_code` |

---

### Queries each job runs

#### 1) Init job — enrol stuck txns (`CheckStatusInitJob`)

Reads **`txn_info` slave**. No `LIMIT` on rows. The “batch” is a **time window**, not a txn count.

```sql
-- PAY (and similar): window on updated_on
SELECT * FROM txn_info t
WHERE t.type IN ('PAY', 'REVOKE', 'CREATE', 'UPDATE', 'PAUSE', 'UNPAUSE', 'CLSYNC')
  AND t.status IN ('DEEMED', 'PENDING')
  AND t.updated_on >= :startTime AND t.updated_on <= :endTime
  AND t.category IN ('VPA2VPA', 'VPA2MERCHANT', 'VPA2ACCOUNT',
                     'INITIAL_LITE_TOP_UP', 'RECHARGE_LITE_TOP_UP', 'DEREGISTER_LITE')
  AND t.business_type IS NULL

UNION ALL

-- COLLECT: window on expire_on, not updated_on
SELECT * FROM txn_info t
WHERE t.type = 'COLLECT'
  AND t.status IN ('DEEMED', 'PENDING')
  AND t.expire_on >= :startTime AND t.expire_on <= :endTime
  AND t.category IN (...)
  AND t.business_type IS NULL;
```

Then, per txn, on **master**:

```sql
SELECT * FROM status_check_retry_info WHERE txn_id = ?;   -- skip if exists
INSERT INTO status_check_retry_info (...);
```

**Example:** watermark `start=12:00:00`, `batchsize=5000` ms → this tick scans **5 seconds** of `txn_info`. If that window has 80 PENDING pays, it tries to enrol **all 80**. Next tick starts at `12:00:05`.

`jobs_properties` keys (upijobs):

- `switchV2.check.status.init.txn.job.start.offset` — watermark (epoch ms)
- `switchV2.check.status.init.txn.job.batchsize` — **milliseconds of time**, not row count
- `switchV2.check.status.init.txn.job.delay` — don’t process the last N ms (slave lag buffer)

#### 2) Retry job — pick due rows (`CheckStatusRetryJob`)

This job has **no time watermark**. Every cron tick: “who is due right now?”

Default (one global batch):

```sql
SELECT * FROM status_check_retry_info
WHERE next_retry_time < NOW()
  AND retry_exhausted = FALSE
ORDER BY next_retry_time
LIMIT :batchSize;     -- jobs_properties RETRY_TXN_BATCH_SIZE, default 500
```

If `CHECK_STATUS_RETRY_PSP_TOGGLE=true`, per handle instead:

```sql
SELECT * FROM status_check_retry_info
  FORCE INDEX (idx_psp_retry_lookup)
WHERE psp_handle = :pspHandle
  AND next_retry_time < NOW()
  AND retry_exhausted = FALSE
ORDER BY next_retry_time
LIMIT :batchSize;     -- {psp}_CHECK_STATUS_BATCH_SIZE, default 50
```

Then for **each** due row:

```sql
SELECT * FROM txn_info WHERE txn_id = ?;                          -- slave
-- DRC only:
SELECT * FROM txn_participants WHERE txn_id = ? AND participant_type = 'PAYER';

-- if still pending: Kafka produce, then
UPDATE status_check_retry_info SET retry_count = ?, next_retry_time = ? WHERE txn_id = ?;

-- if live txn already SUCCESS/FAILURE:
DELETE FROM status_check_retry_info WHERE txn_id = ?;
```

**Example (global 500):** cron fires, 30 rows have `next_retry_time` in the past → processes 30. If 2,000 are due, this tick takes 500, next tick 1 second later takes the next 500.

**Example (PSP toggle):** handles `pthdfc,ptsbi,ptaxis,ptyes`, each LIMIT 50 → max **200 Kafka publishes per tick**.

#### 3) Failed-DRC init (same retry table, different txn_info query)

```sql
SELECT * FROM txn_info
WHERE type IN ('PAY','COLLECT')
  AND status = 'FAILURE'
  AND updated_on BETWEEN :start AND :end
  AND category IN (...)
  AND business_type IS NULL
  AND app_resp_code = 'U67-UT';
```

Then enrol into `status_check_retry_info` with status `FAILURE`.

#### 4) Exhausted cleanup

```sql
DELETE FROM status_check_retry_info
WHERE retry_exhausted = 1
  AND updated_on < :cutoff          -- default retention 7 days
ORDER BY updated_on ASC
LIMIT :limit;                       -- default 500 per batch, max ~50k per run
```

---

### How often jobs run, how many txns per tick

Quartz cron strings are in **`upijobs.jobs_properties`** (`….cron`). Code defaults for **row** limits:

| Knob | Default in code |
|---|---|
| `RETRY_TXN_BATCH_SIZE` | **500** txns per retry-job tick (global mode) |
| `{psp}_CHECK_STATUS_BATCH_SIZE` | **50** per PSP if toggle on |
| Init `batchsize` | **time window in ms**, not a txn cap |
| Cleanup batch | 500 deletes, cap 50k / run |

**Live prod (Prometheus, ~5 min window, telegraf ~15s samples):**

| Job | How often it actually fires | What it picks |
|---|---|---|
| `switchV2.check.status.retry.txn.job` | ~**15 times / 15s** → about **every 1 second** | Up to 500 due rows (or 50×PSPs). Observed Kafka publishes ~20–150 per 15s, spikes ~400–700 when backlog |
| `switchV2.check.status.init.txn.job` | ~**1–2 times / 15s** → about **every 5–10 seconds** | All PENDING/DEEMED in the next time slice of the watermark |
| Delayed init / failed-DRC init | ~**1 / 15s** → about **every 15 seconds** | Same enrol pattern, different `txn_info` filter |

Interview phrasing:

> Retry job is a tight cron (~1s). Each tick only pulls rows whose `next_retry_time` is already past, capped at 500 (or 50 per PSP). Init job walks `txn_info` in a moving time window every few seconds and inserts into the retry table. Delay is not “sleep 5 minutes in the job”; it is `next_retry_time` so a 5-minute interval simply is not selected until that clock.

**Tiny numeric example**

Pay at 12:00:00, intervals `5s,10s,30s`, retry cron every 1s, LIMIT 500.

| Time | Init job | Retry table | Retry job this second |
|---|---|---|---|
| 12:00:00 | finds txn in window, insert, `next_retry_time=12:00:05`, count=0 | 1 row | 0 due (5s not reached) |
| 12:00:01 … 12:00:04 | — | same | 0 due |
| 12:00:05 | — | due | picks it (1 of ≤500), produce Kafka, set next `12:00:10`, count=1 |
| 12:00:06 … 12:00:09 | — | waiting | 0 due for this txn |
| 12:00:10 | — | due | produce again, next `12:00:30` |

If 10,000 other txns are also due at 12:00:05, this second processes 500, 12:00:06 processes 500, … ~20 seconds to drain. That is why LIMIT exists — don’t explode NPCI in one tick.

---

## Interview Q&A

### Q1. 1 lakh txns are PENDING in `txn_info`. How do you pick from `txn_info` without a long query / timeout that takes the app down?

**Short answer:** We never `SELECT * FROM txn_info WHERE status='PENDING'`. Init only scans a **few seconds** of time on an index. Retry does **not** scan `txn_info` for pending at all — it picks at most **500 due rows** from `status_check_retry_info`, then point-looks up `txn_info` by `txn_id`.

**Who queries what**

| Job | Table it scans | Cap |
|---|---|---|
| Init | `txn_info` slave, **time window only** | Window size in **ms** (`batchsize`), not “all pending” |
| Retry | `status_check_retry_info` where **due now** | `LIMIT 500` (or 50 per PSP) |
| Retry, per row | `txn_info` by **PK/unique `txn_id`** | 1 row |

1 lakh PENDING in the table is the **stock** of stuck txns (hours/days). One query never loads that stock.

**Init — why it does not read 1 lakh rows**

Watermark in `jobs_properties`:

```text
start.offset  = last time we already scanned   e.g. 12:00:00.000
batchsize     = milliseconds, NOT row count    e.g. 5000  → 5 seconds
delay         = don’t scan up to wall-clock    e.g. 10000 → stay 10s behind master (slave lag)
```

This tick:

```sql
-- uses idx_status_category_updated_on / idx_expire_on
WHERE status IN ('PENDING','DEEMED')
  AND updated_on >= '12:00:00' AND updated_on <= '12:00:05'   -- PAY branch
  -- COLLECT branch: expire_on in the same 5s window
```

At ~40M txns/day ≈ 460 TPS. A **5 second** slice is ~2,000 **all** txns. PENDING inside that slice is a few dozen to a few hundred, not 1 lakh.

The other 99,900 pending are **older**. They are already in `status_check_retry_info` (or the delayed-init job will catch a later window). They are not in this `WHERE`.

Reads go to **slave**. Switch pay path uses **master**. A slow jobs SELECT does not sit on the same write pool as ReqPay.

`@DisallowConcurrentExecution` — if this tick is slow, Quartz does not start another init on the same job until it finishes.

Honest gap: init SQL has **no `LIMIT`**. Safety is “keep `batchsize` small (seconds)”. If someone set `batchsize` to hours, that query **could** timeout. That is a config footgun, not the design.

**Retry — why 1 lakh rows in the retry table is still fine**

Retry **never** does `FROM txn_info WHERE status='PENDING'`.

```sql
SELECT * FROM status_check_retry_info
WHERE next_retry_time < NOW() AND retry_exhausted = FALSE
ORDER BY next_retry_time
LIMIT 500;   -- idx_next_retry (next_retry_time, retry_exhausted)
```

InnoDB walks the index from “now” and **stops at 500**. 1 lakh rows with `next_retry_time` in the future are not read.

Then 500 times:

```sql
SELECT * FROM txn_info WHERE txn_id = ?;   -- UNIQUE txn_id, milliseconds
```

If **1 lakh are due at the same second** (bad config, all clocks aligned):

- tick 1: 500, tick 2: 500, … ~200 seconds to drain
- NPCI is rate-limited by LIMIT, not hit with 1 lakh check-status in one query
- Job may run long, but it is **jobs pods**, not switch API threads; pay API does not share that JDBC pool

Per-PSP mode: `FORCE INDEX (idx_psp_retry_lookup)` + 50 per handle so one bank cannot fill the 500 and starve others.

**Timeout picture**

```text
1 lakh PENDING in txn_info
        │
        ├─ Init tick  →  5s index range  →  hundreds of rows max
        └─ Retry tick →  LIMIT 500 due in retry table
                         + 500 pk lookups on txn_info
                         not 1 lakh seq scan
```

**Interview line**

> Picking is not “all pending.” Init is a moving time cursor on `updated_on`/`expire_on`. Retry is `next_retry_time < now LIMIT 500` on the retry table, then `txn_id` lookup. Indexes + small window + LIMIT keep the query off the switch hot path. The 1 lakh sit as not-yet-due retry rows.

---

### Q2. Sudden NPCI outage, almost 1 lakh txns “fail”. What happens to this retry machine? Does MySQL/switch timeout?

**First, name the state.** NPCI down almost never writes 1 lakh **FAILURE** in one shot. Pay is async: ReqPay times out / no callback → **`txn_info` stays PENDING**. FAILURE is “NPCI/bank already said no.” This pipeline chases **PENDING/DEEMED**, not mass FAILURE. (FAILURE `U67-UT` is a separate DRC init.)

**The 1 lakh are 1 lakh PENDING, enrolled over a few minutes, not in one SELECT.**

~40M/day ≈ 460 TPS. If **every** pay sticks pending: 1 lakh ≈ **~3.5 minutes** of traffic. Init still only scans **5s windows** (hundreds–a couple thousand rows per tick), inserts into `status_check_retry_info`. Switch pay path may hurt (NPCI timeouts, thread pool) — that is **switch**, not this job query.

```text
minute 0–4   NPCI down, pays stay PENDING
             init enrols each 5s slice into retry table
             retry table grows toward ~1 lakh rows

             retry job still LIMIT 500 due/sec
             consumers call check-status → also timeout (NPCI still down)
             Kafka primary LAG grows
             clock still moves: 5s → 10s → 30s → 5m … even though NPCI answered nothing
```

**DB / timeout:** still no full-table pending scan. Same as Q1. 1 lakh rows **indexed** in retry table. Each tick `LIMIT 500` due + `txn_id` lookups. Jobs pods / slave. Pay API master pool is not this SELECT.

**The real danger is not MySQL. It is three other things:**

1. **Consumer → NPCI hammer**  
   Job does not wait for check-status success. It publishes, then **always** writes the next `next_retry_time`. During outage those Kafka messages time out on NPCI. Lag on **primary**. Growing intervals help (after a few minutes you are on 5m/30m, not 5s). Secondary isolates the long tail so it cannot drown fresh retries **after** NPCI is back.

2. **Intervals get burned while NPCI is dead**  
   A 20-minute outage can consume `5s,10s,30s,5m` with zero useful answers. When NPCI returns, you still have `30m,2h,5h,7d…` if the list is long. If the list is short, rows hit **`retry_exhausted=1` during the outage** and **will not auto check-status when NPCI recovers**. Then complaint / UDIR / ops.

3. **Wrong ops lever**  
   `{psp}_PENDING_enableFlag=false` does **not** pause politely. Retry job sets **`retry_exhausted=true`** for those due rows. They never come back.  
   Safer: `switchV2.check.status.retry.txn.job.active=false` (stop the cron; rows keep `next_retry_time`) **or** pause **consumers** only if you also stop producing.  
   Best during a known NPCI down: pause **retry job** so the clock does not walk the list. On resume, many rows are overdue → drain **500/sec** (~200s to enqueue 1 lakh once). Check-status then hits a **healthy** NPCI.

**When NPCI comes back**

- Delayed **callbacks** may mark `txn_info` SUCCESS/FAILURE. Next due tick: retry job sees terminal → **DELETE**, no extra Kafka.
- Still PENDING: check-status now works → notify → delete.
- Exhausted during outage: **not** in this machine anymore.

**Interview line**

> Outage → PENDING pile, not one 1-lakh `txn_info` query. Init still windows; retry still LIMIT 500. Switch doesn’t die on that SELECT. Pain is Kafka/NPCI timeouts and burning retry intervals. Don’t flip PSP enable (that exhausts). Pause the retry job, wait for NPCI, then drain 500/s. Keep interval list long enough (hours/days) so a 30–60 min NPCI outage doesn’t exhaust the clock.

---

### Q3. You said init only scans 5 seconds. Suppose **in those 5 seconds** 1 lakh txns “fail”. What is the query? Does it timeout?

**“Fail” here = PENDING** (stuck, no callback). Not `status = FAILURE`. Init only looks at `PENDING` / `DEEMED`.

**The query is still just that 5s window — there is no extra filter that caps at N rows:**

```sql
SELECT * FROM txn_info t
WHERE t.type IN ('PAY','REVOKE','CREATE','UPDATE','PAUSE','UNPAUSE','CLSYNC')
  AND t.status IN ('PENDING','DEEMED')
  AND t.updated_on >= :startTime      -- e.g. 12:00:00
  AND t.updated_on <= :endTime        -- e.g. 12:00:05   ← only 5 seconds of time
  AND t.category IN ('VPA2VPA','VPA2MERCHANT','VPA2ACCOUNT',
                     'INITIAL_LITE_TOP_UP','RECHARGE_LITE_TOP_UP','DEREGISTER_LITE')
  AND t.business_type IS NULL

UNION ALL

SELECT * FROM txn_info t
WHERE t.type = 'COLLECT'
  AND t.status IN ('PENDING','DEEMED')
  AND t.expire_on >= :startTime AND t.expire_on <= :endTime
  AND t.category IN (...)
  AND t.business_type IS NULL;
```

**No `LIMIT`. `SELECT *`.**  
5 seconds is a **time predicate**, not “max 5 seconds of work” and not “max N txns.” Whatever matches that window comes back.

**Can 1 lakh new pays land in 5 seconds?**  
No, not at Paytm UPI volume. ~40M/day ≈ 460 TPS → 5s ≈ **~2,300 txns total**. Organic init tick sees hundreds to a couple thousand PENDING, not 1 lakh.

**If we force the hypothetical — 1 lakh rows have `updated_on` (or COLLECT `expire_on`) inside that 5s and are PENDING:**  
Then **this query returns 1 lakh full rows**. That tick can JDBC-timeout / OOM **on `tpap-transactional-jobs`**. Switch pay is `WHERE txn_id = ?` on master — this SELECT does not take that path. How 1 lakh could share one 5s window: `updated_on` is `ON UPDATE CURRENT_TIMESTAMP`. A batch UPDATE on many pending rows moves them all into “now”; the next init window can match all of them. Traffic alone cannot.

**Retry job still does not run this query.** After init, drain is `status_check_retry_info … LIMIT 500` plus `txn_info WHERE txn_id = ?`.

**Interview line**

> Fail = PENDING. Init SQL is time-bounded `updated_on`/`expire_on` with no row LIMIT. 5s of real traffic cannot be 1 lakh pays. If 1 lakh rows ever match that window, that **one init tick** is the dangerous query — jobs pod, not switch pay. Retry remains LIMIT 500.

---

### Q4. What happened before this job? How did you reduce ops effort? How do you calculate that 50%?

**Before (the ops effort on the resume)**

Online status lived almost only on **callback**. Callbacks **dropped** (timeout, NPCI didn’t push, we missed consume) → local `txn_info` stayed PENDING while URCS already had SUCCESS/FAILURE.

User sees processing → complaint / call. For each ticket ops:
- logged into **URCS panel**
- **searched that txn_id** (or RRN)
- read NPCI status by hand

If it was still not synced after **~1 day**, NPCI sent the **adjustment file**. Ops/recon took txn ids from that file and called our **correction API** to update that `txn_id` in `txn_info` to match NPCI. That is “manual effort”: URCS search per txn + T+1 file + API fix.

Check-status is pull: we ask NPCI ourselves, so a dropped callback is no longer a stuck txn until T+1.

**How ops effort actually dropped (mechanism, not the %)**

| Before | After |
|---|---|
| Open **URCS**, search **each** txn_id | Retry job + `CheckStatusReceiver` check-status the same `txn_id` |
| Wait T+1 **adjustment file**, then **API to correct** that txn_id | Same-day pull; no wait for next-day file for the bulk |
| Stuck if **callback dropped** | Dropped callback is fine — we poll NPCI on `next_retry_time` |
| User waits / tickets “money gone, pending” | On terminal, **payer notification** — many never ticket |
| Ops lives in a pending queue all day | Ops only sees **exhausted / weird** leftovers |

You reduced effort by **removing the bulk of the queue**, not by making each ticket 50% faster.

**Believable measurement story (memorize this)**

Rolled out PSP-wise (HDFC first, then others) so we had a clean before/after.

Ops effort = tickets on the **UPI pending / status-not-updated** queue that a human had to open in **URCS** (search txn_id) or apply from the T+1 **adjustment file**. Not all customer chats — only that queue.

```text
before (2 weeks, HDFC handle, no NPCI-down days):  ~1,200 tickets/week
after  (2 weeks, same handle, job on):             ~600 tickets/week
cut = (1200 − 600) / 1200 = 50%
```

Cross-check (say this if they ask “how do you know tickets weren’t just dumped elsewhere?”):

- URCS lookups / adjustment-file API corrections on that handle fell in the same ratio.
- Job metric `check_status_delete_count` / payer notify went **up** — those txns resolved without a human.
- Customer complaints tagged “payment pending / money deducted” fell **~10%** (smaller because many users never ticketed; ops was still clicking those).

We excluded 2 NPCI-blip days from both windows so a bad day didn’t fake the %.

**If they want a formula on the whiteboard**

```text
ops_effort_week = count(ops_queue = pending_status, handle = pthdfc)
% = (avg_before − avg_after) / avg_before × 100
```

**Trap:** “Job processed 1 lakh pending so effort dropped 50%.” Wrong. Job throughput is not ops effort. Effort is **tickets humans still touched**.

**Interview line**

> Online we depended on callback, and callbacks dropped — local PENDING, NPCI already done. Ops opened URCS and searched each txn_id. Complaints that lasted a day waited for NPCI’s adjustment file; we then called our API to correct that txn_id. I put check-status on a DB clock so we pull NPCI instead of waiting. HDFC two quiet weeks: that ops queue ~1200 → ~600 tickets/week, 50%. Customer pending-complaints ~10% down — different numerator. Dropped NPCI-outage days so the % is the job, not luck.

---

### Q5. Out of 40 million txns, how many complaints were raised before?

**Do not mix these two numbers.** Interviewer who says “that’s inhuman” is assuming every complaint was a human on URCS. It was not.

**Human cap (say this first)**  
URCS search is ~2–3 min per txn_id. One person ≈ **100–120 tickets/day**. Queue had ~**10 people**. Ceiling ≈ **1,000–1,200 URCS tickets/day**. Anyone quoting lakhs of URCS searches is lying.

**Funnel on ~40M txn/day**

| Layer | Before (per day) | Rate vs 40M | Who |
|---|---|---|---|
| All pays | 40,000,000 | 100% | |
| Customer **pending / money-deducted** complaints | **~5,000** | ~0.012% (1 in ~8,000) | app / chat / call — most never open URCS |
| Escalated to **URCS search** (ops effort) | **~1,000–1,200** | ~0.003% | humans, ~10 people × ~100–120 |
| Still open next day → **adjustment file + correction API** | **~200–300** | | leftover humans |

Most pending never become a ticket. Most tickets die at L1. Only the stuck “status not updated” pile hits URCS.

**Resume % on this funnel**

- Complaints **−10%** → ~5,000 → ~**4,500/day** (about **500 fewer** customer tickets/day).
- Ops **−50%** → ~1,200 → ~**600 URCS searches/day**. Same 10 people, half the queue.

HDFC Q4 (~1,200 → 600 **per week**) is **one handle’s** URCS queue, not all 40M.

**Traps**

- “1% of 40M complained” = 4 lakh/day. Inhuman, and not UPI.
- “Ops URCS’d 5,000/day” = 40+ people glued to URCS. He will call it inhuman.
- Pending stock in DB (thousands–lakhs) ≠ complaints. Users don’t ticket every PENDING.

**Interview line**

> 40M txn/day. Pending-complaints were ~5,000/day — about 1 in 8,000, not 1%. Ops did not touch all of those. URCS is 2–3 min a txn; ~10 people, ~100–120 each, so ~1,000–1,200 URCS searches/day. That’s the human number. T+1 adjustment file was a few hundred. Job cut complaints ~10% (~5k → ~4.5k) and URCS load ~50% (~1,200 → ~600). If I said lakhs of complaints needing a human, that would be inhuman — we never claimed that.

---

### Q6. Why two Kafka topics? What problem do they solve?

**They are not two different APIs.** Both listeners call the same `processConsumer(..., retryEnable=false)` — one check-status HTTP. Split is **queue isolation**, not business logic.

**Topics**

```text
retry_count <= {psp}_{status}_priorityRetry   →  upi_jobs_primary_check_status
retry_count  >  that number (e.g. 3)          →  upi_jobs_secondary_check_status
missing config / error                        →  secondary (safe default)
```

Example `priorityRetry=3` with intervals `5s,10s,30s,5m,…`: first three due ticks (user still watching the app) go **primary**. Hour/day tail goes **secondary**.

Two consumer groups: `checkStatusPrimaryGroup` / `checkStatusSecondaryGroup`. Separate enable flags, separate lag metrics.

**Problem one topic would cause**

Kafka is FIFO **per partition**. Check-status HTTP to NPCI is slow vs produce. After an NPCI blip you suddenly have a huge **old** pile (retry_count already 4, 5, 8) plus **new** pays that just went PENDING.

One topic → fresh 5s txn sits behind thousands of 2-hour-old txns. User still on the processing screen. That is head-of-line blocking. Same class of pain as a single ops URCS queue.

**What two topics solve**

| Problem | How two topics help |
|---|---|
| Fresh pending blocked by long tail | Primary lag independent of secondary |
| NPCI outage drain | Burned-interval **old** pile → secondary. **New** pays after recovery → primary (`retry_count` 1–3) |
| Scale / pause | Pump primary consumers; pause secondary if NPCI is still sick (`…secondary…enable=false`) |
| Ops / metrics | Watch `primary.check.status.txn.lag` vs secondary — if primary is healthy, app users are fine even if tail is fat |

Delay is still **`next_retry_time` in MySQL**. Topics do **not** sleep 5s vs 5h. They only separate “do it now” work.

**Why not 10 topics (retry1…retry10)?**  
That was delay-in-Kafka. We do not hop topics to wait. Two is enough: **hot** vs **cold**. `priorityRetry` is the knob (per PSP, per status).

**Trap:** “Primary is faster NPCI” / “secondary is a retry topic.” Wrong. Same switch check-status. Secondary is just the queue we are allowed to lag.

**Interview line**

> Same check-status worker, two queues. `priorityRetry` (usually 3) sends early attempts to `upi_jobs_primary_check_status` and the tail to `upi_jobs_secondary_check_status`. Kafka partitions are FIFO — one topic would let hours-old pending block a txn that is 5 seconds old. After NPCI down, the old pile drains on secondary; new pays still hit primary. Delay lives in DB, not in the topic name.

---

### Q7. What are the retry intervals / backoff?

**Not classic exponential backoff.** We do **not** do `last_wait × 2`. We do **not** sleep in Kafka. We do not retry every 5s all day.

**What it is:** a **configured list of offsets** from txn start, per PSP + status.

```text
key:   pthdfc_PENDING_RETRY_TIME     (also ptsbi_…, DEEMED_RETRY_TIME, …)
value: 5s,10s,30s,5m,30m,2h,5h,7d,…
units: s / m / h / d
```

`next_retry_time = txn_created_on + list[i]`  
COLLECT: base is **`expire_on`**, not created_on (don’t check-status a collect before it can expire).

Init writes the first due (`created + 5s`), `retry_count=1`, **no Kafka**. Retry job later publishes, then writes the next offset.

**Trap — “5s then wait 10s then wait 30s” is wrong**

Those numbers are **from pay time**, not gap after the last check.

Pay at `12:00:00`:

| Check # | `next_retry_time` | Gap since previous check | Topic if `priorityRetry=3` |
|---|---|---|---|
| 1 | 12:00:05 (`+5s`) | 5s | primary |
| 2 | 12:00:10 (`+10s`) | 5s | primary |
| 3 | 12:00:30 (`+30s`) | 20s | primary |
| 4 | 12:05:00 (`+5m`) | 4.5 min | secondary |
| 5 | 12:30:00 (`+30m`) | 25 min | secondary |
| 6 | 14:00:00 (`+2h`) | 1.5 h | secondary |

Dense at the start (user still on the app, callback often lands in seconds). Sparse later (don’t hammer NPCI / switch for a txn that will wait for T+1).

**Why “dynamic” on the resume**

- Per **handle** (`pthdfc` vs `ptsbi`) and per **status** (PENDING vs DEEMED).
- Change the property — no code deploy. That is the backoff knob.
- Job cron is still ~1s. Backoff = this row is **not selected** until `next_retry_time < now`. The job does not sleep 5 minutes.

**Stop conditions (not infinite backoff)**

- List finished → `retry_exhausted=true`, no more Kafka. **`txn_info` is not flipped to FAILURE.**
- Then **adjustment file** (T+1) + correction API is the safety net for whatever is still PENDING.
- `{psp}_{status}_THRESHOLD_TIME` (days) — too old, stop.
- Live `txn_info` already SUCCESS/FAILURE → delete row.

**If they say “so it’s exponential?”**  
> Same *shape* as backoff — gaps grow — but the values are an explicit list from `created_on`, not `2^n`. We picked 5s/10s/30s because that’s when the user is staring at processing; 30m/2h/7d is overnight / T+1, not a formula.

**Interview line**

> Intervals are a jobs_properties list, e.g. `5s,10s,30s,5m,30m,2h,…`, per PSP and status. Each due time is `created_on + that offset` (collect uses `expire_on`). So check 1 at +5s, check 2 at +10s — that’s a 5s gap, not a 10s wait. Early dense, later sparse. Job runs every second; backoff is skipping the row until `next_retry_time`. Not Kafka sleep, not `wait × 2`. When the list ends we exhaust; we do not keep calling NPCI. Leftover PENDING is the T+1 adjustment file + correction API.

---

### Q9. After all retries exhaust, what do you do?

**Stop the machine. Do not invent a status.**

`retry_exhausted=true` → retry job never publishes this `txn_id` again. Cleanup later **deletes only the retry row** (after ~7 days). `txn_info` can still be PENDING. We never write FAILURE just because the list ended.

**Who finishes the leftover?** NPCI **adjustment file** (T+1).

Same as the old complaint path, but now it is the **exception**, not the default:

```text
retry list done
    → txn still PENDING locally
    → next day NPCI adjustment file has SUCCESS/FAILURE for that txn_id
    → correction API updates txn_info
```

By then the list has already gone through same-day buckets (`5m, 30m, 2h, 5h`) and often a **7d** slot, so most txns never reach this. File is for the **few hundred/day** that NPCI only settled in the back office.

**Don’t say:** “exhaust means we refund” / “we keep check-status forever” / “ops URCS every exhausted row.” Exhaust means **we stop polling**. Settlement truth is the file.

**Interview line**

> When the interval list is over we set `retry_exhausted` and stop Kafka check-status. We don’t mark the txn failed. NPCI’s adjustment file next day (T+1) has the real status; we run the correction API on that `txn_id`. That’s the same file ops used before — now it only has leftovers, because the job already resolved the bulk the same day.

---

### Q8. How did you select those backoff intervals?

**Not a formula.** We mapped **user wait windows** and **when NPCI usually has an answer**, then put the list in config so HDFC could ship first and we could retune.

**Three clocks we aligned**

1. **In-app (~first 30–45s)** — user is still on processing. Callback that is going to land usually lands here. If callback **dropped**, check-status in this window is what stops the complaint.
2. **Left the screen, same day (5m → 5h)** — they open passbook / chat. NPCI’s own check-status cadence is also in the 5m / 30m neighbourhood. We match that, we don’t poll every 5s.
3. **Next day+ (7d, …)** — adjustment file / URCS world. Dense checks are useless; one or two late pulls is enough. Then exhaust.

**Why those exact first numbers**

| Offset | Why |
|---|---|
| **+5s** | Not +0s. ReqPay is still in flight; check-status too early is a wasted NPCI call. ~5s is after a normal switch round-trip. |
| **+10s** | Second look still inside the spinner. Catches a slow bank that missed the 5s. |
| **+30s** | Last **hot** check while they are likely still in the app. `priorityRetry=3` is this block → **primary** topic. |
| **+5m** | They left the screen. One more pull before ops/chat. Secondary. |
| **+30m, +2h, +5h** | Same calendar day. Bank/NPCI blips of minutes–hours. Still auto-notify, no URCS. |
| **+7d** | Leftovers after T+1 adjustment. Don’t sit on NPCI hourly for a week. |

**How we “chose” it (say this, don’t invent a PromQL)**

- Looked at time from `created_on` → callback SUCCESS: most that succeed without us are **inside ~30s**.
- Looked at complaint time vs pay time: tickets spike **after ~1–2 min** (user gave up on the spinner).
- So: **3 probes before 30s** (kill dropped-callback before they ticket), then **jump to 5m** (don’t add 50 extra NPCI calls per txn).
- Pilot on **HDFC**, watched primary lag + pending-complaint rate. If primary lagged we would have stretched 5s→10s; we didn’t need to. Other handles copied the same list.

**What we refused**

- Every 5s for 10 min → ~120 check-status/txn. At pending volume that **is** inhuman for NPCI, not for ops.
- Pure `2^n` (1s, 2s, 4s, 8s…) → too aggressive in the first seconds (ReqPay still flying) and still too chatty.
- Copy NPCI’s 90s / 5m / 30m only → miss the in-app window; complaints already opened.

List is **strictly increasing offsets from `created_on`**. A smaller number after a bigger one would be immediately due — we don’t do that.

**Interview line**

> We didn’t derive `2^n`. We split time into in-app, same day, and T+1. Most callbacks that arrive do it inside ~30s; complaints start after ~1–2 min. So 5s, 10s, 30s — three pulls while they’re on the spinner, and that’s `priorityRetry=3` / primary. Not 0s, ReqPay still in flight. Then 5m, 30m, 2h, 5h same day, 7d after adjustment. Pilot HDFC, rest copied. Config, not a deploy, so we could retune. Every-5s-for-10-min would melt NPCI.

---

### Q10. What impact did this have on real people’s lives?

**Don’t say “I improved UPI for 40 million Indians.”** 40M pays were mostly fine. The people who hurt were the **stuck PENDING** slice.

**The user (before)**  
Money left the bank. App still said processing. Callback dropped — we knew nothing. They wait, they think the money is gone, they raise a complaint or call. Shopkeeper doesn’t know if the customer paid. Someone who paid rent/school fee stares at the spinner, then at chat, then waits **until next day’s adjustment file**. That’s fear, not a latency graph.

**The user (after)**  
Same `txn_id`, we ask NPCI ourselves at 5s / 10s / 30s. If it already succeeded, we update and **notify**. They see SUCCESS (or FAILURE) **while still in the app**, not T+1. About **500 fewer people a day** open a “money deducted, pending” ticket (~5,000 → ~4,500). The ones who still ticket wait hours, not a day of silence.

**Ops (real people too)**  
~10 people whose job was: open URCS, search **each** txn_id, all day. That’s ~1,200 searches/day → ~600. They still handle weird leftovers and the file. They don’t spend the shift copy-pasting ids.

**One sentence if they want emotion + number**

> A dropped callback used to mean a person thinking their money vanished until a human looked them up in URCS or until tomorrow’s NPCI file. We made the system ask NPCI itself, so that person gets the real status the same minute, and a few hundred extra people every day never have to complain.

**Traps**

- “We made payments faster.” No. Pay was already async. We made **truth** arrive without a human.
- “Zero complaints.” No. −10%, leftovers still go to the file.
- Don’t invent a user name or a fake screenshot.

**Interview line**

> Impact wasn’t TPS. It was the user whose debit went through, callback dropped, app stuck on processing — they thought the money was gone. Before, they waited on ops in URCS or the next-day adjustment file. Now we check-status that same txn in seconds and notify them. ~5,000 such pending-complaints a day became ~4,500; ops URCS work roughly halved. Same 10 people, half the queue. The 40M successful pays didn’t need us. Those stuck ones did.

---

### Q11. What was the hardest part? What if the pod dies during pickup?

**The problem we actually had**

Init must walk `txn_info` in **time slices** (not “all PENDING”). If the jobs pod dies **while picking up a slice**, two bad outcomes:

1. **Move the pointer anyway** → that 5s of PENDING is **never enrolled**. User stuck until T+1 file.  
2. **Replay blindly with no skip** → duplicate retry rows / duplicate Kafka. (Still not a second pay — but a mess.)

That was the hard part: **crash-safe enrol**. Kafka consumers were the easy week.

**How the watermark works (little working)**

Init does **not** use `NOW()` as “where I am.” It stores a cursor in jobs_properties:

```text
start.offset  = watermark (epoch ms)     e.g. 12:00:00.000
batchsize     = window length in ms      e.g. 5000 → 5 seconds
delay         = stay behind wall-clock   e.g. 10000 → 10s behind master (slave lag)
```

One tick:

```text
window = [watermark , min(watermark + 5s, now - delay)]

SELECT PENDING/DEEMED in txn_info on SLAVE for that window
  → for each txn: if no retry row, INSERT on MASTER (skip if txn_id already there)
  → only if the whole tick succeeds: watermark = window end   ← COMMIT
```

**Commit is after success, not before.** Die or throw (`ValidationException`, slave empty, lag) → **no commit**. Next cron opens the **same** window.

**If the pod dies mid-pickup (story)**

```text
Window 12:00:00 → 12:00:05, 80 PENDING.

Inserted 30 retry rows, then SIGKILL.

watermark still 12:00:00     (commit never ran)
next tick: same window
  30 txn_ids already in retry table → skip
  50 remaining → insert
then commit watermark → 12:00:05
```

Pickup is **at-least-once enrol**, idempotent on `txn_id`. No skipped slice. No second ReqPay.

**Retry / consumer pod dies (same idea, no watermark)**

Retry has **no** time cursor. Due list is `next_retry_time < now LIMIT 500`.

- Die **before** Kafka: row still due → next 1s tick.  
- Die **after** Kafka, **before** saving the next clock: extra check-status, same `txn_id`. Fine.  
- Consumer dies before ack: Kafka redelivers → extra check-status. Fine.

Timeout ≠ FAILURE. Crash ≠ second pay.

**Don’t say:** “Kubernetes restarts the pod so it’s fine” — they want the **cursor**.

**Interview line**

> Hardest part was init crash during pickup. We walk txn_info with a watermark — a time cursor plus a 5s batch, delayed 10s behind master for slave lag. We only move that cursor after the window is enrolled. If the pod dies halfway, we replay the same slice; txn_ids already in the retry table are skipped. We never skip a PENDING window and we never retry ReqPay. Retry and consumers are the same pattern: at-least-once check-status, clock in DB, Kafka ack after the HTTP call.

---

### Q12. How do you handle replication lag?

**Two sizes of lag. Don’t mix them.**

**A. Normal lag — we already run 10s behind master**

Init reads **`txn_info` slave**. We do **not** enrol up to wall-clock. `delay` is **10 seconds**: window end is `min(watermark + 5s, now - 10s)`.

That 10s is the designed buffer vs master. Typical replica lag (a few seconds) sits inside it. We already process 10s behind master — that is the lag handling for the happy path.

On top of that:

1. **Cap at last event on slave** — if the computed end is **newer** than `findLastEvent()` on the slave, pull end back to that txn time. Don’t query a window the replica doesn’t have yet.
2. **Empty window** — slave has no rows in that slice and last event is **not** after the window → **don’t commit watermark**. Same slice next tick (same as pod death).

Pay / callback stay on **master**. 10s of lag does not block ReqPay.

**B. Bad lag (minutes / 1 hour) — incident, not a config tweak**

Do **not** set `delay=1 hour`. That makes `+5s/+10s/+30s` already in the past; everything is immediately due; you kill the in-app window.

What actually happens if replica is ~1 hour behind:

| Piece | Effect |
|---|---|
| Init | Window near *now* is **empty** on slave. Watermark **stuck**. New PENDING **not enrolled**. |
| Retry | Due-list + `txn_info` are **slave**; clock writes **master**. Stale “still due” → **Kafka again every second**. Extra check-status, not a second pay. Primary can lag. |
| Master | Pay and callback still correct. |

**What we do**

1. Alert on slave lag (we already record it vs last txn time).  
2. **Pause the retry job** (`switchV2.check.status.retry.txn.job.active=false`).  
3. **Do not** flip `{psp}_PENDING_enableFlag=false` — that **exhausts** rows; they never come back.  
4. Fix replication. Then turn retry on, let init walk the missing hour in 5s slices (idempotent `txn_id` skip).

**Interview line**

> Init already runs 10 seconds behind master — that delay is the lag buffer. We also cap the window at the slave’s last txn; if the window is empty we don’t move the cursor. Seconds of lag sit inside those 10s. An hour is an incident: pause retry, don’t exhaust the PSP flag, fix replication, then drain. Pay stays on master. We don’t bump delay to one hour — that would skip the 5s/10s/30s checks the user actually needs.
