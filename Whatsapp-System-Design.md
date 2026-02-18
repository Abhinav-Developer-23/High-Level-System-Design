# WhatsApp System Design — Questions

---

## Section 1: Database Choice

**Q1.** Why did we use Cassandra or ScyllaDB over MongoDB or MySQL for message storage?

<details>
<summary>Answer</summary>

The message data has very specific properties that make Cassandra/ScyllaDB the best fit:

- **230,000 writes per second** (20 billion messages/day)
- **Simple access pattern:** "Get the last N messages for this conversation" — no complex joins or aggregations
- **Time-series nature:** recent messages are hot, old messages are cold
- **No transactions needed:** a message either exists or it doesn't
- **High availability is critical:** if the DB goes down, messaging stops

### Why Not MySQL?

1. **Write throughput:** Relational databases use B-tree indexes. At 230K writes/sec, index maintenance becomes a major bottleneck. Cassandra uses **log-structured storage (LSM trees)**, which converts random writes into sequential writes — dramatically faster.
2. **Scaling is painful:** MySQL scales vertically (bigger machines) or with manual sharding. Cassandra scales **linearly** — just add nodes and data redistributes automatically.
3. **Single point of failure:** MySQL has a primary-replica model. If the primary goes down, you need failover. Cassandra is **masterless** — every node can accept writes, giving true high availability.
4. **Partition key design:** Cassandra's partition key (`conversation_id`) + clustering key (`message_id` as TimeUUID) means all messages in a conversation are **physically co-located and pre-sorted on disk**. The most common query becomes a simple sequential range scan, not an index lookup.

> **Note:** The design *does* use PostgreSQL — but only for **user and group data**, where you need joins, transactions, and complex queries.

### Why Not MongoDB?

1. **Write performance at scale:** Cassandra's LSM-tree storage is purpose-built for write-heavy workloads. MongoDB uses a B-tree based engine (WiredTiger), which has higher write amplification at extreme throughput.
2. **Predictable latency:** Cassandra offers **tunable consistency** per query. You can choose low-latency eventual consistency for message delivery while using stronger consistency where needed. MongoDB's consistency model is tied to replica sets, which can introduce latency spikes during elections or failovers.
3. **Linear horizontal scaling:** Cassandra distributes data via consistent hashing across nodes with no single coordinator. MongoDB relies on a **config server and mongos routers** for sharding — more moving parts that can become bottlenecks.
4. **Time-series optimization:** Cassandra's clustering keys keep messages **physically sorted by time on disk**. MongoDB would need an index on timestamp, and range queries still involve more random I/O.
5. **Proven at messaging scale:** Cassandra (and ScyllaDB, its C++ rewrite) is battle-tested at companies like Discord, Apple, and Netflix for exactly this kind of high-write, time-ordered workload.

### Summary Table

| Factor | MySQL | MongoDB | Cassandra/ScyllaDB |
|---|---|---|---|
| Write throughput | Limited | Good | Excellent |
| Horizontal scaling | Manual sharding | Config-server based | Automatic, linear |
| Time-ordered queries | Index scan | Index scan | Sequential disk read |
| High availability | Primary-replica failover | Replica set elections | Masterless, always writable |
| Best for | User/group data (relational) | Flexible documents | High-write, time-series data |

The core insight is: **match the database to the access pattern**. Message data is write-heavy, time-ordered, and needs simple lookups — that's exactly what Cassandra was built for.

</details>

---

## Section 2: Real-Time Communication & Resilience

**Q2.** How does the system protect against WebSocket connection failures so that messages are never lost?

<details>
<summary>Answer</summary>

WebSocket is the primary transport for sending messages because it offers the **lowest latency** with a persistent, bidirectional connection. However, WebSocket connections can fail due to:

- Corporate firewalls or strict proxies that block the WebSocket protocol
- Network switches (e.g., WiFi to cellular) that drop the connection
- Server crashes or restarts
- Client-side issues (app backgrounded, OS kills the socket)

