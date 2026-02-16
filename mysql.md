# **MySQL Data Types**

MySQL provides a wide range of data types grouped into three main categories: **Numeric**, **String (Text)**, and **Date/Time**. Choosing the right data type is critical for storage efficiency, query performance, and data integrity.

---

## **Numeric Data Types**

### **Integer Types**

| Type | Storage | Range (Signed) |
| --- | --- | --- |
| `TINYINT` | 1 byte | -128 to 127 |
| `SMALLINT` | 2 bytes | -32,768 to 32,767 |
| `MEDIUMINT` | 3 bytes | -8,388,608 to 8,388,607 |
| `INT` (or `INTEGER`) | 4 bytes | -2,147,483,648 to 2,147,483,647 |
| `BIGINT` | 8 bytes | -9.2 quintillion to 9.2 quintillion |

**When to use:** Use `TINYINT` for small-range values like status flags, boolean-style columns, or age. Use `SMALLINT` for moderately small numbers like year or a limited counter. `INT` is the most commonly used integer type and works well for primary keys, counters, and general-purpose whole numbers. Reach for `BIGINT` only when you expect values to exceed the ~2 billion limit of `INT`, such as large-scale ID generators or financial transaction counts. Always pick the smallest type that safely fits your data to save storage.

### **Decimal / Floating-Point Types**

| Type | Storage | Precision |
| --- | --- | --- |
| `FLOAT` | 4 bytes | ~7 decimal digits |
| `DOUBLE` | 8 bytes | ~15 decimal digits |
| `DECIMAL(M,D)` | Varies | Exact precision (user-defined) |

**When to use:** Use `DECIMAL` (also known as `NUMERIC`) whenever you need exact precision, especially for financial data like prices, salaries, and account balances — it stores numbers as exact values and avoids rounding errors. Use `FLOAT` or `DOUBLE` for scientific calculations, measurements, or any scenario where a small degree of approximation is acceptable and performance matters more than pinpoint accuracy. `DOUBLE` gives you more precision than `FLOAT` at the cost of double the storage.

### **Bit Type**

| Type | Storage |
| --- | --- |
| `BIT(M)` | ~(M+7)/8 bytes |

**When to use:** Use `BIT` when you need to store binary bit-field values, such as a set of on/off flags packed into a single column.

---

## **String (Text) Data Types**

### **Character Types**

| Type | Max Length | Storage |
| --- | --- | --- |
| `CHAR(M)` | 255 characters | Fixed-length (M bytes) |
| `VARCHAR(M)` | 65,535 characters | Variable-length (data + 1-2 bytes) |

**What does `VARCHAR(255)` mean?** The number inside the parentheses is **not** the number of bytes — it is the **maximum number of characters** you are allowing that column to hold. So `VARCHAR(255)` means "this column can store a string up to 255 characters long." If you insert `'Hello'` (5 characters), MySQL only stores those 5 characters plus a 1-byte length prefix — it does **not** pad it to 255. The `255` is simply a ceiling; it tells MySQL to reject any value longer than 255 characters. You can pick any number from 1 to 65,535 (e.g., `VARCHAR(50)`, `VARCHAR(100)`, `VARCHAR(2000)`), and you should choose a limit that reflects the realistic maximum for that data. The reason `255` is so commonly seen is historical — at 255 or below, the length prefix costs only 1 byte; at 256 and above, it costs 2 bytes. This 1-byte saving is negligible today, so pick a limit based on your data, not convention.

**When to use:** Use `CHAR` for fixed-length strings where every row has the same length, such as country codes (`CHAR(2)`), state abbreviations, or MD5 hashes (`CHAR(32)`) — it is slightly faster for lookups because of its predictable size. Use `VARCHAR` for variable-length strings like names, email addresses, and URLs where the length differs from row to row. `VARCHAR` saves storage by only using as much space as the actual data requires plus a small length prefix.

### **Text Types**

| Type | Max Length |
| --- | --- |
| `TINYTEXT` | 255 bytes |
| `TEXT` | 65,535 bytes (~64 KB) |
| `MEDIUMTEXT` | 16,777,215 bytes (~16 MB) |
| `LONGTEXT` | 4,294,967,295 bytes (~4 GB) |

