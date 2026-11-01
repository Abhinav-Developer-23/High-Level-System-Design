# Full UPI API Flow — TPAP + TSP (OCIL Gateway)

> **Last verified**: April 2026. APIs confirmed active via Kibana (last-3d traffic).
> Only OCIL gateway flows. Mindgate (HDFC/SBI) and Juspay (Axis) excluded.

---

## Architecture

```
                 ┌─────────────┐
  Paytm App ───► │ TPAP Switch │  (PSP switch: payer-facing)
                 └──────┬──────┘
                        │ internal HTTP (mTLS/JWT)
                 ┌──────▼──────┐
                 │OCIL Gateway │  (tpap_gwts_ocil: bank gateway for Yes Bank)
                 │  (switch)   │
                 └──────┬──────┘
                        │ internal HTTP (mTLS/JWT)
                 ┌──────▼──────┐
                 │ TSP Switch  │  (bank/TSP switch: Yes Bank UPI switch)
                 └──────┬──────┘
                        │ NPCI UPI protocol (XML/mTLS)
                 ┌──────▼──────┐
                 │    NPCI     │
                 │  UPI Switch │
                 └──────┬──────┘
                        │
                 ┌──────▼──────┐
                 │  Payee Bank │  (any member bank)
                 └─────────────┘
```

**Role mapping:**
| Component | Class | Who is it |
|-----------|-------|-----------|
| TPAP Switch | Payer PSP | Paytm app users |
| OCIL Gateway | Bank gateway | Mediates TPAP ↔ TSP |
| TSP Switch | Bank/TSP switch | Yes Bank UPI switch — acts as payer bank AND payee bank |
| NPCI | Routing hub | Routes between member banks |

---

## Terminology (UPI User Guide)

| API | Direction | Meaning |
|-----|-----------|---------|
| **ReqPay** | PSP/TSP → NPCI | Initiate pay/collect. Payer PSP sends to NPCI. NPCI also sends to payee bank for credit. |
| **ReqAuthDetails** | NPCI → PSP | Address resolution: NPCI asks payer PSP to translate VPA → bank account + auth credentials |
| **RespAuthDetails** | PSP → NPCI | PSP returns bank account + encrypted credentials |
| **RespPay** | NPCI → PSP/Bank | Final pay result from NPCI to payer bank/PSP |
| **ReqTxnConfirmation** | NPCI → PSP | Final txn status sent by NPCI to SECOND PSP (payer PSP for collect, payee PSP for pay) |
| **ReqChkTxn** | PSP/Bank → NPCI | Check transaction status |
| **RespChkTxn** | NPCI → PSP/Bank | Response to ReqChkTxn |
| **ReqHbt** | Both | Heartbeat — connectivity check |
| **ReqComplaint** | PSP → NPCI | Raise complaint for a transaction |
| **RespComplaint** | NPCI → PSP | Response to complaint |

---

## DB Tables

Both TPAP and TSP have identical schema:

### `txn_info`
```
txn_id         — primary UPI txn ID (e.g. PTM..., SBI...)
ref_id         — reference ID (same as txn_id for pay)
rrn            — NPCI-assigned RRN (after NPCI processes)
type           — PAY | COLLECT
business_type  — P2P | P2M | MANDATE etc.
status         — PENDING | SUCCESS | FAILED | DEEMED
amount
npci_resp_code — NPCI response code (00 = success)
app_resp_code  — our app response code
mid            — merchant ID (for P2M)
order_id       — PG order ID
npci_ts        — NPCI timestamp
created_on
updated_on
extended_info  — JSON blob (extra fields)
```

### `txn_participants`
```
txn_id         — FK → txn_info
role           — PAYER | PAYEE
vpa            — UPI VPA
bank_code      — e.g. HDFC, SBIN, YESB
ifsc
account_number (masked)
account_type   — SAVINGS | CURRENT
name
status         — per-participant status
```

### `txn_phases` (audit trail)
```
txn_id, phase_name, created_on
— Records: REQPAY_ACK, REQAUTHDETAILS_ACK, REQTXNCONFIRMATION_ACK etc.
```

---

## 1. P2P Pay — Payer Flow (TPAP side)

User (Paytm app) initiates payment to any VPA.

### 1a. Confirmed Active APIs (Kibana — 3d traffic)

| # | API | URL | Volume | Notes |
|---|-----|-----|--------|-------|
| 1 | CommonPayRequestAsync | `POST /upi/ext/txn/v3/common-pay-request-async` | 363M | **ENTRY POINT** |
| 2 | TransactionStatus | `GET /upi/ext/txn/v6/transaction/status` | 385M | App status poll |
| 3 | TxnCallback | `POST /upi/int/txn/issuing/txn-callback` | 186M | Callback from OCIL (RespPay result) |
| 4 | ReqTxnConfirmationCallback | `POST /upi/int/txn/issuing/req-txn-confirmation-callback` | 226M | Callback from OCIL (NPCI final confirm) |
| 5 | CheckStatusResponse | `POST /upi/int/txn/issuing/check/status/response` | 1.1M | Check status result from OCIL |
| 6 | StatusJobs | `POST /upi/int/txn/status-jobs` | 2.2M | Job-triggered status reconciliation |
| 7 | InternalStatus | `POST /upi/int/txn/v4/transaction/status` | 3.8M | Internal check status |

