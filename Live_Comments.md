# Live Comments System Design

## Clarifying Requirements

Before diving into the design, let's narrow down the scope of the problem. Here's an example of how a discussion between candidate and interviewer might flow:

### Discussion

**Candidate:** "Should users only post text comments, or do we also need to support images, emojis, or reactions?"

**Interviewer:** "For now, only short text-based comments. Reactions or media attachments can be ignored."

---

**Candidate:** "Do comments need to be delivered in real-time to all viewers?"

**Interviewer:** "Yes, the experience should feel live. Ideally under 500 ms from publish to delivery."

---

**Candidate:** "Do we need to support playback after the live event ends like showing comments alongside recorded video?"

**Interviewer:** "Yes. Playback is in scope. Users watching later should see the comments synchronized with the original timeline."

---

**Candidate:** "Can users reply to comments or have threaded conversations?"

**Interviewer:** "No. No replies or threads. Just a flat stream of comments."

---

**Candidate:** "What about comment moderation like spam filtering, profanity, abuse detection?"

**Interviewer:** "Assume moderation already exists. You can treat it as out of scope."

---

**Candidate:** "For ordering, do we need strict global time ordering across distributed regions?"

**Interviewer:** "No. Exact strict ordering is not require. We just need roughly correct chronological order that feels consistent to the user."

---

## Question 1: What are the Functional Requirements?

### Functional Requirements
- **Post Comments**: Users can post short, text-based comments during a live event.
- **Real-Time Viewing**: Users can view new comments posted by others in real-time.
- **Playback**: Users can replay the stream with synchronized comments (time-aligned with the video) after the event ends.

### Out of Scope
- **Reactions**: Users can react (like, heart, etc.) to comments.
- **Replies**: Users can reply to comments.
- **Moderation**: The system must filter spam, and other undesirable content.

---

## Question 2: What are the Non-Functional Requirements?

### Non-Functional Requirements
- **High Scalability**: Support millions of concurrent viewers and thousands of new comments per second.
- **Low Latency**: Deliver comments to clients within sub-second latency (< 500 ms ideally).
- **Reliability & Durability**: Once accepted, a comment should never be lost even during failures.
- **Ordering**: Comments should appear in approximately the order they were sent. Strict ordering is difficult in a distributed system, but we should aim for a consistent experience.
- **Eventual Consistency**: Small ordering differences or delays are acceptable as long as the user experience remains smooth.

---

## Storage Size Reference

Understanding how characters are stored in different parts of the system:

### 1. Network Transmission (JSON over HTTP)

Uses **UTF-8 encoding**:
- **English characters**: 1 byte per character
- **Accented characters** (é, ñ, ü): 2 bytes per character
- **Emojis** (😀, 🎉, 🔥): 4 bytes per character

**Examples:**
```
"Hello"        = 5 characters = 5 bytes
"GOAL!!!"      = 7 characters = 7 bytes
"GOAL!!! 🎉"   = 9 characters = 11 bytes (7 + 4 for emoji)
"Café"         = 4 characters = 5 bytes (é is 2 bytes)
```

### 2. Java (In-Memory)

Uses **UTF-16 encoding** internally:
- **Each char**: 2 bytes
- **String object overhead**: ~32 bytes (object header, array overhead, metadata)

**For network transmission (UTF-8):**
```java
String comment = "GOAL!!!";  // 7 characters
byte[] bytes = comment.getBytes(StandardCharsets.UTF_8);
// bytes.length = 7 bytes

String commentEmoji = "GOAL!!! 🎉";  // 9 characters
byte[] bytesEmoji = commentEmoji.getBytes(StandardCharsets.UTF_8);
// bytesEmoji.length = 11 bytes (7 + 4 for emoji)
```

### 3. MySQL Database

Uses **VARCHAR** with **utf8mb4** encoding (supports emojis):

**Storage Formula:**
```
Actual storage = (text bytes in UTF-8) + overhead

VARCHAR(n):
- Overhead: 1 byte if max length ≤ 255
- Overhead: 2 bytes if max length > 255
```

