// Wallet System page: hero, questions, requirements, scale, API, data model.
const { code, table, nl, bl, callout, say, endpoint } = require('../../lib');
const { H2, H3, card, qcard } = require('./ui');

const hero = `
<header class="hero">
  <div class="crumbs">System Design Interviews <span>›</span> Payment &amp; Financial Systems <span>›</span> Digital Wallet</div>
  <h1>Design a Digital Wallet System</h1>
  <p class="sub">Add money, pay, send and withdraw. Every rupee is credited and debited exactly once, the balance never goes negative, and the books always balance, even when servers crash halfway.</p>
  <div class="meta"><span class="tag-red">High Priority</span><span class="tag-amber">● Hard</span><span>⏱ 50 min read</span><span>🔌 7 APIs</span><span>🗄 8 tables</span><span>🧭 13 diagrams</span><span>🔍 13 deep dives</span></div>
  <div class="whatis">
    <div class="wi-text">
      <h4>👛 What is a Digital Wallet?</h4>
      <p>A digital wallet (Paytm Wallet, PhonePe Wallet, Amazon Pay balance, PayPal balance) is an account that <strong>holds money for a user inside our system</strong>. Users load it from a card or bank, spend it at merchants, send it to friends and withdraw it back to their bank.</p>
      <p>The hard part isn't the UI. It's the <strong>money</strong>: two payments hitting the same wallet at the same millisecond, a client that retries a "send ₹500" request, a transfer between two databases where one side crashes, and a bank that says "timeout" after it actually sent the money.</p>
    </div>
    <div class="wmock" aria-hidden="true">
      <div class="wcard"><div class="wl">Wallet balance</div><div class="wb">₹2,450<small>.00</small></div><div class="wsub">Available ₹2,150 · ₹300 on hold</div>
        <div class="wbtns"><span>＋ Add</span><span>↗ Send</span><span>⇩ Withdraw</span></div></div>
      <div class="wtx">
        <div><span class="ic up">＋</span><span class="d">Added from bank card<small>Today, 10:02</small></span><b class="cr">+₹500.00</b></div>
        <div><span class="ic">☕</span><span class="d">Paid to Corner Cafe<small>Today, 09:41</small></span><b>−₹120.00</b></div>
        <div><span class="ic">↗</span><span class="d">Sent to Ravi<small>Yesterday</small></span><b>−₹300.00</b></div>
        <div><span class="ic hold">⏳</span><span class="d">Withdrawal to bank<small>Processing</small></span><b class="hd">₹300.00</b></div>
      </div>
    </div>
  </div>
  <p class="lead" style="margin-top:22px">In this chapter we design the wallet end to end: the ledger, the locking, idempotency, transfers across database shards (and whether that needs <strong>two-phase commit</strong>), and how money moves safely in and out through payment gateways and banks.</p>
  <div class="hard">
    <div><b>🔒 No double spend</b><p>Two debits race for the same ₹500. One conditional UPDATE under a row lock decides.</p></div>
    <div><b>🔁 Exactly-once money</b><p>Idempotency keys stored in the same transaction as the money movement.</p></div>
    <div><b>🧾 Books always balance</b><p>Double-entry ledger: every transaction's debits equal its credits, across shards too.</p></div>
  </div>
</header>`;