**When to use:** Use `TEXT` types when you need to store large blocks of text that exceed `VARCHAR`'s practical limits, such as blog post bodies, comments, descriptions, or articles. Use `TINYTEXT` for short notes, `TEXT` for typical content fields, `MEDIUMTEXT` for large documents, and `LONGTEXT` for extremely large data like book manuscripts or serialized JSON blobs. Keep in mind that `TEXT` columns cannot have default values and are stored off-page, which can impact query performance — so prefer `VARCHAR` when the data fits within its limits.

---

### **VARCHAR vs TEXT — Deep Comparison**

This is one of the most common decisions developers face. Both store variable-length strings, but they behave very differently under the hood.

### **Storage Mechanism**

| Aspect | `VARCHAR(M)` | `TEXT` |
| --- | --- | --- |
| **Where data lives** | Stored **inline** with the row on the same data page (as long as the row fits within the page size). | Stored **off-page** — the row holds a 20-byte pointer, and the actual text lives on separate overflow pages. (InnoDB may store small `TEXT` values inline if they fit, but treats them as off-page candidates.) |
| **Length prefix** | 1 byte if M ≤ 255, 2 bytes if M > 255. | Always a 2-byte length prefix (for `TEXT`), up to 4 bytes for `LONGTEXT`. |
| **Max declared size** | Up to 65,535 bytes *shared across the entire row*. If you have other columns, the effective max for `VARCHAR` shrinks. | Each `TEXT` variant has its own fixed max (64 KB for `TEXT`, 16 MB for `MEDIUMTEXT`, 4 GB for `LONGTEXT`) independent of other columns. |
| **Memory for temp tables** | When MySQL needs an in-memory temporary table (e.g., for `ORDER BY`, `GROUP BY`, `DISTINCT`), `VARCHAR` columns are allocated at their **declared max length** in the MEMORY engine. A `VARCHAR(10000)` allocates 10 KB per row even if most values are 50 bytes. | `TEXT` columns **force the temporary table to disk** (MyISAM-based temp table), because the MEMORY engine does not support `TEXT`/`BLOB` types at all. |
| **Row size contribution** | Directly counted toward the InnoDB 8 KB page row-size limit. | Only the pointer (~20 bytes) counts toward the row size, so you can have many `TEXT` columns without hitting the row limit. |

### **When to Use VARCHAR**

- The data length is **predictable and bounded** — names (max ~100 chars), emails (max ~320 chars), URLs (max ~2,000 chars), short descriptions.
- You need to set a **DEFAULT value** — `TEXT` columns cannot have a `DEFAULT` in most MySQL versions.
- You want the **best query performance** — inline storage means fewer disk seeks; the data is right there in the row.
- You need to use the column in a **`GROUP BY`, `ORDER BY`, or `DISTINCT`** frequently — `VARCHAR` keeps temp tables in memory, which is much faster than spilling to disk.
- You want to create a **full-length index** on the column — `VARCHAR` columns can be indexed on their entire length (up to the index size limit), whereas `TEXT` requires a **prefix index** (e.g., `INDEX(col(255))`), which limits index effectiveness.
- You want to use the column in a **`MEMORY` table** or the **`MEMORY` storage engine** — `TEXT` is not supported there.

### **When to Use TEXT**

- The data length is **unpredictable or very large** — blog posts, user comments, article bodies, HTML content, log messages.
- You have **many variable-length columns** in a single table and are hitting the row-size limit (~65,535 bytes). Switching some to `TEXT` offloads them off-page and keeps the row compact.
- You **rarely query, sort, or filter** by this column — it is mostly written and then read back as-is (e.g., a `body` column you display on a page).
- The content can realistically be **larger than a few KB per row**.

### **Pros and Cons Summary**

|  | VARCHAR | TEXT |
| --- | --- | --- |
| **Pros** | Inline storage = faster reads. Supports `DEFAULT` values. Full-length indexing. Keeps temp tables in memory. Better for `WHERE`, `ORDER BY`, `GROUP BY`. | No impact on row-size limit. Can store very large strings. Good for write-heavy "dump and retrieve" columns. |
| **Cons** | Eats into the shared row-size budget. Declared max length wastes memory in temp tables if set too high. | Forces temp tables to disk. Requires prefix indexes only. No `DEFAULT` value. Off-page storage adds an extra I/O hop. |

### **Practical Rule of Thumb**

