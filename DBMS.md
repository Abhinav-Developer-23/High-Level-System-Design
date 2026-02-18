# **MySQL Data Types**

MySQL provides a wide range of data types grouped into three main categories: **Numeric**, **String (Text)**, and **Date/Time**. Choosing the right data type is critical for storage efficiency, query performance, and data integrity.

---

## **Numeric Data Types**

### **Integer Types**

| Type | Storage | Range (Signed) | Range (Unsigned) |
| --- | --- | --- | --- |
| `TINYINT` | 1 byte | -128 to 127 | 0 to 255 |
| `SMALLINT` | 2 bytes | -32,768 to 32,767 | 0 to 65,535 |
| `MEDIUMINT` | 3 bytes | -8,388,608 to 8,388,607 | 0 to 16,777,215 |
| `INT` (or `INTEGER`) | 4 bytes | -2,147,483,648 to 2,147,483,647 | 0 to 4,294,967,295 |
| `BIGINT` | 8 bytes | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | 0 to 18,446,744,073,709,551,615 |
| `BOOL` / `BOOLEAN` | 1 byte | Synonym for `TINYINT(1)` | 0 = false, 1 = true |

**When to use:** Use `TINYINT` for small-range values like status flags, boolean-style columns, or age. Use `SMALLINT` for moderately small numbers like year or a limited counter. `INT` is the most commonly used integer type and works well for primary keys, counters, and general-purpose whole numbers. Reach for `BIGINT` only when you expect values to exceed the ~2 billion limit of `INT`, such as large-scale ID generators or financial transaction counts. Always pick the smallest type that safely fits your data to save storage.

**Signed vs Unsigned:** By default, integer columns are **signed** (allow negative values). Adding `UNSIGNED` after the type doubles the positive range by removing the negative half. Use `UNSIGNED` when a column can never be negative, like `age`, `quantity`, or auto-increment IDs. Example: `INT UNSIGNED` gives you 0 to ~4.3 billion instead of -2.1 billion to +2.1 billion.

### **Decimal / Floating-Point Types**

| Type | Storage | Range / Precision |
| --- | --- | --- |
| `FLOAT` | 4 bytes | -3.402823466E+38 to +3.402823466E+38 (~7 decimal digits precision) |
| `DOUBLE` (or `DOUBLE PRECISION`, `REAL`) | 8 bytes | -1.7976931348623157E+308 to +1.7976931348623157E+308 (~15 decimal digits precision) |
| `DECIMAL(M,D)` (or `DEC`, `NUMERIC`) | Varies (~4 bytes per 9 digits) | Exact precision, max range same as DOUBLE. M = up to 65 total digits, D = up to 30 decimal places |

**What does `DECIMAL(M,D)` mean?** `M` is the **total number of digits** (both sides of the decimal point combined), and `D` is the **number of digits after the decimal point**. So `DECIMAL(10,2)` means: up to 10 digits total, with 2 after the decimal point. The digits before the decimal = `M - D` = 8 digits, giving you a range of `-99,999,999.99` to `99,999,999.99`. If you insert `49.99`, MySQL stores exactly `49.99` with no approximation or binary conversion. Storage varies: roughly 4 bytes per 9 digits (e.g., `DECIMAL(10,2)` uses about 5 bytes). `M` can go up to 65, and `D` can go up to 30 (but `D` must always be less than or equal to `M`).

**Common declarations:**

| Declaration | Meaning | Range | Use Case |
|---|---|---|---|
| `DECIMAL(10,2)` | 8 digits before decimal, 2 after | -99,999,999.99 to 99,999,999.99 | Product prices, order totals |
| `DECIMAL(15,4)` | 11 digits before, 4 after | -99,999,999,999.9999 to 99,999,999,999.9999 | Banking, financial calculations |
| `DECIMAL(18,8)` | 10 digits before, 8 after | Up to 9,999,999,999.99999999 | Cryptocurrency (satoshi precision) |
| `DECIMAL(5,2)` | 3 digits before, 2 after | -999.99 to 999.99 | Percentages, small amounts |

