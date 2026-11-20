// Wallet System page: deep dives, failure cheat sheet, quick revision.
const { code, table, nl, bl, callout, say, seq, C } = require('../../lib');
const { H2, H3, DD, approach } = require('./ui');
const pro = html => ({ html: `<strong>Pros:</strong> ${html}`, kind: 'pro' });
const con = html => ({ html: `<strong>Cons:</strong> ${html}`, kind: 'con' });
const verdict = html => callout('', '✅ Our choice', html);

const P = {
  t1: { n: 'Request 1', s: 'pay ₹400', c: C.blue }, t2: { n: 'Request 2', s: 'pay ₹400', c: C.orange },
  dbA: { n: 'Shard 3', s: 'Asha: ₹500', c: C.purple }, db: { n: 'Shard 3', s: 'wallets', c: C.purple },
  tA: { n: 'Tx A', s: 'Asha → Ravi', c: C.blue }, tB: { n: 'Tx B', s: 'Ravi → Asha', c: C.orange },
  co: { n: 'Coordinator', s: 'Transfer Service', c: C.orange }, log: { n: 'Coordinator log', s: 'durable decision', c: C.gray },
  s3: { n: 'Shard 3', s: 'Asha (XA branch)', c: C.purple }, s9: { n: 'Shard 9', s: 'Ravi (XA branch)', c: C.pink },
  app: { n: 'Client', s: 'retries', c: C.blue }, ts: { n: 'Transfer Service', s: '', c: C.orange },
  psp: { n: 'Payment Gateway', s: '', c: C.red }, tu: { n: 'Top-up Service', s: '', c: C.orange }, poll: { n: 'Status Poller', s: 'every 1 min', c: C.yellow },
  ps: { n: 'Payout Service', s: '', c: C.orange }, bank: { n: 'Bank API', s: '', c: C.red },
  svc: { n: 'Wallet Service', s: '', c: C.orange }, relay: { n: 'Outbox relay', s: 'CDC on binlog', c: C.teal }, kafka: { n: 'Kafka', s: '', c: C.teal }, cons: { n: 'Consumers', s: 'notify · history', c: C.green },
};

// ---------- DD1 ledger ----------
const dd1 = `
${DD(1, 'Why a double-entry ledger? Isn\'t a balance column enough?', 'Why a double-entry ledger?')}
<p>Three ways to store "how much money does Asha have":</p>
${approach(1, 'Only a mutable <code>balance</code> column')}
${code('sql', `UPDATE wallets SET balance_minor = balance_minor - 50000 WHERE wallet_id = :asha;`)}
${nl([pro('simplest; balance read is one primary-key lookup.'), con('no history of <em>why</em> the balance is what it is. A bug that subtracts twice is invisible and unrecoverable. Auditors and regulators will not accept it.')])}
${approach(2, 'Only a ledger; balance = <code>SUM(entries)</code> on every read')}
${nl([pro('the ledger is the single source of truth; nothing to drift.'), con('summing a wallet with 50,000 entries on every debit is slow, and the "check then insert" still needs a lock to prevent double spend.')])}
${approach(3, 'Ledger + cached balance, updated in the same transaction')}
${nl([pro('fast exact reads (one row), full history, and drift is detectable: <code>balance_minor</code> must equal the sum of entries, and each entry carries <code>balance_after_minor</code>, so an audit can walk the chain.'), con('two writes per account per movement; the code must always write both (enforce by only allowing writes through one "post entries" function).')])}
${verdict('Approach 3. The ledger is append-only (no <code>UPDATE</code> / <code>DELETE</code> privileges on <code>ledger_entries</code> for the app user). Mistakes are fixed with a new <strong>reversing transaction</strong>, so history always shows what happened and when.')}
${bl(['<strong>Every transaction balances:</strong> sum of debits = sum of credits, checked in code before commit and again by reconciliation.', '<strong>System accounts</strong> (<code>gateway_clearing</code>, <code>payout_clearing</code>, <code>transfer_clearing</code>, <code>fees_revenue</code>) represent money owed to / by the outside world, so even top-ups and withdrawals are balanced pairs.', '<strong>Available vs ledger balance:</strong> <code>available = balance_minor − held_minor</code>. Holds reserve money without moving it.'])}
${say('"I store money as a double-entry ledger: every movement is a debit and an equal credit, entries are append-only, and the wallet balance is a cached sum updated in the same transaction, so it\'s fast to read and provably consistent with the history."')}`;

// ---------- DD2 double spend ----------
const dd2 = `
${DD(2, 'Asha has ₹500. Two ₹400 payments arrive at the same millisecond. How do you stop double spending?', 'Stopping double spending')}
${seq({ parts: [P.t1, P.dbA, P.t2], steps: [
  ['m', 0, 1, 'SELECT balance → 500'], ['m', 2, 1, 'SELECT balance → 500'],
  ['note', 0, 0, '500 ≥ 400 ✓'], ['note', 2, 2, '500 ≥ 400 ✓'],
  ['m', 0, 1, 'UPDATE SET balance = 100'], ['m', 2, 1, 'UPDATE SET balance = 100'],
  ['note', 1, 1, '₹800 spent from ₹500, balance shows ₹100'],
], caption: 'The naive read-check-write: both requests read ₹500 before either writes. A classic lost update.' })}
<p>The bug is the gap between <strong>reading</strong> the balance and <strong>writing</strong> it. Any fix has to make "check and debit" one indivisible step for that wallet.</p>
${approach(1, 'Pessimistic lock: <code>SELECT … FOR UPDATE</code>')}
${code('sql', `
START TRANSACTION;
SELECT balance_minor, held_minor FROM wallets WHERE wallet_id = :asha FOR UPDATE;  -- request 2 waits here
-- app checks balance - held >= 40000, then:
UPDATE wallets SET balance_minor = balance_minor - 40000 WHERE wallet_id = :asha;
INSERT INTO ledger_entries …;
COMMIT;                                                                              -- request 2 now reads 10000 → rejected`)}
${nl([pro('obviously correct; the second request waits and then sees ₹100.'), con('lock held across an extra round trip between app and DB; if the app pauses (GC, slow network) everyone else waits for that wallet.')])}
${approach(2, 'Atomic conditional UPDATE (check inside the write)')}
${code('sql', `
UPDATE wallets
   SET balance_minor = balance_minor - 40000, version = version + 1
 WHERE wallet_id = :asha AND status = 'ACTIVE'
   AND balance_minor - held_minor >= 40000;
