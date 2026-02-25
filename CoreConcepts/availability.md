# Availability — Interview Questions

---

## Fundamentals

**Q1. How is availability measured, and what does the formula represent?**

<details>
<summary>Answer</summary>

Availability answers the question: "What fraction of time is my system actually up and reachable by users?"

**Formula:**
```
Availability = Uptime / (Uptime + Downtime)
```

- **Uptime** = total time the system was operational and serving requests correctly
- **Downtime** = total time the system was completely or partially unavailable
- The result is expressed as a **percentage** over a chosen period (year, month, or week)

**Example:**  
A system was down for 1 day in a year:
```
Availability = 364 / 365 = 99.726%
```
That single day of downtime drops you **below three nines (99.9%)**.

**Why the period matters:**  
The same availability percentage means very different things depending on context:
- 99% annually = 3.65 days of downtime — unacceptable for most production systems
- 99% weekly = 1.68 hours of downtime — may be tolerable for a maintenance window

**Important nuance:**  
Availability only measures whether the system is *up*, not whether it is giving *correct* answers. A system that always returns HTTP 200 with garbage data has high availability but low reliability. These are separate concerns.

</details>

---

**Q2. What are the "nines" of availability? Give examples with their annual downtime.**

<details>
<summary>Answer</summary>

The "nines" is shorthand for describing availability percentages. Each additional nine reduces allowed downtime by roughly 10×.

| Nines | Availability | Downtime / Year | Downtime / Month | Downtime / Week |
|-------|-------------|-----------------|-----------------|-----------------|
| Two nines | 99% | 3.65 days | 7.3 hours | 1.68 hours |
| Three nines | 99.9% | 8.76 hours | 43.8 minutes | 10.1 minutes |
| Four nines | 99.99% | 52.6 minutes | 4.38 minutes | 1.01 minutes |
| Five nines | 99.999% | 5.26 minutes | 26.3 seconds | 6.05 seconds |
| Six nines | 99.9999% | 31.5 seconds | 2.63 seconds | 0.6 seconds |

**Real-world benchmarks:**
- **Three nines (99.9%):** Most basic production SLAs. A single deployment gone wrong can consume your whole budget.
- **Four nines (99.99%):** Common target for serious web applications. Requires automation, redundancy, and fast automated failover. ~52 minutes of downtime budget per year.
- **Five nines (99.999%):** Telecom-grade. Extremely difficult to achieve. Requires no single human-dependent recovery steps — everything must be automated.
- **Six nines:** Typically only seen in specialized financial or safety-critical systems.

**Key insight:** Going from three nines to four nines is not just a 0.09% improvement — it is an *order of magnitude* reduction in allowed downtime. This jump usually requires fundamentally different architecture decisions.

</details>

---

**Q3. What is the difference between availability and reliability?**

<details>
<summary>Answer</summary>

These two terms are often confused but describe completely different system properties.

| Property | Question It Answers | Definition |
|---|---|---|
| **Availability** | Is the system up? | The system is accessible and operational |
| **Reliability** | Does the system work correctly? | The system produces correct results consistently |

**A system can be:**

- **High availability, high reliability** — The ideal. Always up and always correct. (e.g., a well-engineered banking system)
- **High availability, low reliability** — Always reachable, but sometimes returns wrong data. (e.g., a buggy service that never crashes but silently corrupts records)
- **Low availability, high reliability** — Goes down for maintenance or crashes often, but when it is up, it always gives correct results. (e.g., a poorly operated but well-written batch system)
- **Low availability, low reliability** — Worst case. Crashes frequently and gives wrong answers when running.

**Example to make it concrete:**  
Imagine a bank's fund transfer service is always responding (high availability), but due to a race condition it occasionally debits the sender without crediting the receiver. This is a **reliability** failure, not an availability failure. The system is up — it is just wrong.

**Why this distinction matters in interviews:**  
When designing a system, you need to explicitly address both. Just adding redundant servers fixes availability. Fixing data correctness requires consensus protocols, distributed transactions, idempotency keys, and other reliability patterns.

</details>

---

## Series vs Parallel

**Q4. How does combining components in series affect overall availability? Give an example.**

<details>
<summary>Answer</summary>

When components are **in series**, the entire chain must be working for the system to function. Think of it like a pipeline — if any stage breaks, the whole flow stops.

**Formula:**
```
A_total = A1 × A2 × A3 × ... × An
```

Because each availability is a number less than 1.0, multiplying them together always gives a **smaller** result. The more components you add in series, the lower the overall availability.

**Example:**

A typical web request travels through:
1. Load Balancer: 99.9% available
2. Application Server: 99.9% available
3. Database: 99.9% available

```
Overall = 0.999 × 0.999 × 0.999 = 0.997 = 99.7%
```

You started with three components each at "three nines" but the combined system has dropped to below three nines.

**Scaling the problem:**  
In a microservices architecture with 10 services in a request chain, each at 99.9%:
```
0.999^10 = 0.99 = 99%
```
Ten "three nines" services in series gives you only *two nines* end-to-end availability.

**Implications:**
- Every new service you add to a synchronous call chain degrades overall availability
- This is why microservice architectures need aggressive timeouts, circuit breakers, and async communication for non-critical paths
- Prefer asynchronous processing (queues) where possible to break series dependencies

</details>

---

**Q5. How does combining components in parallel affect availability? Why is it so much better?**

<details>
<summary>Answer</summary>

When components are **in parallel**, the system only fails when *all* components fail simultaneously. Any single working component can serve the request.

**Formula:**  
Since failure probabilities multiply:
```
P(all fail) = (1 - A1) × (1 - A2) × ... × (1 - An)
Availability = 1 - P(all fail)
```

**Example:**  
Two servers, each with 99.9% availability (0.1% failure rate):
```
P(both fail) = 0.001 × 0.001 = 0.000001 = 0.0001%
Availability = 1 - 0.000001 = 99.9999%
```

Two "three nines" servers running in parallel give you **six nines** availability — an improvement of 1000×.

**Why this is so powerful:**
- Each server independently fails with probability 0.1%
- For the system to go down, two independent low-probability events must happen at exactly the same time
- Adding a third parallel server makes it essentially impossible for all three to fail together

**Important assumption:**  
This math assumes **independent failures**. If all your servers are in the same rack, powered by the same PDU, sharing the same switch — their failures are *correlated*, not independent. The math breaks down. True parallel availability requires:
- Different power circuits
- Different network paths
- Different physical racks or data centers (ideally different AZs)