**How is it different from FLOAT/DOUBLE internally?** `FLOAT` and `DOUBLE` convert your number to **binary (base-2)** using IEEE 754. The number `0.1` cannot be represented exactly in binary, just like `1/3` cannot be represented exactly in base-10, so you get tiny errors (`0.1 + 0.2 = 0.30000000000000004`). `DECIMAL` skips binary entirely and stores each digit **as-is in base-10**, so `0.1` is stored as exactly `0.1`. This is why `DECIMAL` is the only safe choice for money.

**When to use:** Use `DECIMAL` (also known as `NUMERIC`) whenever you need exact precision, especially for financial data like prices, salaries, and account balances — it stores numbers as exact values and avoids rounding errors. Use `FLOAT` or `DOUBLE` for scientific calculations, measurements, or any scenario where a small degree of approximation is acceptable and performance matters more than pinpoint accuracy. `DOUBLE` gives you more precision than `FLOAT` at the cost of double the storage.

---

### **Handling Prices in Production — The Recurring Decimal Problem**

Storing prices seems simple until you run into cases like:

- A bill of **$100 split 3 ways** → $33.333333... (recurring)
- **Tax calculation:** $49.99 × 7.25% = $3.624275 (needs rounding)
- **Currency conversion:** 100 USD × 0.8333... EUR/USD (recurring)
- **Discount:** 10% off $9.99 = $0.999 (needs rounding)

These aren't edge cases — they happen in every e-commerce system, every day. Let's look at how production systems actually handle this.

#### The Core Problem: Why Do Recurring Decimals Exist?

Not every fraction can be represented exactly in decimal. `1/3 = 0.333...` goes on forever. When you store this in a `DECIMAL(10,2)` column, MySQL **truncates or rounds** to `0.33`. That missing `$0.003333...` per person, over millions of transactions, adds up.

```sql
-- Splitting $100 three ways
SELECT 100 / 3;
-- Result: 33.3333  (MySQL default 4 decimal places)

SELECT CAST(100 / 3 AS DECIMAL(10,2));
-- Result: 33.33

-- But 33.33 × 3 = 99.99 — where did the missing $0.01 go?
```

#### Never Use FLOAT or DOUBLE for Money

Before we solve recurring decimals, let's understand why `FLOAT`/`DOUBLE` are completely unacceptable for financial data:

```sql
-- FLOAT horror show
CREATE TABLE bad_prices (price FLOAT);
INSERT INTO bad_prices VALUES (0.1), (0.2);

SELECT SUM(price) FROM bad_prices;
-- Expected: 0.3
-- Actual:   0.30000000447034836  ← WRONG

-- DECIMAL does this correctly
CREATE TABLE good_prices (price DECIMAL(10,2));
INSERT INTO good_prices VALUES (0.1), (0.2);

SELECT SUM(price) FROM good_prices;
-- Result: 0.30  ← CORRECT
```

`FLOAT` and `DOUBLE` use **binary floating-point** (IEEE 754), which cannot represent `0.1` exactly in binary — just like `1/3` can't be represented exactly in decimal. `DECIMAL` stores each digit as-is (base-10), so `0.1` is stored as exactly `0.1`.

**Rule: Always use `DECIMAL` for money. No exceptions.**

#### Production Strategy 1: Store Prices in Smallest Currency Unit as INT (Most Common)

The most widely used approach in production (Stripe, Shopify, Amazon) is to **avoid decimals entirely** by storing amounts in the **smallest currency unit** (cents, paise, etc.) as an integer.

```sql
-- Instead of this:
CREATE TABLE orders (
    price DECIMAL(10,2)    -- $49.99
);

-- Do this:
CREATE TABLE orders (
    price_cents INT         -- 4999 (meaning $49.99)
);
```

**Why this works:**

| Aspect | DECIMAL(10,2) | INT (cents) |
|---|---|---|
| Stores $49.99 as | `49.99` | `4999` |
| Stores $100.00 as | `100.00` | `10000` |
| Recurring decimal risk | Still possible in calculations | Eliminated — all values are whole numbers |
| Arithmetic precision | Exact for storage, rounding needed for division | Exact — integer math has no precision loss |
| Performance | Slightly slower (variable-length) | Faster — fixed 4 bytes, native CPU operations |