-- rows affected = 1 → debited.  0 → insufficient funds (or frozen)`)}
${nl([pro('one statement, one round trip. InnoDB\'s <code>UPDATE</code> is a <em>locking read</em>: it takes an exclusive lock on the row and evaluates the <code>WHERE</code> against the <strong>latest committed</strong> version (not the transaction\'s snapshot), so the second request waits, re-evaluates against ₹100, and matches 0 rows.'), con('you learn only "0 rows", so read the row afterwards if you need the reason (frozen vs insufficient).')])}
${approach(3, 'Optimistic locking with a version column')}
${code('sql', `
SELECT balance_minor, held_minor, version FROM wallets WHERE wallet_id = :asha;   -- version = 41
UPDATE wallets SET balance_minor = :new_balance, version = 42
 WHERE wallet_id = :asha AND version = 41;
-- 0 rows → someone else changed the wallet; re-read and retry (max 3 times)`)}
${nl([pro('no lock held while the app thinks; good when conflicts are rare.'), con('under contention (a busy merchant, a sale) most attempts fail and retry, so throughput collapses exactly when you need it.')])}
${approach(4, 'Distributed lock in Redis around the wallet')}
${nl([pro('can serialize work that spans several systems.'), con('Redis locks have expiry: if the holder pauses longer than the TTL, two holders can run at once, unless every write checks a fencing token. The database must still enforce the rule, so the Redis lock adds a dependency without removing the DB check.')])}
${table(['', 'Read-check-write', 'FOR UPDATE', 'Conditional UPDATE', 'Optimistic (version)', 'Redis lock'], [
  ['Correct under races', '❌', '✅', '✅', '✅', '⚠️ only with fencing'],
  ['Round trips', '2', '2+', '1', '2 + retries', '+2 to Redis'],
  ['Behaviour under contention', 'wrong', 'queue', 'queue (short)', 'retry storms', 'queue'],
  ['Extra dependency', '—', '—', '—', '—', 'Redis'],
], { hl: [0] })}
${verdict('Conditional UPDATE for single-wallet debits; <code>SELECT … FOR UPDATE</code> (in <code>wallet_id</code> order) when a transaction touches two wallets on the same shard (Flow 1). Plus a <code>CHECK (balance_minor &gt;= held_minor)</code> constraint as a last line of defence. Isolation level stays at InnoDB\'s default <code>REPEATABLE READ</code>: the safety comes from locking reads, not from the isolation level.')}
${callout('tip', 'Follow-up: "Would SERIALIZABLE fix the naive version?"', 'In InnoDB, <code>SERIALIZABLE</code> turns plain <code>SELECT</code>s into shared-lock reads. Both requests take a shared lock, both try to upgrade to exclusive, and InnoDB detects a deadlock and kills one. Correct, but you pay with deadlock errors and retries. Taking the exclusive lock directly is cleaner.')}`;

// ---------- DD3 deadlocks ----------
const dd3 = `
${DD(3, 'Asha pays Ravi while Ravi pays Asha. Why can this deadlock, and how do you prevent it?', 'Deadlocks in transfers')}
${seq({ parts: [P.tA, P.db, P.tB], steps: [
  ['m', 0, 1, 'lock Asha ✓'], ['m', 2, 1, 'lock Ravi ✓'],
  ['m', 0, 1, 'lock Ravi … waits for B'], ['m', 2, 1, 'lock Asha … waits for A'],
  ['note', 1, 1, 'cycle → InnoDB kills one: ERROR 1213 (40001)\nDeadlock found when trying to get lock'],
], caption: 'Each transaction locks "my sender first". Opposite transfers lock in opposite order.' })}
${nl([
  '<strong>Lock in a global order:</strong> always lock the two wallets in ascending <code>wallet_id</code> (<code>SELECT … WHERE wallet_id IN (a, b) ORDER BY wallet_id FOR UPDATE</code>). Both transactions now want the lower id first, so one simply waits for the other. No cycle is possible.',
  '<strong>Still retry on 1213 and 1205</strong> (deadlock, lock-wait timeout): InnoDB rolls back the whole transaction, and with the idempotency key inside it, a retry is safe. Retry 2–3 times with jitter.',
  '<strong>Keep transactions tiny:</strong> no HTTP calls, no Kafka sends, no user think-time inside a transaction. The gateway call happens <em>before</em> (create order) or <em>after</em> (webhook), never while a wallet row is locked.',
  '<strong>Lower <code>innodb_lock_wait_timeout</code></strong> from the default 50 s to ~2 s for the wallet service, so a stuck lock fails fast instead of piling up requests.',
])}
${say('"Two-wallet transactions lock rows in wallet-id order, which rules out lock cycles; any remaining deadlock or lock timeout just rolls back and is retried, which is safe because the idempotency key is part of the same transaction."')}`;

