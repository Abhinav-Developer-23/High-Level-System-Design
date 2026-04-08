# Movie Ticket Booking System - Pagination

## 1. Client Request

The client sends a `GET` request with pagination parameters:

```
GET /movies?city=NYC&genre=action&page=2&limit=10
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Which page of results to fetch |
| `limit` | int | 10 | Number of items per page |
| `city` | string | required | Filter by city |
| `genre` | string | optional | Filter by genre |

---

## 2. Server Processing

When the server receives this request, it does two things:

**Step 1 — Calculate the SQL offset:**
```
offset = (page - 1) * limit
       = (2 - 1) * 10
       = 10
```
This means: skip the first 10 results and return the next 10.

**Step 2 — Execute two SQL queries:**

**Query A — Get the paginated results:**
```sql
SELECT movie_id, title, genre, duration_minutes, rating, poster_url
FROM movies
WHERE city = 'NYC'
  AND genre = 'action'
  AND release_date <= CURRENT_DATE
ORDER BY release_date DESC, rating DESC
LIMIT 10 OFFSET 10;
```

**Query B — Get the total count (for calculating total pages):**
```sql
SELECT COUNT(*) AS total_count
FROM movies
WHERE city = 'NYC'
  AND genre = 'action'
  AND release_date <= CURRENT_DATE;
```

> If `total_count = 47`, then `total_pages = CEIL(47 / 10) = 5`

---

## 3. Response Format

```json
{
  "movies": [
    {
      "movie_id": "mov_201",
      "title": "Fast & Furious 12",
      "genre": "Action",
      "duration": 135,
      "rating": 7.8,
      "poster_url": "https://cdn.example.com/ff12.jpg"
    },
    {
      "movie_id": "mov_202",
      "title": "The Dark Phoenix",
      "genre": "Action",
      "duration": 142,
      "rating": 8.1,
      "poster_url": "https://cdn.example.com/phoenix.jpg"
    }
  ],
  "pagination": {
    "page": 2,
    "limit": 10,
    "total_items": 47,
    "total_pages": 5,
    "has_next": true,
    "has_previous": true
  }
}
```

---

## 4. Visual Flow

```
Client                        Server                         Database
  |                             |                               |
  |-- GET /movies?page=2&limit=10 -->                           |
  |                             |                               |
  |                             |-- SELECT ... LIMIT 10 OFFSET 10 -->
  |                             |<-- 10 movie rows -------------|
  |                             |                               |
  |                             |-- SELECT COUNT(*) ----------->|
  |                             |<-- total_count = 47 ----------|
  |                             |                               |
  |                             | Calculate:                    |
  |                             |   total_pages = CEIL(47/10)=5 |
  |                             |   has_next = (2 < 5) = true   |
  |                             |   has_previous = (2 > 1)=true |
  |                             |                               |
  |<-- JSON response -----------|                               |
```

---

## 5. Offset vs Cursor-Based Pagination

The above is **offset-based** pagination (`LIMIT/OFFSET`). It's simple but has a problem: **large offsets are slow** because the DB must scan and discard all skipped rows.

For the movie browsing use case, offset pagination is fine because:
- Movie catalog is small (~10K movies)
- Users rarely go past page 5

But for **booking history** (potentially millions of records), use **cursor-based pagination** instead:

```
GET /bookings?user_id=user_123&cursor=book_def456&limit=10
```

```sql
-- Cursor-based: no OFFSET, uses WHERE instead
SELECT booking_id, show_id, total_amount, status, booked_at
FROM bookings
WHERE user_id = 'user_123'
  AND booking_id > 'book_def456'   -- cursor = last seen ID
ORDER BY booking_id ASC
LIMIT 10;
```

**Cursor-based Response:**
```json
{
  "bookings": [ "..." ],
  "pagination": {
    "next_cursor": "book_ghi789",
    "has_next": true
  }
}
```

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Offset** (`LIMIT/OFFSET`) | Simple, supports "jump to page N" | Slow for large offsets, inconsistent if data changes | Small datasets (movies, showtimes) |
| **Cursor** (`WHERE id > cursor`) | Fast at any depth, consistent | Can't jump to arbitrary page | Large datasets (bookings, history) |

---

# Elasticsearch Consistency Model

## Write Consistency

- When you index a document, it's **not immediately searchable**
- Elasticsearch writes to an in-memory buffer first, then **refreshes** (flushes to a searchable segment) every **1 second** by default
- So there's a **~1 second lag** between writing and being able to search for it

```
Write → In-Memory Buffer → [1 sec refresh] → Searchable Segment → [30 min flush] → Disk
```

## Read Consistency

| Operation | Consistency | Latency |
|-----------|------------|---------|
| **Search** (`GET /index/_search`) | **Eventual** (~1 sec stale) | Fast |
| **Get by ID** (`GET /index/_doc/id`) | **Real-time** (reads from translog) | Fast |

- **Searching** may miss documents written <1 second ago
- **Getting by ID** is real-time because it checks the transaction log directly, bypassing the refresh cycle

## In the Context of Movie Ticket Booking

This is why we use Elasticsearch **only for browsing/discovery** and NOT for seat status:

| Data | Store | Why |
|------|-------|-----|
| Movie search, filters | **Elasticsearch** ✅ | Eventual consistency is fine — a new movie appearing 1 sec late is acceptable |
| Seat availability | **PostgreSQL + Redis** ✅ | Needs **strong consistency** — can't sell the same seat twice |
| Booking records | **PostgreSQL** ✅ | Needs **ACID guarantees** |

## Can You Force Strong Consistency in ES?

Yes, but at a **heavy performance cost**:

```
# Force refresh after write (makes it immediately searchable)
POST /movies/_doc/mov_123?refresh=true
```

- `refresh=true` — blocks until searchable (slow, not recommended at scale)
- `refresh=wait_for` — waits for next natural refresh (up to 1 sec)
- `refresh=false` — default, fastest, eventually consistent

> **Bottom line:** Elasticsearch is optimized for **search speed over consistency**. For the movie booking system, that's perfectly fine for movie/theater discovery, but you'd never use it for anything requiring strong consistency like seat inventory.

---

# How Elasticsearch & PostgreSQL Work Together

## PostgreSQL is the **Source of Truth** — it has EVERYTHING

```
movies table (PostgreSQL)
├── movie_id          (UUID)
├── title             (VARCHAR)
├── description       (TEXT)
├── duration_minutes  (INT)
├── genre             (VARCHAR)
├── language          (VARCHAR)
├── release_date      (DATE)
├── rating            (DECIMAL)
├── poster_url        (VARCHAR)
├── cast              (JSONB)        ← full cast details
├── director          (VARCHAR)
├── certification     (VARCHAR)      ← "PG-13", "R", etc.
├── created_at        (TIMESTAMP)
└── updated_at        (TIMESTAMP)
```

## Elasticsearch has a **Copy** — optimized for search

```
movies index (Elasticsearch)
├── movie_id          (keyword)       ← same ID, to link back to DB
├── title             (text)          ← analyzed for full-text search + fuzzy matching
├── title.keyword     (keyword)       ← exact match / sorting
├── description       (text)          ← searchable
├── genre             (keyword)       ← filterable
├── language          (keyword)       ← filterable
├── release_date      (date)          ← range queries
├── rating            (float)         ← sorting
├── cast              (text)          ← search by actor name
├── city_ids          (keyword[])     ← which cities this movie is showing in
└── poster_url        (keyword)       ← passed through, not searched
```

## The Key Difference

| Feature | PostgreSQL | Elasticsearch |
|---------|-----------|---------------|
| Full-text search ("avangers" → "Avengers") | ❌ Slow / basic `LIKE` | ✅ Fuzzy matching, typo tolerance |
| Autocomplete ("inc" → "Inception") | ❌ Not built for this | ✅ Edge n-gram analyzers |
| Filter by city + genre + language | ⚠️ Works but slower with complex joins | ✅ Blazing fast with inverted index |
| Search by actor name | ❌ Requires JSONB parsing | ✅ Full-text search on cast field |
| ACID transactions | ✅ Yes | ❌ No |
| Joins (movie → shows → theaters) | ✅ Yes | ❌ Denormalized, no joins |

## How Data Flows Between Them

```
Admin adds movie
       |
       v
  PostgreSQL          (write happens here FIRST — source of truth)
       |
       |  Sync mechanism (one of these):
       |  ├── CDC (Change Data Capture) via Debezium
       |  ├── Kafka event: MovieCreated / MovieUpdated
       |  └── Periodic sync job (every few minutes)
       |
       v
  Elasticsearch       (index updated — now searchable)
