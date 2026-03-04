# System Design Interview Question Bank

---

## Group 1: Networking Foundations

### Client-Server Model

1. What is the client-server model and why is it fundamental to web application architecture?

<details><summary>Answer</summary>The client-server model is a pattern where the client (browser, mobile app) sends requests and the server processes them and returns responses. It is fundamental because it allows separation of concerns — clients handle presentation while servers handle business logic and data. This separation enables independent development, scaling, and deployment of frontend and backend.</details>

2. What are the advantages of separating the client and server in a system?

<details><summary>Answer</summary>Separation allows: (1) independent scaling of client and server, (2) multiple client types (web, mobile, IoT) sharing the same server, (3) independent development and deployment cycles, and (4) the ability to swap or upgrade one side without impacting the other.</details>

3. Can a server act as a client to another server? Give a scenario where this happens.

<details><summary>Answer</summary>Yes. In microservices, an API server acts as a client when it calls another backend service. For example, an Order Service (server to the user) acts as a client when it calls the Payment Service or Inventory Service to complete an order.</details>

4. How does the client-server model enable independent scaling of frontend and backend?

<details><summary>Answer</summary>Since the client and server communicate over a defined API contract, the backend can be horizontally scaled (adding more server instances behind a load balancer) without any changes to the client. Similarly, new client applications can be built without modifying the server.</details>

### IP Address

5. What is the difference between IPv4 and IPv6, and why was IPv6 introduced?

<details><summary>Answer</summary>IPv4 uses 32-bit addresses (e.g., 192.168.1.1) providing ~4.3 billion addresses. IPv6 uses 128-bit addresses (e.g., 2001:0db8::7334) providing virtually unlimited addresses. IPv6 was introduced because IPv4 addresses were exhausted due to the explosion of internet-connected devices (phones, IoT, etc.).</details>

6. How many unique addresses does IPv4 support, and why is that no longer sufficient?

<details><summary>Answer</summary>IPv4 supports approximately 4.3 billion unique addresses. This is insufficient because every smartphone, laptop, tablet, IoT device, and server needs an IP address, far exceeding 4.3 billion devices worldwide.</details>

7. In a distributed system, how are IP addresses used to identify individual components like servers, load balancers, and database nodes?

<details><summary>Answer</summary>Each component (application server, load balancer, database node, cache server) is assigned a unique IP address on the network. Other components use these IP addresses to route requests, establish connections, and communicate. Load balancers expose a single virtual IP while routing to multiple backend IPs.</details>

### DNS (Domain Name System)

8. Walk through the full DNS resolution process when a user types a URL into their browser.

<details><summary>Answer</summary>(1) Browser checks its local cache. (2) If not cached, asks the OS resolver. (3) OS asks the configured DNS resolver (usually ISP). (4) Resolver queries a root server, which directs to the TLD server (.com). (5) TLD server directs to the authoritative name server for the domain. (6) Authoritative server returns the IP address. (7) The result is cached at every level for future lookups.</details>

9. What are root servers, TLD servers, and authoritative name servers? How do they work together?

<details><summary>Answer</summary>Root servers are the top of the DNS hierarchy — they direct queries to TLD servers. TLD (Top-Level Domain) servers handle domains like .com, .org, .net and point to the authoritative name servers. Authoritative name servers hold the actual DNS records for a specific domain and return the final IP address.</details>

10. How does DNS caching improve performance, and at which levels does caching occur?

<details><summary>Answer</summary>DNS caching avoids repeating the full resolution chain for every request. Caching occurs at: (1) the browser, (2) the operating system, (3) the ISP's DNS resolver, and (4) intermediate DNS servers. Each level has a TTL (time-to-live) after which the cache expires and a fresh lookup is performed.</details>

11. How can DNS be used for load balancing and failover?

<details><summary>Answer</summary>For load balancing, DNS can return different IP addresses for the same domain in a round-robin fashion, distributing traffic across multiple servers. For failover, DNS health checks can detect a downed server and stop returning its IP, redirecting traffic to healthy servers.</details>

12. What happens if a DNS server goes down? How does the system handle this?

<details><summary>Answer</summary>If one DNS server goes down, redundancy handles it — DNS zones are typically served by multiple name servers. Clients and resolvers also rely on cached results, allowing resolution to continue temporarily. If all authoritative servers for a domain go down and caches expire, the domain becomes unreachable.</details>

### Proxy vs Reverse Proxy

13. What is the difference between a forward proxy and a reverse proxy?

<details><summary>Answer</summary>A forward proxy sits in front of clients and hides the client's identity from the server (e.g., VPN, corporate proxy). A reverse proxy sits in front of servers and hides the server's identity from the client (e.g., Nginx, HAProxy). Forward proxies protect clients; reverse proxies protect and optimize servers.</details>

14. Give real-world use cases for a forward proxy.

<details><summary>Answer</summary>(1) VPNs — hiding user identity and bypassing geo-restrictions. (2) Corporate proxies — filtering content and monitoring employee internet usage. (3) Caching proxies — caching frequently accessed content to save bandwidth. (4) Anonymity — masking the client's real IP address.</details>

15. Why do large-scale systems place a reverse proxy in front of their backend servers?

<details><summary>Answer</summary>Reverse proxies provide: (1) load balancing across multiple servers, (2) SSL termination (offloading encryption from app servers), (3) caching of static content, (4) compression, (5) protection against DDoS attacks, and (6) a single entry point that hides backend infrastructure.</details>

16. What additional responsibilities can a reverse proxy handle beyond routing (e.g., SSL termination, caching, compression)?

<details><summary>Answer</summary>Beyond routing: SSL/TLS termination, response caching, gzip/brotli compression, rate limiting, request logging, A/B testing (routing subsets of traffic), health checking backend servers, and serving as a web application firewall (WAF).</details>

### Latency

17. What are the main sources of latency in a distributed system?

<details><summary>Answer</summary>(1) Network distance — speed of light in fiber optic cables. (2) Serialization/deserialization — converting data to/from bytes. (3) Server processing time — executing business logic. (4) Queuing delays — when the server is busy and requests wait. (5) DNS resolution time. (6) TLS handshake overhead.</details>

18. How does physical distance between client and server affect latency?

<details><summary>Answer</summary>Data travels at the speed of light through fiber optic cables. A round trip from Mumbai to New York (~13,000 km) takes ~200ms minimum due to physics alone. This cannot be reduced — the only solution is to move the server closer to the user using CDNs or regional deployments.</details>

19. What techniques can you use to reduce latency in a system design?

<details><summary>Answer</summary>(1) CDNs — serve content from edge nodes near users. (2) Caching — avoid unnecessary database or network round trips. (3) Regional deployments — place servers closer to users. (4) Connection pooling — reuse existing connections. (5) Data compression — reduce payload size. (6) Async processing — offload non-critical work to background queues.</details>