// ---------- DD4 2PC vs saga ----------
const dd4 = `
${DD(4, 'Asha and Ravi are on different shards. Do we need two-phase commit?', 'Cross-shard: 2PC vs saga')}
<p>A transfer must debit shard 3 and credit shard 9 <strong>all-or-nothing</strong>. A single MySQL transaction can't span two servers. There are two families of answers: make the two databases commit together (<strong>2PC</strong>), or commit them one after another and guarantee the rest finishes or is undone (<strong>saga</strong>).</p>

${approach(1, 'Two-phase commit (XA transactions)')}
<p>A <strong>coordinator</strong> (our Transfer Service) runs a branch on each shard and then asks both to commit together:</p>
${nl([
  '<strong>Phase 1 — Prepare (voting):</strong> each shard does its work, writes it durably to its redo log, keeps its row locks, and votes YES ("I can definitely commit") or NO.',
  '<strong>Decision:</strong> if every vote is YES, the coordinator durably writes <code>COMMIT</code> to its own log. <strong>This write is the commit point.</strong> Any NO or timeout → <code>ABORT</code>.',
  '<strong>Phase 2 — Commit / rollback:</strong> the coordinator tells every shard the decision; each commits (or rolls back) and releases its locks. Retried until every shard acknowledges.',
])}
${seq({ parts: [P.co, P.log, P.s3, P.s9], steps: [
  ['m', 0, 1, 'txn 77: STARTED'],
  ['m', 0, 2, "XA START 't77','s3'; debit Asha; XA END"], ['m', 0, 3, "XA START 't77','s9'; credit Ravi; XA END"],
  ['m', 0, 2, "XA PREPARE 't77','s3'"], ['m', 0, 3, "XA PREPARE 't77','s9'"],
  ['m', 2, 0, 'YES (locks still held)', { dash: 1 }], ['m', 3, 0, 'YES (locks still held)', { dash: 1 }],
  ['m', 0, 1, 'txn 77: COMMIT  ← commit point (fsync)'],
  ['m', 0, 2, "XA COMMIT 't77','s3'"], ['m', 0, 3, "XA COMMIT 't77','s9'"],
  ['note', 2, 3, 'locks released only now'],
], caption: 'Two-phase commit with MySQL XA. Between PREPARE and COMMIT both rows stay locked.' })}
${code('sql', `
-- on shard 3 (the coordinator runs the same pattern on shard 9 with 's9' and the credit)
XA START 't77','s3';
UPDATE wallets SET balance_minor = balance_minor - 50000
 WHERE wallet_id = :asha AND balance_minor - held_minor >= 50000;   -- 0 rows → vote NO
INSERT INTO ledger_entries (txn_id, wallet_id, direction, amount_minor, …) VALUES (77, :asha, 'DEBIT', 50000, …);
XA END 't77','s3';
XA PREPARE 't77','s3';          -- durable; survives a crash or restart (MySQL 5.7.7+)
-- … coordinator logs COMMIT …
XA COMMIT 't77','s3';           -- or XA ROLLBACK 't77','s3'

XA RECOVER;                     -- after a crash: lists branches that are PREPARED and waiting for a decision`)}
<h4>What happens when things fail</h4>
${table(['Failure', 'What happens', 'Who is stuck?'], [
  ['A shard can\'t do its part (insufficient funds, constraint)', 'it votes NO → coordinator aborts → <code>XA ROLLBACK</code> on all', 'nobody'],
  ['A shard crashes <strong>before</strong> PREPARE', 'its branch is lost; coordinator times out → abort', 'nobody'],
  ['A shard crashes <strong>after</strong> PREPARE', 'on restart, the branch is still PREPARED (<code>XA RECOVER</code>), holding its locks, waiting for the decision', 'that wallet, until the coordinator answers'],
  ['Coordinator crashes <strong>before</strong> logging the decision', 'recovery finds no decision → <strong>presumed abort</strong> → <code>XA ROLLBACK</code> prepared branches', 'both wallets, until recovery runs'],
  ['Coordinator crashes <strong>after</strong> logging COMMIT', 'recovery re-sends <code>XA COMMIT</code> to every branch until all acknowledge', 'both wallets, until recovery runs'],
  ['Network partition between coordinator and a prepared shard', 'the shard <strong>cannot decide alone</strong> (the other shard may already have committed); it must wait', 'that wallet, for as long as the partition lasts'],
], { hl: [5] })}
${nl([pro('true atomicity <em>and</em> isolation: nobody ever sees Asha debited without Ravi credited. Works with ordinary SQL on each shard.'), con('<strong>blocking:</strong> a prepared branch holds row locks across several network round trips and a log fsync, and indefinitely if the coordinator is down. Asha\'s next payment waits behind it. Latency = slowest shard + 2 round trips + 2 fsyncs. The coordinator log becomes critical infrastructure, and XA has operational sharp edges (prepared transactions that someone must resolve by hand).')])}

${approach(2, 'Saga: local transactions + clearing account + compensation')}
<p>Flow 2 above. Each step is a normal local transaction that commits immediately, so no lock is ever held across shards:</p>
${table(['Step', 'Shard', 'Ledger entries', 'transfers.state'], [
  ['T1 debit', '3', 'DEBIT Asha 500 · CREDIT transfer_clearing@3 500', '<code>DEBITED</code>'],
  ['T2 credit', '9', 'DEBIT transfer_clearing@9 500 · CREDIT Ravi 500 (+ <code>applied_transfers</code> row)', '—'],
  ['T3 finish', '3', '—', '<code>COMPLETED</code>'],
  ['T2′ compensate (only if T2 can never succeed)', '3', 'DEBIT transfer_clearing@3 500 · CREDIT Asha 500', '<code>REVERSED</code>'],
])}
${nl([
  '<strong>Every step balances on its own shard,</strong> and across the system <code>transfer_clearing@3</code> (+500) and <code>transfer_clearing@9</code> (−500) cancel out once both steps are done. The sum of all clearing accounts = money currently in flight. Reconciliation checks it.',
  '<strong>Every step is idempotent:</strong> T1 by the idempotency key, T2 by <code>applied_transfers.txn_id</code> (primary key), T3 and T2′ by conditional state transitions (<code>WHERE state = \'DEBITED\'</code>).',
  '<strong>Recovery is "retry forward":</strong> a worker picks <code>transfers</code> rows stuck in <code>DEBITED</code> past <code>next_retry_at</code> and re-runs T2 then T3. Compensation only on a <em>permanent</em> error (receiver closed / frozen / over cap), never on a timeout, because T2 might have committed.',
  '<strong>Debit first, credit second:</strong> if we credited first and the debit failed, Ravi could spend money that never arrived. Debiting first means the worst intermediate state is "money in clearing", which is safe.',
])}
${nl([pro('no cross-shard locks, no blocking, each step is fast (a few ms); a shard outage delays the credit but never freezes the sender\'s wallet; failures are visible as rows in a table.'), con('<strong>no isolation:</strong> for ~10–100 ms Asha is debited and Ravi not yet credited (he may see it a moment later); compensation logic must be written and tested; needs a recovery worker and monitoring of stuck transfers.')])}
${callout('tip', 'Variant: TCC (Try–Confirm–Cancel)', 'Instead of debiting into a clearing account, <strong>Try</strong> puts a hold on Asha (<code>held_minor += 500</code>), <strong>Confirm</strong> turns the hold into a debit and credits Ravi, <strong>Cancel</strong> releases the hold. Same saga structure; it just keeps the money visibly "on hold" in Asha\'s wallet while in flight.')}

${approach(3, 'Avoid the cross-shard case')}
${bl(['<strong>Co-locate</strong> wallets that always transact together (a merchant\'s sub-wallets, a family wallet group) on one shard.', '<strong>Use a distributed SQL database</strong> (Spanner, CockroachDB, TiDB, YugabyteDB). They still run 2PC internally, but each participant and the transaction record are replicated with Paxos / Raft, so a crashed coordinator is replaced automatically and the blocking problem mostly disappears, at the cost of higher write latency and a different operational model.', '<strong>For random P2P you can\'t avoid it:</strong> with 16 shards, ~94% of transfers cross shards.'])}

${table(['', '2PC (XA)', 'Saga (our choice)', 'Distributed SQL'], [
  ['Atomic', '✅', '✅ eventually (retry forward or compensate)', '✅'],
  ['Isolation (no in-between state visible)', '✅', '❌ money visibly "in transit"', '✅'],
  ['Locks held across shards', 'yes, until the decision', 'never', 'yes, but short and replicated'],
  ['Coordinator failure', 'blocks prepared rows', 'worker resumes from the transfers table', 'automatic failover'],
  ['Latency', '2 round trips + 2 fsyncs + slowest shard', 'T1 + T2 ≈ two local commits', 'consensus write latency'],
  ['Complexity lives in', 'XA recovery ops', 'compensation + idempotency code', 'the database'],
], { hl: [] })}
${verdict('A <strong>saga with a clearing account</strong> for cross-shard transfers, and a plain local transaction when both wallets share a shard. 2PC is correct and is the right answer when you truly need isolation across a few internal databases at modest volume (for example moving money between two internal ledgers that auditors require to change together). For a high-volume wallet where any wallet row may be hot, holding locks across a network round trip and blocking on coordinator failure is the wrong trade.')}
${say('"Same-shard transfers are one ACID transaction. Cross-shard I use a saga: debit the sender into a per-shard clearing account, credit the receiver idempotently on the other shard, and drive it with a durable state machine that retries forward and compensates only on permanent failure. I\'d use 2PC only where I need isolation across a couple of internal databases and can live with blocking if the coordinator dies."')}`;