**Examples:**
```sql
-- VARCHAR(255) storing "GOAL!!!" (7 chars)
Storage = 7 + 1 = 8 bytes

-- VARCHAR(500) storing "GOAL!!!" (7 chars)
Storage = 7 + 2 = 9 bytes

-- VARCHAR(500) storing "GOAL!!! 🎉" (9 chars, 11 bytes UTF-8)
Storage = 11 + 2 = 13 bytes
```

### 4. Complete Comment Storage

**Example comment:** "What an incredible shot!"

| Location | Size | Details |
|----------|------|---------|
| **Network (JSON)** | ~100-150 bytes | Text (25 bytes) + JSON metadata (user_id, timestamp, etc.) |
| **Java (In-Memory)** | ~80 bytes | Just the text data for processing (2 bytes/char + overhead) |
| **MySQL (Storage)** | ~120-150 bytes | Text + metadata columns + row overhead |

### 5. Emoji Considerations

Emojis use **4 bytes** in UTF-8:

**Impact on storage:**
```
"Nice! 👍"     = 7 characters = 10 bytes (6 + 4 for emoji)
"GOAL! ⚽🎉"   = 9 characters = 14 bytes (6 + 4 + 4 for two emojis)
```

**MySQL Column Sizing:**
```sql
-- For 500 characters with potential emojis:
comment_text VARCHAR(2000) CHARACTER SET utf8mb4

-- Calculation: 500 chars × 4 bytes max = 2000 bytes
```

### Key Takeaway

**For English text:**
- 1 character ≈ 1 byte (network/storage)

**For emojis:**
- 1 emoji = 4 bytes

**Average comment in Live Comments system:**
- Text: ~100 bytes
- JSON metadata: ~50 bytes
- **Total: ~150 bytes** (as assumed in scale estimation)

---

## Question 3: Why is `stream_id` a Path Variable and Not a Query Parameter?

### API Design Choice

```
✅ Path Variable (Chosen):
POST /v1/streams/{stream_id}/comments

❌ Query Parameter (Not Used):
POST /v1/streams/comments?stream_id=abc-123
```

### When to Use Path Variables vs Query Parameters

#### Use **Path Variables** when:

1. **Identifying a Resource** - The parameter identifies WHICH resource you're operating on
2. **Required Parameter** - The parameter is mandatory for the operation
3. **Hierarchical Structure** - Shows parent-child relationship in the URL
4. **RESTful Design** - Represents the resource's identity in the URL path

**Examples:**
```
GET  /v1/streams/{stream_id}              - Get a specific stream
POST /v1/streams/{stream_id}/comments     - Add comment to a stream
GET  /v1/users/{user_id}                  - Get a specific user
DELETE /v1/comments/{comment_id}          - Delete a specific comment
```

#### Use **Query Parameters** when:

1. **Filtering/Searching** - Narrowing down results from a collection
2. **Optional Parameters** - The parameter is not required
3. **Sorting/Pagination** - Controlling how data is returned
4. **Multiple Options** - When you have many optional filters

**Examples:**
```
GET /v1/streams?status=live&category=sports          - Filter streams
GET /v1/comments?start_time=900&duration=180         - Filter by time range
GET /v1/users?sort=name&limit=50&offset=100          - Pagination/sorting
GET /v1/streams?region=us&language=en                - Multiple filters
```

### Why `stream_id` is a Path Variable in Our Design

1. **Resource Identity**: Comments belong to a specific stream. The URL `/v1/streams/{stream_id}/comments` clearly shows "comments within this stream"

2. **Required Parameter**: You cannot post a comment without specifying which stream it belongs to

3. **RESTful Hierarchy**: The URL structure shows the relationship:
   ```
   /streams/{stream_id}           → The stream resource
   /streams/{stream_id}/comments  → Comments collection under that stream
   ```