### The Fallback: REST API (`POST /messages`)

The system exposes a **REST endpoint** (`POST /messages`) as a fallback. If the WebSocket connection is unavailable, the client automatically retries the message over a standard HTTP POST request.

### How the Client Handles It

1. **Primary path:** Client sends the message over the open WebSocket connection and starts a timer.
2. **No ACK received:** If no server acknowledgment arrives within a timeout (e.g., 5 seconds), the client assumes the WebSocket is broken.
3. **Reconnection attempt:** The client tries to re-establish the WebSocket connection in the background.
4. **REST fallback:** While reconnecting, the client retries sending the message via `POST /messages` over standard HTTPS. This works through virtually any network, firewall, or proxy.
5. **Deduplication:** The message carries a `client_message_id` (a UUID generated on the device). If both the WebSocket retry and the REST fallback reach the server, the server detects the duplicate ID and stores the message only once.

### Why This Works

| Scenario | What Happens |
|---|---|
| WebSocket is healthy | Message sent instantly over WebSocket (lowest latency) |
| WebSocket drops mid-send | Client retries over WebSocket first, then falls back to REST |
| WebSocket blocked (firewall) | Client detects failure on connect and uses REST directly |
| Server crashes | Client reconnects to a different chat server; pending messages are retried with the same `client_message_id` |

### Key Takeaway

The combination of **WebSocket as the primary channel + REST as a fallback + client-generated deduplication IDs** ensures that:

- Messages are **never lost** regardless of connection state
- Messages are **never duplicated** regardless of how many retries happen
- The user experience degrades gracefully — slightly higher latency over REST, but the message still gets through

</details>

---

**Q3.** How does the system differentiate between duplicate messages in unreliable networks and ensure a recipient never sees the same message twice?

<details>
<summary>Answer</summary>

### The Problem

Networks are unreliable. Consider this scenario:

1. User A taps **Send**.
2. The message reaches the server and is persisted.
3. The server sends back an ACK, but the ACK is **lost** due to a network glitch.
4. User A's client never receives the ACK, assumes the send failed, and **retries**.
5. The server now receives the **same message again**.

Without any safeguard, the server stores it a second time, and User B sees the message **twice**.

### The Solution: `client_message_id` (Idempotency Key)

Before sending, the client generates a **unique ID** (typically a UUID) called `client_message_id` and attaches it to the message. This ID acts as a fingerprint for that specific message.

**On every incoming message, the server checks:**

1. Look up `client_message_id` in the database — "Have I seen this ID before?"
2. **If NO** → It's a new message. Store it, generate a `server_message_id`, and return ACK.
3. **If YES** → It's a duplicate. Skip storage, return the original ACK (with the same `server_message_id`).

### Why the Client Generates the ID (Not the Server)

If the server generated the ID, the client would have no way to match a retry with the original send. The whole point is that the client **knows** the ID before the first attempt, so every retry carries the **exact same ID**. The server can then recognize retries as duplicates.

### Example Flow

| Step | Client | Server |
|---|---|---|
| 1 | Generate `client_message_id: "abc-123"` | — |
| 2 | Send message with `"abc-123"` | Lookup `"abc-123"` → not found → **store** → ACK |
| 3 | ACK lost in network | — |
| 4 | Retry with same `"abc-123"` | Lookup `"abc-123"` → **found** → skip store → ACK |
| 5 | Receives ACK ✓ | — |

User B sees the message **exactly once**.

### This Pattern Is Called Idempotent Delivery

**Idempotent** means performing the same operation multiple times produces the same result as performing it once. The client can retry **as aggressively as it needs to** — 2 times, 5 times, 100 times — and the server guarantees the message is stored only once.

This is a fundamental pattern in distributed systems and is not unique to messaging. Payment systems, API gateways, and event processors all use idempotency keys to prevent duplicate processing over unreliable networks.

</details>

---

