# High-Level System Design: Delivery Serviceability API

## 1. Problem Statement

Design an API that determines whether a product can be delivered within 2 days, given a destination pincode.

**Key aspects covered:**
- Core logic for distance and transit time validation.
- Data modeling for products, warehouses, and logistics transit times.
- Extensibility for multiple regions or service levels (e.g., 2-day, standard, hyperlocal).
- Traffic and bandwidth estimation.
- Fault tolerance, handling API failures, and scalability.

---

## 2. Requirements Gathering

### Functional Requirements
* **Check Serviceability:** Given a `product_id` and `destination_pincode`, return whether it can be delivered within a specific SLA (e.g., 2 days) and the estimated delivery time.
* **Support Multiple Parameters:** Handle different products, varying warehouse inventory, and all valid pincodes.
* **Extensibility:** Must support different service levels in the future (e.g., Next-Day Delivery, Same-Day Delivery, Hyperlocal) and adapt to different geographic regions.

### Non-Functional Requirements
* **High Availability (HA):** This is a Tier-1 API. If it is down, it halts the user's browsing and checkout flow. A 99.99% availability is required.
* **Low Latency:** Must respond in `< 50ms` at the p99 percentile, as it operates synchronously when users view product details or add products to the cart.
* **Scalability:** Should withstand high read throughput, specifically during peak sale events.
* **Eventual Consistency:** Background sync operations (updating inventory, modifying route transit times due to weather) can be eventually consistent.

---

## 3. Capacity Planning & Estimation

Let's assume a scale similar to a major e-commerce platform (e.g., Amazon/Flipkart).

* **Daily Active Users (DAU):** 50 Million
* **Reads:**
  * Assume an average user checks 20 product pages per day.
  * Total Read Requests = $50 \text{M} \times 20 = 1$ Billion requests/day.
  * **Read QPS** = $1,000,000,000 \div 86400 \approx 11,500$ QPS.
  * **Peak Read QPS** = $3 \times 11,500 \approx 35,000$ QPS.
* **Writes:** (Updates from logistics partners or inventory changes)
  * Very low compared to reads. Assume **~100 QPS**.
* **Bandwidth Estimation:**
  * Request Size: ~100 Bytes (Product ID, Destination Pincode).
  * Response Size: ~200 Bytes (JSON with booleans, SLA days, messages).
  * Total Bandwidth per second = $11,500 \times 300$ Bytes $\approx 3.45$ MB/s.

---

## 4. API Design

We need a lightweight RESTful endpoint optimized for GET requests.

**Request:** `GET /v1/delivery/serviceability?product_id={pid}&destination_pincode={pincode}`

**Response (200 OK):**
```json
{
  "product_id": "PROD-98765",
  "destination_pincode": "560001",
  "is_deliverable_in_2_days": true,
  "service_level": "2-DAY",
  "estimated_transit_hours": 42,
  "cutoff_time": "16:00:00",
  "message": "Eligible for 2-Day Delivery"
}
```

*Note: If the current time is beyond the warehouse logic `cutoff_time`, the frontend/backend can adjust expectations by adding an offset.*

---

## 5. Database Schema & Data Modeling

The system requires two primary domains of information: **Inventory Mapping** and **Logistics Routes**.

### Table 1: `product_warehouse` (Inventory Domain)
Tracks which warehouse currently has stock for a specific product.
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `product_id` (PK) | VARCHAR | Unique ID of the product. |
| `warehouse_id` (PK) | VARCHAR | ID of the warehouse stocking it. |
| `inventory_count` | INT | Available quantity. |

### Table 2: `warehouses` (Facility Domain)
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `warehouse_id` (PK) | VARCHAR | Unique warehouse ID. |
| `source_pincode` | VARCHAR | Pincode where the facility is located. |
| `processing_time_hrs`| INT | Time needed to pack & load (e.g., 4 hrs). |

