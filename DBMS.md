# **MySQL Data Types**

MySQL provides a wide range of data types grouped into three main categories: **Numeric**, **String (Text)**, and **Date/Time**. Choosing the right data type is critical for storage efficiency, query performance, and data integrity.

---

## **Numeric Data Types**

### **Integer Types**

| Type                 | Storage | Range (Signed)                                          | Range (Unsigned)                |
| -------------------- | ------- | ------------------------------------------------------- | ------------------------------- |
| `TINYINT`            | 1 byte  | -128 to 127                                             | 0 to 255                        |
| `SMALLINT`           | 2 bytes | -32,768 to 32,767                                       | 0 to 65,535                     |
| `MEDIUMINT`          | 3 bytes | -8,388,608 to 8,388,607                                 | 0 to 16,777,215                 |
| `INT` (or `INTEGER`) | 4 bytes | -2,147,483,648 to 2,147,483,647                         | 0 to 4,294,967,295              |
| `BIGINT`             | 8 bytes | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | 0 to 18,446,744,073,709,551,615 |
| `BOOL` / `BOOLEAN`   | 1 byte  | Synonym for `TINYINT(1)`                                | 0 = false, 1 = true             |

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

---

# Indexes in MySQL (InnoDB)

An index is a **separate data structure** that MySQL maintains alongside your table data. Its sole purpose is to make finding rows **fast** — without an index, MySQL has no choice but to scan every single row in the table (a "full table scan") to answer your query. With the right index, MySQL can jump directly to the matching rows, the same way a book's index lets you jump to the exact page instead of reading the whole book.

Indexes are not free. They speed up reads but slow down writes, and they consume storage. Understanding **how** they work internally is the key to using them well.

---

## How a B+ Tree Works — The Engine Behind MySQL Indexes

Almost every index in InnoDB is a **B+ Tree** (a balanced, sorted tree optimized for disk-based storage). Understanding this structure is essential because it explains *why* indexes are fast for some queries and useless for others.

### Why Not a Simple Binary Search Tree?

A binary search tree (BST) stores one key per node and has two children. For a table with 1 million rows, a balanced BST would be ~20 levels deep (`log₂(1,000,000) ≈ 20`). Each level means a separate **disk read** (since nodes are scattered across disk), so finding one row = 20 disk I/Os. Disk seeks take ~5-10ms each, so a single lookup could take 100-200ms — unacceptable.

A B+ Tree solves this by being **wide and short**:

| Property | Binary Search Tree | B+ Tree (InnoDB) |
|---|---|---|
| Keys per node | 1 | Hundreds (fills a 16 KB page) |
| Children per node | 2 | Hundreds |
| Height for 1M rows | ~20 | **3-4** |
| Disk reads per lookup | ~20 | **3-4** |
| Data stored in | Every node | **Leaf nodes only** |

### The Structure: Internal Nodes vs Leaf Nodes

A B+ Tree has two types of nodes:

**1. Internal (non-leaf) nodes** — Act as signposts. They contain **keys** and **pointers to child nodes**, but no actual row data. Their only job is to route you to the correct leaf.

**2. Leaf nodes** — Contain the actual **indexed key values** plus either:
- The **full row data** (if this is the clustered/primary key index), or
- A **pointer to the row** (if this is a secondary index — the pointer is the primary key value)

All leaf nodes are connected in a **doubly linked list** — this is what makes range scans fast. Once you find the first matching leaf, you just walk sideways through the chain without going back up the tree.

### Visual Example: B+ Tree with Order 4

"Order 4" means each node can hold at most 3 keys and 4 child pointers. (InnoDB nodes are 16 KB pages that can hold hundreds of keys; we use small numbers here for clarity.)

Suppose we insert these employee IDs in order: `10, 20, 30, 40, 50, 60, 70, 80, 90`

The resulting B+ Tree looks like this:

```
                         [40, 70]                          ← Root (internal node)
                        /    |    \
                       /     |     \
              [10, 20, 30] [40, 50, 60] [70, 80, 90]       ← Leaf nodes (hold data)
                   ↔            ↔            ↔              ← Linked list connections
```

**How a lookup works — Find employee_id = 50:**

```
Step 1: Start at root [40, 70]
        → 50 >= 40 and 50 < 70
        → Follow the MIDDLE pointer

Step 2: Arrive at leaf [40, 50, 60]
        → Scan within this small node → Found 50!

Total: 2 disk reads (1 root page + 1 leaf page)
```

**How a range scan works — Find all employees WHERE id BETWEEN 30 AND 60:**

```
Step 1: Start at root [40, 70]
        → 30 < 40 → Follow LEFT pointer

Step 2: Arrive at leaf [10, 20, 30]
        → Start from 30
        → Follow linked list pointer →

Step 3: Arrive at leaf [40, 50, 60]
        → Read 40, 50, 60 → 60 is the upper bound, stop

Result: [30, 40, 50, 60] — found by reading only 3 pages
(No need to go back to the root for each value!)
```

### How Inserts and Splits Work — Step by Step

Understanding splits is crucial because they explain why B+ Trees stay balanced and why write performance has overhead.

**Starting with an empty tree (order 4, max 3 keys per node):**

**Insert 10, 20, 30** — they fit in a single leaf:

```
[10, 20, 30]    ← Root is also a leaf at this point
```

**Insert 40** — the leaf is full (has 3 keys), so it **splits**:

```
Split [10, 20, 30, 40] into two halves:
  Left leaf:  [10, 20]
  Right leaf: [30, 40]
  Promote middle key (30) up to a new root

Result:
           [30]               ← New root (internal node)
          /    \
   [10, 20]  [30, 40]         ← Leaf nodes
       ↔           
```

**Insert 50, 60** — 50 and 60 go into the right leaf (since > 30):

```
           [30]
          /    \
   [10, 20]  [30, 40, 50, 60]   ← This leaf now has 4 keys — OVERFLOW!
```

**Split the right leaf:**

```
Split [30, 40, 50, 60]:
  Left:  [30, 40]
  Right: [50, 60]
  Promote 50 up to the root

Result:
           [30, 50]
          /    |    \
   [10, 20] [30, 40] [50, 60]
       ↔        ↔         
```

**Insert 70, 80, 90** — following the same pattern, the tree keeps growing and splitting:

```
Final tree:
                         [40, 70]
                        /    |    \
              [10, 20, 30] [40, 50, 60] [70, 80, 90]
                   ↔            ↔            ↔
```

**Key observations about splits:**

| Aspect | What happens |
|---|---|
| **When** | A node overflows (exceeds max keys) |
| **What** | Node splits into two halves; middle key is promoted to parent |
| **Cost** | 3 page writes (left child, right child, parent) — this is the write overhead of B+ Trees |
| **Cascading** | If the parent also overflows, it splits too — can cascade up to the root |
| **Tree height increase** | Only increases when the **root** splits — always stays balanced |
| **Deletions** | Reverse of splits — nodes merge when they become less than half full |

### Real InnoDB Numbers

In production (with 16 KB pages and typical `BIGINT` keys):

| Metric | Approximate Value |
|---|---|
| Keys per internal page | ~1,200 |
| Rows per leaf page | ~500 (depends on row size) |
| Height for 1 million rows | **3** |
| Height for 1 billion rows | **4** |
| Disk reads for a point lookup | 2-4 (root is usually cached in memory) |

