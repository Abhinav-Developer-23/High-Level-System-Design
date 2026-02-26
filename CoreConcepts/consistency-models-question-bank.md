# Consistency Models Question Bank

## Beginner Level
1. What is a consistency model in distributed systems?

<details><summary>Answer</summary>A consistency model is a formal contract that defines what values read operations are allowed to return, given a history of writes across replicas. It tells developers what visibility guarantees they can depend on when data is distributed across multiple nodes.</details>

2. Why is consistency easy on a single machine but hard in distributed systems?

<details><summary>Answer</summary>On a single machine, there is one copy of data, so every read can naturally see the latest write. In distributed systems, data is replicated across nodes, and network delay, partitions, clock skew, and node failures can cause replicas to diverge temporarily.</details>

3. What is the replication problem?

<details><summary>Answer</summary>The replication problem is that updates do not reach all replicas at the same time. A write may be visible on one node while another node still serves stale data, creating inconsistent read results across clients.</details>

4. What are the common trade-offs when choosing stronger consistency?

<details><summary>Answer</summary>Stronger consistency typically increases latency (more coordination), can reduce availability during partitions (must reject some operations), and can lower throughput (more serialization and synchronization).</details>

5. What are the benefits of weaker consistency models?

<details><summary>Answer</summary>Weaker models can provide lower read latency, higher availability (serve requests from more replicas), and better throughput because fewer operations require synchronous coordination.</details>

6. Why is consistency considered a spectrum instead of a binary choice?

<details><summary>Answer</summary>Because systems can provide different levels of guarantees—from eventual convergence to strict real-time ordering. Each level changes what anomalies are possible and what performance/availability costs are paid.</details>

7. Name two strong consistency models.

<details><summary>Answer</summary>Linearizability and sequential consistency are classic strong models. Strict serializability is another strong model for transactional systems.</details>

8. Name two weak consistency models.

<details><summary>Answer</summary>Eventual consistency and PRAM (FIFO) consistency are weaker models. Causal consistency is often considered a middle-ground model.</details>

9. What does "single-copy semantics" mean?

<details><summary>Answer</summary>It means the distributed system appears to clients as if there is only one copy of data, even though physically multiple replicas exist.</details>

10. What does it mean when reads are stale?

<details><summary>Answer</summary>A stale read returns an older value than the latest committed write, usually because the serving replica has not yet received recent updates.</details>

## Strong Consistency Models
11. What is linearizability?

<details><summary>Answer</summary>Linearizability is a consistency model where each operation appears to occur atomically at a single instant between invocation and response, and global ordering respects real-time precedence.</details>

12. What real-time guarantee does linearizability provide?

<details><summary>Answer</summary>If operation A completes before operation B starts in wall-clock time, then A must appear before B in the observed history.</details>

13. What is a linearization point?

<details><summary>Answer</summary>A linearization point is the conceptual instant inside an operation’s execution interval where the operation is considered to take effect atomically.</details>

14. Why is linearizability often expensive?

<details><summary>Answer</summary>It requires tight coordination among replicas (often quorum/consensus-based), which adds network round trips and can block progress during failures or partitions.</details>

15. Give three use cases that generally require linearizability.

<details><summary>Answer</summary>Distributed locks, inventory decrement systems (to avoid oversell), and account balance updates in financial workflows.</details>

16. What is sequential consistency?

<details><summary>Answer</summary>Sequential consistency requires that all operations appear in one global sequential order while preserving each process’s program order, but that order does not need to match real-time clocks.</details>

17. How is sequential consistency weaker than linearizability?

<details><summary>Answer</summary>Sequential consistency can reorder operations that are non-overlapping in real time, while linearizability cannot. Linearizability is sequential consistency plus real-time ordering.</details>

18. What is strict serializability?

<details><summary>Answer</summary>Strict serializability is serializability plus real-time ordering. It applies to transactions and ensures the outcome is equivalent to a serial transaction order that respects real time.</details>

19. How is serializability different from strict serializability?

