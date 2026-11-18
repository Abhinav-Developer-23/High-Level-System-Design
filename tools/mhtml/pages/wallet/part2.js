// Wallet System page: high-level design (architecture diagram + components) and detailed flows.
const { code, table, nl, bl, callout, say, seq, C, esc } = require('../../lib');
const { H2, H3 } = require('./ui');

// ---------- architecture diagram (inline SVG, colours from the page theme) ----------
function arch() {
  const box = (x, y, w, h, t, s, col, extra = '') => `<g><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="${col}" fill-opacity=".13" stroke="${col}" stroke-width="1.6"/>` +
    `<text x="${x + w / 2}" y="${y + (s != null ? 24 : h / 2 + 5)}" class="a-t" text-anchor="middle">${esc(t)}</text>` +
    (s ? String(s).split('\n').map((l, i) => `<text x="${x + w / 2}" y="${y + 42 + i * 15}" class="a-s" text-anchor="middle">${esc(l)}</text>`).join('') : '') + extra + `</g>`;
  const ar = (d, dash) => `<path d="${d}" class="a-ln${dash ? ' a-dash' : ''}" marker-end="url(#aah)"/>`;
  const B = '#60a5fa', G = '#22c55e', O = '#f59e0b', P = '#a78bfa', R = '#f87171', T = '#2dd4bf', Y = '#eab308';
  const svc = [['Wallet Service', 'balance · limits · KYC'], ['Transfer Service', 'pay & send · saga coordinator'], ['Top-up Service', 'add money via gateway'], ['Payout Service', 'withdraw to bank'], ['Statement Service', 'history · statements']];
  const rows = [90, 165, 240, 315, 390];
  let s = '';
  s += `<text x="20" y="34" class="a-title">Digital Wallet — High-Level Design</text>`;
  [['CLIENTS', 105], ['ENTRY &amp; EXTERNAL', 305], ['SERVICES', 540], ['DATA', 825], ['ASYNC', 1115]].forEach(([t, x]) => s += `<text x="${x}" y="70" class="a-h" text-anchor="middle">${t}</text>`);
  s += box(20, 92, 170, 54, 'Mobile / Web app', 'users', B) + box(20, 160, 170, 54, 'Merchant APIs', 'pay-ins · refunds', B);
  s += box(220, 90, 170, 125, 'API Gateway', 'auth · device check\nrate limits\nIdempotency-Key\nrequired', G);
  s += box(220, 240, 170, 58, 'Payment Gateway', 'cards · UPI · netbanking', R) + box(220, 315, 170, 58, 'Bank Payout API', 'IMPS / NEFT', R);
  svc.forEach(([t, sub], i) => s += box(430, rows[i], 220, 58, t, sub, O));
  s += box(700, 90, 250, 58, 'Redis', 'balance cache · rate limits', Y);
  const shards = [0, 1, 'N'].map((n, i) => `<rect x="${716 + i * 78}" y="${205}" width="64" height="40" rx="7" fill="${P}" fill-opacity=".22" stroke="${P}" stroke-width="1.2"/><text x="${748 + i * 78}" y="${230}" class="a-s" text-anchor="middle" style="font-weight:700">shard ${n}</text>`).join('');
  s += box(700, 165, 250, 208, 'Wallet DB — MySQL shards', '', P, shards + ['wallets · ledger_entries', 'transactions · transfers', 'idempotency_keys · outbox', 'primary + semi-sync replica'].map((l, i) => `<text x="825" y="${276 + i * 18}" class="a-s" text-anchor="middle">${l}</text>`).join(''));
  s += box(700, 390, 250, 58, 'History Store', 'read model for statements', P);
  s += box(1010, 90, 210, 58, 'Reconciliation', 'ledger vs gateway & bank files', T) + box(1010, 165, 210, 58, 'Kafka', 'wallet events (from outbox)', T) + box(1010, 240, 210, 58, 'Notification Service', 'SMS · push', T) + box(1010, 315, 210, 58, 'Risk & Fraud', 'velocity · anomaly scoring', T);
  // arrows
  s += ar('M190 119 H218') + ar('M190 187 H218');
  s += `<path d="M390 152 H410 M410 110 V410" class="a-ln"/>`;
  rows.forEach(y => s += ar(`M410 ${y + 20} H428`));
  s += ar('M430 282 H392') + ar('M392 282 H428').replace('marker-end', 'marker-start="url(#aah)" marker-end');
  s += ar('M430 357 H392') + ar('M392 357 H428').replace('marker-end', 'marker-start="url(#aah)" marker-end');
  s += ar('M650 112 H698') + ar('M650 133 H675 V182 H698') + ar('M650 205 H698') + ar('M650 269 H698') + ar('M650 344 H698') + ar('M650 419 H698');
  s += ar('M950 194 H1008') + `<text x="979" y="187" class="a-l" text-anchor="middle">outbox</text>`;
  s += `<path d="M1010 212 H990 V419" class="a-ln a-dash"/>` + ar('M990 269 H1008', 1) + ar('M990 344 H1008', 1) + ar('M990 419 H952', 1);
  s += ar('M1010 132 H975 V170 H952', 1);
  s += `<text x="20" y="476" class="a-l">solid = synchronous call · dashed = asynchronous / batch · ⇄ = call + webhook / status poll</text>`;
  const css = `.a-title{font:700 20px var(--font-sans);fill:var(--tx)}.a-h{font:700 12px var(--font-sans);fill:var(--mu);letter-spacing:1.2px}.a-t{font:700 15px var(--font-sans);fill:var(--tx)}.a-s{font:500 12.5px var(--font-sans);fill:var(--mu)}.a-l{font:italic 500 11.5px var(--font-sans);fill:var(--mu)}.a-ln{fill:none;stroke:var(--mu);stroke-width:1.6}.a-dash{stroke-dasharray:6 4}#aah path{fill:var(--mu)}`;
  return `<figure class="diagram"><div class="fig-scroll"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 490" width="1240" height="490" class="arch" role="img"><style>${css}</style><defs><marker id="aah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>${s}</svg></div><figcaption>Money only moves inside the Wallet DB shards. Everything else either calls into them synchronously or reacts to their events.</figcaption></figure>`;
}