const questions = `
<section class="sec">${H2('Questions to Ask the Interviewer', 'Clarifying Questions')}
<div class="cards"><p class="lead">Pin down what money can do, what "never wrong" means, and which systems outside ours touch the money, before drawing anything.</p>
${qcard(1, 'Which money movements are in scope?', 'Each movement has a different counterparty. Wallet-to-wallet moves stay inside our database; add-money and withdraw talk to a payment gateway or bank that can fail, time out or answer late.', 'Add money (top-up) from card / UPI / netbanking, pay a merchant, send to another user (P2P), withdraw to a bank account, and refunds from merchants. Also show balance and transaction history. Credit lines, cashback rules and multi-currency are out of scope.')}
${qcard(2, 'Single currency? How do we store amounts?', 'Multiple currencies bring FX rates and conversion entries. Floating point loses paise (0.1 + 0.2 ≠ 0.3).', 'INR only. Store every amount as an integer number of <strong>paise</strong> (<code>BIGINT</code>): ₹500.00 = <code>50000</code>.')}
${qcard(3, 'What is the expected scale?', 'Decides whether one database is enough or we must shard, and how hot a single wallet can get.', '100M wallets, 20M daily active users, about 50M money movements a day. Festival sales and salary days bring 10× spikes.')}
${qcard(4, 'Can a balance ever go negative?', 'If overdraft is allowed we need credit limits and collections. If not, every debit needs a check that is safe under concurrency. <span class="pill our">our addition</span>', 'Never. No overdraft for users. A debit that would take the balance below zero must fail with <code>INSUFFICIENT_FUNDS</code>.')}
${qcard(5, 'How fresh must the balance be?', 'Tells us which reads can come from replicas or a cache and which must hit the primary.', 'The balance used to approve a debit must be exact. The balance shown on the home screen and the history list may lag by a second or two.')}
${qcard(6, 'Will clients retry requests? What delivery guarantee do we need?', 'Mobile networks drop responses. If "send ₹500" times out, the app retries, and without protection Ravi gets ₹1,000. <span class="pill our">our addition</span>', 'Yes, clients and our own services retry. Every money movement must take effect <strong>exactly once</strong>: at-least-once delivery plus idempotency.')}
${qcard(7, 'How do top-ups and withdrawals reach the outside world?', 'External systems can\'t join our database transaction. A gateway can charge the card and then fail to tell us; a bank transfer can time out and still succeed later.', 'Top-ups go through a payment gateway (PSP) that calls us back with a signed webhook. Withdrawals go through a bank payout API (IMPS / NEFT) that is asynchronous and can stay "pending" for hours.')}
${qcard(8, 'Are there balance and transaction limits?', 'Limits must be checked in the same transaction as the money movement, or two concurrent top-ups can both pass the check. <span class="pill our">our addition</span>', 'Yes, by KYC level (RBI-style prepaid-wallet rules): e.g. a minimum-KYC wallet can hold at most ₹10,000; a full-KYC wallet up to ₹2,00,000. Plus daily and monthly outflow limits.')}
${qcard(9, 'Are there very hot wallets?', 'A big merchant can receive thousands of payments a second. All of them update one balance row, which can become the bottleneck.', 'Yes. Large merchants (food delivery, ticketing) can receive up to ~2,000 payments/s during a sale.')}
${qcard(10, 'What audit and reconciliation do we need?', 'Financial regulators want full history; finance wants our numbers to match the gateway\'s and the bank\'s settlement files every day.', 'Keep an immutable history of every movement for 10 years. Reconcile daily with the payment gateways and banks. Corrections are new entries, never edits.')}
${qcard(11, 'Single region or multi-region?', 'Active-active writes across regions make "no double spend" much harder (two regions could both approve the last ₹500).', 'One active region with a hot standby region for disaster recovery. Committed money must not be lost on failover (RPO = 0 within the region).')}
</div></section>`;

const requirements = `
<section class="sec">${H2('Requirements Gathering', 'Requirements')}
<p class="lead">Before diving into the design, let's outline the functional and non-functional requirements.</p>
${H3('Functional Requirements')}
<div class="cards grid2">
${card(1, 'Wallet & Balance', 'Create a wallet per user (one per user, many per merchant). Show the <strong>available</strong> balance (what can be spent) and amounts <strong>on hold</strong> (e.g. a withdrawal in progress).')}
${card(2, 'Add Money (Credit)', 'Top up from card, UPI or netbanking through a payment gateway. Credit the wallet only after the gateway confirms the payment.')}
${card(3, 'Pay & Send (Debit + Credit)', 'Pay a merchant or send to another user. The sender is debited and the receiver credited <strong>atomically</strong>: both happen or neither does.')}
${card(4, 'Withdraw (Debit)', 'Move money from the wallet to a linked bank account. Funds are reserved immediately and the payout completes asynchronously.')}
${card(5, 'Refunds & Reversals', 'A merchant can refund a payment fully or partly (never more than was paid). Failed withdrawals and failed transfers are reversed automatically.')}
${card(6, 'History & Statements', 'Paginated transaction history and monthly statements, with each entry showing the balance after it.')}
${card(7, 'Limits & KYC', 'Enforce balance caps and daily / monthly limits by KYC level. Freeze a wallet on fraud signals.')}
${card(8, 'Notifications', 'SMS / push for every credit and debit (via the Notification Service from our earlier design).')}
</div>
${H3('Non-Functional Requirements')}
<div class="cards grid2">
${card(1, 'Correctness Above All', 'No lost money, no double spend, no negative balance, no double credit. For every transaction, total debits = total credits. This is the requirement that drives the whole design.')}
${card(2, 'Exactly-Once Effect', 'Any request can be retried any number of times (client retries, service retries, duplicate webhooks) and money moves once.')}
${card(3, 'Strong Consistency for Money', 'The balance check and the debit happen in one ACID transaction. Display-only reads may be slightly stale.')}
${card(4, 'High Availability', '99.99% for pay / send. If we must choose, we reject a payment rather than risk a wrong balance.')}
${card(5, 'Low Latency', 'Wallet-to-wallet pay / send p99 under 300 ms. Top-ups and withdrawals depend on external systems and are asynchronous.')}
${card(6, 'Durability & Auditability', 'A committed transaction survives any single machine failure (RPO = 0). Ledger history is append-only and kept 10 years.')}
${card(7, 'Scalability', 'Handle ~6K money movements/s at peak and grow by adding shards.')}
${card(8, 'Security', 'Strong authentication for debits, encrypted PII and bank details, signed webhooks, least-privilege access to the ledger.')}
</div></section>`;