20. A user in Mumbai is experiencing 200ms latency to a server in New York. How would you bring this below 50ms?

<details><summary>Answer</summary>Deploy a CDN edge node or regional server in or near Mumbai. Serve static assets from the CDN. Cache frequently accessed dynamic data at the edge or in a regional Redis cache. Use connection keep-alive to avoid repeated TLS handshakes. The key is to eliminate the cross-continent round trip.</details>

### HTTP / HTTPS

21. Why is HTTP considered a stateless protocol, and what are the implications for scaling?

<details><summary>Answer</summary>HTTP is stateless because each request is independent — the server retains no memory of previous requests. This makes scaling easier because any server can handle any request (no session affinity required). The trade-off is that state must be managed externally via cookies, tokens, or session stores.</details>

22. How does HTTPS differ from HTTP? Explain the TLS handshake process at a high level.

<details><summary>Answer</summary>HTTPS encrypts HTTP traffic using TLS. The TLS handshake: (1) Client sends "ClientHello" with supported TLS versions and cipher suites. (2) Server responds with "ServerHello" and its SSL certificate. (3) Client verifies the certificate and both parties perform a key exchange. (4) A symmetric session key is established. (5) All subsequent data is encrypted with this key.</details>

23. What are the common HTTP methods and when would you use each one?

<details><summary>Answer</summary>GET — retrieve a resource. POST — create a new resource. PUT — replace/update an entire resource. PATCH — partially update a resource. DELETE — remove a resource. OPTIONS — check what methods are supported. HEAD — same as GET but returns only headers (useful for checking if a resource exists).</details>

24. Explain the significance of HTTP status codes 200, 301, 400, 401, 403, 404, and 500.

<details><summary>Answer</summary>200 OK — request succeeded. 301 Moved Permanently — resource has a new URL. 400 Bad Request — client sent invalid data. 401 Unauthorized — authentication required. 403 Forbidden — authenticated but not authorized. 404 Not Found — resource does not exist. 500 Internal Server Error — server-side failure.</details>

25. How do cookies and tokens compensate for HTTP's statelessness?

<details><summary>Answer</summary>Cookies store session IDs on the client, sent with every request so the server can look up session state. Tokens (like JWTs) encode user identity/claims directly in the token, so the server can verify the user without a session store. Both approaches carry state across stateless HTTP requests.</details>

---

## Group 2: APIs and Communication

### APIs (Application Programming Interfaces)

26. What is an API, and why is it described as a "contract" between software components?

<details><summary>Answer</summary>An API defines the set of requests a client can make, the format of those requests, and the structure of the responses. It is a "contract" because both parties agree on this interface — the client knows what to send, and the server guarantees what it will return. Changes to the contract require versioning to avoid breaking clients.</details>

27. What role does the API layer play in abstracting backend complexity from clients?

<details><summary>Answer</summary>The API layer acts as a facade — the client interacts with clean endpoints without knowing about the backend's databases, caching layers, third-party services, or internal architecture. This allows the backend to change its implementation (e.g., switch databases) without affecting clients.</details>

28. What are the key components of a well-designed API (endpoints, request/response formats, status codes)?

<details><summary>Answer</summary>Key components: (1) Clear, resource-oriented endpoints (e.g., /users, /orders). (2) Consistent request/response formats (usually JSON). (3) Proper HTTP methods (GET, POST, PUT, DELETE). (4) Meaningful status codes (200, 201, 400, 404, 500). (5) Versioning (e.g., /v1/users). (6) Authentication (API keys, OAuth tokens). (7) Pagination for list endpoints.</details>

### REST API

29. What are the core principles of REST (statelessness, cacheability, uniform interface)?

<details><summary>Answer</summary>(1) Statelessness — each request contains all information needed; the server stores no session state. (2) Cacheability — responses should indicate whether they can be cached. (3) Uniform interface — consistent URL patterns and HTTP methods. (4) Client-server separation. (5) Layered system — client cannot tell if it's connected directly to the server or through intermediaries.</details>

30. How do RESTful URLs and HTTP methods map to CRUD operations?

<details><summary>Answer</summary>Create → POST /users (create a new user). Read → GET /users/123 (fetch user 123). Update → PUT /users/123 (replace user 123) or PATCH /users/123 (partial update). Delete → DELETE /users/123 (remove user 123). List → GET /users (fetch all users).</details>

31. What are the drawbacks of REST when a client needs data from multiple resources?

<details><summary>Answer</summary>REST requires separate requests for each resource. Fetching a user profile with their posts and comments could require 3+ requests (over-fetching or under-fetching). This increases latency and network overhead, especially on mobile. This is the exact problem GraphQL was designed to solve.</details>

32. How would you design a RESTful API for a resource like "users" with sub-resources like "posts"?

<details><summary>Answer</summary>GET /users — list all users. GET /users/123 — get user 123. POST /users — create user. GET /users/123/posts — list posts by user 123. POST /users/123/posts — create a post for user 123. GET /users/123/posts/456 — get specific post. This nesting clearly expresses the parent-child relationship.</details>

33. What makes an API "RESTful" vs just "an API that uses HTTP"?

<details><summary>Answer</summary>A truly RESTful API follows REST constraints: statelessness, resource-based URLs (nouns, not verbs), proper use of HTTP methods, hypermedia links (HATEOAS), cacheability, and a uniform interface. Many APIs use HTTP but use verbs in URLs (e.g., /getUser), ignore proper methods, or maintain server-side sessions — these are HTTP APIs, not RESTful.</details>

### GraphQL

34. How does GraphQL solve the over-fetching and under-fetching problems of REST?

<details><summary>Answer</summary>GraphQL lets the client specify exactly which fields it needs in a single query. No over-fetching (receiving unnecessary fields) and no under-fetching (needing multiple endpoints). A single query can request a user's name, their posts' titles, and their friends' avatars — all in one round trip.</details>

35. What are the trade-offs of using GraphQL compared to REST?

<details><summary>Answer</summary>Trade-offs: (1) Server complexity — requires resolvers for each field. (2) Caching is harder — every query is unique, unlike REST's cacheable URLs. (3) Deeply nested queries can cause N+1 problems and performance issues. (4) Steeper learning curve. (5) Harder to rate-limit (one query can be simple or extremely expensive).</details>

36. In what types of applications is GraphQL a better fit than REST?

<details><summary>Answer</summary>GraphQL excels in: (1) Mobile apps where bandwidth is limited and you want minimal payloads. (2) Social media feeds needing flexible, nested data. (3) Applications with many different client types (web, mobile, TV) each needing different data shapes. (4) Rapidly evolving frontends that frequently change data requirements.</details>