const hld = `
<section class="sec">${H2('High Level Design', 'High Level Design')}
<p class="lead">On a high level, the system has a small set of services in front of sharded MySQL databases that hold the ledger. Money moves only inside a database transaction; everything else (notifications, history, risk, analytics) reacts to events.</p>
${arch()}
${H3('1. API Gateway')}
<p>Terminates TLS, authenticates the user and device, applies per-user and per-merchant rate limits, and rejects any money-moving <code>POST</code> without an <code>Idempotency-Key</code>. Routes to the services. Stateless; scales horizontally.</p>
${H3('2. Wallet Service')}
<p>Owns wallets: creation, KYC level, freeze / unfreeze, limits and balance reads. Knows the <strong>shard map</strong> (<code>wallet_id → shard</code>) and is the only code allowed to write <code>wallets</code> and <code>ledger_entries</code>. Other services call its internal "post entries" operation, which runs one local transaction on one shard.</p>
${H3('3. Transfer Service')}
<p>Handles pay and send. If both wallets are on the same shard it runs one local ACID transaction (Flow 1). If not, it coordinates a cross-shard transfer as a <strong>saga</strong> with a durable state machine (Flow 2, Deep Dive 4). Also handles refunds.</p>
${H3('4. Top-up Service')}
<p>Creates gateway orders, receives signed webhooks, verifies the payment status with the gateway, and credits the wallet exactly once. Polls the gateway for payments whose webhook never arrived.</p>
${H3('5. Payout Service')}
<p>Reserves the money, calls the bank payout API with our withdrawal id as the reference, and settles or reverses based on the bank's final answer. Never treats a timeout as a failure.</p>
${H3('6. Statement Service')}
<p>Serves history and monthly statements from the History Store, a read model built from Kafka events. Keeps heavy, paginated queries off the shard primaries.</p>
${H3('7. Wallet DB (MySQL shards)')}
<p>16 shards by <code>wallet_id</code>. Each shard is a primary with a <strong>semi-synchronous</strong> replica (a commit returns only after the replica has the binlog), plus <code>innodb_flush_log_at_trx_commit=1</code> and <code>sync_binlog=1</code>, so a committed payment survives losing the primary.</p>
${H3('8. Kafka, Notification, Risk, Reconciliation')}
<p>An outbox relay (CDC on the binlog, e.g. Debezium) publishes every committed movement to Kafka, keyed by wallet id. Consumers send notifications, update the history store, score fraud, and feed analytics. Reconciliation runs daily against gateway and bank settlement files.</p>
</section>`;