**The takeaway:**  
Parallelism is the single most powerful tool for improving availability. This is why load balancers, read replicas, multi-AZ deployments, and redundant services exist. Every major reliability pattern is essentially a way to structure components in parallel rather than in series.

</details>

---

## Failure Modes

**Q6. What are the main categories of failure modes in distributed systems?**

<details>
<summary>Answer</summary>

Understanding how failures happen is the first step to designing against them. There are four major categories:

**1. Hardware Failures**
Physical components have a finite lifespan and fail randomly.

| Component | Typical Failure Rate | MTBF |
|---|---|---|
| Hard Drive (HDD) | 2–4% per year | ~300,000 hours |
| SSD | 0.5–1% per year | 1–2 million hours |
| Server | 2–4% per year | ~300,000 hours |
| Network Switch | 1–2% per year | ~500,000 hours |
| Power Supply | 1–3% per year | ~400,000 hours |

**At scale, hardware failures are routine, not exceptional.** A data center with 10,000 servers expects hundreds of hardware failures per year. Your architecture must tolerate a server dying at any arbitrary moment.

**2. Software Failures**
Hardware fails randomly. Software fails "creatively."
- **Bugs:** Logic errors causing crashes or incorrect behavior
- **Memory leaks:** Gradual resource exhaustion over hours or days
- **Deadlocks:** Two processes blocking each other indefinitely, starving the system
- **Resource exhaustion:** Thread pool, connection pool, or file descriptor limits hit
- **Cascading failures:** A slow downstream service causes upstream services to queue up requests until they OOM or time out

**3. Network Failures**
Networks fail in subtle, intermittent, and hard-to-diagnose ways:
- **Packet loss:** Requests silently discarded — partial data, timed-out operations
- **Latency spikes:** A 50ms service suddenly takes 5 seconds under load
- **Network partition:** A subset of servers can no longer reach another subset — they are all alive but cannot communicate
- **BGP route flaps:** Internet routing tables transiently advertise incorrect paths
- **DNS failures:** Name resolution stops working — services cannot find each other even if they are all running

**4. Human Errors** *(most important)*
Studies consistently attribute **70–80% of production outages** to human mistakes, not hardware or software:
- Deploying misconfigured environment variables (e.g., pointing prod at staging DB)
- Running a migration that locks tables for longer than expected
- `rm -rf` in the wrong directory or on the wrong server
- Underestimating traffic for a product launch — insufficient capacity planned

**Key insight:** You cannot eliminate human error. You design systems so that mistakes are hard to make, quick to detect, and easy to recover from.

</details>

---

**Q7. Why are human errors considered the leading cause of outages? What mitigations help?**

<details>
<summary>Answer</summary>

**Why humans cause most outages:**

- Systems are increasingly complex — it is impossible for any single person to understand all the interactions and edge cases
- Pressure to ship fast creates shortcuts in testing and review
- Operations work (deployments, config changes) often happens under stress or urgency
- Environment differences (dev vs staging vs prod) mean things that worked locally fail in production
- Fatigue and inattention during on-call rotations lead to wrong commands

**Common failure scenarios:**
- **Configuration mistakes:** Wrong database connection string pushed to production; feature flag enabled in prod by mistake
- **Failed deployments:** New version has a subtle bug triggered only under production load or data patterns
- **Accidental deletions:** `DROP TABLE` without a `WHERE` clause, or executed against prod instead of dev
- **Capacity errors:** Engineering team announces a product launch but infrastructure team is not looped in — servers fall over under unexpected load

**Mitigations — organized by prevention vs. recovery:**

*Prevention:*
- **Automation:** Reduce the number of manual steps. Automate deployments, config management (Ansible, Terraform), and database migrations
- **Code review for infrastructure changes:** Treat config files and IaC as code — require PRs and peer review
- **Canary deployments:** Roll out changes to 1–5% of traffic first; monitor error rates before promoting to 100%
- **Feature flags:** Decouple deployment from release. Code goes out with the feature disabled; a config change enables it
- **Production access controls:** Require explicit approval + audit logs for any direct production database access
- **Read-only prod access by default:** Engineers can query but cannot mutate production without an explicit elevated role

*Recovery:*
- **Runbooks:** Step-by-step documented recovery procedures for known failure modes so on-call engineers don't improvise under pressure
- **Automated rollback:** If error rate spikes after deployment, automatically revert to the previous version
- **Point-in-time recovery (PITR) for databases:** Allows reverting a database to any second in the past, recovering from accidental deletes
- **Blue-green deployments:** Keep the old version running until the new one is confirmed healthy — instant rollback by switching traffic back

</details>

---

**Q8. What is a cascading failure and how can you prevent it?**

<details>
<summary>Answer</summary>

**What it is:**

A cascading failure is a chain reaction where one component's failure causes overload or failure in dependent components, which in turn causes further failures, until the entire system collapses — even though the initial failure was small.

**Classic example:**
1. Database becomes slow due to a long-running query
2. Application servers make DB calls that no longer complete quickly
3. Requests pile up; application server thread pools fill up
4. Application servers stop accepting new connections — they appear down to the load balancer
5. Load balancer retries requests to remaining app servers, doubling their load
6. Remaining app servers also become overwhelmed and fall over
7. The entire system is now down because of one slow database query

**Prevention strategies:**

**1. Circuit Breaker Pattern**
- Stop calling a failing dependency once the failure rate exceeds a threshold
- Fail fast with an error instead of waiting for timeouts
- Give the dependency time to recover before trying again
- Prevents thread pool exhaustion from piling up on a slow service

**2. Timeouts on every downstream call**
- Never make a network call without a timeout
- A service that hangs indefinitely will exhaust caller thread pools
- Set timeouts based on what the client can reasonably wait — not on what the server "usually" takes

**3. Retry with exponential back-off and jitter**
- Blind retries can amplify load on a struggling service ("retry storm")
- Exponential back-off: wait 1s, then 2s, then 4s, then 8s between retries
- Jitter: add randomness so all clients don't retry at the same moment

**4. Bulkheads (failure isolation)**
- Named after watertight compartments in ships
- Dedicate separate thread pools or connection pools to different downstream services
- A failure in one dependency cannot exhaust resources needed by other dependencies
- Example: payment service uses one thread pool, recommendations service uses another — a slow recommendations call cannot starve payment processing