### 1b. Flow Diagram

```
APP                     TPAP SWITCH                  OCIL GATEWAY                TSP SWITCH                NPCI
 |                           |                             |                           |                      |
 |--POST common-pay-async--->|                             |                           |                      |
 |   (VPA, amt, enc.creds)   |                             |                           |                      |
 |                           |--INSERT txn_info(PENDING)   |                           |                      |
 |                           |--INSERT txn_participants    |                           |                      |
 |<--202 PENDING-------------|                             |                           |                      |
 |                           |--POST send-money (async)--->|                           |                      |
 |                           |   /tpap/gateway/txn/v1/send-money                       |                      |
 |                           |                             |--POST common-pay-async--->|                      |
 |                           |                             |   /upi/ext/txn/tsp/v1/... |                      |
 |                           |                             |<--200 ACK-----------------|                      |
 |                           |                             |                           |--INSERT txn_info(PENDING)
 |                           |                             |                           |--INSERT txn_participants
 |                           |                             |                           |--ReqPay (XML)-------->|
 |                           |                             |                           |<--ACK (XML)-----------|
 |                           |                             |                           |                      |
 |                           |                             |                           |<--ReqAuthDetails-----|
 |                           |                             |                           |   (translate VPA)    |
 |                           |                             |                           |--RespAuthDetails---->|
 |                           |                             |                           |   (bank acct + creds)|
 |                           |                             |                           |                      |--ReqPay→Payee Bank
 |                           |                             |                           |                      |<--RespPay←Payee Bank
 |                           |                             |                           |<--RespPay------------|
 |                           |                             |                           |--UPDATE txn_info(result)
 |                           |                             |<--TSP callback------------|                      |
 |                           |                             |   (TSPGatewayResponseDto) |                      |
 |                           |<--POST txn-callback---------|                           |                      |
 |                           |   /upi/int/txn/issuing/txn-callback                    |                      |
 |                           |--UPDATE txn_info(result)    |                           |                      |
 |                           |                             |                           |<--ReqTxnConfirmation-|
 |                           |                             |                           |   (NPCI final status)|
 |                           |                             |<--POST req-txn-conf/cb----|                      |
 |                           |                             |   /tpap/gateway/meta/tsp/switch/v1/req-txn-confirmation/callback
 |                           |<--POST req-txn-conf-cb------|                           |                      |
 |                           |   /upi/int/txn/issuing/req-txn-confirmation-callback   |                      |
 |                           |--UPDATE txn_info(FINAL)     |                           |                      |
 |--GET v6/transaction/status>|                             |                           |                      |
 |<--SUCCESS/FAILED-----------|                             |                           |                      |
```

### 1c. Controller → Service Mapping (TPAP Switch)

| URL | Controller | Service |
|-----|------------|---------|
| `/upi/ext/txn/v3/common-pay-request-async` | `TransactionController` | `CommonPayRequestService` |
| `/upi/ext/txn/v6/transaction/status` | `CheckStatusController` | `TransactionService` |
| `/upi/int/txn/issuing/txn-callback` | `TPAPGatewayController` | `PSPGatewayTxnUpdateService` |
| `/upi/int/txn/issuing/req-txn-confirmation-callback` | `GatewayReqTxnConfirmationCallbackController` | `PSPGatewayReqTxnConfirmation` |
| `/upi/int/txn/issuing/check/status/response` | `TPAPGatewayController` | `PSPGatewayTxnUpdateService` |
| `/upi/int/txn/status-jobs` | `InternalController` | — |

### 1d. Controller → Service Mapping (OCIL Gateway — switch module)

| URL | Controller | Service |
|-----|------------|---------|
| `/upi/int/tpap/gateway/transaction/v1/send-money` | `TransactionController` (OCIL) | ExecutionChain: TransactionRequestMapper → TransactionAPIClient → TpapCallbackClient |
| `/upi/int/tpap/gateway/meta/tsp/switch/v1/req-txn-confirmation/callback` | `SwitchTspController` | `SwitchTspService.reqTxnConfirmationCallback` |
| `/upi/int/tpap/gateway/switch/transaction/v1/status` | `TransactionController` (OCIL) | `txnCheckStatus` → TSP check status → TPAP callback |

---

## 2. P2P/P2M Pay — Payee Flow (TSP side)

