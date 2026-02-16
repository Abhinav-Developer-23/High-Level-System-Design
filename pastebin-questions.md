# Pastebin System Design — Questions

---

## Section 1: Overview & Requirements

**Q1.** What is the primary read-to-write ratio for a Pastebin service, and how does this influence architectural decisions?

<details>
<summary>Answer</summary>

The read-to-write ratio is **10:1** — for every paste created, there are roughly 10 reads. This means the system is **read-heavy**, so the architecture should prioritize fast retrieval over write speed. Investments in **caching** (CDN, Redis) and read-optimized data paths are critical, even if writes become slightly slower as a result.

</details>

---

**Q2.** What is the maximum paste size, and what is the average paste size? Why is this distinction important for storage design?

<details>
<summary>Answer</summary>

- **Maximum size:** 10 MB (to prevent abuse)
- **Average size:** ~10 KB

This distinction matters because it drives the **hybrid storage strategy** — small pastes (~95%) can be stored inline in the database for single-read low-latency access, while large pastes (~5%) go to object storage (like S3) to avoid database bloat and high storage costs.

</details>

---

**Q3.** List all three visibility levels a paste can have. What is the default?

<details>
<summary>Answer</summary>

1. **Public** — discoverable by anyone
2. **Unlisted** — accessible only via the direct link (default)
3. **Private** — requires authentication to access

The default visibility is **unlisted**.

</details>

---

**Q4.** Why are pastes designed to be **immutable** (no editing after creation)?

<details>
<summary>Answer</summary>

Immutability greatly simplifies the system:
- **Caching becomes trivial** — content never changes, so cache invalidation is rarely needed.
- **No conflict resolution** — no need to handle concurrent edits or versioning.
- **CDN caching is safe** — cached content never goes stale (except for expiration).
- Users who want to update content can simply create a new paste.

</details>

---

**Q5.** What are the non-functional requirements for a Pastebin service?

<details>
<summary>Answer</summary>

1. **High Availability:** 99.99% uptime
2. **Low Latency:** p99 < 100ms for paste retrieval
3. **Scalability:** Handle millions of reads and writes per day
4. **Durability:** Once created, pastes must not be lost until they expire

</details>

---

## Section 2: Back-of-the-Envelope Estimation

**Q6.** Given 1 million new pastes per day, calculate the average and peak write QPS.

<details>
<summary>Answer</summary>

- **Average write QPS** = 1,000,000 / 86,400 ≈ **12 QPS**
- **Peak write QPS** (assuming 3× peak factor) = 12 × 3 ≈ **36 QPS**

</details>

---

**Q7.** With a 10:1 read-to-write ratio, what are the average and peak read QPS?

<details>
<summary>Answer</summary>

- **Average read QPS** = 10,000,000 / 86,400 ≈ **115 QPS**
- **Peak read QPS** = 115 × 3 ≈ **350 QPS**

These numbers are modest by internet standards, but horizontal scaling is still designed in for availability and growth.

</details>

---

**Q8.** How much storage does the system need after 1 year and after 5 years?

<details>
<summary>Answer</summary>

Each paste averages ~10.5 KB (8 bytes key + 10 KB content + ~500 bytes metadata).

| Time Period | Total Pastes    | Storage Required |
|-------------|-----------------|------------------|
| 1 Year      | 365 million     | ~3.8 TB          |
| 5 Years     | 1.8 billion     | ~19 TB           |

However, paste **expiration** (default 1 year) means storage will plateau after the first year as expired pastes are cleaned up.

</details>

---

**Q9.** Why is peak bandwidth (3.6 MB/s) not a major concern, and when does bandwidth actually become interesting?

<details>
<summary>Answer</summary>

Peak bandwidth of 3.6 MB/s is trivial — a standard 1 Gbps connection supports ~125 MB/s, giving **35× headroom**.