<details><summary>Answer</summary>Serializability only requires equivalence to some serial order; strict serializability additionally requires that this order respects real-time precedence between transactions.</details>

20. Why do financial systems often need strict serializability?

<details><summary>Answer</summary>Because both transactional correctness and real-time ordering matter; stale or reordered transactional effects can cause double spending, overdrafts, or inconsistent ledgers.</details>

## Weak and Middle-Ground Models
21. What is eventual consistency?

<details><summary>Answer</summary>Eventual consistency guarantees that if no new writes occur, all replicas will eventually converge to the same value. It does not guarantee when convergence will happen.</details>

22. What does eventual consistency not guarantee about staleness?

<details><summary>Answer</summary>It provides no strict bound on staleness—reads may be very old depending on propagation delay, partition duration, and conflict resolution behavior.</details>

23. Does eventual consistency define conflict resolution semantics?

<details><summary>Answer</summary>No. It only requires eventual convergence. Systems must choose separate conflict resolution methods like LWW, vector clocks + merge, CRDTs, or app-level logic.</details>

24. What is Last-Write-Wins (LWW)?

<details><summary>Answer</summary>LWW chooses the update with the greatest timestamp (or version) during conflict resolution. It is simple but can discard concurrent writes and lose data.</details>

25. Why are vector clocks useful under eventual consistency?

<details><summary>Answer</summary>Vector clocks capture causality between versions and can detect concurrent updates, enabling smarter merges than timestamp-only approaches.</details>

26. What are CRDTs, and why do they help?

<details><summary>Answer</summary>CRDTs (Conflict-Free Replicated Data Types) are data structures designed so concurrent updates can be merged deterministically without coordination, guaranteeing convergence.</details>

27. Give two good fits for eventual consistency.

<details><summary>Answer</summary>DNS propagation and CDN-cached content are common fits because temporary staleness is acceptable.</details>

28. Give two risky fits for eventual consistency.

<details><summary>Answer</summary>Inventory counts and bank account balances are risky because stale or conflicting reads/writes can cause overselling or incorrect financial outcomes.</details>

29. What is causal consistency?

<details><summary>Answer</summary>Causal consistency guarantees all processes observe causally related operations in the same order, while allowing different orders for concurrent (independent) operations.</details>

30. What creates a causal relationship between operations?

<details><summary>Answer</summary>Program order (same process), read-from dependencies (an operation uses another’s output), and transitivity (if A→B and B→C, then A→C).</details>

31. Why is causal consistency useful for social feeds or comments?

<details><summary>Answer</summary>It preserves cause-and-effect visibility, preventing users from seeing replies/comments before the original post they depend on.</details>

32. What is PRAM (FIFO) consistency?

<details><summary>Answer</summary>PRAM ensures writes from each individual process are seen by everyone in that process’s write order. Writes from different processes may be observed in different relative orders.</details>

33. How is PRAM weaker than causal consistency?

<details><summary>Answer</summary>PRAM preserves only per-process write order and ignores read-from causality across processes. Causal consistency preserves both.</details>

34. Can two observers disagree on order under causal consistency?

<details><summary>Answer</summary>Yes, for concurrent operations with no causal link. They must agree only on the order of causally related operations.</details>

35. What is the main practical value of causal consistency?

<details><summary>Answer</summary>It gives intuitive application behavior (effects follow causes) without paying the full cost of linearizability for all operations.</details>

## Client-Centric Consistency Models
36. What are client-centric consistency models?

<details><summary>Answer</summary>They provide guarantees from a single client/session perspective rather than requiring strong global ordering across all clients.</details>

37. What is Read-Your-Writes (RYW)?

<details><summary>Answer</summary>RYW guarantees that after a client writes a value, its subsequent reads will see that value (or a newer one), preventing self-staleness.</details>

38. Why is RYW important for user experience?

<details><summary>Answer</summary>Without RYW, users can update settings/profile data and immediately see old values, which feels like data loss or failed updates.</details>

39. What are monotonic reads?

<details><summary>Answer</summary>Monotonic reads guarantee that once a client has observed a value, future reads by that same client will not return older values.</details>