Because the root and first-level internal pages are almost always in the **buffer pool** (InnoDB's memory cache), a typical lookup in a well-configured database needs only **1 disk read** (the leaf page).

---

## Types of Indexes

### 1. Primary Key Index (Clustered Index)

In InnoDB, the **primary key IS the table**. The actual row data is stored in the leaf nodes of the primary key's B+ Tree. This is called a **clustered index** — the table data is physically ordered (clustered) by the primary key.

```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,      -- ← This IS the clustered index
    name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);
```

**What the B+ Tree looks like internally:**

```
Internal nodes: [50, 100]  — contain only IDs and page pointers

Leaf nodes (contain the FULL ROW):
  Page 1: [id=1, name='Alice', dept='Eng', salary=90000]
           [id=2, name='Bob',   dept='Sales', salary=75000]
           ...
  Page 2: [id=51, name='Carol', dept='Eng', salary=95000]
           ...
```

**Key facts:**
- Every InnoDB table has **exactly one** clustered index
- If you don't define a `PRIMARY KEY`, InnoDB uses the first `UNIQUE NOT NULL` index; if none exists, it creates a hidden 6-byte row ID as the clustered key
- Because data is physically sorted by primary key, **sequential primary key access is very fast** (data is in adjacent pages)
- Auto-increment IDs are ideal because new rows always append to the **end** of the tree — no splits in the middle, minimal page fragmentation

### 2. Unique Index

Enforces that no two rows can have the same value in the indexed column(s). Internally, it's the same B+ Tree structure as any other index, but MySQL checks for duplicates on every insert/update.

```sql
CREATE UNIQUE INDEX idx_email ON users (email);

-- Or inline:
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,         -- ← creates a unique index automatically
    username VARCHAR(50) UNIQUE
);
```

**When to use:** When you have a business rule that a column must contain distinct values — email, username, phone number, SSN. Beyond data integrity, unique indexes also help the optimizer: when MySQL knows a column is unique, it can stop searching after finding one match (`const` or `eq_ref` access type in `EXPLAIN`).

### 3. Composite (Multi-Column) Index

An index on **two or more columns**. The B+ Tree is sorted by the first column, then by the second column within rows that share the same first column, and so on — like a phone book sorted by last name, then first name.

```sql
CREATE INDEX idx_dept_salary ON employees (department, salary);
```

**How the B+ Tree is sorted:**

```
('Engineering', 70000)
('Engineering', 85000)
('Engineering', 95000)
('Marketing',   60000)
('Marketing',   72000)
('Sales',       55000)
('Sales',       68000)
('Sales',       90000)
```

**The Leftmost Prefix Rule** — this is the most important rule for composite indexes:

A composite index on `(A, B, C)` can be used for queries that filter on:
- `A` alone ✅
- `A` and `B` ✅
- `A` and `B` and `C` ✅
- `A` and `C` — partially ✅ (uses A, skips to data for C with less efficiency)

But it **cannot** be used for:
- `B` alone ❌
- `C` alone ❌
- `B` and `C` ❌

**Why?** Think of the phone book analogy. A phone book sorted by `(last_name, first_name)` can answer "find all Smiths" and "find Alice Smith", but it **cannot** answer "find all Alices" without scanning the entire book — because Alices are scattered across different last names.

```sql
-- ✅ Uses the index (leftmost prefix)
SELECT * FROM employees WHERE department = 'Engineering';
SELECT * FROM employees WHERE department = 'Engineering' AND salary > 80000;

-- ❌ Cannot use the index (skips the leftmost column)
SELECT * FROM employees WHERE salary > 80000;
```

**Practical rule:** Put the most frequently filtered column **first** in a composite index, and the column used for range/sorting **last**.

### 4. Full-Text Index

Designed for **natural language text search** — finding words or phrases inside `TEXT` or `VARCHAR` columns. Regular B+ Tree indexes are useless for `LIKE '%keyword%'` (leading wildcard prevents index usage). Full-text indexes use an **inverted index** internally: a mapping from each word to the list of rows that contain it.

```sql
CREATE FULLTEXT INDEX idx_ft_content ON articles (title, body);

-- Search for articles mentioning "database indexing"
SELECT * FROM articles
WHERE MATCH(title, body) AGAINST('database indexing');

-- Boolean mode — more control (+ means must include, - means must exclude)
SELECT * FROM articles
WHERE MATCH(title, body) AGAINST('+database +indexing -NoSQL' IN BOOLEAN MODE);
```

**When to use:** Blog search, product search, documentation search — anywhere you need to find rows containing specific words inside large text blocks. For more advanced search (fuzzy matching, synonyms, stemming, ranking), consider **Elasticsearch** or **Solr** instead of MySQL full-text.

### 5. Spatial Index (R-Tree)

Used for **geometry** and **geographic** data types (`POINT`, `POLYGON`, etc.). Spatial indexes use **R-Trees** (not B+ Trees) which partition multi-dimensional space into nested bounding rectangles.

```sql
CREATE SPATIAL INDEX idx_location ON stores (coordinates);

-- Find all stores within 5 km of a point
SELECT name FROM stores
WHERE ST_Distance_Sphere(coordinates, ST_GeomFromText('POINT(77.5946 12.9716)')) < 5000;
```

**When to use:** "Find nearest" queries, geofencing, delivery zone checks, map-based applications.

### 6. Hash Index (MEMORY Engine Only)

A hash index stores a **hash of the key** → row pointer mapping. Lookups are O(1) — instant for exact-match queries. But it **cannot** do range scans, sorting, or partial matches because hashing destroys order.

```sql
-- Only available with the MEMORY storage engine
CREATE TABLE sessions (
    session_id VARCHAR(64),
    user_id INT,
    data TEXT,
    INDEX USING HASH (session_id)
) ENGINE = MEMORY;
```

**InnoDB does NOT support explicit hash indexes**, but it has an **Adaptive Hash Index (AHI)** — InnoDB automatically detects "hot" B+ Tree pages that are accessed very frequently and builds an in-memory hash index on top of them. You don't create this manually; InnoDB manages it transparently.

| Index Type | Structure | Equality | Range | Sorting | Partial Match |
|---|---|---|---|---|---|
| B+ Tree (default) | Sorted tree | ✅ | ✅ | ✅ | ✅ (prefix only) |
| Hash | Hash table | ✅ (O(1)) | ❌ | ❌ | ❌ |
| Full-Text | Inverted index | Words only | ❌ | By relevance | ✅ (words) |
| Spatial (R-Tree) | Bounding rectangles | ❌ | Spatial only | ❌ | ❌ |

---

## When to Use an Index

### ✅ Index These Columns

| Column Type | Why |
|---|---|
| **Primary key** | Automatically indexed; defines the clustered index |
| **Foreign keys** | MySQL needs them for `JOIN` performance and `ON DELETE CASCADE` checks — without an index, every FK check triggers a full table scan on the child table |
| **Columns in `WHERE` clauses** | Equality (`=`), range (`>`, `<`, `BETWEEN`), and `IN` filters all benefit |
| **Columns in `JOIN ON` conditions** | Indexes on both sides of a join condition dramatically reduce lookup time |
| **Columns in `ORDER BY`** | Avoids an expensive filesort — data is already sorted in the index |
| **Columns in `GROUP BY`** | Allows MySQL to group rows by reading the index in order |
| **High-cardinality columns** | Columns with many distinct values (e.g., `email`, `order_id`) are ideal for indexes |
| **Columns used in `UNIQUE` constraints** | Automatically indexed; also enables the optimizer to stop after one match |

### ❌ Do NOT Index These

| Column Type | Why |
|---|---|
| **Low-cardinality columns** | A `gender` column with only `M` and `F` has terrible selectivity — an index on it would still match ~50% of rows, making a full scan cheaper |
| **Columns you rarely query on** | An index no one uses just wastes storage and slows down writes |
| **Very wide columns** | A `VARCHAR(5000)` index entry is huge — use a prefix index or reconsider |
| **Frequently updated columns** | Every `UPDATE` to an indexed column means updating the index B+ Tree too |
| **Small tables** | A table with 100 rows is faster to full-scan than to use an index (disk seek for the index + disk seek for the row > sequential scan of 100 rows) |
| **Columns with lots of NULLs** (usually) | Depends on the use case, but indexes on mostly-NULL columns are often wasteful |

---

## How Indexes Are Used in Common Operations

### 1. Point Lookups (Equality Queries)

The most basic use case. MySQL walks down the B+ Tree to find the exact matching leaf node.

```sql
-- Uses PRIMARY KEY index (1-2 page reads)
SELECT * FROM employees WHERE id = 42;

-- Uses index on email (2-3 page reads for index + 1 for row data)
SELECT * FROM users WHERE email = 'alice@example.com';
```

**Without index:** Full table scan — reads every single row. O(N).
**With index:** B+ Tree seek. O(log N) — in practice, 2-4 disk reads.

### 2. Range Queries

This is where the B+ Tree's **linked list at the leaf level** shines. MySQL seeks to the starting point, then walks the linked list forward (or backward) until the range boundary.

```sql
-- Find all orders placed in January 2025
SELECT * FROM orders
WHERE order_date BETWEEN '2025-01-01' AND '2025-01-31';

-- Find all products priced between $50 and $100
SELECT * FROM products WHERE price >= 50 AND price <= 100;

-- Find all employees with salary > 100000
SELECT * FROM employees WHERE salary > 100000;
```

**How it works with an index on `order_date`:**

```
Step 1: B+ Tree seek to '2025-01-01'         → Find its leaf page
Step 2: Walk the linked list forward          → Read all entries sequentially
Step 3: Stop when you hit '2025-02-01'        → Done

Only reads the pages containing matching rows — skips everything else.
```

**Without index:** MySQL reads the **entire table** and checks every row's `order_date`. If the table has 10 million rows and only 50,000 match, it still reads all 10 million.

### 3. Sorting (`ORDER BY`)

If the `ORDER BY` column matches an index, MySQL reads the data **in index order** — it's already sorted, so no additional sort step is needed. Without an index, MySQL must load all matching rows into memory (or a temp file) and perform a **filesort**, which is slow for large result sets.

```sql
-- With index on (created_at):
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20;
-- MySQL reads the LAST 20 entries from the B+ Tree's leaf linked list
-- No sorting needed — data comes out pre-sorted

-- Without index:
-- MySQL reads ALL posts, sorts them by created_at in memory, returns top 20
-- If there are millions of posts, this is extremely expensive
```

**EXPLAIN tells you:** If you see `Using filesort` in the Extra column, MySQL is sorting in memory/disk instead of using an index. This is a red flag for large tables.

```sql
-- Composite indexes can satisfy ORDER BY too:
CREATE INDEX idx_user_date ON posts (user_id, created_at);

-- ✅ Index used for both WHERE and ORDER BY
SELECT * FROM posts WHERE user_id = 5 ORDER BY created_at DESC;

-- ❌ Index CANNOT help here — different column order than index
SELECT * FROM posts WHERE user_id = 5 ORDER BY title;
```

### 4. JOINs

Joins are where indexes provide the most dramatic performance improvement. Without indexes, MySQL must use a **Nested Loop Join** with full table scans — for every row in table A, it scans every row in table B. That's O(N × M).

```sql
-- Without indexes on the join columns:
SELECT o.order_id, c.name, o.total
FROM orders o
JOIN customers c ON o.customer_id = c.id;

-- For 100,000 orders × 50,000 customers = 5 BILLION comparisons 🔥
```

**With an index on `customers.id` (the primary key) and an index on `orders.customer_id`:**

```sql
-- MySQL can use Nested Loop Join efficiently:
-- For each order, do a B+ Tree lookup on customers.id → 3-4 page reads
-- 100,000 orders × 4 page reads = 400,000 page reads (vs 5 billion comparisons)
```

**Different join types and how indexes help:**

| Join Scenario | Without Index | With Index |
|---|---|---|
| `JOIN ON a.id = b.foreign_id` | Full scan of `b` for every row in `a` | B+ Tree seek on `b.foreign_id` per row |
| `JOIN ... WHERE a.col > 100` | Full scan + filter | Index range scan, then join |
| Multi-table `JOIN` (3+ tables) | Exponentially worse | Indexes on all join columns keep it manageable |

**Always index both sides of a join:**

```sql
-- Make sure BOTH columns involved in the join have indexes:
CREATE INDEX idx_customer_id ON orders (customer_id);
-- customers.id is already indexed (it's the primary key)
```

### 5. GROUP BY

If the `GROUP BY` column has an index, MySQL can group rows by reading the index in order — no need to hash or sort. This is called a **"loose index scan"** or **"tight index scan"** depending on the query.

```sql
-- With index on (department):
SELECT department, COUNT(*), AVG(salary)
FROM employees
GROUP BY department;
-- MySQL reads the index in order: all 'Engineering' rows together, then all 'Marketing', etc.
-- No temporary table or filesort needed

-- With composite index on (department, salary):
SELECT department, MAX(salary)
FROM employees
GROUP BY department;
-- "Loose index scan" — MySQL reads only the LAST entry in each department group
-- (because the index is sorted by department, then salary within each department)
-- Incredibly fast — barely reads any data
```

**EXPLAIN tells you:** Look for `Using index for group-by` (loose index scan) — this is the best case. If you see `Using temporary; Using filesort`, the GROUP BY is not using an index.

### 6. DISTINCT

`DISTINCT` is essentially the same operation as `GROUP BY` from MySQL's perspective. If the column has an index, MySQL reads sorted values and skips duplicates naturally.

```sql
-- With index on (department):
SELECT DISTINCT department FROM employees;
-- MySQL walks the index, reading only the first entry of each group
-- Equivalent to a loose index scan
```

### 7. Aggregate Functions (MIN, MAX)

`MIN()` and `MAX()` on an indexed column are **O(1)** — MySQL just reads the first or last entry in the B+ Tree.

```sql
-- With index on (salary):
SELECT MIN(salary) FROM employees;   -- Read the leftmost leaf → instant
SELECT MAX(salary) FROM employees;   -- Read the rightmost leaf → instant

-- Without index: full table scan to find min/max → O(N)
```

**EXPLAIN shows** `Select tables optimized away` — meaning MySQL answered the query from the index metadata without reading any table rows at all.

### 8. LIKE Queries (Prefix Only)

B+ Tree indexes can help with `LIKE` queries **only when the wildcard is at the end** (prefix search). A leading wildcard destroys the ability to use the index because the B+ Tree is sorted from the left.

```sql
-- ✅ Uses index (prefix search — B+ Tree can seek to 'Joh' and walk forward)
SELECT * FROM users WHERE name LIKE 'Joh%';

-- ❌ Cannot use B+ Tree index (leading wildcard — must scan everything)
SELECT * FROM users WHERE name LIKE '%son';

-- ❌ Cannot use B+ Tree index (wildcard on both sides)
SELECT * FROM users WHERE name LIKE '%ohn%';

-- For the ❌ cases above, use a FULLTEXT index instead:
CREATE FULLTEXT INDEX idx_ft_name ON users (name);
SELECT * FROM users WHERE MATCH(name) AGAINST('son');
```

### 9. Subqueries and EXISTS

Indexes on the correlated column make `EXISTS` and `IN` subqueries efficient.

```sql
-- With index on orders.customer_id:
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);
-- For each customer, MySQL does a quick B+ Tree lookup on orders.customer_id
-- instead of scanning the entire orders table

-- IN with subquery:
SELECT * FROM products
WHERE category_id IN (SELECT id FROM categories WHERE active = 1);
-- Index on categories.id (primary key) and products.category_id
```

### 10. UNION and Deduplication

When using `UNION` (which removes duplicates) vs `UNION ALL` (which doesn't), MySQL needs to sort and deduplicate the combined result. Indexes on the selected columns can speed up this deduplication.

---

## Covering Indexes and Index-Only Scans

A **covering index** is an index that contains **all the columns** a query needs — so MySQL can answer the query entirely from the index, without ever reading the actual table row. This is called an **index-only scan** and it's the fastest possible read path.

### Why It's Fast

Normally, a secondary index lookup has **two steps**:
1. Walk the secondary index B+ Tree to find the matching primary key
2. Use that primary key to walk the **primary key B+ Tree** (clustered index) to fetch the full row

This second step is called a **"bookmark lookup"** or **"clustered index lookup"** — it's an extra disk read per row.

A covering index eliminates step 2 entirely. All the data the query needs is right there in the index's leaf nodes.

```sql
-- Index on (department, salary)
CREATE INDEX idx_dept_salary ON employees (department, salary);

-- ✅ Covering index — all requested columns (department, salary) are IN the index
SELECT department, salary FROM employees WHERE department = 'Engineering';
-- MySQL reads ONLY the index, never touches the table data pages
-- EXPLAIN shows: "Using index" in Extra column

-- ❌ NOT a covering index — 'name' is NOT in the index
SELECT department, salary, name FROM employees WHERE department = 'Engineering';
-- MySQL must look up each matching row in the clustered index to get 'name'
```

### INCLUDE Columns (MySQL 8.0+ Functional Equivalent)

MySQL doesn't have a formal `INCLUDE` keyword (SQL Server/PostgreSQL do), but you can simulate it by adding columns to the end of a composite index. The extra columns are stored in the index but not used for sorting — they just "come along for the ride" to make the index covering.

```sql
-- Make the index covering for queries that also need 'name'
CREATE INDEX idx_dept_salary_name ON employees (department, salary, name);

-- Now this is a covering index:
SELECT department, salary, name FROM employees WHERE department = 'Engineering';
```

**Trade-off:** Wider indexes use more storage and are slower to maintain on writes. Only add columns to make an index covering if the query is critical and frequent.

### How to Know if Your Query Uses a Covering Index

Run `EXPLAIN` and look at the `Extra` column:

| Extra Value | Meaning |
|---|---|
| `Using index` | ✅ Covering index — data read from index only |
| `Using index condition` | Index used for filtering, but table data still accessed |
| (nothing about index) | Index may or may not be used; table rows are being read |

---

## Index Selectivity and Cardinality

**Cardinality** = the number of **distinct values** in a column.
**Selectivity** = cardinality / total rows — the percentage of distinct values.

| Column | Cardinality | Selectivity | Good for Indexing? |
|---|---|---|---|
| `id` (primary key) | 1,000,000 | 1.0 (100%) | ✅ Perfect |
| `email` | 999,950 | 0.999 (~100%) | ✅ Excellent |
| `created_at` (timestamp) | 800,000 | 0.8 (80%) | ✅ Very good |
| `country` | 195 | 0.000195 (0.02%) | ⚠️ Mediocre alone, fine in composite |
| `status` ('active'/'inactive') | 2 | 0.000002 (0.0002%) | ❌ Terrible — match 50% of rows |
| `is_deleted` (0/1) | 2 | 0.000002 | ❌ Terrible |
| `gender` ('M'/'F'/'O') | 3 | 0.000003 | ❌ Bad |

**Rule of thumb:** An index is useful when it can eliminate the vast majority of rows. If a query using an index still matches >20-30% of the table, MySQL's optimizer may choose a full table scan instead — because the random I/O of index lookups is more expensive than a sequential scan at that point.

**How to check cardinality:**

```sql
-- Shows cardinality for all indexes on a table
SHOW INDEX FROM employees;

-- More detailed statistics
SELECT
    INDEX_NAME,
    COLUMN_NAME,
    CARDINALITY,
    ROUND(CARDINALITY / (SELECT COUNT(*) FROM employees) * 100, 2) AS selectivity_pct
FROM information_schema.STATISTICS
WHERE TABLE_NAME = 'employees';
```

**Composite index selectivity:** In a composite index, put the **most selective column first** (the one that eliminates the most rows). However, if the less selective column is used in equality and the more selective one is used in a range, MySQL can still benefit from the less selective column being first.

```sql
-- If 'department' selects 5% and 'created_at' range selects 10%:
-- Better: (department, created_at) — equality first, range second
SELECT * FROM employees WHERE department = 'Eng' AND created_at > '2025-01-01';
```

---

## Impact on Write Performance

Every index is a separate B+ Tree that must be updated on every `INSERT`, `UPDATE` (of indexed columns), or `DELETE`. The cost is real and measurable.

### What Happens on Each Operation

| Operation | Impact on Indexes |
|---|---|
| **INSERT** | New entry must be added to **every** index's B+ Tree. For each index: find the correct leaf page, insert the key, potentially split the leaf if full. |
| **UPDATE** (indexed column) | Old key is deleted from the index, new key is inserted — effectively a **delete + insert** on each affected index. |
| **UPDATE** (non-indexed column) | **No index impact** — only the clustered index (table data) is updated. |
| **DELETE** | Entry is removed from **every** index's B+ Tree. Leaf pages may merge if they become too empty. |

### Real-World Write Overhead

| Indexes on Table | INSERT Relative Speed | Notes |
|---|---|---|
| 0 indexes (heap) | 1× (baseline) | Not possible in InnoDB (always has PK) |
| 1 (primary key only) | ~1× | Just the clustered index |
| 3 indexes | ~1.5-2× slower | Each index adds ~15-30% overhead |
| 5 indexes | ~2-3× slower | Noticeable on high-throughput writes |
| 10+ indexes | ~3-5× slower | Seriously impacts write performance |

**Buffer pool helps:** InnoDB uses the **change buffer** (part of the buffer pool) to defer updates to secondary indexes. Instead of writing to the B+ Tree immediately, it records the change in a buffer and merges it later. This significantly reduces random I/O for write-heavy workloads. However, the change buffer only works for secondary indexes, not the clustered index.

### Best Practices for Write-Heavy Tables

1. **Only create indexes you actually use** — run `SHOW INDEX FROM table` and check if any index is never hit
2. **Monitor unused indexes:**
   ```sql
   -- MySQL 8.0+ performance_schema
   SELECT OBJECT_SCHEMA, OBJECT_NAME, INDEX_NAME
   FROM performance_schema.table_io_waits_summary_by_index_usage
   WHERE INDEX_NAME IS NOT NULL
     AND COUNT_STAR = 0
     AND OBJECT_SCHEMA = 'your_database';
   ```
3. **Bulk insert tip:** Drop indexes before bulk loading, then recreate them — building an index once from sorted data is much faster than inserting into an existing index row by row
4. **Prefer composite indexes over multiple single-column indexes** — one composite index replaces two or three single-column indexes, reducing write overhead

---

## Clustered vs Secondary Indexes (InnoDB Specifics)

This distinction is unique to InnoDB and is **critical** for understanding query performance.

### Clustered Index (Primary Key)

- There is **exactly one** per table — the primary key index
- The leaf nodes store the **complete row data** (all columns)
- Data is **physically sorted** by the primary key on disk
- Lookups by primary key reach the data directly — **one B+ Tree traversal**

```
Clustered Index B+ Tree (PRIMARY KEY = id):

       Internal: [50, 100]
                /    |    \
Leaf pages:  [id=1, ALL_COLUMNS]  [id=51, ALL_COLUMNS]  [id=101, ALL_COLUMNS]
             [id=2, ALL_COLUMNS]  [id=52, ALL_COLUMNS]  [id=102, ALL_COLUMNS]
             ...                   ...                    ...
```

### Secondary Index (Any Non-Primary Index)

- There can be **many** per table
- The leaf nodes store the **indexed columns + the primary key value** (NOT the full row)
- To get columns not in the secondary index, InnoDB must do a **second lookup** on the clustered index using the primary key — this is called a **bookmark lookup** (or **"back to table"**, sometimes called **"double lookup"**)

```
Secondary Index B+ Tree (INDEX on email):

       Internal: ['john@...', 'mary@...']
                /         |          \
Leaf pages:  [email='alice@...', PK=42]   [email='john@...', PK=7]
             [email='bob@...',   PK=15]   [email='mary@...', PK=91]
```

**What happens when you query by email:**

```sql
SELECT * FROM users WHERE email = 'alice@example.com';

-- Step 1: Walk the SECONDARY index (email) → find PK = 42
-- Step 2: Walk the CLUSTERED index (id) → find id = 42 → read full row
-- Total: 2 B+ Tree traversals
```

**What happens when the secondary index is a covering index:**

```sql
SELECT email FROM users WHERE email = 'alice@example.com';

-- Step 1: Walk the SECONDARY index (email) → found the email
-- Step 2: SKIP — 'email' is already in the index, no need to go to clustered index
-- Total: 1 B+ Tree traversal — "Using index"
```

### Why Primary Key Size Matters

Since **every secondary index stores a copy of the primary key** in its leaf nodes, a large primary key bloats all secondary indexes.

| Primary Key Type | PK Size | Impact on Each Secondary Index Entry |
|---|---|---|
| `INT` | 4 bytes | Small — minimal overhead |
| `BIGINT` | 8 bytes | Fine for most use cases |
| `UUID` (`CHAR(36)`) | 36 bytes | ⚠️ 4.5x larger than `BIGINT` — every secondary index wastes space |
| `VARCHAR(255)` | Up to 255 bytes | ❌ Terrible — massively bloats all secondary indexes |

**Recommendation:** Keep primary keys **short** (prefer `INT` or `BIGINT` with auto-increment). If you must use UUIDs, store them as `BINARY(16)` (16 bytes) instead of `CHAR(36)` (36 bytes).

### Clustered vs Secondary — Quick Reference

| Aspect | Clustered Index | Secondary Index |
|---|---|---|
| **Number per table** | Exactly 1 | Unlimited |
| **What leaf nodes store** | Full row data | Indexed columns + primary key |
| **Columns returned directly** | All (it IS the row) | Only indexed columns (otherwise needs bookmark lookup) |
| **Lookup cost** | 1 B+ Tree traversal | 1 (index) + 1 (clustered lookup) = 2 traversals |
| **Range scan** | Very fast (data is physically contiguous) | Slower (each row may need a random clustered lookup) |
| **Insert behavior** | Appends to end if auto-increment PK; random inserts cause page splits | Always positions by indexed value; random by nature |

---

## EXPLAIN — Reading Query Execution Plans

`EXPLAIN` is the single most important tool for understanding how MySQL executes your queries and whether your indexes are being used. Always use `EXPLAIN` before and after adding indexes.

### Basic Usage

```sql
EXPLAIN SELECT * FROM employees WHERE department = 'Engineering';
```

### Key Columns in EXPLAIN Output

| Column | What It Tells You | What to Look For |
|---|---|---|
| **id** | Query step number (subqueries get separate IDs) | Higher IDs execute first |
| **select_type** | Type of SELECT (`SIMPLE`, `PRIMARY`, `SUBQUERY`, `DERIVED`) | `SIMPLE` = no subqueries |
| **table** | Which table this row is about | Self-explanatory |
| **type** | **How MySQL accesses the table** — this is the most important column | See access types below |
| **possible_keys** | Which indexes MySQL *could* use | If NULL, no relevant indexes exist |
| **key** | Which index MySQL *actually chose* | If NULL, no index was used |
| **key_len** | How many bytes of the index are used | For composite indexes, tells you how many columns are being used |
| **ref** | What value is compared against the index | `const` (literal value), column name, or `func` |
| **rows** | **Estimated** number of rows MySQL will examine | Lower is better |
| **filtered** | Percentage of rows that pass the `WHERE` condition | 100% = all examined rows match |
| **Extra** | Additional information | Critical details — see below |

### Access Types (the `type` column) — Best to Worst

| Type | Meaning | Performance | Example |
|---|---|---|---|
| `system` | Table has exactly 1 row | ⚡ Best | System tables |
| `const` | At most 1 matching row (unique index + constant) | ⚡ Excellent | `WHERE id = 42` |
| `eq_ref` | 1 matching row per join iteration (unique index) | ⚡ Excellent | `JOIN ON pk = fk` |
| `ref` | Multiple matching rows via non-unique index | ✅ Good | `WHERE department = 'Eng'` |
| `range` | Index range scan | ✅ Good | `WHERE salary > 80000` |
| `index` | Full index scan (reads entire index, not table) | ⚠️ Okay | Covering index on `SELECT col` |
| `ALL` | **Full table scan** — no index used | 🔴 Bad | `WHERE func(col) = val` |

**Goal:** Get your important queries to `const`, `eq_ref`, `ref`, or `range`. If `EXPLAIN` shows `ALL` for a large table, that query needs an index.

### Important `Extra` Values

| Extra Value | Meaning | Action |
|---|---|---|
| `Using index` | ✅ Covering index — data read from index only | Great — no table access needed |
| `Using where` | Filtering happens after reading (normal) | Fine — check if an index could push filtering earlier |
| `Using index condition` | Index Condition Pushdown (ICP) — filtering pushed to storage engine level | Good optimization |
| `Using temporary` | ⚠️ MySQL created a temporary table (for GROUP BY, DISTINCT, ORDER BY) | Consider adding an index to avoid this |
| `Using filesort` | ⚠️ MySQL sorted results in memory/on disk instead of using an index | Add an index matching the ORDER BY |
| `Using join buffer` | ⚠️ No index for the join — MySQL buffers rows | Add an index on the join column |
| `Select tables optimized away` | ✅ Query answered from index metadata alone (e.g., `MIN`/`MAX`) | Best possible case |

### Practical EXPLAIN Examples

**Example 1: No index — full table scan**

```sql
EXPLAIN SELECT * FROM orders WHERE customer_email = 'alice@example.com';
```

```
+----+------+------+------+------+------+---------+------+--------+-------------+
| id | type | table  | possible_keys | key  | rows   | Extra       |
+----+------+------+------+------+------+---------+------+--------+-------------+
|  1 | ALL  | orders | NULL          | NULL | 500000 | Using where |
+----+------+------+------+------+------+---------+------+--------+-------------+
```

🔴 `type = ALL`, `key = NULL`, `rows = 500000` — scanning the entire table!

**Fix:** `CREATE INDEX idx_email ON orders (customer_email);`

**Example 2: After adding the index**

```sql
EXPLAIN SELECT * FROM orders WHERE customer_email = 'alice@example.com';
```

```
+----+------+--------+---------------+-----------+------+-------+
| id | type | table  | possible_keys | key       | rows | Extra |
+----+------+--------+---------------+-----------+------+-------+
|  1 | ref  | orders | idx_email     | idx_email |    3 |       |
+----+------+--------+---------------+-----------+------+-------+
```

✅ `type = ref`, `key = idx_email`, `rows = 3` — only examines 3 rows!

**Example 3: Covering index**

```sql
CREATE INDEX idx_dept_salary ON employees (department, salary);

EXPLAIN SELECT department, salary FROM employees WHERE department = 'Eng';
```

```
+----+------+-----------+----------------+----------------+------+-------------+
| id | type | table     | possible_keys  | key            | rows | Extra       |
+----+------+-----------+----------------+----------------+------+-------------+
|  1 | ref  | employees | idx_dept_salary| idx_dept_salary|  150 | Using index |
+----+------+-----------+----------------+----------------+------+-------------+
```

✅ `Using index` = covering index, no table data access.

**Example 4: Filesort detected**

```sql
EXPLAIN SELECT * FROM posts WHERE user_id = 5 ORDER BY created_at DESC LIMIT 20;
```

Without `INDEX(user_id, created_at)`:

```
| type | key        | Extra                       |
| ref  | idx_userid | Using where; Using filesort  |
```

⚠️ `Using filesort` — MySQL found the rows via the index but had to sort them in memory.

**Fix:** `CREATE INDEX idx_user_date ON posts (user_id, created_at);`

After the fix:

```
| type | key           | Extra                |
| ref  | idx_user_date | Using index condition |
```

✅ No more filesort — the index provides data already sorted by `created_at` within each `user_id`.

### EXPLAIN ANALYZE (MySQL 8.0.18+)

`EXPLAIN ANALYZE` actually **runs** the query and shows real execution times:

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42;
```

```
-> Index lookup on orders using idx_customer_id (customer_id=42)
   (cost=3.55 rows=8) (actual time=0.045..0.062 rows=8 loops=1)
```

This tells you the **actual** number of rows and execution time, not just estimates. Use it to validate that your index changes actually improve performance.

---

## Common Index Mistakes

| Mistake | Why It's Bad | Fix |
|---|---|---|
| Indexing every column | Wastes storage, kills write performance | Index only queried columns |
| `WHERE YEAR(created_at) = 2025` | Function on column → index unusable | `WHERE created_at >= '2025-01-01' AND created_at < '2026-01-01'` |
| `WHERE age + 10 > 30` | Arithmetic on column → index unusable | `WHERE age > 20` |
| `WHERE LOWER(email) = 'alice@...'` | Function on column → index unusable | Use a generated column or collation: `WHERE email = 'alice@...'` (if collation is ci) |
| `VARCHAR(255)` primary key | Bloats every secondary index by 255 bytes per entry | Use `INT` or `BIGINT` auto-increment |
| **Too many single-column indexes** | MySQL uses at most 1 index per table per query (in most cases) | Use composite indexes that match your query patterns |
| **Wrong column order in composite index** | `INDEX(salary, dept)` can't help `WHERE dept = 'Eng'` | Put equality columns first, range columns last |
| **Not checking EXPLAIN** | You never know if your index is actually being used | Always `EXPLAIN` your important queries |
| **Redundant indexes** | `INDEX(a)` is redundant if `INDEX(a, b)` already exists | Drop the single-column index |

---

## Quick Decision Guide for Indexes

| Scenario | Recommended Index |
|---|---|
| Lookup by primary key | Already indexed (clustered index) |
| Lookup by unique column (email, username) | `UNIQUE INDEX` on that column |
| Filtering + sorting on same query | Composite index `(filter_col, sort_col)` |
| JOIN between two tables | Index on the foreign key column |
| Full-text search in articles | `FULLTEXT INDEX` on text columns |
| "Find nearest" geo queries | `SPATIAL INDEX` on geometry column |
| Frequent `GROUP BY department` | Index on `department` |
| `COUNT(*)` / `SUM()` with filter | Covering index including filter + aggregated column |
| High-write, low-read table (logs) | Minimal indexes — primary key only if possible |

> **The golden rule:** Indexes exist to help **reads**. Every index you add is a **tax on writes**. Design your indexes based on your **actual query patterns**, not theoretical ones. Use `EXPLAIN` to verify that MySQL is actually using the index, and monitor for unused indexes that are just wasting resources.

---

# **Database Partitioning**

When a single table grows to hundreds of millions (or billions) of rows, or has dozens of columns with different access patterns, even well-indexed queries start to slow down — because the table simply doesn't fit efficiently into memory or disk I/O anymore. **Partitioning** is the strategy of splitting a large table into smaller, more manageable pieces.

There are two fundamentally different ways to partition a table:

| Strategy | What It Splits | Analogy |
|---|---|---|
| **Vertical Partitioning** | **Columns** — divides the table into narrower tables | Tearing a wide spreadsheet into separate sheets by column groups |
| **Horizontal Partitioning** | **Rows** — divides the table into smaller tables with the same columns | Splitting a phone book into volumes A–M and N–Z |

---

## Vertical Partitioning

Vertical partitioning means **splitting a table's columns** into two or more separate tables. Each resulting table has the **same number of rows** but **fewer columns**. The tables are linked by the same primary key so you can `JOIN` them back when needed.

### Why Do It?

Not all columns are accessed equally. In a typical `users` table, you might read `name` and `email` on every page load, but `bio` (a large `TEXT` column) and `profile_picture_url` only when someone visits a profile page. Keeping everything in one table means:

- **Row size is large** → fewer rows fit per InnoDB page (16 KB) → more disk reads for common queries
- **Buffer pool is wasted** — hot, small columns share pages with cold, large columns
- **Full scans are slower** — even reading just `name` and `email` has to skip over the bulky `bio` column in every row

### Example — E-Commerce Product Table

Suppose you have a single `products` table:

```sql
CREATE TABLE products (
    id           INT PRIMARY KEY AUTO_INCREMENT,
    name         VARCHAR(200),
    price        DECIMAL(10,2),
    category_id  INT,
    stock        INT,
    -- These columns are accessed rarely (only on the product detail page)
    description  TEXT,             -- ~2 KB average
    specs_json   JSON,             -- ~1 KB average
    warranty     TEXT,             -- ~500 bytes average
    reviews_avg  DECIMAL(3,2),
    created_at   DATETIME
);
```

**Problem:** Every query that lists products (homepage, search results, category pages) reads just `name`, `price`, `category_id`, and `stock` — but InnoDB loads the **full row** including the heavy `description`, `specs_json`, and `warranty` columns. For 10 million products, this wastes enormous amounts of buffer pool memory.

### After Vertical Partitioning

Split into two tables — **frequently accessed columns** and **rarely accessed columns**:

```sql
-- Table 1: Hot data (accessed on every page — listing, search, cart)
CREATE TABLE products_core (
    id           INT PRIMARY KEY AUTO_INCREMENT,
    name         VARCHAR(200),
    price        DECIMAL(10,2),
    category_id  INT,
    stock        INT,
    reviews_avg  DECIMAL(3,2),
    created_at   DATETIME
);

-- Table 2: Cold data (accessed only on the product detail page)
CREATE TABLE products_detail (
    product_id   INT PRIMARY KEY,    -- Same PK as products_core
    description  TEXT,
    specs_json   JSON,
    warranty     TEXT,
    FOREIGN KEY (product_id) REFERENCES products_core(id)
);
```

**How it looks visually:**

```
BEFORE (one wide table):
┌────┬──────────┬───────┬─────┬───────────────────────────┬──────────┬──────────┐
│ id │   name   │ price │stock│       description          │specs_json│ warranty │
├────┼──────────┼───────┼─────┼───────────────────────────┼──────────┼──────────┤
│  1 │ iPhone   │ 999   │  50 │ The latest iPhone with... │ {...}    │ 1 year.. │
│  2 │ MacBook  │ 1999  │  30 │ Powerful laptop for...    │ {...}    │ 2 year.. │
│  3 │ AirPods  │ 249   │ 200 │ Wireless earbuds with...  │ {...}    │ 1 year.. │
└────┴──────────┴───────┴─────┴───────────────────────────┴──────────┴──────────┘

AFTER (two narrower tables):

products_core (HOT — fits in buffer pool)     products_detail (COLD — loaded on demand)
┌────┬──────────┬───────┬─────┐               ┌────────────┬───────────────────┬──────────┬──────────┐
│ id │   name   │ price │stock│               │ product_id │    description    │specs_json│ warranty │
├────┼──────────┼───────┼─────┤               ├────────────┼───────────────────┼──────────┼──────────┤
│  1 │ iPhone   │ 999   │  50 │               │     1      │ The latest iPh... │ {...}    │ 1 year.. │
│  2 │ MacBook  │ 1999  │  30 │               │     2      │ Powerful laptop.. │ {...}    │ 2 year.. │
│  3 │ AirPods  │ 249   │ 200 │               │     3      │ Wireless earbu.. │ {...}    │ 1 year.. │
└────┴──────────┴───────┴─────┘               └────────────┴───────────────────┴──────────┴──────────┘
```

### Query Patterns After Vertical Partitioning

```sql
-- Homepage / Search / Category listing — FAST (reads only the narrow core table)
SELECT id, name, price, stock
FROM products_core
WHERE category_id = 5 AND stock > 0
ORDER BY created_at DESC
LIMIT 20;

-- Product detail page — joins the two tables (only when user clicks a specific product)
SELECT c.id, c.name, c.price, c.stock,
       d.description, d.specs_json, d.warranty
FROM products_core c
JOIN products_detail d ON c.id = d.product_id
WHERE c.id = 42;
```

### When to Use Vertical Partitioning

| ✅ Use When | ❌ Avoid When |
|---|---|
| Some columns are read much more frequently than others | All columns are always accessed together |
| Table has large `TEXT`, `BLOB`, or `JSON` columns mixed with small columns | Table is already narrow (few, small columns) |
| You want to fit hot data entirely in the buffer pool | The overhead of `JOIN`ing tables back is unacceptable (ultra-low-latency systems) |
| Different columns have different security/access requirements | Table is small enough that row size doesn't matter |

---

## Horizontal Partitioning

Horizontal partitioning means **splitting a table's rows** into multiple smaller tables (or partitions). Each partition has the **same columns** but holds only a **subset of the rows**. The split is done based on a **partition key** — a column (or expression) whose value determines which partition a row goes into.

### Why Do It?

When a table grows to hundreds of millions of rows:

- **Index size exceeds memory** — the B+ Tree doesn't fit in the buffer pool, causing frequent disk reads even for indexed queries
- **Range scans read too many pages** — scanning a month of orders out of 5 years touches only 1.6% of the data, but without partitioning the index covers all 5 years
- **Maintenance operations are slow** — `ALTER TABLE`, `OPTIMIZE TABLE`, archiving old data take forever on a massive table
- **Deleting old data is expensive** — `DELETE FROM orders WHERE order_date < '2020-01-01'` generates billions of undo log entries; dropping a partition is instant

### Types of Horizontal Partitioning

| Type | How Rows Are Split | Best For |
|---|---|---|
| **Range** | By a continuous range of values (`date`, `id`) | Time-series data, logs, orders |
| **List** | By exact values from a defined list (`country`, `status`) | Region-based or category-based splits |
| **Hash** | By hash of a column value (evenly distributes rows) | Uniform distribution when there's no natural range |
| **Key** | Like hash but uses MySQL's internal hashing function | Simple even distribution |

### Example — E-Commerce Orders Table (Range Partitioning by Date)

Suppose you have an `orders` table with 500 million rows spanning 5 years:

```sql
-- BEFORE: One massive table
CREATE TABLE orders (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id  INT,
    order_date   DATE,
    total        DECIMAL(10,2),
    status       ENUM('pending', 'shipped', 'delivered', 'cancelled')
);
-- 500 million rows, indexes are 40+ GB, queries are getting slow
```

### After Horizontal Partitioning (Range by Year)

```sql
CREATE TABLE orders (
    id           BIGINT AUTO_INCREMENT,
    customer_id  INT,
    order_date   DATE,
    total        DECIMAL(10,2),
    status       ENUM('pending', 'shipped', 'delivered', 'cancelled'),
    PRIMARY KEY (id, order_date)    -- Partition key MUST be part of the primary key
) PARTITION BY RANGE (YEAR(order_date)) (
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

**How it looks visually:**

```
BEFORE (one huge table — 500M rows):
┌───────────────────────────────────────────────────────────────────────┐
│                          orders (500M rows)                          │
│  id=1,  date=2021-01-15, ...                                        │
│  id=2,  date=2023-07-22, ...                                        │
│  id=3,  date=2021-11-03, ...                                        │
│  ...                                (all 500 million rows together)  │
└───────────────────────────────────────────────────────────────────────┘

AFTER (same table, partitioned by year — MySQL manages the split internally):

┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   p2021 (~80M)  │ │   p2022 (~90M)  │ │   p2023 (~100M) │ │   p2024 (~110M) │ │   p2025 (~120M) │
│ date < 2022     │ │ date < 2023     │ │ date < 2024     │ │ date < 2025     │ │ date < 2026     │
│                 │ │                 │ │                 │ │                 │ │                 │
│ id=1, 2021-01-15│ │ id=5, 2022-03-10│ │ id=2, 2023-07-22│ │ id=8, 2024-01-05│ │ id=9, 2025-02-14│
│ id=3, 2021-11-03│ │ id=6, 2022-08-20│ │ id=7, 2023-12-01│ │ ...             │ │ ...             │
│ ...             │ │ ...             │ │ ...             │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Partition Pruning — The Magic That Makes It Fast

When your query's `WHERE` clause includes the partition key, MySQL's optimizer automatically skips partitions that can't contain matching rows. This is called **partition pruning**.

```sql
-- Find all orders in January 2025
SELECT * FROM orders
WHERE order_date BETWEEN '2025-01-01' AND '2025-01-31';

-- MySQL ONLY scans partition p2025 (~120M rows)
-- It completely SKIPS p2021, p2022, p2023, p2024 (380M rows ignored!)

-- You can verify with EXPLAIN:
EXPLAIN SELECT * FROM orders WHERE order_date BETWEEN '2025-01-01' AND '2025-01-31';
-- Shows: partitions = p2025   ← only one partition scanned
```

**Without partitioning:** MySQL scans the index across all 500M rows.
**With partitioning:** MySQL scans only the ~120M rows in the relevant partition — **4× less data**.

### Other Partitioning Types — Examples

**List Partitioning (by country/region):**

```sql
CREATE TABLE customers (
    id         INT AUTO_INCREMENT,
    name       VARCHAR(100),
    country    VARCHAR(2),
    email      VARCHAR(255),
    PRIMARY KEY (id, country)
) PARTITION BY LIST COLUMNS (country) (
    PARTITION p_india   VALUES IN ('IN'),
    PARTITION p_usa     VALUES IN ('US'),
    PARTITION p_europe  VALUES IN ('GB', 'DE', 'FR', 'IT', 'ES'),
    PARTITION p_others  VALUES IN ('JP', 'BR', 'AU', 'CA')
);

-- Query: all Indian customers — scans ONLY p_india
SELECT * FROM customers WHERE country = 'IN';
```

**Hash Partitioning (even distribution):**

```sql
CREATE TABLE sessions (
    id         BIGINT AUTO_INCREMENT,
    user_id    INT,
    data       JSON,
    created_at DATETIME,
    PRIMARY KEY (id, user_id)
) PARTITION BY HASH(user_id)
  PARTITIONS 8;

-- MySQL distributes rows across 8 partitions using: user_id MOD 8
-- Each partition holds ~12.5% of the data
-- Queries with WHERE user_id = ? only scan 1 of 8 partitions
```

### Dropping Old Data — The Killer Feature

Without partitioning, deleting old data is brutal:

```sql
-- WITHOUT partitioning: generates massive undo logs, locks rows, takes hours
DELETE FROM orders WHERE order_date < '2022-01-01';
-- Deletes 80 million rows one by one 🔥

-- WITH partitioning: instant, zero overhead
ALTER TABLE orders DROP PARTITION p2021;
-- 80 million rows gone in milliseconds — it just deletes the partition's data file
```

### When to Use Horizontal Partitioning

| ✅ Use When | ❌ Avoid When |
|---|---|
| Table has hundreds of millions or billions of rows | Table has < 10 million rows (indexes handle it fine) |
| Queries almost always filter on the partition key (e.g., date range) | Queries rarely include the partition key in `WHERE` (no pruning = no benefit) |
| You need to efficiently archive/delete old data | You need strong foreign key constraints (partitioned tables don't support FK in MySQL) |
| Time-series data: logs, events, orders, transactions | You need many unique indexes across all rows (unique constraints must include the partition key) |
| Each partition can be maintained independently | The table is already fast enough with proper indexing |

---

## Vertical vs Horizontal Partitioning — Comparison

| Aspect | Vertical Partitioning | Horizontal Partitioning |
|---|---|---|
| **What is split** | Columns | Rows |
| **Number of rows per partition** | Same (all rows exist in each sub-table) | Different (rows are distributed) |
| **Number of columns per partition** | Fewer (each sub-table has a subset of columns) | Same (every partition has all columns) |
| **Primary use case** | Separate hot (frequently accessed) columns from cold (rarely accessed) columns | Split a massive table into smaller chunks by a key |
| **How to recombine** | `JOIN` the sub-tables on the shared primary key | `UNION ALL` across partitions (MySQL does this automatically) |
| **Implementation** | Manual — create separate tables and manage the split in your application/queries | Built-in — `CREATE TABLE ... PARTITION BY` (MySQL handles it transparently) |
| **When it shines** | Wide tables with mixed access patterns (hot + cold columns) | Very large tables where queries always filter on the partition key |
| **Real-world example** | Splitting a `users` table into `users_core` (name, email) + `users_profile` (bio, avatar) | Splitting an `orders` table by year so each year is a separate partition |

### Can You Use Both Together?

**Yes.** In large-scale systems, it's common to combine both strategies:

```
Original: one massive "orders" table (50 columns, 1 billion rows)

Step 1 — Vertical Partition:
  → orders_core    (id, customer_id, order_date, total, status)     — queried on every listing
  → orders_detail  (order_id, shipping_address, notes, gift_msg)    — queried on detail page only

Step 2 — Horizontal Partition (on orders_core):
  → orders_core PARTITION BY RANGE (YEAR(order_date))
  → p2023, p2024, p2025...

Result: Fast listing queries hit only the narrow, pruned partition of orders_core.
        Detail queries JOIN orders_detail only for a single order.
```

> **Key takeaway:** Vertical partitioning solves the **"too many columns"** problem (wide rows waste memory). Horizontal partitioning solves the **"too many rows"** problem (massive tables overwhelm indexes and I/O). Use them based on your bottleneck — or combine both when the table is both wide and tall.

---

## Partition-Based Data Retention (TTL Rotation)

When your team drops partitions older than 7 days to delete old data, this process is called **Partition-Based Data Retention** or **TTL (Time-To-Live) Rotation**. It's a widely used pattern in production systems for managing time-series data like logs, events, metrics, sessions, and transactional records that don't need to be kept forever.

### What Is It?

Instead of running expensive `DELETE` queries to remove old rows, you:

1. **Partition the table by date** (one partition per day, week, or month)
2. **Drop entire partitions** when they exceed the retention period (e.g., 7 days)
3. **Add new partitions** ahead of time so incoming data always has a place to land

The lifecycle looks like this:

```
Day 1: Create partitions for Day 1 through Day 8 (7-day window + 1 future)

Day 1   Day 2   Day 3   Day 4   Day 5   Day 6   Day 7   Day 8 (future)
 [p1]    [p2]    [p3]    [p4]    [p5]    [p6]    [p7]    [p8]
  ↑ oldest                                        ↑ today   ↑ pre-created

Day 8: Drop p1 (it's now 7 days old), add p9 for tomorrow

         Day 2   Day 3   Day 4   Day 5   Day 6   Day 7   Day 8   Day 9
          [p2]    [p3]    [p4]    [p5]    [p6]    [p7]    [p8]    [p9]
           ↑ oldest                                        ↑ today  ↑ new

Day 9: Drop p2, add p10 ...and so on forever
```

This forms a **sliding window** — at any given time, the table holds exactly 7 days of data.

### Complete Working Example — 7-Day Retention

**Step 1: Create the table with daily partitions**

```sql
CREATE TABLE events (
    id          BIGINT AUTO_INCREMENT,
    event_type  VARCHAR(50),
    payload     JSON,
    created_at  DATE NOT NULL,
    PRIMARY KEY (id, created_at)       -- Partition key must be in the PK
) PARTITION BY RANGE (TO_DAYS(created_at)) (
    PARTITION p20250218 VALUES LESS THAN (TO_DAYS('2025-02-19')),
    PARTITION p20250219 VALUES LESS THAN (TO_DAYS('2025-02-20')),
    PARTITION p20250220 VALUES LESS THAN (TO_DAYS('2025-02-21')),
    PARTITION p20250221 VALUES LESS THAN (TO_DAYS('2025-02-22')),
    PARTITION p20250222 VALUES LESS THAN (TO_DAYS('2025-02-23')),
    PARTITION p20250223 VALUES LESS THAN (TO_DAYS('2025-02-24')),
    PARTITION p20250224 VALUES LESS THAN (TO_DAYS('2025-02-25')),  -- today
    PARTITION p20250225 VALUES LESS THAN (TO_DAYS('2025-02-26')),  -- tomorrow (pre-created)
    PARTITION p_future  VALUES LESS THAN MAXVALUE                  -- safety net
);
```

> `TO_DAYS()` converts a date to an integer (number of days since year 0). MySQL requires integer expressions for `RANGE` partitioning, so we can't use a `DATE` value directly — `TO_DAYS()` bridges that gap.

**Step 2: Daily rotation — drop the oldest, add a new future partition**

```sql
-- Run this every day at midnight (via a cron job or scheduled event)

-- 1. Drop the partition that is now 7+ days old
ALTER TABLE events DROP PARTITION p20250218;
-- 💥 Millions of rows deleted INSTANTLY — no row-by-row scanning

-- 2. Reorganize the future partition to add tomorrow's dedicated partition
ALTER TABLE events REORGANIZE PARTITION p_future INTO (
    PARTITION p20250226 VALUES LESS THAN (TO_DAYS('2025-02-27')),
    PARTITION p_future  VALUES LESS THAN MAXVALUE
);
```

> **Why `REORGANIZE` instead of `ADD`?** Since `p_future` already catches everything beyond the last named partition, you can't just `ADD PARTITION` (MySQL would complain about overlapping ranges). `REORGANIZE PARTITION` splits `p_future` into the new day's partition plus a new `p_future`.

**Step 3: Automate with a MySQL Event (built-in cron)**

```sql
DELIMITER //

CREATE EVENT rotate_events_daily
ON SCHEDULE EVERY 1 DAY
STARTS '2025-02-25 00:05:00'    -- runs at 12:05 AM daily
DO
BEGIN
    -- Calculate partition names
    SET @old_date = DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 7 DAY), '%Y%m%d');
    SET @new_date = DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 1 DAY), '%Y%m%d');
    SET @new_boundary = DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 2 DAY), '%Y-%m-%d');

    -- Drop old partition
    SET @drop_sql = CONCAT('ALTER TABLE events DROP PARTITION p', @old_date);
    PREPARE stmt FROM @drop_sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- Add new partition
    SET @add_sql = CONCAT(
        'ALTER TABLE events REORGANIZE PARTITION p_future INTO (',
        'PARTITION p', @new_date, ' VALUES LESS THAN (TO_DAYS(''', @new_boundary, ''')), ',
        'PARTITION p_future VALUES LESS THAN MAXVALUE)'
    );
    PREPARE stmt FROM @add_sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //

DELIMITER ;

-- Don't forget to enable the event scheduler
SET GLOBAL event_scheduler = ON;
```

### What Happens Under the Hood

When you run `ALTER TABLE events DROP PARTITION p20250218`:

```
Step 1: MySQL identifies the data file for partition p20250218
        → e.g., events#P#p20250218.ibd  (InnoDB tablespace file)

Step 2: MySQL removes the partition metadata from the table definition
        → The partition no longer exists in INFORMATION_SCHEMA.PARTITIONS

Step 3: MySQL DELETES the .ibd file from disk
        → This is a simple file system operation — instant regardless of row count

Step 4: Done. No undo logs, no row locks, no cleanup needed.
```

Compare this with a regular `DELETE`:

```
DELETE FROM events WHERE created_at < '2025-02-18';

Step 1: MySQL scans the index to find ALL matching rows (millions)
Step 2: For EACH row:
        → Write the old row to the UNDO LOG (for rollback safety)
        → Mark the row as deleted in the clustered index
        → Mark the row as deleted in EVERY secondary index
        → Write all changes to the REDO LOG (for crash recovery)
Step 3: After commit, a background PURGE thread eventually removes the dead rows
Step 4: The freed space is NOT returned to the OS — it becomes "free space within the tablespace"
        → You need OPTIMIZE TABLE to reclaim it (which rebuilds the entire table)
```

### DELETE vs DROP PARTITION — Side by Side

| Aspect | `DELETE WHERE date < X` | `DROP PARTITION` |
|---|---|---|
| **Speed for 10M rows** | Minutes to hours | Milliseconds |
| **Lock behavior** | Row-level locks — blocks other writes to those rows | Metadata lock only — near-instant, minimal blocking |
| **Undo log usage** | Generates undo entries for every deleted row (massive) | Zero undo log entries |
| **Redo log usage** | Writes every change to redo log | Only metadata change logged |
| **Disk space reclaimed?** | ❌ No — space stays allocated in tablespace until `OPTIMIZE TABLE` | ✅ Yes — the `.ibd` file is deleted, OS reclaims the space immediately |
| **Replication impact** | Every deleted row is replicated to replicas (slow) | Only the `ALTER TABLE` statement is replicated (instant) |
| **Impact on running queries** | Holds locks, can cause timeouts for concurrent operations | Brief metadata lock, negligible impact |
| **Rollback possible?** | ✅ Yes — can `ROLLBACK` before `COMMIT` | ❌ No — DDL is auto-committed and irreversible |

### Benefits of Partition-Based TTL Rotation

| Benefit | Explanation |
|---|---|
| **Instant deletion** | Dropping a partition removes millions/billions of rows in milliseconds — it's a file delete, not a row-by-row operation |
| **Zero lock contention** | Unlike `DELETE`, it doesn't hold row locks — your application keeps reading and writing normally during the drop |
| **No undo/redo log bloat** | A `DELETE` of 100M rows generates gigabytes of undo logs; `DROP PARTITION` generates almost none |
| **Disk space actually freed** | `DELETE` leaves "holes" in the tablespace that require `OPTIMIZE TABLE` to reclaim; `DROP PARTITION` deletes the physical file |
| **Replication-friendly** | Only the DDL statement travels to replicas, not millions of row-level delete events |
| **Predictable performance** | The time to drop a partition is constant regardless of how many rows it contains — 1 row or 100 million rows, it's the same speed |
| **Natural data organization** | Queries filtering by date automatically benefit from partition pruning — even your regular `SELECT` queries get faster |
| **Simple archival** | Before dropping, you can `SELECT INTO OUTFILE` from the partition to archive to cold storage (S3, HDFS, etc.) |

### Demerits and Gotchas

| Demerit | Explanation |
|---|---|
| **Partition key must be in every unique index** | MySQL enforces that the partition key column must be part of the primary key and every unique index — this can force you to change your schema. For example, you can't have `PRIMARY KEY (id)` alone; you need `PRIMARY KEY (id, created_at)` |
| **Foreign keys not supported** | MySQL does **not** support foreign key constraints on partitioned tables. If your table has FK relationships, you'll need to enforce referential integrity in your application code |
| **No rollback** | `DROP PARTITION` is a DDL operation — it's auto-committed and **irreversible**. If you accidentally drop the wrong partition, the data is gone (unless you have a backup or replica) |
| **Partition management overhead** | Someone (or something) must create future partitions and drop old ones on schedule. If the cron job fails and no new partition is created, inserts into `p_future` will work but partition pruning degrades. If `p_future` doesn't exist and no partition covers the date, inserts **fail** |
| **Cross-partition queries are slower** | Queries that don't include the partition key in `WHERE` must scan **all** partitions — potentially slower than a single well-indexed table |
| **Limited number of partitions** | MySQL supports up to ~8,192 partitions per table. For daily partitions with 7-day retention, this is never an issue (only 8-9 partitions). But for fine-grained partitions (hourly) over long retention periods, you could hit the limit |
| **ALTER TABLE is heavier** | Adding/modifying columns on a partitioned table is slower because MySQL must modify every partition's data file. Tools like `pt-online-schema-change` have partition-specific limitations |
| **Query planner limitations** | Partition pruning only works when the `WHERE` clause directly references the partition key with constants or simple expressions. Complex expressions like `WHERE DATEDIFF(CURDATE(), created_at) > 7` may not trigger pruning — you should use `WHERE created_at < DATE_SUB(CURDATE(), INTERVAL 7 DAY)` instead |

### Best Practices for Production TTL Rotation

1. **Always keep a `p_future` (or `MAXVALUE`) partition** — this is your safety net. If the cron job that creates new partitions fails, inserts still succeed (they land in `p_future`) instead of throwing errors

2. **Create partitions 2-3 days ahead** — don't wait until midnight to create tomorrow's partition. Pre-create a few days in advance so clock skew, timezone differences, or missed cron runs don't cause failures

3. **Monitor the rotation job** — set up alerts if the partition rotation doesn't run. A common failure mode: partitions stop being created, all new data goes into `p_future`, and partition pruning stops working (silently degraded performance)

4. **Test the partition drop with `EXPLAIN` first** — before automating, verify that your queries actually benefit from pruning:
   ```sql
   EXPLAIN SELECT * FROM events WHERE created_at = '2025-02-24';
   -- Check the "partitions" column — it should show only ONE partition, not all of them
   ```

5. **Archive before dropping** — if there's any chance you'll need the old data later, export it before dropping:
   ```sql
   -- Export the partition's data to a file before dropping
   SELECT * FROM events PARTITION (p20250218)
   INTO OUTFILE '/tmp/events_20250218.csv'
   FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';

   -- Now safe to drop
   ALTER TABLE events DROP PARTITION p20250218;
   ```

6. **Use `RANGE` partitioning (not `HASH`)** — hash partitions can't be dropped selectively by date because rows are distributed by hash value, not by time. Only range (or list) partitioning allows you to drop a specific time window

---

## Partitioning vs Multiple Tables — Are They the Same?

At first glance, partitioning looks identical to just creating separate tables (`events_day1`, `events_day2`, etc.). Both split data into smaller chunks. But they are **fundamentally different** — partitioning is managed **by MySQL internally**, while multiple tables are managed **by you** in your application code. This difference matters enormously.

### The Manual Approach (Multiple Tables)

Without partitioning, you'd create a new table for each day and route queries yourself:

```sql
-- You manually create one table per day
CREATE TABLE events_20250218 (...);
CREATE TABLE events_20250219 (...);
CREATE TABLE events_20250220 (...);
-- ...and so on

-- Your APPLICATION must decide which table to query
-- To find events from Feb 19:
SELECT * FROM events_20250219 WHERE event_type = 'click';

-- To find events across multiple days, YOU must UNION them manually:
SELECT * FROM events_20250218 WHERE event_type = 'click'
UNION ALL
SELECT * FROM events_20250219 WHERE event_type = 'click'
UNION ALL
SELECT * FROM events_20250220 WHERE event_type = 'click';

-- To delete old data:
DROP TABLE events_20250218;
```

### The Partitioning Approach (MySQL Managed)

With partitioning, there's **one logical table** and MySQL handles everything behind the scenes:

```sql
-- One table, MySQL manages the internal split
CREATE TABLE events (...) PARTITION BY RANGE (TO_DAYS(created_at)) (...);

-- Your application queries ONE table — same as any normal table
SELECT * FROM events WHERE event_type = 'click' AND created_at = '2025-02-19';
-- MySQL automatically routes this to the correct partition (partition pruning)

-- Multi-day query — SAME simple query, no UNION needed
SELECT * FROM events
WHERE event_type = 'click'
AND created_at BETWEEN '2025-02-18' AND '2025-02-20';
-- MySQL scans only the relevant partitions automatically

-- Delete old data:
ALTER TABLE events DROP PARTITION p20250218;
```

### Why Partitioning Is Better Than Multiple Tables

| Aspect | Multiple Tables (Manual) | Partitioning (MySQL Managed) |
|---|---|---|
| **Query transparency** | ❌ Application must know which table to query. Every query needs table-routing logic. | ✅ Application queries **one table name** — MySQL routes internally. Zero application code changes. |
| **Cross-partition queries** | ❌ You must write `UNION ALL` across all tables manually. Adding a new day means changing the query. | ✅ Just `SELECT * FROM events WHERE date BETWEEN x AND y` — MySQL unions internally and prunes automatically. |
| **Schema changes** | ❌ `ALTER TABLE` must run on **every** table separately. Add a column? Run it N times. | ✅ One `ALTER TABLE events ADD COLUMN ...` — MySQL applies it to all partitions. |
| **Indexes** | ❌ Must create and maintain indexes on **each** table individually. | ✅ One `CREATE INDEX` — applies to all partitions. |
| **Application complexity** | ❌ Huge — your app needs logic to: pick the right table, build UNIONs, create new tables on schedule, handle edge cases around midnight. | ✅ Minimal — your app doesn't even know partitions exist. It's completely transparent. |
| **Aggregations** | ❌ `COUNT(*)` across all days requires UNION of all tables. | ✅ `SELECT COUNT(*) FROM events` — MySQL aggregates across all partitions automatically. |
| **Foreign keys from other tables** | ❌ Impossible — other tables can't FK to a table that changes name every day. | ⚠️ MySQL doesn't support FK on partitioned tables either, but at least the table name is stable for references in application code. |
| **ORM / Framework support** | ❌ ORMs (JPA, Hibernate, Django ORM) don't know how to route to dynamic table names. You'd need raw SQL everywhere. | ✅ ORMs work normally — they just see one table `events`. |
| **Tooling compatibility** | ❌ Monitoring, backup tools, migration tools all need to handle N tables. | ✅ All tools see one table — `mysqldump events`, `EXPLAIN SELECT`, etc. work as expected. |
| **Dropping old data** | ✅ `DROP TABLE events_20250218` — equally fast. | ✅ `ALTER TABLE events DROP PARTITION p20250218` — equally fast. |

### Example: The Pain of Multiple Tables in Real Code

Imagine you manually manage separate tables in a Spring Boot application:

```java
// ❌ MANUAL TABLE ROUTING — your code becomes a mess

@Service
public class EventService {

    @Autowired
    private JdbcTemplate jdbc;

    public List<Event> getEvents(LocalDate from, LocalDate to) {
        // YOU must figure out which tables to query
        List<String> tableNames = new ArrayList<>();
        for (LocalDate d = from; !d.isAfter(to); d = d.plusDays(1)) {
            tableNames.add("events_" + d.format(DateTimeFormatter.BASIC_ISO_DATE));
        }

        // YOU must build a UNION ALL query dynamically
        String sql = tableNames.stream()
            .map(t -> "SELECT * FROM " + t + " WHERE event_type = ?")
            .collect(Collectors.joining(" UNION ALL "));

        // What if a table doesn't exist yet? You need error handling.
        // What if the date range spans 30 days? That's 30 UNIONs.
        return jdbc.query(sql, mapper, "click");
    }
}
```

With partitioning, the same code is trivial:

```java
// ✅ WITH PARTITIONING — normal JPA, zero routing logic

@Repository
public interface EventRepository extends JpaRepository<Event, Long> {

    // Just a regular query — MySQL handles partition routing
    List<Event> findByEventTypeAndCreatedAtBetween(
        String eventType, LocalDate from, LocalDate to
    );
}
```

### When Multiple Tables Actually Make Sense

There are rare cases where separate tables are preferred over partitioning:

| Scenario | Why Separate Tables Work Better |
|---|---|
| **Each table has a different schema** | Partitions must all share the same columns. If each "slice" has different columns, you need separate tables. |
| **Tables belong to different databases/servers** | Partitioning is within a single MySQL instance. If you're sharding across servers, you need separate tables (or databases). |
| **Per-tenant isolation** | In multi-tenant systems, giving each tenant their own table (or database) provides stronger isolation than partitions. |
| **You need foreign keys** | Partitioned tables don't support FK. If FK constraints are critical, separate tables with FK may be better. |

> **Bottom line:** Partitioning gives you the performance benefits of splitting data across smaller chunks **without** the application complexity of managing multiple tables. Your app queries one table, MySQL does the routing. Always prefer partitioning over manual table splitting unless you have a specific reason not to.

---

# Durability in Databases

Durability is the **D** in ACID. It guarantees that once a transaction is **committed**, its changes are **permanent** — they survive crashes, power failures, and restarts. The moment the database says "COMMIT successful", that data will still be there after a reboot, a crash, or a power cut.

---

## Why Durability Is Hard

The problem is simple: the fastest storage is RAM, but RAM is **volatile** — pull the power and everything in it vanishes instantly. Disk is **persistent** but slow. A naive database that only wrote to RAM would lose all committed data on every crash. A naive database that wrote to disk on every single operation would be unacceptably slow.

Durability is the engineering challenge of making committed data survive on disk **without** making the database unbearably slow.

---

## Mechanism 1: Write-Ahead Logging (WAL) — The Core

The most important durability mechanism in every serious database (MySQL InnoDB, PostgreSQL, Oracle, SQL Server) is **Write-Ahead Logging (WAL)**.

**The idea:** Before you modify the actual data page on disk, you first write a description of the change to a **sequential log file** (the redo log). Only after that log entry is safely on disk do you acknowledge the commit to the client.

```
Client → COMMIT
            ↓
  1. Append redo log entry (sequential write — fast)
            ↓
  2. fsync() the redo log (force to physical disk)
            ↓
  3. ✅ Return "COMMIT OK" to client
            ↓
  4. (Later, in background) Write actual data pages to disk
```

**Why this works for crash recovery:** If the server crashes after step 3 but before step 4, the redo log is already on disk. On restart, InnoDB replays the redo log entries and applies the committed changes to the data files. The client's data is never lost.

**Why sequential writes matter:** The redo log is always *appended* to — sequential writes are dramatically faster than random writes on both HDDs and SSDs. This is why WAL doesn't destroy performance: instead of an expensive random write to a data page, you do a cheap sequential append to the log.

In MySQL InnoDB, the redo log files are `ib_logfile0` and `ib_logfile1` (configurable via `innodb_log_file_size`).

---

## Mechanism 2: `fsync()` — Actually Getting to Disk

When your code calls `write()`, the OS puts the data in an in-memory page cache. It may sit there for seconds before reaching physical disk. If the machine loses power during that window, the "written" data is gone.

`fsync()` is the system call that says: **flush everything to the physical storage device right now**. InnoDB calls `fsync()` on the redo log at every commit.

### The `innodb_flush_log_at_trx_commit` Setting

This is the single most important durability knob in MySQL:

| Value | Behavior | Max Data Loss | Use Case |
|-------|----------|---------------|----------|
| `1` (default) | `fsync()` on every commit | **Zero** | Production — full ACID |
| `2` | Write to OS cache on commit, `fsync()` every second | ~1 second (OS crash only) | Acceptable if OS crash is rare |
| `0` | Write + `fsync()` every second | ~1 second (even MySQL crash) | Dev/staging only |

**Rule:** Always use `1` in production for any transactional or financial system.

Similarly, `sync_binlog = 1` ensures the binary log (used for replication and point-in-time recovery) is also fsynced on every commit. The combination of `innodb_flush_log_at_trx_commit = 1` and `sync_binlog = 1` is called the **"double-1" configuration** — this is the gold standard for full MySQL durability.

---

## Mechanism 3: Checkpointing

The redo log is a **circular buffer** — it has a fixed size. As changes accumulate, older entries must be freed up. But you can only delete a redo log entry once the corresponding data page has been flushed to the actual data file on disk. That flush is called a **checkpoint**.

InnoDB continuously runs a **page cleaner thread** in the background that writes dirty (modified-but-not-yet-flushed) pages from the in-memory buffer pool to the data files. Once a page is written, its redo log entries can be freed.

**What happens if checkpointing falls behind?** If the redo log fills up completely, InnoDB must stall all write operations until space is freed. This is called a "log-full stall" and causes severe latency spikes. To avoid it, `innodb_log_file_size` should be large enough to comfortably absorb your peak write rate.

On crash recovery, InnoDB only needs to replay redo log entries *after* the last checkpoint — everything before is already in the data files.

---

## Mechanism 4: Double Write Buffer — No Torn Pages

InnoDB writes data pages in **16 KB chunks**. But a crash could happen midway through writing a 16 KB page — leaving half the old data and half the new data on disk. This is called a **torn page** and it results in corruption that the redo log alone cannot fix (because the redo log assumes the original page is intact to apply changes on top of).

InnoDB solves this with the **double write buffer**:

```
Step 1: Write dirty pages → doublewrite area (sequential, safe)
Step 2: Confirm doublewrite area is on disk
Step 3: Write dirty pages → actual data file locations
```

On crash recovery, if InnoDB finds a torn page in a data file, it copies the intact version from the doublewrite area and then applies the redo log on top of it. The page is repaired.

---

## Mechanism 5: Replication — Cross-Machine Durability

All the above mechanisms protect a single machine. But what if the disk physically fails? Or the entire server rack burns?

**Replication** solves this by keeping copies of the data on separate machines:

| Type | How It Works | Durability |
|------|-------------|------------|
| **Asynchronous** | Primary commits, replica catches up later | Possible data loss if primary dies before replica syncs |
| **Semi-synchronous** | Primary waits for at least one replica to *acknowledge receipt* | Very small window of data loss |
| **Synchronous** | Commit is only acknowledged after replica has written to its own redo log | Zero data loss even on total primary hardware failure |

MySQL Group Replication and Galera Cluster offer synchronous replication. The trade-off is slightly higher commit latency, since the primary must wait for a network round trip to the replica.

---

## How It All Fits Together

```
Client: COMMIT
    │
    ▼
[1] Append to redo log (RAM buffer)
    │
    ▼
[2] fsync() redo log → physical disk  ◄── Durability on single machine
    │
    ▼
[3] (If sync replication) Wait for replica ACK  ◄── Durability across machines
    │
    ▼
[4] Return "OK" to client  ←── This is the durability guarantee moment
    │
    ▼
[5] Background: checkpoint dirty pages to .ibd data files
    (Using double write buffer to prevent torn pages)
```

The moment the client receives `OK`, the transaction is durable at every configured level.

---

## Battery-Backed Write Cache (BBWC)

There is one subtle trap: many disk controllers have an on-board write cache (RAM on the controller). A `fsync()` call may return "success" when the data is actually in the controller cache, not yet on the magnetic platter or NAND cells. A power failure at that moment still loses the data.

A **battery-backed write cache (BBWC)** keeps this controller cache alive during power loss, flushing it when power returns. With BBWC, `fsync()` is both fast (hits controller RAM) and durable (battery guarantees it survives power loss). This is why enterprise servers have RAID controllers with battery units — it dramatically improves both durability and write throughput.

---

## Summary

| Mechanism | Protects Against |
|-----------|-----------------|
| **Write-Ahead Logging (WAL / redo log)** | Crash before data pages are written to disk |
| **`fsync()` on commit** | OS page cache buffering and power failure |
| **Checkpointing** | Redo log filling up; speeds up crash recovery |
| **Double Write Buffer** | Torn pages from mid-write crashes |
| **Synchronous Replication** | Complete hardware failure on the primary |
| **Battery-Backed Write Cache** | Controller cache loss on power failure |

> **The guarantee:** Every `COMMIT` acknowledgment is a promise. The mechanisms above exist solely to ensure that promise is never broken.