## Section 3: Data Retrieval & Pagination

**Q4.** What is pagination, what is a cursor, and why does a WhatsApp-like system use cursor-based pagination instead of offset-based pagination to fetch message history?

<details>
<summary>Answer</summary>

### What Is Pagination?

Pagination is the technique of **breaking a large result set into smaller chunks** (called "pages") so the client doesn't have to download everything at once.

In WhatsApp, a conversation could have **tens of thousands of messages**. When a user opens a chat, you don't fetch all of them — you fetch the **most recent 50**, and load older messages only when the user scrolls up.

There are two main approaches to pagination:

---

### Approach 1: Offset-Based Pagination

This is the traditional method used in many web applications. The client tells the server *how many rows to skip*.

**Request:**
```
GET /conversations/{id}/messages?offset=0&limit=50    -- Page 1
GET /conversations/{id}/messages?offset=50&limit=50   -- Page 2
GET /conversations/{id}/messages?offset=100&limit=50  -- Page 3
```

**SQL equivalent:**
```sql
SELECT * FROM messages
WHERE conversation_id = 'conv_123'
ORDER BY created_at DESC
LIMIT 50 OFFSET 1000;
```

**The problem at scale:**

| Offset Value | What the Database Does |
|---|---|
| `OFFSET 0` | Read 50 rows → fast |
| `OFFSET 1,000` | Read 1,050 rows, **throw away 1,000**, return 50 → slow |
| `OFFSET 100,000` | Read 100,050 rows, **throw away 100,000**, return 50 → very slow |
| `OFFSET 1,000,000` | Read 1,000,050 rows, **throw away 1,000,000**, return 50 → painfully slow |

The database has to **scan and discard** all the skipped rows. As the offset grows, performance degrades linearly. With billions of messages, this is unacceptable.

**Other problems with offset pagination:**

1. **Inconsistent results:** If a new message arrives between page 1 and page 2 requests, the entire dataset shifts — the user might see a **duplicate message** or **miss one entirely**.
2. **Not supported efficiently in Cassandra:** Cassandra (our message database) does not support `OFFSET` at all. It's designed for sequential scans, not arbitrary skips.

---

### Approach 2: Cursor-Based Pagination (What WhatsApp Uses)

Instead of saying "skip N rows," the client says **"give me the next 50 messages after this specific message."** The "this specific message" part is the **cursor**.

**What is a cursor?**

A cursor is an **opaque pointer** that identifies a specific position in the result set. It's typically a **base64-encoded value** derived from an indexed column — like a `message_id` (TimeUUID) or a `timestamp`. The client doesn't need to understand what's inside the cursor; it just passes it back to the server to get the next page.

**Request:**
```
GET /conversations/{id}/messages?limit=50
→ Returns 50 messages + next_cursor = "eyJtc2dfaWQiOiJtc2dfMTIyIn0="

GET /conversations/{id}/messages?limit=50&cursor=eyJtc2dfaWQiOiJtc2dfMTIyIn0=
→ Returns next 50 messages + next_cursor = "eyJtc2dfaWQiOiJtc2dfMDcyIn0="

GET /conversations/{id}/messages?limit=50&cursor=eyJtc2dfaWQiOiJtc2dfMDcyIn0=
→ Returns next 50 messages + has_more = false
```

**What the cursor decodes to (server-side):**
```json
{ "msg_id": "msg_122" }
```

**CQL equivalent (Cassandra):**
```sql
SELECT * FROM messages
WHERE conversation_id = 'conv_123'
  AND message_id < msg_122      -- ← cursor: start after this message
ORDER BY message_id DESC
LIMIT 50;
```

**Why this is fast:** The database uses the `message_id` (which is the clustering key in Cassandra) to **jump directly** to the right position on disk. It doesn't scan or skip anything — it's an indexed seek regardless of how deep into the conversation you are.

---

### Side-by-Side Comparison