Bandwidth becomes interesting when a **single paste goes viral**. For example, 100,000 views in an hour = ~28 QPS for one paste. Serving this repeatedly from origin wastes resources, which is why **CDN caching** is essential to absorb such hotspots.

</details>

---

**Q10.** What are the four key design insights from the back-of-the-envelope estimation?

<details>
<summary>Answer</summary>

1. **Read-heavy workload** — invest heavily in caching and optimize for fast retrieval
2. **Modest compute requirements** — compute isn't the bottleneck; focus on storage and caching
3. **Storage architecture matters** — separate small pastes (inline in DB) from large pastes (object storage) for cost and performance
4. **Expiration is a feature, not just cleanup** — it keeps storage costs predictable and databases performant

</details>

---

## Section 3: Core APIs

**Q11.** What are the three core API endpoints for a Pastebin service?

<details>
<summary>Answer</summary>

1. **POST /pastes** — Create a new paste
2. **GET /pastes/{paste_key}** — Retrieve a paste by its unique key
3. **DELETE /pastes/{paste_key}** — Remove a paste (owner only, requires authentication)

</details>

---

**Q12.** What is the difference between HTTP status codes **404** and **410** in the context of paste retrieval, and why is this distinction intentional?

<details>
<summary>Answer</summary>

- **404 Not Found** — The paste key was never created or has been deleted.
- **410 Gone** — The paste existed but has passed its expiration time.

The distinction is intentional because **410** tells the client the resource *used to exist* but is no longer available. This is useful for **caching** (caches know not to look again) and **user messaging** (the UI can show "this paste has expired" instead of "not found").

</details>

---

**Q13.** Why is the DELETE endpoint designed to be **idempotent**?

<details>
<summary>Answer</summary>

DELETE returns success even if the paste was already deleted. This **simplifies client retry logic** — if a delete request times out and the client retries, it won't get an unexpected error. The outcome is the same regardless of how many times the request is sent.

</details>

---

**Q14.** What error code is returned when a user tries to use a custom key that's already taken?

<details>
<summary>Answer</summary>

**409 Conflict** — indicates the requested `custom_key` is already in use by another paste.

</details>

---

## Section 4: High-Level Design

**Q15.** Name all the core components in the Pastebin architecture and briefly describe each one's role.

<details>
<summary>Answer</summary>

1. **API Gateway** — SSL termination, request validation, rate limiting, routing
2. **Paste Service** — Core business logic (stateless, horizontally scalable)
3. **Key Generation Service** — Produces unique, short, unpredictable paste keys
4. **Metadata Database (PostgreSQL)** — Stores paste metadata (key, user, timestamps, visibility, content pointer)
5. **Object Storage (S3/GCS)** — Stores actual paste content (cheap, durable, CDN-friendly)
6. **CDN** — Edge caching for public/unlisted pastes, absorbs traffic spikes
7. **Redis Cache** — Application-level cache with sub-millisecond latency
8. **Cleanup Service** — Background worker that removes expired pastes

</details>

---

**Q16.** In the paste creation flow, why is content stored in object storage **before** metadata is saved in the database?

<details>
<summary>Answer</summary>

**Ordering matters for failure resilience:**
- If **content storage fails**, there's nothing to save metadata about — we simply return an error.
- If **metadata storage fails** after content is written, we have orphaned content in object storage. This is **wasteful but not incorrect** — a cleanup job can later find and remove orphaned objects.

The reverse order would be worse: metadata pointing to non-existent content means users see broken pastes.

</details>

---

**Q17.** What are the three possible cache hit scenarios when a user requests a paste, ordered from fastest to slowest?

<details>
<summary>Answer</summary>

1. **CDN hit** (best case, ~10–50ms): The edge node closest to the user has the paste cached. Origin servers never see the request.
2. **Redis hit** (~50–100ms): CDN missed, but the Paste Service finds the content in Redis. Database is still avoided.
3. **Full cache miss** (~100ms+): Neither cache has the content. Query metadata from DB, fetch content from object storage (if large), populate Redis cache, then return.