// ---------- detailed flows ----------
const P = {
  app: { n: 'Client', s: 'mobile app', c: C.blue }, gw: { n: 'API Gateway', s: 'auth · rate limit', c: C.green },
  ts: { n: 'Transfer Service', s: '', c: C.orange }, ws: { n: 'Wallet Service', s: '', c: C.orange },
  db: { n: 'Shard 3', s: 'Asha + Ravi', c: C.purple }, dbA: { n: 'Shard 3', s: 'Asha (sender)', c: C.purple }, dbB: { n: 'Shard 9', s: 'Ravi (receiver)', c: C.pink },
  tu: { n: 'Top-up Service', s: '', c: C.orange }, psp: { n: 'Payment Gateway', s: 'PSP', c: C.red }, ps: { n: 'Payout Service', s: '', c: C.orange }, bank: { n: 'Bank API', s: 'IMPS', c: C.red },
  k: { n: 'Kafka', s: 'outbox relay', c: C.teal },
};

const flow1 = `
${H3('Flow 1: Pay / Send — Same Shard', 'Flow 1: Send money (same shard)')}
${seq({ parts: [P.app, P.gw, P.ts, P.db], steps: [
  ['m', 0, 1, 'POST /transfers'], ['m', 1, 2, 'forward (auth ok)'],
  ['m', 2, 2, 'shard(Asha) = shard(Ravi) = 3'], ['m', 2, 3, 'BEGIN … one local transaction'],
  ['note', 3, 3, 'idem key · debit Asha · credit Ravi\nledger entries · outbox row'],
  ['m', 3, 2, 'COMMIT ✓', { dash: 1 }], ['m', 2, 0, '201 COMPLETED', { dash: 1 }],
], caption: 'Both wallets on one shard: one ACID transaction, no coordination needed.' })}
${nl([
  '<strong>Gateway:</strong> authenticates, checks the device, rate-limits, requires <code>Idempotency-Key</code>.',
  '<strong>Transfer Service:</strong> validates the request (amount &gt; 0, not the same wallet, step-up done for large amounts), looks up both shards. Same shard → local path.',
  '<strong>One transaction on shard 3:</strong> the SQL below. Locks are taken in <code>wallet_id</code> order so two opposite transfers can\'t deadlock (Deep Dive 3).',
  '<strong>Commit</strong> → the outbox row is published to Kafka → notifications and history update within a second.',
])}
${code('sql', `
START TRANSACTION;
-- 1. dedup: a retry with the same key fails here with a duplicate-key error (Deep Dive 5)
INSERT INTO idempotency_keys (scope_id, idem_key, request_hash, txn_id) VALUES (:asha, :key, :hash, :txn);
INSERT INTO transactions (txn_id, type, status, from_wallet_id, to_wallet_id, amount_minor)
     VALUES (:txn, 'TRANSFER', 'COMPLETED', :asha, :ravi, 50000);

-- 2. lock both wallets in id order (deadlock-free), then check-and-debit atomically
SELECT wallet_id FROM wallets WHERE wallet_id IN (:asha, :ravi) ORDER BY wallet_id FOR UPDATE;
UPDATE wallets SET balance_minor = balance_minor - 50000, version = version + 1
 WHERE wallet_id = :asha AND status = 'ACTIVE' AND balance_minor - held_minor >= 50000;
-- 0 rows affected → ROLLBACK, return INSUFFICIENT_FUNDS (or WALLET_FROZEN)
UPDATE wallets SET balance_minor = balance_minor + 50000, version = version + 1
 WHERE wallet_id = :ravi AND status = 'ACTIVE' AND balance_minor + 50000 <= :ravi_cap;
-- 0 rows affected → ROLLBACK, return LIMIT_EXCEEDED (or WALLET_FROZEN)

-- 3. the ledger: one debit + one credit, equal amounts
INSERT INTO ledger_entries (txn_id, wallet_id, direction, amount_minor, balance_after_minor) VALUES
  (:txn, :asha, 'DEBIT',  50000, :asha_after),
  (:txn, :ravi, 'CREDIT', 50000, :ravi_after);

-- 4. event for notifications / history / risk, published after commit by the relay
INSERT INTO outbox (aggregate_id, type, payload) VALUES (:asha, 'TRANSFER_COMPLETED', :json);
COMMIT;`)}
${callout('tip', 'Why this is safe', 'The balance check is <em>inside</em> the <code>UPDATE … WHERE balance - held &gt;= amount</code>, which runs on the latest committed row under an exclusive row lock. Two concurrent debits can\'t both pass it (Deep Dive 2). The <code>CHECK</code> constraint is a second safety net.')}`;