**How the split-the-bill problem is solved with cents:**

```sql
-- $100.00 = 10000 cents, split 3 ways
SELECT 10000 DIV 3;          -- Result: 3333 (integer division, no decimals)
-- 3333 cents = $33.33

-- But 3333 * 3 = 9999 cents = $99.99 — still 1 cent missing!
-- Solution: assign the remainder to the last person
```

```java
int totalCents = 10000;
int people = 3;
int perPerson = totalCents / people;         // 3333
int remainder = totalCents % people;         // 1

// Person 1: 3333 cents ($33.33)
// Person 2: 3333 cents ($33.33)
// Person 3: 3333 + 1 = 3334 cents ($33.34)  ← gets the extra cent
// Total: 3333 + 3333 + 3334 = 10000
```

This is called the **"last person absorbs the remainder"** pattern. It's simple, deterministic, and accounts for every cent.

**Display conversion (cents to dollars) happens only in the presentation layer:**

```java
int priceCents = 4999;

// Only convert for display
String display = String.format("$%.2f", priceCents / 100.0);  // "$49.99"

// API response
// { "price": 4999, "currency": "USD", "display": "$49.99" }
```

#### Production Strategy 2: DECIMAL with Controlled Rounding

If you need to store fractional amounts (e.g., crypto prices, unit rates), use `DECIMAL` with **more precision than you display** and round explicitly.

```sql
-- Store with extra precision (4 decimal places)
CREATE TABLE products (
    unit_price DECIMAL(12,4)    -- $33.3333
);

-- Round to 2 decimal places only at the final step
SELECT ROUND(unit_price, 2) AS display_price FROM products;
-- 33.3333 becomes 33.33
```

**The key rule: carry extra precision through calculations, round only at the end.**

```sql
-- Bad: round at each step (error accumulates)
SET @subtotal = ROUND(33.33, 2);                  -- 33.33
SET @tax = ROUND(@subtotal * 0.0725, 2);          -- 2.42
SET @total = @subtotal + @tax;                     -- 35.75

-- Good: round only at the final result
SET @subtotal = 33.3333;                           -- keep precision
SET @tax = @subtotal * 0.0725;                     -- 2.41666...
SET @total = ROUND(@subtotal + @tax, 2);           -- 35.75
```

#### Production Strategy 3: Banker's Rounding (For Financial Systems)

Standard rounding (`ROUND_HALF_UP`) always rounds `0.5` up: `2.5 becomes 3`, `3.5 becomes 4`. Over millions of transactions, this introduces a systematic upward bias.

**Banker's rounding** (`ROUND_HALF_EVEN`) rounds `0.5` to the nearest **even** number: `2.5 becomes 2`, `3.5 becomes 4`. Over many transactions, the rounding errors cancel out statistically.

```
Standard rounding:     2.5 -> 3,  3.5 -> 4,  4.5 -> 5,  5.5 -> 6   (always up)
Banker's rounding:     2.5 -> 2,  3.5 -> 4,  4.5 -> 4,  5.5 -> 6   (alternates)
```

MySQL's `ROUND()` function uses **banker's rounding by default** for exact-value types (`DECIMAL`):

```sql
SELECT ROUND(2.5);   -- 2  (rounds to even)
SELECT ROUND(3.5);   -- 4  (rounds to even)
SELECT ROUND(4.5);   -- 4  (rounds to even)
SELECT ROUND(5.5);   -- 6  (rounds to even)
```

In Java/Spring Boot, use `BigDecimal` with explicit rounding mode:

```java
BigDecimal price = new BigDecimal("33.3333");

// Banker's rounding
BigDecimal rounded = price.setScale(2, RoundingMode.HALF_EVEN);  // 33.33

// Standard rounding
BigDecimal roundedUp = price.setScale(2, RoundingMode.HALF_UP);  // 33.33
```

#### What Real Companies Do