37. What are resolvers in GraphQL, and why can deeply nested queries cause performance issues?

<details><summary>Answer</summary>Resolvers are functions that fetch the data for each field in a query. For a nested query like user → posts → comments → author, each level triggers its own resolver, potentially causing N+1 query problems (fetching authors one by one for each comment). Solutions include DataLoader (batching) and query depth limiting.</details>

### WebSockets

38. How do WebSockets differ from traditional HTTP request-response communication?

<details><summary>Answer</summary>HTTP is unidirectional (client initiates, server responds) and each request creates a new connection. WebSockets establish a persistent, bidirectional connection — both client and server can send messages at any time without the overhead of new connections. This enables real-time communication.</details>

39. Walk through the lifecycle of a WebSocket connection from initiation to closure.

<details><summary>Answer</summary>(1) Client sends an HTTP request with an "Upgrade: websocket" header. (2) Server responds with 101 Switching Protocols. (3) The connection is upgraded to WebSocket — now bidirectional. (4) Both sides exchange messages freely over the open connection. (5) Either side can send a close frame to terminate the connection.</details>

40. Why are WebSocket connections harder to scale than stateless HTTP connections?

<details><summary>Answer</summary>WebSocket connections are stateful — the server must maintain each open connection in memory. If a server holds 10,000 connections and goes down, all 10,000 are lost. Load balancing is harder because connections are sticky (you can't route mid-connection). Horizontal scaling requires a pub/sub layer (like Redis) to broadcast messages across servers.</details>

41. Name three real-world use cases where WebSockets are the right choice.

<details><summary>Answer</summary>(1) Chat applications (instant message delivery). (2) Live sports scores or stock tickers (real-time data push). (3) Collaborative editing tools like Google Docs (real-time sync between users). Other examples: multiplayer games, live notifications, IoT device monitoring.</details>

42. What happens to active WebSocket connections if the server goes down?

<details><summary>Answer</summary>All active connections on that server are immediately lost. Clients must detect the disconnection (via heartbeat/ping-pong timeouts) and reconnect — ideally to another healthy server via the load balancer. Any in-flight messages may be lost unless the system has a message persistence layer (e.g., message queue).</details>

### Webhooks

43. How do webhooks differ from polling, and why are they more efficient?

<details><summary>Answer</summary>Polling means the client repeatedly asks "any updates?" at intervals — wasteful when there are no changes. Webhooks flip this: the server pushes a notification to the client's registered URL only when an event occurs. This eliminates wasted requests and delivers updates in near real-time.</details>

44. What challenges arise with webhook reliability, and how do you handle them (retries, idempotency)?

<details><summary>Answer</summary>Challenges: (1) Your server may be down when the webhook fires. (2) Network failures can cause missed or duplicate deliveries. Solutions: (1) The sender retries with exponential backoff. (2) The receiver implements idempotency (using event IDs to deduplicate). (3) Event logging for audit and replay. (4) Dead-letter queues for failed deliveries.</details>

45. A payment provider like Stripe sends a webhook to your server, but your server is temporarily down. How should the system handle this?

<details><summary>Answer</summary>Stripe will retry the webhook with exponential backoff (e.g., after 1min, 5min, 30min, etc.). Your server should: (1) Return 200 OK quickly upon receiving the webhook. (2) Process it asynchronously. (3) Use the event ID for idempotency to handle duplicate deliveries when retries arrive. (4) Have a reconciliation job that periodically checks for missed events.</details>

46. What security concerns exist with webhooks, and how would you address them?

<details><summary>Answer</summary>(1) Spoofing — anyone could POST to your webhook URL. Solution: verify webhook signatures (e.g., Stripe signs payloads with a secret). (2) Replay attacks — old webhooks resent. Solution: check timestamps and reject old events. (3) Data exposure — webhook payloads may contain sensitive data. Solution: use HTTPS and validate the source IP if possible.</details>

---

## Group 3: Data Storage

### Databases

47. What are the four main types of databases (relational, document, key-value, graph), and when would you choose each?

<details><summary>Answer</summary>Relational (PostgreSQL, MySQL) — structured data with relationships, ACID needed. Document (MongoDB) — flexible/evolving schemas, JSON-like data. Key-value (Redis, DynamoDB) — fast lookups by key, caching, sessions. Graph (Neo4j) — heavily connected data like social networks or recommendation engines. Choose based on data model and query patterns.</details>

48. For a social network, which database type would you use for user profiles, and which for modeling friend relationships? Why?

<details><summary>Answer</summary>User profiles → Document or Relational database (structured data with flexible fields like bio, interests). Friend relationships → Graph database (Neo4j) because friendships are inherently graph-like — traversing connections (friends-of-friends, mutual friends) is orders of magnitude faster in a graph DB than doing recursive joins in SQL.</details>

49. What factors should you consider when choosing a database for a new system?

<details><summary>Answer</summary>(1) Data model — structured, semi-structured, or unstructured? (2) Query patterns — simple lookups vs complex joins? (3) Consistency requirements — strong vs eventual? (4) Scale — read-heavy vs write-heavy? (5) Schema flexibility — fixed or evolving? (6) Latency requirements. (7) Operational maturity and team expertise.</details>

### SQL vs NoSQL

50. When would you choose a SQL database over a NoSQL database, and vice versa?

<details><summary>Answer</summary>Choose SQL when: strong consistency is required (banking, inventory), complex queries with joins are needed, schema is well-defined, ACID guarantees matter. Choose NoSQL when: horizontal scalability is needed, schema evolves frequently, high write throughput is required, data is naturally unstructured (logs, social media), eventual consistency is acceptable.</details>

51. What does ACID stand for, and why does it matter for transactional systems?

<details><summary>Answer</summary>Atomicity — transaction fully completes or fully rolls back. Consistency — data moves from one valid state to another. Isolation — concurrent transactions don't interfere. Durability — committed data survives crashes. ACID matters for systems like banking where partial operations (e.g., money debited but not credited) would be catastrophic.</details>

52. What does "eventual consistency" mean in the context of NoSQL databases?

<details><summary>Answer</summary>Eventual consistency means that after a write, not all replicas immediately reflect the update. Given enough time with no new writes, all replicas will converge to the same value. Reads during this window may return stale data. This is acceptable for systems like social feeds where a post appearing a second late is fine.</details>

53. Can you use both SQL and NoSQL in the same system? Give an example.

<details><summary>Answer</summary>Yes, this is called polyglot persistence. Example: An e-commerce platform uses PostgreSQL for orders and payments (needs ACID), MongoDB for the product catalog (flexible schema, read-heavy), and Redis as a key-value cache for session data and frequently accessed product details.</details>

54. A system handles both financial transactions and user activity logs. Which database type would you use for each, and why?

<details><summary>Answer</summary>Financial transactions → SQL (PostgreSQL) because ACID compliance is critical — you cannot have partial transfers or inconsistent balances. User activity logs → NoSQL (Cassandra or MongoDB) because logs are append-heavy, schema may evolve (new event types), volume is massive, and eventual consistency is perfectly fine.</details>

### Database Indexing

55. What is a database index, and how does it improve query performance?

<details><summary>Answer</summary>An index is a data structure (typically a B-tree) built on one or more columns that allows the database to find rows without scanning the entire table. Instead of O(n) full table scans, indexed lookups are O(log n). It's like the index at the back of a textbook — you jump directly to the relevant page.</details>

56. Explain how a B-tree index works at a high level.

<details><summary>Answer</summary>A B-tree is a balanced, sorted tree structure. Each node contains multiple keys and pointers. Searching starts at the root and follows pointers based on comparisons, narrowing down at each level until reaching a leaf node that contains the actual row location on disk. The tree stays balanced, guaranteeing O(log n) lookups regardless of data size.</details>

57. What is the trade-off of adding indexes to a table?

<details><summary>Answer</summary>Indexes speed up reads (lookups, WHERE clauses, JOINs) but slow down writes. Every INSERT, UPDATE, or DELETE must also update all affected indexes. Indexes also consume additional disk space. The trade-off is: faster reads at the cost of slower writes and more storage.</details>

58. Which columns should you typically index, and which should you avoid indexing?

<details><summary>Answer</summary>Index: columns in WHERE clauses, JOIN conditions, ORDER BY, and columns with high cardinality (many unique values like email, user_id). Avoid indexing: columns rarely queried, columns with low cardinality (e.g., boolean gender), tables with very frequent writes and rare reads, and very wide columns (large text fields).</details>

59. If a query is slow on a table with 100 million rows, what is the first thing you would investigate?

<details><summary>Answer</summary>Run EXPLAIN (or EXPLAIN ANALYZE) on the query to see the query execution plan. Check if the query is doing a full table scan instead of using an index. If the relevant columns aren't indexed, add appropriate indexes. Also check for missing JOIN indexes, inefficient subqueries, or lock contention.</details>

### Vertical Partitioning

60. What is vertical partitioning, and how does it differ from horizontal partitioning?

<details><summary>Answer</summary>Vertical partitioning splits a table by columns — each partition holds a subset of columns (e.g., profile data vs billing data). Horizontal partitioning (sharding) splits by rows — each partition holds a subset of rows. Vertical separates by access pattern; horizontal separates by data volume.</details>

61. Give an example of when vertical partitioning would improve performance.

<details><summary>Answer</summary>A Users table with 30 columns: name, email, avatar, bio, password_hash, billing_address, card_number, login_count, etc. The profile page only needs name, email, avatar. By splitting into Profile, Auth, and Billing tables, profile queries read far fewer bytes from disk, improving speed and cache efficiency.</details>

62. How does vertical partitioning improve security in addition to performance?

<details><summary>Answer</summary>By separating sensitive data (billing info, passwords) into dedicated tables, you can apply stricter access controls (different permissions, encryption at rest, audit logging) to those tables without affecting the performance or access patterns of non-sensitive data like profile information.</details>

### Caching

63. Explain the cache-aside (lazy loading) pattern step by step.

<details><summary>Answer</summary>(1) Application receives a request. (2) Check the cache (e.g., Redis) for the data. (3) Cache HIT → return data immediately. (4) Cache MISS → query the database. (5) Store the result in the cache with a TTL. (6) Return the data to the client. Subsequent requests for the same data hit the cache, avoiding the database.</details>

64. What are the common cache invalidation strategies (TTL, write-through, write-behind)?

<details><summary>Answer</summary>TTL (Time-to-Live) — cache entries expire automatically after a set duration. Simple but may serve stale data. Write-through — every write updates both the cache and the database simultaneously. Consistent but adds write latency. Write-behind — write to cache first, then asynchronously update the database. Fast writes but risks data loss if cache crashes before DB write.</details>

65. What is a cache stampede, and how would you prevent it?

<details><summary>Answer</summary>A cache stampede occurs when a popular cache entry expires and hundreds of concurrent requests all miss the cache simultaneously, flooding the database. Prevention: (1) Lock/mutex — only one request fetches from DB while others wait. (2) Staggered TTLs — add jitter to expiration times. (3) Background refresh — proactively refresh before expiry.</details>

66. When should you NOT use caching?

<details><summary>Answer</summary>(1) When data changes very frequently and staleness is unacceptable (e.g., real-time bank balances). (2) When the data is rarely read more than once (caching provides no benefit). (3) When the working set is too large to fit in memory. (4) When consistency is more important than performance.</details>

67. Compare Redis and Memcached. When would you choose one over the other?

<details><summary>Answer</summary>Redis: supports rich data structures (lists, sets, sorted sets, hashes), persistence, replication, pub/sub. Choose when you need more than simple key-value caching (e.g., leaderboards, rate limiting, session management). Memcached: simpler, multi-threaded, slightly faster for pure key-value caching. Choose for straightforward, high-throughput caching with no persistence needs.</details>

### Denormalization

68. What is denormalization, and why would you intentionally add redundant data?

<details><summary>Answer</summary>Denormalization adds redundant copies of data to reduce expensive JOIN operations at read time. Instead of joining Users, Orders, and Products tables, you store user_name and product_title directly in the Orders table. This trades storage and write complexity for dramatically faster reads.</details>

69. What are the risks of denormalization, and how do you keep redundant data consistent?

<details><summary>Answer</summary>Risks: data inconsistency (if a user changes their name, it must be updated everywhere), increased storage, and more complex writes. Consistency strategies: (1) Application-level updates (update all copies in the same transaction). (2) Event-driven updates (publish a change event, consumers update their copies). (3) Periodic reconciliation jobs.</details>

70. In what type of systems is denormalization most beneficial?

<details><summary>Answer</summary>Read-heavy systems where read performance is critical: social media feeds, e-commerce product pages, analytics dashboards. If a system has a 100:1 read-to-write ratio, optimizing reads with denormalization is almost always worth the trade-off in write complexity.</details>

71. How does denormalization relate to NoSQL database design?

<details><summary>Answer</summary>NoSQL databases (especially document stores like MongoDB) don't natively support JOINs. So you denormalize by design — embedding related data within a single document. A user document might contain their posts, comments, and profile in one object, eliminating the need for joins entirely.</details>

### Blob Storage

72. Why should you store large files (images, videos) in blob storage instead of a database?

<details><summary>Answer</summary>Databases are optimized for structured queries, not storing multi-megabyte files. Storing blobs in a DB bloats table size, slows backups, wastes expensive DB resources, and hurts query performance. Blob storage (S3) is purpose-built: cheap, highly durable, scalable to petabytes, and integrates with CDNs for fast delivery.</details>

73. Describe the typical pattern for handling file uploads in a system (blob store + URL in DB).

<details><summary>Answer</summary>(1) Client uploads the file to the application server (or directly to blob storage via a pre-signed URL). (2) The file is stored in blob storage (e.g., S3). (3) Blob storage returns a URL/key. (4) The application stores only this URL/key in the database. (5) When serving the file, the URL points to S3 or a CDN in front of S3.</details>

74. What does "11 nines of durability" mean in the context of services like Amazon S3?

<details><summary>Answer</summary>99.999999999% durability means that if you store 10 million objects, you can statistically expect to lose a single object once every 10,000 years. S3 achieves this by automatically replicating data across multiple facilities and availability zones. This makes blob storage extremely trustworthy for critical data.</details>

75. How do CDNs integrate with blob storage to serve media files efficiently?

<details><summary>Answer</summary>The blob store (S3) acts as the origin server. The CDN (CloudFront) caches files at edge nodes worldwide. The first request from a region goes to S3 (cache miss), but subsequent requests are served from the nearest edge node. This reduces latency, decreases load on S3, and provides faster media delivery globally.</details>

---

## Group 4: Scaling

### Vertical Scaling (Scale Up)

76. What is vertical scaling, and what are its advantages?

<details><summary>Answer</summary>Vertical scaling means upgrading a single machine (more CPU, RAM, faster disks). Advantages: (1) No code changes required. (2) No distributed systems complexity. (3) Simple operational model. (4) Works well for small-to-medium workloads. It's the easiest and fastest way to handle more load initially.</details>

77. What are the limitations of vertical scaling?

<details><summary>Answer</summary>(1) Hardware ceiling — machines have maximum specs you cannot exceed. (2) Disproportionate cost — the biggest instances cost exponentially more. (3) Single point of failure — if the one big server goes down, everything goes down. (4) Downtime during upgrades — scaling up often requires restarting the machine.</details>

78. At what point should a team consider moving from vertical to horizontal scaling?

<details><summary>Answer</summary>When: (1) you're approaching the maximum instance size available, (2) costs are increasing faster than capacity gains, (3) you need high availability (single point of failure is unacceptable), (4) traffic is growing unpredictably and you need elastic scaling, or (5) you need to deploy across multiple regions.</details>

### Horizontal Scaling (Scale Out)

79. What is horizontal scaling, and why is there no theoretical upper limit?

<details><summary>Answer</summary>Horizontal scaling means adding more machines to the pool instead of upgrading one machine. There's no upper limit because you can keep adding servers — 10, 100, 10,000. Each server handles a portion of the traffic. Google, Netflix, and Amazon all scale this way across thousands of machines.</details>

80. What design constraints does horizontal scaling impose on your application?

<details><summary>Answer</summary>(1) Application servers must be stateless — no local session storage. (2) Shared state must live in external stores (Redis, database). (3) Need a load balancer to distribute traffic. (4) Database needs its own scaling strategy (replication/sharding). (5) Deployments must handle multiple instances (rolling updates, blue-green deployments).</details>

81. Why must application servers be stateless for horizontal scaling to work effectively?

<details><summary>Answer</summary>If a server stores user sessions locally, a user routed to a different server on their next request will lose their session. Stateless servers ensure any server can handle any request. All shared state (sessions, carts, etc.) lives in a centralized store (Redis) accessible by all server instances.</details>

82. Where should session data be stored in a horizontally scaled system, and why?

<details><summary>Answer</summary>In a shared, external store like Redis or a database. This way, any server instance can access any user's session. Redis is the most popular choice because it's in-memory (fast), supports TTL (sessions auto-expire), and can be replicated for high availability.</details>

### Load Balancers

83. What is a load balancer, and where does it sit in a typical system architecture?

<details><summary>Answer</summary>A load balancer distributes incoming requests across multiple backend servers to prevent any single server from being overwhelmed. It sits between the client and the server pool. In a typical architecture, it's the first thing after DNS resolution — clients hit the load balancer, which routes to healthy backend servers.</details>

84. Compare Round Robin, Least Connections, and Weighted load balancing algorithms. When would you use each?

<details><summary>Answer</summary>Round Robin — distributes sequentially; good when servers are identical and requests are uniform. Least Connections — routes to the server with fewest active connections; good when request processing times vary. Weighted — assigns more traffic to more powerful servers; good when servers have different capacities (e.g., mix of old and new hardware).</details>

85. How do health checks work in a load balancer, and what happens when a server fails?

<details><summary>Answer</summary>The load balancer periodically sends health check requests (e.g., HTTP GET /health) to each server. If a server fails to respond within a timeout or returns an error for consecutive checks, the LB marks it as unhealthy and stops routing traffic to it. Traffic is redistributed to remaining healthy servers. When the server recovers, it's automatically added back.</details>

86. Can you have multiple layers of load balancers in a system? Why would you?

<details><summary>Answer</summary>Yes. A common pattern: Layer 1 LB in front of web/API servers, Layer 2 LB in front of application/microservice servers, Layer 3 LB in front of database replicas. Each layer independently handles distribution and failover for its tier, providing defense in depth and allowing each tier to scale independently.</details>

### Replication

87. Explain the primary-replica replication model. How do reads and writes flow?

<details><summary>Answer</summary>All writes go to a single primary (master) database. Changes are then replicated to one or more read replicas. Read queries are directed to replicas, offloading the primary. This works well for read-heavy workloads (most apps are 90%+ reads). The primary handles consistency; replicas handle scale.</details>

88. What is replication lag, and what problems can it cause?

<details><summary>Answer</summary>Replication lag is the delay between a write to the primary and its appearance on replicas. Problems: (1) A user updates their profile but sees the old data on a subsequent read (read-your-own-write inconsistency). (2) Two users see different data for the same resource. Solutions: read critical data from the primary, or use "read-after-write" consistency guarantees.</details>

89. For which types of reads should you always query the primary rather than a replica?

<details><summary>Answer</summary>Read from the primary when: (1) immediately after a write (e.g., user just updated their email, show the new email). (2) For financial/critical data where stale reads are unacceptable (account balance, inventory count). (3) For operations that depend on the latest state (e.g., checking if a username is taken during registration).</details>

90. What happens when the primary database goes down in a replicated setup?

<details><summary>Answer</summary>A replica is promoted to become the new primary (this process is called failover). It can be automatic (using tools like orchestrators or cloud-managed failover) or manual. During the transition, writes may be briefly unavailable. Any unreplicated writes on the old primary may be lost. After promotion, other replicas are reconfigured to replicate from the new primary.</details>

### Sharding

91. What is sharding, and how does it differ from replication?

<details><summary>Answer</summary>Sharding splits data across multiple nodes — each node holds a different subset of the data (e.g., users 1-1M on Shard 1, 1M-2M on Shard 2). Replication copies all data to every node. Sharding distributes the write load and storage; replication distributes the read load. They're often used together.</details>

92. What is a shard key, and why is choosing the right one critical?

<details><summary>Answer</summary>The shard key determines which shard holds each row of data (e.g., user_id % N). A bad key causes uneven distribution — one shard gets most traffic (hot shard) while others are idle. A good shard key has high cardinality, distributes evenly, and aligns with query patterns so most queries hit a single shard.</details>

93. What is a "hot shard," and how would you prevent one?

<details><summary>Answer</summary>A hot shard receives disproportionately more traffic than others. Example: sharding by date puts all today's writes on one shard. Prevention: (1) use a hash-based shard key for uniform distribution, (2) add a random suffix or salt to the key, (3) use composite shard keys, (4) monitor shard load and rebalance when needed.</details>

94. What are the challenges of cross-shard queries?

<details><summary>Answer</summary>Cross-shard queries (e.g., JOIN or aggregate across shards) require the application to query multiple shards and merge results — this is slow and complex. There's no single transaction across shards (no distributed ACID by default). This is why choosing a shard key that keeps related data together is so important.</details>

95. You have 500 million users and a single database can hold 100 million. Design a sharding strategy.

<details><summary>Answer</summary>Use 5+ shards with hash-based sharding on user_id (hash(user_id) % num_shards). Each shard holds ~100M users. Add read replicas to each shard for read scaling. Use a shard router/proxy to direct queries. Plan for future growth by using consistent hashing, which makes adding new shards easier without reshuffling all data.</details>

---

## Group 5: Distributed Systems

### CAP Theorem

96. State the CAP theorem and explain each of the three properties.

<details><summary>Answer</summary>The CAP theorem states a distributed system can guarantee only 2 of 3 properties: Consistency (every read returns the latest write), Availability (every request gets a response), Partition Tolerance (system works despite network failures between nodes). Since network partitions are inevitable, the real choice is between CP and AP.</details>

97. Why is partition tolerance non-negotiable in a distributed system?

<details><summary>Answer</summary>Network partitions (communication failures between nodes) are unavoidable in any distributed system — cables fail, switches go down, data centers lose connectivity. A system that can't handle partitions simply isn't a distributed system. So the real trade-off is always between consistency and availability during a partition.</details>

98. What is the practical choice that engineers face given the CAP theorem (CP vs AP)?

<details><summary>Answer</summary>CP (Consistency + Partition Tolerance): system refuses to serve requests if it can't guarantee data is up-to-date. Good for banking, inventory. AP (Availability + Partition Tolerance): system always responds, even if data might be stale. Good for social feeds, product catalogs. The choice depends on whether stale data or downtime is more harmful.</details>

99. Give an example of a system that should be CP and one that should be AP. Justify your choices.

<details><summary>Answer</summary>CP: A banking system — showing an incorrect account balance or processing a duplicate transfer is unacceptable. Better to return an error than wrong data. AP: A social media feed — if a post appears a second late on some users' feeds, that's fine. Availability (always loading the feed) is more important than perfect real-time consistency.</details>

100. How does eventual consistency relate to the CAP theorem?

<details><summary>Answer</summary>Eventual consistency is the consistency model used by AP systems. During normal operation, data is consistent. During a partition, the system remains available but may serve stale data. Once the partition heals, all nodes converge to the same state. It's a weaker guarantee than strong consistency but enables higher availability.</details>

### CDN (Content Delivery Network)

101. How does a CDN reduce latency for end users?

<details><summary>Answer</summary>A CDN caches content at edge servers distributed globally. Instead of every request traveling to the origin server (potentially across continents), users get content from the nearest edge node — often in the same city or country. This dramatically reduces the physical distance data travels, cutting latency from hundreds of milliseconds to single digits.</details>

102. What types of content are best served through a CDN?

<details><summary>Answer</summary>Static content: images, CSS, JavaScript files, fonts, videos, PDFs. Some CDNs also cache dynamic content (API responses with appropriate cache headers) or run serverless functions at the edge. Content that rarely changes and is accessed by many users benefits most from CDN caching.</details>

103. What happens on a CDN cache miss? Walk through the full flow.

<details><summary>Answer</summary>(1) User requests a resource. (2) Request hits the nearest CDN edge node. (3) Edge node doesn't have the content (cache miss). (4) Edge node fetches the content from the origin server. (5) Origin returns the content. (6) Edge node caches it (with a TTL) and serves it to the user. (7) Subsequent requests from users in that region get the cached copy instantly.</details>

104. How does a CDN improve availability even if the origin server goes down?

<details><summary>Answer</summary>CDN edge nodes serve cached content independently of the origin. If the origin goes down, any content already cached at edge nodes continues to be served until the cache TTL expires. This provides a buffer — users may not even notice a brief origin outage if the content was recently cached.</details>

105. Name three major CDN providers and their differentiating features.

<details><summary>Answer</summary>(1) CloudFront (AWS) — deep integration with AWS services (S3, EC2), Lambda@Edge for serverless at the edge. (2) Cloudflare — strong DDoS protection, built-in WAF, DNS services, generous free tier. (3) Akamai — largest and oldest CDN network, enterprise-grade, extensive global coverage. Choice depends on existing cloud provider, security needs, and scale.</details>

### Idempotency

106. What does idempotency mean, and why is it important in distributed systems?

<details><summary>Answer</summary>An idempotent operation produces the same result no matter how many times it's executed. It's critical in distributed systems because network failures cause retries — if a payment request times out, the client retries, and without idempotency, the customer could be charged twice. Idempotency ensures retries are safe.</details>

107. Which HTTP methods are naturally idempotent, and which are not?

<details><summary>Answer</summary>Naturally idempotent: GET (fetching the same resource twice returns the same result), PUT (replacing a resource with the same data), DELETE (deleting an already-deleted resource is a no-op). NOT naturally idempotent: POST (creating a resource twice creates two resources). This is why POST operations need explicit idempotency keys.</details>

108. How do idempotency keys work? Give an example with a payment system.

<details><summary>Answer</summary>The client generates a unique idempotency key (e.g., UUID) and sends it with the request. The server checks: has this key been seen before? If yes, return the stored result without reprocessing. If no, process the request and store the result with that key. Example: POST /payments with Idempotency-Key: abc-123. If retried with the same key, the server returns the original payment result.</details>

109. A network timeout occurs after a client sends a payment request. The client retries. How does idempotency prevent a double charge?

<details><summary>Answer</summary>The first request may have succeeded (the server processed it, but the response was lost due to the timeout). When the client retries with the same idempotency key, the server looks up that key, finds it was already processed, and returns the original result (payment_id, amount, status) without charging again. The client gets a successful response as if the first request completed normally.</details>

110. Why do payment APIs like Stripe require idempotency keys?

<details><summary>Answer</summary>Payment operations have real financial consequences — duplicate charges damage customer trust and create reconciliation nightmares. Network failures and retries are inevitable. Stripe requires idempotency keys so that even if a client retries a charge request 10 times (due to timeouts), the customer is charged exactly once. It's a safety net for the entire payment flow.</details>

---

## Group 6: Architecture Patterns

### Microservices

111. What are microservices, and how do they differ from a monolithic architecture?

<details><summary>Answer</summary>Microservices split an application into small, independent services — each responsible for one business capability with its own database. A monolith is a single codebase where all features are tightly coupled. Microservices enable independent deployment, scaling, and team ownership, but introduce distributed systems complexity (network calls, eventual consistency, operational overhead).</details>

112. What are the key benefits of microservices (independent deployment, scaling, team autonomy)?

<details><summary>Answer</summary>(1) Independent deployment — update one service without redeploying everything. (2) Independent scaling — scale only the services under heavy load. (3) Team autonomy — different teams own different services, can use different tech stacks. (4) Fault isolation — a bug in one service doesn't crash the entire application. (5) Technology diversity — each service can use the best tool for its job.</details>

113. What are the downsides and operational challenges of a microservices architecture?

<details><summary>Answer</summary>(1) Network latency — function calls become network calls. (2) Data consistency — no shared database means no easy transactions across services. (3) Operational complexity — monitoring, logging, and debugging across dozens of services. (4) Deployment complexity — CI/CD pipelines for each service. (5) Testing — integration testing across services is harder. (6) Service discovery and communication overhead.</details>

114. When should you NOT use microservices?

<details><summary>Answer</summary>(1) Small teams / early-stage startups — the overhead outweighs the benefits. (2) Simple applications with few features. (3) When the team lacks experience with distributed systems and DevOps. (4) When the domain boundaries are unclear — splitting too early leads to wrong service boundaries and expensive refactoring. Start monolithic, split when pain points emerge.</details>

115. How do you handle data consistency across microservices when there is no shared database?

<details><summary>Answer</summary>(1) Saga pattern — a sequence of local transactions where each service publishes events that trigger the next step; compensating transactions handle failures. (2) Event-driven architecture — services emit events; other services consume and update their local state. (3) Eventual consistency — accept that data won't be perfectly in sync at all times. (4) Two-phase commit (rarely used due to performance overhead).</details>

### Message Queues

116. What is a message queue, and how does it decouple services?

<details><summary>Answer</summary>A message queue is an intermediary that stores messages produced by one service until another service consumes them. Decoupling: the producer doesn't need to know about the consumer (or if it's even running). Services communicate through the queue, not directly. If a consumer is down, messages wait in the queue and are processed when it recovers.</details>