40. What user-facing anomaly do monotonic reads prevent?

<details><summary>Answer</summary>They prevent “time travel backward” where items previously visible disappear on refresh due to reads hitting a staler replica.</details>

41. What are monotonic writes?

<details><summary>Answer</summary>Monotonic writes guarantee that writes issued by a client are applied in the same order everywhere they are observed.</details>

42. Why do monotonic writes matter operationally?

<details><summary>Answer</summary>They prevent out-of-order state transitions (e.g., metadata indicating an update happened before the data update itself is visible).</details>

43. What is writes-follow-reads?

<details><summary>Answer</summary>Writes-follow-reads guarantees that if a client reads some state and then writes, the write is ordered after at least the state it observed.</details>

44. Why is writes-follow-reads important for conditional logic?

<details><summary>Answer</summary>Because read-modify-write workflows depend on making decisions from fresh-enough context; without this guarantee, updates may ignore what was read.</details>

45. Can a system be eventually consistent globally but still offer RYW per session?

<details><summary>Answer</summary>Yes. Many systems provide session guarantees (like RYW and monotonic reads) over an eventually consistent replication layer.</details>

## Application and Design Decisions
46. What first question should guide consistency model selection?

<details><summary>Answer</summary>Ask: “What is the business cost of stale or out-of-order reads/writes for this specific data path?”</details>

47. Which model is typical for balances, locks, and inventory?

<details><summary>Answer</summary>Linearizable (or strict-serializable for transactions) consistency is typical because correctness failures are high-impact.</details>

48. Which model is often enough for social media timelines?

<details><summary>Answer</summary>Causal consistency is often a good fit to preserve conversational/contextual ordering while keeping performance reasonable.</details>

49. Which model is often enough for counters like views or likes?

<details><summary>Answer</summary>Eventual consistency is often acceptable because small temporary inaccuracies rarely harm business correctness.</details>

50. Why do real systems use mixed consistency levels?

<details><summary>Answer</summary>Different data domains have different correctness needs. Mixing levels gives strong guarantees where required and better performance where staleness is acceptable.</details>

51. Give an e-commerce example of mixed consistency.

<details><summary>Answer</summary>Use linearizable consistency for inventory/payment, causal consistency for reviews/Q&A order, and eventual consistency for recommendations or view history.</details>

52. What happens if you use strong consistency everywhere?

<details><summary>Answer</summary>You increase latency and operational cost unnecessarily for low-risk data paths, often reducing overall system scalability and availability.</details>

53. What happens if you use weak consistency everywhere?

<details><summary>Answer</summary>You risk correctness bugs in critical flows (overselling, double spending, incorrect lock behavior), damaging trust and business outcomes.</details>

54. How should architects choose “right consistency” in practice?

<details><summary>Answer</summary>Map each use case to required invariants, define tolerated staleness/anomalies, and choose the weakest model that still preserves those invariants.</details>

55. When should you use linearizability?

<details><summary>Answer</summary>Use linearizability when the cost of reading stale or out-of-order data is unacceptable. Classic use cases: distributed locks (must prevent two holders), inventory decrements (cannot oversell), account balances and payment processing (cannot double-spend), and leader election. Any operation where correctness failure causes direct financial, safety, or integrity damage belongs here.</details>

56. When should you use sequential consistency?

<details><summary>Answer</summary>Use sequential consistency when you need all clients to agree on a single global operation order and each process's operations must appear in program order, but you can tolerate the system ignoring wall-clock timing. It fits shared-memory multiprocessor hardware models and some academic distributed storage systems. In practice, full sequential consistency is rare in production distributed databases because linearizability is usually preferred for similar cost.</details>

57. When should you use causal consistency?

<details><summary>Answer</summary>Use causal consistency when cause-and-effect relationships must be visible to all users, but you do not need a strict global total order. Ideal use cases: social media comment threads (replies visible only after the original post), collaborative document editing (an annotation appears only after the text it references), chat applications (messages from a conversation thread arrive in order), and notification systems (a "congratulations" notification arrives only after the triggering event).</details>