| Company / Domain | Strategy | How They Store Price |
|---|---|---|
| **Stripe** | Integer cents | `amount: 4999` (INT, always in smallest unit) |
| **Shopify** | Integer cents | `price_cents: 4999` (INT) |
| **Amazon** | Integer cents | All internal calculations in cents |
| **Banks** | DECIMAL with banker's rounding | `DECIMAL(15,4)` with `ROUND_HALF_EVEN` |
| **Crypto exchanges** | DECIMAL with high precision | `DECIMAL(18,8)` for satoshi-level precision |
| **Accounting software** | DECIMAL + remainder allocation | `DECIMAL(12,4)` internally, round at invoice level |

#### Quick Decision Guide for Prices

| Scenario | Recommended Approach |
|---|---|
| E-commerce (USD, EUR, etc.) | `INT` in cents — simplest, no precision bugs |
| Multi-currency with variable decimals | `BIGINT` in smallest unit + `currency` column (JPY has 0 decimals, BHD has 3) |
| Financial / banking calculations | `DECIMAL(15,4)` + banker's rounding at final step |
| Cryptocurrency | `DECIMAL(18,8)` or `DECIMAL(24,8)` |
| Bill splitting, tax proration | `INT` in cents + remainder allocation to last line item |

> **The golden rule:** Never store money as `FLOAT` or `DOUBLE`. Prefer `INT` (cents) for most applications. Use `DECIMAL` with extra precision when you genuinely need fractional amounts. Always round at the **last possible step**, never during intermediate calculations.

---

### **Bit Type**

| Type | Storage |
| --- | --- |
| `BIT(M)` | ~(M+7)/8 bytes |

**When to use:** Use `BIT` when you need to store binary bit-field values, such as a set of on/off flags packed into a single column.

---

## **String (Text) Data Types**

### **Character Types**

| Type | Max Length | Storage |
| --- | --- | --- |
| `CHAR(M)` | 255 characters | Fixed-length (M bytes) |
| `VARCHAR(M)` | 65,535 characters | Variable-length (data + 1-2 bytes) |

**What does `VARCHAR(255)` mean?** The number inside the parentheses is **not** the number of bytes — it is the **maximum number of characters** you are allowing that column to hold. So `VARCHAR(255)` means "this column can store a string up to 255 characters long." If you insert `'Hello'` (5 characters), MySQL only stores those 5 characters plus a 1-byte length prefix — it does **not** pad it to 255. The `255` is simply a ceiling; it tells MySQL to reject any value longer than 255 characters. You can pick any number from 1 to 65,535 (e.g., `VARCHAR(50)`, `VARCHAR(100)`, `VARCHAR(2000)`), and you should choose a limit that reflects the realistic maximum for that data. The reason `255` is so commonly seen is historical — at 255 or below, the length prefix costs only 1 byte; at 256 and above, it costs 2 bytes. This 1-byte saving is negligible today, so pick a limit based on your data, not convention.

**When to use:** Use `CHAR` for fixed-length strings where every row has the same length, such as country codes (`CHAR(2)`), state abbreviations, or MD5 hashes (`CHAR(32)`) — it is slightly faster for lookups because of its predictable size. Use `VARCHAR` for variable-length strings like names, email addresses, and URLs where the length differs from row to row. `VARCHAR` saves storage by only using as much space as the actual data requires plus a small length prefix.

### **Text Types**

| Type | Max Length |
| --- | --- |
| `TINYTEXT` | 255 bytes |
| `TEXT` | 65,535 bytes (~64 KB) |
| `MEDIUMTEXT` | 16,777,215 bytes (~16 MB) |
| `LONGTEXT` | 4,294,967,295 bytes (~4 GB) |

**When to use:** Use `TEXT` types when you need to store large blocks of text that exceed `VARCHAR`'s practical limits, such as blog post bodies, comments, descriptions, or articles. Use `TINYTEXT` for short notes, `TEXT` for typical content fields, `MEDIUMTEXT` for large documents, and `LONGTEXT` for extremely large data like book manuscripts or serialized JSON blobs. Keep in mind that `TEXT` columns cannot have default values and are stored off-page, which can impact query performance — so prefer `VARCHAR` when the data fits within its limits.

---

### **VARCHAR vs TEXT — Deep Comparison**

This is one of the most common decisions developers face. Both store variable-length strings, but they behave very differently under the hood.