| Factor | Offset-Based | Cursor-Based |
|---|---|---|
| **Performance at depth** | Degrades linearly with offset | Constant — always O(limit) |
| **New data arriving between pages** | Causes duplicates or missed items | Stable — cursor anchors to a fixed point |
| **Cassandra compatibility** | Not supported | Native — uses clustering key range scans |
| **Can jump to arbitrary page?** | Yes (`?page=50`) | No — must traverse sequentially |
| **Complexity** | Simple to implement | Slightly more complex (cursor encoding/decoding) |
| **Best for** | Small, static datasets (admin panels, dashboards) | Large, append-heavy datasets (chat, feeds, logs) |

---

### How It Works in WhatsApp's Architecture

1. **User opens a chat** → Client sends `GET /conversations/{id}/messages?limit=50` (no cursor = start from newest).
2. **Server queries Cassandra:**
   ```sql
   SELECT * FROM messages
   WHERE conversation_id = 'conv_123'
   ORDER BY message_id DESC
   LIMIT 50;
   ```
   Because `conversation_id` is the **partition key** and `message_id` (TimeUUID) is the **clustering key**, this query hits a **single partition** and reads **pre-sorted data sequentially** from disk — extremely fast.
3. **Server responds** with 50 messages + a `next_cursor` (the `message_id` of the oldest message in this batch, base64-encoded).
4. **User scrolls up** → Client sends the same request with `?cursor=<next_cursor>`.
5. **Server decodes the cursor** and queries:
   ```sql
   SELECT * FROM messages
   WHERE conversation_id = 'conv_123'
     AND message_id < <decoded_message_id>
   ORDER BY message_id DESC
   LIMIT 50;
   ```
   Again, a direct indexed seek — no scanning, no skipping.
6. **Repeat** until `has_more = false`.

### Sample API Response

```json
{
  "messages": [
    {
      "message_id": "msg_150",
      "sender_id": "user_456",
      "content": "See you tomorrow!",
      "timestamp": "2024-01-15T10:30:00Z",
      "status": "read"
    },
    {
      "message_id": "msg_149",
      "sender_id": "user_789",
      "content": "Sounds good",
      "timestamp": "2024-01-15T10:29:45Z",
      "status": "read"
    }
  ],
  "next_cursor": "eyJtc2dfaWQiOiJtc2dfMTAxIn0=",
  "has_more": true
}
```

### Edge Cases: What If the Cursor Is Missing, Lost, or Invalid?

Cursors can go wrong in several ways. A robust system must handle each gracefully.

#### Case 1: Client Has No Cursor (First Load)

This is the **normal case**, not an error. When the user opens a conversation for the first time (or pulls to refresh), the client simply **omits the cursor parameter**.

```
GET /conversations/{id}/messages?limit=50       -- no cursor
```

The server interprets "no cursor" as **"start from the newest message"** and returns the most recent page.

#### Case 2: Cursor Is Lost (Client Crash, App Restart, Cache Cleared)

If the client had a cursor but lost it (e.g., the app was killed, local storage was cleared, or the user switched devices), it simply **starts over without a cursor** — exactly like Case 1.

**The CQL query when cursor is missing or lost (fetch the newest messages):**

```sql
SELECT message_id, sender_id, content, status, created_at
FROM messages
WHERE conversation_id = 'conv_123'
ORDER BY message_id DESC
LIMIT 50;
```

Since `conversation_id` is the partition key and `message_id` (TimeUUID) is the clustering key sorted descending, this query hits a **single partition** and reads the **most recent 50 messages** directly off disk — no scanning, no offset.

**The server then builds the cursor from the response:**

The cursor is not fetched *from* Cassandra — it is **derived from the query results**. After the server gets the 50 messages back, it takes the `message_id` of the **last (oldest) message** in the batch and encodes it as the cursor.

