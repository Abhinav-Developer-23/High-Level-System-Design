# TPAP Check Status Jobs Flow

> Verified: 2026-04-25. Jobs confirmed active via Kibana logs (last 3 days) and DB flags.
> System: tpap-transactional-jobs (Set 6 - Status)

## Architecture Context
The `tpap-transactional-jobs` service is responsible for triggering background tasks that ensure transaction eventual consistency. The "Check Status" suite of jobs identifies transactions stuck in a non-terminal state (`PENDING`, `DEEMED`) and initiates a verification flow via Kafka.

## Flow Overview (ASCII Diagram)

```
┌───────────────────────────┐
│ tpap-transactional-jobs   │
│ (Quartz Cron / Set 6)     │
└───────────┬───────────────┘
            │
            │ (1) Trigger Job (executeTrigger)
            ▼
┌───────────────────────────┐      (2) Query PENDING Txns
│  UnboundedJobHelper       │ ◄──────────────────────────►  DB[switchv2.txn_info]
└───────────┬───────────────┘                                (Slave)
            │
            │ (3) Construct Payload (TxnStatusPayload)
            ▼
┌───────────────────────────┐      (4) Produce Message
│      Kafka Producer       │ ───────────────────────────►  Topic: upi_switchv2_pendingtxnv2
└───────────────────────────┘
                                                                     │
                                                                     │
                                                                     ▼
                                                       ┌───────────────────────────┐
                                                       │      tpap-consumers       │
                                                       │ (Downstream - Implicit)   │
                                                       └───────────────────────────┘
```

## Active Jobs (Kibana Verified)

| Job Name (Enum Keyword) | Class Name | Frequency | Status |
|---|-|---|---|
| `switchV2.check.status.job` | `SwitchV2TxnStatusJob` | Periodic | **ACTIVE** |
| `switchV2.check.status.init.txn.job` | `SwitchV2CheckStatusInitJob` | Periodic | **ACTIVE** |
| `switchV2.check.status.retry.txn.job` | `SwitchV2CheckStatusRetryJob` | High | **ACTIVE** |
| `switchV2.check.status.delayed.job` | `SwitchV2TxnStatusDelayedJob` | Periodic | **ACTIVE** |
| `switchV2.complaint.check.status.job` | `SwitchV2ComplaintCheckStatusJob` | Periodic | **ACTIVE** |

## Step-by-Step Logic

### 1. Job Triggering
Jobs are scheduled via Quartz. Each job class (e.g., `SwitchV2TxnStatusJob`) is annotated with `@ConditionalOnExpression` checking for its specific enablement flag.

### 2. Activity Check
The `UnboundedJobHelper.executeTrigger` method calls `checkStatus(job.getKeyword())` which verifies if the job should run based on internal state or DB settings.

### 3. Data Fetching (Fetch Phase)
- **Normal/Init/Delayed Jobs:** Use `AbstractCheckStatusJobProcessor.findPendingTransaction`.
  - Queries `DB[txn_info]` (slave) for `status = 'PENDING'`.
  - Scopes the query between `startDate` and `endDate` (defined by the job's last run and batch size).
  - **Flag Check:** If `ENABLE_MANDATE_TXN_ONLY` is `true`, it filters for mandate transactions.
- **Retry Job:** Uses `CheckStatusRetryJobProcessor.findPendingRetries`.
  - Queries `DB[txn_retry_info]` (or similar retry table) for records whose `next_retry_time <= NOW()`.

### 4. Payload & Kafka (Production Phase)
- For each transaction found, a `TxnStatusPayload` is created containing the `txnId` and `businessType`.
- The `Sender` service pushes this payload to the Kafka topic: `upi_switchv2_pendingtxnv2`.
- The `CheckStatusRetryJobProcessor` additionally calculates the next retry time using `checkStatusUtil.calculateRetryTime` and updates `DB[txn_retry_info]` (Master).

## DB Write Points

| Step | Job | Table | Operation | Purpose |
|---|---|---|---|---|
| Commit | All | `jobs_properties` | `UPDATE` | Updates `last_processed_id` or `last_timestamp` for the job. |
| Retry Update | Retry Job | `txn_retry_info` | `UPDATE` | Updates `retry_count` and `next_retry_time`. |
| Retry Cleanup | Retry Job | `txn_retry_info` | `DELETE` | Deletes record if txn reached terminal state or retry exhausted. |

## Feature Flags (Verified)

| Flag Name | Value | Purpose |
|---|---|---|
| `switchv2.txn.status.job` | `true` | Enables the primary status check job. |
| `switchV2.check.status.init.txn.job` | `true` | Enables status check for newly initiated txns. |
| `IS_PENDING_TXN_V3_ENABLED` | `true` | Enables V3 optimized query for pending transactions. |
| `IS_TXN_STATUS_STATUS_JOB_NEW_API_ENABLED` | `true` | Uses new API for status verification downstream. |

## Monitoring (Grafana)

- **Dashboard:** [Check Status Monitoring](https://monitor.mypaytm.com/d/ba7f1bca-d465-4af6-9440-514e7e118c8e)
- **Key Metrics:**
  - `TPAPupi_jobs_metrics_service_execution_time_95_percentile`: Monitors job latency.
  - `TPAPupi_jobs_metrics_check_status_deemed_convert_count_value`: Counts txns moving to `DEEMED` status.
  - `pending.txn`: Global count of pending transactions being processed.

## Known Error Patterns
- `ProxyConnection rollback ... due to dirty commit state`: Observed in logs for `switchV2.check.status.delayed.job`. Typically indicates a read-only transaction attempting a rollback on connection close.
- `No data Found in Database`: Logged when no pending transactions exist in the current time window (Normal behavior).

## Kibana Links
- [TPAP Jobs Logs (Last 1h)](https://tpapprod-logging-elk.paytm.com/app/discover#/?_g=(filters:!(),time:(from:now-1h,to:now))&_a=(columns:!('@timestamp',log.message,log.loggerName,contextMap.job-name),dataSource:(dataViewId:prod-tpap-transactional-jobs-*,type:dataView),query:(language:kuery,query:'')))