117. How does a message queue help handle traffic spikes?

<details><summary>Answer</summary>During a traffic spike, the producer (e.g., order service) can generate messages faster than consumers can process them. The queue absorbs this burst, buffering messages. Consumers process at their own pace without being overwhelmed or dropping requests. This smooths out load and prevents cascading failures during peak traffic.</details>

118. Compare Kafka, RabbitMQ, and SQS. When would you choose each?

<details><summary>Answer</summary>Kafka — high-throughput event streaming, message replay, log-based retention. Best for analytics, event sourcing, real-time data pipelines. RabbitMQ — traditional message broker, supports complex routing (exchanges, bindings), message acknowledgment. Best for task distribution, RPC patterns. SQS — fully managed AWS service, zero ops, auto-scaling. Best when you're on AWS and want simplicity without managing infrastructure.</details>

119. What happens to messages in the queue if a consumer service goes down?

<details><summary>Answer</summary>Messages persist in the queue until a consumer processes and acknowledges them. When the consumer comes back online, it picks up where it left off. Most queues support visibility timeouts — if a consumer picks up a message but crashes before acknowledging it, the message becomes visible again for another consumer to process. This ensures no messages are lost.</details>

120. Design a flow where an order placement triggers email, inventory update, and analytics — using a message queue.

<details><summary>Answer</summary>Order Service places an "OrderCreated" event on the queue. Three independent consumers subscribe: (1) Email Service reads the event and sends confirmation email. (2) Inventory Service reads it and decrements stock. (3) Analytics Service reads it and logs the event. Each consumer processes independently and at its own pace. If email service is down, it catches up later — order processing isn't blocked.</details>