When any payer (from any bank) sends money to a Paytm Yes Bank VPA (`@ptyes`, `@paytmybl` etc.).

### 2a. Confirmed Active APIs

| # | API | URL | Volume | Notes |
|---|-----|-----|--------|-------|
| 1 | ReqPay (inward) | `POST /upi/ReqPay/2.0/{txnid}` | 288M | **ENTRY** — NPCI credits payee |
| 2 | ReqTxnConfirmation | `POST /upi/ReqTxnConfirmation/2.0/{txnid}` | 318M | NPCI final status to payee PSP |
| 3 | RespHbt | `POST /upi/RespHbt/2.0/` | 959K | Heartbeat response from NPCI |
| 4 | ReqChkTxn | `POST /upi/ReqChkTxn/2.0/` | 8.1K | NPCI check status |
| 5 | RespChkTxn | `POST /upi/RespChkTxn/2.0/` | 973K | NPCI reply to our ReqChkTxn |
| 6 | RespComplaint | `POST /upi/RespComplaint/2.0/` | 3K | NPCI complaint response |
| 7 | ReqComplaint | `POST /upi/ReqComplaint/2.0/` | 1.2K | NPCI sends complaint to bank |

### 2b. Flow Diagram

```
NPCI                     TSP SWITCH
  |                           |
  |--POST ReqPay/2.0/{id}---->|   (XML — credit payee account)
  |<--ACK (XML)---------------|
  |                           |--INSERT txn_info(PENDING)
  |                           |--INSERT txn_participants(PAYEE)
  |                           |--Process credit to payee bank account
  |                           |--UPDATE txn_info(SUCCESS/FAILED)
  |                           |--RespPay sent async to NPCI
  |--POST ReqTxnConfirmation->|   (NPCI confirms final status to payee PSP)
  |<--ACK (XML)---------------|
  |                           |--UPDATE txn_info(FINAL)
  |                           |--txn_phases(REQTXNCONFIRMATION_ACK)
```

### 2c. Controller Mapping (TSP Switch)

| URL | Controller | Service |
|-----|------------|---------|
| `/upi/ReqPay/2.0/{txnid}` | `NpciRequestController.ReqPay` | `BankApiService` |
| `/upi/ReqTxnConfirmation/2.0/{txnid}` | `NpciRequestController.reqTxnConfirmation` | `TxnService` |
| `/upi/RespPay/2.0/` | `NpciRequestController` | — |
| `/upi/ReqChkTxn/2.0/` | `NpciRequestController` | — |
| `/upi/RespChkTxn/2.0/` | `NpciRequestController` | — |
| `/upi/ReqComplaint/2.0/` | `NpciRequestController` | `ReqComplaintService` |
| `/upi/RespComplaint/2.0/` | `NpciRequestController` | — |
| `/upi/RespHbt/2.0/` | `NpciRequestController` | `HeartBeatService` |

---

## 3. P2P Pay — Payer on TSP (TSP-initiated pay)

When a Paytm Yes Bank user (TSP) initiates payment (not through Paytm app, e.g. Yes Bank app or other channel).

### 3a. Confirmed Active APIs

| # | API | URL | Volume | Notes |
|---|-----|-----|--------|-------|
| 1 | CommonPayAsync | `POST /upi/ext/txn/tsp/v1/common-pay-request-async` | 73M | **TSP PAY ENTRY POINT** |
| 2 | ReqAuthDetails | `POST /upi/ReqAuthDetails/2.0/{txnid}` | 317M | NPCI asks TSP to validate payer creds |
| 3 | RespPay | `POST /upi/RespPay/2.0/` | 75M | NPCI returns debit result to TSP |
| 4 | TransactionStatus | `POST /upi/ext/txn/tsp/v1/transaction/status` | 423K | Status check |
| 5 | UpdateTxnStatus | `POST /upi/transaction/update-txn-status` | 43K | Internal status update |
| 6 | UpdateDrcTxnStatus | `POST /upi/int/txn/update-drc-txn-status` | 59K | DRC status update |

### 3b. Flow Diagram

```
CHANNEL                 TSP SWITCH                    NPCI
  |                          |                           |
  |--POST tsp/common-pay---->|                           |
  |   (VPA, amt, enc.creds)  |                           |
  |                          |--INSERT txn_info(PENDING) |
  |                          |--INSERT txn_participants  |
  |<--ACK (txnId)------------|                           |
  |                          |--ReqPay (XML)------------>|
  |                          |<--ACK (XML)---------------|
  |                          |                           |
  |                          |<--ReqAuthDetails----------|
  |                          |   (validate payer VPA)   |
  |                          |--RespAuthDetails-------->|
  |                          |   (bank acct + auth creds)|
  |                          |                           |--ReqPay→Payee Bank
  |                          |                           |<--RespPay←Payee Bank
  |                          |<--RespPay-----------------|
  |                          |--UPDATE txn_info(result)  |
  |                          |<--ReqTxnConfirmation------|
  |                          |--UPDATE txn_info(FINAL)   |
  |--GET tsp/v1/txn/status-->|                           |
  |<--result----------------|                            |
```

