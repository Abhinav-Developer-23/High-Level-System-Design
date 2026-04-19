## Web Crawler — HLD Architecture Diagram

![Web Crawler HLD](./WebCrawler_HLD.svg)

---
---

## What is `robots.txt`?


> `robots.txt` is a plain-text file placed at the root of a website (e.g., `https://example.com/robots.txt`) that tells web crawlers which pages or sections of the site they are **allowed** or **disallowed** to access. It follows the **Robots Exclusion Protocol (REP)**.

---

### Why Does It Exist?

- **Server Protection**: Prevents crawlers from overwhelming a site with too many requests.
- **Content Control**: Lets site owners hide private, duplicate, or low-value pages from crawlers.
- **Crawl Budget Optimization**: Guides crawlers toward important pages instead of wasting resources on irrelevant ones.
- **Legal / Policy Compliance**: Establishes explicit rules that well-behaved crawlers are expected to follow.

---

### Format & Syntax

A `robots.txt` file consists of **rules** grouped under **User-agent** directives:

```
# Rules for all crawlers
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/
Crawl-delay: 2

# Rules specific to Googlebot
User-agent: Googlebot
Disallow: /no-google/
Allow: /

# Sitemap reference
Sitemap: https://example.com/sitemap.xml
```

---

### Key Directives

| Directive | Description |
|---|---|
| `User-agent` | Specifies which crawler the rules apply to. `*` means all crawlers. |
| `Disallow` | Blocks the crawler from accessing the specified path. |
| `Allow` | Explicitly permits access to a path (overrides `Disallow` for more specific matches). |
| `Crawl-delay` | Minimum seconds between consecutive requests from that crawler. |
| `Sitemap` | Points to the XML sitemap for easier URL discovery. |

---

### Matching Rules

1. **Most specific User-agent wins** — If a crawler matches both `*` and its own name (e.g., `Googlebot`), the named block takes priority.
2. **First matching path rule wins** — Rules are evaluated top-to-bottom within a user-agent block. The first `Allow` or `Disallow` that matches the URL path is applied.
3. **No rule = Allowed** — If no `Disallow` matches a URL, the crawler is free to access it.
4. **Empty `Disallow`** — `Disallow:` (with no path) means nothing is disallowed i.e., everything is allowed.

---

### Real-World Examples

#### Google (`https://www.google.com/robots.txt`)
```
User-agent: *
Disallow: /search
Allow: /search/about
Allow: /search/static
Disallow: /sdch
```

#### Twitter/X (`https://x.com/robots.txt`)
```
User-agent: *
Disallow: /*/followers
Disallow: /*/following
Disallow: /search?q=*
```

---

### How a Web Crawler Handles `robots.txt`

```
┌───────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Fetch URL │──────▶ │ robots.txt       │──────▶ │  Allowed?        │
│ Request   │        │ cached for domain│        │  Check rules     │
└───────────┘        └──────────────────┘        └────────┬─────────┘
                                                          │
                                              ┌───────────┴───────────┐
                                              │                       │
                                        ┌─────▼─────┐          ┌─────▼─────┐
                                        │  Allowed   │          │  Blocked  │
                                        │ Proceed to │          │ Skip URL  │
                                        │ fetch page │          │ Mark as   │
                                        └────────────┘          │ blocked   │
                                                                └───────────┘
```

#### Caching Strategy

| Aspect | Details |
|---|---|
| **Cache TTL** | Typically 24 hours per domain |
| **Storage** | In-memory or distributed cache (Redis) |
| **Fetch failure** | Use stale cached version if available; if no cache, assume everything is allowed |
| **404 response** | No `robots.txt` exists → treat all paths as allowed |
| **5xx response** | Server error → temporarily assume all paths are disallowed (conservative) or use cached version |

---

### `robots.txt` in Web Crawler System Design

In a distributed web crawler architecture, the **Robots Checker** is a dedicated component in the **Fetcher Service** pipeline:

```
URL Frontier ──▶ DNS Resolver ──▶ Robots Checker ──▶ HTTP Client ──▶ Validator
                                       │
                                       ▼
                                 Robots.txt Cache
                                 (per-domain, 24h TTL)
```

**Key implementation details:**

- **Per-domain cache**: Store parsed rules (not raw text) for fast lookups.
- **Pre-fetching**: When a new domain is encountered, fetch its `robots.txt` before any page from that domain.
- **Rate limit extraction**: Parse `Crawl-delay` and enforce it in the per-host rate limiter.
- **Wildcard support**: Some `robots.txt` files use `*` and `$` in paths (e.g., `Disallow: /*.pdf$`).

---

### Important Caveats

> [!WARNING]
> `robots.txt` is a **voluntary protocol** — it relies on crawlers choosing to respect it. Malicious bots can and do ignore it. It is **not a security mechanism** and should never be used to protect sensitive data. Use authentication, firewalls, or access controls for actual security.

- **Not legally binding** (in most jurisdictions), but ignoring it can lead to IP bans or legal action.
- **Visible to everyone** — Anyone can read `https://yoursite.com/robots.txt`, so don't list sensitive paths in it.
- **Does not remove pages from search** — Use `noindex` meta tags or `X-Robots-Tag` HTTP headers for that.

---

### `robots.txt` vs Other Mechanisms

| Mechanism | Scope | Purpose |
|---|---|---|
| `robots.txt` | Entire site | Controls which paths crawlers can access |
| `<meta name="robots">` | Single page | Controls indexing and link-following per page |
| `X-Robots-Tag` (HTTP header) | Single response | Same as meta robots but works for non-HTML files (PDFs, images) |
| `Sitemap.xml` | Entire site | Tells crawlers which pages exist and their priority |

---

### FAQ

#### Q: What happens if `robots.txt` is missing?
**A:** The crawler treats it as if everything is allowed. A `404` response for `robots.txt` means "no restrictions."

#### Q: Can `robots.txt` block specific URLs?
**A:** It blocks URL **paths**, not individual URLs. For example, `Disallow: /admin/` blocks all URLs under `/admin/`.

#### Q: Does respecting `Crawl-delay` matter at scale?
**A:** Absolutely. At 400+ pages/sec across millions of domains, ignoring `Crawl-delay` can get your crawler's IP blocked, harm small sites, or even lead to legal consequences. The politeness constraint is non-negotiable in production crawlers.

---
---

## What is a Bloom Filter?

> A **Bloom Filter** is a space-efficient, probabilistic data structure used to test whether an element is **a member of a set**. It can tell you **"definitely not in the set"** or **"probably in the set"** — it may produce **false positives**, but **never false negatives**.

---

### How It Works

It uses a **bit array** of size `m` (all 0s initially) and **`k` hash functions**.

- **Insert**: Hash the element `k` times, set those bit positions to `1`.
- **Lookup**: Hash the element `k` times, check if **all** bits are `1`.
  - Any bit is `0` → **definitely not in set**.
  - All bits are `1` → **probably in set** (could be false positive from other insertions).

```
Insert "page1":  Hash₁=3, Hash₂=7, Hash₃=11 → set bits 3, 7, 11

Bit Array:  0  0  0  1  0  0  0  1  0  0  0  1  0  0  0  0
                     ↑              ↑              ↑

Lookup "page2": Hash₁=3, Hash₂=5, Hash₃=11
  bit[3]=1 ✓, bit[5]=0 ✗ → DEFINITELY NOT IN SET

Lookup "page3": Hash₁=3, Hash₂=7, Hash₃=11
  bit[3]=1 ✓, bit[7]=1 ✓, bit[11]=1 ✓ → PROBABLY IN SET
```

> **False positives** happen because as more elements are inserted, more bits become `1`, and an unseen element may find all its positions already set by others.

---

### Why Use It (Instead of a HashSet)?

At **10 billion URLs**, a HashSet needs **~640 GB**. A Bloom filter does it in **~11 GB** at 1% false positive rate.