### Table 3: `transit_times` (Logistics Routing Matrix)
Defines the time it takes to travel between two points.
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `source_pincode` (PK) | VARCHAR | e.g., 110001 (Delhi). |
| `dest_pincode` (PK) | VARCHAR | e.g., 560001 (Bangalore). |
| `transit_hours` | INT | Base transit time in hours. |
| `logistics_partner` (PK)| VARCHAR | e.g., EcomExpress, BlueDart. |

*Storage Consideration:* **India has approximately 19,300 PIN codes** (often rounded to 20,000 for capacity planning). The maximum size of this matrix for India is $20,000 \times 20,000 = 400$ Million rows. This handles geographic scale easily. We use a distributed NoSQL DB (like **Cassandra**) for fast distributed reads, or heavily sharded PostgreSQL/MySQL.

---

## 6. Core Logic Design (Distance/Time Validation)

When a request arrives for dynamically calculating serviceability:

1. **Locate Product:** Fetch all `warehouse_id`s holding `product_id` where `inventory_count > 0`.
2. **Resolve Sources:** Look up `source_pincode` for each identified `warehouse_id`.
3. **Transit Matrix Lookup:** Query the `transit_times` Redis cache for each `(source_pincode, destination_pincode)` permutation.
4. **Filtering & Final SLA Selection:**
   * Filter out permutations that have no viable logistics partner.
   * Calculate Total SLA: `transit_hours + warehouse.processing_time_hrs`.
   * Find the minimum Total SLA across all holding warehouses.
   * Optionally handle Time-of-Day constraints: If the order is placed after the warehouse's cut-off time, append an extra 12-24 hours.
   * **Return Data:** If the finalized SLA $\le 48$ hours, `is_deliverable_in_2_days` is returned as `true`.

---

## 7. High-Level Design (Architecture)

```ascii
                      +------------------+
                      |   Mobile/Web App |
                      +--------+---------+
                               | GET /v1/delivery/serviceability
                               v
                     +---------+---------+
                     |    API Gateway    |  (Rate Limiting, Auth, Load Balancing)
                     +---------+---------+
                               |
                               v
                  +------------+------------+
                  |  Serviceability Service | (Stateless App Servers, Horizontal Scaling)
                  +----+------------+----+--+
                       |            |    |
          +------------+            |    +-------------+
          |             Read-Through Cache             |
          v                         v                  v
  +--------------+          +--------------+   +---------------+
  | Redis Hash 1 |          | Redis Hash 2 |   | Redis Hash 3  |
  | (Inventory)  |          | (Warehouse)  |   | (Transit Time)|
  +-------+------+          +-------+------+   +-------+-------+
          |                         |                  |
   (Cache Miss / Async Update)      |                  |
          |                         |                  |
          v                         v                  v
+------------------+     +------------------+ +-------------------+
| Inventory DB     |     |   Warehouse DB   | | Route / Transit DB|
| (PostgreSQL)     |     |   (PostgreSQL)   | | (Cassandra)       |
+---------+--------+     +---------+--------+ +---------+---------+
          ^                        ^                    ^
          |                        |                    |
          +------------------------+--------------------+
                                   | (CDC / Async Events)
                          +--------+---------+
                          |   Kafka Broker   |
                          +------------------+
                                   ^
                                   |
                          +--------+---------+
                          | Logistics & Core | (Updates Transit Times,
                          | Systems          |  Restocks, Weather Alerts)
                          +------------------+
```

---

## 8. Deep Dives

### A. Extensibility for Multiple Regions & Service Levels
- **Problem:** Extending capabilities to support Hyperlocal delivery (Same-Day/10-minute) or expanding into regions with sparse/unstructured zip codes.
- **Solution:**
   - **Geospatial Queries (Hyperlocal):** Instead of a static pincode-to-pincode time matrix, introduce spatial indexing databases (like **PostGIS** or **Elasticsearch**). The logic shifts to: "Find dark-stores with stock within a 5-km radius of the user's lat/long."
   - **Zone-Based Fallbacks for Regions:** In locations where the matrix isn't fully mapped, construct pincode groups based on prefixes or geo-zones. If an exact `(source_pincode, dest_pincode)` key is missing, fallback to queries evaluating average time via `(source_zone, dest_zone)`.