// ---------- DD5 idempotency ----------
const dd5 = `
${DD(5, 'The client timed out and retried "send ₹500". How do you make sure money moves only once?', 'Idempotency: exactly-once money')}
${seq({ parts: [P.app, P.ts, P.db], steps: [
  ['m', 0, 1, 'POST /transfers  key=K1'], ['m', 1, 2, 'BEGIN; INSERT idempotency_keys(K1) …'],
  ['note', 0, 0, 'network drops, client retries'],
  ['m', 0, 1, 'POST /transfers  key=K1 (retry)'], ['m', 1, 2, 'INSERT idempotency_keys(K1)'],
  ['note', 2, 2, 'retry waits on the first\'s\nunique-key lock'],
  ['m', 2, 1, 'first tx COMMIT ✓', { dash: 1 }], ['m', 2, 1, 'retry: ERROR 1062 duplicate key', { dash: 1 }],
  ['m', 1, 2, 'read stored response for K1'],
  ['m', 1, 0, '201 (same response as before)', { dash: 1 }],
], caption: 'The idempotency row is inserted in the same transaction as the money movement, so "recorded" and "moved" can never disagree.' })}
${nl([
  '<strong>The client creates the key</strong> once per user action (tap "Pay") and sends the same key on every retry. A new tap = a new key.',
  '<strong>The key row is part of the money transaction.</strong> Either both the movement and the key commit, or neither does. A separate "check Redis, then move money" step has a crash window between the two.',
  '<strong>Concurrent duplicates are handled by InnoDB:</strong> the second <code>INSERT</code> of the same primary key blocks on the first transaction\'s lock; if the first commits, the second gets <code>1062 Duplicate entry</code>; if the first rolls back, the second proceeds as if it were first.',
  '<strong>Store the response</strong> and replay it, including failures that are final (<code>INSUFFICIENT_FUNDS</code>), so a retry gets the same answer instead of a second attempt that might now succeed.',
  '<strong>Same key, different body</strong> (compare <code>request_hash</code>) → <code>409 IDEMPOTENCY_KEY_REUSED</code>. Protects against a client bug reusing keys.',
  '<strong>Scope the key</strong> to the caller (<code>scope_id</code> = wallet or merchant), so two merchants can\'t collide. Purge after 7 days; the transaction itself stays forever.',
])}
<h4>Idempotency all the way down</h4>
${table(['Hop', 'Dedup key'], [
  ['Client → our API', '<code>Idempotency-Key</code> header → <code>idempotency_keys</code> row'],
  ['Transfer saga T2 on the receiver\'s shard', '<code>applied_transfers.txn_id</code> primary key'],
  ['Us → payment gateway', 'our <code>txn_id</code> as the order receipt; gateways dedup on it'],
  ['Gateway webhook → us', 'conditional <code>status = \'PENDING\' → \'COMPLETED\'</code> transition'],
  ['Us → bank payout', 'our <code>txn_id</code> as the payout reference'],
  ['Kafka → consumers', '<code>event_id</code>; each consumer stores processed ids (or upserts)'],
])}
${say('"Exactly-once is at-least-once delivery plus an idempotency key stored in the same transaction as the money movement. Every hop after that (saga steps, gateway, bank, Kafka consumers) has its own dedup key, so any retry anywhere is harmless."')}`;