### 3c. Controller Mapping (TSP Switch)

| URL | Controller | Service |
|-----|------------|---------|
| `/upi/ext/txn/tsp/v1/common-pay-request-async` | `TransactionV2Controller` (or via `RouterGatewayController`) | `PayMerchantService` / `CommonPayRequestService` |
| `/upi/ReqAuthDetails/2.0/{txnid}` | `NpciRequestController.ReqAuthDetails` | `AuthDetailService` |
| `/upi/RespPay/2.0/` | `NpciRequestController` | — |
| `/upi/ext/txn/tsp/v1/transaction/status` | `TransactionHistoryStatusController` | — |

---

## 4. Collect Flow (Payer side — TPAP)

A merchant/payee initiates collect. Payer (Paytm app) receives notification and authorizes.

### 4a. Confirmed Active APIs

| # | API | URL | Volume | Notes |
|---|-----|-----|--------|-------|
| 1 | GetPendingRequest | `POST /upi/ext/txn/v2/transaction/get-pending-request` | 911K | App polls for pending collect |
| 2 | CollectAuth | `POST /upi/ext/txn/v3/collect-auth` | 885K | Payer approves + enters MPIN |
| 3 | CreateTxnForCollect | `POST /upi/int/txn/issuing/create-txn-for-collect` | 521K | OCIL notifies TPAP of incoming collect |

### 4b. Flow Diagram

```
PAYEE                PAYEE PSP               NPCI              TSP SWITCH            OCIL             TPAP SWITCH         APP(PAYER)
  |                      |                     |                     |                   |                    |                  |
  |--initiate collect--->|                     |                     |                   |                    |                  |
  |                      |--ReqPay(COLLECT)--->|                     |                   |                    |                  |
  |                      |                     |--ReqPay(COLLECT)--->|   (TSP = payer bank)                   |                  |
  |                      |                     |<--ACK---------------|                   |                    |                  |
  |                      |                     |                     |--create collect--->                    |                  |
  |                      |                     |                     |  POST /upi/int/txn/issuing/            |                  |
  |                      |                     |                     |  incoming-money-to-customer/           |                  |
  |                      |                     |                     |  create-txn-for-collect (OCIL)         |                  |
  |                      |                     |                     |                   |--POST create-txn-->|                  |
  |                      |                     |                     |                   |   /upi/int/txn/issuing/create-txn-for-collect
  |                      |                     |                     |                   |                    |--INSERT txn_info(PENDING)
  |                      |                     |                     |                   |                    |--push notification→APP
  |                      |                     |                     |                   |                    |<--GET get-pending-request-|
  |                      |                     |                     |                   |                    |--return collect details-->|
  |                      |                     |                     |                   |                    |<--POST collect-auth-------|
  |                      |                     |                     |                   |                    |   (enc. MPIN)            |
  |                      |                     |                     |                   |<--send-money(collt)-|                         |
  |                      |                     |                     |<--common-pay-async-|                   |                         |
  |                      |                     |<--ReqPay(PAY)-------|                   |                    |                         |
  |                      |                     |  (CREDIT payee)     |                   |                    |                         |
  ... (same as Pay flow from here)
  |                      |                     |<--RespPay(result)---|                   |                    |                         |
  |                      |                     |                     |--TSP callback---->|--TPAP txn-callback>|                         |
  |                      |                     |--ReqTxnConfirmation>|                   |                    |                         |
  |                      |                     |   (payer PSP)       |--req-txn-conf-cb->|->TPAP req-txn-conf-|                         |
```

### 4c. OCIL Endpoint for Collect
From OCIL exchange logs:
- OCIL receives collect from TSP at: `POST /upi/int/txn/issuing/incoming-money-to-customer/create-txn-for-collect` (1.5M hits)
- OCIL → TPAP: `POST /upi/int/txn/issuing/create-txn-for-collect`

---

## 5. PG (Payment Gateway) Flow — TSP

Merchants accept UPI payments via Paytm PG (OCL). TSP acts as payee bank + handles order lifecycle.

### 5a. Confirmed Active APIs