### **Storage Mechanism**

| Aspect | `VARCHAR(M)` | `TEXT` |
| --- | --- | --- |
| **Where data lives** | Stored **inline** with the row on the same data page (as long as the row fits within the page size). | Stored **off-page** — the row holds a 20-byte pointer, and the actual text lives on separate overflow pages. (InnoDB may store small `TEXT` values inline if they fit, but treats them as off-page candidates.) |
| **Length prefix** | 1 byte if M ≤ 255, 2 bytes if M > 255. | Always a 2-byte length prefix (for `TEXT`), up to 4 bytes for `LONGTEXT`. |
| **Max declared size** | Up to 65,535 bytes *shared across the entire row*. If you have other columns, the effective max for `VARCHAR` shrinks. | Each `TEXT` variant has its own fixed max (64 KB for `TEXT`, 16 MB for `MEDIUMTEXT`, 4 GB for `LONGTEXT`) independent of other columns. |
| **Memory for temp tables** | When MySQL needs an in-memory temporary table (e.g., for `ORDER BY`, `GROUP BY`, `DISTINCT`), `VARCHAR` columns are allocated at their **declared max length** in the MEMORY engine. A `VARCHAR(10000)` allocates 10 KB per row even if most values are 50 bytes. | `TEXT` columns **force the temporary table to disk** (MyISAM-based temp table), because the MEMORY engine does not support `TEXT`/`BLOB` types at all. |
| **Row size contribution** | Directly counted toward the InnoDB 8 KB page row-size limit. | Only the pointer (~20 bytes) counts toward the row size, so you can have many `TEXT` columns without hitting the row limit. |

### **When to Use VARCHAR**

- The data length is **predictable and bounded** — names (max ~100 chars), emails (max ~320 chars), URLs (max ~2,000 chars), short descriptions.
- You need to set a **DEFAULT value** — `TEXT` columns cannot have a `DEFAULT` in most MySQL versions.
- You want the **best query performance** — inline storage means fewer disk seeks; the data is right there in the row.
- You need to use the column in a **`GROUP BY`, `ORDER BY`, or `DISTINCT`** frequently — `VARCHAR` keeps temp tables in memory, which is much faster than spilling to disk.
- You want to create a **full-length index** on the column — `VARCHAR` columns can be indexed on their entire length (up to the index size limit), whereas `TEXT` requires a **prefix index** (e.g., `INDEX(col(255))`), which limits index effectiveness.
- You want to use the column in a **`MEMORY` table** or the **`MEMORY` storage engine** — `TEXT` is not supported there.

### **When to Use TEXT**

- The data length is **unpredictable or very large** — blog posts, user comments, article bodies, HTML content, log messages.
- You have **many variable-length columns** in a single table and are hitting the row-size limit (~65,535 bytes). Switching some to `TEXT` offloads them off-page and keeps the row compact.
- You **rarely query, sort, or filter** by this column — it is mostly written and then read back as-is (e.g., a `body` column you display on a page).
- The content can realistically be **larger than a few KB per row**.

### **Pros and Cons Summary**

|  | VARCHAR | TEXT |
| --- | --- | --- |
| **Pros** | Inline storage = faster reads. Supports `DEFAULT` values. Full-length indexing. Keeps temp tables in memory. Better for `WHERE`, `ORDER BY`, `GROUP BY`. | No impact on row-size limit. Can store very large strings. Good for write-heavy "dump and retrieve" columns. |
| **Cons** | Eats into the shared row-size budget. Declared max length wastes memory in temp tables if set too high. | Forces temp tables to disk. Requires prefix indexes only. No `DEFAULT` value. Off-page storage adds an extra I/O hop. |

### **Practical Rule of Thumb**

> If the maximum realistic length is **under ~1,000 characters** and you will query/sort/filter on it, use **`VARCHAR`**. If the content is free-form, unbounded, or regularly **over a few KB**, and you mostly just store and retrieve it, use **`TEXT`**. Never use `VARCHAR(65535)` "just in case" — you get the worst of both worlds (huge memory allocation for temp tables, yet still constrained by row size). Switch to `TEXT` at that point.
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