```

## Typical Search Flow

```
1. User types: "avengers action NYC"
        |
        v
2. Elasticsearch query:
   {
     "query": {
       "bool": {
         "must": [
           { "match": { "title": { "query": "avengers", "fuzziness": "AUTO" } } }
         ],
         "filter": [
           { "term": { "genre": "action" } },
           { "term": { "city_ids": "NYC" } }
         ]
       }
     },
     "sort": [{ "rating": "desc" }],
     "from": 0, "size": 10
   }
        |
        v
3. ES returns: [movie_id: "mov_123", movie_id: "mov_456", ...]
        |
        v
4. Two options here:
   Option A: ES already has enough data (title, poster, rating) → return directly
   Option B: Need extra details → fetch from PostgreSQL by movie_ids
```

**Option A** is preferred — denormalize enough data into ES so you don't need to hit PostgreSQL for search results. The DB is only hit when a user clicks into a specific movie's detail page.

## Summary

```
User searches "avengers"  →  Elasticsearch      →  fast fuzzy search, returns results
User clicks on a movie    →  PostgreSQL          →  full details, showtimes, reviews
User selects seats        →  Redis + PostgreSQL  →  strong consistency
User books tickets        →  PostgreSQL          →  ACID transaction
```

> **Think of it this way:**
> - **PostgreSQL** = the library's catalog system (accurate, complete, authoritative)
> - **Elasticsearch** = the library's search kiosk (fast, forgiving, helps you find things quickly)
> - They stay in sync, but if there's ever a conflict, PostgreSQL wins.

---

# Why Both Redis Cache & WebSocket for Seat Map?

```
Redis Cache    → "Here's what the seat map looks like RIGHT NOW" (snapshot)
WebSocket      → "Here's what just CHANGED" (delta stream)
```

You need BOTH because:
1. WebSocket can't give you history you missed
2. Database can't handle 10,000 simultaneous snapshot requests
3. Redis absorbs the thundering herd for pennies

## The Problem: WebSocket Only Sends Future Updates

WebSockets only push **changes** (deltas). They don't give you the **full current state**. Consider this timeline:

```
10:00:00 - Seats A1, A2 reserved by User X     ← WebSocket event sent
10:00:05 - Seat B3 reserved by User Y           ← WebSocket event sent
10:00:10 - Seat C5 reserved by User Z           ← WebSocket event sent

10:00:15 - YOU open the seat map                 ← 🤔 Now what?
```

When you join at `10:00:15`, you **missed all three events**. The WebSocket connection didn't exist yet, so those events were never delivered to you. Without a snapshot, your seat map would show A1, A2, B3, and C5 as "available" — **but they're already taken**.

This is why Step 1 (fetching the full seat map from Redis/DB) is essential. It gives you the **current state of every seat** at the moment you open the page. Only **after** you have this snapshot does the WebSocket take over, keeping your view in sync with future changes.

```
Step 1 (Redis/DB):  "Here are all 200 seats and their current status"   ← SNAPSHOT
Step 2 (WebSocket):  "Seat D4 just changed to reserved"                 ← DELTA
Step 2 (WebSocket):  "Seat A1 just changed to available (timeout)"      ← DELTA
```

> Without Step 1, Step 2 is meaningless — you'd be applying changes to something you never loaded.

## Flow: How They Work Together

```
User opens seat map
       |
       v
  Step 1: GET /shows/{id}/seats
       |
       v
  Redis cache hit? ──── Yes ──→ Return cached seat map (sub-ms)
       |
       No
       |
       v
  Query PostgreSQL → store in Redis (TTL=5s) → return
       |
       v
  Step 2: Open WebSocket, subscribe to show:{id}
       |
       v
  Step 3: Receive real-time deltas going forward
          { seat: "A1", status: "reserved" }
          { seat: "B2", status: "available" }  ← someone's reservation expired
```

---

# seat_layout (Screens table) vs show_seats table

## `seat_layout` (JSONB in Screens table) — Physical Layout / UI Template

Describes the **physical arrangement** of the screen — how seats are positioned in the theater. It's **static** and never changes unless the theater renovates.

```json
{
  "rows": 10,
  "columns": 15,
  "seats": [
    { "id": "A1", "row": "A", "col": 1, "type": "standard", "price_tier": "regular" },
    { "id": "A2", "row": "A", "col": 2, "type": "standard", "price_tier": "regular" },
    { "id": "A3", "row": "A", "col": 3, "type": "wheelchair", "price_tier": "regular" },
    { "id": "J8", "row": "J", "col": 8, "type": "recliner", "price_tier": "premium" }
  ],
  "aisles": [4, 12],
  "screen_position": "top",
  "blocked_seats": ["F7"]
}
```

**It answers:** Where does each seat physically sit? Where are the aisles? Which seats are premium recliners? Where's the wheelchair spot? Which seat has a pillar blocking the view?

## `show_seats` table — Live Booking Status Per Show

Tracks **who booked what** for a **specific show**. It changes constantly as users reserve and book.

```
show_id    | seat_id | status    | reserved_by | reserved_at
-----------|---------|-----------|-------------|------------------
show_789   | A1      | available | NULL        | NULL
show_789   | A2      | reserved  | user_123    | 2024-01-15 10:00
show_789   | A3      | booked    | user_456    | 2024-01-15 09:30
```

**It answers:** Is seat A2 taken for the 7 PM show tonight? Who reserved it? When?

## Comparison

```
                     seat_layout                    show_seats
                     (Screens table)                (per show)