```
Step-by-step:

1. Server runs the query above → gets 50 messages (msg_200 down to msg_151)

2. The OLDEST message in this batch is msg_151

3. Server encodes it:   base64("{"msg_id":"msg_151"}")  →  "eyJtc2dfaWQiOiJtc2dfMTUxIn0="

4. Server returns:
   {
     "messages": [ ... 50 messages ... ],
     "next_cursor": "eyJtc2dfaWQiOiJtc2dfMTUxIn0=",
     "has_more": true
   }
```

**When the client sends the cursor back (user scrolls up for older messages):**

The server decodes the cursor to extract `msg_151`, then runs:

```sql
SELECT message_id, sender_id, content, status, created_at
FROM messages
WHERE conversation_id = 'conv_123'
  AND message_id < msg_151          -- ← "give me messages OLDER than this"
ORDER BY message_id DESC
LIMIT 50;
```

This query **seeks directly** to the position of `msg_151` using the clustering key index and reads the next 50 in order. Whether this is page 2 or page 200, the cost is exactly the same.

**The full cycle:**

```
Client                          Server                         Cassandra
──────                          ──────                         ─────────
Open chat (no cursor)  ───→  SELECT ... LIMIT 50          ───→  Return msg_200..msg_151
                        ←───  { messages, cursor: "msg_151" }

Scroll up (cursor)     ───→  SELECT ... AND id < msg_151  ───→  Return msg_150..msg_101
                        ←───  { messages, cursor: "msg_101" }

Scroll up (cursor)     ───→  SELECT ... AND id < msg_101  ───→  Return msg_100..msg_051
                        ←───  { messages, cursor: "msg_051" }

...and so on until has_more = false
```

The user sees the latest 50 messages. As they scroll up, new cursors are generated from the fresh responses. No data is lost; the worst that happens is the client re-fetches some messages it already had.

#### Case 3: Cursor Is Invalid or Corrupted

The client sends a cursor that the server can't decode (garbled base64, tampered data, wrong format).

```
GET /conversations/{id}/messages?cursor=GARBAGE_VALUE&limit=50
```

**How the server handles it:**

| Strategy | What Happens |
|---|---|
| **Reject with error (recommended)** | Server returns `400 Bad Request` with a message like `"invalid cursor"`. The client catches this, **drops the bad cursor**, and retries without one — falling back to the latest messages. |
| **Fail-safe fallback** | Server detects the decode failure, logs a warning, ignores the cursor, and returns the newest messages as if no cursor was provided. Simpler for the client, but hides bugs. |

#### Case 4: Cursor Points to a Deleted Message

The user had a valid cursor pointing to `msg_122`, but that message was **deleted** between requests.

```
GET /conversations/{id}/messages?cursor=eyJtc2dfaWQiOiJtc2dfMTIyIn0=&limit=50
```

**How the server handles it:**

Because the cursor query uses a **range comparison** (`message_id < msg_122`), not an exact lookup, it still works even if `msg_122` no longer exists. The database simply returns the next 50 messages with IDs less than `msg_122`. No special handling needed — this is a natural benefit of range-based cursors.

#### Case 5: Cursor Is Expired or Too Old

In some systems, cursors are given a **TTL** (e.g., valid for 24 hours). If the client sends an expired cursor:

- Server detects the expiration (e.g., via a timestamp embedded in the cursor).
- Returns `400 Bad Request` or `410 Gone` with `"cursor expired"`.
- Client drops the cursor and starts fresh.

> **Note:** WhatsApp-style systems typically use **stateless cursors** (just an encoded `message_id`), which don't expire because the message ID is a permanent reference. TTL-based expiration is more common in systems that store cursor state server-side (like paginated search results).

#### Summary

| Scenario | What Happens | User Impact |
|---|---|---|
| No cursor (first load) | Server returns newest messages | None — this is normal |
| Cursor lost (app restart) | Client starts over without cursor | Re-fetches latest page, no data loss |
| Cursor corrupted/invalid | Server returns `400`; client retries without cursor | Momentary re-fetch, transparent to user |
| Cursor points to deleted message | Range query still works — skips past the gap | None — seamless |
| Cursor expired (if TTL-based) | Server returns `400`/`410`; client starts fresh | Re-fetches latest page |