// ---------- DD6 top-up failures ----------
const dd6 = `
${DD(6, 'The gateway charged the user, but our server crashed before crediting. What now?', 'Top-up: charged but not credited')}
<p>The gateway and our database can't share a transaction, so we design for every gap between them:</p>
${seq({ parts: [P.psp, P.tu, P.poll, P.db], steps: [
  ['m', 0, 1, 'webhook: captured'], ['note', 1, 1, '💥 crash before commit'],
  ['m', 0, 1, 'webhook retried later'],
  ['m', 2, 3, 'find top-ups PENDING > 2 min'], ['m', 2, 0, 'GET status (receipt = txn_id)'],
  ['m', 0, 2, 'captured, ₹500', { dash: 1 }], ['m', 2, 3, 'credit if still PENDING'],
], caption: 'Three independent ways to finish a top-up: the webhook, its retries, and our own poller. The conditional state change makes them safe together.' })}
${table(['Situation', 'Handling'], [
  ['Webhook lost / we crashed mid-credit', 'gateway retries the webhook; our poller also asks the gateway for every top-up <code>PENDING</code> for over 2 minutes'],
  ['Duplicate webhooks', '<code>UPDATE … WHERE status = \'PENDING\'</code> changes 1 row the first time and 0 afterwards'],
  ['Webhook says "success" but it\'s forged', 'verify the HMAC signature and re-fetch the payment from the gateway API; check amount and currency match our row'],
  ['Payment succeeded <strong>after</strong> we marked the top-up FAILED (expired)', 'still credit it (the user paid) or auto-refund through the gateway; never silently keep the money. Reconciliation catches any we missed'],
  ['Credit would break the KYC cap', 'refund the payment to its source via the gateway and tell the user'],
  ['Chargeback weeks later', 'a new <code>REVERSAL</code> transaction debits the wallet (may go to a negative recovery account if already spent; risk team follows up)'],
])}
${say('"We never credit on the client\'s word or the webhook body alone: a pending row exists first, the gateway\'s status API confirms, and a conditional PENDING → COMPLETED transition makes webhooks, retries and the poller safe to run together."')}`;

// ---------- DD7 bank timeout ----------
const dd7 = `
${DD(7, 'The bank payout call timed out. Did the money leave or not?', 'Withdrawals: bank timeouts')}
${seq({ parts: [P.ps, P.bank, P.db], steps: [
  ['m', 0, 1, 'payout ref=wd_77 ₹300'], ['note', 1, 1, 'bank processes it…'], ['m', 1, 0, '⏱ timeout (no answer)', { dash: 1 }],
  ['note', 0, 0, 'unknown! keep PROCESSING'],
  ['m', 0, 1, 'GET status ref=wd_77 (after 1, 5, 15 min…)'], ['m', 1, 0, 'SUCCESS, UTR 4129…', { dash: 1 }],
  ['m', 0, 2, 'COMPLETED; payout_clearing → bank_settlement'],
], caption: 'A timeout is not a failure. Only the bank\'s status for our reference decides.' })}
${nl([
  '<strong>Three outcomes, not two:</strong> success, definite failure, and <em>unknown</em> (timeout, 5xx, "pending", "deemed success"). Unknown stays <code>PROCESSING</code>.',
  '<strong>If we refunded on timeout</strong> and the bank actually paid, Ravi gets ₹300 in his bank <em>and</em> back in the wallet. That is real money lost.',
  '<strong>If we re-sent the payout</strong> with a new reference, he could be paid twice. Retries always reuse the same reference so the bank dedups.',
  '<strong>Resolution:</strong> poll the status API with back-off; the bank\'s end-of-day statement settles anything still open; past an SLA (e.g. 24 h) it goes to an operations queue. The user sees "Processing".',
  '<strong>Late returns:</strong> a payout that succeeded can be returned days later (account closed). That arrives as a new credit in the bank statement → a new <code>REVERSAL</code> transaction credits Ravi back.',
])}`;

// ---------- DD8 hot wallets ----------
const dd8 = `
${DD(8, 'A big merchant receives 2,000 payments a second. Its wallet row is the bottleneck. What do you do?', 'Hot merchant wallets')}
<p>Every payment updates the merchant's <code>balance_minor</code>, so every payment waits for the same row lock. Each holder keeps the lock until its commit is fsynced and (with semi-sync) acknowledged by the replica, roughly 1–3 ms, which caps one row at a few hundred to ~1,000 updates/s.</p>
${approach(1, 'Split the merchant into N sub-wallets (bucketed balance)')}
${code('sql', `
-- merchant 501 has 16 rows: (501, bucket 0) … (501, bucket 15), all on the same shard
UPDATE merchant_buckets SET balance_minor = balance_minor + :amt
 WHERE merchant_id = 501 AND bucket = :txn_id % 16;
-- merchant balance = SUM over its 16 buckets; payouts sweep buckets`)}
${nl([pro('16× the write throughput with no change to correctness; credits never need a balance check, so any bucket will do.'), con('debits (refunds, payouts) must pick a bucket with enough money or sweep first; balance reads sum 16 rows.')])}
${approach(2, 'Append now, apply in batches')}
<p>Insert the credit's ledger entry immediately (inserts don't contend on one row), and let a per-merchant worker fold pending entries into the balance every ~100 ms in one <code>UPDATE … + SUM(…)</code>.</p>
${nl([pro('one balance update per batch instead of per payment.'), con('merchant balance lags by the batch interval; refunds must count unapplied credits or wait.')])}
${approach(3, 'Credit asynchronously through a queue')}
${nl([pro('smooths spikes completely.'), con('the payer is debited synchronously but the merchant credit is eventually consistent, and the clearing balance in between must be monitored. Fine for merchants (they settle daily anyway), not for P2P.')])}
${verdict('Bucketed balances for the few known hot merchants (configured per merchant, e.g. 16–64 buckets). Users never need it: a person can\'t make 1,000 payments a second. Only <strong>credits</strong> are spread; debits on a merchant are rare and can take a short lock across buckets.')}`;

// ---------- DD9 outbox ----------
const dd9 = `
${DD(9, 'How do notifications, history and fraud checks learn about a payment without ever missing or inventing one?', 'Reliable events: transactional outbox')}
<p>The naive version, "commit to MySQL, then publish to Kafka", has a crash window: commit succeeds, publish never happens, and the user gets no SMS and no history entry. Publishing first is worse: Kafka says "paid" for a transaction that then rolls back.</p>
${seq({ parts: [P.svc, P.db, P.relay, P.kafka, P.cons], steps: [
  ['m', 0, 1, 'one tx: ledger + outbox row'],
  ['m', 2, 1, 'tail binlog (Debezium)'], ['m', 2, 3, 'publish key = wallet_id'],
  ['m', 3, 4, 'WALLET_DEBITED #9001'], ['note', 4, 4, 'dedup by event_id'],
], caption: 'The outbox row commits with the money, so an event exists if and only if the money moved.' })}
${bl(['<strong>Atomic:</strong> the outbox insert is in the same transaction as the ledger entries.', '<strong>At-least-once:</strong> the relay may publish an event twice after a restart, so consumers dedup on <code>event_id</code> (or make their writes upserts).', '<strong>Ordered per wallet:</strong> Kafka partition key = <code>wallet_id</code>, so a wallet\'s debits and credits arrive in commit order.', '<strong>Cleanup:</strong> outbox rows are deleted (or the partition dropped) after a few days; with binlog CDC the table can even be write-only.'])}`;