### Rate Limiting

121. What is rate limiting, and why is it necessary for both public and internal APIs?

<details><summary>Answer</summary>Rate limiting controls how many requests a client can make within a time window. For public APIs: prevents abuse, DDoS, and ensures fair usage. For internal APIs: prevents one service from overwhelming another (noisy neighbor problem), protects expensive operations (like DB queries), and ensures system stability during traffic spikes.</details>

122. Explain the Token Bucket algorithm for rate limiting.

<details><summary>Answer</summary>A bucket holds tokens, refilled at a constant rate (e.g., 10 tokens/second). Each request costs one token. If tokens are available, the request is allowed and a token is consumed. If the bucket is empty, the request is rejected (429 Too Many Requests). The bucket has a maximum capacity, allowing short bursts up to that limit. Simple, memory-efficient, and widely used.</details>

123. How does a Sliding Window algorithm differ from a Fixed Window algorithm?

<details><summary>Answer</summary>Fixed Window: counts requests in discrete intervals (e.g., 12:00-12:01). Problem: a burst at the boundary (100 requests at 12:00:59 + 100 at 12:01:00) allows 200 requests in 2 seconds. Sliding Window: tracks requests in a rolling time window relative to the current time. Smoother rate enforcement, but slightly more memory-intensive as it must track individual request timestamps.</details>