The key design principle: **a cursor is a convenience, not a requirement.** The system must always work without one. If anything goes wrong with the cursor, the client simply drops it and starts from the top. The worst case is re-fetching messages the user already has — never data loss or a broken UI.

### Why Do We Base64-Encode the Cursor Instead of Sending the Raw Message ID?

You might wonder: why not just send `?cursor=msg_151` directly? Why bother encoding it into `eyJtc2dfaWQiOiJtc2dfMTUxIn0=`?

There are several important reasons:

#### 1. Opacity — The Client Should Not Understand the Cursor

The cursor is a **contract between the server and itself**, not between the server and the client. By encoding it, we signal to the client: "this is an opaque token — just pass it back, don't try to parse or build it yourself."

If clients see a raw `msg_151`, developers will be tempted to:
- Construct cursors manually (`msg_152`, `msg_153`...)
- Hardcode cursor values
- Use the cursor for logic it wasn't designed for

This creates a **tight coupling**. If we later change the cursor format (say, from `message_id` to a composite of `timestamp + message_id`), every client that assumed the old format breaks. With an opaque encoded token, we can change the internal structure freely — the client just passes back whatever it received.

#### 2. Flexibility — Cursor Can Carry Multiple Fields

A raw ID limits you to one value. An encoded cursor can contain a **JSON payload** with as many fields as needed:

```json
// Simple cursor (what we use now)
{ "msg_id": "msg_151" }

// Compound cursor (if we need it later)
{ "msg_id": "msg_151", "timestamp": "2024-01-15T10:30:00Z", "shard": 3 }

// Cursor with metadata
{ "msg_id": "msg_151", "version": 2, "expires": "2024-01-16T00:00:00Z" }
```

All of these encode to a single base64 string that the client treats identically. The server can evolve the cursor format **without any client-side changes**.

#### 3. Security — Prevents Cursor Manipulation

If the cursor is a plain `msg_151`, a malicious user could:
- Change it to `msg_999999` to try accessing messages they shouldn't see
- Guess message IDs from other conversations
- Enumerate messages by incrementing the ID

Encoding doesn't provide encryption, but it adds a layer of obscurity. For stronger protection, you can **sign the cursor** (e.g., append an HMAC):

```json
{
  "msg_id": "msg_151",
  "sig": "a3f8b2c1..."   // HMAC of the payload using a server-side secret
}
```

When the cursor comes back, the server verifies the signature. If it's been tampered with, reject it. This prevents any client-side forgery.

#### 4. URL Safety — Avoids Encoding Issues in Transit

Raw values may contain characters that are **unsafe in URLs** (`:`, `/`, `+`, `=`, spaces, unicode). Base64 (specifically base64url) produces a clean alphanumeric string that works safely in query parameters, HTTP headers, and JSON responses without any escaping issues.

#### Summary

| Reason | Raw ID (`msg_151`) | Encoded (`eyJtc2d...`) |
|---|---|---|
| Client coupling | Clients build/parse cursors — fragile | Opaque token — client just passes it back |
| Format evolution | Changing format breaks clients | Server can change internals freely |
| Multiple fields | Limited to one value | Can embed JSON with any number of fields |
| Security | Easy to guess/tamper | Obscured; can be signed with HMAC |
| URL safety | May need escaping | Always URL-safe |

> **In short:** Encoding the cursor is a small upfront cost that buys you **decoupling, flexibility, security, and future-proofing**. The client never needs to know what's inside — it just stores the token and sends it back.

### Key Takeaway

Cursor-based pagination is the standard for **any system with large, continuously growing datasets** — chat messages, social media feeds, activity logs, notifications. It provides **constant-time performance** regardless of how deep into the data you paginate, and it naturally avoids the duplicate/missing-item bugs that plague offset-based pagination in real-time systems.

