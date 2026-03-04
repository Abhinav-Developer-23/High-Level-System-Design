# Java Concurrency — ThreadPoolExecutor & CompletableFuture

---

## 1. ThreadPoolExecutor

`ThreadPoolExecutor` is the most powerful and configurable thread pool implementation in Java (`java.util.concurrent`). All the convenience pools created via `Executors` factory methods (`newFixedThreadPool`, `newCachedThreadPool`, etc.) ultimately delegate to a `ThreadPoolExecutor` under the hood.

### 1.1 Why Do We Need a Thread Pool?

- **Thread creation is expensive** — each thread allocates a stack (~512 KB–1 MB) and involves a kernel call.
- Without pooling, a burst of 10 000 requests would spawn 10 000 threads, causing massive context-switching overhead and possible `OutOfMemoryError`.
- A thread pool **reuses** a fixed set of threads, queues excess work, and applies back-pressure when the system is overloaded.

### 1.2 Constructor Parameters

```java
public ThreadPoolExecutor(
    int corePoolSize,
    int maximumPoolSize,
    long keepAliveTime,
    TimeUnit unit,
    BlockingQueue<Runnable> workQueue,
    ThreadFactory threadFactory,
    RejectedExecutionHandler handler
)
```

| Parameter | What It Does |
|---|---|
| **corePoolSize** | Minimum number of threads kept alive in the pool (even if idle), unless `allowCoreThreadTimeOut(true)` is set. |
| **maximumPoolSize** | Upper cap on threads. Extra threads beyond `corePoolSize` are created only when the **queue is full**. |
| **keepAliveTime + unit** | How long an idle thread **above** `corePoolSize` waits before being terminated. |
| **workQueue** | A `BlockingQueue<Runnable>` that holds tasks waiting to be executed. Choice of queue heavily influences pool behaviour. |
| **threadFactory** | Factory for creating new threads (lets you set names, daemon status, priority, etc.). |
| **handler** | The `RejectedExecutionHandler` invoked when both the queue and maximum threads are exhausted. |

### 1.3 How Task Submission Works (Internal Flow)

```
          submit(task)
              │
              ▼
   ┌──────────────────────┐
   │ activeThreads < core?│──YES──▶ Create new core thread, run task
   └──────────────────────┘
              │ NO
              ▼
   ┌──────────────────────┐
   │   Queue has space?   │──YES──▶ Enqueue task (a free thread will pick it up)
   └──────────────────────┘
              │ NO
              ▼
   ┌──────────────────────────────┐
   │ activeThreads < maxPoolSize? │──YES──▶ Create new non-core thread, run task
   └──────────────────────────────┘
              │ NO
              ▼
     RejectedExecutionHandler
        is invoked ✋
```

> **Key insight:** A new thread beyond `corePoolSize` is **only** created when the queue is already full. If you use an **unbounded** queue (e.g., `LinkedBlockingQueue()` with no capacity), `maximumPoolSize` is effectively ignored because the queue never fills up.

### 1.4 Common Queue Choices

| Queue Type | Behaviour | Best For |
|---|---|---|
| `SynchronousQueue` | Zero capacity — every put must be matched by a take. Forces thread creation up to `maxPoolSize`. | `CachedThreadPool`-style pools where you want fast hand-off. |
| `LinkedBlockingQueue(capacity)` | Bounded FIFO. Tasks queue up, and once full, new threads are created up to `maxPoolSize`. | General-purpose bounded pools. |
| `LinkedBlockingQueue()` (unbounded) | Unlimited capacity. `maxPoolSize` is effectively meaningless because the queue never fills. | `FixedThreadPool`. Risk of OOM if producers are faster than consumers. |
| `ArrayBlockingQueue(capacity)` | Bounded, backed by an array. Slightly better cache locality than `LinkedBlockingQueue`. | When you want a bounded queue with predictable memory footprint. |
| `PriorityBlockingQueue` | Unbounded, orders tasks by priority (natural order or `Comparator`). | When some tasks are more urgent than others. |

### 1.5 Pre-built Pools via `Executors` Factory