const scale = `
<section class="sec">${H2('Scale Estimation', 'Scale Estimation')}
<p class="ask">“Would you like me to cover back-of-the-envelope calculations, or focus on the design?”</p>
<h4>Assumptions</h4>
${bl(['<strong>Wallets:</strong> 100M, of which 20M are active daily.', '<strong>Money movements:</strong> 50M a day (payments, transfers, top-ups, withdrawals, refunds).', '<strong>Peak:</strong> 3× the average at daily peak, 10× during a festival sale.', '<strong>Reads:</strong> about 10 balance / history reads per money movement.'])}
<h4>Traffic</h4>
${code('text', `
Money movements    50M / day ÷ 86,400 s                        ≈ 580 / s
  daily peak       × 3                                          ≈ 1.7K / s
  sale peak        × 10                                         ≈ 6K / s
Reads              × 10 of writes                               ≈ 6K / s avg, 60K / s at sale peak
Row writes         per movement: 1 transaction + 2 ledger entries + 2 balance updates
                   + 1 idempotency row + 1 outbox row           ≈ 7 rows
                   6K / s × 7                                   ≈ 42K row writes / s at peak`)}
<h4>Storage</h4>
${code('text', `
Wallets            100M × ~200 B                                ≈ 20 GB
Ledger entries     50M × 2 entries × ~250 B (row + indexes)     ≈ 25 GB / day
Transactions       50M × ~400 B                                 ≈ 20 GB / day
Total              ≈ 45 GB / day                                ≈ 16 TB / year
Kept 10 years      ≈ 160 TB  → last ~13 months hot in MySQL (~18 TB), older partitions archived`)}
<h4>Key insights</h4>
${nl([
  '<strong>Writes are the hard part, not reads:</strong> 42K row writes/s at peak with fsync on every commit is too much for one MySQL primary, and 18 TB of hot data is too big for one box. We <strong>shard by <code>wallet_id</code></strong> (16 shards ≈ 600 transactions/s and ~1.1 TB per shard).',
  '<strong>Sharding creates the real problem:</strong> with 16 shards, ~15 of every 16 P2P transfers have sender and receiver on <em>different</em> databases. That is where two-phase commit vs saga comes in (Deep Dive 4).',
  '<strong>Hot rows:</strong> one wallet row can take only a few hundred to ~1,000 updates/s (each update holds the row lock until commit + fsync). A merchant receiving 2,000 payments/s needs special handling (Deep Dive 8).',
  '<strong>Reads are cheap:</strong> a balance read is a primary-key lookup; history comes from a separate read model.'
])}
</section>`;