────────────────────────────────────────────────────────────────
Scope                1 per screen                   1 per seat per show
                     (200 seats in layout)          (200 rows × 4 shows/day)

Changes?             Almost never                   Every few seconds
                     (theater renovation)           (reserves, bookings)

Contains             Position, type, price tier,    Status (available/reserved/booked),
                     aisles, gaps, blocked seats    user_id, timestamp

Used for             Rendering the seat map UI      Coloring seats green/gray
                     (where to draw each seat)      (available or taken)
────────────────────────────────────────────────────────────────
```

## How They Work Together to Render the Seat Map

```
Step 1: Fetch seat_layout from Screens table
        → "Screen 3 has 10 rows × 15 cols, aisle at col 4 and 12,
           row J is recliners, seat F7 is blocked"

Step 2: Fetch show_seats for this specific show
        → "A1=available, A2=reserved, A3=booked, ..."

Step 3: Merge them in frontend
        → Draw each seat at correct position (from layout)
        → Color it green/gray/red (from status)
```

```
Without seat_layout:  You know A1 is "available" but not WHERE to draw it on screen
Without show_seats:   You know A1 is a "recliner in row J" but not if someone bought it
```

> **Think of it this way:**
> - `seat_layout` = the **blueprint** of the theater (like an architect's floor plan)
> - `show_seats` = the **attendance sheet** for tonight's 7 PM show (who's sitting where)
> - The blueprint doesn't change show to show. The attendance sheet is different for every show.

---

# How Redis Handles Two Users Competing for the Same Seat

## Scenario

- **User A** wants seats: `A1, A2, A3`
- **User B** wants seats: `A3, A4, A5`
- Seat **A3 is the conflict**

Both click "Reserve" at almost the same time.

## Step-by-Step: What Happens Inside Redis

The Lua script tries to acquire locks for **all seats atomically** (all-or-nothing). Only one script can execute at a time in Redis (Redis is **single-threaded**).

```
t=0ms   User A's request arrives at Redis FIRST (even by 1ms)
        Lua script runs:
        ├── SETNX lock:show:789:seat:A1 → ✅ Key didn't exist, LOCKED
        ├── SETNX lock:show:789:seat:A2 → ✅ Key didn't exist, LOCKED
        └── SETNX lock:show:789:seat:A3 → ✅ Key didn't exist, LOCKED
        Result: ALL 3 acquired → User A gets reservation ✅

t=1ms   User B's request arrives at Redis
        Lua script runs:
        ├── SETNX lock:show:789:seat:A3 → ❌ Key EXISTS (User A has it!)
        │
        │   CONFLICT DETECTED! Rollback:
        │   (no locks were acquired before A3, so nothing to release)
        │
        └── Return FAIL immediately
        Result: User B gets 409 Conflict ❌
```

## What If User B Had Some Seats Before the Conflict?

Say User B wants `A4, A5, A3` (in that order):

```
t=1ms   User B's Lua script runs:
        ├── SETNX lock:show:789:seat:A4 → ✅ LOCKED
        ├── SETNX lock:show:789:seat:A5 → ✅ LOCKED
        ├── SETNX lock:show:789:seat:A3 → ❌ CONFLICT!
        │
        │   Rollback ALL locks acquired so far:
        │   DEL lock:show:789:seat:A4    ← release
        │   DEL lock:show:789:seat:A5    ← release
        │
        └── Return FAIL
        Result: User B gets 409 Conflict, A4 & A5 released back ❌
```

**This is critical** — we don't keep A4, A5 and fail on just A3. It's **all-or-nothing**. Nobody wants 2 out of 3 seats.

## The Lua Script That Does This

```lua
-- Runs ATOMICALLY in Redis (single-threaded, no interruption)
local locks_acquired = {}

for i, seat_key in ipairs(KEYS) do
    local result = redis.call('SET', seat_key, ARGV[1], 'NX', 'EX', 600)
    --                                         ^^        ^^
    --                                    set-if-not-    10 min
    --                                      exists       expiry

    if result then
        table.insert(locks_acquired, seat_key)
    else
        -- CONFLICT: this seat is taken
        -- Rollback: release ALL locks we acquired so far
        for j, acquired_key in ipairs(locks_acquired) do
            redis.call('DEL', acquired_key)
        end
        return nil  -- FAIL
    end
end

return locks_acquired  -- SUCCESS: all seats locked
```

## ⚠️ WHY THIS WORKS: REDIS IS SINGLE-THREADED — ALL SCRIPTS RUN SEQUENTIALLY

> ### **🔴 CRITICAL: Redis executes ALL commands and Lua scripts ONE AT A TIME in a single thread. Even if 10,000 requests arrive simultaneously, they are queued and processed sequentially. This is THE reason double-booking is impossible.**

```
Even if 10,000 users send requests at the same millisecond:

Redis processes them ONE BY ONE in a queue:

  Request Queue:     [User A] → [User B] → [User C] → [User D] → ...
                        ↓
  Processing:        User A's Lua script runs COMPLETELY
                        ↓
                     User B's Lua script runs COMPLETELY
                        ↓
                     User C's Lua script runs COMPLETELY

  No two scripts run at the same time = NO RACE CONDITION
```

This is the superpower of Redis — **single-threaded execution means Lua scripts are naturally atomic.** No need for complex mutexes or database locks.

## Full Flow: What Each User Sees

```
User A                                          User B
───────                                         ───────
Selects A1, A2, A3                              Selects A3, A4, A5
Clicks "Reserve"                                Clicks "Reserve"
     |                                               |
     v                                               v
Redis: Lua script                               Redis: Lua script
locks A1 ✅                                     tries A3 ❌ (User A has it)
locks A2 ✅                                     ROLLBACK everything
locks A3 ✅                                          |
     |                                               v
     v                                          409 Conflict Response:
201 Created:                                    {
{                                                 "error": "seats_unavailable",
  "reservation_id": "res_abc",                    "unavailable_seats": ["A3"],
  "seats": ["A1","A2","A3"],                      "message": "Seat A3 is already
  "expires_at": "10:10:00"                         reserved by another user"
}                                               }
     |                                               |
     v                                               v
Shows payment page                              Shows error:
with 10-min countdown                           "Seat A3 is unavailable.
                                                 Please select different seats."
                                                      |
                                                      v
                                                User B picks A4, A5, A6 instead
                                                Clicks "Reserve" again → ✅ Success
```

> **Key takeaway:** Redis single-threaded execution + Lua script atomicity + all-or-nothing locking = **it's physically impossible for two users to lock the same seat.** Whoever's request reaches Redis first (even by 1 nanosecond) wins.

---

# Spring Boot + Redis Lua Script Integration

## 1. Dependency (`pom.xml`)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

## 2. Lua Script File (`src/main/resources/scripts/reserve-seats.lua`)

```lua
local locks_acquired = {}

for i, seat_key in ipairs(KEYS) do
    local result = redis.call('SET', seat_key, ARGV[1], 'NX', 'EX', tonumber(ARGV[2]))
    if result then
        table.insert(locks_acquired, seat_key)
    else
        for j, acquired_key in ipairs(locks_acquired) do
            redis.call('DEL', acquired_key)
        end
        return nil
    end