**When to use:** Use `BINARY` and `VARBINARY` for small fixed or variable-length binary data like UUIDs stored in raw form or hashed passwords. Use `BLOB` types to store binary large objects such as images, audio files, PDFs, or serialized objects directly in the database. In practice, it is often better to store large files on the filesystem or an object store and keep only a reference path in the database, but `BLOB` types are there when direct storage is necessary.

### **Enum and Set**

| Type | Description |
| --- | --- |
| `ENUM('val1','val2',...)` | A string object with one value from a predefined list |
| `SET('val1','val2',...)` | A string object that can have zero or more values from a predefined list |

**When to use:** Use `ENUM` when a column should only ever contain one value from a small, fixed list — such as status (`'active'`, `'inactive'`, `'pending'`), gender, or t-shirt size. It is stored internally as an integer, making it space-efficient and fast. Use `SET` when a column can hold multiple values simultaneously from a list, like user permissions (`'read'`, `'write'`, `'delete'`). Be cautious with both: changing the allowed values requires an `ALTER TABLE`, which can be expensive on large tables. If the list of values changes frequently, a separate lookup table with a foreign key is often a better design.

---

## **Date and Time Data Types**

| Type | Format | Range |
| --- | --- | --- |
| `DATE` | `YYYY-MM-DD` | 1000-01-01 to 9999-12-31 |
| `TIME` | `HH:MM:SS` | -838:59:59 to 838:59:59 |
| `DATETIME` | `YYYY-MM-DD HH:MM:SS` | 1000-01-01 00:00:00 to 9999-12-31 23:59:59 |
| `TIMESTAMP` | `YYYY-MM-DD HH:MM:SS` | 1970-01-01 00:00:01 UTC to 2038-01-19 03:14:07 UTC |
| `YEAR` | `YYYY` | 1901 to 2155 |

**When to use:** Use `DATE` when you only care about the calendar date — birthdays, hire dates, or due dates. Use `TIME` for storing durations or time-of-day values independent of a specific date. Use `DATETIME` for general-purpose date-and-time storage such as appointment scheduling, event dates, or log entries where you want to record an absolute point in time as entered by the user. Use `TIMESTAMP` for audit columns like `created_at` and `updated_at` — it automatically converts to and from UTC, making it ideal for applications serving users across multiple time zones, and it supports auto-initialization and auto-update. Note that `TIMESTAMP` has a limited range ending in 2038, so use `DATETIME` for dates beyond that. Use `YEAR` when you only need to store a four-digit year, such as a graduation year or model year.

---

## **JSON Data Type**

| Type | Max Size |
| --- | --- |
| `JSON` | ~4 GB (same as `LONGTEXT`) |

**When to use:** Use the `JSON` type when you need to store semi-structured or schema-less data — such as API payloads, configuration objects, user preferences, or metadata that varies between rows. MySQL validates the JSON on insert, and provides functions like `JSON_EXTRACT()`, `->`, and `->>` for querying nested values directly. It is a great fit when the data structure is flexible, but avoid it as a replacement for properly normalized relational columns when the fields are consistent across rows, since querying and indexing JSON is less efficient than querying regular columns.

---

## **Spatial Data Types**

| Type | Description |
| --- | --- |
| `GEOMETRY` | Any type of spatial value |
| `POINT` | A single location (X, Y) |
| `LINESTRING` | A curve of connected points |
| `POLYGON` | A closed shape |
| `MULTIPOINT`, `MULTILINESTRING`, `MULTIPOLYGON`, `GEOMETRYCOLLECTION` | Collections of the above |

**When to use:** Use spatial data types when you are building location-aware applications — store coordinates, map boundaries, delivery zones, or geographic regions. Combined with spatial indexes and functions like `ST_Distance()` and `ST_Contains()`, they enable efficient geospatial queries such as "find all restaurants within 5 km." If you only need to store a simple latitude/longitude pair without spatial queries, two `DECIMAL` columns may be simpler.

---

## **Quick Decision Guide**