| Aspect | HashSet | Bloom Filter |
|---|---|---|
| **Memory** | Stores actual elements → huge | Stores only bits → compact |
| **False Positives** | None | Possible (tunable) |
| **False Negatives** | None | None |
| **Deletion** | Yes | No (standard version) |

---

### Where It's Used in a Web Crawler

1. **URL Deduplication** — Before adding a discovered URL to the frontier, check the Bloom filter. If "definitely not seen", add it directly (skips ~90% of DB lookups). If "probably seen", skip it.
2. **Content Deduplication** — Store content hashes (MD5/SHA-256) in a separate Bloom filter to avoid storing duplicate page content.
3. **DNS Cache Miss Detection** — Check if a hostname was recently resolved before querying the DNS resolver.

---
---

## What is SimHash?

> **SimHash** is a locality-sensitive hashing algorithm that generates a fingerprint (hash) for a piece of text such that **similar documents produce similar hashes**. The closer two SimHashes are (measured by **Hamming distance**), the more similar the documents.

This is the key difference from MD5/SHA-256 — cryptographic hashes change completely with even one character change. SimHash preserves similarity.

---

### How It's Used in a Web Crawler

The web is full of **near-duplicate content** — same article on different URLs, pages with slightly different ads, mobile vs desktop versions, syndicated content. MD5 won't catch these — SimHash will.

**Flow:**

1. Fetch a page and extract its text content.
2. Compute its 64-bit SimHash fingerprint.
3. Compare against stored SimHashes using **Hamming distance**.
4. If distance `< 3` → near-duplicate → skip storing, or merge with original.
5. If distance `≥ 3` → unique content → store it and save its SimHash.

```
Page A SimHash:  1 0 1 1 0 0 1 0 ... (64 bits)
Page B SimHash:  1 0 1 1 0 0 1 1 ... (64 bits)
                                 ↑
                          1 bit different → Hamming distance = 1 → NEAR-DUPLICATE
```

---

### How SimHash Works (Brief)

1. **Tokenize** the document into words/shingles.
2. **Hash** each token into a 64-bit hash.
3. For each bit position, add `+1` if that bit is `1`, `-1` if `0`, weighted by token frequency.
4. Take the **sign** of each position's sum → that's the final 64-bit SimHash.

Result: two documents sharing most of the same words will have very similar bit vectors → small Hamming distance.

> **Does a large document produce a tiny hash?** Yes — and that's the point. The output is always a **fixed 64-bit fingerprint (8 bytes)**, regardless of whether the page is 1 KB or 5 MB. The entire document's content gets "summarized" into those 64 bits through the weighted bit aggregation. More tokens just affect the weights in step 3 — the output size never changes. This is what makes it practical to store one SimHash per crawled page and compare billions of them cheaply.

---

### Where It's Used in a Web Crawler

- **Content-level deduplication** — primary use case. Detects near-duplicate pages that URL dedup and MD5 would miss.
- Stored per URL in the `url_metadata` table (`content_hash` field) for fast lookups.
- Works alongside MD5/SHA for **exact** duplicates (MD5 first, SimHash if MD5 misses).

---
---

## How Do We Maintain a Priority Queue in a Distributed Environment?

> A single in-memory priority queue can't scale to billions of URLs across dozens of crawler machines. The solution is to **partition the queue by host hash** and manage it with a combination of a database, a distributed cache, and a coordinator.

---

### The Problem with a Single Priority Queue

- Can't fit 10B URLs in one machine's memory.
- Multiple crawler nodes pulling from one queue = contention, locking, bottlenecks.
- No politeness enforcement — multiple workers could hit the same domain simultaneously.

---

### Solution: Partitioned Queues + Coordinator

**Partition by host hash** — each crawler node owns a subset of domains:

```
hash(domain) % N  →  assigned crawler node

"news.com"    → hash % 10 = 3  → Crawler Node 3
"blog.net"    → hash % 10 = 7  → Crawler Node 7
"example.com" → hash % 10 = 3  → Crawler Node 3
```

Each node maintains its own **local priority queue** (in-memory min-heap) for only its assigned domains. This means:
- No cross-node contention.
- Politeness is local — rate limiting per domain is trivial.
- DNS/robots.txt caches stay warm per node.

