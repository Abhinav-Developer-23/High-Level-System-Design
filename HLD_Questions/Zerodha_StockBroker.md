# Zerodha Stock Broker — High-Level System Design

---

## What is Zerodha?

> **Zerodha** is India's largest discount stock broker, serving 10M+ active traders on platforms like **Kite** (web/mobile trading app) and **Console** (portfolio analytics). It allows users to buy/sell stocks, derivatives (F&O), commodities, mutual funds, and bonds via NSE and BSE exchanges.

**Key Scale Numbers (Interview Context):**

| Metric | Value |
|---|---|
| Active Users | 10 million+ |
| Daily Orders | 10–15 million |
| Peak Orders/sec | 50,000+ (market open at 9:15 AM) |
| Real-time Price Updates | Every 100ms per instrument |
| Instruments Tracked | ~10,000 (equities + F&O) |
| Uptime SLA | 99.99% during market hours (9:00 AM – 3:30 PM IST) |

---

## Functional Requirements

1. **User Onboarding & Authentication** — KYC, Demat account linking, 2FA login
2. **Order Placement** — Market, Limit, Stop-Loss, CNC, MIS, CO, BO orders
3. **Order Book / Portfolio** — Real-time view of open orders, positions, holdings
4. **Market Data Feed** — Live price ticker for 10,000+ instruments
5. **Trade Execution** — Route orders to NSE/BSE, receive confirmations
6. **Risk Management** — Margin checks, circuit breakers, position limits
7. **Payment & Fund Transfer** — Add funds via UPI/NEFT, withdraw to bank
8. **Reports & Analytics** — P&L, tax reports, trade history

---

## Non-Functional Requirements

| Requirement | Target |
|---|---|
| **Latency** | Order placement < 10ms end-to-end; market data < 100ms |
| **Throughput** | 50,000 orders/sec at peak |
| **Availability** | 99.99% during market hours |
| **Consistency** | Strong consistency for orders/funds; eventual for analytics |
| **Durability** | Zero order loss — every order must be persisted before acknowledgment |
| **Regulatory** | SEBI compliance — full audit trail, 5-year data retention |

---

## System Components Overview

```
           ┌──────────────────────────────────────────────────────┐
           │                   Clients                            │
           │   Kite Web App   │   Kite Mobile   │   Kite API      │
           └────────────────────────┬─────────────────────────────┘
                                    │ HTTPS / WebSocket
                          ┌─────────▼──────────┐
                          │    API Gateway /    │
                          │    Load Balancer    │
                          └──────┬──────┬───────┘
                     ┌───────────┘      └───────────┐
          ┌──────────▼────────┐          ┌──────────▼────────┐
          │   Auth Service    │          │  Market Data Svc   │
          │   (JWT + 2FA)     │          │  (WebSocket Push)  │
          └───────────────────┘          └──────────┬────────┘
                                                    │ Feed
                                         ┌──────────▼──────────┐
          ┌───────────────────┐          │  Market Data        │
          │   Order Service   │          │  Aggregator         │
          │  (OMS — Validate, │          │  (NSE/BSE DMA Feed) │
          │   Risk, Route)    │          └─────────────────────┘
          └────────┬──────────┘
                   │
        ┌──────────▼────────────┐
        │   Kafka Message Bus   │
        └───┬──────────┬────────┘
            │          │
   ┌────────▼──┐  ┌────▼────────────┐
   │  Exchange │  │  Trade Processor │
   │  Gateway  │  │  (Confirmation  │
   │  (FIX 4.4)│  │   + Settlement) │
   └────────────┘  └────────────────┘
```

---

## 1. Authentication & Session Management

### How Login Works

```
User ──▶ API Gateway ──▶ Auth Service ──▶ Redis (Session Store)
              │                │
              │          Validate 2FA (TOTP)
              │                │
              ▼            Issue JWT
          Rate Limiter    (15-min TTL)
```