</details>

---

**Q18.** What `Cache-Control` headers are set for public vs. private pastes, and why?

<details>
<summary>Answer</summary>

- **Public/unlisted pastes:** `Cache-Control: public, max-age=3600` — allows CDN caching for up to 1 hour.
- **Private pastes:** `Cache-Control: private, no-cache` — prevents CDN caching since they require authentication.

Private pastes should never be stored at shared edge nodes because only the owner should be able to access them.

</details>

---

**Q19.** What happens if a paste expires while it's still cached in the CDN or Redis?

<details>
<summary>Answer</summary>

The application **always checks the `expires_at` timestamp** before serving content, regardless of where the data comes from (cache or database). If a cached paste has expired, the system returns **HTTP 410 (Gone)** and removes it from the cache. TTL-based expiration alone is not sufficient — the real-time check on every read is the guarantee.

</details>

---

## Section 5: Database Design

**Q20.** Why is PostgreSQL chosen for metadata instead of a NoSQL database like DynamoDB or Cassandra?

<details>
<summary>Answer</summary>

PostgreSQL is preferred because:
- **Multiple access patterns:** Queries by `paste_key`, `user_id`, `expiry_date`, and `visibility` all need efficient indexes — relational DBs handle this naturally.
- **Strong consistency:** Users should see their paste immediately after creation.
- **Mature tooling:** Backups, replication, and monitoring are well-understood.
- **Flexible schema:** Easy to add new fields as requirements evolve.

NoSQL benefits (extreme scale, eventual consistency) **don't match the needs** — the query patterns are varied enough that a relational DB is simpler.

</details>

---

**Q21.** Why is actual paste content stored in object storage (S3) rather than in the database?

<details>
<summary>Answer</summary>

Four reasons:
1. **Cost** — Object storage costs ~$0.02/GB/month vs. $0.10–0.20/GB for DB storage (5–10× cheaper).
2. **Size handling** — Databases struggle with multi-MB rows; object storage is designed for it.
3. **Durability** — S3 offers 99.999999999% (11 nines) durability.
4. **CDN integration** — Object storage integrates seamlessly with CDNs for edge caching.

Paste content is **opaque** — it doesn't need to be queried, joined, or partially updated, making it a perfect fit for object storage.

</details>

---

**Q22.** What are the fields in the `pastes` table, and why does it have both a `content_inline` and a `content_path` column?

<details>
<summary>Answer</summary>

Key fields: `paste_key` (PK), `user_id`, `title`, `language`, `content_path`, `content_size`, `content_inline`, `visibility`, `created_at`, `expires_at`.

**Dual content columns are an optimization:**
- `content_inline` (TEXT) — For small pastes (< 64 KB), content is stored directly in the DB, requiring only **one read operation**.
- `content_path` (VARCHAR) — For large pastes (≥ 64 KB), this holds the S3 path. Content requires a **second hop** to object storage.

Only one of the two columns is populated per row. This optimizes the common case (small pastes) while handling large pastes cost-effectively.

</details>

---

**Q23.** What indexes should be created on the `pastes` table and why?

<details>
<summary>Answer</summary>

1. **Primary Key on `paste_key`** — Fast point lookups (the most common operation)
2. **Index on `user_id`** — Listing a user's pastes for dashboards
3. **Index on `expires_at`** — Efficient batch queries for the cleanup job
4. **Composite index on `(visibility, created_at)`** — Filtering and sorting public paste listings

</details>

---

## Section 6: Deep Dive — Key Generation

**Q24.** What four properties must a good paste key have?

<details>
<summary>Answer</summary>

1. **Unique** — No two pastes can ever share the same key
2. **Short** — Easy to share (target: 8 characters)
3. **Unpredictable** — Users can't guess other paste URLs by incrementing/modifying keys
4. **Scalable** — Key generation must not become a bottleneck as servers are added

