# tpap DB Schema

## DB: switchv2

---

### switchv2.txn_info

Core transaction table. Every payment/collect/refund creates a row here.

#### DDL

```sql
CREATE TABLE `txn_info` (
  `id`                       bigint NOT NULL AUTO_INCREMENT,
  `txn_id`                   varchar(50) NOT NULL,
  `note`                     varchar(100) DEFAULT NULL,
  `ref_id`                   varchar(50) DEFAULT NULL,
  `ref_url`                  varchar(255) DEFAULT NULL,
  `rrn`                      varchar(20) DEFAULT NULL,
  `category`                 varchar(20) DEFAULT NULL,
  `org_txn_id`               varchar(50) DEFAULT NULL,
  `type`                     varchar(20) NOT NULL,
  `business_type`            varchar(50) DEFAULT NULL,
  `first_phase`              varchar(50) NOT NULL,
  `npci_resp_code`           varchar(50) DEFAULT NULL,
  `status`                   varchar(20) DEFAULT NULL,
  `amount`                   decimal(10,2) DEFAULT NULL,
  `payment_aggregator`       varchar(50) DEFAULT NULL,
  `expire_after`             int DEFAULT NULL,
  `mid`                      varchar(50) DEFAULT NULL,
  `order_id`                 varchar(50) DEFAULT NULL,
  `npci_ts`                  timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `created_on`               timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `expire_on`                datetime DEFAULT NULL,
  `updated_on`               timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  `extended_info`            json DEFAULT NULL,
  `application_updated_on`   timestamp(3) NULL DEFAULT NULL,
  `txn_mode`                 varchar(50) DEFAULT NULL,
  `channel_code`             varchar(100) DEFAULT NULL,
  `app_resp_code`            varchar(50) DEFAULT NULL,
  `ext_ref_id`               varchar(100) DEFAULT NULL,
  `umn`                      varchar(100) DEFAULT NULL,
  `settlement_type`          varchar(20) DEFAULT NULL,
  `version`                  smallint DEFAULT '0',
  `psp_ts`                   timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `psp_handle`               varchar(20) DEFAULT NULL,
  `purpose`                  varchar(20) DEFAULT NULL,
  `initiation_mode`          varchar(20) DEFAULT NULL,
  `future_column1`           varchar(20) DEFAULT NULL,
  `future_column2`           varchar(20) DEFAULT NULL,
  `future_column3`           varchar(50) DEFAULT NULL,
  `future_column4`           varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `txn_id` (`txn_id`),
  UNIQUE KEY `uq_txn_info_order_id` (`order_id`),
  KEY `idx_txn_info_created_on` (`created_on`),
  KEY `idx_txn_info_updated_on` (`updated_on`),
  KEY `idx_txn_info_rrn` (`rrn`),
  KEY `idx_status_category_updated_on` (`status`, `category`, `updated_on`),
  KEY `idx_txn_info_type` (`type`),
  KEY `idx_to_app_resp_code` (`app_resp_code`),
  KEY `idx_org_txn_id` (`org_txn_id`),
  KEY `idx_txn_info_business_type_updated_on` (`business_type`, `updated_on`),
  KEY `idx_expire_on` (`expire_on`),
  KEY `idx_txn_info_umn` (`umn`),
  KEY `idx_psp_handle` (`psp_handle`),
  KEY `idx_txn_info_mid` (`mid`)
) ENGINE=InnoDB AUTO_INCREMENT=42308899113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

#### Columns

| Column | Type | Key | Notes |
|--------|------|-----|-------|
| `id` | bigint | PK, AI | Internal row ID |
| `txn_id` | varchar(50) | UNIQUE | Primary business identifier |
| `order_id` | varchar(50) | UNIQUE | Merchant/platform order reference |
| `rrn` | varchar(20) | IDX | RRN from NPCI — use for reconciliation |
| `org_txn_id` | varchar(50) | IDX | Original txn ID (for refunds/reversals) |
| `umn` | varchar(100) | IDX | UPI mandate number (collect flows) |
| `mid` | varchar(50) | IDX | Merchant ID |
| `type` | varchar(20) | IDX | PAY / COLLECT / REFUND etc. |
| `category` | varchar(20) | — | Business category |
| `business_type` | varchar(50) | IDX | e.g. P2P, P2M |
| `status` | varchar(20) | IDX | SUCCESS / FAILURE / PENDING |
| `first_phase` | varchar(50) | — | Initiation phase outcome |
| `amount` | decimal(10,2) | — | Transaction amount |
| `npci_resp_code` | varchar(50) | — | Raw NPCI response code |
| `app_resp_code` | varchar(50) | IDX | App-level response code |
| `payment_aggregator` | varchar(50) | — | Aggregator routing this txn |
| `psp_handle` | varchar(20) | IDX | PSP VPA handle |
| `txn_mode` | varchar(50) | — | QR / INTENT / COLLECT etc. |
| `channel_code` | varchar(100) | — | Channel (mobile, web, etc.) |
| `initiation_mode` | varchar(20) | — | UPI initiation mode code |
| `purpose` | varchar(20) | — | UPI purpose code |
| `settlement_type` | varchar(20) | — | Settlement category |
| `expire_after` | int | — | TTL in seconds from creation |
| `expire_on` | datetime | IDX | Absolute expiry datetime |
| `npci_ts` | timestamp(3) | — | NPCI-reported timestamp |
| `psp_ts` | timestamp(3) | — | PSP-reported timestamp |
| `created_on` | timestamp(3) | IDX | Row creation time |
| `updated_on` | timestamp(3) | IDX | Auto-updated on any change |
| `application_updated_on` | timestamp(3) | — | App-layer explicit update time |
| `extended_info` | json | — | Flexible payload — varies by flow |
| `version` | smallint | — | Optimistic lock version |
| `ref_id` / `ref_url` | varchar | — | External reference ID and URL |
| `ext_ref_id` | varchar(100) | — | Extended external reference |
| `note` | varchar(100) | — | User-provided payment note |
| `future_column1–4` | varchar | — | Reserved for future use |

#### Indexes

| Index | Columns | Use case |
|-------|---------|----------|
| PK | `id` | Internal joins |
| `txn_id` (UNIQUE) | `txn_id` | Lookup by business txn ID |
| `uq_txn_info_order_id` (UNIQUE) | `order_id` | Lookup by order |
| `idx_status_category_updated_on` | `status, category, updated_on` | Status polling, batch jobs |
| `idx_txn_info_rrn` | `rrn` | Reconciliation by RRN |
| `idx_org_txn_id` | `org_txn_id` | Refund/reversal chain lookup |
| `idx_txn_info_umn` | `umn` | Mandate-linked txn lookup |
| `idx_txn_info_mid` | `mid` | Merchant-scoped queries |
| `idx_psp_handle` | `psp_handle` | PSP-scoped debugging |
| `idx_txn_info_business_type_updated_on` | `business_type, updated_on` | Type + time range scans |
| `idx_expire_on` | `expire_on` | Expiry sweeper jobs |
| `idx_to_app_resp_code` | `app_resp_code` | Error code analysis |

#### Common Debug Queries

```sql
-- Full lookup by txn_id — run as two separate queries
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