</details>

---

## Section 4: Offline Message Handling & Reconnection

**Q5.** When an offline user reconnects, how does the system deliver pending messages without breaking message ordering — given that new real-time messages are also arriving?

<details>
<summary>Answer</summary>

### The Problem

When User B comes back online, two things happen simultaneously:

1. The server needs to deliver **old undelivered messages** from the database (sent while User B was offline).
2. Other users are sending **new messages** to User B in real-time (via server-to-server calls, since User B is now connected).

If both paths deliver at the same time with no coordination, messages arrive **out of order**:

```
10:00 AM  — User B goes offline
10:01 AM  — Alice sends "Hey" → persisted in DB with status = 'sent' (msg_1, seq 45)
10:05 AM  — Bob sends "Meeting at 3" → persisted in DB with status = 'sent' (msg_2, seq 46)
10:10 AM  — Carol sends "Happy birthday!" → persisted in DB with status = 'sent' (msg_3, seq 47)

10:15 AM  — User B opens the app

WITHOUT protection:
10:15:00  — Server starts delivering old messages from DB (msg_1, msg_2, msg_3)
10:15:01  — Session Service updated: "User B is online"
10:15:01  — Alice sends NEW message "Are you there?" (msg_4, seq 48)
10:15:01  — msg_4 routed to User B via real-time path
10:15:01  — User B receives: msg_1, msg_4, msg_2, msg_3  ❌ WRONG ORDER
```

### The Solution: Three-Phase Sync with Redis Status

Redis does **NOT** store messages. Messages live only in the **database (Cassandra)**. Redis is used purely to track **connection state** — specifically, whether a user is `offline`, `syncing`, or `online`. This state controls which delivery path is active.

#### What Redis Stores (and What It Does NOT)

```
Redis stores:
  session:user_b        String    → "chat_server_3"     (which server the user is on)
  sync_status:user_b    String    → "syncing"            (connection phase)
  presence:user_b       String    → "online" TTL=30s     (online/offline indicator)

Redis does NOT store:
  ✗ Message content
  ✗ Message queues
  ✗ Pending message lists
  All messages are in Cassandra. Period.
```

---

#### Phase 1: Connect and Set Status to "Syncing"

User B opens the app and connects to Chat Server 3. The server does **NOT** register User B as online yet. Instead, it sets a syncing flag in Redis:

```
> SET sync_status:user_b "syncing"
OK

> EXPIRE sync_status:user_b 60
(integer) 1      ← auto-expires in 60s as a safety net (in case sync hangs)
```

At this point:
- `session:user_b` does **NOT exist** → the Session Service thinks User B is offline.
- `sync_status:user_b` = `"syncing"` → the chat server knows a sync is in progress.

**What happens if someone sends a message to User B right now?**

The sending chat server checks the Session Service → no entry for User B → treats as offline → message is **persisted to the database** with `status = 'sent'` + push notification sent. It does NOT go through the real-time path. No race condition.

---

#### Phase 2: Fetch All Pending Messages from Database and Deliver

The chat server queries **Cassandra** for all undelivered messages:

```sql
SELECT message_id, sender_id, content, sequence, created_at
FROM messages
WHERE recipient_id = 'user_b'
  AND status = 'sent'
ORDER BY sequence ASC;
```

The database is the **single source of truth**. Every message was persisted here before any delivery was attempted. This query returns every message User B hasn't received yet — regardless of how long they were offline.

The server delivers these messages to User B over WebSocket **in sequence order**:

```
→ WebSocket push: msg_1 (seq 45, Alice: "Hey")
→ WebSocket push: msg_2 (seq 46, Bob: "Meeting at 3")
→ WebSocket push: msg_3 (seq 47, Carol: "Happy birthday!")

← Client ACK: "Received up to seq 47"
```

After ACK, update the message statuses in the database:

```sql
UPDATE messages SET status = 'delivered'
WHERE recipient_id = 'user_b' AND status = 'sent';
```

