# tsp DB Schema

## Sharding

tsp switchv2 is sharded across 4 clusters. Always query all shards unless user specifies one.

| Shard | Redash data_source_id |
|-------|----------------------|
| switchv2_C1 | 22 |
| switchv2_C2 | 21 |
| switchv2_C3 | 19 |
| switchv2_C6 | 14 |
| Config_UPI_Jobs | 16 (non-sharded) |

---

## DB: switchv2 (all shards)

---

### switchv2.txn_info

Core transaction table. Every payment/collect/refund creates a row here.

#### Columns

| Column | Type | Notes |
|--------|------|-------|
| `id` | bigint | PK, auto_increment |
| `txn_id` | varchar | Primary business identifier |
| `note` | varchar | User-provided payment note |
| `ref_id` | varchar | External reference ID |
| `ref_url` | varchar | External reference URL |
| `rrn` | varchar | RRN from NPCI — use for reconciliation |
| `category` | varchar | Business category (e.g. VPA2VPA) |
| `org_txn_id` | varchar | Original txn ID (for refunds/reversals) |
| `type` | varchar | PAY / COLLECT / REFUND etc. |
| `business_type` | varchar | e.g. P2P, P2M |
| `first_phase` | varchar | Initiation phase outcome |
| `npci_resp_code` | varchar | Raw NPCI response code |
| `status` | varchar | SUCCESS / FAILURE / PENDING |
| `amount` | decimal(10,2) | Transaction amount |
| `payment_aggregator` | varchar | Aggregator routing this txn |
| `expire_after` | int | TTL in seconds from creation |
| `mid` | varchar | Merchant ID |
| `order_id` | varchar | Merchant/platform order reference |
| `npci_ts` | timestamp(3) | NPCI-reported timestamp |
| `created_on` | timestamp(3) | Row creation time |
| `expire_on` | datetime | Absolute expiry datetime |
| `updated_on` | timestamp(3) | Auto-updated on any change |
| `extended_info` | json | Flexible payload — varies by flow |
| `application_updated_on` | timestamp(3) | App-layer explicit update time |
| `txn_mode` | varchar | QR / INTENT / COLLECT etc. |
| `channel_code` | varchar | Channel (mobile, web, etc.) |
| `app_resp_code` | varchar | App-level response code |
| `ext_ref_id` | varchar | Extended external reference |
| `umn` | varchar | UPI mandate number (collect flows) |
| `settlement_type` | varchar | Settlement category |
| `version` | smallint | Optimistic lock version |

---

### switchv2.txn_participants

| Column | Type | Notes |
|--------|------|-------|
| `id` | bigint | PK |
| `txn_id` | varchar | FK → txn_info.txn_id |
| `participant_type` | varchar | PAYER / PAYEE |
| `name` | varchar | Account holder name |
| `vpa` | varchar | UPI VPA |
| `mobile_no` | bigint | |
| `user_id` | bigint | Internal user ID |
| `scope_cust_id` | varchar | Scope customer ID |
| `bank_code` | varchar | e.g. PUNB, SBIN |
| `handle` | varchar | UPI handle |
| `account_type` | varchar | SAVINGS / CURRENT |
| `address_type` | varchar | ACCOUNT / VPA |
| `detail_1` | varchar | Encrypted account number |
| `detail_2` | varchar | IFSC code |
| `resp_code` | varchar | 00 = success |
| `reversal_resp_code` | varchar | |
| `mcc` | varchar | Merchant category code |
| `amount` | decimal(10,2) | |
| `country_code` | bigint | |
| `system_timestamp` | datetime | |
| `created_on` | timestamp(3) | |
| `updated_on` | timestamp(3) | |
| `extended_info` | json | hashed_account_number etc. |
| `request_metadata` | json | |
| `version` | smallint | |

---

## Common Debug Queries

```sql
-- Full lookup by txn_id — run as two separate queries (no JOINs)
-- Query 1:
SELECT * FROM txn_info WHERE txn_id = '<txn_id>';
-- Query 2:
SELECT * FROM txn_participants WHERE txn_id = '<txn_id>';

-- Full lookup by RRN — run as two separate queries
-- Query 1: get txn_id
SELECT txn_id FROM txn_info WHERE rrn = '<rrn>' LIMIT 10;
-- Query 2: use txn_id from above
SELECT * FROM txn_participants WHERE txn_id = '<txn_id_from_above>';

-- Recent failures
SELECT txn_id, status, app_resp_code, npci_resp_code, amount, created_on
FROM txn_info
WHERE status = 'FAILURE'
  AND created_on >= NOW() - INTERVAL 1 HOUR
ORDER BY created_on DESC LIMIT 100;

-- Pending past expiry
SELECT txn_id, status, expire_on, created_on
FROM txn_info
WHERE status = 'PENDING' AND expire_on < NOW()
ORDER BY expire_on ASC LIMIT 50;

-- Error code distribution (last 1h)
SELECT app_resp_code, npci_resp_code, COUNT(*) AS cnt
FROM txn_info
WHERE created_on >= NOW() - INTERVAL 1 HOUR AND status = 'FAILURE'
GROUP BY app_resp_code, npci_resp_code
ORDER BY cnt DESC;

-- Refund/reversal chain
SELECT txn_id, type, status, amount, org_txn_id, created_on
FROM txn_info
WHERE org_txn_id = '<original_txn_id>'
ORDER BY created_on ASC;
```

> **Sharding note**: All queries above fan-out to all 4 shards (C1/C2/C3/C6) unless user specifies a shard.
> **Config_UPI_Jobs**: non-sharded, specify `db_name = "Config_UPI_Jobs"` explicitly.

---

## DB: Config_UPI_Jobs

---

### Config_UPI_Jobs.application_properties

| Column | Type | Notes |
|--------|------|-------|
| `id` | bigint | PK |
| `name` | varchar | Property key (UNIQUE) |
| `value` | varchar | Property value |
| `rules` | json | Conditional rules |
| `created_by` | varchar | |
| `created_on` | timestamp(3) | |
| `updated_on` | timestamp(3) | |

---

### Config_UPI_Jobs.business_properties

| Column | Type | Notes |
|--------|------|-------|
| `id` | bigint | PK |
| `name` | varchar | Property key (UNIQUE) |
| `value` | varchar | Property value |
| `rules` | json | Conditional rules |
| `created_by` | varchar | |
| `created_on` | timestamp(3) | |
| `updated_on` | timestamp(3) | |