</details>

---

**Q25.** Explain the three key generation approaches and compare their trade-offs.

<details>
<summary>Answer</summary>

| Strategy | How It Works | Uniqueness | Throughput | Complexity | Key Length |
|----------|-------------|------------|------------|------------|------------|
| **Random Keys** | Generate random 8-char Base62 string, check DB for collision, retry if needed | Check per creation | Low-medium | Simple | 8 chars |
| **Pre-Generated Key Pool** | Background service pre-generates millions of keys; paste creation grabs an unused one atomically | Guaranteed | High | Medium | 8 chars |
| **Snowflake-like** | 64-bit ID from timestamp + worker ID + sequence, then Base62 encoded | Guaranteed | Very high | Higher | 11 chars |

</details>

---

**Q26.** Why is Base62 encoding used, and how many possible combinations does an 8-character Base62 key provide?

<details>
<summary>Answer</summary>

**Base62** uses lowercase a–z (26), uppercase A–Z (26), and digits 0–9 (10) = 62 characters. It produces URL-safe strings without special characters.

An 8-character Base62 key gives **62⁸ = ~218 trillion** possible combinations. At 1 million pastes/day, it would take over **600,000 years** to exhaust this key space, making collisions vanishingly rare.

</details>

---

**Q27.** In the pre-generated key pool approach, how is concurrency handled when multiple Paste Service instances try to grab keys simultaneously?

<details>
<summary>Answer</summary>

Three approaches:
1. **Atomic UPDATE** — A single SQL statement selects and marks a key as used atomically using `SELECT ... FOR UPDATE`:
   ```sql
   UPDATE keys SET is_used = true, assigned_at = NOW()
   WHERE key_value = (SELECT key_value FROM keys WHERE is_used = false LIMIT 1 FOR UPDATE)
   RETURNING key_value;
   ```
2. **Batch allocation** — Each server fetches a batch of keys (e.g., 1,000) into memory, reducing DB contention.
3. **Server-specific ranges** — Assign different key prefixes to different servers (Server 1 = "a*", Server 2 = "b*"), eliminating contention entirely.

</details>

---

**Q28.** Which key generation strategy is recommended for a Pastebin-scale system and why?

<details>
<summary>Answer</summary>

The **Pre-Generated Key Pool** is recommended. It provides:
- **Guaranteed uniqueness** without collision checking
- **Short keys** (8 characters)
- **Good performance** with no retry logic
- **Moderate complexity** — much simpler than Snowflake

Snowflake would be overkill for Pastebin's scale (~12 write QPS). It's justified at Twitter/Discord scale (billions of operations/day), but for millions of pastes/day, the key pool is the sweet spot.

</details>

---

## Section 7: Deep Dive — Content Storage

**Q29.** What is the threshold for inline vs. object storage, and why was that threshold chosen?

<details>
<summary>Answer</summary>

The threshold is **64 KB**.

- **Below 64 KB:** Stored inline in the database's `content_inline` column. The overhead of a second network call to S3 isn't worth it for small content.
- **Above 64 KB:** Stored in object storage. At this size, DB bloat and longer connection holding times become noticeable.

~95% of pastes fall below 64 KB, so the common case is optimized for single-read, low-latency access.

</details>

---

**Q30.** What compression algorithms can be used for large paste content, and what are their trade-offs?

<details>
<summary>Answer</summary>

| Algorithm  | Compression Ratio | CPU Cost  | Best For                     |
|------------|-------------------|-----------|------------------------------|
| GZIP       | 60–80% reduction  | Moderate  | Storage optimization         |
| LZ4        | 40–60% reduction  | Very low  | Speed-sensitive reads        |
| Zstandard  | 70–85% reduction  | Moderate  | Best of both worlds          |