| # | API | URL | Volume | Notes |
|---|-----|-----|--------|-------|
| 1 | OrderCallback | `POST /upi/ext/txn/v1/create/order/callback` | 280M | **PG→TSP**: PG notifies TSP of new order |
| 2 | PgTxnStatus | `GET /Paytm_UPI/upi/pg-transaction-status` | 46M | PG polls txn status from TSP |
| 3 | PgTxnStatusCrossCluster | `GET /int/pg-transaction-status-crossCluster` | 45M | Cross-cluster status (c2/c3/c6) |
| 4 | OrderDetails | `GET /Paytm_UPI/upi/order-details` | 18M | Fetch order details |
| 5 | CollectMerchantRequest | `POST /Paytm_UPI/upi/collect-merchant-request` | 418K | Merchant-initiated collect |
| 6 | PreapprovedOrgTxnInfo | `POST /upi/preapproved/org-txn-info` | 399K | Pre-approved txn info |
| 7 | EntityData | `GET /int/upi/entityData` | 21M | Entity/merchant data |
| 8 | TriggerNotification | `POST /upi/ext/txn/acquirer/v1/trigger-notification` | 8.7K | Trigger payment notification |

### 5b. Flow Diagram

```
PAYER APP           PG (OCL)              TSP SWITCH              NPCI          PAYEE BANK
    |                   |                      |                     |                |
    |--pay intent------->|                     |                     |                |
    |                   |--POST order/callback->|   (pgEntity=OCL)   |                |
    |                   |                      |--INSERT txn_info(PENDING)            |
    |                   |                      |--INSERT txn_participants             |
    |                   |<--ACK----------------|                     |                |
    |                   |                      |                     |                |
    |--enters MPIN------>|                     |                     |                |
    |                   |--POST tsp/common-pay->|                    |                |
    |                   |   (or TPAP route)    |--ReqPay(CREDIT)---->|                |
    |                   |                      |<--ACK---------------|                |
    |                   |                      |<--ReqAuthDetails----|                |
    |                   |                      |--RespAuthDetails--->|                |
    |                   |                      |                     |--ReqPay------->|
    |                   |                      |                     |<--RespPay------|
    |                   |                      |<--RespPay-----------|                |
    |                   |                      |--UPDATE txn_info(SUCCESS/FAILED)     |
    |                   |<--GET pg-txn-status--|   (PG polls)        |                |
    |                   |--200 {status}-------->|                    |                |
    |<--payment result---|                     |                     |                |
```

### 5c. PG Key Notes
- `pgEntity` in callback identifies the PG (OCL = OCIL/Yes Bank PG)
- `merchantOrderId` = PG's reference ID, `npciTxnId` = UPI txn ID
- Cross-cluster status (`/int/pg-transaction-status-crossCluster`) used when txn landed on a different cluster

---

## 6. Collect Flow — TSP-initiated Collect

When a merchant (payee) on TSP initiates a collect request.

### 6a. Confirmed Active APIs

| # | API | URL | Volume | Notes |
|---|-----|-----|--------|-------|
| 1 | CollectAuth | `POST /upi/ext/txn/tsp/v1/collect-auth` | 89K | Payer (TSP user) approves collect |
| 2 | CollectMerchantReq | `POST /Paytm_UPI/upi/collect-merchant-request` | 418K | Merchant initiates collect via TSP |

---

## 7. UPI Lite Flow

On-device wallet. No MPIN required for debit. Topup requires MPIN.

### 7a. Confirmed Active APIs — TPAP

| # | API | URL | Volume |
|---|-----|-----|--------|
| 1 | LiteAppPay | `POST /upi/ext/txn/lite/v2/app-pay` | 8M |
| 2 | LiteSync | `POST /upi/ext/txn/lite/v2/sync` | 5.3M |
| 3 | LiteCheckStatus | `POST /upi/ext/txn/lite/v1/sync/check-status` | 4.3M |
| 4 | LiteSyncCallback | `POST /upi/int/txn/lite/v1/sync/callback` | 2.6M |
| 5 | LiteTopup | `POST /upi/ext/txn/lite/v1/topup` | 1.7M |
| 6 | LiteDeregister | `POST /upi/ext/txn/lite/v1/deregister` | 77.7K |
| 7 | LiteDeregisterCallback | `POST /upi/int/txn/lite/v1/deregister/callback` | 38.9K |

### 7b. Confirmed Active APIs — OCIL Gateway (relaying TSP Lite)

| # | API | URL | Volume |
|---|-----|-----|--------|
| 1 | LiteSendMoney | `POST /upi/int/tpap/gateway/transaction/v1/lite/send-money` | 29M |
| 2 | LiteTopup | `POST /upi/int/tpap/gateway/transaction/v1/lite/topup` | 7M |
| 3 | LiteSync | `POST /upi/int/tpap/gateway/lite/v1/lite-sync` | 6.9M |
| 4 | LiteSyncCheckStatus | `POST /upi/int/tpap/gateway/lite/v2/sync/check-status` | 10.3M |
| 5 | LiteZeroBalance | `POST /upi/int/tpap/gateway/lite/v1/zero-balance-disablement` | 403K |

### 7c. Confirmed Active APIs — TSP

