# TPAP Check Status Full Flow (End-to-End)

> Verified: 2026-04-25. Full multi-service flow confirmed via code trace and Kibana production traffic (now-3d).
> Systems: TPAP Jobs -> TPAP Consumers -> TPAP Switch -> OCIL Gateway -> TSP Switch -> NPCI

## Architecture Context
The check status flow is a critical recovery mechanism that ensures transactions eventually reach a terminal state (SUCCESS/FAILURE). It bridges the TPAP and TSP systems through the OCIL gateway.

## Flow Overview (ASCII Diagram)

```
┌───────────────────────────┐
│ tpap-transactional-jobs   │ (Set 6 - Status)
│ [Quartz Cron Trigger]     │
└───────────┬───────────────┘
            │ 
            │ (1) Produce: upi_jobs_pendingtxnv2
            ▼
┌───────────────────────────┐
│      tpap-consumers       │ (PendingTxnStatusReceiver)
└───────────┬───────────────┘
            │
            │ (2) POST /upi/int/txn/status-jobs
            ▼
┌───────────────────────────┐
│ tpap-transactional-switch │ (InternalController)
└───────────┬───────────────┘
            │
            │ (3) POST /upi/int/tpap/gateway/switch/transaction/v1/status
            ▼
┌───────────────────────────┐
│       OCIL Gateway        │ (TransactionController)
└───────────┬───────────────┘
            │
            │ (4) POST /upi/ext/txn/tsp/v1/transaction/status
            ▼
┌───────────────────────────┐
│        TSP Switch         │ (PspGatewayController)
└───────────┬───────────────┘
            │
            │ (5) XML: ReqChkTxn/2.0
            ▼
┌───────────────────────────┐
│           NPCI            │
└───────────────────────────┘
```

## Step-by-Step Logic

### 1. TPAP Jobs (Trigger)
- **Service:** `tpap-transactional-jobs`
- **Action:** Quartz cron jobs (e.g., `SwitchV2TxnStatusJob`) trigger `UnboundedJobHelper`.
- **DB Hit:** Queries `DB[switchv2.txn_info]` (Slave) for `status = 'PENDING'`.
- **Kafka:** Pushes `txnId` to topic `upi_jobs_pendingtxnv2`.

### 2. TPAP Consumers (Dispatcher)
- **Service:** `tpap-consumers`
- **Listener:** `PendingTxnStatusReceiver` consumes from `upi_jobs_pendingtxnv2`.
- **Logic:** Calls `PendingTxnStatusServiceImpl.checkTxnStatus()`.
- **Outward:** Makes a synchronous HTTP POST call to `tpap-transactional-switch`.
- **API:** `/upi/int/txn/status-jobs` (Verified: ~2.1M hits/3d).

### 3. TPAP Switch (Internal Logic)
- **Service:** `tpap-transactional-switch`
- **Controller:** `InternalController.checkStatusForJobs()`.
- **Logic:** Validates txn eligibility in `InternalCheckTxnStatusService`.
- **Outward:** Calls OCIL gateway asynchronously via `GatewayAsyncHttpClientHelper`.
- **API:** `/upi/int/tpap/gateway/switch/transaction/v1/status` (Verified: ~7.2M hits/3d).

### 4. OCIL Gateway (Bank Bridge)
- **Service:** `tpap_gwts_ocil`
- **Controller:** `TransactionController.txnCheckStatus()`.
- **Logic:** Transforms TPAP format to TSP format using `CheckTransactionStatusMapper`.
- **Outward:** Calls TSP switch via `CheckTransactionStatusClient`.
- **API:** `/upi/ext/txn/tsp/v1/transaction/status` (Verified: ~600k hits/3d).

### 5. TSP Switch (Final Hop)
- **Service:** `tsp-transactional-switch`
- **Controller:** `PspGatewayController.checkTspTxnStatus()`.
- **Logic:** `CheckTxnStatusService` prepares the NPCI request.
- **NPCI Call:** Sends `ReqChkTxn` XML via `NpciClient`.
- **API:** `/upi/ReqChkTxn/2.0/` (Verified: ~9.7k hits/3d for TSP-initiated checks).

## Active APIs (Kibana Verified Hits - Last 3 Days)

| Service | API URL | Hits (3d) | Role |
|---|---|---|---|
| TPAP Switch | `/upi/int/txn/status-jobs` | 2,189,758 | Entry from Consumers |
| OCIL Gateway | `/upi/int/tpap/gateway/switch/transaction/v1/status` | 7,230,068 | Bridge to TSP |
| TSP Switch | `/upi/ext/txn/tsp/v1/transaction/status` | 600,270 | Bank side handler |
| NPCI (Out) | `/upi/ReqChkTxn/2.0/` | 9,793 | External Check |

## DB Write Points

| Service | Table | Operation | Purpose |
|---|---|---|---|
| TPAP Jobs | `jobs_properties` | `UPDATE` | Offset/Cursor management |
| TSP Switch | `txn_phases` | `INSERT` | Log NPCI `ReqChkTxn` phase |
| TSP Switch | `txn_info` | `UPDATE` | Update final status from NPCI response |

## Monitoring
- **TPAP Dashboard:** [Check Status Monitoring](https://monitor.mypaytm.com/d/ba7f1bca-d465-4af6-9440-514e7e118c8e)
- **TSP Dashboard:** [UPI War Room](https://paytmybl-grafana.paytmybl.com/d/DNTezbS7z/upi-war-room) (Check 'NPCI Health Sentinel' row)