Text compresses well — a 1 MB log file might compress to ~200 KB with GZIP. Compression is applied before storing in object storage and decompressed on read. For inline DB content, compression is typically skipped since PostgreSQL's TOAST handles large values automatically.

</details>

---

## Section 8: Deep Dive — Caching Strategy

**Q31.** Describe the three-layer caching architecture and the expected hit rate for each layer.

<details>
<summary>Answer</summary>

| Layer | Technology | Latency | Expected Hit Rate | What It Serves |
|-------|-----------|---------|-------------------|----------------|
| Layer 1 | **CDN** | 10–50ms | 70–80% | Public/unlisted pastes in hot regions |
| Layer 2 | **Redis** | ~1ms | 15–20% | Private pastes, CDN misses |
| Layer 3 | **Database** | ~20ms | 5–10% | Cold pastes, first access |

Each layer catches a portion of requests so that only **5–10%** reach the database.

</details>

---

**Q32.** Why is the Redis cache TTL set to `min(time_until_expiry, 24 hours)`?

<details>
<summary>Answer</summary>

Two reasons:
1. **Paste expiration alignment** — If a paste expires in 30 minutes, the cache entry should also expire in 30 minutes so expired content isn't served.
2. **Freshness guarantee** — Even for long-lived pastes, capping at 24 hours ensures the cache stays reasonably in sync with the database and catches any edge cases where cache and DB diverge.

</details>

---

**Q33.** Why is cache invalidation particularly simple for Pastebin?

<details>
<summary>Answer</summary>

Because **pastes are immutable** — once created, content never changes. This eliminates the hardest part of caching.

- **On creation:** No cache to invalidate (new key).
- **On deletion:** Remove from Redis + issue CDN purge request.
- **On expiration:** TTL-based eviction handles it automatically.

The only active invalidation needed is for deletion, and most CDN providers offer purge APIs for this.

</details>

---

**Q34.** What is **cache warming**, and why is it useful for Pastebin?

<details>
<summary>Answer</summary>

Cache warming means **proactively populating the Redis cache** right after a paste is created, before any user requests it.

It's useful because the user who just created the paste is likely about to **share the link immediately**. Without warming, the first viewer would experience a cache miss and hit the database. By writing to Redis during the create flow, the first viewer gets a fast cache hit.

The trade-off is a small amount of added latency to the create operation.

</details>

---

## Section 9: Deep Dive — Paste Expiration

**Q35.** Why can't we rely solely on cache TTLs or background cleanup for expiration enforcement?

<details>
<summary>Answer</summary>

Because timing gaps exist:
- A paste might be cached with a **1-hour TTL** but expire in **30 minutes**.
- The cleanup job might **not have run yet**.

The only reliable method is **checking `expires_at` against the current time on every read request**, regardless of whether the data comes from cache or database. If expired, return HTTP 410 (Gone). This runtime check is the guarantee; TTLs and cleanup are optimizations, not the source of truth.

</details>

---

**Q36.** Why does the cleanup job process expired pastes in batches of 1,000 instead of deleting all at once?

<details>
<summary>Answer</summary>

Deleting millions of rows in a single transaction would **lock the database** and impact live traffic. Batch processing:
- Keeps each transaction **small and fast**
- Allows the database to handle **regular queries between batches**
- Prevents long-running transactions that could cause replication lag

</details>

---

**Q37.** What is the "soft delete" strategy for expired pastes, and why use it?

<details>
<summary>Answer</summary>

Instead of immediately hard-deleting expired rows, set a `deleted_at` timestamp first:

```sql
UPDATE pastes SET deleted_at = NOW()
WHERE expires_at < NOW() AND deleted_at IS NULL
LIMIT 1000;
```

A second job hard-deletes rows where `deleted_at` is more than **7 days old**.

This provides a **recovery window** — if something goes wrong (accidental deletion, bug in cleanup logic), the data can be recovered within 7 days before it's permanently removed.

</details>

---

## Section 10: Deep Dive — Rate Limiting & Abuse Prevention