// ---------- DD10 sharding ----------
const dd10 = `
${DD(10, 'How do you shard the wallets, and how do you add shards later?', 'Sharding & resharding')}
${nl([
  '<strong>Shard key = <code>wallet_id</code>.</strong> Every single-wallet operation (debit, credit, history, idempotency) is then local. Sharding by user would work the same (one wallet per user), but merchants have several wallets.',
  '<strong>Logical shards:</strong> <code>logical = hash(wallet_id) % 4096</code>, and a small directory maps the 4,096 logical shards onto 16 physical MySQL clusters. Resharding moves whole logical shards (copy, catch up from binlog, brief write freeze, flip the directory), never re-hashes individual wallets.',
  '<strong>System accounts per shard:</strong> each physical shard has its own clearing accounts, so top-ups and withdrawals stay local and no system row is shared by all traffic.',
  '<strong>Global ids:</strong> <code>txn_id</code> from a Snowflake-style generator (time + node + sequence), unique without coordination.',
  '<strong>Cross-wallet queries</strong> (all transactions of a merchant group, finance reports) run on the warehouse fed by Kafka, never by fanning out to every shard.',
])}`;

// ---------- DD11 durability ----------
const dd11 = `
${DD(11, 'A shard primary dies one millisecond after confirming a payment. Is the payment lost?', 'Durability & failover')}
${table(['Setting', 'Value', 'Why'], [
  ['<code>innodb_flush_log_at_trx_commit</code>', '<code>1</code>', 'redo log fsynced at every commit; no committed transaction lost on a crash'],
  ['<code>sync_binlog</code>', '<code>1</code>', 'binlog fsynced at every commit, so replicas and CDC never miss a committed transaction'],
  ['Semi-sync replication', '<code>AFTER_SYNC</code> (lossless)', 'the commit is acknowledged only after at least one replica has the binlog event. Semi-sync silently falls back to async if no replica answers within <code>rpl_semi_sync_source_timeout</code>: set it high and alert on fallback'],
  ['Failover', 'Orchestrator / MySQL Group Replication', 'promote the replica that has every acknowledged transaction; fence the old primary so it can\'t accept writes'],
  ['Backups', 'daily physical backup + continuous binlog archive', 'point-in-time recovery (e.g. after a bad deploy)'],
])}
${bl(['<strong>RPO = 0 within the region:</strong> anything we told the user "COMPLETED" is on at least two machines.', '<strong>DR region:</strong> asynchronous replication (a few seconds behind). After a regional failover, the last seconds may be missing; reconciliation against gateway / bank records and client-side receipts restores them. That\'s why the interviewer\'s RPO = 0 was scoped to one region.', '<strong>No active-active writes</strong> for the same wallet in two regions: two regions could each approve the last ₹500.'])}`;

// ---------- DD12 reconciliation ----------
const dd12 = `
${DD(12, 'How do you prove the money is right, every day?', 'Reconciliation & audit')}
<h4>Internal checks (our books agree with themselves)</h4>
${code('sql', `
-- 1. every transaction balances
SELECT txn_id FROM ledger_entries
 GROUP BY txn_id
HAVING SUM(CASE direction WHEN 'DEBIT' THEN amount_minor ELSE -amount_minor END) <> 0;

-- 2. cached balance = sum of entries (run incrementally from the last checked entry_id)
SELECT w.wallet_id FROM wallets w
  JOIN (SELECT wallet_id, SUM(CASE direction WHEN 'CREDIT' THEN amount_minor ELSE -amount_minor END) s
          FROM ledger_entries GROUP BY wallet_id) l USING (wallet_id)
 WHERE w.type <> 'SYSTEM' AND w.balance_minor <> l.s;