| Factory Method | corePoolSize | maxPoolSize | keepAlive | Queue | Notes |
|---|---|---|---|---|---|
| `newFixedThreadPool(n)` | n | n | 0 | Unbounded `LinkedBlockingQueue` | Fixed number of threads; tasks queue indefinitely. |
| `newCachedThreadPool()` | 0 | `Integer.MAX_VALUE` | 60 s | `SynchronousQueue` | Creates threads on demand, reuses idle ones. Can explode under load. |
| `newSingleThreadExecutor()` | 1 | 1 | 0 | Unbounded `LinkedBlockingQueue` | Guarantees sequential execution. |
| `newScheduledThreadPool(n)` | n | `Integer.MAX_VALUE` | 10 ms | `DelayedWorkQueue` | For delayed / periodic tasks. |

> ⚠️ **Production tip:** Prefer constructing `ThreadPoolExecutor` directly with bounded queues and explicit rejection handlers instead of using `Executors` factory methods — the defaults can lead to memory exhaustion.

---

## 2. Rejection Handlers (When the Queue Is Full)

When **both** the work queue is full **and** the number of threads has reached `maximumPoolSize`, the pool can't accept any more tasks. At this point, the `RejectedExecutionHandler` kicks in.

Java provides **4 built-in** policies:

### 2.1 `AbortPolicy` *(default)*

```java
new ThreadPoolExecutor.AbortPolicy()
```

- **Behaviour:** Throws a `RejectedExecutionException` immediately.
- **Use when:** You want the caller to know right away that the system is overloaded and handle the failure explicitly.
- **Example scenario:** An API server that should return HTTP 503 (Service Unavailable) when overwhelmed rather than silently dropping requests.

### 2.2 `CallerRunsPolicy`

```java
new ThreadPoolExecutor.CallerRunsPolicy()
```

- **Behaviour:** The **calling thread** (the one that submitted the task) executes the task itself, effectively slowing down the producer.
- **Use when:** You want natural back-pressure — the producer slows down because it's busy executing the task.
- **Example scenario:** A message-processing pipeline where slowing down the ingestion thread is preferable to losing messages.

> 💡 This is the most commonly recommended policy for production systems because it provides **graceful degradation** without data loss.

### 2.3 `DiscardPolicy`

```java
new ThreadPoolExecutor.DiscardPolicy()
```

- **Behaviour:** Silently drops the rejected task. No exception, no log, nothing.
- **Use when:** The task is non-critical and losing it is acceptable (e.g., optional metrics/telemetry).
- **Example scenario:** Fire-and-forget analytics events where occasional loss is fine.

### 2.4 `DiscardOldestPolicy`

```java
new ThreadPoolExecutor.DiscardOldestPolicy()
```

- **Behaviour:** Drops the **oldest** task waiting in the queue (the head), then retries submitting the new task.
- **Use when:** The latest data is more valuable than older data.
- **Example scenario:** A live stock-price display — showing an old price is worse than showing the latest one, so discard stale updates.

### 2.5 Custom Handler

You can write your own by implementing `RejectedExecutionHandler`:

```java
public class LogAndDiscardPolicy implements RejectedExecutionHandler {
    private static final Logger log = LoggerFactory.getLogger(LogAndDiscardPolicy.class);

    @Override
    public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
        log.warn("Task {} rejected. Queue size: {}, Active threads: {}",
                  r, executor.getQueue().size(), executor.getActiveCount());
        // optionally: persist to a dead-letter queue, emit a metric, etc.
    }
}
```

### 2.6 Rejection Handlers Comparison

| Policy | Throws Exception? | Task Lost? | Back-Pressure? | Best For |
|---|---|---|---|---|
| **AbortPolicy** | ✅ Yes | ✅ Yes | ❌ No (caller must handle) | Fail-fast systems |
| **CallerRunsPolicy** | ❌ No | ❌ No | ✅ Yes (caller blocks) | Graceful degradation |
| **DiscardPolicy** | ❌ No | ✅ Yes | ❌ No | Non-critical fire-and-forget |
| **DiscardOldestPolicy** | ❌ No | ✅ Yes (oldest) | ❌ No | Latest-value-wins scenarios |
| **Custom** | Your choice | Your choice | Your choice | Logging, DLQ, metrics |

---

## 3. CompletableFuture

`CompletableFuture<T>` (Java 8+) is Java's answer to **composable, non-blocking asynchronous programming**. It implements both `Future<T>` and `CompletionStage<T>`.

### 3.1 Why Not Just `Future<T>`?