4. **Semantic Clarity**: Reading the URL tells you exactly what you're doing:
   - `POST /v1/streams/abc-123/comments` ✓ Clear: "Create a comment in stream abc-123"
   - `POST /v1/comments?stream_id=abc-123` ✗ Less clear: "Create a comment... somewhere... for stream abc-123"

### Real-World Comparison

**Example 1: YouTube Comments**
```
✅ POST /videos/{video_id}/comments
❌ POST /comments?video_id={video_id}
```

**Example 2: GitHub Issues**
```
✅ POST /repos/{owner}/{repo}/issues
❌ POST /issues?owner={owner}&repo={repo}
```

**Example 3: Twitter/X Tweets**
```
✅ GET /users/{user_id}/tweets
❌ GET /tweets?user_id={user_id}
```

### When Both Can Work

For the **playback API**, query parameters make sense because we're filtering:

```
GET /v1/streams/{stream_id}/comments?start_time=900&duration=180&limit=100
```

- Path variable: `stream_id` (identifies WHICH stream)
- Query parameters: `start_time`, `duration`, `limit` (filter/pagination options)

This combination is common and follows REST best practices:
- Path = "What resource am I accessing?"
- Query = "How do I want to filter/sort/paginate it?"

---

## Question 4: Why is HTTP Polling Bad for Live Comments?

### Question

If we need to deliver comments in real-time to **millions of concurrent viewers**, why is a simple HTTP polling approach (e.g., `GET /comments` every N seconds) considered a poor design choice?

### Key Reasons

- **Per-viewer overhead**: Polling traffic scales with **number of viewers**, not just the number of comments. Example: 5M viewers polling every 2 seconds means ~2.5M requests/sec.
- **High fixed cost per request**: Even when the response is empty or small, each poll still pays HTTP/TLS, load balancer, header parsing, and application overhead.
- **Latency vs cost trade-off**: To achieve a “live feel” (< 500ms), the polling interval must be small, which explodes request volume.
- **Thundering herd**: Polling on a fixed cadence can synchronize clients and create periodic request spikes.
- **Often empty across the platform**: Even if one stream is extremely active, many streams and time windows are not, so a large fraction of polls return no new data.

---

## Question 5: Why Prefer SSE Over WebSockets for the Read Path?

### Question

WebSockets provide a persistent, bi-directional connection. If WebSockets are more powerful, why do we still prefer **Server-Sent Events (SSE)** for the live comments **read path**?

### Key Reasons

- **Better fit for one-way delivery**: The read path is server → client only (broadcast). SSE is purpose-built for this; WebSockets are more general than we need.
- **Simpler operational model**: SSE is just a long-lived HTTP response, so connection management is simpler compared to a full WebSocket stack (custom heartbeats, reconnect logic, state management).
- **Proxy/CDN/load balancer friendly**: SSE runs over standard HTTP and tends to work better through corporate proxies and typical HTTP infrastructure.
- **Automatic reconnection**: Browsers automatically reconnect with `EventSource` without requiring heavy custom client logic.
- **Resume support with `Last-Event-ID`**: SSE has a native mechanism to resume from the last seen event (requires the server to emit an `id:` field per event).

---

## Question 6: How Does Cassandra Use Partition and Clustering Keys for Live Comments?

### The Question

To make this query incredibly fast, we will design our comments table with a composite primary key that aligns perfectly with this access pattern.

- **Partition Key:** `stream_id`. The partition key tells the database how to group and distribute data across the cluster. By using `stream_id`, we ensure that all comments for the same live stream are physically stored together. When we query for a stream, the database knows exactly which nodes to go to, avoiding a slow, full-database scan.
- **Clustering Key:** `timestamp`. Within each partition (for a given `stream_id`), the data will be physically sorted on disk by timestamp. This is a massive performance optimization. It means that when we fetch the comments, they are already in chronological order. The database doesn't need to perform an expensive sorting operation on the fly.

How does this exactly work under the hood in a database like Apache Cassandra or Amazon DynamoDB?