| Component | Technology | Reason |
|---|---|---|
| **Password Hash** | bcrypt (cost=12) | Resistant to brute force |
| **2FA** | TOTP (Google Authenticator) | SEBI-mandated for brokers |
| **Session Store** | Redis (Cluster mode) | Sub-ms token validation at scale |
| **Token** | JWT (short-lived, 15 min) + Refresh Token (7 days) | Stateless, revocable |
| **Rate Limiting** | Token Bucket per IP | Blocks credential stuffing attacks |

> **Why Redis for sessions?** With 10M users and 50K concurrent sessions at peak open, an SQL session table would be too slow. Redis gives O(1) lookup with TTL-based auto-expiry.

---

## 2. Order Management System (OMS)

> The **OMS** is the most critical component — it accepts, validates, risk-checks, and routes orders to the exchange. Every millisecond here matters.

### Order Types Supported

| Type | Description |
|---|---|
| **Market** | Execute immediately at best available price |
| **Limit** | Execute only at specified price or better |
| **Stop-Loss (SL)** | Trigger a market/limit order when price crosses a threshold |
| **CNC** | Cash-and-Carry — delivery-based equity trade |
| **MIS** | Margin Intraday Square-off — auto squared at 3:20 PM; 3-5× leverage |
| **CO** | Cover Order — market order with mandatory stop-loss |
| **BO** | Bracket Order — entry + target + stop-loss in one |

---

### Order Lifecycle

```
Client Request
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Order Service                            │
│                                                                 │
│  1. Schema Validation  ──▶  2. Auth/Session Check              │
│         │                           │                          │
│         ▼                           ▼                          │
│  3. Idempotency Check  ──▶  4. Risk Engine (Margin Check)      │
│         │                           │                          │
│         ▼                           ▼                          │
│  5. Persist to DB      ──▶  6. Push to Kafka (order.placed)   │
│         │                           │                          │
│         └───────────────────────────┘                          │
│                         │                                       │
│                    7. ACK to Client                             │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Exchange Gateway    │
              │   (FIX 4.4 Protocol) │
              └───────────┬───────────┘
                          │
                  ┌───────▼────────┐
                  │  NSE / BSE     │
                  │  Matching Engine│
                  └───────┬────────┘
                          │ Trade Confirmation
                          ▼
              ┌───────────────────────┐
              │   Trade Processor     │
              │   Update positions    │
              │   Release/use margin  │
              └───────────────────────┘
```

---

### Why Kafka Between OMS and Exchange Gateway?

| Without Kafka | With Kafka |
|---|---|
| OMS directly calls Exchange Gateway — tight coupling | Decoupled — OMS publishes, Gateway consumes |
| If Gateway is slow, OMS blocks | Gateway can consume at its own pace |
| No replay on failure | Kafka retains messages — full replay on crash |
| Single point of failure | Multiple consumers possible (audit, analytics) |

> **Order events flow through multiple Kafka topics:** `order.placed`, `order.cancelled`, `order.executed`, `order.rejected`, `order.modified`

---

### Idempotency in Order Placement

> **Problem:** Client sends order, network drops, client retries → duplicate order placed.

**Solution:** Each order request carries a client-generated `client_order_id` (UUID). The OMS checks this against a Redis `SET` before processing:

```
SETNX order:idempotency:<client_order_id> "1" EX 300
```

- If `SETNX` returns `1` → new order, proceed.
- If `SETNX` returns `0` → duplicate, return cached response.

TTL of 5 minutes covers network retry windows without permanent storage bloat.

---

## 3. Risk Management Engine

> **Before any order is routed to the exchange, the Risk Engine must approve it.** This is a hard gate — no bypass, no async check.

### Checks Performed

```
Incoming Order
      │
      ├──▶ 1. Available Margin Check
      │        Is free_margin ≥ required_margin?
      │
      ├──▶ 2. Position Limit Check
      │        Does this order breach SEBI's per-client position limit?
      │
      ├──▶ 3. Price Band Check
      │        Is limit price within circuit breaker bands (±20%)?
      │
      ├──▶ 4. Order Value Check
      │        Is order_qty × price under the per-order cap?
      │
      └──▶ 5. Exposure Check (F&O)
               Is total F&O exposure within allowed leverage limits?
```