| Scenario | Recommended Type |
| --- | --- |
| Primary key / auto-increment ID | `INT` or `BIGINT` |
| True/false flag | `TINYINT(1)` or `BOOLEAN` |
| Money / currency | `INT` (cents) or `DECIMAL(10,2)` |
| Short label (fixed length) | `CHAR` |
| Name, email, URL | `VARCHAR` |
| Blog post body | `TEXT` or `MEDIUMTEXT` |
| Image or file | `BLOB` (or store path as `VARCHAR`) |
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

---

# Cursors & Cursor-Based Pagination in MySQL

MySQL uses the word "cursor" in two very different contexts. Understanding both is important.

---

## 1. SQL Cursors (Stored Procedure Feature)

MySQL has a built-in `CURSOR` keyword for use inside **stored procedures**. It lets you iterate over a result set **row by row**, similar to a for-each loop in application code.

```sql
DELIMITER //
CREATE PROCEDURE process_pending_messages()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE msg_id VARCHAR(50);
    DECLARE msg_content TEXT;

    -- Declare a cursor over a query
    DECLARE msg_cursor CURSOR FOR
        SELECT message_id, content FROM messages WHERE status = 'pending';

    -- Handler that sets `done = TRUE` when no more rows
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN msg_cursor;

    read_loop: LOOP
        FETCH msg_cursor INTO msg_id, msg_content;
        IF done THEN LEAVE read_loop; END IF;

        -- Process each row (e.g., mark as processed)
        UPDATE messages SET status = 'processed' WHERE message_id = msg_id;
    END LOOP;

    CLOSE msg_cursor;
END //
DELIMITER ;
```

### Key Points

| Aspect | Detail |
|---|---|
| **Where it works** | Only inside stored procedures / functions |
| **What it does** | Iterates a result set one row at a time on the server side |
| **Read-only?** | Yes — MySQL cursors are **read-only** and **forward-only** (you cannot go backwards or update via the cursor) |
| **When to use** | Batch processing, row-by-row transformations, data migration scripts |
| **When NOT to use** | Pagination, APIs, anything client-facing — SQL cursors live entirely on the database server |

> **Important:** SQL cursors are a **server-side database feature**. They have nothing to do with API pagination. Don't confuse the two.

---

## 2. Cursor-Based Pagination (API Pattern)

MySQL doesn't have a native "pagination cursor" like Cassandra's paging state, but you can implement the same **cursor-based pagination pattern** using a `WHERE` clause on an indexed column.

### The Problem with Offset Pagination

```sql
-- Page 1: fast
SELECT * FROM messages WHERE conversation_id = 'conv_123'
ORDER BY created_at DESC LIMIT 50 OFFSET 0;

-- Page 100: slow — MySQL scans and discards 5,000 rows
SELECT * FROM messages WHERE conversation_id = 'conv_123'
ORDER BY created_at DESC LIMIT 50 OFFSET 5000;

-- Page 10,000: very slow — scans and discards 500,000 rows
SELECT * FROM messages WHERE conversation_id = 'conv_123'
ORDER BY created_at DESC LIMIT 50 OFFSET 500000;
```

`OFFSET` forces MySQL to **read and throw away** all the skipped rows. Performance degrades linearly with the offset value.

### The Solution: Cursor-Based Pagination in MySQL

Instead of skipping rows, use the **last seen value** from the previous page as a cursor:

```sql
-- Page 1: no cursor, fetch the newest messages
SELECT message_id, sender_id, content, created_at
FROM messages
WHERE conversation_id = 'conv_123'
ORDER BY message_id DESC
LIMIT 50;
-- Returns msg_200 ... msg_151
-- Cursor for next page = msg_151 (the last/oldest ID in this batch)

-- Page 2: use cursor
SELECT message_id, sender_id, content, created_at
FROM messages
WHERE conversation_id = 'conv_123'
  AND message_id < 'msg_151'          -- ← cursor
ORDER BY message_id DESC
LIMIT 50;
-- Returns msg_150 ... msg_101
-- Cursor for next page = msg_101

-- Page 3: use new cursor
SELECT message_id, sender_id, content, created_at
FROM messages
WHERE conversation_id = 'conv_123'
  AND message_id < 'msg_101'          -- ← cursor
ORDER BY message_id DESC
LIMIT 50;
```