> If the maximum realistic length is **under ~1,000 characters** and you will query/sort/filter on it, use **`VARCHAR`**. If the content is free-form, unbounded, or regularly **over a few KB**, and you mostly just store and retrieve it, use **`TEXT`**. Never use `VARCHAR(65535)` "just in case" — you get the worst of both worlds (huge memory allocation for temp tables, yet still constrained by row size). Switch to `TEXT` at that point.
> 

---

### **Binary Types**

| Type | Max Length |
| --- | --- |
| `BINARY(M)` | 255 bytes (fixed) |
| `VARBINARY(M)` | 65,535 bytes (variable) |
| `TINYBLOB` | 255 bytes |
| `BLOB` | 65,535 bytes (~64 KB) |
| `MEDIUMBLOB` | 16,777,215 bytes (~16 MB) |
| `LONGBLOB` | 4,294,967,295 bytes (~4 GB) |

**When to use:** Use `BINARY` and `VARBINARY` for small fixed or variable-length binary data like UUIDs stored in raw form or hashed passwords. Use `BLOB` types to store binary large objects such as images, audio files, PDFs, or serialized objects directly in the database. In practice, it is often better to store large files on the filesystem or an object store and keep only a reference path in the database, but `BLOB` types are there when direct storage is necessary.

### **Enum and Set**

| Type | Description |
| --- | --- |
| `ENUM('val1','val2',...)` | A string object with one value from a predefined list |
| `SET('val1','val2',...)` | A string object that can have zero or more values from a predefined list |

**When to use:** Use `ENUM` when a column should only ever contain one value from a small, fixed list — such as status (`'active'`, `'inactive'`, `'pending'`), gender, or t-shirt size. It is stored internally as an integer, making it space-efficient and fast. Use `SET` when a column can hold multiple values simultaneously from a list, like user permissions (`'read'`, `'write'`, `'delete'`). Be cautious with both: changing the allowed values requires an `ALTER TABLE`, which can be expensive on large tables. If the list of values changes frequently, a separate lookup table with a foreign key is often a better design.

---

## **Date and Time Data Types**

| Type | Format | Range |
| --- | --- | --- |
| `DATE` | `YYYY-MM-DD` | 1000-01-01 to 9999-12-31 |
| `TIME` | `HH:MM:SS` | -838:59:59 to 838:59:59 |
| `DATETIME` | `YYYY-MM-DD HH:MM:SS` | 1000-01-01 00:00:00 to 9999-12-31 23:59:59 |
| `TIMESTAMP` | `YYYY-MM-DD HH:MM:SS` | 1970-01-01 00:00:01 UTC to 2038-01-19 03:14:07 UTC |
| `YEAR` | `YYYY` | 1901 to 2155 |

**When to use:** Use `DATE` when you only care about the calendar date — birthdays, hire dates, or due dates. Use `TIME` for storing durations or time-of-day values independent of a specific date. Use `DATETIME` for general-purpose date-and-time storage such as appointment scheduling, event dates, or log entries where you want to record an absolute point in time as entered by the user. Use `TIMESTAMP` for audit columns like `created_at` and `updated_at` — it automatically converts to and from UTC, making it ideal for applications serving users across multiple time zones, and it supports auto-initialization and auto-update. Note that `TIMESTAMP` has a limited range ending in 2038, so use `DATETIME` for dates beyond that. Use `YEAR` when you only need to store a four-digit year, such as a graduation year or model year.

---

## **JSON Data Type**

| Type | Max Size |
| --- | --- |
| `JSON` | ~4 GB (same as `LONGTEXT`) |

**When to use:** Use the `JSON` type when you need to store semi-structured or schema-less data — such as API payloads, configuration objects, user preferences, or metadata that varies between rows. MySQL validates the JSON on insert, and provides functions like `JSON_EXTRACT()`, `->`, and `->>` for querying nested values directly. It is a great fit when the data structure is flexible, but avoid it as a replacement for properly normalized relational columns when the fields are consistent across rows, since querying and indexing JSON is less efficient than querying regular columns.

---

## **Spatial Data Types**

| Type | Description |
| --- | --- |
| `GEOMETRY` | Any type of spatial value |
| `POINT` | A single location (X, Y) |
| `LINESTRING` | A curve of connected points |
| `POLYGON` | A closed shape |
| `MULTIPOINT`, `MULTILINESTRING`, `MULTIPOLYGON`, `GEOMETRYCOLLECTION` | Collections of the above |