The old `Future<T>` returned by `ExecutorService.submit()` has a fundamental limitation — the **only** way to get the result is `future.get()`, which **blocks** the calling thread.

| Feature | `Future<T>` | `CompletableFuture<T>` |
|---|---|---|
| Get result | `get()` blocks the thread | `thenApply`, `thenAccept`, callbacks — non-blocking |
| Chain operations | ❌ Not possible | ✅ `thenApply().thenCompose().thenAccept()` |
| Combine multiple futures | ❌ Manual polling | ✅ `allOf()`, `anyOf()`, `thenCombine()` |
| Exception handling | `ExecutionException` from `get()` | `exceptionally()`, `handle()`, `whenComplete()` |
| Manually complete | ❌ | ✅ `complete()`, `completeExceptionally()` |

### 3.2 Creating a CompletableFuture

```java
// 1. Run an async task that RETURNS a value
CompletableFuture<String> cf1 = CompletableFuture.supplyAsync(() -> {
    return fetchDataFromDB();  // runs on ForkJoinPool.commonPool()
});

// 2. Run an async task that returns NOTHING
CompletableFuture<Void> cf2 = CompletableFuture.runAsync(() -> {
    sendNotification();
});

// 3. With a CUSTOM executor (recommended for I/O-bound work)
ExecutorService ioPool = Executors.newFixedThreadPool(10);
CompletableFuture<String> cf3 = CompletableFuture.supplyAsync(() -> {
    return callExternalApi();
}, ioPool);

// 4. Already-completed future (useful for testing or default values)
CompletableFuture<String> cf4 = CompletableFuture.completedFuture("default");
```

> ⚠️ By default, `supplyAsync` / `runAsync` use `ForkJoinPool.commonPool()`, which has `(Runtime.availableProcessors() - 1)` threads. This pool is **shared across the entire JVM** — always pass a custom executor for I/O-bound or long-running tasks to avoid starving other work.

### 3.3 Chaining & Transforming

#### `thenApply` — Transform the result (like `.map()`)

```java
CompletableFuture<Integer> lengthFuture = CompletableFuture
    .supplyAsync(() -> "Hello World")
    .thenApply(s -> s.length());  // 11
```

- Input: `T` → Output: `U`
- Runs **synchronously** on the thread that completed the previous stage (or the calling thread if already done).
- Use `thenApplyAsync()` to run on a different thread.

#### `thenAccept` — Consume the result (like `.forEach()`)

```java
CompletableFuture.supplyAsync(() -> fetchOrder(orderId))
    .thenAccept(order -> log.info("Order fetched: {}", order));
```

- Input: `T` → Output: `Void`

#### `thenRun` — Run an action (ignores the result)

```java
CompletableFuture.supplyAsync(() -> saveToDb(data))
    .thenRun(() -> log.info("Save completed"));
```

- Input: nothing → Output: `Void`

#### `thenCompose` — Flat-map (chain dependent async calls)

```java
CompletableFuture<Order> orderFuture = CompletableFuture
    .supplyAsync(() -> getUserId(token))
    .thenCompose(userId -> CompletableFuture.supplyAsync(() -> getOrder(userId)));
```

- Use when the next stage itself returns a `CompletableFuture` — avoids `CompletableFuture<CompletableFuture<T>>`.
- **`thenApply` vs `thenCompose`** = `map` vs `flatMap` in streams.

### 3.4 Combining Multiple Futures

#### `thenCombine` — Combine two independent futures

```java
CompletableFuture<String> nameFuture  = CompletableFuture.supplyAsync(() -> fetchName(userId));
CompletableFuture<String> emailFuture = CompletableFuture.supplyAsync(() -> fetchEmail(userId));

CompletableFuture<String> combined = nameFuture.thenCombine(emailFuture,
    (name, email) -> name + " <" + email + ">");
```

#### `allOf` — Wait for ALL futures to complete

```java
CompletableFuture<Void> all = CompletableFuture.allOf(cf1, cf2, cf3);
all.thenRun(() -> {
    // all three are done — safe to call .join()
    String r1 = cf1.join();
    String r2 = cf2.join();
    String r3 = cf3.join();
});
```

- Returns `CompletableFuture<Void>` — you need to extract individual results via `join()`.

#### `anyOf` — Wait for the FIRST future to complete