end

return locks_acquired
```

## 3. Service Class

```java
@Service
public class SeatReservationService {

    private final StringRedisTemplate redisTemplate;
    private final RedisScript<List> reserveScript;

    public SeatReservationService(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;

        // Load Lua script from resources folder
        this.reserveScript = RedisScript.of(
            new ClassPathResource("scripts/reserve-seats.lua"),
            List.class
        );
    }

    public ReservationResult reserveSeats(String showId, List<String> seatIds, String userId) {

        // Build Redis keys: lock:show:789:seat:A1, lock:show:789:seat:A2, ...
        List<String> keys = seatIds.stream()
            .map(seatId -> "lock:show:" + showId + ":seat:" + seatId)
            .toList();

        String userValue = userId + ":" + System.currentTimeMillis();
        String ttlSeconds = "600"; // 10 minutes

        // Execute Lua script atomically
        List<String> result = redisTemplate.execute(
            reserveScript,
            keys,           // KEYS[] in Lua
            userValue,      // ARGV[1] in Lua
            ttlSeconds      // ARGV[2] in Lua
        );

        if (result == null) {
            return ReservationResult.conflict("One or more seats are unavailable");
        }

        return ReservationResult.success(seatIds, userId);
    }
}
```

## 4. Controller

```java
@RestController
@RequestMapping("/shows")
public class SeatController {

    private final SeatReservationService reservationService;

    @PostMapping("/{showId}/reserve")
    public ResponseEntity<?> reserveSeats(
            @PathVariable String showId,
            @RequestBody ReserveRequest request) {

        ReservationResult result = reservationService.reserveSeats(
            showId, request.getSeatIds(), request.getUserId()
        );

        if (result.isSuccess()) {
            return ResponseEntity.status(201).body(result);
        }
        return ResponseEntity.status(409).body(result); // Conflict
    }
}
```

## How Spring Boot Maps to Redis

```
Spring Boot                          Redis
───────────                          ─────
keys = ["lock:show:789:seat:A1",     KEYS[1], KEYS[2], KEYS[3]
        "lock:show:789:seat:A2",
        "lock:show:789:seat:A3"]

args = ["user_123:170531",           ARGV[1] = user value
        "600"]                       ARGV[2] = TTL seconds

redisTemplate.execute(script,        → script runs atomically
    keys, args)                        in Redis, returns result
```

> **Key point:** `redisTemplate.execute()` sends the entire Lua script to Redis, which runs it **atomically** in its single thread. Spring Boot just sends and receives — all the locking logic happens inside Redis.

---

# What "Single-Threaded" Actually Means in Redis

## Thread = Worker

A multi-threaded system (like a bank with 10 counters) processes multiple customers simultaneously. Redis is like a bank with **1 counter** — but that 1 counter is extraordinarily fast.

```
Multi-threaded (e.g., PostgreSQL):

  Request 1 ──→ [Worker 1] ──→ processes simultaneously
  Request 2 ──→ [Worker 2] ──→ processes simultaneously
  Request 3 ──→ [Worker 3] ──→ processes simultaneously
  
  ⚠️ Problem: Worker 1 and Worker 2 might touch the same seat at the same time
     → Need complex locks, mutexes, transactions to prevent conflicts


Single-threaded (Redis):

  Request 1 ──┐
  Request 2 ──┤
  Request 3 ──┼──→ [QUEUE] ──→ [Single Worker] ──→ one at a time
  Request 4 ──┤
  Request 5 ──┘

  ✅ Impossible for two requests to process at the same time
     → No race conditions BY DESIGN
```

## Can Redis Handle 10K Requests Sequentially? YES.

Redis is **insanely fast**. Each operation takes **microseconds** (not milliseconds):

```
Single Redis operation:     ~1 microsecond  (0.001 ms)
Lua script (5 operations):  ~5 microseconds (0.005 ms)

10,000 Lua scripts:         ~50 milliseconds (0.05 seconds)
```

| Requests | Time to Process All | Perspective |
|----------|-------------------|-------------|
| 100 | ~0.5 ms | Instant |
| 1,000 | ~5 ms | Still instant |
| 10,000 | ~50 ms | Blink of an eye |
| 100,000 | ~500 ms | Half a second |

Redis handles **100,000+ ops/sec** on a single thread because:
1. Everything runs **in memory** (no disk I/O)
2. Operations are **simple** (SET, GET, SETNX) — not complex SQL joins
3. No **context switching** overhead (single thread = no thread scheduling)

## 10K Users Booking the Same Seat

```
10:00:00.000  Request 1 arrives → SETNX seat:A1 → ✅ LOCKED (User 1 wins!)
10:00:00.001  Request 2 arrives → SETNX seat:A1 → ❌ EXISTS (fail)
10:00:00.002  Request 3 arrives → SETNX seat:A1 → ❌ EXISTS (fail)
10:00:00.003  Request 4 arrives → SETNX seat:A1 → ❌ EXISTS (fail)
...
10:00:00.050  Request 10,000    → SETNX seat:A1 → ❌ EXISTS (fail)

Total time: ~50ms
Result: 1 winner, 9,999 instant failures with "seat unavailable"
```

**The first request wins. The remaining 9,999 fail immediately** — they don't wait or retry.

## Why Not Multi-Threaded? Wouldn't That Be Faster?

```
Multi-threaded approach:

  Thread 1: Read seat A1 → status = "available"     ← both read at the same time
  Thread 2: Read seat A1 → status = "available"     ← both see "available"
  
  Thread 1: Write seat A1 → status = "reserved" ✅
  Thread 2: Write seat A1 → status = "reserved" ✅  ← DOUBLE BOOKING! 💀

  To fix: Need mutexes, semaphores, database locks, SELECT FOR UPDATE
          All of which ADD latency and complexity


Single-threaded approach (Redis):

  [Queue]: Request 1 → Request 2
  
  Process Request 1: SETNX seat:A1 → ✅ (key created)
  Process Request 2: SETNX seat:A1 → ❌ (key exists)
  
  → No locks needed. Correctness is FREE because of sequential execution.
```

> **TL;DR:** "Single-threaded" means Redis has ONE worker processing ONE command at a time. Yes, it handles 10K requests sequentially — but each takes ~5 microseconds, so all 10K finish in ~50ms. The single thread is actually the **feature, not the limitation**, because it makes race conditions impossible.

---

# 10K Requests Locking DIFFERENT Seats — Still Sequential?

**Yes, still sequential.** Even if all 10K requests want different seats, Redis processes them one by one. But it doesn't matter because each is so fast:

```
10:00:00.000  User 1:  SETNX seat:A1 → ✅ (no conflict, instant)
10:00:00.005  User 2:  SETNX seat:B3 → ✅ (no conflict, instant)
10:00:00.010  User 3:  SETNX seat:C7 → ✅ (no conflict, instant)
10:00:00.015  User 4:  SETNX seat:D2 → ✅ (no conflict, instant)
...
10:00:00.050  User 10K: SETNX seat:F9 → ✅ (no conflict, instant)