124. Where in the system architecture should the rate limiter sit?

<details><summary>Answer</summary>Typically at the API Gateway level — it's the single entry point for all requests, making it the most effective place. It can also be implemented as middleware in the application layer. The rate limiter usually uses a fast store like Redis to track request counts per client, as it needs sub-millisecond lookups on every request.</details>

125. How would you implement different rate limits for free-tier vs paid-tier users?

<details><summary>Answer</summary>The rate limiter checks the API key or user token to determine the tier. Each tier has a different rate limit configuration (e.g., free: 100 req/min, paid: 10,000 req/min). Store tier-to-limit mappings in configuration. The rate limiter looks up the user's tier, then applies the corresponding token bucket or sliding window limit from Redis.</details>

### API Gateway

126. What is an API gateway, and what problems does it solve?

<details><summary>Answer</summary>An API gateway is a single entry point for all client requests to a microservices backend. It solves: (1) clients needing to know addresses of many services, (2) duplicating cross-cutting concerns (auth, rate limiting, logging) across every service, (3) protocol translation (clients use REST, internal services use gRPC), and (4) response aggregation from multiple services.</details>

127. What cross-cutting concerns does an API gateway handle?

<details><summary>Answer</summary>(1) Authentication and authorization. (2) Rate limiting. (3) Request/response logging. (4) SSL termination. (5) Request routing to the correct microservice. (6) Load balancing. (7) Caching. (8) Request/response transformation. (9) Circuit breaking (stopping calls to failing services). (10) CORS handling. This centralizes concerns that would otherwise be duplicated in every service.</details>