-- 3. money in flight: transfer_clearing summed over all shards = open transfers' amounts`)}
<h4>External checks (our books agree with the outside world)</h4>
${table(['Compare', 'With', 'Typical break'], [
  ['Completed top-ups per day', 'gateway settlement file', 'payment captured but never credited (webhook + poller both missed it)'],
  ['Completed withdrawals', 'bank statement / payout report (UTRs)', 'payout we think failed actually succeeded, or a late return'],
  ['<code>gateway_clearing</code> balance', 'money the gateway actually transferred to our bank (T+1)', 'fees, chargebacks'],
  ['Total user balances', 'money held in our escrow / nodal bank account', 'any of the above'],
])}
${bl(['Every mismatch becomes a "break" in an ops queue; fixes are new, approved transactions (<strong>maker–checker</strong>: one person proposes, another approves), never edits.', 'Stuck states are alerts too: transfers in <code>DEBITED</code> &gt; 5 min, withdrawals <code>PROCESSING</code> &gt; 24 h, top-ups <code>PENDING</code> with a captured payment.', 'Ledger immutability: the app\'s DB user has only <code>INSERT</code> / <code>SELECT</code> on <code>ledger_entries</code>; monthly partitions are archived to write-once object storage.'])}`;

// ---------- DD13 limits, fraud, security ----------
const dd13 = `
${DD(13, 'How do you enforce limits, stop fraud and secure the wallet?', 'Limits, fraud & security')}
<h4>Limits checked inside the money transaction</h4>
${code('sql', `
-- daily outflow: one counter row per wallet per day, on the wallet's shard, same transaction as the debit
INSERT IGNORE INTO daily_usage (wallet_id, day, out_minor) VALUES (:w, CURRENT_DATE, 0);
UPDATE daily_usage SET out_minor = out_minor + :amt
 WHERE wallet_id = :w AND day = CURRENT_DATE AND out_minor + :amt <= :daily_cap;
-- 0 rows → LIMIT_EXCEEDED → ROLLBACK (the row lock also serializes two concurrent debits)
-- balance cap on credit: the receiver's UPDATE has "balance_minor + :amt <= :kyc_cap" (Flow 1)`)}
<p>Limits checked outside the transaction (a Redis counter, say) have the same race as the naive balance check: two requests both read "₹9,000 of ₹10,000 used" and both pass.</p>
<h4>Fraud</h4>
${bl(['<strong>Synchronous risk check</strong> before high-risk debits (new device, new payee, large amount, unusual hour): a fast rules + model score; high score → step-up (MPIN / OTP) or block.', '<strong>Asynchronous scoring</strong> on the Kafka stream: velocity (10 payees in 5 minutes), mule patterns (money in, immediately out to a bank) → freeze the wallet (<code>status = \'FROZEN\'</code>; the debit <code>UPDATE</code> already requires <code>ACTIVE</code>).', '<strong>New-device cooling period</strong>: lower limits for the first 24 h after a device or SIM change.'])}
<h4>Security</h4>
${bl(['OAuth access tokens bound to a registered device; MPIN or biometric for debits above a threshold.', 'Bank account numbers and KYC documents encrypted at rest (envelope encryption, KMS); masked in logs and APIs.', 'Card data never touches us: the gateway tokenizes it (keeps us out of most PCI scope).', 'Webhooks: HMAC signature + timestamp (reject replays) + status re-fetch; bank APIs over mTLS.', 'Admin tools: every manual adjustment is a ledger transaction with maker–checker approval and an audit trail.'])}`;

// ---------- DD14 passbook (2-year history) ----------
const dd14 = `
${DD(14, 'Show me my passbook for the last 2 years. Where does it come from?', 'Passbook: 2 years of history')}
<p><strong>The query:</strong> "this wallet's entries, newest first, 20 per page, keep scrolling back up to 2 years". It always reads <strong>one wallet</strong>, sorted by <strong>time</strong>. It never joins tables or needs a transaction.</p>
${code('text', `
Passbook rows   50M movements/day × ~2 user-visible sides  ≈ 100M rows / day
2 years         100M × 730                                 ≈ 73B rows
On disk         73B × ~300 B ≈ 22 TB × RF 3 ≈ 66 TB raw    ≈ 35 TB after compression
Writes          6K movements/s at sale peak × 2            ≈ 12K rows / s
Reads           ~30K passbook pages / s at sale peak (each = 1 partition read)`)}
${approach(1, 'Read history straight from the MySQL ledger shards')}
${nl([pro('no new system; the data is exact.'), con('long scroll-back queries compete with the fsync-bound money writes on the same primaries. 73B rows in B-trees. Deleting rows older than 2 years means huge <code>DELETE</code>s or managing partitions by hand.')])}
${approach(2, 'A separate, sharded MySQL just for history')}
${nl([pro('familiar; SQL for ad-hoc queries.'), con('you hand-build sharding, resharding and retention for an append-only time series that never uses joins or transactions.')])}
${approach(3, 'Cassandra (or DynamoDB / ScyllaDB) as a read model')}
${nl([pro('fast appends (LSM: sequential writes, no B-tree page splits). One page read = one partition, read sequentially. Scales by adding nodes, with automatic rebalancing. <strong>TTL</strong> deletes old rows for free. Multi-DC replication is built in.'), con('eventually consistent, which is fine because the passbook may lag about 1 s. No ad-hoc queries: you design the table for this one query. TTL and tombstones need the right compaction.')])}
${verdict('Approach 3: Cassandra. The MySQL ledger stays the <strong>source of truth</strong> (money, audit, reconciliation, ~13 months hot). Cassandra is a <strong>read model</strong> built from events. Entries older than 2 years are served from the <strong>S3 / Parquet archive</strong>.')}

<h4>Table and shard key</h4>
${code('sql', `
CREATE TABLE passbook (
  wallet_id           bigint,
  month               int,          -- 202611
  created_at          timestamp,
  entry_id            bigint,
  txn_id              text,
  type                text,         -- TOPUP / TRANSFER_OUT / PAYMENT / REFUND …
  amount_minor        bigint,       -- signed
  balance_after_minor bigint,       -- copied from the ledger, never recomputed
  counterparty_name   text,         -- denormalised, so no lookups at read time
  status              text,         -- e.g. PROCESSING → COMPLETED for payouts
  PRIMARY KEY ((wallet_id, month), created_at, entry_id)
) WITH CLUSTERING ORDER BY (created_at DESC, entry_id DESC)
  AND default_time_to_live = 63072000                       -- 2 years
  AND compaction = {'class': 'TimeWindowCompactionStrategy',
                    'compaction_window_unit': 'DAYS', 'compaction_window_size': 30};`, 'CQL')}
${bl([
  '<strong>Shard key = partition key = <code>(wallet_id, month)</code>.</strong> Cassandra hashes it (Murmur3) onto the token ring, so you never shard by hand. Adding a node takes over a range of tokens.',
  '<strong>Why <code>wallet_id</code>:</strong> every query is for one wallet, so one page is answered by one partition on one replica set.',
  '<strong>Why <code>month</code> as well:</strong> with <code>wallet_id</code> alone, a partition grows forever (merchants, 10 years). With month only, all of today\'s writes land on one hot partition. A month bucket keeps a user\'s partition tiny (~100 rows, ~30 KB). It also matches the monthly statement, which is exactly one partition read.',
  '<strong>Clustering <code>(created_at DESC, entry_id DESC)</code>:</strong> rows are stored on disk newest first, so "latest 20" is a sequential read with no sorting. <code>entry_id</code> breaks ties when two entries share a timestamp.',
  '<strong>Hot merchants</strong> (2,000 payments/s ≈ 5B rows/month in one partition): for wallets flagged as high-volume, the bucket is <code>(wallet_id, day, sub_bucket 0..N-1)</code>. Merchants mostly use exported reports from the warehouse, not a scrolling passbook.',
])}