Total time: ~50ms
Result: ALL 10,000 succeed ✅ (no conflicts = everyone wins)
```

**50ms for 10,000 bookings.** Each user waits at most 50ms. That's unnoticeable.

## Isn't This a Bottleneck? Redis vs PostgreSQL Comparison

```
Sequential but fast (Redis):
  10,000 requests × 5μs each = 50ms total
  Last user waits: 50ms  ← totally fine

Parallel but slow (PostgreSQL with row locks):
  10,000 requests × 5ms each = but with lock contention...
  Lock waits, deadlocks, retries = 200-500ms per request
  Last user waits: could be seconds  ← worse despite being "parallel"
```

| | Redis (Sequential) | PostgreSQL (Parallel with Locks) |
|--|---|---|
| **Per operation** | ~5 μs | ~5 ms (1000x slower) |
| **10K operations** | ~50 ms total | Varies wildly due to lock contention |
| **Conflicts?** | Handled naturally | Needs explicit `SELECT FOR UPDATE` |
| **Can deadlock?** | ❌ Impossible | ✅ Possible with multi-row locks |

## When Does Single-Threaded Actually Become a Problem?

Only at **millions** of requests per second:

```
Redis limit:     ~100,000 ops/sec on single thread
Our peak load:   ~1,200 seat requests/sec (from the estimates)

Headroom:        100,000 / 1,200 = 83x buffer 🟢

Even during flash sales (10x spike):
                 100,000 / 12,000 = 8x buffer 🟢
```

## Scaling Beyond: Redis Cluster

If you truly need more, **Redis Cluster** shards keys across multiple nodes. Different shows go to different nodes, so they process in parallel:

```
Redis Cluster (3 nodes):

  Node 1: show_123 seats processed here     ← single-threaded within this node
  Node 2: show_456 seats processed here     ← single-threaded within this node
  Node 3: show_789 seats processed here     ← single-threaded within this node

  3 shows processing in PARALLEL across nodes
  But within each show, still SEQUENTIAL (which is what we want!)
```

> **TL;DR:** Yes, 10K different-seat requests are still sequential. But at 5μs each, they ALL finish in 50ms — faster than a single PostgreSQL query with a lock. If you ever need more, Redis Cluster adds parallelism across different shows while keeping same-show requests sequential (exactly what we need).

---

# Why Kafka for Notifications Instead of Direct API?

## The Problem with Direct API Call

```
Booking Service                    Notification Service
     |                                    |
     |--- POST /send-email -------------->|
     |         (synchronous call)         |
     |                                    |--- Sending email via SMTP...
     |                                    |--- Takes 2-5 seconds...
     |                                    |--- Maybe SMTP server is down? 💀
     |<--- 500 Internal Server Error -----|
     |
     v
  What now? Booking already confirmed, payment already taken.
  Do we fail the entire booking because email failed? 😱
```

**The booking response is BLOCKED** until the email is sent. If the email service is slow or down, the user's booking gets delayed or fails.

## With Kafka (Async)

```
Booking Service              Kafka              Notification Service
     |                         |                        |
     |-- Publish event ------->|                        |
     |   (takes ~1ms)          |                        |
     |                         |                        |
     v                         |                        |
  Return 201 to user           |--- Deliver event ----->|
  INSTANTLY ✅                 |                        |--- Send email (2-5 sec)
                               |                        |--- If fails, RETRY
                               |                        |--- Success ✅
```

## Why Kafka Specifically?

### 1. Decoupling — Booking Shouldn't Care About Notifications

```
Direct API: Booking fails if Email service is down     ❌
Kafka:      Booking succeeds regardless                ✅
            Email service can be down for 10 minutes,
            comes back up, processes the queue          ✅
```

### 2. Guaranteed Delivery — Messages Don't Get Lost

```
Direct API: Network blip → request lost → no email → nobody knows  ❌
Kafka:      Message persisted to disk → consumer picks it up
            If consumer crashes → message stays in queue
            Consumer restarts → processes the message              ✅
```

### 3. Retry Without Blocking the User

```
Direct API retry:
  Booking Service: "Email failed, let me retry..."
  User: waiting... waiting... 😤

Kafka retry:
  Notification Service: "Email failed, I'll retry in 30 seconds"
  User: already got their booking confirmation ✅
```

### 4. Multiple Consumers — One Event, Many Actions

```
Booking Service publishes ONE event: "BookingConfirmed"

Kafka fans it out to MULTIPLE consumers:

  BookingConfirmed ──→ Email Service     → sends confirmation email
                   ──→ SMS Service       → sends text message
                   ──→ Analytics Service → tracks booking metrics
                   ──→ Loyalty Service   → awards reward points
                   ──→ Push Notification → sends app notification

With direct API: Booking Service calls ALL 5 services (tightly coupled)
Adding a new consumer? Change Booking Service code. ❌
With Kafka? Just add a new consumer. No code changes. ✅
```

### 5. Handles Traffic Spikes

```
Flash sale: 10,000 bookings in 1 minute

Direct API: 10,000 simultaneous email requests → Email service crashes 💀
Kafka:      10,000 events queued → Email service processes at its own pace
            All emails sent in ~100 seconds, no crash ✅
```

## Summary

| | Direct API | Kafka |
|--|-----------|-------|
| **User wait time** | Blocked until email sent (2-5s) | Instant response (~1ms) |
| **If email service is down** | Booking fails or no email | Email sent when service recovers |
| **Message lost?** | Possible (network failure) | No — persisted to disk |
| **Adding new consumers** | Change booking code | Just add consumer, zero code change |
| **Traffic spikes** | Email service crashes | Queue absorbs spike |

> **Rule of thumb:** If the downstream action (email, SMS, analytics) is NOT required for the user's response, put it behind a message queue.

---

# If Kafka Is So Good, Why Not Use It Everywhere Instead of API?

## The Core Difference: Kafka is Fire-and-Forget, APIs Get Answers Back

```
API (Synchronous):
  Client: "Are seats A1, A2 available?"
  Server: "Yes, here's the seat map" ← client NEEDS this answer to show UI
  
Kafka (Asynchronous):
  Producer: "Here's a booking event" → drops into queue → walks away
  Consumer: picks it up whenever     → producer never gets a response
```

## Where Kafka CANNOT Replace API

### 1. User Needs an Immediate Response

```
User opens seat map:
  
  With API:   GET /shows/789/seats → 200 OK { seats: [...] } → render ✅
  With Kafka: Publish "GetSeats" event → ??? → blank screen 😐
```

### 2. User Needs to Know If It Worked

```
User clicks "Reserve seats":

  With API:   POST /reserve → 201 Created OR 409 Conflict   ✅ (user KNOWS)
  With Kafka: Publish "ReserveSeats" → ??? did it work? 🤷
```

### 3. Sequential Operations That Depend on Each Other

```
Step 1: Search movies     → need results to pick a movie
Step 2: Get showtimes     → need showtimes to pick one
Step 3: View seat map     → need seat data to select seats
Step 4: Reserve seats     → need confirmation to proceed
Step 5: Process payment   → need success/failure immediately