**5. Queue-based buffering**
- Put a queue between producers and consumers
- Spikes in traffic are absorbed by the queue rather than hammering the database directly
- Workers process at a sustainable rate even if the queue grows temporarily

**6. Load shedding**
- When a service is overloaded, deliberately reject the least-important requests
- Return HTTP 429 (Too Many Requests) to low-priority clients
- Protect capacity for critical operations (e.g., payments) over non-critical ones (e.g., analytics)

</details>

---

## Redundancy

**Q9. What is active-passive redundancy? What are its pros and cons?**

<details>
<summary>Answer</summary>

**What it is:**

In active-passive mode, one component (the **primary**) handles all production traffic while a second component (the **standby**) sits idle, waiting to take over if the primary fails. The standby keeps itself synchronized with the primary but does not serve any real traffic under normal conditions.

**How failover works:**
1. A monitoring process (health check, heartbeat) detects that the primary has failed
2. The standby is promoted to become the new primary
3. Routing (DNS, VIP, load balancer config) is updated to send traffic to the new primary
4. The old primary is taken offline or demoted to standby once it recovers

**When to use it:**
- Databases where you need a single authoritative source of truth for writes
- Stateful services where data consistency is paramount
- Systems using single-leader replication (Postgres with Patroni, MySQL with Orchestrator)

**Pros:**
- Simple to understand and reason about — at any moment, there is exactly one leader
- Standby consumes fewer resources since it is not serving traffic
- Clear source of truth: all writes go to the primary, no ambiguity about which copy is authoritative
- Data consistency is easier to guarantee

**Cons:**
- **Failover takes time:** the monitoring system must first detect the failure (usually 10–30 seconds), then promote the standby, then update routing. During this window, the system is unavailable.
- **Standby is untested under real load:** since the standby never serves production traffic, you can never be sure it will behave correctly when promoted. It may have hidden configuration issues.
- **Split-brain risk:** if the network partitions and the monitoring system loses contact with the primary, it may promote the standby while the primary is still running and accepting writes — now you have two primaries simultaneously accepting different writes, which leads to data corruption.
- **Wasted capacity:** the standby server is paid for but does no useful work in steady state (unless used for read replicas or backups)

</details>

---

**Q10. Explain the three standby types in active-passive: cold, warm, hot.**

<details>
<summary>Answer</summary>

The standby server can be kept in different states of readiness. The trade-off is always cost vs. failover speed.

**Cold Standby**

| Attribute | Detail |
|---|---|
| State | Powered off or archived (e.g., AMI snapshot, VM image) |
| Failover time | 5–15+ minutes |
| Cost | Lowest — you pay only for storage, not running compute |

- Must boot the machine, start services, potentially restore from backup or replay WAL logs
- Acceptable for **disaster recovery** where hours of downtime per year are tolerable
- Not suitable for production SLAs requiring sub-minute failover

**Warm Standby**

| Attribute | Detail |
|---|---|
| State | Running, configured, receiving replicated data — but not in the load balancer |
| Failover time | Seconds to 2–3 minutes |
| Cost | Medium — you pay for a running server but at reduced capacity |

- Already running the application/database process
- Data replication is happening continuously in the background
- Failover requires: promoting the standby, updating routing (load balancer / DNS TTL)
- The most common choice for production databases — balances cost and recovery speed

**Hot Standby**

| Attribute | Detail |
|---|---|
| State | Fully synchronized, potentially serving read traffic, ready to become primary instantly |
| Failover time | Under 30 seconds (automated), sometimes under 10 seconds |
| Cost | Highest — full-spec server running at all times |

- Uses **synchronous replication**: every write to the primary is confirmed on the hot standby before the write is acknowledged to the client
- If the primary dies, the hot standby has zero data loss (RPO = 0)
- Often used in financial systems where losing a single transaction is unacceptable
- The standby may serve **read-only queries** to make use of its resources

**How to choose:**

| Scenario | Best Choice |
|---|---|
| Disaster recovery, budget-constrained | Cold standby |
| Most production databases | Warm standby |
| Financial systems, zero-data-loss requirement | Hot standby |

</details>

---

**Q11. What is active-active redundancy? When is it preferred over active-passive?**

<details>
<summary>Answer</summary>

**What it is:**

In active-active mode, **all nodes handle live production traffic simultaneously**. There is no standby waiting in reserve — every server is doing real work, all the time.

**How failures are handled:**
- The load balancer continuously health-checks all nodes
- When a node fails, the load balancer simply stops routing traffic to it — immediately, with no failover delay
- The remaining healthy nodes absorb the additional load
- There is no "promotion" or "recovery" step — the other nodes were already handling traffic

**How it works for stateless services:**
Any request can be handled by any node because there is no local state. The load balancer distributes requests using round-robin, least-connections, or consistent hashing. A node dying is a non-event from the system's perspective — the next request goes to the next available node.

**For stateful services:**
Active-active is harder but achievable by:
- Using **shared external storage** (a database or Redis) that all nodes read/write — the state is not on the nodes themselves
- Using **sticky sessions** (same client always routes to same server) — reduces the availability benefit but maintains state
- Using **distributed consensus protocols** (Raft, Paxos) for leader coordination across nodes

**When to prefer active-active over active-passive:**

| Factor | Lean Active-Active | Lean Active-Passive |
|---|---|---|
| Service statefulness | Stateless | Needs single write leader |
| Failover speed requirement | Sub-second | Seconds acceptable |
| Resource efficiency concern | Yes (want to use all servers) | No (standby cost okay) |
| Consistency requirement | Eventual okay | Strong consistency needed |
| Example | HTTP API servers | Primary-replica database |

**Pros:**
- No failover delay — already handling traffic, nothing to promote
- All nodes are continuously battle-tested under real production load — no surprises at failover time
- Better resource utilization — you are getting compute value from every server you are paying for
- Scales horizontally — add more nodes without architectural changes

**Cons:**
- Stateful active-active is significantly more complex to implement correctly
- Requires careful session management or truly stateless application design
- Distributed state management introduces consistency trade-offs (CAP theorem)

</details>

---

**Q12. What is the "split-brain" problem in database redundancy?**

<details>
<summary>Answer</summary>

**What it is:**