---

### What Backs the Queue?

| Layer | Tool | Purpose |
|---|---|---|
| **Persistent store** | Cassandra / RocksDB | All queued URLs with priority + `next_crawl_at` — survives crashes |
| **In-memory heap** | Local min-heap per node | Hot URLs ready to crawl right now |
| **Coordinator** | Zookeeper / etcd | Tracks domain-to-node assignment, detects node failures |

**On startup / recovery**, each crawler node queries its partition from Cassandra and rebuilds its in-memory heap. Nothing is lost on crash.

---

### How Priority is Enforced

URLs are scored and sorted by a composite priority:

```
priority_score = domain_authority × freshness_weight × (1 / depth)
next_crawl_at  = now + crawl_delay
```

The local heap is keyed by `next_crawl_at` (min-heap), so the crawler always picks the URL that is **due soonest** while respecting its domain's rate limit.

---

### What Happens When a Node Fails?

1. Coordinator detects missed heartbeats (e.g., 3 missed in 15s).
2. Failed node's domain assignments are redistributed to surviving nodes via **consistent hashing** (minimizes reshuffling).
3. Surviving nodes reload URLs for newly assigned domains from Cassandra.
4. In-progress URLs that were lost are marked `failed` and retried.

---
---

## Why S3 for Page Content Storage (Not Cassandra or MySQL)?

> We store **raw HTML content** in S3 (object storage), not in Cassandra or MySQL. This is a deliberate choice based on the nature of the data and access patterns.

---

### What Are We Storing?

Each crawled page = full HTTP response body (HTML). Average ~500 KB uncompressed, ~100 KB compressed.

At 1B pages/month → **500 TB/month** of raw content. That rules out anything row-based.

---

### Why Not MySQL?

| Issue | Explanation |
|---|---|
| **Not built for BLOBs** | MySQL stores rows in pages (16 KB). A 500 KB HTML blob spans many pages → terrible read/write performance |
| **Schema overhead** | You'd need a `content` column with `LONGBLOB` — bloats the table, kills index performance |
| **Not horizontally scalable** | Sharding MySQL for 500 TB is painful and operationally expensive |
| **No compression / chunking** | No native support for gzip compression or streaming large objects |

---

### Why Not Cassandra?

Cassandra is great for URL metadata (small, structured, high-throughput reads/writes). But for raw content:

| Issue | Explanation |
|---|---|
| **Row size limits** | Cassandra recommends keeping values under 1 MB. Storing 500 KB blobs at scale causes compaction pressure and GC issues |
| **Not designed for large blobs** | Cassandra is a wide-column store optimized for small structured values, not arbitrary binary payloads |
| **Costly reads** | Reading a 500 KB value from Cassandra forces deserialization through the LSM tree — much slower than a direct S3 GET |
| **Expensive storage** | Cassandra replicates data 3x across nodes on SSDs. 500 TB × 3 = 1.5 PB on expensive SSD storage |

---

### Why S3?

| Advantage | Explanation |
|---|---|
| **Designed for large objects** | S3 is purpose-built for storing arbitrary-size blobs efficiently |
| **Cheap at scale** | ~$23/TB/month vs Cassandra/MySQL which need expensive SSD nodes |
| **High throughput writes** | Handles 200 MB/sec ingestion easily, scales automatically |
| **Compression support** | Store WARC files with gzip — reduces 500 TB to ~100 TB |
| **Decoupled from compute** | Crawler nodes write to S3; downstream indexers read from S3 independently — no coupling |
| **Durability** | 99.999999999% (11 nines) durability out of the box |

---

### The Right Tool for Each Job

| Data | Storage | Why |
|---|---|---|
| Raw HTML content | **S3** | Large blobs, write-heavy, cheap, sequential reads |
| URL metadata | **Cassandra** | Small rows, high-throughput random reads/writes, fast point lookups |
| robots.txt / DNS cache | **Redis** | Hot data, TTL-based, in-memory speed |