**Q38.** What are the rate limits for anonymous, registered, and premium users?

<details>
<summary>Answer</summary>

| User Type   | Paste Creation | Paste Reading | Identifier  |
|-------------|----------------|---------------|-------------|
| Anonymous   | 10/hour        | 100/hour      | IP address  |
| Registered  | 100/hour       | 1,000/hour    | User ID     |
| Premium     | 1,000/hour     | Unlimited     | User ID     |

Create limits are stricter than read limits because creating pastes **consumes storage** and requires write operations, whereas reads are much cheaper (especially from cache).

</details>

---

**Q39.** What automated checks are performed on paste creation to prevent abuse?

<details>
<summary>Answer</summary>

1. **Size validation** — Reject content over 10 MB
2. **Spam detection** — Check against known spam patterns and URLs
3. **Malware scanning** — For binary content or suspicious scripts
4. **Link analysis** — Flag pastes with known phishing domains

Additionally:
- **CAPTCHA** is required for anonymous creations, after hitting 50% of rate limit, or when patterns look automated
- **IP reputation** checks flag high-risk IPs for stricter limits

</details>

---

**Q40.** When should a CAPTCHA be triggered?

<details>
<summary>Answer</summary>

1. **All anonymous paste creations**
2. **After hitting 50% of the rate limit**
3. **When request patterns look automated** (same content, rapid succession)
4. **From IP addresses with poor reputation**

Modern services like reCAPTCHA v3 or Cloudflare Turnstile provide **invisible protection** for most legitimate users while only challenging suspicious traffic.

</details>

---

## Section 11: Deep Dive — Scaling

**Q41.** Why is the Paste Service designed to be stateless, and how does this help scaling?

<details>
<summary>Answer</summary>

**Stateless** means any Paste Service instance can handle any request — no session affinity or local state required. All state lives in the database and cache layers.

This enables **straightforward horizontal scaling:**
- Add more instances behind a load balancer
- Use auto-scaling based on CPU utilization (target ~70%) or request queue depth
- Each new instance adds capacity **linearly**
- No need for sticky sessions or state synchronization between instances

</details>

---

**Q42.** What is the two-stage approach to scaling the database?

<details>
<summary>Answer</summary>

**Stage 1: Read Replicas**
- Offload read queries to async replicas while the primary handles writes.
- Reads tolerate slight staleness (replication lag < 100ms).
- Scales read capacity **linearly** with the number of replicas.
- Sufficient for Pastebin's scale (1M pastes/day) for years.

**Stage 2: Sharding (if needed)**
- If write volume becomes a bottleneck (unlikely for Pastebin).
- Shard by `paste_key` using consistent hashing.
- Each shard handles a subset of the key space.
- Adds complexity but enables horizontal write scaling.

</details>

---

**Q43.** How is the Redis cache layer scaled?

<details>
<summary>Answer</summary>

Two ways:
1. **Vertical scaling** — Use larger instances with more memory. Simple but has limits.
2. **Horizontal scaling** — Deploy **Redis Cluster**, which partitions data across nodes using **hash slots**. Adding nodes rebalances data automatically and the cluster handles failover if a node goes down.

Keys are distributed using **consistent hashing** on the paste key across multiple Redis nodes.

</details>

---

**Q44.** Which components in the architecture scale automatically without manual intervention?

<details>
<summary>Answer</summary>

| Component | Scaling Approach | Our Responsibility |
|-----------|-----------------|-------------------|
| Object Storage (S3/GCS) | Fully managed, infinite scale | Pay for what we use |
| CDN (CloudFront/Fastly) | Global edge network, auto-scales | Configure cache policies |
| Load Balancer (ALB/NLB) | Managed, scales with traffic | Monitor and adjust limits |

The database is usually the **limiting factor**, but read replicas handle read-heavy workloads well.

</details>

---

## Bonus: Scenario-Based Questions