**When to use:** Use spatial data types when you are building location-aware applications — store coordinates, map boundaries, delivery zones, or geographic regions. Combined with spatial indexes and functions like `ST_Distance()` and `ST_Contains()`, they enable efficient geospatial queries such as "find all restaurants within 5 km." If you only need to store a simple latitude/longitude pair without spatial queries, two `DECIMAL` columns may be simpler.

---

## **Quick Decision Guide**

| Scenario | Recommended Type |
| --- | --- |
| Primary key / auto-increment ID | `INT` or `BIGINT` |
| True/false flag | `TINYINT(1)` or `BOOLEAN` |
| Money / currency | `DECIMAL(10,2)` |
| Short label (fixed length) | `CHAR` |
| Name, email, URL | `VARCHAR` |
| Blog post body | `TEXT` or `MEDIUMTEXT` |
| Image or file | `BLOB` (or store path as `VARCHAR`) |
| Status with fixed options | `ENUM` |
| Date only | `DATE` |
| Created/updated timestamps | `TIMESTAMP` |
| Flexible metadata | `JSON` |
| GPS coordinates with spatial queries | `POINT` |

---

# Locking & Concurrency Control in MySQL

When multiple transactions try to read and update the same row at the same time, you can end up with **lost updates**, **dirty reads**, or **inconsistent data**. MySQL provides several mechanisms to handle this. Below are the main approaches, each illustrated with real-world examples from an **Inventory Management System** and a **Banking Transaction System**.

---

## 1. Pessimistic Locking (`SELECT ... FOR UPDATE`)

**How it works:** You explicitly lock the row(s) when you read them. Any other transaction that tries to read the same row with `FOR UPDATE` (or tries to update it) will **block and wait** until the first transaction commits or rolls back. This is called "pessimistic" because you assume a conflict *will* happen, so you lock preemptively.

### Inventory Example — Purchasing the Last Item

Two customers try to buy the last unit of a product at the same time.

```sql
-- Transaction A (Customer 1)
START TRANSACTION;

-- Lock the row — no one else can modify it until we commit
SELECT quantity FROM products WHERE product_id = 101 FOR UPDATE;
-- Returns: quantity = 1

-- Quantity is enough, proceed with purchase
UPDATE products SET quantity = quantity - 1 WHERE product_id = 101;
INSERT INTO orders (customer_id, product_id, qty) VALUES (1, 101, 1);

COMMIT;

-- Transaction B (Customer 2) — runs concurrently
START TRANSACTION;

-- This BLOCKS here, waiting for Transaction A to finish
SELECT quantity FROM products WHERE product_id = 101 FOR UPDATE;
-- After A commits, returns: quantity = 0

-- Quantity is 0 — cannot fulfil, inform customer
ROLLBACK;
```

**What happens without the lock?** Both transactions would read `quantity = 1` simultaneously, both would decrement it, and you'd end up with `quantity = -1` — selling stock you don't have.

### Bank Example — Transferring Money Between Accounts

Transfer $500 from Account A to Account B.

```sql
START TRANSACTION;

-- Always lock in a consistent order (lower ID first) to avoid deadlocks
SELECT balance FROM accounts WHERE account_id = 1001 FOR UPDATE;
-- Returns: balance = 2000

SELECT balance FROM accounts WHERE account_id = 1002 FOR UPDATE;
-- Returns: balance = 500

-- Check sufficient funds
-- 2000 >= 500 ✓

UPDATE accounts SET balance = balance - 500 WHERE account_id = 1001;
UPDATE accounts SET balance = balance + 500 WHERE account_id = 1002;

INSERT INTO transactions (from_acc, to_acc, amount) VALUES (1001, 1002, 500);

COMMIT;
```

**Key tip:** When locking multiple rows, always lock them in a **consistent order** (e.g., by ascending `account_id`). If Transaction A locks account 1001 then 1002, and Transaction B locks 1002 then 1001, they will **deadlock** — each waiting for the other to release.

#### What are START TRANSACTION, COMMIT, and ROLLBACK?

Think of a **transaction** as a protective wrapper around a group of SQL statements that says: "Either **all** of these succeed together, or **none** of them happen."

| Command | What it does |
|---------|-------------|
| `START TRANSACTION` | Opens the wrapper. From this point, nothing you do is made permanent yet — it's all tentative. Other connections **cannot see** your uncommitted changes (depending on isolation level). |
| `COMMIT` | Closes the wrapper and **saves everything permanently**. All the `INSERT`, `UPDATE`, `DELETE` statements inside the transaction are now final and visible to everyone. Locks are released. |
| `ROLLBACK` | Closes the wrapper and **throws everything away**. The database goes back to exactly how it was before `START TRANSACTION`. Locks are released. |

