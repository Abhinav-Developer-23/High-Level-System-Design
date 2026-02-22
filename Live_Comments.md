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