### How it Works

#### 1. The Partition Key (`stream_id`): "The Where"
Cassandra is a distributed database, meaning your data isn't sitting on one server; it's spread across dozens or hundreds of servers (called **nodes**) arranged in a ring.

When a user posts a comment, Cassandra takes the **Partition Key** (`stream_id`) and puts it through a mathematical function called a **hash function**. 
- Let's say the `stream_id` is `"world-cup-final"`. 
- Cassandra hashes `"world-cup-final"` and gets a number, say `42`.
- It knows that node #3 is responsible for number `42`.
- Therefore, the comment goes strictly to node #3.

**Why this is fast for reading:** 
When someone opens the stream and requests the chat history, Cassandra doesn't have to go ask all 100 servers, "Hey, do any of you have comments for the world cup?" It hashes the ID, immediately knows node #3 has *all* of them, and goes straight there. This prevents a massive performance bottleneck known as a "full-database scan."

#### 2. The Clustering Key (`timestamp`): "The Order"
So now we are at node #3, looking at all the comments for `"world-cup-final"`. But a high-traffic stream might have 500,000 comments. 

In a traditional SQL database, if you ran `SELECT * WHERE stream_id = 'world-cup-final' ORDER BY timestamp DESC`, the database might have to grab those 500,000 comments, load them into memory, and sort them on the fly before giving you the latest 50. That is slow and expensive.

This is where the **Clustering Key** comes in. Cassandra physically writes the data to the hard drive **already sorted** by the clustering key. 
- As comments arrive, Cassandra puts them on disk sequentially, perfectly ordered by their `timestamp`.
- When you request the "latest 50 comments," Cassandra literally just goes to the end of the `world-cup-final` block on the disk and reads the last 50 lines sequentially. The machine doesn't sort anything; it just reads.

### The Real-World Analogy
Imagine a massive library with hundreds of filing cabinets (the **Nodes**).

1. **Partition Key (`stream_id`)**: The label on the outside of a specific drawer. You walk directly to the drawer labeled `"world-cup-final"` instead of opening every cabinet in the library.
2. **Clustering Key (`timestamp`)**: Inside that drawer, the papers aren't just thrown in a messy pile. The librarian insists they are perfectly filed in chronological order as soon as they are handed in. 

Because of this rigid rule, when you walk up to the drawer and say, "Give me the 10 most recent comments," the librarian doesn't have to organize anything. They just pull the 10 papers from the very front.

### Summary
By combining these two keys into a **Composite Primary Key**, Cassandra gives you `O(1)` routing (knowing exactly which server to talk to) and `O(1)` sorting (the data on the hard drive is already sorted for you). This is what enables companies like Twitch or Discord to serve millions of chat messages seamlessly!

### What exactly is a "Partition"?
In a distributed database like Cassandra, a **Partition** is a fundamental unit of data storage. 

If you think of the whole database as a massive filing cabinet, a partition is a single *folder* within that cabinet. 

1. **A partition is a group of rows that share the exact same Partition Key.** In our case, every comment for `stream_id = 'world-cup-final'` lives inside the "world-cup-final" partition folder.
2. **A partition always lives on ONE physical node (server).** Cassandra never splits a single partition across multiple servers. If the 'world-cup-final' partition is assigned to Node #3, *all* comments for the World Cup will be physically written to the hard drive of Node #3. (It will also be copied to backup nodes for redundancy, but the primary copy is strictly on one machine).
3. **Data inside a partition is read together.** Because all rows in a single partition are sitting right next to each other on the physical hard drive, the database can scoop them all up in one quick motion. This is called "data locality."

**Why this matters:**
If we didn't use partitions, the comments for the World Cup stream would be scattered randomly across all 100 servers in our cluster. To get the chat history, the system would have to query all 100 servers, merge the results over the network, sort them, and return them. That is incredibly slow. 

By grouping them into a **Partition**, we guarantee that all the data we need for one specific query is sitting right next to each other on exactly one server.