<h4>Reading 2 years back</h4>
${code('sql', `
-- page 1
SELECT * FROM passbook WHERE wallet_id = ? AND month = 202611 LIMIT 20;
-- next page: cursor = (month, created_at, entry_id) of the last row
SELECT * FROM passbook WHERE wallet_id = ? AND month = 202611
   AND (created_at, entry_id) < (?, ?) LIMIT 20;
-- month exhausted → move to the previous month that has entries`, 'CQL')}
${bl([
  'A small <code>passbook_months (wallet_id, month)</code> table (clustered <code>month DESC</code>) lists the months that actually have entries. A dormant user with 1 payment in 2 years then costs 2 reads, not 24 empty-month probes. The cursor is opaque to the app, which never sees months.',
  '<strong>Date-range filter ("March 2025"):</strong> jump straight to that month\'s partition.',
  '<strong>Type filter ("only debits"):</strong> filter in the service. A user\'s month is small.',
  '<strong>Text search ("Swiggy"):</strong> optional Elasticsearch index over the last ~6 months. It\'s not the passbook.',
])}

<h4>Who writes it</h4>
${nl([
  'The money transaction commits in MySQL together with its outbox row (Deep Dive 9).',
  'CDC publishes the event to Kafka, keyed by <code>wallet_id</code>, so each wallet\'s events stay in order.',
  'The <strong>Passbook consumer</strong> inserts the row with <code>LOCAL_QUORUM</code>. Cassandra <code>INSERT</code> is an upsert on the primary key, so a duplicate event writes the same row again and does no harm. That\'s idempotent with no dedup table.',
  'A payout changing <code>PROCESSING → COMPLETED</code> is an upsert of the <code>status</code> column on the same row.',
])}
<p>Reads use <code>LOCAL_ONE</code>. The few-ms staleness doesn't matter because the app already shows the user's own payment from the API response (<code>balanceAfterMinor</code>).</p>

<h4>Older than 2 years</h4>
<p>TTL plus TWCS deletes whole 30-day SSTables once they expire, with no <code>DELETE</code> and no tombstone scans. The 10-year audit copy lives in <strong>S3 as Parquet</strong> (the Kafka → archive pipeline, partitioned by <code>month/shard</code>). "Statement for 2021" is an <strong>async job</strong> (Trino / Athena query → PDF → email / download link), not an infinite scroll.</p>
${say('"The ledger in MySQL is the source of truth; the passbook is a read model in Cassandra, partitioned by (wallet_id, month) and clustered by time descending, fed from the outbox through Kafka with idempotent upserts. Two years via TTL, older statements from the S3 archive as an async job."')}`;

const deepDives = `
<section class="sec">${H2('Deep Dives', 'Deep Dives')}
<p class="lead">The follow-ups an interviewer will push on: locking, deadlocks, cross-shard atomicity, exactly-once, and the external systems that can fail in strange ways.</p>
${dd1}${dd2}${dd3}${dd4}${dd5}${dd6}${dd7}${dd8}${dd9}${dd10}${dd11}${dd12}${dd13}${dd14}
</section>`;

const failures = `
<section class="sec">${H2('Failure Scenarios Cheat Sheet', 'Failure Cheat Sheet')}
${table(['What fails', 'What the system does', 'Money safe because'], [
  ['Client retries / double tap', 'second request hits the same idempotency key → stored response', 'key row is in the money transaction'],
  ['Two debits race on one wallet', 'second waits on the row lock, then fails the balance condition', 'conditional UPDATE + CHECK constraint'],
  ['Deadlock between two transfers', 'InnoDB rolls one back; we retry', 'id-ordered locking; idempotent retry'],
  ['Crash between saga T1 and T2', 'recovery worker retries T2 (dedup by <code>applied_transfers</code>)', 'money sits in <code>transfer_clearing</code>, visible to reconciliation'],
  ['Receiver wallet frozen mid-saga', 'compensate: credit sender back', 'T2 fails permanently, never on a timeout'],
  ['2PC coordinator crash (if XA used)', 'recovery reads its log: COMMIT → re-send, none → rollback', 'decision is durable before phase 2'],
  ['Shard primary dies', 'semi-sync replica promoted, old primary fenced', 'commit acknowledged only after the replica has it'],
  ['Gateway webhook lost / duplicated', 'poller + conditional PENDING → COMPLETED', 'state transition happens once'],
  ['Bank payout timeout', 'stay PROCESSING, poll status by reference', 'never refund or re-send on a timeout'],
  ['Kafka down', 'outbox rows accumulate; relay catches up', 'events come from committed rows only'],
  ['Hot merchant spike', 'credits spread over buckets', 'no single row takes all the locks'],
])}
</section>`;

const revision = `
<section class="sec">${H2('Quick Revision', 'Quick Revision')}
${nl([
  '<strong>Store money as integers (paise)</strong> in a <strong>double-entry, append-only ledger</strong>; the wallet balance is a cached sum updated in the same transaction.',
  '<strong>No double spend:</strong> <code>UPDATE … SET balance = balance − x WHERE balance − held ≥ x</code> (atomic check-and-debit under a row lock) + <code>CHECK</code> constraint.',
  '<strong>Two wallets, one shard:</strong> lock both in <code>wallet_id</code> order (no deadlocks), one local transaction, retry on 1213 / 1205.',
  '<strong>Exactly-once:</strong> <code>Idempotency-Key</code> row inside the money transaction; dedup keys on every hop (saga step, gateway, bank, Kafka).',
  '<strong>Cross-shard:</strong> saga — debit into a per-shard clearing account, idempotent credit on the other shard, durable state machine, retry forward, compensate only on permanent failure. <strong>2PC (XA)</strong> gives isolation but holds locks between prepare and commit and blocks if the coordinator dies.',
  '<strong>External money:</strong> pending row first; credit only after the gateway confirms; withdrawals reserve first and treat timeouts as unknown, never as failure.',
  '<strong>Events:</strong> transactional outbox → CDC → Kafka keyed by wallet; consumers dedup by event id.',
  '<strong>Scale:</strong> shard by <code>wallet_id</code> (logical shards → physical), bucket hot merchant balances, history from a read model.',
  '<strong>Prove it daily:</strong> every transaction sums to zero, balances equal their entries, clearing accounts match in-flight work, and our totals match gateway and bank files.',
])}
</section>`;

module.exports = { deepDives, failures, revision };