128. How does an API gateway simplify the client's interaction with a microservices backend?

<details><summary>Answer</summary>Without a gateway, the client must know the URLs of 20+ services, handle authentication with each, and make multiple calls to compose a single page. With a gateway, the client talks to one URL. The gateway routes requests, handles auth once, and can aggregate responses from multiple services into a single response — making the client code dramatically simpler.</details>

129. What is response aggregation, and when is it useful in an API gateway?

<details><summary>Answer</summary>Response aggregation means the gateway calls multiple backend services, combines their responses, and returns a single unified response to the client. Useful when a single page needs data from several services (e.g., user profile from User Service + recent orders from Order Service + recommendations from Recommendation Service). Reduces client-side complexity and round trips.</details>

130. Compare Kong, AWS API Gateway, and Nginx as API gateway solutions.

<details><summary>Answer</summary>Kong — open-source, plugin-based, highly extensible, supports gRPC and WebSockets. Good for complex, multi-cloud setups. AWS API Gateway — fully managed, tight integration with Lambda and AWS services, auto-scaling, pay-per-request pricing. Good for serverless architectures on AWS. Nginx — lightweight, high-performance reverse proxy that can function as a gateway, extensive community, good for on-premise or custom setups.</details>

---

## Group 7: Java Concurrency Internals