Split-brain occurs when a **network partition** isolates nodes in a distributed system from each other, and each isolated group believes it is the only surviving group — and therefore elects or promotes itself as the new leader. The result: you now have **two nodes both acting as the primary**, independently accepting writes.

**How it happens — step by step:**
1. You have a primary database and a standby, connected by a network link
2. The network link breaks (a switch reboots, cable cut, etc.)
3. The standby can no longer "see" the primary, so it assumes the primary is dead
4. The failover monitor promotes the standby to primary
5. Clients are re-routed to the new primary
6. But the original primary is still alive — it just cannot see the standby
7. The original primary is still accepting writes from old clients whose routing hasn't been updated yet
8. **Now both nodes think they are the primary** — both are accepting writes
9. The data on two nodes diverges — you have two conflicting histories with no automatic way to reconcile

**Why this is catastrophic:**
- Lost updates — a write committed on the old primary is not on the new primary
- Data corruption — two different writes to the same record produce an irreconcilable conflict
- Reconciliation is often a manual process that can take hours

**Prevention strategies:**

**1. Quorum-based leader election (Raft, Paxos)**
- A node can only become leader if it has the acknowledgment of a **majority (quorum)** of nodes
- In a 3-node cluster, you need 2 votes to become leader
- If the cluster is split 1+2, only the group of 2 can form a quorum and elect a leader
- The isolated single node cannot become leader because it cannot reach quorum
- This prevents two leaders existing simultaneously because two majorities cannot exist in the same cluster

**2. STONITH — Shoot The Other Node In The Head**
- Before the standby promotes itself, it sends a fencing command to forcibly power off or isolate the old primary
- Uses out-of-band management interfaces (IPMI, AWS EC2 stop-instance API)
- Guarantees the old primary is dead before the new one starts accepting writes
- Brutal but effective — no ambiguity about who is primary

**3. Epoch / generation numbers**
- Every time a new primary is elected, it gets a new, higher epoch number
- All writes and commands are tagged with the epoch of the leader that issued them
- If the old primary (epoch 5) tries to commit a write, but the cluster is now on epoch 6, all nodes reject it
- Stale leaders cannot make progress once they are superseded

**4. Lease-based leadership**
- A leader holds a time-limited "lease" on leadership, issued by a distributed coordination service (ZooKeeper, etcd)
- If the leader cannot renew its lease, it stops accepting writes before its lease expires
- Guarantees that at most one node is acting as leader at any moment

</details>

---

**Q13. What is geographic redundancy and what failure scenarios does it protect against?**

<details>
<summary>Answer</summary>

**What it is:**

Geographic redundancy means running your system across multiple physically separate locations — different buildings, different cities, or different continents. A failure that takes out one location does not affect the others.

**Why a single data center is not enough:**
A data center can fail entirely due to:
- Power grid failure (even with UPS and generators, extended grid outages can exhaust fuel)
- Natural disaster (flood, earthquake, tornado)
- Cooling system failure
- Fiber cut or upstream network provider failure
- Fire
- Even a backhoe accidentally cutting a buried fiber line has taken down large sections of the internet

**Three levels of geographic redundancy:**

**1. Availability Zones (AZs)**
- Separate data centers within the same metropolitan region
- Connected by dedicated, low-latency fiber (1–2ms round trip)
- Independent power, cooling, and physical networking
- Cloud providers (AWS, GCP, Azure) design AZs to be isolated from each other's failure modes
- **What it protects against:** Single data center hardware failure, power outage, connectivity issue
- **Latency impact:** Minimal — synchronous replication is feasible
- **Cost:** Moderate — data transfer between AZs is billed but cheap
- **Best for:** Most production applications. Deploy across 2–3 AZs as a baseline.

**2. Multi-Region**
- Data centers in geographically separate areas (e.g., US-East vs US-West vs Europe)
- Round-trip latency of 50–150ms between regions
- Fully independent infrastructure — a regional outage or natural disaster cannot affect another region
- **What it protects against:** Regional disasters, major network outages, regulatory data residency requirements
- **Latency impact:** Significant — synchronous replication would add 50–100ms to every write. Most multi-region setups use **asynchronous replication**, accepting a small risk of data loss (RPO of seconds to minutes) in a disaster
- **Best for:** Global applications needing low latency for worldwide users, strict disaster recovery requirements (RTO/RPO SLAs), compliance (e.g., data must stay in EU)

**3. Multi-Cloud**
- Running workloads across different cloud providers (e.g., AWS + Google Cloud)
- Protects against an entire cloud provider having an outage (which does happen)
- Highest complexity — different APIs, different networking models, different tooling
- Data egress fees make multi-cloud expensive
- **Best for:** Very large enterprises with strict provider independence requirements; rarely justified for most organizations

**Data replication challenge across regions:**

Because of high latency, most multi-region systems make a deliberate trade-off:
- Use **asynchronous replication** to keep write latency acceptable
- Accept that in a regional failure, the surviving region may be missing the last few seconds of writes (the "replication lag")
- This is measured as **RPO (Recovery Point Objective)** — the maximum acceptable data loss

</details>

---

**Q14. Why is redundancy at every layer critical? What is a single point of failure (SPOF)?**

<details>
<summary>Answer</summary>

**What is a SPOF?**

A Single Point of Failure (SPOF) is any component in your system whose failure alone causes the entire system to become unavailable. It does not matter how redundant everything else is — if one component has no redundancy, it is your weakest link, and it determines your real-world availability ceiling.

**Why every layer matters:**

Imagine a system with redundant app servers but a single database:
- 3 app servers at 99.9% in parallel → 99.9999% app availability
- 1 database at 99.9% → 99.9% database availability
- **Overall availability is 99.9%** — the single database is your SPOF, and all the app server redundancy is irrelevant to your actual uptime

**Common SPOFs to identify and eliminate:**

| Layer | SPOF Example | Solution |
|---|---|---|
| DNS | Single DNS provider | Use multiple DNS providers or anycast DNS |
| Load Balancer | Single HAProxy / Nginx instance | Redundant LBs with virtual IP (keepalived) or managed cloud LB |
| App Servers | Single server | Multiple servers behind a load balancer |
| Database | Single primary DB | Active-passive with hot standby + automatic failover |
| Cache | Single Redis node | Redis Sentinel or Redis Cluster |
| Message Queue | Single Kafka broker | Kafka cluster with replication |
| Storage | Single disk | RAID, distributed storage (S3, GCS), or replicated volumes |
| Region | All infra in one region | Multi-AZ or multi-region deployment |