| # | API | URL | Volume |
|---|-----|-----|--------|
| 1 | LiteAppPay | `POST /upi/ext/txn/tsp/lite/v1/app-pay` | 3.3M |
| 2 | LiteSync | `POST /upi/ext/txn/tsp/lite/v2/sync` | 1.9M |
| 3 | LiteCheckStatus | `POST /upi/ext/txn/tsp/lite/v3/sync/check-status` | 1.4M |
| 4 | LiteTopup | `POST /upi/ext/txn/tsp/lite/v1/topup` | 783K |
| 5 | LiteDeregister | `POST /upi/ext/txn/tsp/lite/v1/deregister` | 38.3K |
| 6 | TspLiteSync (via OCIL) | `POST /upi/ext/txn/tsp/lite/v2/sync` | 11M (on OCIL) |
| 7 | TspLiteCheckStatus (via OCIL) | `POST /upi/ext/txn/tsp/lite/v3/sync/check-status` | 8.6M (on OCIL) |

### 7d. Lite Pay Flow

```
APP                  TPAP Switch           OCIL Gateway          TSP Switch
 |                        |                     |                      |
 |--POST lite/v2/app-pay->|                     |                      |
 |<--ACK PENDING----------|                     |                      |
 |                        |--POST lite/send-money->|                   |
 |                        |                     |--POST tsp/lite/v1/app-pay->|
 |                        |                     |<--ACK---------------|      |
 |                        |                     |                      |--process (no MPIN)
 |                        |                     |<--TSP callback-------|
 |                        |<--POST lite/sync/callback-|               |
 |--GET lite/check-status->|                    |                      |
 |<--result---------------|                     |                      |
```

---

## 8. Check Status / Status Reconciliation

### 8a. Confirmed Active APIs

| # | API | Location | URL | Volume |
|---|-----|----------|-----|--------|
| 1 | AppStatus | TPAP | `GET /upi/ext/txn/v6/transaction/status` | 385M |
| 2 | InternalStatus | TPAP | `POST /upi/int/txn/v4/transaction/status` | 3.8M |
| 3 | StatusJobs | TPAP | `POST /upi/int/txn/status-jobs` | 2.2M |
| 4 | GatewayStatus | OCIL | `POST /upi/int/tpap/gateway/switch/transaction/v1/status` | 7.6M |
| 5 | TspStatus | TSP | `POST /upi/ext/txn/tsp/v1/transaction/status` | 423K |
| 6 | PgStatus | TSP | `GET /Paytm_UPI/upi/pg-transaction-status` | 46M |
| 7 | CrossClusterStatus | TSP | `GET /int/pg-transaction-status-crossCluster` | 45M |
| 8 | CheckStatusCrossCluster | TSP | `GET /int/checkStatusCrossCluster` | 13K |
| 9 | CheckStatusTpapCrossCluster | TSP | `GET /int/checkStatusTPAPCrossCluster` | 30K |

### 8b. Check Status Flow (TPAP-initiated, ReqChkTxn to NPCI)

```
TPAP Switch            OCIL Gateway              TSP Switch              NPCI
    |                       |                         |                     |
    |--POST status-jobs---->|  (internal timer)        |                    |
    |                       |--POST gateway/status---->|                    |
    |                       |                          |--ReqChkTxn(XML)--->|
    |                       |                          |<--ACK-------------|
    |                       |                          |<--RespChkTxn------|
    |                       |                          |--UPDATE txn_info   |
    |                       |<--callback (check-status-result)             |
    |<--POST issuing/check/status/response             |                    |
    |--UPDATE txn_info       |                         |                    |
```

---

## 9. Complaint Flow

### 9a. Confirmed Active APIs

| # | API | Location | URL | Volume |
|---|-----|----------|-----|--------|
| 1 | InitiateComplaint | TPAP | `POST /upi/int/txn/v1/initiate/complaint` | 6.7K |
| 2 | ComplaintCheckStatus | TPAP | `POST /upi/int/txn/v1/complaint/checkstatus` | 329K |
| 3 | RespComplaint | TPAP | `POST /upi/int/txn/v1/RespComplaint` | 37.4K |
| 4 | InitiateComplaint | TSP | `POST /upi/ext/txn/tsp/v1/initiate/complaint` | 2.9K |
| 5 | ComplaintCheckStatus | TSP | `POST /upi/ext/txn/tsp/v1/complaint/checkstatus` | 18K |
| 6 | ReqComplaint (to NPCI) | TSP | `POST /upi/ReqComplaint/2.0/` | 1.2K |
| 7 | RespComplaint (from NPCI) | TSP | `POST /upi/RespComplaint/2.0/` | 3K |

---

## 10. Misc Internal/Config APIs (Active)