### Thread Leak and Proper Thread Pool Shutdown in Java

**What is a Thread Leak?**

A thread leak occurs when threads are created but never properly terminated, causing them to accumulate in the JVM over time. Each thread consumes memory (stack space, ~512 KB–1 MB by default) and OS-level resources. If enough threads accumulate, the application runs out of memory or the OS refuses to create new threads, resulting in `OutOfMemoryError: unable to create new native thread`.

Thread leaks are particularly common when developers manually create threads with `new Thread(() -> { ... }).start()` inside loops, request handlers, or service methods — without any mechanism to track or stop them.

**Common Causes of Thread Leaks**

- Creating raw threads with `new Thread(...)` inside business logic instead of using a managed `ExecutorService`.
- Submitting tasks to an `ExecutorService` that is never shut down (threads stay alive forever waiting for new tasks).
- Using `Executors.newCachedThreadPool()` under high load — it creates an unbounded number of threads with no cap.
- Blocking threads stuck in infinite loops, waiting on a lock, or waiting on `queue.take()` with no interruption logic.
- Not calling `shutdown()` or `shutdownNow()` on `ExecutorService` instances when they are no longer needed.

**How ExecutorService Shutdown Works**

Java's `ExecutorService` manages a pool of worker threads internally. When you submit tasks, threads from the pool pick them up. Even after all tasks are done, the threads remain alive and idle — waiting for future tasks. This is by design, but it means you must explicitly tell the pool to stop.

There are two methods for this:

- `executor.shutdown()` — signals the pool to stop accepting new tasks. Already-submitted tasks complete normally. Threads terminate gracefully once all pending work is done.
- `executor.shutdownNow()` — attempts to stop all actively executing tasks immediately by interrupting them, and returns a list of tasks that were waiting but never started. Tasks must respond to interrupts (`Thread.interrupted()`) for this to work.

The recommended shutdown pattern is:

```java
executor.shutdown(); // No new tasks
try {
    if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
        executor.shutdownNow(); // Force stop if not done in 60s
        if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
            System.err.println("Executor did not terminate");
        }
    }
} catch (InterruptedException e) {
    executor.shutdownNow();
    Thread.currentThread().interrupt(); // Restore interrupt status
}
```

**What Happens If You Don't Shut Down Properly?**

If `shutdown()` is never called on an `ExecutorService`:

1. **Threads stay alive forever.** Worker threads keep running in the background waiting for new tasks. They are non-daemon threads by default, which means the JVM itself will not exit until every one of them terminates. Your application process will hang at exit, never fully stopping.

2. **Memory is never released.** Each idle thread holds its stack memory. If your application creates a new `ExecutorService` per request (a common mistake), you accumulate thousands of idle thread pools, each with live threads, rapidly consuming all available heap and native memory.

3. **`OutOfMemoryError` under load.** In a web application that creates unmanaged threads per request, a sustained traffic spike will spawn hundreds of threads. Since none are cleaned up, the application crashes with `OutOfMemoryError: unable to create new native thread`.

4. **Hidden during testing.** Thread leaks are silent in short-lived tests or development with low traffic. They only surface under sustained production load — making them difficult to diagnose without profiling tools like VisualVM, Java Flight Recorder, or thread dump analysis.

5. **Application hangs on shutdown.** Because non-daemon threads block JVM exit, the application container (e.g., Tomcat, Spring Boot) appears to hang during restart or deployment, requiring a forced kill.

**How to Prevent Thread Leaks in Java**

- **Always use `ExecutorService` instead of raw threads.** Never call `new Thread(...).start()` in business logic.
- **Declare `ExecutorService` as a singleton or scoped bean**, not as a local variable inside a method. In Spring, use `@Bean` with `@PreDestroy` shutdown hooks.
- **Always call `shutdown()` in a `finally` block or lifecycle hook.** Use the two-phase shutdown pattern shown above.
- **Use `try-with-resources`** when using `ExecutorService` in Java 19+ (it implements `AutoCloseable` via `ExecutorService.close()`), which calls `shutdown()` and `awaitTermination()` automatically.
- **Prefer bounded thread pools** (`Executors.newFixedThreadPool(n)`) over unbounded ones (`newCachedThreadPool`) when the workload is unpredictable.
- **Set threads as daemon threads** for background monitoring tasks that should not prevent JVM shutdown:
  ```java
  ThreadFactory daemonFactory = r -> {
      Thread t = new Thread(r);
      t.setDaemon(true);
      return t;
  };
  ExecutorService executor = Executors.newFixedThreadPool(4, daemonFactory);
  ```
- **Monitor thread counts in production** using metrics (e.g., Micrometer + Prometheus) to alert when thread count grows anomalously.