const json = (s) => code('json', s);
const api = `
<section class="sec">${H2('API Design', 'API Design')}
<p class="lead">REST APIs used by the apps and merchant integrations. Amounts are integers in paise. Every money-moving <code>POST</code> requires an <code>Idempotency-Key</code> header (a UUID the client generates once per user action and reuses on every retry).</p>
${H3('1. Add Money (Top-up)')}
${endpoint('POST', '/v1/wallets/{walletId}/topups')}
<p>Starts a top-up. The wallet is <strong>not</strong> credited yet; the client completes payment on the gateway's page or UPI app and we credit when the gateway confirms.</p>
<h4>Request</h4>
${json(`
// Headers: Authorization: Bearer <token>, Idempotency-Key: 5f1c2a9e-7d1b-4c3e-9a51-0c2f6e8b1d44
{
  "amountMinor": 50000,          // ₹500.00
  "method": "UPI"                 // CARD | UPI | NETBANKING
}`)}
<h4>Response — 201 Created</h4>
${json(`
{
  "topupId": "tp_01JD8Q3K",
  "status": "PENDING",            // PENDING → SUCCEEDED | FAILED
  "gatewayOrderId": "order_Nx81",  // the client opens the gateway checkout with this
  "expiresAt": "2026-11-18T10:17:00Z"
}`)}
${H3('2. Pay / Send Money (Transfer)')}
${endpoint('POST', '/v1/transfers')}
<p>Moves money from one wallet to another (user → user or user → merchant). Synchronous when both wallets are on the same shard; may return <code>202 PROCESSING</code> for a few hundred milliseconds when they are not.</p>
<h4>Request</h4>
${json(`
// Headers: Authorization, Idempotency-Key, X-Device-Id
{
  "fromWalletId": "w_asha",
  "toWalletId": "w_ravi",
  "amountMinor": 50000,
  "note": "dinner"
}`)}
<h4>Response — 201 Created</h4>
${json(`
{
  "transferId": "tx_01JD8R0P",
  "status": "COMPLETED",          // COMPLETED | PROCESSING | FAILED
  "amountMinor": 50000,
  "balanceAfterMinor": 195000     // sender's balance after the debit
}`)}
<h4>Errors</h4>
${table(['Status', 'Code', 'When'], [
  ['422', '<code>INSUFFICIENT_FUNDS</code>', 'available balance &lt; amount'],
  ['422', '<code>LIMIT_EXCEEDED</code>', 'daily / monthly outflow limit, or the receiver\'s balance cap'],
  ['409', '<code>IDEMPOTENCY_KEY_REUSED</code>', 'same key sent with a different body'],
  ['423', '<code>WALLET_FROZEN</code>', 'either wallet frozen by risk / compliance'],
  ['403', '<code>STEP_UP_REQUIRED</code>', 'amount needs MPIN / OTP; retry with the step-up token'],
])}
${H3('3. Withdraw to Bank')}
${endpoint('POST', '/v1/wallets/{walletId}/withdrawals')}
${json(`
// Request (Idempotency-Key required)
{ "amountMinor": 30000, "bankAccountId": "ba_9921" }

// Response — 202 Accepted: money is reserved now, the bank transfer finishes later
{ "withdrawalId": "wd_01JD8T2C", "status": "PROCESSING" }`)}
${H3('4. Refund a Payment')}
${endpoint('POST', '/v1/transfers/{transferId}/refunds')}
${json(`
// Called by the merchant. Partial refunds allowed; the total can never exceed the payment
{ "amountMinor": 20000, "reason": "item out of stock" }

// Response — 201 Created
{ "refundId": "rf_01JD8V7M", "status": "COMPLETED", "refundedSoFarMinor": 20000 }`)}
${H3('5. Get Balance')}
${endpoint('GET', '/v1/wallets/{walletId}/balance')}
${json(`
{ "balanceMinor": 245000, "heldMinor": 30000, "availableMinor": 215000, "asOf": "2026-11-18T10:05:31Z" }`)}
${H3('6. Transaction History')}
${endpoint('GET', '/v1/wallets/{walletId}/transactions?cursor=…&limit=20')}
${json(`
{
  "items": [
    { "entryId": 88123, "transactionId": "tx_01JD8R0P", "type": "TRANSFER_OUT",
      "amountMinor": -50000, "balanceAfterMinor": 195000, "counterparty": "Ravi", "at": "2026-11-18T10:05:31Z" }
  ],
  "nextCursor": "eyJpZCI6ODgxMjN9"   // keyset pagination on entry id (no OFFSET)
}`)}
${H3('7. Gateway Webhook (internal)')}
${endpoint('POST', '/internal/gateway/webhooks')}
<p>The payment gateway calls this when a top-up payment succeeds or fails. We verify the HMAC signature, then <strong>re-fetch the payment status from the gateway's API</strong> before crediting anything. The same event can arrive several times.</p>
${callout('tip', 'Why amounts in paise, and why an Idempotency-Key on every POST?', 'Integers make every sum exact, and the key lets the server recognise a retry of the same user action and return the first result instead of moving money again (Deep Dive 5).')}
</section>`;

