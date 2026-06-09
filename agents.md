# Agents — Purpose of These Notes

---

## What Are These Files?

These files are **personal quick-reference notes and runnable tutorials** — created to help revise and recall key Java concepts, syntax, and patterns before interviews, system design rounds, or when building projects.

## Why This Exists

- **Quick syntax recall** — Forget how `thenCompose` works? Check [TutorialsJava.java](Java/JavaTutorial/src/test/java/org/example/TutorialsJava.java).
- **Concept refresher** — Concurrency, GC, memory model — all in [Java.md](Java/Java.md).
- **Interview prep** — Each topic has quick-fire Q&A tables for last-minute revision.
- **No fluff** — Straight to the point with code examples, comparison tables, and diagrams.

## File Index

| File | Type | Covers |
|---|---|---|
| [Java.md](Java/Java.md) | Markdown notes | ThreadPoolExecutor, CompletableFuture theory, JVM Memory Model, Garbage Collection, GC Tuning |
| [TutorialsJava.java](Java/JavaTutorial/src/test/java/org/example/TutorialsJava.java) | **Runnable JUnit 5 tests** | CompletableFuture — 14 fully documented examples with rich comments explaining every method and pattern |

## About TutorialsJava.java

> **This file is designed for learning via testing.** Every test method, every line has detailed documentation and comments explaining:
> - **What** the API does
> - **Why** you'd use it
> - **When** to choose one approach over another
> - **Gotchas** and production tips
>
> You can **run individual tests** directly from your IDE (like IntelliJ IDEA) by clicking the Play button next to the test methods, or run the entire suite using Maven (`mvn test`).

### Topics covered in TutorialsJava.java:

1. Creating futures — `supplyAsync`, `runAsync`
2. Chaining — `thenApply`, `thenAccept`, `thenRun`
3. Composing — `thenCompose` (flatMap for dependent async calls)
4. Combining — `thenCombine`, `allOf`, `anyOf`
5. Exception handling — `exceptionally`, `handle`, `whenComplete`
6. Custom executors (why to avoid `commonPool` for I/O)
7. Real-world parallel API aggregation example

## How to Use

1. **Before an interview** — Skim the comparison tables in Java.md and the comment boxes in TutorialsJava.java.
2. **While coding** — Look up exact syntax and patterns from the test cases.
3. **Deep revision** — Read the full sections with diagrams and real-world examples.
4. **Hands-on practice** — Run tests in `TutorialsJava.java` and modify assertions to experiment.

---

> 💡 **Keep adding more topics here as you learn them.** These notes are a living document.