---

#### Phase 3: Go Online — Switch from Syncing to Online

Now that all old messages are delivered, register User B as online and remove the syncing flag:

```
> SET session:user_b "chat_server_3"
OK

> DEL sync_status:user_b
(integer) 1      ← no longer syncing
```

**But there's a tiny window:** Between the DB query (Phase 2) and the session registration (Phase 3), someone might have sent a new message that was persisted to the DB with `status = 'sent'`. One final database check catches these stragglers:

```sql
SELECT message_id, sender_id, content, sequence, created_at
FROM messages
WHERE recipient_id = 'user_b'
  AND status = 'sent'
ORDER BY sequence ASC;
```

- **Empty result?** → Done. User B is fully synced.
- **Has rows?** → Deliver them over WebSocket → update status to `'delivered'`.

Now User B is fully synced and online. From this point, all new messages flow through the **real-time path** (server-to-server → WebSocket). Messages are still persisted to the DB first, but delivery is immediate — no need to query the DB again.

---

### The Complete Flow

```
USER B RECONNECTS
│
├─ Phase 1: Mark as Syncing (Redis only — state tracking)
│   > SET sync_status:user_b "syncing"
│   > EXPIRE sync_status:user_b 60
│   (session:user_b does NOT exist → User B appears offline to everyone)
│
├─ Phase 2: Sync Pending Messages (Database only — message retrieval)
│   → Query Cassandra: SELECT ... WHERE recipient_id = 'user_b' AND status = 'sent'
│   → Deliver all messages over WebSocket in sequence order
│   ← Client ACKs
│   → UPDATE messages SET status = 'delivered' ...
│
├─ Phase 3: Go Online (Redis only — state update)
│   > SET session:user_b "chat_server_3"
│   > DEL sync_status:user_b
│
├─ Final Check: Catch Stragglers (Database only)
│   → Query Cassandra again: SELECT ... WHERE status = 'sent'
│   (if rows exist → deliver + update status)
│
└─ DONE — User B is fully online, real-time messages flow directly
```

### How Other Servers Use the Sync Status

When Chat Server 1 wants to deliver a message to User B, it checks Redis:

```
> GET session:user_b
(nil)                          ← not registered as online

> GET sync_status:user_b
"syncing"                      ← user is reconnecting but not ready yet
```

**Decision:** User B is syncing → treat as offline → persist message to database with `status = 'sent'`. The syncing chat server will pick it up in the final DB check.

If neither key exists → User B is truly offline → persist to DB + send push notification.

### Defense in Depth: Client-Side Sequence Buffer

Even with the sync protocol, network packets can arrive out of order. As a final safety net, the client maintains a **sequence buffer**:

```
Client receives:     seq 45, seq 46, seq 48, seq 47

Display logic:
  seq 45 → expected 45 ✓ → display → last_seen = 45
  seq 46 → expected 46 ✓ → display → last_seen = 46
  seq 48 → expected 47 ✗ → BUFFER (don't display yet)
  seq 47 → expected 47 ✓ → display → last_seen = 47 → flush buffer → display 48 → last_seen = 48
```

Messages **always appear in the correct order** on screen, regardless of network-level delivery order.

### Summary

| Phase | Redis State | Database Action | What Happens to New Messages |
|---|---|---|---|
| **Offline** | No session, no sync_status | Messages stored with `status = 'sent'` | Persisted to DB + push notification |
| **Syncing** | `sync_status:user_b = "syncing"` | Fetch all `status = 'sent'` → deliver → update to `'delivered'` | Persisted to DB (treated as offline) |
| **Online** | `session:user_b = "chat_server_3"` | Messages persisted, then delivered in real-time | Real-time via server-to-server |

**Redis = connection state only.** `session:*` tracks which server a user is on. `sync_status:*` tracks the syncing phase. That's it. All message storage and retrieval goes through **Cassandra**.

</details>

---