### B. High Availability and Handling API Failures
Since this API runs synchronously on the product page, we cannot afford outages or slow dependency calls dragging down the frontend.
- **Local Application Cache (L1 Cache):** Redis handles peak traffic well, but a sudden flash sale (Thundering Herd hitting 35K QPS on a single iPhone ID) can bottleneck Redis shards. Introduce an In-Memory cache (e.g., Guava/Caffeine in Java) on the Serviceability Servers with short 1-minute TTLs for the hottest product-to-SLA keys.
- **Circuit Breakers & Degradation:** If the backend inventory DB is temporarily inaccessible, the API should not return an HTTP 500. Instead, gracefully degrade by resolving to a "Standard Default Delivery" (e.g., 5-7 days). It is better to show conservative timelines than preventing the checkout altogether.
- **Stale Cache Delivery:** In scenarios where Redis synchronization lags and we serve a stale timeframe (e.g., displaying 2-day delivery when stock actually just depleted 2 seconds ago), adopt an **Over-promising risk model**. The platform accepts the risk and later asynchronously emails the customer about slight delays, prioritizing uninterrupted conversion rates.

### C. Scalability of the Data Layer
- **Storing the Transit Matrix in Memory:** Caching up to 400 Million combinations requires memory efficiency.
  - Storing `{src_pin}:{dest_pin}` mapped to a 2-byte integer representing transit hours totals about $8$ GB of memory. This can be handled effectively by a minimal Redis Cluster with partitioned nodes.
- **Cache Invalidation:** Using **Kafka** guarantees eventual consistency without taxing the main read pathways. When a road is blocked or a warehouse goes offline, the logistics microservice flushes an event to Kafka. A dedicated "Cache Invalidator worker" consumes the topic and preemptively updates Redis, ensuring clients always see the nearest real-time projection.

---

## 9. API Request/Event Flow Sequence

### Visual Flow (Left-to-Right)
```ascii
+----------+ 1.GET  +---------+ 2.Route +----------------+ 3.Hit +------------+
|          | -----> |         | ------> |                | ----> | L1 Cache   | --+
| Mobile   |        | API     |         | Serviceability |       | (Instant)  |   |
| App      |        | Gateway |         | API            |       +------------+   |
+----------+        +---------+         +----------------+                        |
     ^                                        |                                   |
     |                                      3.Miss                                |
     |                                        v                                   |
     |      +-----------------+             +----------------+                    |
     |      | Redis Inventory | <=========> | Serviceability | (4. WH List)       |
     |      +-----------------+             | API            |                    |
     |                                      +----------------+                    |
     |                                        |                                   |
     |                                      5.MGET Routes                         |
     |                                        v                                   |
     |      +-----------------+             +----------------+                    |
     |      | Redis Route     | <=========> | Serviceability | (6. Transit SLAs)  |
     |      | Matrix          |             | API            |                    |
     |      +-----------------+             +----------------+                    |
     |                                        |                                   |
     |                                      7.Compute Min SLA                     |
     |                                        v                                   |
     |                                      +----------------+                    |
     +----------- 8. JSON SLA Response ---- | SLA Engine     | <------------------+
                                            +----------------+
```

### The Happy Path (Everything Works Perfectly)
Imagine a user in Bangalore (560001) opens the product page for an iPhone (`P-123`).
1. **User Action:** The mobile app calls: `GET /v1/delivery/serviceability?product_id=P-123&destination_pincode=560001`.
2. **API Gateway:** The Gateway receives the request, checks rate limits, and routes it to the `Serviceability Service`.
3. **L1 Cache (Local) Check:** The service checks if it already knows this answer recently in its local memory. If not, it moves to Redis.
4. **Inventory Cache Query:** `Serviceability Service` asks Redis: *"Which warehouses have P-123 in stock?"*
   - *Result:* Redis replies: Warehouse A (Delhi) and Warehouse B (Bangalore).