**Why does this matter?** In the bank transfer above, you debit Account A and credit Account B. If MySQL crashes *after* the debit but *before* the credit, without a transaction the money simply vanishes. With a transaction, either both happen or neither happens — this is the **Atomicity** guarantee in ACID.

**What is auto-commit?** By default, MySQL runs in **auto-commit** mode — every single SQL statement is its own mini-transaction that immediately commits. When you explicitly say `START TRANSACTION`, you turn off auto-commit for that session until you `COMMIT` or `ROLLBACK`.

#### How to Achieve This in Spring Boot + JPA (Hibernate)

In a Spring application, you almost **never** write `START TRANSACTION` or `COMMIT` manually. Spring's `@Transactional` annotation handles it for you.

**1. The `@Transactional` Annotation (Most Common)**

```java
@Service
public class TransferService {

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private TransactionRepository transactionRepository;

    @Transactional  // ← This is your START TRANSACTION + COMMIT/ROLLBACK
    public void transferMoney(Long fromId, Long toId, BigDecimal amount) {

        // Lock rows using FOR UPDATE (via JPA query)
        Account from = accountRepository.findByIdForUpdate(fromId);
        Account to   = accountRepository.findByIdForUpdate(toId);

        if (from.getBalance().compareTo(amount) < 0) {
            throw new InsufficientFundsException("Not enough balance");
            // ↑ Any exception = automatic ROLLBACK, nothing is saved
        }

        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));

        accountRepository.save(from);
        accountRepository.save(to);

        transactionRepository.save(new BankTransaction(fromId, toId, amount));

        // ← Method ends normally = automatic COMMIT
    }
}
```

**What Spring does behind the scenes:**
1. Before `transferMoney()` runs → Spring calls `START TRANSACTION`
2. Your method executes all the JPA operations
3. Method returns normally → Spring calls `COMMIT`
4. Method throws a runtime exception → Spring calls `ROLLBACK`

**2. The Repository — `FOR UPDATE` in JPA**

```java
@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {

    // The PESSIMISTIC_WRITE lock = SELECT ... FOR UPDATE
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    Account findByIdForUpdate(@Param("id") Long id);

    // For OPTIMISTIC locking, use:
    // @Lock(LockModeType.OPTIMISTIC)
}
```

**3. The Entity**

```java
@Entity
@Table(name = "accounts")
public class Account {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private BigDecimal balance;

    @Version  // ← For optimistic locking (auto-managed version column)
    private Integer version;

    // getters and setters
}
```

**4. Key `@Transactional` Options**

```java
// Read-only transaction (optimizes performance, no dirty checking)
@Transactional(readOnly = true)
public Account getAccount(Long id) { ... }

// Custom isolation level
@Transactional(isolation = Isolation.SERIALIZABLE)
public void criticalOperation() { ... }

// Custom timeout (seconds) — auto-rollback if exceeded
@Transactional(timeout = 5)
public void timeSensitiveOperation() { ... }

// Specify which exceptions trigger rollback
@Transactional(rollbackFor = Exception.class)        // rollback on ALL exceptions
@Transactional(noRollbackFor = MailException.class)   // don't rollback for this one
```

**5. JPA Lock Modes Mapped to MySQL**

| JPA Lock Mode | MySQL Equivalent | When to Use |
|---------------|-----------------|-------------|
| `PESSIMISTIC_WRITE` | `SELECT ... FOR UPDATE` | You will modify the row — block everyone else |
| `PESSIMISTIC_READ` | `SELECT ... LOCK IN SHARE MODE` | You need to ensure the row doesn't change, but you won't modify it |
| `OPTIMISTIC` | No SQL lock — checks `@Version` on flush | Low contention, retry-friendly scenarios |
| `OPTIMISTIC_FORCE_INCREMENT` | No SQL lock — increments `@Version` even on read | Force a version bump to signal "this was touched" |