**The key principle — redundancy gets harder as you go deeper in the stack:**

Adding more web servers is trivial and nearly zero risk. Adding database replicas with automatic failover requires:
- Choosing a replication mode (sync vs async) with real trade-offs
- Solving the split-brain problem
- Configuring and testing automated failover (Patroni for Postgres, Orchestrator for MySQL)
- Ensuring applications can handle a primary switch (connection pooling, reconnect logic)

This is why databases are the most common SPOF in real-world systems despite engineers knowing better.

**How to audit for SPOFs:**
1. Draw the full request flow from user to storage
2. For each component: "If this dies right now, what happens?"
3. Every component with the answer "the whole system goes down" is a SPOF
4. Prioritize eliminating SPOFs that are most likely to fail or would cause the most damage

</details>

---

## High Availability Patterns

**Q15. Describe the Load Balancer + Multiple Backends pattern for HA. How does the load balancer itself become a SPOF and how is it solved?**

<details>
<summary>Answer</summary>

**The pattern:**

A load balancer sits in front of a pool of backend servers. It:
1. Continuously **health-checks** each backend (TCP check, HTTP GET, custom endpoint)
2. **Distributes traffic** among healthy backends only
3. **Removes failed backends** from the pool automatically (no manual intervention)
4. **Re-adds recovered backends** once they pass health checks again

Traffic distribution algorithms:
- **Round-robin:** Requests go to each server in sequence — simple and works well when servers are identical
- **Least connections:** Routes to the server with fewest active connections — better when requests have variable processing time
- **Consistent hashing:** Same client/session always routes to the same server — useful for soft session affinity
- **IP hash:** Client IP determines the server — useful for geographic consistency

**How this provides HA:**
- A server crashing is detected within seconds (health check intervals are typically 5–30 seconds)
- Failed server is automatically removed; its traffic redistributes to remaining healthy servers
- New servers can be added to the pool at any time without downtime (blue-green, rolling deployments)
- The system degrades gracefully under partial failure — you lose capacity but not availability

**The Load Balancer SPOF Problem:**

If you have a single load balancer, it is now Your SPOF:
- The LB crashes → all traffic fails, despite your 3 healthy backend servers sitting idle
- The LB's network interface fails → same result
- The LB's OS needs a security patch requiring a reboot → planned downtime

**Solutions:**

**Cloud-managed load balancers (recommended):**
- AWS ALB/NLB, Google Cloud Load Balancer, Azure Load Balancer
- The cloud provider manages redundancy internally — the LB endpoint is backed by multiple physical nodes across AZs
- No additional configuration needed — redundancy is built in
- DNS returns an IP (or an Anycast IP) that is served by the cloud provider's globally redundant infrastructure

**On-premises / self-managed: keepalived + Virtual IP (VIP)**
- Run two load balancer instances (e.g., two HAProxy servers)
- `keepalived` runs on both, sending heartbeats between them
- A **Virtual IP (VIP)** floats between them — whichever is the active one owns the VIP
- If the active LB dies, keepalived on the standby detects the missing heartbeat and claims the VIP for itself using **VRRP (Virtual Router Redundancy Protocol)**
- Clients always connect to the VIP — they never notice which physical LB is serving them
- Failover typically happens in under 5 seconds

**Multiple LBs with DNS-based routing:**
- Two LBs, each with their own IP, registered in DNS with low TTL
- If one LB goes down, remove its IP from DNS
- Limited by DNS TTL — clients may still route to the dead LB for minutes until their cache expires

</details>

---

**Q16. What is the difference between synchronous and asynchronous database replication? When would you choose each?**

<details>
<summary>Answer</summary>

**The core question:** When a write is committed on the primary, how do we ensure it also exists on the replica — and how urgent is that guarantee?

---

**Synchronous Replication**

- The primary sends the write to the replica and **waits for a confirmation (ACK)** from the replica before telling the client the write succeeded
- The client does not get a success response until the data is safely on **both** the primary and the replica
- If the replica is unavailable or slow, the primary's write latency increases

**Properties:**
- **RPO = 0** (Recovery Point Objective): If the primary dies immediately after a write is acknowledged, the replica has that data. Zero data loss.
- **Higher write latency:** Every write must make a round trip to the replica. For same-AZ replicas (1–2ms), this is negligible. For cross-region replicas (100ms+), this is unacceptable.
- **Replica availability affects primary availability:** If the replica crashes, synchronous replication can either block or fail writes (depending on configuration)

**Use cases:**
- The designated **failover target** — the replica you will promote if the primary dies
- Same-region or same-AZ replicas where the latency penalty is minimal
- Financial systems, order processing — any workload where losing even one transaction is unacceptable

---

**Asynchronous Replication**

- The primary writes to its local durable storage and **immediately acknowledges the client** — without waiting for the replica
- The write is shipped to the replica in the background, typically within milliseconds to seconds
- The replica "catches up" continuously, but is always slightly behind the primary (called **replication lag**)

**Properties:**
- **No write latency impact:** The client gets a response as fast as the primary's local disk can commit
- **Non-zero RPO:** If the primary crashes before the replica has replicated the latest writes, those writes are lost — the replica becomes the new primary and it is missing data
- **Replication lag can grow:** During high write load or a slow network, the replica may fall further behind. In extreme cases it can lag by minutes.

**Use cases:**
- **Read replicas** — offloading read traffic from the primary. Slightly stale reads are often fine (e.g., product listings, user profiles)
- **Analytics replicas** — run expensive reporting queries without impacting the production primary
- **Cross-region replicas** — synchronous would add 100ms+ to every write; async allows geo-replication without sacrificing write performance

---

**Semi-synchronous Replication (middle ground)**

- The primary waits for **at least one** replica to acknowledge before responding to the client
- Other replicas continue asynchronously
- **Result:** If the primary fails, at least one replica has the latest data. But you cannot guarantee all replicas are up to date.
- Used in: MySQL with `rpl_semi_sync_master_enabled`, PostgreSQL quorum-based synchronous commit

---

**Practical architecture (what most production systems use):**