### Margin Ledger

| Component | Technology | Why |
|---|---|---|
| **Margin Store** | Redis (Hash per user) | Sub-millisecond read/write for margin balance |
| **Locks** | Redis `WATCH` + `MULTI/EXEC` (optimistic) | Prevent double-spend when concurrent orders arrive |
| **Persistent Copy** | PostgreSQL | Source of truth; Redis is the hot cache |
| **Sync** | Write-through: update both Redis and Postgres on every settlement | Consistency guarantee |

> **Why Redis for margin, not Postgres directly?**
> The risk check is on the **critical latency path** — adding even a 5ms SQL query here would violate the <10ms SLA. Redis gives <1ms reads. Postgres is the durable source of truth; Redis is the fast gate.

---

### Auto Square-off (MIS Orders)

MIS positions are auto-closed at **3:20 PM IST** to prevent overnight holding (since MIS uses leverage):

```
3:20 PM Cron ──▶ Fetch all open MIS positions ──▶
    For each position, place a Market Order (reverse) ──▶
        Route through OMS (bypass manual risk check, use system user) ──▶
            Exchange ──▶ Confirmation ──▶ Update P&L
```

> The square-off service uses a Kafka topic `squareoff.trigger` to fan out work across multiple workers in parallel, handling thousands of positions simultaneously.

---

## 4. Market Data Feed Service

> Zerodha receives a **raw DMA (Direct Market Access) feed** from NSE/BSE tick-by-tick. This must be processed, normalized, and pushed to 10M clients with <100ms latency.

### Architecture

```
NSE/BSE
Tick Feed ──▶ Feed Handler ──▶ Kafka (market.ticks) ──▶ Aggregator
  (UDP multicast)    (normalizer)                          │
                                                           ▼
                                              ┌────────────────────────┐
                                              │  Redis Pub/Sub         │
                                              │  (per instrument topic)│
                                              └────────────┬───────────┘
                                                           │
                                              ┌────────────▼───────────┐
                                              │  WebSocket Servers     │
                                              │  (horizontal scale)    │
                                              └────────────┬───────────┘
                                                           │ Push ~100ms
                                              ┌────────────▼───────────┐
                                              │  Kite Web / Mobile     │
                                              └────────────────────────┘
```

### Feed Processing Pipeline

| Stage | Component | Details |
|---|---|---|
| **Ingest** | Feed Handler (C++ process) | Receives UDP multicast; ultra-low latency |
| **Normalize** | Kafka Consumer (Go service) | Parse binary FIX/ITCH format → JSON/Protobuf |
| **Distribute** | Redis Pub/Sub | Fan-out to all WebSocket servers |
| **Deliver** | WebSocket Server (Node.js) | Each server holds ~50K connections |
| **Client** | Kite WebSocket client | Reconnect + heartbeat logic |

> **Why Redis Pub/Sub (not Kafka) for last-mile delivery?**
> Kafka is great for durable fan-out, but there's no concept of "subscribe to a specific instrument channel." Redis Pub/Sub gives per-instrument channel semantics and sub-millisecond publish latency. The trade-off is no persistence — if a client misses a tick, it's lost. That's acceptable for a price feed (next tick arrives in ~100ms anyway).

---

### WebSocket Connection Management

With 10M users, not all are simultaneously connected:

| Time | Concurrent WebSocket Connections |
|---|---|
| Pre-market (8:00–9:15 AM) | ~500K |
| Market open (9:15 AM) | ~2–3M |
| Mid-day (1 PM) | ~1M |
| Market close (3:30 PM) | ~500K |

**Scaling Strategy:**
- Each WebSocket server handles ~50K connections (Node.js event loop)
- 60 WebSocket servers needed at peak (3M / 50K)
- Nginx load balancer with `ip_hash` (sticky sessions — user always hits same WS server)
- Horizontal auto-scaling based on connection count metric (via Kubernetes HPA)

