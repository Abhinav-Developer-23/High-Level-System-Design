# Consistent Hashing Question Bank

## Beginner Level
1. What problem in distributed systems does consistent hashing solve?
2. Why does the formula `Hash(key) mod N` become inefficient when `N` changes?
3. What is a hash ring in consistent hashing?
4. Why is the hash space in consistent hashing circular?
5. How are servers mapped onto a hash ring?
6. How are keys mapped onto a hash ring?
7. How is the target server selected after hashing a key?
8. What happens when a key’s hash value exactly matches a node’s position?
9. What is meant by “clockwise lookup” in consistent hashing?
10. How does consistent hashing minimize key remapping compared to modulo-based hashing?
11. What does the expression `k/n` represent in consistent hashing?
12. Why is consistent hashing considered suitable for elastic systems?

## Intermediate Level
13. What happens to key assignments when a new server is added to a hash ring?
14. Which subset of keys is remapped when a node is inserted between two existing nodes?
15. What happens to key assignments when a server is removed from the ring?
16. Why does removing one node in consistent hashing affect fewer keys than removing one node in modulo hashing?
17. How does consistent hashing help preserve cache locality?
18. How does consistent hashing reduce session disruption in stateful applications?
19. What are virtual nodes (vnodes) in consistent hashing?
20. Why can single-position-per-server consistent hashing lead to uneven load distribution?
21. How do virtual nodes improve load balancing?
22. How do virtual nodes improve failure handling when one physical node goes down?
23. How does increasing the number of virtual nodes per server affect distribution smoothness?
24. What trade-offs arise when using a very high number of virtual nodes?
25. How do you choose the number of replicas (virtual nodes) per physical server?
26. Why is a sorted data structure useful for implementing consistent hashing?
27. What is the role of wrap-around behavior in server lookup?
28. Why is a deterministic hash function required in consistent hashing?
29. What properties should a hash function have for production-grade consistent hashing?
30. How does consistent hashing behave when the hash ring is empty?

## Code and Implementation Level
31. Why is `TreeMap` (or any balanced sorted map) a good fit for implementing a hash ring?
32. What is the time complexity of key lookup with a balanced tree-backed ring?
33. What is the time complexity of adding a node with `R` virtual nodes?
34. What is the time complexity of removing a node with `R` virtual nodes?
35. How do hash collisions between virtual nodes affect the ring?
36. What strategies can be used to handle hash collisions in a consistent hash implementation?
37. Why might you hash `serverId + "-" + replicaIndex` for virtual node placement?
38. What are potential risks of using only a partial digest (e.g., first 32 bits of MD5)?
39. How would you test that key distribution is approximately balanced?
40. How would you test that only a small fraction of keys move after adding one node?
41. How would you test correctness of wrap-around lookup at ring boundaries?
42. What metrics would you track in production to evaluate consistent hashing quality?
43. How would you detect and mitigate hotspots in a consistent hashing system?
44. How would you safely rebalance data after membership changes?
45. How would you implement node draining using consistent hashing during planned maintenance?
46. How does concurrent ring update handling impact request routing consistency?
47. How would you design a thread-safe consistent hashing class?
48. What failure modes can occur if different clients use inconsistent membership views?
49. How can gossip or consensus-based membership help consistent hashing correctness?
50. How would you version and roll out ring changes across a large fleet?

## Advanced and System Design Level
51. How does consistent hashing compare to rendezvous (highest-random-weight) hashing?
52. In what scenarios might rendezvous hashing be preferred over consistent hashing?
53. How does consistent hashing interact with replication factor in distributed databases?
54. How are preference lists built on top of a consistent hash ring in systems like Dynamo-style stores?
55. How can hinted handoff complement consistent hashing during temporary node failures?
56. How do read-repair and anti-entropy relate to ring-based partitioning?
57. How does token ownership affect storage skew in ring-based databases?
58. How can heterogeneous nodes (different capacities) be modeled in consistent hashing?
59. What is weighted consistent hashing, and when should it be used?
60. How can virtual node counts be adjusted to represent node capacity differences?
61. How does consistent hashing influence cross-zone or cross-region traffic patterns?
62. How would you design rack-aware or AZ-aware placement using consistent hashing?
63. How does consistent hashing impact tail latency under bursty workloads?
64. What are the security considerations when keys are user-controlled inputs to hashing?
65. How can adversarial key distributions create denial-of-service hotspots?
66. What safeguards can be added to avoid predictable placement abuse?
67. How would you perform capacity planning for a ring-based cluster under growth?
68. What migration strategy would you use when changing hash function in production?
69. How would you simulate ring stability under repeated churn events?
70. What are common operational pitfalls when running consistent hashing at scale?

## Scenario-Based Questions
71. If a cluster grows from 5 to 6 nodes, how would key movement differ between modulo hashing and consistent hashing?
72. A node fails during peak traffic; how would consistent hashing affect request routing immediately after failure?
73. Your cache hit rate drops after adding nodes—what consistent hashing checks would you perform first?
74. Two services claim different owners for the same key—what debugging steps would you take?
75. Load is uneven despite virtual nodes—what root causes would you investigate?
76. A new node receives too little traffic after joining—what configuration or implementation issues might explain this?
77. After node removal, one neighbor is overloaded—how could virtual nodes or weights help?
78. How would you design a canary rollout for adding 100 new nodes to a ring-based system?
79. What would be your rollback plan if a ring update causes widespread cache misses?
80. How would you explain consistent hashing trade-offs to a non-technical stakeholder?

## Interview-Focused Questions
81. Can you explain consistent hashing in one minute using a real-world analogy?
82. Why does consistent hashing reduce remapping from “most keys” to “a small fraction”?
83. How do virtual nodes improve both balance and resilience?
84. What data structures would you use to implement consistent hashing and why?
85. How do you handle edge cases like an empty ring or single-node ring?
86. How would you evaluate whether your implementation is production-ready?
87. What are the key differences between partitioning, replication, and consistent hashing?
88. How would you reason about consistency and availability during node churn in a ring-based system?
89. What operational dashboards would you build for a consistent hashing cluster?
90. What follow-up improvements would you propose after a first working implementation?