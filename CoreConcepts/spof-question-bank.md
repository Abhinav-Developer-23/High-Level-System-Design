# Single Point of Failure (SPOF) — Question Bank

## Beginner Level
1. What is a Single Point of Failure (SPOF) in system design?

<details><summary>Answer</summary>A Single Point of Failure (SPOF) is any component whose failure can stop the whole system or a critical user flow. If one component fails and there is no backup path, that component is a SPOF.</details>

2. Why are SPOFs dangerous in distributed systems?

<details><summary>Answer</summary>SPOFs are dangerous because distributed systems are expected to fail in parts (hardware, network, software, power, and human mistakes). If one failure can cause full outage, downtime and user impact become severe.</details>

3. Give a real-life analogy for SPOF.

<details><summary>Answer</summary>A bridge connecting two cities is a SPOF if it is the only route. If the bridge collapses, all movement between the cities stops.</details>

4. Is a single load balancer usually a SPOF? Why?

<details><summary>Answer</summary>Yes. If only one load balancer exists, clients cannot reach backend servers when it fails, even if application servers are healthy.</details>

5. Is a single primary database typically a SPOF?

<details><summary>Answer</summary>Yes. If the only database instance fails, data becomes unavailable and can cause downtime or even data loss without replication and backups.</details>

6. Is a cache server always a SPOF?

<details><summary>Answer</summary>Not always. Cache failure may not stop the entire system, but it can heavily degrade performance and overload the database. So it is often a performance SPOF, not always a total availability SPOF.</details>

7. Are two application servers enough to remove all SPOFs?

<details><summary>Answer</summary>No. Redundancy at one layer helps, but SPOFs can still exist in other layers like load balancer, database, DNS, network link, or authentication service.</details>

8. What is the simplest mitigation for a SPOF?

<details><summary>Answer</summary>Add redundancy: at least one healthy backup path or instance that can take over automatically or manually.</details>

## Intermediate Level
9. How do you identify SPOFs using architecture mapping?

<details><summary>Answer</summary>Draw all components and dependencies end-to-end. Then mark components with no backup or failover path. Any required component without redundancy is a likely SPOF.</details>

10. How does dependency analysis help find SPOFs?

<details><summary>Answer</summary>If many services depend on one shared component (e.g., one auth service, one message broker, one config service), failure blast radius is large. Shared critical dependencies without backup are SPOFs.</details>

11. What is a failure impact assessment for SPOF detection?

<details><summary>Answer</summary>It is a “what if this fails?” analysis per component. If failure causes system-wide outage or severe degradation with no fallback, it is a SPOF candidate.</details>

12. How does chaos testing help uncover SPOFs?

<details><summary>Answer</summary>By intentionally shutting down instances or introducing network faults, chaos tests reveal hidden assumptions and components that cause disproportionate outages when they fail.</details>

13. What is active-active vs active-passive redundancy in SPOF mitigation?

<details><summary>Answer</summary>Active-active means multiple instances serve traffic simultaneously. Active-passive means one serves traffic while standby waits for failover. Both remove SPOFs when failover is reliable.</details>

14. How can load balancer redundancy be implemented?

<details><summary>Answer</summary>Use multiple load balancer instances with health checks and failover (often with VIP, DNS failover, or managed LB service). If one fails, traffic shifts to healthy LB nodes.</details>

15. Why is data replication key to avoiding database SPOFs?

<details><summary>Answer</summary>Replication creates copies of data across nodes/regions. If one database node or location fails, another can serve reads/writes (depending on architecture), reducing downtime and data loss risk.</details>

16. Synchronous vs asynchronous replication: which is better for SPOF prevention?

<details><summary>Answer</summary>Both help availability but trade off differently. Synchronous replication improves consistency and durability but can increase latency. Asynchronous replication improves performance but risks replica lag and data loss on failover.</details>

17. How does geographic distribution reduce SPOF risk?

<details><summary>Answer</summary>Regional outages (power/network/cloud-zone failures) can take down single-region systems. Multi-region deployment and distributed data reduce dependence on one geography.</details>

18. What is graceful degradation and how does it relate to SPOFs?

<details><summary>Answer</summary>Graceful degradation keeps core features available when a non-critical dependency fails. It reduces the chance that one subsystem failure becomes full-system failure.</details>

## Advanced / Interview Level
19. In a system with 2 app servers, 1 load balancer, 1 DB, and 1 cache, identify SPOFs.

<details><summary>Answer</summary>Likely SPOFs: single load balancer and single database. Cache is often not a full SPOF but can cause severe slowdown and DB overload when unavailable. App tier is not a SPOF if one node can handle reduced traffic.</details>

20. How would you prioritize SPOF fixes with limited engineering time?

<details><summary>Answer</summary>Rank by business impact × likelihood × recovery difficulty. First remove SPOFs on critical user journeys and stateful data systems (LB, DB, DNS, auth). Then harden secondary paths (cache, analytics, back-office tools).</details>

21. What monitoring signals are most useful for SPOF early detection?

<details><summary>Answer</summary>Component health checks, failover success rate, error rate, latency spikes, dependency saturation, replication lag, and “single remaining healthy instance” alerts.</details>

22. How can automation reduce SPOF risk during incidents?

<details><summary>Answer</summary>Automated failover, auto-healing, self-registration/deregistration, and runbook automation reduce human delay and mistakes, lowering MTTR when a critical component fails.</details>

23. Why can a control plane become a hidden SPOF even if data plane is redundant?

<details><summary>Answer</summary>If all routing/config/auth decisions depend on one control-plane service, data-plane nodes may be healthy but unusable when control plane is down. Control and data planes both need redundancy.</details>

24. What are common false assumptions that create hidden SPOFs?

<details><summary>Answer</summary>“Cloud managed service cannot fail,” “DNS is always available,” “one region is enough,” “manual failover is fine,” and “replicas are always up-to-date.” These assumptions fail in real incidents.</details>

25. Design question: How would you make a payment API resilient to SPOFs?

<details><summary>Answer</summary>Use redundant API gateways/LBs, multi-instance stateless app layer, replicated transactional datastore, multi-AZ/region deployment, idempotency keys, circuit breakers, queue-based retries, and strict monitoring with tested failover drills.</details>

---

## Rapid-Fire Revision Prompts
- Define SPOF in one sentence.
- Name three common SPOFs in a web architecture.
- Why is a single DB more dangerous than a single cache?
- Give one active-passive and one active-active example.
- What metric indicates failover quality?
- How does chaos testing reveal hidden SPOFs?