---

## 5. Exchange Gateway (FIX Protocol)

> The Exchange Gateway translates internal order representations into **FIX 4.4 protocol** messages sent to NSE/BSE via dedicated leased lines.

### What is FIX Protocol?

**FIX (Financial Information eXchange)** is the industry-standard messaging protocol for securities trading. All brokers must communicate with exchanges using FIX.

```
FIX Order Message (New Order - Single):
  Tag 35 = D         → MsgType = New Order
  Tag 49 = ZERODHA   → SenderCompID
  Tag 11 = <order_id> → ClOrdID (client order ID)
  Tag 55 = RELIANCE  → Symbol
  Tag 54 = 1         → Side (1=Buy, 2=Sell)
  Tag 38 = 100       → OrderQty
  Tag 40 = 2         → OrdType (1=Market, 2=Limit)
  Tag 44 = 2500.00   → Price
  Tag 60 = <timestamp> → TransactTime
```

### Gateway Design

| Concern | Solution |
|---|---|
| **Connection** | Persistent TCP connection (FIX session) with sequence numbers |
| **Sequencing** | Every FIX message has a `SeqNum`. Gap = disconnection = must resend |
| **Heartbeat** | `Heartbeat (35=0)` every 30s to detect dead connections |
| **Failover** | Primary + Secondary gateway; auto-switch on disconnect |
| **Rate Limit** | NSE enforces order rate limits (~1000 orders/sec per TM ID) |

---

## 6. Database Design

### Core Tables

#### `users`
```sql
user_id        UUID        PRIMARY KEY
email          VARCHAR     UNIQUE NOT NULL
phone          VARCHAR     UNIQUE NOT NULL
pan            VARCHAR     UNIQUE NOT NULL   -- KYC
demat_account  VARCHAR     NOT NULL
created_at     TIMESTAMP
kyc_status     ENUM('pending','approved','rejected')
```

#### `orders`
```sql
order_id          UUID         PRIMARY KEY
client_order_id   VARCHAR      UNIQUE NOT NULL   -- idempotency key
user_id           UUID         FK → users
instrument_token  INT          NOT NULL           -- NSE symbol token
order_type        ENUM('market','limit','sl','sl-m')
product_type      ENUM('CNC','MIS','NRML','CO','BO')
transaction_type  ENUM('BUY','SELL')
quantity          INT          NOT NULL
price             DECIMAL(10,2)
trigger_price     DECIMAL(10,2)
status            ENUM('open','complete','cancelled','rejected')
exchange_order_id VARCHAR                          -- assigned by NSE/BSE
placed_at         TIMESTAMP    NOT NULL
executed_at       TIMESTAMP
```

#### `positions`
```sql
position_id       UUID         PRIMARY KEY
user_id           UUID         FK → users
instrument_token  INT
product_type      ENUM('CNC','MIS','NRML')
quantity          INT          -- positive=long, negative=short
average_price     DECIMAL(10,2)
pnl               DECIMAL(12,2)
last_updated      TIMESTAMP
```

#### `margin_ledger`
```sql
ledger_id     UUID       PRIMARY KEY
user_id       UUID       FK → users
type          ENUM('credit','debit')
amount        DECIMAL(12,2)
reason        VARCHAR    -- 'order_block','trade_settlement','fund_add'
order_id      UUID       FK → orders (nullable)
created_at    TIMESTAMP
```

### Database Technology Choices

| Data | Database | Reason |
|---|---|---|
| Users, KYC | **PostgreSQL** | Strong ACID, UNIQUE constraints for PAN/demat |
| Orders | **PostgreSQL** | ACID critical — no order loss tolerated |
| Positions (hot) | **Redis Hash** + PostgreSQL | Redis for sub-ms reads; PG for durability |
| Market Ticks | **TimescaleDB / InfluxDB** | Time-series optimized; fast range queries for charts |
| Trade History | **Amazon S3 + Parquet** | Cheap, queryable with Athena for regulatory reporting |
| Search (instruments) | **Elasticsearch** | Full-text search for symbol lookup ("Reliance", "RELI…") |