#### Common Mistakes to Avoid in Spring

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| Calling a `@Transactional` method from **within the same class** | Spring proxies don't intercept self-calls — no transaction is started | Extract the method to a separate `@Service` class |
| Catching exceptions inside the method silently | Spring never sees the exception, so it **commits** instead of rolling back | Let exceptions propagate, or call `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()` |
| Using `@Transactional` on a **private** method | Spring AOP proxies can't intercept private methods | Make the method `public` |
| Long-running logic inside a transaction | Holds locks and DB connections for too long | Keep transactions short — do non-DB work (API calls, file I/O) outside the `@Transactional` method |

**Pros:**
- Guarantees no conflicting updates — strongest safety
- Simple mental model: lock, read, write, commit

**Cons:**
- Blocks other transactions — reduces throughput under high concurrency
- Risk of **deadlocks** if lock ordering is not consistent
- Holding locks for long transactions hurts performance

---

## 2. Optimistic Locking (Application-Level Version Check)

**How it works:** You do **not** lock the row when reading. Instead, you include a `version` (or `updated_at` timestamp) column. When updating, you check that the version hasn't changed since you read it. If it has, someone else modified the row first — your update affects 0 rows, and you know to retry. This is called "optimistic" because you assume conflicts are **rare**.

### Inventory Example — Two Warehouse Staff Updating Stock

```sql
-- Table structure
-- products (product_id, name, quantity, version)

-- Staff Member A reads the product
SELECT quantity, version FROM products WHERE product_id = 101;
-- Returns: quantity = 50, version = 3

-- Staff Member B also reads it (at the same time)
SELECT quantity, version FROM products WHERE product_id = 101;
-- Returns: quantity = 50, version = 3

-- Staff A updates (adding 20 units from a shipment)
UPDATE products
SET quantity = 70, version = version + 1
WHERE product_id = 101 AND version = 3;
-- ✅ Affected rows = 1 → Success! version is now 4

-- Staff B tries to update (removing 10 units for a dispatch)
UPDATE products
SET quantity = 40, version = version + 1
WHERE product_id = 101 AND version = 3;
-- ❌ Affected rows = 0 → version is no longer 3!
-- B knows the row was modified — must re-read and retry

-- Staff B retries
SELECT quantity, version FROM products WHERE product_id = 101;
-- Returns: quantity = 70, version = 4

UPDATE products
SET quantity = 60, version = version + 1
WHERE product_id = 101 AND version = 4;
-- ✅ Affected rows = 1 → Success!
```

### Bank Example — Concurrent Withdrawals

```sql
-- accounts (account_id, balance, version)

-- ATM 1: Customer tries to withdraw 300
SELECT balance, version FROM accounts WHERE account_id = 1001;
-- Returns: balance = 1000, version = 5

-- ATM 2: Same customer, different ATM, tries to withdraw 800
SELECT balance, version FROM accounts WHERE account_id = 1001;
-- Returns: balance = 1000, version = 5

-- ATM 1 processes first
UPDATE accounts
SET balance = balance - 300, version = version + 1
WHERE account_id = 1001 AND version = 5;
-- ✅ Affected rows = 1 → balance is now 700, version = 6

-- ATM 2 tries to process
UPDATE accounts
SET balance = balance - 800, version = version + 1
WHERE account_id = 1001 AND version = 5;
-- ❌ Affected rows = 0 → version mismatch!
-- ATM 2 re-reads: balance = 700 — not enough for 800 withdrawal
-- Transaction declined. No overdraft.
```

**Pros:**
- No blocking — great throughput under low-to-moderate contention
- No deadlocks
- Works well in distributed systems and APIs (version can travel in HTTP ETags)

**Cons:**
- Requires a `version` or `updated_at` column on every table
- Under **high contention**, many retries can happen — worse performance than just locking
- Application must handle the retry logic

---

## 3. Atomic Updates (No Explicit Lock Needed)

**How it works:** Instead of reading a value into the application and then writing back a new value, you do the math **directly in the SQL statement**. Because a single `UPDATE` statement is atomic in InnoDB, MySQL internally acquires a row lock for the duration of that single statement, preventing a race condition — and you don't need to manage locks yourself.

### Inventory Example — Decrement Stock on Purchase

```sql
-- ❌ Bad: read-then-write race condition
SELECT quantity FROM products WHERE product_id = 101;  -- App reads 10
-- Another transaction could change it here!
UPDATE products SET quantity = 10 - 1 WHERE product_id = 101;

-- ✅ Good: atomic in-place update
UPDATE products
SET quantity = quantity - 1
WHERE product_id = 101 AND quantity >= 1;

-- Check affected rows:
-- 1 → purchase succeeded
-- 0 → out of stock, no negative inventory possible
```