Each step DEPENDS on the previous step's response.
Kafka can't chain these — there's no "response" concept.
```

## The Rule: When to Use What

```
Does the caller NEED a response to continue?
│
├── YES → Use API (synchronous)
│         ├── GET /movies          (need data to show UI)
│         ├── POST /reserve        (need success or conflict?)
│         ├── POST /payment        (need charged or declined?)
│         └── GET /bookings        (need data to show history)
│
└── NO  → Use Kafka (asynchronous)
          ├── Send confirmation email     (user doesn't wait)
          ├── Send SMS notification        (fire and forget)
          ├── Update analytics dashboard   (background)
          ├── Award loyalty points         (can happen later)
          └── Generate PDF ticket          (async)
```

## In Our Movie Booking System

| Operation | API or Kafka? | Why? |
|-----------|:---:|------|
| Search movies | **API** | User needs results to browse |
| Get showtimes | **API** | User needs data to pick a show |
| View seat map | **API** | User needs seat data NOW |
| Reserve seats | **API** | User needs instant success/failure |
| Process payment | **API** | User needs to know if card was charged |
| Send email | **Kafka** | User already has booking, email can wait |
| Send SMS | **Kafka** | Background task |
| Award loyalty points | **Kafka** | Can happen minutes later |
| Update analytics | **Kafka** | User doesn't care about this |

> **TL;DR:** Kafka is great when the producer doesn't need a response — "do this whenever you can." APIs are essential when the caller needs an answer — "tell me right now." Everything the **user interacts with** uses APIs. Everything that happens **after the user gets their response** goes through Kafka.

---

# Without Redis: All-or-Nothing Seat Booking Using PostgreSQL

## Scenario

- **User A** wants: `A1, A2, A3`
- **User B** wants: `A3, A4, A5`
- Seat **A3 is the conflict**

## The SQL Approach: Transaction + SELECT FOR UPDATE

### User A's Request (arrives first)

```sql
BEGIN;

-- Lock the rows we want (other transactions will WAIT if they touch these rows)
SELECT seat_id, status 
FROM show_seats 
WHERE show_id = 'show_789' 
  AND seat_id IN ('A1', 'A2', 'A3') 
  AND status = 'available'
FOR UPDATE;

-- App checks: got 3 rows back? Yes → all available → proceed
UPDATE show_seats 
SET status = 'reserved', reserved_by = 'user_A', reserved_at = NOW()
WHERE show_id = 'show_789' 
  AND seat_id IN ('A1', 'A2', 'A3');

COMMIT;  -- Locks released
```

### User B's Request (arrives almost simultaneously)

```sql
BEGIN;

-- Tries to lock A3, A4, A5
-- But A3 is ALREADY LOCKED by User A's transaction
-- User B's query WAITS here... ⏳ (blocked until User A commits)
SELECT seat_id, status 
FROM show_seats 
WHERE show_id = 'show_789' 
  AND seat_id IN ('A3', 'A4', 'A5') 
  AND status = 'available'
FOR UPDATE;

-- After User A commits, lock released, query runs
-- A3 is now 'reserved' → doesn't match status='available'
-- Only A4, A5 returned (count=2, needed 3) → ROLLBACK!
ROLLBACK;
```

## Timeline

```
Time     User A                              User B
────     ──────                              ──────
t=0      BEGIN                               BEGIN
t=1      SELECT FOR UPDATE (A1,A2,A3)        SELECT FOR UPDATE (A3,A4,A5)
         → Locks A1, A2, A3 ✅               → A3 is locked by User A
                                             → BLOCKED, WAITING... ⏳
t=2      UPDATE → reserved ✅                   (still waiting)
t=3      COMMIT → locks released ✅           → Unblocked! Query runs now
                                             → A3 is 'reserved', not 'available'
                                             → Only A4, A5 returned (count=2)
                                             → Need 3, got 2 → ROLLBACK ❌
```

## How SELECT FOR UPDATE Works

```
Normal SELECT:
  "Let me READ these rows" → others can also read AND write

SELECT FOR UPDATE:
  "Let me READ these rows AND LOCK THEM" → other transactions:
    ├── Can still READ (normal SELECT)
    └── CANNOT write or lock → they WAIT ⏳

Lock held until:
  ├── COMMIT   → changes saved, lock released
  └── ROLLBACK → changes discarded, lock released
```

---

# Where Does the "All-or-Nothing" Check Happen?

> **⚠️ Important:** The SQL query does NOT enforce "all or nothing" by itself. The check happens in your **application code**.

## What the Query Actually Returns

```sql
-- You asked for A1, A2, A3
-- But A2 is already 'reserved' (not 'available')

SELECT seat_id, status 
FROM show_seats 
WHERE show_id = 'show_789' 
  AND seat_id IN ('A1', 'A2', 'A3') 
  AND status = 'available'    ← A2 doesn't match this filter
FOR UPDATE;
```

**Result:**
```
seat_id | status
--------|----------
A1      | available     ← matched
A3      | available     ← matched

(2 rows)      ← A2 is MISSING because it's 'reserved', not 'available'
```

The query doesn't fail — it just returns fewer rows. A2 is simply filtered out.

## Your Application Code Does the Check

```java
// You asked for 3 seats
List<String> requestedSeats = List.of("A1", "A2", "A3");  // count = 3

// Query returned only 2 (A1, A3)
List<String> availableSeats = jdbcTemplate.queryForList(sql, ...);  // count = 2

// YOUR code checks:
if (availableSeats.size() != requestedSeats.size()) {
    // 2 ≠ 3 → NOT all seats are available!
    
    // Find which seats are unavailable
    Set<String> unavailable = new HashSet<>(requestedSeats);
    unavailable.removeAll(availableSeats);
    // unavailable = ["A2"]
    
    throw new SeatsUnavailableException("Seats unavailable: " + unavailable);
    // @Transactional → auto ROLLBACK → locks on A1, A3 released
}
```

## Full Flow

```
User wants: A1, A2, A3 (A2 is already reserved)

Step 1: SELECT ... WHERE seat_id IN (A1,A2,A3) AND status='available' FOR UPDATE
        → Returns: [A1, A3]  (only 2 rows, A2 filtered out)
        → A1 and A3 are now LOCKED

Step 2: App checks: returned 2 rows, but requested 3
        → 2 ≠ 3 → ROLLBACK!

Step 3: ROLLBACK releases locks on A1 and A3
        → A1 and A3 are free again for other users

Step 4: Return 409 Conflict: "Seat A2 is unavailable"
```

## Spring Boot Service (Complete Code)

```java
@Service
@Transactional
public class SeatReservationService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public ReservationResult reserveSeats(String showId, List<String> seatIds, String userId) {
        
        // Step 1: Lock rows + check availability
        String placeholders = seatIds.stream().map(s -> "?").collect(Collectors.joining(","));
        String sql = "SELECT seat_id FROM show_seats " +
                     "WHERE show_id = ? AND seat_id IN (" + placeholders + ") " +
                     "AND status = 'available' FOR UPDATE";
        
        List<Object> params = new ArrayList<>();
        params.add(showId);
        params.addAll(seatIds);
        
        List<String> availableSeats = jdbcTemplate.queryForList(
            sql, params.toArray(), String.class
        );
        
        // Step 2: All-or-nothing check (THIS is where the magic happens)
        if (availableSeats.size() != seatIds.size()) {
            Set<String> unavailable = new HashSet<>(seatIds);
            unavailable.removeAll(new HashSet<>(availableSeats));
            throw new SeatsUnavailableException(unavailable);
            // @Transactional → auto ROLLBACK → all locks released
        }
        
        // Step 3: All available → reserve them
        String updateSql = "UPDATE show_seats SET status = 'reserved', " +
                          "reserved_by = ?, reserved_at = NOW() " +
                          "WHERE show_id = ? AND seat_id IN (" + placeholders + ")";
        
        List<Object> updateParams = new ArrayList<>();
        updateParams.add(userId);
        updateParams.add(showId);
        updateParams.addAll(seatIds);
        
        jdbcTemplate.update(updateSql, updateParams.toArray());
        
        return ReservationResult.success(seatIds, userId);
    }
}
```

## Redis vs PostgreSQL FOR UPDATE

| | Redis (Lua + SETNX) | PostgreSQL (SELECT FOR UPDATE) |
|--|---|---|
| **Speed** | ~5 μs per operation | ~5 ms per operation (1000x slower) |
| **Conflicting requests** | Fail instantly | WAIT until lock released (blocking) |
| **10K same-seat requests** | ~50ms, 9,999 instant failures | Queued, each waits — could take seconds |
| **Deadlock possible?** | ❌ No (single-threaded) | ⚠️ Yes (if lock order differs) |
| **Auto-expiry** | ✅ Built-in TTL | ❌ Need background job for cleanup |
| **Complexity** | Need Redis infrastructure | Just your existing database |
| **Best for** | High-concurrency, flash sales | Low-medium traffic, simpler setups |

> **TL;DR:** PostgreSQL CAN do all-or-nothing seat booking using `SELECT FOR UPDATE`. The query returns only available seats, and your **application code** checks if `returned count == requested count`. If not, `ROLLBACK` releases all locks. It works correctly but is slower under high concurrency compared to Redis.

---

# Virtual Waiting Room with Redis — Deep Dive

## The Problem: 100,000 Users Hit the System at 10:00:00 AM

```
Without waiting room:

  10:00:00 AM — Avengers tickets go on sale
  
  100,000 users simultaneously:
  → 100,000 seat map requests → API servers overwhelmed
  → 100,000 WebSocket connections → WebSocket servers crash
  → 100,000 payment attempts → Payment gateway rate-limits you
  → Database connections exhausted → everything crashes 💀

  It's not about Redis being slow — it's about EVERYTHING ELSE dying.