---

### switchv2.txn_participants

| Column | Type | Key | Notes |
|--------|------|-----|-------|
| `id` | bigint | PK | auto_increment |
| `txn_id` | varchar(50) | IDX | FK → txn_info.txn_id |
| `participant_type` | varchar(10) | — | PAYER / PAYEE |
| `name` | varchar(100) | — | Account holder name |
| `vpa` | varchar(100) | IDX | UPI VPA |
| `mobile_no` | bigint | IDX | |
| `user_id` | bigint | IDX | Internal user ID |
| `scope_cust_id` | varchar(50) | — | Scope customer ID |
| `bank_code` | varchar(10) | — | e.g. PUNB, SBIN |
| `bank_iin` | varchar(100) | — | |
| `handle` | varchar(50) | — | UPI handle e.g. ptyes |
| `psp_handle` | varchar(20) | — | |
| `psp_bank_unique_id` | varchar(100) | — | |
| `account_type` | varchar(50) | — | SAVINGS / CURRENT |
| `address_type` | varchar(50) | — | ACCOUNT / VPA |
| `detail_1` | varchar(100) | IDX | Encrypted account number |
| `detail_2` | varchar(20) | — | IFSC code |
| `masked_account_number` | varchar(100) | — | Encrypted |
| `acc_ref_id` | varchar(100) | — | Account ref ID |
| `resp_code` | varchar(50) | — | 00 = success |
| `reversal_resp_code` | varchar(50) | — | |
| `mcc` | varchar(10) | — | Merchant category code |
| `amount` | decimal(10,2) | — | |
| `country_code` | bigint | — | |
| `system_timestamp` | datetime | PK | |
| `created_on` | timestamp(3) | IDX | |
| `updated_on` | timestamp(3) | IDX | |
| `extended_info` | json | — | hashed_account_number etc. |

---

### switchv2.complaint_info

| Column | Type | Key | Notes |
|--------|------|-----|-------|
| `id` | bigint | PK | auto_increment |
| `crn` | varchar(40) | UNIQUE | Complaint ref number |
| `complaint_txn_id` | varchar(50) | UNIQUE | Txn ID of complaint txn |
| `org_txn_id` | varchar(50) | IDX | Original txn being disputed |
| `type` | varchar(20) | — | Complaint type |
| `sub_type` | varchar(50) | — | |
| `status` | varchar(20) | IDX | |
| `req_adj_flag` | varchar(50) | — | Requested adjustment flag |
| `req_adj_code` | varchar(50) | — | Requested adjustment code |
| `adj_flag` | varchar(50) | — | Actual adjustment flag |
| `adj_code` | varchar(50) | — | Actual adjustment code |
| `channel` | varchar(20) | — | |
| `cust_id` | varchar(50) | — | Customer ID |
| `psp_handle` | varchar(20) | — | |
| `retry_count` | int | — | |
| `retry_exhausted` | tinyint(1) | — | |
| `next_retry_time` | timestamp(3) | — | |
| `org_txn_date` | timestamp(3) | — | |
| `created_on` | timestamp(3) | IDX | |
| `updated_on` | timestamp(3) | IDX | |
| `extended_info` | json | — | |

---

## DB: upi_config

---

### upi_config.application_properties

| Column | Type | Key | Notes |
|--------|------|-----|-------|
| `id` | bigint | PK | auto_increment |
| `name` | varchar(255) | UNIQUE | Property key |
| `value` | varchar(4000) | — | Property value |
| `rules` | json | — | Conditional rules |
| `created_by` | varchar(50) | — | |
| `created_on` | timestamp(3) | — | |
| `updated_on` | timestamp(3) | IDX | |

---

### upi_config.business_properties

| Column | Type | Key | Notes |
|--------|------|-----|-------|
| `id` | bigint | PK | auto_increment |
| `name` | varchar(255) | UNIQUE | Property key |
| `value` | varchar(2000) | — | Property value |
| `rules` | json | — | Conditional rules |
| `created_by` | varchar(50) | — | |
| `created_on` | timestamp(3) | — | |
| `updated_on` | timestamp(3) | IDX | |