const flow2 = `
${H3('Flow 2: Pay / Send — Different Shards', 'Flow 2: Send money (cross-shard)')}
${seq({ parts: [P.app, P.ts, P.dbA, P.dbB], steps: [
  ['m', 0, 1, 'POST /transfers'],
  ['m', 1, 2, 'T1: debit Asha'],
  ['note', 2, 2, 'Asha −500 · clearing +500\nstate = DEBITED'],
  ['m', 2, 1, 'committed ✓', { dash: 1 }],
  ['m', 1, 3, 'T2: credit Ravi'],
  ['note', 3, 3, 'applied_transfers(txn) dedup\nclearing −500 · Ravi +500'],
  ['m', 3, 1, 'committed ✓', { dash: 1 }],
  ['m', 1, 2, 'T3: state = COMPLETED'],
  ['m', 1, 0, '201 COMPLETED', { dash: 1 }],
  ['alt', 'T2 fails for good (Ravi frozen / over cap)'],
  ['m', 1, 2, 'T2′: credit Asha back'],
  ['m', 1, 0, 'FAILED (refunded)', { dash: 1 }],
  ['end'],
], caption: 'Cross-shard transfer as a saga: three small local transactions, each idempotent, tied together by a durable state machine.' })}
<p>Asha is on shard 3 and Ravi on shard 9. No single database transaction can cover both rows. The Transfer Service runs a <strong>saga</strong>:</p>
${nl([
  '<strong>T1 on shard 3:</strong> debit Asha and credit shard 3\'s <code>transfer_clearing</code> account (the books still balance on shard 3), insert the <code>transfers</code> row with state <code>DEBITED</code>. One local transaction; the idempotency key lives here.',
  '<strong>T2 on shard 9:</strong> insert <code>applied_transfers(txn_id)</code> (primary key → applying twice is impossible), debit shard 9\'s <code>transfer_clearing</code>, credit Ravi.',
  '<strong>T3 on shard 3:</strong> mark the transfer <code>COMPLETED</code>. Return 201.',
  '<strong>Crash anywhere?</strong> A recovery worker scans <code>transfers</code> rows stuck in <code>DEBITED</code> and simply retries T2 (safe because it\'s idempotent), then T3.',
  '<strong>T2 fails permanently</strong> (Ravi\'s wallet frozen, or this credit would break his cap): compensate on shard 3: credit Asha back from <code>transfer_clearing</code>, state <code>REVERSED</code>.',
])}
<p>Why a saga and not two-phase commit, and what 2PC would look like, is <strong>Deep Dive 4</strong>.</p>`;

const flow3 = `
${H3('Flow 3: Add Money (Top-up)', 'Flow 3: Add money (top-up)')}
${seq({ parts: [P.app, P.tu, P.psp, P.dbA], steps: [
  ['m', 0, 1, 'POST /topups ₹500'],
  ['m', 1, 3, 'INSERT transactions(TOPUP, PENDING)'],
  ['m', 1, 2, 'create order (receipt = txn_id)'],
  ['m', 2, 1, 'gatewayOrderId', { dash: 1 }],
  ['m', 1, 0, '201 PENDING + gatewayOrderId', { dash: 1 }],
  ['m', 0, 2, 'user pays in gateway checkout / UPI app'],
  ['m', 2, 1, 'webhook: captured (signed)'],
  ['m', 1, 2, 'GET payment: check status + amount'],
  ['m', 1, 3, 'credit tx (only if still PENDING)'],
  ['note', 3, 3, 'PENDING → COMPLETED (conditional)\n1 row → post ledger entries\n0 rows → duplicate, ignore'],
  ['m', 1, 2, '200 OK (ack webhook)', { dash: 1 }],
], caption: 'Credit only after the gateway confirms, and only once: the PENDING → COMPLETED transition is the dedup.' })}
${nl([
  '<strong>Create a pending top-up</strong> in our DB first, so every gateway payment can be matched to a row (the gateway order carries our <code>txn_id</code>).',
  '<strong>The user pays</strong> on the gateway\'s page or UPI app. We never see card numbers (PCI scope stays with the gateway).',
  '<strong>Webhook arrives:</strong> verify the HMAC signature, then <strong>re-fetch the payment from the gateway API</strong> and check status, amount and currency. Never trust the webhook body alone.',
  '<strong>Credit in one local transaction:</strong> <code>UPDATE … SET status=\'COMPLETED\' WHERE txn_id=? AND status=\'PENDING\'</code>. If 1 row changed, post the ledger entries (debit <code>gateway_clearing</code>, credit Asha) and the outbox event. If 0 rows changed, it was a duplicate webhook: do nothing, still return 200.',
  '<strong>No webhook after 2 minutes?</strong> A poller asks the gateway for the status of every top-up still <code>PENDING</code>. After the order expires with no payment, mark it <code>FAILED</code>.',
  '<strong>Cap check:</strong> if the credit would exceed the wallet\'s KYC cap, the payment is refunded to the source through the gateway instead (and the user is told why). Better: check the cap when creating the top-up too.',
])}`;