| API | Location | URL | Volume | Purpose |
|-----|----------|-----|--------|---------|
| RouterConfig | TSP | `GET /upi/int/v1/router/config` | 460K | TSP router pulls routing config |
| ApplicationConfig | TPAP | `POST /upi/int/v1/application/config` | 46.6K | App config |
| GetProperties | TPAP | `POST /upi/int/get/properties` | 193 | Properties fetch |
| UpdateProperties | TPAP | `POST /upi/int/update/properties` | 25 | Properties update |
| UthTxnView | TPAP | `POST /upi/int/txn/uth/view` | 45K | UTH view |
| UthTxnView | OCIL | `POST /upi/int/tpap/gateway/mandate/payer/txn/uth/view` | 22 | — |
| UdirAutoUpdate | TPAP | `POST /upi/int/txn/v1/udir/autoupdate` | 14K | UDIR address update |
| RouterConfig | OCIL→TSP | `GET /upi/int/v1/router/config` | 460K | — |
| EntityData | TSP | `GET /int/upi/entityData` | 21M | Entity/merchant metadata |
| PreapprovedOrgTxnInfo | TSP | `POST /upi/preapproved/org-txn-info` | 399K | Pre-approved UPI txn |
| StatusJobs | TSP | `POST /int/status-jobs` | 8.3K | Background status reconciliation |
| UpdateTxnStatus | TSP | `POST /upi/transaction/update-txn-status` | 43K | — |
| UpdateDrcTxnStatus | TPAP | `POST /upi/int/txn/update-drc-txn-status` | 7.2K | DRC status update |
| UpdateDrcTxnStatus | TSP | `POST /upi/int/txn/update-drc-txn-status` | 59K | — |

---

## 11. Summary: All Active APIs by System

### TPAP Switch (Kibana index: `prod-tpap-transactional-switch_exchange-*`)
```
EXTERNAL (App-facing):
  POST /upi/ext/txn/v3/common-pay-request-async      [363M] ← PAY ENTRY
  GET  /upi/ext/txn/v6/transaction/status            [385M] ← STATUS POLL
  POST /upi/ext/txn/v2/transaction/get-pending-request[911K] ← COLLECT PENDING
  POST /upi/ext/txn/v3/collect-auth                  [884K] ← COLLECT APPROVE
  POST /upi/ext/txn/lite/v2/app-pay                  [8M]   ← LITE PAY
  POST /upi/ext/txn/lite/v2/sync                     [5.3M]
  POST /upi/ext/txn/lite/v1/sync/check-status        [4.3M]
  POST /upi/ext/txn/lite/v1/topup                    [1.7M]
  POST /upi/ext/txn/lite/v1/deregister               [77K]

INTERNAL (from OCIL gateway callbacks):
  POST /upi/int/txn/issuing/req-txn-confirmation-callback [226M] ← NPCI FINAL
  POST /upi/int/txn/issuing/txn-callback                  [186M] ← RESPPAY
  POST /upi/int/txn/v4/transaction/status                 [3.8M]
  POST /upi/int/txn/lite/v1/sync/callback                 [2.6M]
  POST /upi/int/txn/status-jobs                           [2.2M]
  POST /upi/int/txn/issuing/check/status/response         [1.1M]
  POST /upi/int/txn/issuing/create-txn-for-collect        [521K]
  POST /upi/int/txn/v1/complaint/checkstatus              [329K]
  POST /upi/int/txn/lite/v1/deregister/callback           [38.9K]
  POST /upi/int/txn/v1/RespComplaint                      [37.4K]
  POST /upi/int/txn/v1/udir/autoupdate                    [14.3K]
  POST /upi/int/txn/update-drc-txn-status                 [7.2K]
  POST /upi/int/txn/update-txn-status                     [7K]
  POST /upi/int/txn/v1/initiate/complaint                 [6.7K]
  POST /upi/int/txn/uth/view                              [45.5K]
  POST /upi/int/v1/application/config                     [46.6K]
```

### OCIL Gateway (Kibana index: `prod-tpap-gwts-ocil-switch-yes-*`)
```
FROM TPAP SWITCH (inbound — TPAP calls OCIL):
  POST /upi/int/tpap/gateway/transaction/v1/send-money            [1.3B] ← PAY
  POST /upi/int/tpap/gateway/transaction/v1/lite/send-money       [29M]
  POST /upi/int/tpap/gateway/transaction/v1/lite/topup            [7M]
  POST /upi/int/tpap/gateway/switch/transaction/v1/status         [7.6M]
  POST /upi/int/tpap/gateway/lite/v1/lite-sync                    [6.9M]
  POST /upi/int/tpap/gateway/lite/v2/sync/check-status            [10.3M]
  POST /upi/int/tpap/gateway/lite/v1/zero-balance-disablement     [403K]
  POST /upi/int/txn/issuing/incoming-money-to-customer/create-txn-for-collect [1.5M]
  POST /upi/int/tpap/gateway/complaints/v1/status                 [225K]
  POST /upi/int/tpap/gateway/complaint/v1/initiate-complaint      [38K]

FROM TSP SWITCH (callbacks — TSP calls back OCIL):
  POST /upi/int/tpap/gateway/meta/tsp/switch/v1/req-txn-confirmation/callback [1.4B]
  POST /upi/int/tpap/gateway/meta/tsp/switch/v1/collect-auth      [1.5M]

TSP-FACING (OCIL relays to TSP):
  POST /upi/ext/txn/tsp/lite/v2/sync                              [11M]
  POST /upi/ext/txn/tsp/lite/v3/sync/check-status                 [8.6M]
  POST /upi/ext/txn/tsp/v1/mandate/search-active-mandates         [1.7M]
```