5. **Transit Cache Query:** The service then makes parallel, asynchronous requests to the Redis Transit Matrix:
   - *"How long from Delhi (110001) to Bangalore (560001)?"* -> 48 hours
   - *"How long from Bangalore (560001) to Bangalore (560001)?"* -> 12 hours
6. **Business Logic Calculation:**
   - The service adds "Warehouse Processing Time" (e.g., 4 hours) to both.
   - Delhi SLA = 52 hours. Bangalore SLA = 16 hours.
   - It picks the **minimum**: 16 hours.
7. **Final Decision:** Since 16 hours is less than 48 hours, it returns `{ "is_deliverable_in_2_days": true, "estimated_transit_hours": 16 }`.
8. **Frontend:** The UI displays **"Get it by Tomorrow!"**

### Alternative & Failure Flows (If things don't go perfectly)
- **Scenario A: Product is Out of Stock.** At step 4, Redis Inventory returns an empty list. The service halts immediately and returns `false`.
- **Scenario B: Desired SLA not met.** If the item is only in Delhi (52 hours total), the service logic evaluates `52 > 48`. It returns `false` with `estimated_transit_hours: 52`. The frontend adjusts to "Usually delivered in 3-4 days".
- **Scenario C: User orders after the Cut-off Time.** The calculated SLA is 40 hours, but the warehouse dispatch cutoff of 4 PM has passed. The service adds a 24-hour penalty (total 64 hours) and returns `false`.
- **Scenario D: Cache/DB is completely DOWN.** Connection to Redis times out. The **Circuit Breaker** catches the error. To prevent a blocked purchase flow, it returns a **Safe Default SLA** (e.g., standard 5-to-7 day delivery) so the user can still check out.

---

## 10. Architectural Decisions: Transit Matrix vs Spatial Indexing (Geohash / QuadTree)

A very common question during system design is: **Why use a static Transit Matrix instead of Geohashes or QuadTrees?**

### Why we DON'T use Geohash/QuadTrees for 2-Day Ecommerce
Geohashes and QuadTrees calculate **straight-line geographical distance** (or proximity within a radius). For national e-commerce shipping (Amazon/Flipkart), geographic distance is often a **terrible predictor** of delivery time.
- *Example 1:* A warehouse in Delhi is 2,000 km away from Bangalore, but because 5 dedicated cargo flights run between them daily, delivery takes **24 hours**.
- *Example 2:* A warehouse in a remote mountain village in the same state might only be 150 km away, but because trucks only pass through once a week, delivery takes **5 days**.

Therefore, asking a QuadTree "what is the closest warehouse?" will result in the 150km warehouse winning, which actively worsens the delivery SLA. This is why we use a pre-calculated **Transit Time Matrix** where logistics providers input the exact time based on physical infrastructure, flight availability, and highway conditions.

### When DO we use Geohash / QuadTrees? (Hyperlocal Delivery)
We switch entirely to Geohash/QuadTrees if the architecture is for a **10-Minute Grocery App** or **Food Delivery** (like Swiggy, UberEats, or Zepto).
- Over a 2 km to 5 km radius inside a city, geographic distance closely matches actual travel time on a bike.
- The system converts user GPS coordinates into a Geohash, queries a Spatial Database (PostGIS / Redis GEO / Uber's H3) to locate "Dark Stores" or drivers within a 3km radius, and routes the order to them accurately.


### 2. Spatial / Radius Filtering
If density is incredibly high, you do a fast geographical filter before touching the Transit Matrix.
- Use a Redis GEO / Geohash query: *"Find all warehouses within 100km of the user."*
- This instantly narrows the 10,000 down to roughly 20-30 stores, and you only MGET the transit SLAs for those 20.