```
Primary (sync) ──► Sync Replica [Failover Target]   ← zero data loss failover
        (async) ──► Read Replica 1                   ← offload reads
        (async) ──► Read Replica 2 (cross-region)    ← geo reads, DR
        (async) ──► Analytics Replica                ← reporting queries
```

</details>

---

**Q17. What is the Queue-Based Load Leveling pattern and how does it improve availability?**

<details>
<summary>Answer</summary>

**The problem it solves:**

Many systems have workloads that are **bursty** — traffic is not uniform. A flash sale, a viral social media post, or a batched cron job can generate 10×–100× the normal request rate for a short window. If your database or downstream service is sized for average load, these spikes overwhelm it, causing failures.

Without a queue: Client → App Server → Database  
If traffic spikes 100×, the database receives 100× the write pressure and either queues connections internally (adding latency) or rejects connections entirely.

**The pattern:**

Insert a **durable message queue** (Kafka, AWS SQS, RabbitMQ) between the producers (your API servers) and the consumers (workers that do the actual database writes or heavy processing).

```
API Servers ──► Message Queue ──► Worker Pool ──► Database
```

- API servers **write the request into the queue** — this is fast and can handle huge burst rates
- Workers **read from the queue and process at a sustainable rate** — they are not overwhelmed by the burst
- The queue **buffers the excess** — messages accumulate during the spike and drain as normal traffic resumes

**How it improves availability:**

**1. Decoupling producers from consumers:**  
The API server's job is done once the message is in the queue. If the database goes down for 10 minutes, the API servers keep writing to the queue. When the database recovers, workers resume processing from where they left off. Without a queue, a 10-minute database outage = 10 minutes of failure for all clients.

**2. Traffic spike absorption:**  
A flash sale generates 50,000 orders in 30 seconds. With a queue, all 50,000 write successfully into the queue immediately. Workers process them at whatever rate the database can sustain (e.g., 1,000/second). The queue depth grows during the spike and drains over the next minute. No failures, just a brief processing delay.