### Why This Is Fast

MySQL uses the **B-tree index** on `message_id` to **seek directly** to the cursor position. It doesn't scan or discard any rows. Whether you're fetching page 2 or page 2,000, the cost is the same — O(limit).

**Required index for this to work efficiently:**

```sql
-- Composite index that covers the query
CREATE INDEX idx_conv_msg ON messages (conversation_id, message_id DESC);
```

Without this index, MySQL falls back to a full table scan, and cursor pagination loses its advantage.

### Offset vs Cursor — Side-by-Side

| Factor | `OFFSET` Pagination | Cursor Pagination |
|---|---|---|
| **Page 1 speed** | Fast | Fast |
| **Page 1,000 speed** | Slow (scans 50,000 rows) | Fast (index seek) |
| **New rows inserted between pages** | Causes duplicates or missed rows | Stable — cursor anchors to a fixed point |
| **Can jump to arbitrary page?** | Yes (`?page=50`) | No — must traverse sequentially |
| **Index requirement** | Index helps but `OFFSET` still scans | **Must** have index on cursor column |
| **Best for** | Small datasets, admin panels | Large/growing datasets, APIs, feeds, chat |

### How the API Server Builds the Cursor

The cursor is **not stored in MySQL**. It's derived from the query results:

```
1. Server runs:  SELECT ... ORDER BY message_id DESC LIMIT 50
2. Gets back:    [msg_200, msg_199, ..., msg_151]
3. Takes the LAST item:  msg_151
4. Encodes it:   base64('{"msg_id":"msg_151"}')  →  "eyJtc2dfaWQiOiJtc2dfMTUxIn0="
5. Returns to client:
   {
     "data": [ ... 50 rows ... ],
     "next_cursor": "eyJtc2dfaWQiOiJtc2dfMTUxIn0=",
     "has_more": true
   }
```

The cursor is base64-encoded to keep it **opaque** — the client doesn't need to know the internal format. The server can change the cursor structure (e.g., add a timestamp field) without breaking any client.

### Spring Boot / JPA Example

```java
@Repository
public interface MessageRepository extends JpaRepository<Message, String> {

    // First page (no cursor)
    @Query("SELECT m FROM Message m WHERE m.conversationId = :convId ORDER BY m.messageId DESC")
    List<Message> findFirstPage(@Param("convId") String convId, Pageable pageable);

    // Next page (with cursor)
    @Query("SELECT m FROM Message m WHERE m.conversationId = :convId AND m.messageId < :cursor ORDER BY m.messageId DESC")
    List<Message> findNextPage(@Param("convId") String convId, @Param("cursor") String cursor, Pageable pageable);
}
```

```java
@Service
public class MessageService {

    @Autowired
    private MessageRepository messageRepository;

    public CursorPage<Message> getMessages(String conversationId, String cursor, int limit) {
        List<Message> messages;

        if (cursor == null) {
            messages = messageRepository.findFirstPage(conversationId, PageRequest.of(0, limit));
        } else {
            String decodedCursor = decodeCursor(cursor);  // base64 → msg_id
            messages = messageRepository.findNextPage(conversationId, decodedCursor, PageRequest.of(0, limit));
        }

        String nextCursor = messages.size() == limit
            ? encodeCursor(messages.get(messages.size() - 1).getMessageId())  // last item's ID
            : null;

        return new CursorPage<>(messages, nextCursor, messages.size() == limit);
    }
}
```

---

## SQL Cursor vs Cursor-Based Pagination — Quick Comparison

| | SQL Cursor (`DECLARE CURSOR`) | Cursor-Based Pagination (`WHERE id < ?`) |
|---|---|---|
| **What it is** | Database feature for row-by-row iteration | API design pattern for efficient paging |
| **Where it runs** | Inside stored procedures on the DB server | Application code / API layer |
| **Scope** | Server-side only — never exposed to clients | Client-facing — cursor token travels in API responses |
| **Performance** | Fine for batch jobs; not for real-time APIs | Designed for low-latency, high-scale APIs |
| **Use case** | Data migration, batch processing | Chat history, feeds, search results, logs |