# UPI Lite End-to-End Flow

> Verified: 2026-04-25. APIs confirmed via Kibana (now-3d traffic).
> Systems: TPAP Switch | OCIL Gateway | TSP Switch | NPCI

## Architecture Context
UPI Lite is a low-value offline payment feature (max ₹500) where the balance is maintained in an on-device wallet. The flow involves loading funds into a "Lite Pool" (escrow) at the bank and performing payments using a cryptogram (ARQC) which is later synchronized with the bank switch.

## Flow Overview (ASCII Diagram)

```
   Mobile App          TPAP Switch         OCIL Gateway         TSP Switch            NPCI
       │                    │                   │                   │                  │
       │  /app-pay (v2)     │                   │                   │                  │
       ├───────────────────►│                   │                   │                  │
       │                    │                   │                   │                  │
       │                    │ → DB[txn_info]:   │                   │                  │
       │                    │   INSERT PENDING  │                   │                  │
       │                    │                   │                   │                  │
       │                    │  /tsp/lite/app-pay│                   │                  │
       │                    ├──────────────────►│                   │                  │
       │                    │                   │                   │                  │
       │                    │                   │  /tsp/lite/app-pay│                  │
       │                    │                   ├──────────────────►│                  │
       │                    │                   │                   │                  │
       │                    │                   │                   │ → DB[txn_info]:  │
       │                    │                   │                   │   INSERT PENDING │
       │                    │                   │                   │                  │
       │                    │                   │                   │    ReqPay XML    │
       │                    │                   │                   ├─────────────────►│
       │                    │                   │                   │ (Purpose 41-44)  │
       │                    │                   │                   │                  │
       │                    │                   │                   │    RespPay XML   │
       │                    │                   │                   │◄─────────────────┤
       │                    │                   │                   │                  │
       │                    │                   │                   │ → DB[txn_info]:  │
       │                    │                   │                   │   UPDATE SUCCESS │
       │                    │                   │                   │                  │
       │                    │   Callback        │   Callback        │                  │
       │◄───────────────────┼◄──────────────────┼◄──────────────────┤                  │
       │ (Push Notification)│                   │                   │                  │
```

## Step-by-Step: [Payer Side / TPAP]
- **API Entry:** `POST /upi/v2/ext/txn/lite/app-pay`
- **Controller:** `UPILiteController.appPayRequestV2`
- **Logic:**
    1.  Validates the request (device binding, user session).
    2.  Sets `TXN_MODEL.ASYNC`.
    3.  `LitePayServiceImpl.requestPay` is called.
    4.  **DB[txn_info]:** Creates a new record with status `PENDING`.
    5.  **DB[txn_participants]:** Records payer and payee details.
    6.  **Forwarding:** Calls OCIL Gateway via `GatewayAsyncHttpClientHelper`.
- **Response to App:** Immediate `200 OK` (ASYNC ACK).

## Step-by-Step: [Gateway / OCIL]
- **API Entry:** `POST /upi/ext/txn/tsp/lite/v1/app-pay`
- **Logic:**
    1.  Receives the request from TPAP.
    2.  Forwards the payload to the TSP Switch URL `/upi/ext/txn/tsp/lite/v1/app-pay`.

## Step-by-Step: [TSP / Bank Side]
- **API Entry:** `POST /upi/ext/txn/tsp/lite/v1/app-pay`
- **Controller:** `UPILiteController.appPayRequest`
- **Logic:**
    1.  `LitePayServiceImpl.requestPay` (TSP version) handles the logic.
    2.  **DB[txn_info]:** Records the transaction in TSP's database.
    3.  **NPCI XML:** Marshals `ReqPay` XML.
        -   **Purpose Code:** 41 (Lite Pay), 42 (Lite Top-up), etc.
        -   **Creds:** Includes `ARQC` (cryptogram) from the app.
        -   **Details:** Includes `LRN` (Lite Reference Number).
    4.  **NPCI Call:** Dispatches XML to NPCI.
- **NPCI Response:**
    1.  Receives `RespPay` XML asynchronously at `NpciResponseController.respPay`.
    2.  Updates `DB[txn_info]` with final status (SUCCESS/FAILURE) and RRN.
    3.  Sends callback to OCIL Gateway.

## Active APIs (Kibana Verified)

| Service | API URL | Hits (3d) | Controller |
|---------|---------|-----------|------------|
| TSP | `/upi/ext/txn/tsp/lite/v1/app-pay` | 38,132,446 | `UPILiteController` |
| TSP | `/upi/ext/txn/tsp/lite/v2/sync` | 11,257,036 | `UPILiteController` |
| TSP | `/upi/ext/txn/tsp/lite/v1/topup` | 9,363,665 | `UPILiteController` |
| TSP | `/upi/ext/txn/tsp/lite/v3/sync/check-status` | 1,743,962 | `UPILiteController` |
| TSP | `/upi/ext/txn/tsp/lite/v1/deregister` | 585,486 | `UPILiteController` |

## DB Write Points

| Step | Service | Table | Operation | Fields |
|------|---------|-------|-----------|--------|
| Entry | TPAP | `txn_info` | INSERT | status=PENDING, txn_id |
| Entry | TPAP | `txn_participants` | INSERT | payer_vpa, payee_vpa |
| Forward| TSP | `txn_info` | INSERT | status=PENDING |
| ACK | TSP | `txn_phases` | INSERT | phase=REQPAY_ACK |
| Result | TSP | `txn_info` | UPDATE | status, rrn, npci_resp_code |

## Key Logs for Tracing

### TPAP Switch
- `Lite App Pay Response { ... }` - Printed after processing entry request.
- `Validation status for app common pay: true` - Validation result.

### TSP Switch
- `Npci req Pay Request <XML>` - The actual XML sent to NPCI.
- `NPCI Ack received : <XML>` - Immediate acknowledgment from NPCI.
- `NPCI RespPay callback received` - Async result from NPCI.

## Kibana Links
- [TSP Lite Pay Traffic (3d)](https://kibana.paytmybl.com/app/discover#/?_g=(filters:!(),time:(from:'now-3d',to:'now'))&_a=(columns:!('@timestamp',log.message,log.loggerName),dataSource:(dataViewId:'7a188ab3-b1a9-4e8b-9d99-49bfd718cc38',type:dataView),filters:!(),interval:auto,query:(language:kuery,query:'%2Fupi%2Fext%2Ftxn%2Ftsp%2Flite%2Fv1%2Fapp-pay'),sort:!(!('@timestamp',asc))))

## Grafana Proof
- Dashboard: **UPI War Room** (`DNTezbS7z`)
- Panel: **Traffic DC/DR (txn)** shows overall volume including Lite.