**Q45.** A paste goes viral and receives 1 million views in one hour. Walk through how the system handles this without degrading performance.

<details>
<summary>Answer</summary>

1. The **CDN absorbs the vast majority** of requests. After the first request populates the edge cache, subsequent requests from the same region (~70–80%) never reach the origin.
2. Requests that miss the CDN hit **Redis** (~1ms latency), which serves another 15–20%.
3. Only the initial cold request per region hits the **database and object storage**.
4. The CDN **protects the origin** from the traffic spike — origin servers see only a tiny fraction of the 1M views.
5. Rate limiting at the **API gateway** protects against any malicious amplification.

The system's multi-layer caching is specifically designed for this asymmetry between writes and reads.

</details>

---

**Q46.** A user creates a paste and immediately shares the link. How do we ensure the first viewer doesn't experience a slow load?

<details>
<summary>Answer</summary>

Through **cache warming**: after the paste is created in the database/object storage, the Paste Service **proactively writes the paste content and metadata to Redis** before returning the URL to the creator. When the first viewer clicks the link, they get a **Redis cache hit** instead of a full database round-trip.

</details>

---

**Q47.** What would happen if the Key Generation Service goes down? How does the system remain resilient?

<details>
<summary>Answer</summary>

With the **pre-generated key pool** approach, resilience is built in:
- The keys are already stored in the database, so even if the generation service dies, there's a **pool of unused keys** available.
- The Paste Service can continue grabbing keys from the pool until it runs low.
- The system only degrades if the pool is completely exhausted, which is mitigated by monitoring the pool size and alerting when it drops below a threshold (e.g., 1 million unused keys).
- The generation service can be restarted or replaced without affecting live traffic.

</details>

---

**Q48.** Why does the system return HTTP 410 (Gone) for expired pastes instead of just 404?

<details>
<summary>Answer</summary>

- **410 (Gone)** signals that the resource **previously existed** but is permanently unavailable.
- **404 (Not Found)** means the key was never created or was deleted.

This distinction helps:
1. **Caching** — Proxies and browsers know a 410 resource won't come back, so they can stop retrying.
2. **User experience** — The UI can show "This paste has expired" (410) vs. "Paste not found" (404), which is more informative.
3. **Client logic** — API consumers can differentiate between a typo in the URL vs. legitimately expired content.

</details>

---

**Q49.** You're asked to add a "list all public pastes" feature. What considerations come to mind?

<details>
<summary>Answer</summary>

1. **Pagination** — Use **cursor-based pagination** (not offset-based) for efficient queries on large datasets.
2. **Index** — A composite index on `(visibility, created_at)` is already designed for this query.
3. **Caching** — Public listings can be cached aggressively since they change slowly (new pastes appear, expired ones disappear).
4. **Separate endpoint** — `GET /pastes?visibility=public` with pagination parameters.
5. **Content exclusion** — Don't return paste content in the listing, only metadata (title, language, created_at, content_size) to keep responses lightweight.
6. **Rate limiting** — Apply limits to prevent scraping of all public pastes.

</details>

---

**Q50.** If you had to pick the single most impactful architectural decision in this design, what would it be and why?

<details>
<summary>Answer</summary>

**Separating content storage from metadata storage.**

This single decision unlocks multiple benefits:
- **Cost optimization** — 95% of storage (paste content) goes to cheap object storage instead of expensive database storage.
- **Performance** — The metadata database stays small and fast; queries over indexes remain efficient.
- **Durability** — Object storage provides 11 nines of durability by default.
- **CDN integration** — Content can be served directly from S3/CloudFront edge nodes.
- **Scalability** — Object storage scales infinitely; the database only handles small metadata rows.
- **Flexibility** — The hybrid inline/object storage strategy optimizes both the common case (small pastes) and the edge case (large pastes).

Without this separation, the database would bloat, queries would slow down, costs would spike, and CDN integration would be complicated.

</details>
