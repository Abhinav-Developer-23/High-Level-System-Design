# Leadership Principles — Interview Questions & Answers

---

> [!IMPORTANT]
> ## 🤖 LLM Instruction — STAR Format
>
> **All answers in this file MUST follow the STAR pattern:**
>
> | Step | What to Write |
> |---|---|
> | **S — Situation** | Set the scene. Describe the context — project, team, timeline, constraints. |
> | **T — Task** | What was *your* specific responsibility or the challenge you owned? |
> | **A — Action** | What did *you* do? Be specific — decisions made, steps taken, trade-offs considered. |
> | **R — Result** | What was the measurable outcome? Metrics, impact, lessons learned. |
>
> **When adding a new question:**
> 1. Write the question as a `###` heading.
> 2. Add the answer below using the STAR template provided.
> 3. Keep answers concise but impactful — aim for 6–10 sentences total.
>
> **STAR Answer Template:**
> ```
> **Situation:** ...
> **Task:** ...
> **Action:** ...
> **Result:** ...
> ```

---

## Questions

---

### <span style="color:red">Q1. Tell me about a situation where you were assigned a critical task. Why was it critical, and how did you solve the challenges faced?</span>

**Also asked as:**
- <span style="color:red">*Have you ever fixed any critical issue?*</span>

> **💡 Principle:** Deliver Results · Bias for Action · Ownership

**Suggested Answer (customize with your own experience):**

**Situation:** In my previous role, our production payment service started throwing intermittent 5xx errors during peak hours (8–10 PM), impacting ~15% of transactions. The on-call engineer escalated it to me because the root cause wasn't obvious — logs showed timeouts but no clear failure point. Revenue loss was estimated at ₹X lakhs/hour, and the business team was already getting customer complaints.

**Task:** I was tasked with identifying the root cause, applying an immediate fix to restore service health, and then implementing a permanent solution — all while keeping stakeholders updated on the timeline.

**Action:**
1. I first checked dashboards (Grafana/CloudWatch) and noticed the DB connection pool was exhausting during peak load — connections were being acquired but not released in a specific code path (a missing `finally` block in a try-with-resources equivalent).
2. For the **immediate fix**, I increased the connection pool size from 20 → 50 and set a hard acquisition timeout of 5s so threads wouldn't hang indefinitely. Deployed this hotfix within 30 minutes.
3. For the **permanent fix**, I traced the leak to a recently merged PR that bypassed the connection-release logic on a specific error branch. I fixed the resource handling, added a connection-leak detection flag in HikariCP config, and wrote an integration test that simulated pool exhaustion.
4. I also set up an alert on `active connections > 80%` so we'd catch this early in the future.

**Result:** The hotfix restored error rates from ~15% back to <0.1% within minutes of deployment. The permanent fix was shipped the next day with a regression test. I also drove a mini post-mortem where we added connection-pool monitoring as a standard checklist item for all new services. No recurrence in the following 6+ months.

---

> [!TIP]
> **How to make this your own:**
> - Swap the scenario with a real incident you handled (DB issue, memory leak, API outage, deployment failure, etc.)
> - Mention specific tools you used (Grafana, Splunk, Datadog, CloudWatch, etc.)
> - Quantify the impact — error %, revenue affected, time to resolve
> - Highlight what you did *differently* or *proactively* (alert, post-mortem, test)

<!-- Add more questions below -->