const T = (name, desc, rows) => `<div class="tbl-title"><span class="db-ic">▤</span><code>${name}</code><span class="tbl-desc">${desc}</span></div>` + table(['Column', 'Type', 'Key', 'Notes'], rows);
const c = s => `<code>${s}</code>`;
const model = `
<section class="sec">${H2('Data Model', 'Database Schema')}
<p class="lead">MySQL 8 (InnoDB), sharded by <code>wallet_id</code>. Everything about one wallet (its balance, its ledger entries, its idempotency keys) lives on the <strong>same shard</strong>, so a single-wallet operation is one local ACID transaction.</p>
${H3('1. Why a Ledger and not just a Balance Column?')}
<p>A <strong>double-entry ledger</strong> records every movement as at least two entries: a <strong>debit</strong> from one account and a <strong>credit</strong> to another, of equal amounts. Money is never created or destroyed, only moved. The wallet's <code>balance</code> column is a cached sum of its entries, updated in the same transaction.</p>
${table(['Transaction', 'Account', 'Debit', 'Credit'], [
  ['Asha adds ₹1,000 by UPI', 'gateway_clearing (system)', '₹1,000', ''],
  ['', 'wallet: Asha', '', '₹1,000'],
  ['Asha sends Ravi ₹500', 'wallet: Asha', '₹500', ''],
  ['', 'wallet: Ravi', '', '₹500'],
  ['Ravi withdraws ₹300', 'wallet: Ravi', '₹300', ''],
  ['', 'payout_clearing (system)', '', '₹300'],
], { hl: [2, 3] })}
<p>Every row pair sums to zero. Summing all entries for Asha gives her balance (₹1,000 − ₹500 = ₹500); summing every account in the system always gives zero. That makes errors <strong>detectable</strong> (Deep Dive 12), which a single mutable balance column never is.</p>
${H3('2. Tables (per shard)')}
${T('wallets', 'one row per wallet; also system accounts like gateway_clearing', [
  [c('wallet_id'), c('BIGINT'), '🔑 PK', 'shard is derived from it'],
  [c('owner_id'), c('BIGINT'), 'INDEX', 'user or merchant'],
  [c('type'), c('ENUM'), '', c('USER') + ' · ' + c('MERCHANT') + ' · ' + c('SYSTEM')],
  [c('status'), c('ENUM'), '', c('ACTIVE') + ' · ' + c('FROZEN') + ' · ' + c('CLOSED')],
  [c('kyc_level'), c('ENUM'), '', c('MIN') + ' · ' + c('FULL') + ' (drives the caps)'],
  [c('balance_minor'), c('BIGINT'), 'NOT NULL', 'cached sum of ledger entries, in paise'],
  [c('held_minor'), c('BIGINT'), 'NOT NULL', 'reserved for in-flight withdrawals / transfers'],
  [c('version'), c('BIGINT'), 'NOT NULL', 'bumped on every change (optimistic reads, cache invalidation)'],
  [c('updated_at'), c('TIMESTAMP(6)'), '', ''],
])}
${code('sql', `
-- the database itself refuses a negative balance, even if application code has a bug
ALTER TABLE wallets ADD CONSTRAINT chk_funds
  CHECK (type = 'SYSTEM' OR (held_minor >= 0 AND balance_minor >= held_minor));`)}
${T('transactions', 'one row per money movement (the business event)', [
  [c('txn_id'), c('BIGINT'), '🔑 PK', 'globally unique (Snowflake-style)'],
  [c('type'), c('ENUM'), '', c('TOPUP') + ' · ' + c('TRANSFER') + ' · ' + c('WITHDRAWAL') + ' · ' + c('REFUND') + ' · ' + c('REVERSAL')],
  [c('status'), c('ENUM'), '', c('PENDING') + ' · ' + c('PROCESSING') + ' · ' + c('COMPLETED') + ' · ' + c('FAILED') + ' · ' + c('REVERSED')],
  [c('from_wallet_id'), c('BIGINT'), '', ''],
  [c('to_wallet_id'), c('BIGINT'), '', ''],
  [c('amount_minor'), c('BIGINT'), '', 'always positive'],
  [c('refunded_minor'), c('BIGINT'), '', 'for payments: total refunded so far'],
  [c('external_ref'), c('VARCHAR'), 'UNIQUE', 'gateway payment id / bank reference'],
  [c('created_at'), c('TIMESTAMP(6)'), '', ''],
])}
${T('ledger_entries', 'append-only; never updated or deleted', [
  [c('entry_id'), c('BIGINT'), '🔑 PK', 'auto-increment per shard'],
  [c('txn_id'), c('BIGINT'), 'INDEX', 'which movement'],
  [c('wallet_id'), c('BIGINT'), 'INDEX (wallet_id, entry_id)', 'history query'],
  [c('direction'), c('ENUM'), '', c('DEBIT') + ' · ' + c('CREDIT')],
  [c('amount_minor'), c('BIGINT'), '', '&gt; 0'],
  [c('balance_after_minor'), c('BIGINT'), '', 'running balance (statements, audits)'],
  [c('created_at'), c('TIMESTAMP(6)'), '', 'table partitioned by month'],
])}
${T('idempotency_keys', 'dedups retries; written in the same transaction as the money movement', [
  [c('scope_id'), c('BIGINT'), '🔑 PK (1)', 'the caller: wallet or merchant'],
  [c('idem_key'), c('VARCHAR(64)'), '🔑 PK (2)', 'from the Idempotency-Key header'],
  [c('request_hash'), c('BINARY(32)'), '', 'SHA-256 of the body: same key + different body → 409'],
  [c('txn_id'), c('BIGINT'), '', 'the movement it created'],
  [c('response'), c('JSON'), '', 'stored response, replayed on retry'],
  [c('created_at'), c('TIMESTAMP'), '', 'purged after 7 days'],
])}
${T('transfers', 'cross-shard transfer state machine; lives on the sender\'s shard', [
  [c('txn_id'), c('BIGINT'), '🔑 PK', ''],
  [c('state'), c('ENUM'), '', c('DEBITED') + ' → ' + c('CREDITED') + ' → ' + c('COMPLETED') + ', or ' + c('DEBITED') + ' → ' + c('REVERSED')],
  [c('to_shard'), c('INT'), '', 'where the credit must be applied'],
  [c('attempts'), c('INT'), '', ''],
  [c('next_retry_at'), c('TIMESTAMP'), 'INDEX', 'recovery worker scans this'],
])}
${T('applied_transfers', 'on the receiver\'s shard: "this credit was already applied"', [
  [c('txn_id'), c('BIGINT'), '🔑 PK', 'makes the cross-shard credit idempotent'],
  [c('applied_at'), c('TIMESTAMP'), '', ''],
])}
${T('holds', 'money reserved but not yet moved (withdrawals)', [
  [c('hold_id'), c('BIGINT'), '🔑 PK', ''],
  [c('wallet_id'), c('BIGINT'), 'INDEX', ''],
  [c('txn_id'), c('BIGINT'), 'UNIQUE', ''],
  [c('amount_minor'), c('BIGINT'), '', ''],
  [c('status'), c('ENUM'), '', c('HELD') + ' · ' + c('CAPTURED') + ' · ' + c('RELEASED')],
])}
${T('outbox', 'events written in the same transaction, published to Kafka by a relay', [
  [c('event_id'), c('BIGINT'), '🔑 PK', ''],
  [c('aggregate_id'), c('BIGINT'), '', 'wallet id (Kafka partition key, keeps per-wallet order)'],
  [c('type'), c('VARCHAR'), '', c('WALLET_DEBITED') + ', ' + c('WALLET_CREDITED') + ', …'],
  [c('payload'), c('JSON'), '', ''],
  [c('created_at'), c('TIMESTAMP(6)'), '', ''],
])}
${callout('tip', 'System accounts live on every shard', 'Each shard has its own <code>gateway_clearing</code>, <code>payout_clearing</code> and <code>transfer_clearing</code> rows. A top-up for a wallet on shard 7 debits shard 7\'s <code>gateway_clearing</code>, so it stays a local transaction, and no single system row becomes a global hotspot.')}
${H3('3. Which database, and why?')}
${table(['Data', 'Store', 'Why'], [
  ['Wallets, ledger, transactions, idempotency, outbox', 'MySQL 8 InnoDB, 16 shards; each a primary + semi-sync replica', 'ACID, row locks, CHECK constraints, mature tooling; money needs multi-row transactions'],
  ['Balance cache, rate limits', 'Redis', 'display-only balance, per-user request limits'],
  ['Wallet events', 'Kafka (partitioned by wallet id)', 'fan-out to notifications, history, risk, analytics'],
  ['History read model', 'MySQL read replicas, or Cassandra at larger scale', 'keeps heavy history queries off the primaries'],
  ['Archive (&gt; 13 months)', 'Object storage (Parquet) + warehouse', 'cheap 10-year retention for audit'],
])}
</section>`;

module.exports = { hero, questions, requirements, scale, api, model };