```java
CompletableFuture<Object> fastest = CompletableFuture.anyOf(cf1, cf2, cf3);
fastest.thenAccept(result -> log.info("First result: {}", result));
```

- Returns `CompletableFuture<Object>` — result type is erased.

### 3.5 Exception Handling

#### `exceptionally` — Recover from exceptions

```java
CompletableFuture<String> safe = CompletableFuture
    .supplyAsync(() -> riskyOperation())
    .exceptionally(ex -> {
        log.error("Failed", ex);
        return "fallback-value";
    });
```

- Only invoked if the previous stage **throws**.

#### `handle` — Process result OR exception

```java
CompletableFuture<String> handled = CompletableFuture
    .supplyAsync(() -> riskyOperation())
    .handle((result, ex) -> {
        if (ex != null) {
            log.error("Error", ex);
            return "fallback";
        }
        return result.toUpperCase();
    });
```

- Always invoked, regardless of success or failure. Exactly **one** of `result` or `ex` is non-null.

#### `whenComplete` — Side-effect on completion (doesn't alter the result)

```java
CompletableFuture<String> logged = CompletableFuture
    .supplyAsync(() -> riskyOperation())
    .whenComplete((result, ex) -> {
        if (ex != null) log.error("Failed", ex);
        else log.info("Succeeded: {}", result);
    });
// The original result (or exception) is propagated unchanged.
```

### 3.6 Async Variants

Almost every method has three variants:

| Variant | Thread Used |
|---|---|
| `thenApply(fn)` | Same thread that completed the previous stage |
| `thenApplyAsync(fn)` | A thread from `ForkJoinPool.commonPool()` |
| `thenApplyAsync(fn, executor)` | A thread from the **specified** executor |

Use the `Async` variant when the callback is CPU-intensive or I/O-bound and you don't want to block the completing thread.

### 3.7 `join()` vs `get()`

| Method | Checked Exception? | Wrapping |
|---|---|---|
| `get()` | ✅ `InterruptedException`, `ExecutionException` | Wraps in `ExecutionException` |
| `join()` | ❌ Unchecked | Wraps in `CompletionException` |

Prefer `join()` in lambda chains because it doesn't force you to catch checked exceptions.

### 3.8 Real-World Example — Parallel API Aggregation

```java
ExecutorService ioPool = Executors.newFixedThreadPool(5);

CompletableFuture<UserProfile> profileFuture =
    CompletableFuture.supplyAsync(() -> userService.getProfile(userId), ioPool);

CompletableFuture<List<Order>> ordersFuture =
    CompletableFuture.supplyAsync(() -> orderService.getOrders(userId), ioPool);

CompletableFuture<WalletBalance> walletFuture =
    CompletableFuture.supplyAsync(() -> walletService.getBalance(userId), ioPool);

CompletableFuture<UserDashboard> dashboard = CompletableFuture
    .allOf(profileFuture, ordersFuture, walletFuture)
    .thenApply(ignored -> new UserDashboard(
        profileFuture.join(),
        ordersFuture.join(),
        walletFuture.join()
    ))
    .exceptionally(ex -> {
        log.error("Dashboard aggregation failed", ex);
        return UserDashboard.empty();
    });
```

All three API calls run **in parallel**. Once all complete, the results are composed into a single `UserDashboard`. If any fails, a fallback is returned.

---

## 4. Quick Reference Cheat Sheet

```
ThreadPoolExecutor Lifecycle
─────────────────────────────
RUNNING  →  SHUTDOWN  →  TIDYING  →  TERMINATED
              (no new      (queue      (terminated()
               tasks)      empty,       hook runs)
                           all tasks
                           finished)

shutdown()        — graceful; finishes queued tasks, rejects new ones
shutdownNow()     — aggressive; interrupts running tasks, drains queue
awaitTermination()— blocks until terminated or timeout

CompletableFuture Pipeline
──────────────────────────
supplyAsync(fn)              — start
  .thenApply(fn)             — transform    T → U
  .thenCompose(fn)           — flat-map     T → CF<U>
  .thenCombine(other, fn)    — merge        (T, U) → V
  .thenAccept(fn)            — consume      T → void
  .exceptionally(fn)         — recover      Throwable → T
  .handle((r, ex) -> ...)    — handle both
  .whenComplete((r, ex) -> …)— side-effect
  .join()                    — block & get result
```