### Bank Example — Atomic Withdrawal

```sql
-- Single atomic statement: debit only if sufficient balance
UPDATE accounts
SET balance = balance - 500
WHERE account_id = 1001 AND balance >= 500;

-- Affected rows = 1 → withdrawal succeeded
-- Affected rows = 0 → insufficient funds, no overdraft
```

**Pros:**
- Simplest approach — one statement, no version columns, no explicit locks
- Inherently safe against lost updates
- Great performance

**Cons:**
- Only works for simple operations (increment, decrement, set to computed value)
- Cannot handle complex business logic that requires reading multiple columns or rows before deciding what to write
- You don't get the "before" value unless you use a follow-up `SELECT` or `RETURNING` (MySQL 8.1+)

---

## 4. `LOCK IN SHARE MODE` (Shared / Read Lock)

**How it works:** Similar to `FOR UPDATE`, but instead of an exclusive lock, it places a **shared lock**. Multiple transactions can hold a shared lock on the same row simultaneously (so concurrent reads are fine), but no transaction can **write** to that row until all shared locks are released.

```sql
-- Use case: Validate that a referenced row exists and won't be deleted
-- while you insert a child record

START TRANSACTION;

-- Shared lock — others can also read, but nobody can delete/update this row
SELECT * FROM accounts WHERE account_id = 1001 LOCK IN SHARE MODE;

-- Safe to insert a transaction referencing this account
INSERT INTO transactions (account_id, amount, type) VALUES (1001, 200, 'DEPOSIT');

COMMIT;
```

**When to use:** When you need to ensure a row **exists and stays unchanged** while you do related work, but you don't need to modify that row yourself. It's lighter than `FOR UPDATE` because it doesn't block other readers.

---

## 5. Isolation Levels

MySQL's InnoDB engine supports four transaction isolation levels that control how much transactions "see" each other's uncommitted work. Choosing the right level is another way to manage concurrency.

| Level | Dirty Reads | Non-Repeatable Reads | Phantom Reads | Performance |
|-------|:-----------:|:--------------------:|:-------------:|:-----------:|
| `READ UNCOMMITTED` | Yes | Yes | Yes | Fastest |
| `READ COMMITTED` | No | Yes | Yes | Fast |
| `REPEATABLE READ` (default) | No | No | Possible* | Balanced |
| `SERIALIZABLE` | No | No | No | Slowest |

*\*InnoDB's `REPEATABLE READ` uses gap locks to prevent most phantom reads, making it safer than the SQL standard requires.*

```sql
-- Set for current session
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Or per transaction
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
START TRANSACTION;
-- ... your queries ...
COMMIT;
```

**Quick guidance:**
- **`READ COMMITTED`** — Use when you want to avoid dirty reads but can tolerate seeing new committed data mid-transaction. Common in high-throughput systems where some inconsistency is acceptable.
- **`REPEATABLE READ`** (default) — Good for most applications. Once you read a row, you see the same value throughout your transaction, even if others commit changes.
- **`SERIALIZABLE`** — Use when absolute correctness matters more than speed (e.g., financial reconciliation). Every `SELECT` automatically behaves like `LOCK IN SHARE MODE`.
- **`READ UNCOMMITTED`** — Rarely used. Only for rough analytics where speed matters and stale/dirty data is acceptable.

---

## Which Approach Should You Pick?

| Scenario | Recommended Approach |
|----------|---------------------|
| Simple increment/decrement (stock count, balance) | **Atomic Update** — fastest and simplest |
| Low-contention reads with occasional conflicts | **Optimistic Locking** — no blocking, retry on conflict |
| High-contention critical operations (payments, bookings) | **Pessimistic Locking** (`FOR UPDATE`) — guaranteed safety |
| Validate a parent row exists before inserting child | **`LOCK IN SHARE MODE`** — lightweight read lock |
| Entire transaction must see a perfectly consistent snapshot | **`SERIALIZABLE` isolation level** |
| Mixed workload in a typical web app | **`REPEATABLE READ`** (default) + **atomic updates** where possible |

### General Rule of Thumb

> Start with **atomic updates** for simple operations. If the logic is too complex for a single statement, try **optimistic locking** first. Fall back to **pessimistic locking** (`FOR UPDATE`) only when contention is high and retries are too costly. Use **isolation levels** as a global safety net underneath all of these.