const flow4 = `
${H3('Flow 4: Withdraw to Bank', 'Flow 4: Withdraw to bank')}
${seq({ parts: [P.app, P.ps, P.dbA, P.bank], steps: [
  ['m', 0, 1, 'POST /withdrawals ₹300'],
  ['m', 1, 2, 'reserve: debit Ravi'],
  ['m', 1, 0, '202 PROCESSING', { dash: 1 }],
  ['m', 1, 3, 'payout(ref = txn_id, ₹300)'],
  ['alt', 'bank: SUCCESS'],
  ['m', 3, 1, 'success (UTR number)', { dash: 1 }],
  ['m', 1, 2, 'mark COMPLETED'],
  ['else', 'bank: FAILED (definite)'],
  ['m', 1, 2, 'reverse: credit Ravi back'],
  ['else', 'timeout / PENDING / unknown'],
  ['m', 1, 3, 'poll status by ref (never re-send)'],
  ['end'],
], caption: 'Money leaves the wallet before the bank call, and comes back only on a definite failure.' })}
${nl([
  '<strong>Reserve first:</strong> one local transaction debits Ravi (if available ≥ ₹300) and credits <code>payout_clearing</code>. His balance drops immediately, so he can\'t spend the same ₹300 while the bank works.',
  '<strong>Call the bank</strong> with our <code>txn_id</code> as the unique reference. Banks dedup on it, so a retried call can\'t pay twice.',
  '<strong>Definite success:</strong> mark <code>COMPLETED</code>, store the bank\'s UTR, move the money from <code>payout_clearing</code> to <code>bank_settlement</code>.',
  '<strong>Definite failure</strong> (wrong account, account closed): reverse: credit Ravi back from <code>payout_clearing</code>, status <code>FAILED</code>, notify him.',
  '<strong>Timeout or "pending":</strong> the money may already have left. Keep it <code>PROCESSING</code> and poll the bank\'s status API by reference. Unresolved after N hours → manual operations queue. <strong>Never</strong> refund the wallet on a timeout (Deep Dive 7).',
])}`;

const flow5 = `
${H3('Flow 5: Refund a Payment', 'Flow 5: Refund')}
<p>A refund is a <strong>new transaction</strong> in the opposite direction (merchant → user) that references the original payment. The original is never edited.</p>
${code('sql', `
-- on the merchant's shard: cap total refunds at the paid amount, atomically
UPDATE transactions SET refunded_minor = refunded_minor + :amt
 WHERE txn_id = :orig AND type = 'TRANSFER' AND status = 'COMPLETED'
   AND refunded_minor + :amt <= amount_minor;
-- 0 rows → REFUND_EXCEEDS_PAYMENT. 1 row → debit merchant, credit user
-- (same shard: same transaction; different shards: the same saga as Flow 2)`)}
${bl(['Two concurrent partial refunds can\'t over-refund: the conditional <code>UPDATE</code> serializes them on the original row.', 'If the merchant\'s balance is too low (already settled to their bank), the refund fails with <code>INSUFFICIENT_FUNDS</code> and the merchant tops up; a platform-funded refund would debit a system account instead.'])}`;

const flow6 = `
${H3('Flow 6: Balance & History Reads', 'Flow 6: Balance & history')}
${table(['Read', 'Served from', 'Freshness'], [
  ['Balance used to approve a debit', 'shard primary, inside the debit transaction', 'exact'],
  ['Balance on the home screen', 'Redis (key = wallet id, value = balance + version), refreshed from Kafka; miss → primary', '≤ ~1 s'],
  ['Transaction history', 'History Store, keyset pagination on <code>(wallet_id, entry_id)</code>', '≤ ~1–2 s'],
  ['Right after the user\'s own payment', 'the API response already carries <code>balanceAfterMinor</code>; the app shows that', 'read-your-writes'],
])}
${callout('interview', '💬 Interview line', '"Only the debit path needs the exact balance, and it gets it for free because the check is inside the debit\'s UPDATE. Everything users merely look at comes from a cache or a read model that lags by about a second."')}`;

const detailed = `
<section class="sec">${H2('Detailed Design', 'Detailed Design (Flows)')}
<p class="lead">Each flow below is a sequence of small local transactions. The rule for the whole system: <strong>money changes only inside one database transaction that also writes the ledger, the idempotency record and the outbox event.</strong></p>
${flow1}${flow2}${flow3}${flow4}${flow5}${flow6}
</section>`;

module.exports = { hld, detailed };