```

## The Solution: Queue Users, Let Them In Gradually

```
100,000 users arrive at 10:00 AM

  ┌─────────────────────────────────────────────────┐
  │              WAITING ROOM                        │
  │                                                  │
  │  "You are #34,521 in queue"                     │
  │  "Estimated wait: ~3 minutes"                   │
  │  ████████░░░░░░░░░░  35%                        │
  │                                                  │
  └─────────────────────────────────────────────────┘
         |
         | Let in 1,000 users/minute (controlled rate)
         v
  ┌─────────────────────────────────────────────────┐
  │           BOOKING SYSTEM                         │
  │  (only 1,000 concurrent users at a time)        │
  │  Seat selection → Reserve → Pay                 │
  └─────────────────────────────────────────────────┘
```

## How Redis Powers the Waiting Room

Redis uses a **Sorted Set** — an ordered list where each entry has a score (timestamp).

```
Redis Data Structure: Sorted Set

Key: waitingroom:show:789

Score (timestamp)     | Value (user)
──────────────────────|─────────────
1705312800.001        | user_1        ← arrived first
1705312800.002        | user_2
1705312800.003        | user_3
...
1705312800.100000     | user_100000   ← arrived last
```

## Redis Commands Used

```
Step 1: User arrives → add to queue
  ZADD waitingroom:show:789 1705312800.001 "user_1"
  → O(log N) — fast even with 100K entries

Step 2: What's my position?
  ZRANK waitingroom:show:789 "user_34521"
  → Returns: 34520 (0-indexed)
  → "You are #34,521 in queue"

Step 3: How many people ahead of me?
  ZCOUNT waitingroom:show:789 -inf (current_user_score)
  → Used to estimate wait time

Step 4: Let next batch in (every second, let in ~17 users)
  ZPOPMIN waitingroom:show:789 17
  → Removes and returns the 17 earliest users
  → These users get a TOKEN to enter the booking system

Step 5: Remove user who left/disconnected
  ZREM waitingroom:show:789 "user_5678"
```

## The Token System

When your turn comes, you get a **time-limited token** stored in Redis:

```
User's turn arrives:
  ZPOPMIN → removes user_1 from waiting room
  
  Generate token:
  SET booking_token:user_1 "show_789" EX 300
  ← Token valid for 5 minutes (300 seconds)

User enters booking system:
  API checks: GET booking_token:user_1
  → Exists? → Allow access to seat selection ✅
  → Missing? → "Your session expired, rejoin queue" ❌

User who skips the queue (no token):
  API checks: GET booking_token:hacker_user
  → Missing → "Please join the waiting room" 🚫
```

## Full Architecture

```
                         ┌──────────────┐
  100,000 users ────────→│ Load Balancer │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              Has token?              No token
                    │                       │
                    v                       v
          ┌─────────────────┐    ┌────────────────────┐
          │ Booking System   │    │ Waiting Room Page   │
          │ (seat map, pay)  │    │ (static HTML + WS)  │
          │ Max: 1000 users  │    │                      │
          └─────────────────┘    │ ZADD to Redis queue  │
                                 │ Show position via WS │
                                 │ Poll for turn         │
                                 └────────────────────┘
                                          │
                              Your turn → GET token
                                          │
                                 Redirect to Booking System
```

## Timeline: User Experience

```
10:00:00  User arrives → ZADD to sorted set → "You are #34,521"
10:00:05  Position update via WebSocket → "You are #33,200"
10:00:10  Position update → "You are #31,800"
...
10:02:30  Position update → "You are #500, almost there!"
10:03:00  ZPOPMIN → user popped from queue
          SET booking_token:user EX 300
          → "It's your turn! Redirecting to seat selection..."