**3. Resilience to worker failures:**  
A worker crashes mid-processing. The message it was handling is either still in the queue (if it hadn't been acknowledged yet) or can be re-queued via dead letter queues. The message is not lost. The remaining workers continue processing.

**4. Independent scaling:**  
You can scale workers separately from API servers, based on queue depth. Auto-scaling rules: "If queue depth > 10,000 messages, add 5 more workers."

**What it does NOT solve:**
- It introduces **eventual processing** — clients cannot get an immediate result from the database (you need to shift to an async request-response model, e.g., return a job ID and let the client poll for completion)
- Queue itself is now a component that needs redundancy (Kafka cluster with replication, SQS which is managed and redundant by default)

**Best for:** Order processing, image/video processing, email sending, notification delivery, data ingestion pipelines — any workload where the result does not need to be synchronous.

</details>

---

**Q18. Explain the Circuit Breaker pattern. What are its three states and how do they transition?**

<details>
<summary>Answer</summary>

**The problem it solves:**

When a downstream service starts failing or slowing down, the naive behavior is to keep retrying — flooding the failing service with more requests it cannot handle, exhausting your own thread pools waiting for responses that never come, and turning one small failure into a full system outage.

The circuit breaker pattern solves this by **failing fast** when a dependency is known to be unhealthy, buying the failing service time to recover without being hammered.

Named after electrical circuit breakers: when too much current flows (too many failures), the breaker trips (opens), stopping the flow (stopping calls) to prevent further damage.

---

**The Three States:**

**1. CLOSED — Normal Operation**
- All requests pass through to the downstream service
- The circuit breaker tracks the **failure rate** over a rolling time window (e.g., "if more than 50% of the last 20 calls failed")
- Failures include: exceptions, timeouts, HTTP 5xx responses
- **Transition to OPEN:** When the failure rate exceeds the configured threshold

**2. OPEN — Failing Fast**
- All requests to the downstream service are **immediately rejected** with an error — no actual network call is made
- This prevents: wasting thread pool capacity on calls that will fail, overloading a struggling dependency with even more requests
- The circuit breaker starts a **timeout timer** (e.g., 30 seconds)
- During this time, the failing service (hopefully) has time to recover
- **Transition to HALF-OPEN:** After the timeout expires

**3. HALF-OPEN — Testing Recovery**
- The circuit breaker allows a **small number of test requests** through to the dependency
- These test requests check: "Has the service recovered?"
- **Transition to CLOSED:** If the test requests succeed (failure rate drops below threshold) → circuit closes, normal traffic resumes
- **Transition back to OPEN:** If test requests fail → service has not recovered yet; reset the timeout and go back to Open

---

**State Diagram:**
```
CLOSED ──(failures > threshold)──► OPEN
  ▲                                  │
  │                              (timeout)
  │                                  ▼
  └──(test succeeds)────── HALF-OPEN
                               │
                          (test fails)
                               │
                               ▼
                            OPEN (reset timeout)
```

---

**Configuration parameters you tune in an interview:**
- **Failure threshold:** What percentage of calls must fail before tripping (e.g., 50%)
- **Minimum request volume:** Require at least N calls in the window before evaluating (avoids tripping on 1 failure when traffic is low)
- **Evaluation window:** Rolling time window (last 60 seconds) or rolling count (last 20 calls)
- **Open timeout (sleep duration):** How long to stay Open before testing recovery (e.g., 30 seconds)
- **Test request volume in Half-Open:** How many test requests to allow (e.g., 5)

---

**Benefits in practice:**
- **Faster failure detection:** Clients get an immediate error instead of waiting for a timeout (often 30+ seconds) — turns a 30-second hang into a 5ms rejection
- **Prevents resource exhaustion:** No threads tied up waiting on a service that is down
- **Gives dependencies time to recover:** Stops the flood of traffic that was preventing the dependency from healing
- **Degraded-mode operation:** The circuit-open error can be caught and handled — e.g., serve a cached result, return a sensible default, or show "this feature is temporarily unavailable"

</details>

---

## Tradeoffs & Design Thinking

**Q19. Redundancy is not free. How do you justify the cost of high availability to stakeholders?**

<details>
<summary>Answer</summary>

**The core framing:** High availability is insurance. You are paying a known, predictable cost to protect against an uncertain but potentially catastrophic event. The question is whether the premium is justified by the risk.

**Step 1: Quantify the cost of downtime**

You need to calculate what an outage actually costs the business:

- **Direct revenue loss:**  
  If your e-commerce site does $1M/day in revenue, that is ~$700/minute. One hour of downtime = $42,000 in lost sales.

- **SLA penalties:**  
  Enterprise contracts often include financial penalties for missing uptime SLAs. A 99.9% SLA breach on a $1M/year contract might trigger a 10–30% credit.

- **Recovery costs:**  
  Engineering on-call time during incident, time to debug and restore, potential data recovery work.

- **Reputational damage:**  
  Harder to quantify but real. Customer churn, negative press, loss of enterprise deals. For B2B SaaS, a major outage can be cited in contract terminations.

- **Regulatory consequences:**  
  In healthcare, finance, or government: non-compliance fines, audit failures, license revocations.

**Step 2: Compare against the cost of redundancy**

Running a hot standby database might cost an additional $500–$2,000/month depending on instance size. If your revenue is $700/minute and the standby saves you from one 10-minute outage per year, it pays for itself in that single incident — and prevents the SLA penalties, churn, and reputation damage on top.

**Step 3: Use tiered SLAs — not everything needs five nines**

Not all services have equal business impact. A tiered approach lets you spend HA budget wisely:

| Service | Criticality | Target | Justification |
|---|---|---|---|
| Payment processing | Revenue-critical | 99.99% | Direct revenue loss, chargeback risk |
| User authentication | High | 99.9% | Users cannot access anything |
| Recommendations engine | Low | 99% | Degraded experience but still functional |
| Admin dashboard | Very low | 95% | Only internal users, low volume |

**Step 4: Prioritize redundancy by risk**

Eliminate SPOFs in priority order based on: (probability of failure) × (impact of failure).

- Your single database: high probability of eventually failing, catastrophic impact → eliminate first
- A single load balancer: moderate probability, catastrophic impact → eliminate second
- Each app server: moderate probability, low impact (other servers absorb) → already covered by horizontal scaling

**Step 5: Frame it as operational maturity, not just cost**

Organizations that invest in HA also benefit from:
- Faster deployments (rolling updates, blue-green) — engineering velocity goes up
- Less on-call stress — fewer 3 AM pages when systems fail gracefully
- Confidence to move faster — teams that know they can roll back quickly take smarter risks

</details>

---

**Q20. How would you design a system to achieve 99.99% (four nines) availability?**

<details>
<summary>Answer</summary>

Four nines means **52 minutes of downtime budget per year**. That is less than one minute per week. Every deployment, every hardware failure, every on-call response must happen within that budget.

**This requires that every single failure is automatically handled without human intervention.** You cannot page an on-call engineer and wait for them to act — that alone takes longer than your weekly budget.

---

**Layer-by-layer design:**

**DNS Layer**
- Use a managed, globally redundant DNS provider (Route 53, Cloudflare) — they are already multi-region and anycast by design
- Configure low TTLs (60 seconds) for fast failover if you need to switch endpoints
- Use health-check-based routing (Route 53 health checks + failover routing policy)

**Load Balancer Layer**
- Use **cloud-managed load balancers** (AWS ALB, GCP Load Balancer) — redundancy is automatic and included
- Configure health checks with aggressive thresholds: check every 10 seconds, mark unhealthy after 2 failures
- Use cross-zone load balancing to distribute across all AZs even if traffic enters through one

**Application Layer**
- Deploy across **at least 2 Availability Zones** (ideally 3 for N+2 redundancy)
- Use auto-scaling groups that automatically replace unhealthy instances with new ones
- Stateless application design: no local state on the servers (sessions in Redis, files in S3)
- Implement circuit breakers on all downstream calls with appropriate timeout values
- Graceful degradation: if a non-critical service is down, return sensible defaults rather than failing the whole request

**Database Layer** (the hardest part)
- **Primary database** with a **synchronous hot standby** in a second AZ for zero-data-loss failover
- Automated failover orchestration (Patroni for PostgreSQL, AWS RDS Multi-AZ which handles this automatically)
- Read replicas (async) in additional AZs to offload read traffic and increase read availability
- Connection pooling (PgBouncer, ProxySQL) so application reconnects transparently after failover
- Regular automated failover drills to verify the failover works and measure actual failover time

**Caching Layer**
- Redis Cluster or Redis Sentinel for HA cache
- Design the application to tolerate cache misses gracefully — a cache failure should cause slower responses, not errors

**Queue Layer (if applicable)**
- Kafka with at least 3 brokers and replication factor ≥ 2 (minimum 1 replica per broker)
- Or use managed SQS/Pub-Sub which handles redundancy automatically

**Deployment Strategy**
- **Rolling deployments:** Replace old instances one at a time while maintaining minimum capacity
- **Blue-green deployments:** Spin up the new version in full, run health checks, then switch traffic over atomically — instant rollback by switching back
- **Canary deployments:** Send 1% of traffic to new version first; if error rate is acceptable, gradually increase to 100%
- Zero-downtime deploys are non-negotiable at four nines

**Monitoring & Incident Response**
- **Real-time alerting:** P99 latency, error rate, database replication lag — alert within 60 seconds of an anomaly
- **Runbooks for every alert:** On-call engineer should be able to follow steps, not improvise
- **Automated remediation:** Auto-scaling triggers, automatic instance replacement, automated cache warming scripts
- **Chaos engineering:** Regularly intentionally kill instances, cut network connections, and verify the system behaves as designed (Netflix's chaos monkey approach)
- **RTO target:** Mean Time To Recovery must be under 5 minutes for most failure types

---

**What four nines does NOT require:**
- Multi-region (multi-AZ is sufficient for most failure modes)
- Exotic distributed databases (PostgreSQL with Patroni + multi-AZ is well-understood and achieves this)
- Massive additional cost — the marginal cost of going from 3 nines to 4 nines is primarily engineering effort on automation, not raw infrastructure spend

</details>

---

**Q21. What is MTBF and MTTR? How do they relate to availability?**

<details>
<summary>Answer</summary>

**MTBF — Mean Time Between Failures**

The average amount of time a system or component operates successfully before experiencing a failure. Measured in hours, days, or years.

- MTBF = Total operational time / Number of failures
- Example: A server runs for 1 year and fails 3 times → MTBF = 365 days / 3 = ~121 days between failures
- A high MTBF means the system is reliable and does not fail often
- MTBF is about the **frequency** of failures

**MTTR — Mean Time To Recovery (also called Mean Time To Repair)**

The average time it takes to restore service after a failure occurs. Includes detection time, diagnosis time, remediation time, and verification time.

- MTTR = Total downtime / Number of failures
- Example: Over 3 failures, total downtime was 3 hours → MTTR = 60 minutes per failure
- A low MTTR means you recover quickly when things go wrong
- MTTR is about the **speed** of recovery

**The formula connecting them to availability:**

```
Availability = MTBF / (MTBF + MTTR)
```

**Example:**
- MTBF = 1000 hours (system fails once every ~6 weeks)
- MTTR = 1 hour (takes 1 hour to recover each time)
```
Availability = 1000 / (1000 + 1) = 99.9% (three nines)
```

**What happens when you improve each metric:**

| MTBF | MTTR | Availability |
|---|---|---|
| 1000 hours | 1 hour | 99.9% |
| 2000 hours | 1 hour | 99.95% |
| 1000 hours | 0.1 hours (6 min) | 99.99% |
| 2000 hours | 0.1 hours | 99.995% |

Cutting MTTR from 1 hour to 6 minutes is often **cheaper and faster** to achieve than doubling MTBF. You reduce the blast radius of each failure without needing to prevent the failure itself.

**Strategies to improve MTBF (reduce failure frequency):**
- Redundancy: if one component fails, another takes over — the system as a whole does not "fail"
- Better hardware with higher reliability ratings
- Chaos engineering: find weaknesses before they occur in production
- Load testing: identify breaking points before real traffic hits them
- Proactive replacement: replace hardware before its expected end of life

**Strategies to reduce MTTR (recover faster):**
- **Automated failover:** Replace minutes of manual steps with seconds of automated switching
- **Health checks + auto-healing:** Automatically terminate and replace unhealthy instances
- **Runbooks:** Documented step-by-step recovery procedures so on-call engineers don't improvise under pressure
- **Monitoring and alerting:** Detect failures within seconds rather than hearing about them from customers
- **Rollback automation:** Redeploy the previous version in one command or one click
- **Pre-warmed spare capacity:** AWS Warm Pools, reserved instances, or pre-scaled auto-scaling groups

**The key insight for system design interviews:**

In highly available systems, we often redefine "failure" at the system level. A single server failing is Not a system failure if redundancy kicks in automatically and traffic continues uninterrupted. In that case, the "MTTR" from the system's perspective is effectively zero — even though the failed server takes an hour to replace. This is why redundancy is so effective: it converts component-level failures into non-events from the system's perspective.

</details>

---

**Q22. Compare multi-region vs multi-AZ deployment. When would you choose each?**

<details>
<summary>Answer</summary>

**What each protects against:**

| | Multi-AZ | Multi-Region |
|---|---|---|
| Single server failure | ✅ | ✅ |
| Single data center failure | ✅ | ✅ |
| Regional disaster (natural disaster, major network event) | ❌ | ✅ |
| Cloud provider regional outage | ❌ | ✅ |
| Global CDN failure | ❌ | Partial |

---

**Multi-AZ Deployment**

**What it is:**  
Running your application and database replicas across 2–3 Availability Zones within the same cloud region. AZs are separate data centers within the same metropolitan area, connected by high-speed, low-latency fiber.

**Characteristics:**
- Round-trip latency between AZs: **1–2ms**
- Makes **synchronous database replication** feasible — zero data loss failover
- Same region = same cloud provider APIs, same IAM, same VPC (just different subnets)
- Data transfer between AZs is billed but cheap ($0.01–$0.02/GB typically)

**Architecture:**
- 3 app servers: one per AZ, behind a cross-zone load balancer
- Primary database in AZ-1, synchronous standby in AZ-2 (Patroni/RDS Multi-AZ handles this)
- If AZ-1 goes down: load balancer stops routing to the AZ-1 app server, standby in AZ-2 is promoted to primary in ~30 seconds

**Best for:**
- Most production web applications
- Systems with strong consistency requirements (synchronous replication is feasible)
- Teams with moderate operational complexity budget
- SLAs up to 99.99% (four nines)

---

**Multi-Region Deployment**

**What it is:**  
Running independent deployments of your stack in geographically separate regions — different cities or countries. Each region is self-sufficient — it has its own load balancers, app servers, and database.

**Characteristics:**
- Round-trip latency between regions: **50–200ms** depending on geography
- **Synchronous replication across regions is impractical** — adds 50–100ms to every write
- Most multi-region systems use **asynchronous replication** with the trade-off of possible data loss (seconds to minutes of RPO) in a disaster
- DNS-based traffic routing (Route 53 geolocation or latency-based routing, Cloudflare)
- Each region needs its own operational setup: monitoring, deployment pipelines, secrets management

**Additional challenges:**
- **Data consistency:** With async replication, reads in one region may be stale relative to writes in another
- **Conflict resolution:** If users in two regions write to the same data, you need a conflict resolution strategy (last-write-wins, vector clocks, merge functions)
- **Cost:** Roughly 2× the infrastructure cost, plus data transfer fees between regions
- **Operational complexity:** Significantly higher — deployments must be coordinated across regions, schema migrations must be backward compatible and rolled out carefully

**Best for:**
- **Global applications** where users in Europe should connect to EU servers for low latency, and users in Asia to Asia-Pacific servers
- **Strict disaster recovery requirements** with defined RTO/RPO SLAs (e.g., "we must recover within 15 minutes of a complete regional failure")
- **Regulatory compliance** — data from EU customers may be legally required to stay within EU borders (GDPR)
- **Maximum availability SLAs** (five nines) where a regional cloud provider outage cannot be acceptable

---

**Decision framework:**

| Question | If Yes → |
|---|---|
| Do you need to survive a complete AWS us-east-1 outage? | Multi-region |
| Do users in Asia currently experience >150ms latency connecting to US? | Multi-region (with region in Asia) |
| Is GDPR data residency a legal requirement? | Multi-region |
| Is your team smaller than 10 engineers? | Multi-AZ (multi-region is operationally very expensive) |
| Do you have strong consistency requirements that make async replication risky? | Multi-AZ (synchronous replication feasible) |
| Can you tolerate up to 10 minutes of data loss in a disaster? | Multi-region with async replication is viable |

**For most production applications**, multi-AZ across 2–3 zones is the right default. Multi-region is a deliberate escalation for specific business requirements, not a baseline best practice.

</details>
