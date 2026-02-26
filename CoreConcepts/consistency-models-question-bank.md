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

## Advanced and Interview-Level Questions
55. Is linearizability compositional across objects?

<details><summary>Answer</summary>Linearizability is compositional for independent objects at the operation level, but cross-object invariants usually need transactional mechanisms (e.g., strict serializability) for correctness.</details>

56. Why can wall-clock timestamps be dangerous for ordering writes?

<details><summary>Answer</summary>Clock skew and non-monotonic clocks can misorder concurrent events, making timestamp-based conflict resolution unreliable without additional safeguards.</details>

57. How do quorum reads/writes relate to consistency?

<details><summary>Answer</summary>Quorums can strengthen consistency when read and write quorums overlap (e.g., R + W > N), but exact guarantees depend on replication protocol, failure handling, and conflict rules.</details>

58. Can eventual consistency systems provide strong consistency for a subset of operations?

<details><summary>Answer</summary>Yes. Many systems offer tunable consistency, allowing selected operations to use stronger coordination while keeping others asynchronous.</details>

59. Why is “eventual” not a useful SLA by itself?

<details><summary>Answer</summary>Because it does not bound convergence time. Production systems need concrete staleness objectives (e.g., p99 replication lag) to reason about user impact.</details>

60. What is the key principle for consistency model selection in interviews and real design?

<details><summary>Answer</summary>Do not maximize consistency blindly; optimize for correctness requirements. Choose the weakest model that safely preserves the invariants of each workload.</details>