### TSP Switch (Kibana index: `prod-paytmybl-tsp-switchc2/c3/c6_exchange*`)
```
FROM NPCI (inward UPI protocol):
  POST /upi/ReqTxnConfirmation/2.0/{id}   [318M] ← NPCI final status (payer PSP or payee PSP)
  POST /upi/ReqAuthDetails/2.0/{id}       [317M] ← NPCI auth/address resolution (payer bank)
  POST /upi/ReqPay/2.0/{id}              [288M] ← NPCI pay to payee bank
  POST /upi/RespPay/2.0/                 [75M]  ← NPCI RespPay
  POST /upi/RespChkTxn/2.0/             [973K]
  POST /upi/RespHbt/2.0/                [959K]
  POST /upi/ReqChkTxn/2.0/             [8.1K]
  POST /upi/RespComplaint/2.0/          [3K]
  POST /upi/ReqComplaint/2.0/           [1.2K]

FROM PG / APP (external):
  POST /upi/ext/txn/v1/create/order/callback   [280M] ← PG notifies TSP
  POST /upi/ext/txn/tsp/v1/common-pay-request-async [73M] ← TSP PAY ENTRY
  GET  /Paytm_UPI/upi/pg-transaction-status   [46M]
  GET  /int/pg-transaction-status-crossCluster [45M]
  GET  /int/upi/entityData                     [21M]
  GET  /Paytm_UPI/upi/order-details            [18M]
  POST /upi/ext/txn/tsp/lite/v1/app-pay        [3.3M]
  POST /upi/ext/txn/tsp/lite/v2/sync           [1.9M]
  POST /upi/ext/txn/tsp/lite/v3/sync/check-status [1.4M]
  POST /Paytm_UPI/upi/collect-merchant-request [418K]
  POST /upi/preapproved/org-txn-info           [399K]
  POST /upi/ext/txn/tsp/v1/transaction/status  [423K]
  POST /upi/ext/txn/tsp/lite/v1/topup          [783K]
  POST /upi/ext/txn/tsp/v1/collect-auth        [89K]
  POST /upi/ext/txn/tsp/lite/v1/deregister     [38K]
  GET  /upi/int/v1/router/config               [460K]
  POST /upi/ext/txn/acquirer/v1/trigger-notification [8.7K]
  POST /upi/ext/txn/tsp/v1/initiate/complaint  [2.9K]
  POST /upi/ext/txn/tsp/v1/complaint/checkstatus [18K]

INTERNAL:
  POST /int/checkStatusTPAPCrossCluster       [30K]
  POST /int/checkStatusCrossCluster           [13K]
  POST /int/txn/update-txn-status-cross-cluster [2.6K]
  POST /int/txn/update-drc-txn-status-cross-cluster [1.3K]
  POST /int/status-jobs                       [8.3K]
  POST /upi/transaction/update-txn-status     [43K]
  POST /upi/int/txn/update-drc-txn-status     [59K]
```

---

## 12. DB Write Points (Both TPAP and TSP)

```
API Call                            DB Operation
─────────────────────────────────────────────────────────────────────────
common-pay-request-async (entry)  → INSERT txn_info (status=PENDING)
                                  → INSERT txn_participants (payer + payee)
ReqPay ACK received               → INSERT txn_phases (REQPAY_ACK)
ReqAuthDetails ACK                → INSERT txn_phases (REQAUTHDETAILS_ACK)
RespPay received                  → UPDATE txn_info (status, npci_resp_code, rrn)
txn-callback from OCIL           → UPDATE txn_info (status)
ReqTxnConfirmation ACK            → INSERT txn_phases (REQTXNCONFIRMATION_ACK)
req-txn-confirmation-callback    → UPDATE txn_info (FINAL status)
create-txn-for-collect           → INSERT txn_info (collect, status=PENDING)
ReqPay (payee bank, inward)       → INSERT txn_info + txn_participants (payee side)
PG order/callback                 → INSERT txn_info (order_id, mid)
```

---

*Source: Kibana `now-3d` aggregation on `contextMap.url.keyword` + source repo controller analysis.*
*Repos: `tpap-transactional-switch`, `tsp-transactional-switch`, `tpap_gwts_ocil`.*
*UPI API descriptions: `resources/Docs/india-unified-payment-interface-upi-user-guide.md`.*