58. When should you use eventual consistency?

<details><summary>Answer</summary>Use eventual consistency when temporary staleness is acceptable and you prioritize availability and low latency. Good fits: DNS propagation (minutes of staleness is fine), CDN-cached static content, social media like/view counters (approximate values are acceptable), product recommendations, shopping cart merges (union of items from concurrent sessions), and analytics counters. Avoid it for inventory, balances, locks, or anything where stale reads cause correctness failures.</details>

59. When should you use Read-Your-Writes (RYW) or session consistency?

<details><summary>Answer</summary>Use RYW whenever a user must immediately see the effects of their own actions. It is the minimum acceptable guarantee for most user-facing applications: profile/settings updates, posting content and seeing it in your own feed, password changes, and preference toggles. RYW can be layered on top of an eventually consistent backend using sticky sessions or version tokens without requiring global strong consistency.</details>

60. When should you use monotonic reads?

<details><summary>Answer</summary>Use monotonic reads when data must never appear to "disappear" or regress from the user's perspective. Order history (viewed items must not vanish on refresh), message threads, document version history, and audit logs are good fits. Without monotonic reads, load-balancing across replicas with different replication lag can cause data to appear and vanish, which is deeply confusing to users.</details>

61. When is PRAM (FIFO) consistency sufficient?

<details><summary>Answer</summary>PRAM is sufficient when you only care that a single producer's writes are seen in the order they were issued, but you have no cross-process causal dependencies. It is useful in simple publish-subscribe or log-streaming systems where each producer's stream must be ordered but relative ordering between producers does not matter. It is rarely chosen explicitly in modern systems—causal consistency is usually preferred for the small additional cost.</details>

## Advanced and Interview-Level Questions
62. Is linearizability compositional across objects?

<details><summary>Answer</summary>Linearizability is compositional for independent objects at the operation level, but cross-object invariants usually need transactional mechanisms (e.g., strict serializability) for correctness.</details>

63. Why can wall-clock timestamps be dangerous for ordering writes?

<details><summary>Answer</summary>Clock skew and non-monotonic clocks can misorder concurrent events, making timestamp-based conflict resolution unreliable without additional safeguards.</details>

64. How do quorum reads/writes relate to consistency?

<details><summary>Answer</summary>Quorums can strengthen consistency when read and write quorums overlap (e.g., R + W > N), but exact guarantees depend on replication protocol, failure handling, and conflict rules.</details>

65. Can eventual consistency systems provide strong consistency for a subset of operations?

<details><summary>Answer</summary>Yes. Many systems offer tunable consistency, allowing selected operations to use stronger coordination while keeping others asynchronous.</details>

66. Why is "eventual" not a useful SLA by itself?

<details><summary>Answer</summary>Because it does not bound convergence time. Production systems need concrete staleness objectives (e.g., p99 replication lag) to reason about user impact.</details>

67. What is the key principle for consistency model selection in interviews and real design?

<details><summary>Answer</summary>Do not maximize consistency blindly; optimize for correctness requirements. Choose the weakest model that safely preserves the invariants of each workload.</details>

68. What is the core difference between causal consistency and sequential consistency?

<details><summary>Answer</summary>Sequential consistency requires a single total order of all operations across all processes that everyone agrees on, and each process's operations must appear in program order within that global order. Causal consistency does NOT require a single global total order—it only requires that causally related operations (program order + read-from + transitivity) are seen in the same order by everyone. Concurrent (causally independent) operations can be observed in different orders by different processes. This makes causal consistency strictly weaker than sequential consistency but much cheaper to implement.</details>

69. Give a concrete scenario that illustrates the difference between causal and sequential consistency.