---

## 7. Fund Transfer & Payment Flow

```
User Clicks "Add Funds"
        │
        ▼
    Payment Service
        │
        ├──▶ UPI (via Razorpay/PayU gateway)
        │         │ webhook on success
        │         ▼
        │    Idempotent Fund Credit
        │    + Update margin_ledger (PostgreSQL)
        │    + Update Redis margin cache
        │
        └──▶ NEFT/IMPS (bank transfer)
                  │ Reconciliation job (nightly)
                  ▼
             Match bank statement → Credit account
```

> **Idempotency is critical here:** UPI webhooks can be delivered multiple times. Each payment has a `payment_reference_id`; the service checks `INSERT ... ON CONFLICT DO NOTHING` to prevent double-crediting.

---

## 8. Notifications & Alerts

| Event | Channel | Latency Requirement |
|---|---|---|
| Order placed | In-app, WebSocket | < 500ms |
| Trade executed | In-app, SMS, Email | < 2s |
| Margin call warning | SMS + Push notification | < 5s |
| Auto square-off triggered | SMS + Email | < 30s |
| Fund credit | In-app, SMS | < 5s |

**Architecture:** Kafka → Notification Service → (FCM for push / SNS for SMS / SES for email)

All notification sends are **at-least-once** (Kafka consumer group), and delivery status is tracked in a `notifications` table for deduplication.

---

## 9. Handling Peak Load (9:15 AM Market Open)

> The most challenging moment is **9:15:00 AM** — thousands of pre-placed orders fire simultaneously, the market data feed surges, and millions of clients reconnect.

### Strategies

| Problem | Strategy |
|---|---|
| **Order surge** | Kafka buffers the spike; OMS processes at its own throughput rate |
| **DB write surge** | Batch inserts into Postgres using COPY command; write-ahead log |
| **Market data surge** | WebSocket servers pre-warm connections at 9:00 AM |
| **Redis hotspot** | Consistent hashing across Redis Cluster — no single-node bottleneck |
| **Auto-scaling** | Kubernetes HPA scales OMS replicas based on Kafka consumer lag |

### Pre-market Window (9:00–9:15 AM)

Orders placed in this window go to a **Pre-Open Session** with special rules:
- Price discovery via call auction (not continuous matching)
- Orders accepted but not executed until 9:15 AM
- Final equilibrium price determined based on demand/supply

These pre-open orders are stored with `status = 'pre-open'` and bulk-submitted to the exchange at 9:08 AM.

---

## 10. SEBI Compliance & Audit Trail

> All actions must be logged with timestamps and stored for **5 years** (SEBI regulation).

### Audit Log Design

Every significant action writes to an immutable audit log:

```
audit_id      UUID          PRIMARY KEY
entity_type   VARCHAR       -- 'order', 'user', 'fund', 'margin'
entity_id     UUID
action        VARCHAR       -- 'created', 'modified', 'cancelled', 'executed'
actor         VARCHAR       -- user_id or 'system'
old_state     JSONB
new_state     JSONB
ip_address    INET
timestamp     TIMESTAMP     NOT NULL
```

**Storage:** Audit logs are streamed via Kafka → S3 (Parquet format, partitioned by date). Queryable via AWS Athena for regulatory investigations.

> **Why not write directly to S3?** Kafka provides buffering, ordering guarantee per partition, and replayability. S3 writes are batched (every 10 minutes) for efficiency, not on each event.

---

## 11. High Availability & Disaster Recovery

| Component | HA Strategy |
|---|---|
| **PostgreSQL** | Primary + 2 Read Replicas; auto-failover via Patroni |
| **Redis** | Redis Cluster (6 nodes: 3 primary + 3 replica) |
| **Kafka** | 3-node cluster; replication factor = 3; `min.insync.replicas = 2` |
| **Exchange Gateway** | Active-Passive; automatic failover on disconnect |
| **WebSocket Servers** | Stateless; Nginx reconnects client to any server |
| **OMS** | 5+ replicas behind load balancer; Kubernetes restarts on crash |
| **Data Center** | Multi-AZ deployment (Mumbai region primary; DR in Hyderabad) |