10:03:01  User enters booking system with token
10:03:05  User sees seat map, selects seats
10:03:30  User reserves seats (normal Redis SETNX flow)
10:04:00  User pays, booking confirmed ✅
```

## Why Redis Sorted Set is Perfect for This

| Requirement | Redis Sorted Set | Why it works |
|---|---|---|
| Maintain order | Score = timestamp | First-come-first-served |
| Get position | `ZRANK` → O(log N) | Instant even with 100K users |
| Pop next batch | `ZPOPMIN` → O(log N) | Atomic removal + return |
| Handle disconnects | `ZREM` → O(log N) | Clean removal |
| Scale | 100K entries = ~10 MB | Fits easily in memory |
| Speed | All ops < 1ms | Real-time position updates |

## Without vs With Waiting Room

```
Without waiting room:                    With waiting room:
─────────────────────                    ─────────────────
100K hit API servers                     100K sit in lightweight queue
→ API servers: 💀                        → Queue page: static HTML, cheap
→ Database: 💀                           → Booking system: only 1K users
→ Redis: survives, but                   → Everything runs smoothly
   payment gateway: 💀                   → Everyone gets a fair turn
→ Users see errors, retry                → Users see position, wait calmly
→ More retries = more load               → No retry storms
→ Total meltdown                         → Controlled, predictable load
```

> **TL;DR:** The waiting room uses Redis Sorted Set (`ZADD`, `ZRANK`, `ZPOPMIN`) to queue 100K users and let them into the booking system at a controlled rate (~1000/minute). Users get a time-limited token when it's their turn. This protects the entire backend — not just Redis, but API servers, databases, payment gateways — from being overwhelmed.

---

# Other Strategies to Handle 100K+ Concurrent Users

## 1. Rate Limiting (at API Gateway)

Prevent any single user from overwhelming the system:

```
Per User:
  → Max 10 requests/second to seat map API
  → Max 3 reservation attempts/minute
  → Max 1 active reservation at a time

Per IP:
  → Max 50 requests/second (prevents bots)

Global:
  → Max 5,000 booking requests/second across all users
```

**Redis implementation:**

```
Redis key: ratelimit:user:123:reserve
Command:   INCR ratelimit:user:123:reserve
           EXPIRE ratelimit:user:123:reserve 60

  Attempt 1: INCR → count=1 → ✅ allowed
  Attempt 2: INCR → count=2 → ✅ allowed  
  Attempt 3: INCR → count=3 → ✅ allowed
  Attempt 4: INCR → count=4 → ❌ 429 Too Many Requests
  (key expires after 60 sec → counter resets)
```

## 2. Circuit Breaker (protect downstream services)

If the payment gateway starts failing, stop sending requests:

```
Normal:     Booking → Payment Gateway → ✅ working

3 failures: Booking → Payment Gateway → ❌ timeout ×3

Circuit OPENS:
  Booking → ⛔ "stop calling gateway" → return "try again in 30s"
  → No more requests hit the already-struggling gateway

After 30s (HALF-OPEN):
  Booking → send 1 test request → ✅ it's back! → CLOSE circuit
```

## 3. Load Shedding (intentionally drop requests)

```
Load 80%  → Accept all requests ✅
Load 90%  → Reject 20% of NEW requests ⚠️
Load 95%  → Reject 50% of NEW requests ⚠️⚠️
Load 99%  → Only allow existing reservations to complete 🛑

Priority:
  1. Users completing payment    → NEVER drop
  2. Users in seat selection     → Drop only if critical
  3. Users browsing movies       → Show cached/stale data
  4. New users arriving          → Redirect to waiting room
```

## 4. Caching Layers (reduce DB load)

```
100,000 requests arrive:
  → 80,000 served by CDN (static assets)        → DB: 0 queries
  → 15,000 served by Redis cache                 → DB: 0 queries
  → 4,000 served by application cache            → DB: 0 queries
  → 1,000 actually hit the database              → DB handles easily ✅
```

## 5. Auto-Scaling (horizontal)

```
Normal: 5 API servers, 3 Redis nodes, 2 DB read replicas

Traffic spike (CPU > 70%):
  → API servers: 5 → 20 (within 2 minutes)
  → DB read replicas: 2 → 5
  → WebSocket servers: 3 → 10

After spike ends → scale back down to save costs
```

## 6. Pre-computation (before the rush)

```
Before ticket sales open:
  → Pre-create all 200 show_seats rows (status='available')
  → Pre-warm Redis cache (seat layout, movie details)
  → Pre-create WebSocket pub/sub channels
  → Pre-create waiting room sorted set

Result: No cold-start penalty when 100K users arrive.
```

## How They All Work Together

```
                    100,000 users
                         │
              ┌──────────┴──────────┐
              │   CDN (Layer 1)      │  ← 80K requests gone
              └──────────┬──────────┘
                         │ 20,000
              ┌──────────┴──────────┐
              │   Rate Limiter       │  ← blocks bots (2K blocked)
              └──────────┬──────────┘
                         │ 18,000
              ┌──────────┴──────────┐
              │   Waiting Room       │  ← queues users, 1K/min in
              └──────────┬──────────┘
                         │ 1,000 at a time
              ┌──────────┴──────────┐
              │   Load Balancer      │  ← distributes across servers
              └──────────┬──────────┘
                         │
              ┌──────────┴──────────┐
              │   API Servers        │  ← Redis cache handles reads
              └──────────┬──────────┘
                         │ ~50 req/sec
              ┌──────────┴──────────┐
              │   PostgreSQL         │  ← handles easily ✅
              └─────────────────────┘
```

| Strategy | What It Protects | When It Kicks In |
|----------|-----------------|------------------|
| **CDN** | API servers | Always (static content) |
| **Rate Limiting** | All services | Per-user abuse |
| **Waiting Room** | Entire backend | Flash sales |
| **Circuit Breaker** | Downstream services | When a service starts failing |
| **Load Shedding** | System stability | System near capacity |
| **Caching** | Database | Always (read-heavy traffic) |
| **Auto-Scaling** | Compute resources | Traffic spikes |
| **Pre-computation** | Cold-start latency | Before known events |

---

# Real-World Websites That Use Waiting Rooms

### 🎵 Ticketmaster
- Taylor Swift Eras Tour: 2.4 million people in queue
- Uses **Queue-it** as their waiting room provider
- Shows position + estimated wait time

### 🎬 BookMyShow (India)
- Coldplay India concert 2024: 13 million users in queue for 100K tickets
- "You are in the queue. Please do not refresh."

### 🛒 Nike SNKRS
- Limited edition sneaker drops
- Uses a **lottery-based** waiting room (random selection, not first-come-first-served)

### 🏥 COVID Vaccine Booking Sites (2021)
- CoWIN (India), NHS (UK), CVS/Walgreens (US)
- Millions trying to book appointments simultaneously

### ☁️ Cloudflare Waiting Room (most popular provider)
- A product ANY website can plug in
- Used by government sites, retail, ticketing

### 🎮 Steam (game launches)
- Major launches (Elden Ring, Counter-Strike 2)
- "Your transaction is being processed" queue

### Waiting Room Providers:
- **Queue-it** — used by Ticketmaster, FIFA, Olympics
- **Cloudflare** — edge-based waiting rooms (Redis sorted set behind the scenes)
- **Fastly** — edge-based waiting rooms

> **Fun fact:** Cloudflare's waiting room is literally a Redis sorted set behind the scenes — exactly like what we discussed! They packaged it as a product anyone can use with a few clicks.