<details><summary>Answer</summary>Suppose Process P1 writes X=1, and Process P2 writes Y=1 (with neither reading the other's write—they are concurrent). Under sequential consistency, all observers must agree on a single global order: either X=1 appears before Y=1 for everyone, or Y=1 before X=1 for everyone. Under causal consistency, Observer A can see X=1 first, while Observer B sees Y=1 first—because these writes have no causal link, no agreement is required. Now if P3 reads X=1 and then writes Z=1, causal consistency guarantees all observers who see Z=1 have also already seen X=1, because Z causally depends on X.</details>

70. Which is stronger: causal consistency or sequential consistency? Why does this matter in practice?

<details><summary>Answer</summary>Sequential consistency is strictly stronger than causal consistency. It imposes a global total order that causal consistency does not. In practice, this difference matters for cost: sequential consistency requires coordinating global ordering across all nodes, incurring higher latency and coordination overhead. Causal consistency can be implemented with vector clocks or dependency tracking without global coordination, making it feasible at large scale. Most social and collaborative applications that feel like they need ordering actually only need causal ordering (replies follow posts), not global sequential ordering, so causal consistency is the more practical choice.</details>

## Use-Case Scenario Questions
71. What consistency model would you use for a bank account balance, and why?

<details><summary>Answer</summary>Linearizable consistency. A bank balance must reflect the absolute latest state at all times. Showing a stale balance can lead to double-spending or overdrafts—both financially and legally unacceptable. Linearizability ensures every read sees the most recent committed write, and all operations appear to happen atomically in real-time order. The higher latency cost is justified because correctness failure is catastrophic.</details>

72. What consistency model would you use for an inventory count (e.g., items left in stock), and why?

<details><summary>Answer</summary>Linearizable consistency. Inventory operations are classic read-modify-write scenarios: read current stock, decrement by 1, write back. If two users concurrently read the last item from stale replicas and both decrement, the system oversells. Linearizability prevents this by ensuring only one operation can observe and modify the count at a time, effectively serializing decrements.</details>

73. What consistency model would you use for a distributed lock, and why?

<details><summary>Answer</summary>Linearizable consistency. A distributed lock's entire purpose is to allow exactly one holder at a time. If two processes read a stale "unlocked" state from different replicas and both believe they have acquired the lock, mutual exclusion is violated—leading to race conditions and data corruption. Linearizability is the minimum requirement; in practice systems like etcd and ZooKeeper are used precisely because they guarantee linearizable reads and compare-and-swap operations.</details>

74. What consistency model would you use for a user profile page, and why?

<details><summary>Answer</summary>Session consistency (Read-Your-Writes + Monotonic Reads). Users should always see their own updates immediately—if they change their display name or profile photo and refresh the page, they must see the new value. However, showing another user a slightly stale profile for a few seconds is acceptable. Session consistency provides this guarantee without the cost of full linearizability, typically implemented by routing a user's reads to the same replica or using version tokens.</details>

75. What consistency model would you use for a social media feed (posts and replies), and why?

<details><summary>Answer</summary>Causal consistency. Replies must appear after the post they are responding to. If Carol sees Bob's reply "Congratulations!" before she sees Alice's original "I got the job!" post, the feed is confusing and broken. Causal consistency guarantees that if you see an effect, you also see its cause. It does not require a global total order over all posts from all users, so it scales better than linearizability while still preserving conversational coherence.</details>

76. What consistency model would you use for comment threads, and why?

<details><summary>Answer</summary>Causal consistency. Comments in a thread form a causal chain: each reply depends on reading the parent comment. Viewers must see parent comments before their replies, otherwise the thread is incoherent. Causal consistency enforces this cause-and-effect ordering without requiring a strict global order for unrelated threads, making it a practical and efficient choice for large-scale comment systems.</details>

77. What consistency model would you use for a like count on a social post, and why?

<details><summary>Answer</summary>Eventual consistency. Like counts are approximate by nature—users are not harmed if the count reads 1,482 instead of the exact 1,485 for a few seconds. The priority is high availability and low latency so every user can like a post quickly without waiting for coordination. Temporary divergence across replicas is acceptable because the count will converge once propagation completes, and no business-critical decision (e.g., financial transaction) depends on its exact real-time value.</details>

78. What consistency model would you use for a view count on a video or article, and why?

<details><summary>Answer</summary>Eventual consistency. View counts are analytics metrics where approximate figures are perfectly acceptable. Showing "1.2M views" vs "1,200,003 views" makes no practical difference to any user. Using eventual consistency allows each replica to increment its local counter independently and merge later, enabling massive write throughput at global scale without coordination overhead.</details>

79. What consistency model would you use for DNS record propagation, and why?

<details><summary>Answer</summary>Eventual consistency. DNS is a globally distributed, hierarchical system where propagation delays of minutes or even hours are explicitly expected and documented (TTL-based caching). Users understand that a newly registered or changed DNS record may not be immediately visible everywhere. The enormous scale of DNS (billions of queries per day) makes strong consistency physically impractical—eventual consistency is the deliberate design choice that makes the system work at internet scale.</details>

80. What consistency model would you use for CDN-cached content, and why?

<details><summary>Answer</summary>Eventual consistency. A CDN serves cached copies of content from edge nodes close to users. By design, cached content may be seconds, minutes, or hours old depending on the cache TTL. Stale content is the explicit trade-off for dramatically lower latency and origin server load reduction. When content is updated, the new version propagates to edge nodes over time—this is eventual consistency in practice. Cache invalidation can be used to accelerate convergence for time-sensitive updates.</details>

81. How is session consistency (Read-Your-Writes + Monotonic Reads) achieved in practice?

<details><summary>Answer</summary>Session consistency is achieved through one of three main mechanisms: (1) Sticky sessions — route all reads and writes from the same user/session to the same replica, so that replica always has the user's latest writes. (2) Version tokens / write tokens — after a write, the server returns a version number or timestamp; subsequent reads include this token, and the replica refuses to serve the read until it has caught up to at least that version. (3) Client-side tracking — the client tracks the highest version it has seen and sends it with each request; any replica that is not yet at that version either waits (read-your-writes) or redirects to a more up-to-date replica.</details>

82. What is the sticky session approach to session consistency, and what are its drawbacks?

<details><summary>Answer</summary>Sticky sessions pin all of a user's requests to the same backend replica using mechanisms like session cookies, IP hashing in a load balancer, or a session routing layer. This trivially guarantees RYW and monotonic reads because the user always talks to the same copy of data. Drawbacks: (1) Poor load balancing — one replica can become a hotspot if a user is very active. (2) No fault tolerance — if that replica goes down, the session must be re-pinned and the user may temporarily see stale data. (3) Horizontal scaling is harder because sessions are coupled to specific nodes.</details>

83. What is the version token (write token) approach to session consistency, and how does it work?

<details><summary>Answer</summary>When a client performs a write, the system returns a write token — typically a logical timestamp, vector clock entry, or monotonically increasing version number representing the state after that write. The client attaches this token to subsequent read requests. The serving replica checks: "Have I applied updates up to at least this version?" If yes, it serves the read normally. If no, it either (a) waits/blocks until replication catches up, (b) forwards the request to a replica that is sufficiently up-to-date, or (c) rejects and retries. This decouples session guarantees from replica affinity, enabling better load balancing. DynamoDB's "consistent read" and session tokens in Cassandra and MongoDB follow this pattern.</details>

84. What is the trade-off between sticky sessions and version tokens for session consistency?

<details><summary>Answer</summary>Sticky sessions are simple to implement (just configure the load balancer) but create uneven load distribution and single points of session failure. Version tokens are more complex (require token generation, propagation, and replica coordination) but allow reads to be served by any sufficiently up-to-date replica, giving better load balancing and fault tolerance. In high-scale systems, version tokens are preferred because they decouple session guarantees from specific nodes. Sticky sessions are often used in smaller or legacy systems where simplicity is prioritized over scalability.</details>

85. How is causal consistency achieved in practice?

<details><summary>Answer</summary>Causal consistency is implemented using causal metadata — typically vector clocks or dependency vectors — that travel with every read and write. The mechanism works in three steps: (1) Tracking: Each write is tagged with a vector clock entry representing its causal dependencies (all writes it has seen before being issued). (2) Propagation: This causal metadata is attached to messages between clients and replicas. When a replica receives a write, it checks that all causally preceding writes are already applied before applying the new one. (3) Blocking on read: When a client reads from a replica, it sends its current causal context. If the replica has not yet received all causally preceding writes, it blocks the read until those writes arrive. This guarantees that effects are not visible before their causes. Systems like MongoDB (causal consistency sessions) and Cassandra (with lightweight transactions) use variants of this approach.</details>

86. What is a vector clock, and how does it enable causal consistency?

<details><summary>Answer</summary>A vector clock is an array of counters, one per node in the system. Each node increments its own counter on every write. When a message is sent (write or read response), the sender attaches its current vector clock. The receiver takes the element-wise maximum of its own clock and the received clock — this is the "merge" step. A write W1 causally precedes W2 if W1's vector clock is strictly less than W2's in every component. Replicas use this ordering to hold back W2 until W1 is applied, enforcing causality. Vector clocks detect concurrent writes (neither clock dominates) and causally ordered writes (one clock dominates), giving the system exactly the information it needs to enforce causal ordering without requiring full global coordination.</details>

87. How is sequential consistency achieved in practice?

<details><summary>Answer</summary>Sequential consistency requires that all operations appear in a single total order consistent with each process's program order. It is typically achieved through: (1) Total Order Broadcast (TOB) / Atomic Broadcast: All writes are sent through a central sequencer or a consensus protocol (e.g., Paxos, Raft) that assigns a global sequence number to each operation. Every replica applies operations in this global sequence order, and reads are served only after the replica has applied all preceding operations. (2) Primary-order replication: A designated primary node serializes all writes and forwards them to replicas in order. Reads must go through the primary or a replica that is fully caught up. (3) Shared log (e.g., Apache Kafka as a replication log): All writes are appended to an ordered log; replicas replay the log in order. Sequential consistency is more expensive than causal consistency because it requires global agreement on the order of ALL operations — even concurrent ones that have no causal relationship.</details>

88. What is Total Order Broadcast (TOB), and why is it key to sequential consistency?

<details><summary>Answer</summary>Total Order Broadcast is a distributed communication primitive that guarantees two properties: (1) Reliability — if one correct node delivers a message, all correct nodes eventually deliver it. (2) Total order — all nodes deliver messages in the same order. TOB is the core building block for sequential consistency because it gives every replica an identical, globally agreed-upon sequence of operations to apply. Once all replicas apply writes in the same total order, reads served from any fully caught-up replica will see an identical history. Consensus algorithms like Raft and Paxos implement TOB internally; this is why consensus-based systems (etcd, ZooKeeper) naturally provide strong ordering guarantees.</details>

89. What is the key implementation difference between causal consistency and sequential consistency?

<details><summary>Answer</summary>Causal consistency only requires agreement on the order of causally related operations. Each node tracks its local causal dependencies using vector clocks and delays only those writes that have missing causal predecessors. Concurrent (causally independent) writes can be applied in any order — no global coordination is needed for them. Sequential consistency requires global agreement on the total order of ALL operations — even concurrent, causally unrelated ones. This demands a consensus protocol or central sequencer that every write must pass through, making it significantly more expensive in terms of latency and coordination overhead. In short: causal consistency = coordinate only when causally necessary; sequential consistency = always coordinate for everything.</details>

90. Can causal consistency be implemented without blocking reads? How?

<details><summary>Answer</summary>Yes, using a technique called optimistic causal consistency or causal+ consistency. Instead of blocking reads when causal dependencies are not yet satisfied, the system can: (1) Return the read immediately with a "causal snapshot" — a consistent view up to the point the client's causal context allows — even if some concurrent writes are not yet visible. (2) Use dependency-aware routing: route reads to a replica that is known to have seen at least the client's causal context, avoiding the need to wait. (3) Use sharded causal consistency (as in systems like COPS and Causal+): replicas propagate writes with their causal dependencies, and reads are served from local replicas as long as the client's causal session is satisfied. This avoids cross-datacenter blocking on reads while still preserving causal ordering.</details>