---

## 12. Key Design Decisions & Trade-offs

### Strong Consistency for Orders vs. Eventual for Analytics

| Operation | Consistency | Reason |
|---|---|---|
| Order placement | **Strong (synchronous DB write)** | Can't lose an order — regulatory and financial liability |
| Margin check | **Strong (Redis WATCH)** | Can't allow double-spend |
| Portfolio P&L calculation | **Eventual** | Slight staleness is acceptable for reporting |
| Market data feed | **Best-effort** | Missed tick is fine — next arrives in 100ms |

---

### Why Not a Microservices-per-Feature Architecture?

Zerodha uses **bounded microservices** — not one service per feature, but services grouped by domain:

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Auth Svc   │  │  Order Svc  │  │ Market Data │  │ Payment Svc │
│             │  │  + Risk     │  │  + Feed     │  │             │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

> Splitting Order and Risk into separate services would add a network hop on the critical order path. They're co-located to keep latency minimal.

---

## Summary: Technology Stack

| Component | Technology |
|---|---|
| **API Gateway** | Nginx / Kong |
| **Backend Services** | Go (OMS, Risk, Feed), Python (Analytics), Node.js (WebSocket) |
| **Message Bus** | Apache Kafka |
| **Primary DB** | PostgreSQL (with Patroni for HA) |
| **Cache / Session** | Redis Cluster |
| **Time-Series DB** | TimescaleDB (charts), InfluxDB (metrics) |
| **Search** | Elasticsearch |
| **Object Storage** | AWS S3 |
| **Audit / Analytics** | S3 + AWS Athena |
| **Exchange Protocol** | FIX 4.4 over leased line |
| **Container Orchestration** | Kubernetes (EKS) |
| **CDN** | Cloudflare |
| **Monitoring** | Prometheus + Grafana; PagerDuty for alerts |

---

## Common Interview Follow-up Questions

#### Q: How do you prevent overselling (selling more shares than held)?

**A:** The Risk Engine checks `available_quantity` (from Redis, sourced from Postgres holdings) before every sell order. It uses an **optimistic lock** (`WATCH + MULTI/EXEC` in Redis) to atomically decrement the quantity only if the check passes. If a concurrent order races, the transaction is retried.

---

#### Q: What happens if Kafka goes down?

**A:** Kafka is deployed as a 3-broker cluster with `replication.factor=3` and `min.insync.replicas=2`. The cluster tolerates one broker failure with no data loss. If all brokers are unavailable (extremely rare), the OMS falls back to **synchronous DB writes** — it writes directly to Postgres and an internal in-memory queue, which replays to Kafka once it recovers.

---

#### Q: How do you handle the 9:15 AM thundering herd?

**A:** Three mechanisms:
1. **Kafka absorbs the burst** — OMS publishes to Kafka; downstream services process at capacity.
2. **Pre-warm resources** — Redis connections, DB connection pools, and WebSocket servers are pre-scaled before 9:15 AM.
3. **Rate limiting at gateway** — API Gateway enforces per-user order rate limits to prevent runaway bots from flooding the system.

---

#### Q: How is market data latency kept under 100ms?

**A:** The feed handler is written in **C++** and reads the NSE UDP multicast feed with kernel-bypass networking (DPDK). The tick is published to Kafka, consumed by a Go normalizer, pushed to Redis Pub/Sub, and delivered via existing WebSocket connections. Each hop adds ~1–5ms. Total end-to-end is typically **20–50ms**.

---

#### Q: How do you reconcile positions end-of-day?

**A:** NSE/BSE sends a **End-of-Day (EOD) file** with all trade confirmations. A nightly reconciliation job compares this file against Zerodha's Postgres order book. Any discrepancy triggers an alert. Positions and P&L are recomputed from this authoritative EOD file and stored for the next day's opening.
