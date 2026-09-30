# Gemini Agent Instructions — AlgoMaster HLD Workflow

---

## 🎯 Purpose & Workflow Objective

This repository contains High-Level System Design (HLD) study notes, interview architectures, and system blueprints.

The user will provide URLs to specific High-Level System Design pages (such as from [AlgoMaster.io](https://algomaster.io)). The coding agent's responsibility follows a 3-step iterative learning and design process:

```
[AlgoMaster HLD URL]
        │
        ▼ (Step 1: Ingestion)
[Capture .mhtml via Chrome DevTools]
        │
        ▼ (Step 2: Discussion)
[User & Agent Discuss Gaps, Trade-offs & Improvements]
        │
        ▼ (Step 3: Enhancement)
[Agent Updates & Enriches the MHTML / HLD Design]
```

---

## 📋 The 3-Step Process

### 1. Capture & Snapshot (.mhtml)
- **Tooling**: Use Chrome DevTools (CDP / Chrome DevTools MCP) via headless Chrome (`Page.captureSnapshot` with `format: 'mhtml'`).
- **Target Folder**: Store generated files in the [`hld/`](./hld) folder (and mirror into [`HLD_Questions/`](./HLD_Questions) if relevant).
- **Quality Requirements**:
  - Full client-side hydration (Next.js / React apps).
  - Programmatic scroll-through to trigger lazy-loaded images, SVG diagrams, and charts.
  - Self-contained archive including CSS, fonts, and inline assets so it opens identically offline.

### 2. Design Review & Improvement Discussion
- The user and agent analyze the baseline design captured in the MHTML.
- Discuss system bottlenecks, missing components, and real-world scale challenges:
  - **Scalability & Partitioning**: Hot partitions, sharding keys, consistent hashing.
  - **Reliability & Fault Tolerance**: Idempotency keys, retry backoff, Dead-Letter Queues (DLQ), circuit breakers.
  - **Availability & Latency**: Multi-region failover, caching layers, write-through vs read-through.
  - **Security & Rate Limiting**: Token bucket / sliding window rate limiting, authentication, payload encryption.
  - **Cost & Operational Efficiency**: Batching, deduplication windows, tiering storage (hot vs cold).

### 3. Iterative Enhancement in the MHTML / HLD
- **The Core Goal**: The `.mhtml` file is **not just an archive**, but a **living baseline** to be enhanced.
- The coding agent modifies and improves the MHTML (or accompanying interactive HTML / Markdown notes) by:
  - Inserting new architecture diagrams (Mermaid / SVG).
  - Adding deep-dive sections addressing the edge cases discussed with the user.
  - Adding comparison tables, trade-off analyses, and production-grade failure handling strategies.
  - Highlighting additions clearly with distinctive callout banners or section headers (e.g., `⭐ Enhanced Architecture & Improvements`).

---

## 🛠️ Automated MHTML Capture Recipe

When given a new AlgoMaster URL:
1. Run a script using Chrome with remote debugging enabled (`--remote-debugging-port`).
2. Connect to the CDP WebSocket.
3. Enable `Page` and `Network`.
4. Navigate to the target URL, wait for initial hydration and scroll down the document to load all lazy diagrams.
5. Invoke `Page.captureSnapshot` with `{ format: 'mhtml' }`.
6. Write the resulting MHTML data to `hld/<slug>.mhtml`.

---

## 📁 File Organization

| Path | Purpose |
|---|---|
| [`hld/`](./hld) | Offline `.mhtml` snapshots and enhanced interactive designs |
| [`HLD_Questions/`](./HLD_Questions) | Markdown notes, question breakdowns, and design summaries |
| [`AGENTS.md`](./AGENTS.md) | Java, Concurrency, and System Design quick-reference notes |
| [`gemini.md`](./gemini.md) | AlgoMaster HLD capture & design enhancement workflow guidelines |
