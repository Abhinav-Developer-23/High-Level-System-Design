# 📚 Table of Contents

> **DBMS roadmap:** https://whimsical.com/dbms-roadmap-C9vhnZy9RY9QkGRPgpZnDN

1. [SQL Commands — DDL, DQL, DML, DCL & TCL](#sql-commands--ddl-dql-dml-dcl--tcl)
   - [DDL — Data Definition Language](#1-ddl--data-definition-language)
   - [DQL — Data Query Language](#2-dql--data-query-language)
   - [DML — Data Manipulation Language](#3-dml--data-manipulation-language)
   - [DCL — Data Control Language](#4-dcl--data-control-language)
   - [TCL — Transaction Control Language](#5-tcl--transaction-control-language)
2. [MySQL Data Types](#mysql-data-types)
   - [Numeric Data Types](#numeric-data-types)
   - [String (Text) Data Types](#string-text-data-types)
   - [Date and Time Data Types](#date-and-time-data-types)
   - [JSON Data Type](#json-data-type)
   - [Spatial Data Types](#spatial-data-types)
   - [Quick Decision Guide](#quick-decision-guide)
3. [ALTER TABLE in MySQL — Online DDL, Locking & Internals](#alter-table-in-mysql--online-ddl-locking--internals)
   - [❓ What Happens Internally When We Run an ALTER Query? Does It Lock the Table?](#-what-happens-internally-when-we-run-an-alter-query-does-it-lock-the-table)
   - [Advantages of ALTER TABLE](#advantages-of-alter-table)
   - [Disadvantages of ALTER TABLE](#disadvantages-of-alter-table)
   - [The "Future Columns" Strategy — Pre-Allocating Columns to Avoid ALTER](#the-future-columns-strategy--pre-allocating-columns-to-avoid-alter)
4. [❓ What is Schema Migration? (Prisma, Django, Rails, etc.)](#-what-is-schema-migration-prisma-django-rails-etc)
   - [The Migration Tracking Table](#the-migration-tracking-table)
   - [Prisma: `migrate dev` vs `db push`](#prisma-migrate-dev-vs-db-push)
5. [❓ What Does "Seed a Database" Mean?](#-what-does-seed-a-database-mean)
   - [Migration vs Seeding — What's the Difference?](#migration-vs-seeding--whats-the-difference)
6. [❓ MySQL Pagination — OFFSET/LIMIT vs Cursor-Based (Keyset) Pagination](#-mysql-pagination--offsetlimit-vs-cursor-based-keyset-pagination)
   - [Approach 1 — OFFSET/LIMIT](#approach-1-offsetlimit-the-naïve-way)
   - [Approach 2 — Deferred Join](#approach-2-deferred-join-keep-offsetlimit-just-make-it-fast)
   - [Approach 3 — Cursor-Based / Keyset](#approach-3-cursor-based--keyset-pagination-the-right-way)
7. [❓ What is the N+1 Query Problem and How to Solve It?](#-what-is-the-n1-query-problem-and-how-to-solve-it)
8. [Instance, Schema & Sub-Schema in DBMS](#instance-schema--sub-schema-in-dbms)
9. [Referential Integrity Rule in RDBMS](#referential-integrity-rule-in-rdbms)
10. [Foreign Key Referential Actions (`ON DELETE` / `ON UPDATE`)](#foreign-key-referential-actions-on-delete--on-update)
    - [Setup Example](#setup-example)
    - [All 5 Referential Actions](#all-5-referential-actions)
    - [Side-by-Side Comparison](#side-by-side-comparison)
    - [Real-World Examples](#real-world-examples)
    - [What Happens If You Don't Use FK Constraints?](#what-happens-if-you-dont-use-fk-constraints)
    - [Do FK Actions Fix Anomalies?](#do-fk-actions-fix-anomalies)
    - [Quick Decision Guide](#quick-decision-guide-1)
11. [Three Relationship Types in ER Modeling](#three-relationship-types-in-er-modeling)
12. [Keys in DBMS](#keys-in-dbms)
    - [Super Key](#1-super-key)
    - [Candidate Key](#2-candidate-key)
    - [Primary Key](#3-primary-key)
    - [Alternate Key](#4-alternate-key)
    - [Foreign Key](#5-foreign-key)
    - [Secondary Key](#6-secondary-key-search-key)
    - [Does Declaring a KEY in MySQL Automatically Create an Index?](#-does-declaring-a-key-in-mysql-automatically-create-an-index)
13. [SQL Joins (INNER, LEFT, RIGHT, FULL, CROSS, SELF & NATURAL)](#sql-joins-inner-left-right-full-cross-self--natural)
    - [INNER JOIN](#1-inner-join)
    - [LEFT JOIN](#2-left-join-left-outer-join)
    - [RIGHT JOIN](#3-right-join-right-outer-join)
    - [FULL JOIN](#4-full-join-full-outer-join)
    - [CROSS JOIN](#5-cross-join-cartesian-product)
    - [SELF JOIN](#6-self-join)
    - [NATURAL JOIN](#7-natural-join)
14. [SQL Views](#sql-views)
    - [Creating Views](#1-creating-views)
    - [Managing Views](#2-managing-views)
    - [Modifying Data Through Views](#3-modifying-data-through-views)
    - [Rules for Updatable Views](#4-rules-for-updatable-views)
    - [WITH CHECK OPTION](#5-with-check-option)
15. [SQL Triggers](#sql-triggers)
16. [Stored Procedures in SQL](#stored-procedures-in-sql)
    - [MySQL Trigger vs Stored Procedure — With Example](#mysql-trigger-vs-stored-procedure--with-example)
    - [Why Do Most Companies Avoid Triggers & Stored Procedures?](#-why-do-most-companies-avoid-triggers--stored-procedures-and-keep-logic-in-the-application)
17. [Primary Key vs Unique Key](#primary-key-vs-unique-key)
18. [UUID vs Auto-Increment Integer as Primary Key](#uuid-vs-auto-increment-integer-as-primary-key)
    - [What Each Option Looks Like](#what-each-option-looks-like)
    - [Storage Comparison](#storage-comparison)
    - [Insert Performance — The B+ Tree Problem](#insert-performance--the-b-tree-problem)
    - [UUID v7 / ULID — The Best of Both Worlds?](#uuid-v7--ulid--the-best-of-both-worlds)
    - [Advantages of Auto-Increment Integer](#advantages-of-auto-increment-integer)
    - [Disadvantages of Auto-Increment Integer](#disadvantages-of-auto-increment-integer)
    - [Advantages of UUID](#advantages-of-uuid)
    - [Disadvantages of UUID](#disadvantages-of-uuid)
    - [Practical Performance Comparison Summary](#practical-performance-comparison-summary)
    - [Best Practice: Use Both (Hybrid Approach)](#best-practice-use-both-hybrid-approach)
    - [Quick Decision Guide](#quick-decision-guide-2)
19. [SQL Injection](#sql-injection)
20. [MySQL GRANT / REVOKE Privileges (Detailed)](#mysql-grant--revoke-privileges-detailed)
21. [Clustered vs Non-Clustered Index](#clustered-vs-non-clustered-index-1)
22. [Indexes in MySQL (InnoDB)](#indexes-in-mysql-innodb)
    - [How a B+ Tree Works — The Engine Behind MySQL Indexes](#how-a-b-tree-works--the-engine-behind-mysql-indexes)
    - [Types of Indexes](#types-of-indexes)
    - [When to Use an Index](#when-to-use-an-index)
    - [How Indexes Are Used in Common Operations](#how-indexes-are-used-in-common-operations)
    - [Covering Indexes and Index-Only Scans](#covering-indexes-and-index-only-scans)
    - [Index Selectivity and Cardinality](#index-selectivity-and-cardinality)
    - [Impact on Write Performance](#impact-on-write-performance)
    - [Clustered vs Secondary Indexes (InnoDB Specifics)](#clustered-vs-secondary-indexes-innodb-specifics)
    - [EXPLAIN — Reading Query Execution Plans](#explain--reading-query-execution-plans)
    - [Common Index Mistakes](#common-index-mistakes)
    - [Quick Decision Guide for Indexes](#quick-decision-guide-for-indexes)
23. [Dense Index vs Sparse Index](#dense-index-vs-sparse-index)
    - [What Is a Dense Index?](#what-is-a-dense-index)
    - [What Is a Sparse Index?](#what-is-a-sparse-index)
    - [Advantages of Sparse Index Over Dense Index](#advantages-of-sparse-index-over-dense-index)
    - [Disadvantages of Sparse Index vs Dense Index](#disadvantages-of-sparse-index-vs-dense-index)
    - [Why Would Anyone Use a Sparse Index?](#why-would-anyone-use-a-sparse-index)
    - [How Is a Sparse Index Created?](#how-is-a-sparse-index-created)
    - [Dense vs Sparse Index — Quick Comparison](#dense-vs-sparse-index--quick-comparison)
24. [Compound (Composite) Index](#compound-composite-index)
25. [Types of Index — Quick Reference](#types-of-index--quick-reference)
26. [Cursor in SQL](#cursor-in-sql)
27. [Functional Dependencies in DBMS](#functional-dependencies-in-dbms)
    - [Trivial Functional Dependency](#1-trivial-functional-dependency)
    - [Non-Trivial Functional Dependency](#2-non-trivial-functional-dependency)
    - [Full Functional Dependency](#3-full-functional-dependency-fully-functional)
    - [Partial Functional Dependency](#4-partial-functional-dependency)
    - [Transitive Functional Dependency](#5-transitive-functional-dependency)
28. [Database Anomalies](#database-anomalies)
    - [The Problematic Table (Unnormalized)](#the-problematic-table-unnormalized)
    - [1. Insertion Anomaly](#1-insertion-anomaly)
    - [2. Deletion Anomaly](#2-deletion-anomaly)
    - [3. Update Anomaly](#3-update-anomaly)
    - [The Fix: Normalization](#the-fix-normalization)
    - [Summary](#summary-1)
29. [Database Normalization — 1NF, 2NF, 3NF & BCNF](#database-normalization--1nf-2nf-3nf--bcnf)
    - [Why Normalize? — The Three Anomalies](#why-normalize--the-three-anomalies)
    - [Anomalies Resolved by Normalization — Deep Dive](#anomalies-resolved-by-normalization--deep-dive)
    - [1NF — First Normal Form](#1nf--first-normal-form)
    - [2NF — Second Normal Form](#2nf--second-normal-form)
    - [3NF — Third Normal Form](#3nf--third-normal-form)
    - [BCNF — Boyce–Codd Normal Form](#bcnf--boycecodd-normal-form-35nf)
    - [Lossless Join & Dependency Preservation](#two-rules-every-decomposition-must-respect)
    - [Denormalization](#denormalization--deliberately-going-backwards)
30. [Transactions in DBMS](#transactions-in-dbms)
    - [ACID Properties](#acid-properties)
    - [Transaction States](#transaction-states)
    - [Schedules & Serializability](#serializability)
31. [COMMIT, ROLLBACK & SAVEPOINT — In Detail](#commit-rollback--savepoint--in-detail)
32. [How Each ACID Property Is Achieved — Deep Dive](#how-each-acid-property-is-achieved--deep-dive)
33. [Durability in Databases](#durability-in-databases)
    - [Why Durability Is Hard](#why-durability-is-hard)
    - [Mechanism 1: Write-Ahead Logging (WAL) — The Core](#mechanism-1-write-ahead-logging-wal--the-core)
    - [Mechanism 2: `fsync()` — Actually Getting to Disk](#mechanism-2-fsync--actually-getting-to-disk)
    - [Mechanism 3: Checkpointing](#mechanism-3-checkpointing)
    - [Mechanism 4: Double Write Buffer — No Torn Pages](#mechanism-4-double-write-buffer--no-torn-pages)
    - [Mechanism 5: Replication — Cross-Machine Durability](#mechanism-5-replication--cross-machine-durability)
    - [How It All Fits Together](#how-it-all-fits-together)
    - [Battery-Backed Write Cache (BBWC)](#battery-backed-write-cache-bbwc)
    - [Summary](#summary-2)
34. [❓ What Is Consistency and Integrity in DBMS?](#-what-is-consistency-and-integrity-in-dbms)
    - [Integrity — The Rules](#integrity--the-rules)
    - [Consistency — The Guarantee](#consistency--the-guarantee)
    - [ACID Consistency vs CAP Consistency](#️-gotcha--consistency-in-acid--consistency-in-cap)
35. [Concurrency Problems (Without Proper Isolation)](#concurrency-problems-without-proper-isolation)
    - [Dirty Read](#1-dirty-read-reading-uncommitted-data)
    - [Lost Update](#2-lost-update)
    - [Non-Repeatable Read](#3-non-repeatable-read)
    - [Phantom Read](#4-phantom-read)
    - [SQL Isolation Levels](#sql-isolation-levels)
36. [Concurrency Control in DBMS](#concurrency-control-in-dbms)
    - [Lock-Based Concurrency Control](#1-lock-based-concurrency-control)
    - [Two-Phase Locking (2PL)](#2-two-phase-locking-2pl)
    - [Timestamp-Based Concurrency Control](#3-timestamp-based-concurrency-control)
    - [Optimistic Concurrency Control](#4-optimistic-concurrency-control-validation-based)
    - [Deadlocks](#deadlocks)
      - [The 4 Necessary Conditions](#the-4-necessary-conditions)
      - [Detection — Wait-For Graph](#deadlock-detection--the-wait-for-graph-wfg)
      - [Prevention Schemes (Wait-Die, Wound-Wait, Timeout)](#prevention-schemes-timestamp-based)
      - [Deadlock Recovery (Victim Selection, Rollback)](#deadlock-recovery)
      - [Starvation (Livelock)](#starvation-livelock)
    - [Recoverable & Cascadeless Schedules](#recoverable--cascadeless-schedules)
37. [Locking & Concurrency Control in MySQL](#locking--concurrency-control-in-mysql)
    - [1. Pessimistic Locking (`SELECT ... FOR UPDATE`)](#1-pessimistic-locking-select--for-update)
    - [2. Optimistic Locking (Application-Level Version Check)](#2-optimistic-locking-application-level-version-check)
    - [3. Atomic Updates (No Explicit Lock Needed)](#3-atomic-updates-no-explicit-lock-needed)
    - [4. `LOCK IN SHARE MODE` (Shared / Read Lock)](#4-lock-in-share-mode-shared--read-lock)
    - [5. Isolation Levels](#5-isolation-levels)
    - [Which Approach Should You Pick?](#which-approach-should-you-pick)
38. [Types of Schedules in DBMS](#types-of-schedules-in-dbms)
    - [Serial Schedule](#1-serial-schedule)
    - [Non-Serial Schedule](#2-non-serial-schedule)
    - [Serializable Schedule](#3-serializable-schedule)
    - [Non-Serializable Schedules](#4-non-serializable-schedules)
    - [Thomas' Write Rule](#thomas-write-rule)
39. [What Is the Meaning of the Word "Relational" in RDBMS?](#what-is-the-meaning-of-the-word-relational-in-rdbms)
40. [MySQL Query Pipeline — Parser, Precompiler & the Cost-Based Optimizer](#mysql-query-pipeline--parser-precompiler--the-cost-based-optimizer)
    - [The Whole Pipeline](#the-whole-pipeline)
    - [Stage 2 — The Parser](#stage-2--the-parser)
    - [Stage 3 — The Preprocessor (the "precompiler" step)](#stage-3--the-preprocessor-the-precompiler-step)
    - [Stage 4 — The Cost-Based Optimizer](#stage-4--the-cost-based-optimizer)
    - [Quick-Fire Q&A](#quick-fire-qa-1)
41. [How to Optimize a SQL Query](#how-to-optimize-a-sql-query)
42. [The Buffer Pool — How Data Actually Flows Between Disk and Memory](#the-buffer-pool--how-data-actually-flows-between-disk-and-memory)
    - [Key Terms — Page, Frame, Dirty, Clean, Pinned](#key-terms--page-frame-dirty-clean-pinned)
    - [The Read Path](#the-read-path--page-hit-vs-page-miss)
    - [The Write Path](#the-write-path--why-a-write-doesnt-touch-the-table-file)
    - [`fsync()` — What "Written to Disk" Really Means](#fsync--what-written-to-disk-actually-means)
    - [Why We Need It](#why-we-need-it--the-latency-gap)
    - [What If We Had No Buffer Pool?](#what-if-we-had-no-buffer-pool)
    - [Eviction — LRU](#eviction--which-page-gets-thrown-out)
43. [File System vs DBMS — Why Do We Need a DBMS at All?](#file-system-vs-dbms--why-do-we-need-a-dbms-at-all)
    - [The 8 Problems with a Plain File System](#the-8-problems-with-a-plain-file-system)
    - [Side-by-Side Comparison](#file-system-vs-dbms--side-by-side-comparison)
    - [When a File System Is Still the Right Choice](#when-a-file-system-is-still-the-right-choice)
44. [Database Partitioning](#database-partitioning)
    - [Vertical Partitioning](#vertical-partitioning)
    - [Horizontal Partitioning](#horizontal-partitioning)
    - [Vertical vs Horizontal Partitioning — Comparison](#vertical-vs-horizontal-partitioning--comparison)
    - [Partition-Based Data Retention (TTL Rotation)](#partition-based-data-retention-ttl-rotation)
    - [Partitioning vs Multiple Tables — Are They the Same?](#partitioning-vs-multiple-tables--are-they-the-same)
45. [Multikey / Composite Sharding (e.g. `user_id` + `order_id`)](#multikey--composite-sharding-eg-user_id--order_id)
    - [Two Different Meanings of "`user_id` + `order_id`"](#two-different-meanings-of-user_id--order_id)
    - [Example Schema on One Shard (same SQL shape everywhere)](#example-schema-on-one-shard-same-sql-shape-everywhere)
    - [SQL Patterns After Sharding](#sql-patterns-after-sharding)
    - [Practical Takeaways](#practical-takeaways)

---

# SQL Commands — DDL, DQL, DML, DCL & TCL

SQL (Structured Query Language) is the standard language for interacting with relational databases. Every operation you perform on a database — querying data, creating tables, inserting rows, managing permissions, or handling transactions — is done through SQL commands.

These commands are categorized into **five distinct groups** based on what they do:

```
                        ┌─────────────────────┐
                        │    SQL Commands      │
                        └─────────┬───────────┘
          ┌───────────┬───────────┼───────────┬───────────┐
          ▼           ▼           ▼           ▼           ▼
       ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
       │ DDL │    │ DQL │    │ DML │    │ DCL │    │ TCL │
       └─────┘    └─────┘    └─────┘    └─────┘    └─────┘
      Structure   Querying   Data       Access     Transaction
      Define      Fetch      Manipulate Control    Control
```

> **Think of it this way:**
> - **DDL** = Building the house (structure)
> - **DQL** = Looking through the windows (reading)
> - **DML** = Moving furniture in/out (modifying data)
> - **DCL** = Giving/taking house keys (permissions)
> - **TCL** = Ensuring the moving truck either delivers everything or nothing (atomicity)

---

## 1. DDL — Data Definition Language

**Purpose:** Define and modify the *structure* (schema) of the database — tables, columns, indexes, constraints, etc.

> **Key idea:** DDL doesn't touch the actual data rows. It deals with the *blueprint* — what tables exist, what columns they have, what types those columns are, etc.

### Commands

| Command | What It Does | Syntax |
|---------|-------------|--------|
| `CREATE` | Creates a new database object (table, index, view, etc.) | `CREATE TABLE table_name (col1 type, col2 type, ...);` |
| `ALTER` | Modifies an existing object's structure | `ALTER TABLE table_name ADD COLUMN col_name type;` |
| `DROP` | Permanently deletes an object from the database | `DROP TABLE table_name;` |
| `TRUNCATE` | Removes **all rows** from a table (but keeps the table structure) | `TRUNCATE TABLE table_name;` |
| `RENAME` | Renames an existing object | `RENAME TABLE old_name TO new_name;` |
| `COMMENT` | Adds a descriptive comment to a table/column in the data dictionary | `COMMENT ON TABLE table_name IS 'text';` |

### Example — Creating a Table

```sql
CREATE TABLE employees (
    employee_id   INT PRIMARY KEY,
    first_name    VARCHAR(50),
    last_name     VARCHAR(50),
    department    VARCHAR(50),
    hire_date     DATE
);
```

This tells the database: *"Create a container called `employees` with these five columns and their data types."*

### TRUNCATE vs DROP vs DELETE — A Common Confusion

| Aspect | `TRUNCATE` | `DROP` | `DELETE` (DML) |
|--------|-----------|--------|----------------|
| Removes rows? | ✅ All rows | ✅ All rows | ✅ Selective or all |
| Removes table structure? | ❌ | ✅ | ❌ |
| Can use WHERE clause? | ❌ | ❌ | ✅ |
| Can be rolled back? | ❌ (auto-commits) | ❌ (auto-commits) | ✅ (within a transaction) |
| Speed | Very fast (deallocates pages) | Fast | Slower (row-by-row logging) |

> **Interview tip:** `TRUNCATE` is a DDL command, not DML, because it operates at the *structure level* (deallocates data pages) rather than deleting rows one-by-one. That's why it's faster and can't be rolled back.

### ALTER Examples

```sql
-- Add a new column
ALTER TABLE employees ADD COLUMN salary DECIMAL(10,2);

-- Modify a column's data type
ALTER TABLE employees MODIFY COLUMN salary BIGINT;

-- Drop a column
ALTER TABLE employees DROP COLUMN salary;

-- Add a constraint
ALTER TABLE employees ADD CONSTRAINT unique_email UNIQUE (email);
```

> **📌 Deeper DDL topics — each now has its own top-level section further down in this file:**
> - [MySQL Data Types](#mysql-data-types) — picking the right column type, and what each one costs
> - [ALTER TABLE in MySQL — Online DDL, Locking & Internals](#alter-table-in-mysql--online-ddl-locking--internals) — what happens internally, `INSTANT` / `INPLACE` / `COPY`, the metadata-lock trap
> - [❓ What is Schema Migration? (Prisma, Django, Rails, etc.)](#-what-is-schema-migration-prisma-django-rails-etc) — version control for your database schema
> - [❓ What Does "Seed a Database" Mean?](#-what-does-seed-a-database-mean) — populating a fresh database with initial/sample data

---

## 2. DQL — Data Query Language

**Purpose:** Retrieve/fetch data from the database. DQL is **read-only** — it never modifies any data.

> **Key idea:** DQL has only ONE command: `SELECT`. Everything else (`FROM`, `WHERE`, `GROUP BY`, etc.) are **clauses** of the `SELECT` statement, not separate commands.

### The SELECT Statement & Its Clauses

| Clause | Purpose | Example |
|--------|---------|---------|
| `SELECT` | Specifies *which columns* to retrieve | `SELECT first_name, salary` |
| `FROM` | Specifies *which table(s)* to read from | `FROM employees` |
| `WHERE` | Filters rows *before* grouping (row-level filter) | `WHERE department = 'Sales'` |
| `GROUP BY` | Groups rows sharing a value, typically for aggregation | `GROUP BY department` |
| `HAVING` | Filters *after* grouping (group-level filter) | `HAVING COUNT(*) > 5` |
| `ORDER BY` | Sorts the result set (ASC by default) | `ORDER BY salary DESC` |
| `DISTINCT` | Removes duplicate rows from the result | `SELECT DISTINCT department` |
| `LIMIT` | Caps the number of rows returned | `LIMIT 10` |

### Logical Order of Execution

This is crucial to understand — SQL does NOT execute in the order you write it:

```
Written Order:          Execution Order:
─────────────          ────────────────
SELECT          →  5.  SELECT / DISTINCT
FROM            →  1.  FROM (& JOINs)
WHERE           →  2.  WHERE
GROUP BY        →  3.  GROUP BY
HAVING          →  4.  HAVING
ORDER BY        →  6.  ORDER BY
LIMIT           →  7.  LIMIT
```

> **Why does this matter?**
> - You **can't** use a column alias defined in `SELECT` inside a `WHERE` clause — because `WHERE` runs *before* `SELECT`.
> - You **can** use it in `ORDER BY` — because `ORDER BY` runs *after* `SELECT`.
> - `WHERE` filters individual rows *before* grouping. `HAVING` filters groups *after* grouping.

### Example

```sql
SELECT department, COUNT(*) AS emp_count
FROM employees
WHERE hire_date > '2023-01-01'
GROUP BY department
HAVING COUNT(*) > 5
ORDER BY emp_count DESC
LIMIT 3;
```

**Step-by-step execution:**
1. **FROM** → look at the `employees` table
2. **WHERE** → keep only rows where `hire_date` is after Jan 1, 2023
3. **GROUP BY** → group the remaining rows by `department`
4. **HAVING** → keep only groups with more than 5 employees
5. **SELECT** → pick the `department` name and the count
6. **ORDER BY** → sort by count descending
7. **LIMIT** → return only the top 3 departments

### WHERE vs HAVING

| | `WHERE` | `HAVING` |
|--|---------|----------|
| Filters | Individual rows | Groups (after `GROUP BY`) |
| Can use aggregate functions? | ❌ No | ✅ Yes |
| Runs | Before grouping | After grouping |
| Example | `WHERE salary > 50000` | `HAVING AVG(salary) > 50000` |

> **📌 Deeper DQL topics — each now has its own top-level section further down in this file:**
> - [❓ MySQL Pagination — OFFSET/LIMIT vs Cursor-Based (Keyset) Pagination](#-mysql-pagination--offsetlimit-vs-cursor-based-keyset-pagination) — deferred joins, keyset pagination, and the API cursor contract
> - [❓ What is the N+1 Query Problem and How to Solve It?](#-what-is-the-n1-query-problem-and-how-to-solve-it) — JOINs, `IN` batching, and ORM eager loading

---

## 3. DML — Data Manipulation Language

**Purpose:** Insert, update, and delete the *actual data* inside the tables.

> **Key idea:** DDL defines the container, DML fills and modifies the contents. DML operations can be rolled back within a transaction (unlike DDL).

### Commands

| Command | What It Does | Syntax |
|---------|-------------|--------|
| `INSERT` | Adds new row(s) into a table | `INSERT INTO table (col1, col2) VALUES (v1, v2);` |
| `UPDATE` | Modifies existing row(s) | `UPDATE table SET col1 = v1 WHERE condition;` |
| `DELETE` | Removes row(s) from a table | `DELETE FROM table WHERE condition;` |

### INSERT Examples

```sql
-- Insert a single row
INSERT INTO employees (first_name, last_name, department)
VALUES ('Jane', 'Smith', 'HR');

-- Insert multiple rows at once
INSERT INTO employees (first_name, last_name, department)
VALUES
    ('Alice', 'Johnson', 'Engineering'),
    ('Bob',   'Brown',   'Marketing'),
    ('Carol', 'Davis',   'Engineering');

-- Insert from another table (useful for backups/migrations)
INSERT INTO employees_archive
SELECT * FROM employees WHERE hire_date < '2020-01-01';
```

### UPDATE Examples

```sql
-- Update specific rows
UPDATE employees
SET department = 'Marketing'
WHERE employee_id = 101;

-- Update multiple columns
UPDATE employees
SET department = 'IT', salary = salary * 1.1
WHERE department = 'Engineering' AND hire_date < '2022-01-01';
```

> ⚠️ **Danger:** Running `UPDATE` or `DELETE` **without a `WHERE` clause** affects ALL rows in the table. Always double-check your `WHERE` conditions.

### DELETE Examples

```sql
-- Delete specific rows
DELETE FROM employees
WHERE department = 'Sales' AND hire_date < '2020-01-01';

-- Delete ALL rows (but table structure remains)
DELETE FROM employees;  -- Can be rolled back, unlike TRUNCATE
```

---

## 4. DCL — Data Control Language

**Purpose:** Manage **permissions and access control** — who can do what on which database objects.

> **Key idea:** In a production database, you don't want every user to have full access. DCL commands let you grant specific privileges (SELECT, INSERT, UPDATE, etc.) to specific users and revoke them when no longer needed.

### Commands

| Command | What It Does | Syntax |
|---------|-------------|--------|
| `GRANT` | Gives a user permission to perform specific actions | `GRANT privilege ON object TO user;` |
| `REVOKE` | Takes back previously granted permissions | `REVOKE privilege ON object FROM user;` |

### Common Privileges

| Privilege | Allows |
|-----------|--------|
| `SELECT` | Read data |
| `INSERT` | Add new rows |
| `UPDATE` | Modify existing rows |
| `DELETE` | Remove rows |
| `ALL PRIVILEGES` | Full access |
| `EXECUTE` | Run stored procedures/functions |
| `CREATE` | Create new objects |

### Examples

```sql
-- Grant read-only access
GRANT SELECT ON employees TO analyst_user;

-- Grant read + write access
GRANT SELECT, INSERT, UPDATE ON employees TO app_user;

-- Grant everything
GRANT ALL PRIVILEGES ON employees TO admin_user;

-- Grant with the ability to pass on the privilege to others
GRANT SELECT ON employees TO team_lead WITH GRANT OPTION;

-- Revoke write access
REVOKE INSERT, UPDATE ON employees FROM app_user;

-- Revoke all access
REVOKE ALL PRIVILEGES ON employees FROM intern_user;
```

### GRANT OPTION & CASCADE

- **`WITH GRANT OPTION`** — allows the grantee to further grant the same privilege to other users (delegation).
- **`CASCADE`** — when revoking, also revokes from anyone who received the privilege through the original grantee.

```
admin  ──GRANT SELECT──▶  team_lead (WITH GRANT OPTION)
                                │
                          GRANT SELECT
                                │
                                ▼
                            developer

-- If admin revokes from team_lead with CASCADE:
REVOKE SELECT ON employees FROM team_lead CASCADE;
-- Both team_lead AND developer lose SELECT access
```

---

## 5. TCL — Transaction Control Language

**Purpose:** Manage **transactions** — groups of SQL statements that must either ALL succeed or ALL fail (atomicity).

> **Key idea:** A transaction is a logical unit of work. Think of transferring money: you debit Account A and credit Account B. If the credit fails, the debit must also be undone. TCL gives you this control.

### Commands

| Command | What It Does | Syntax |
|---------|-------------|--------|
| `BEGIN TRANSACTION` | Starts a new transaction | `BEGIN TRANSACTION;` |
| `COMMIT` | Saves all changes made in the transaction permanently | `COMMIT;` |
| `ROLLBACK` | Undoes all changes made in the transaction | `ROLLBACK;` |
| `SAVEPOINT` | Creates a checkpoint within the transaction to partially roll back to | `SAVEPOINT savepoint_name;` |

### Transaction Lifecycle

```
BEGIN TRANSACTION
       │
       ▼
   ┌───────────────────┐
   │  SQL statements    │
   │  (INSERT, UPDATE,  │
   │   DELETE, etc.)    │
   └────────┬──────────┘
            │
       ┌────┴────┐
       ▼         ▼
   COMMIT    ROLLBACK
   (save)    (undo all)
```

### Example — Bank Transfer

```sql
BEGIN TRANSACTION;

-- Step 1: Debit sender
UPDATE accounts SET balance = balance - 500 WHERE account_id = 'A001';

-- Step 2: Credit receiver
UPDATE accounts SET balance = balance + 500 WHERE account_id = 'B001';

-- If both succeed:
COMMIT;

-- If something went wrong, you would:
-- ROLLBACK;
```

### SAVEPOINT — Partial Rollback

Savepoints let you undo *part* of a transaction without rolling back everything:

```sql
BEGIN TRANSACTION;

UPDATE employees SET department = 'Marketing' WHERE department = 'Sales';
SAVEPOINT sp1;  -- checkpoint here

UPDATE employees SET department = 'IT' WHERE department = 'HR';
-- Oops, this was a mistake!

ROLLBACK TO SAVEPOINT sp1;  -- undo only the HR→IT change
-- The Sales→Marketing change is still intact

COMMIT;  -- save the Sales→Marketing change permanently
```

---

## Quick Reference — All 5 Categories at a Glance

| Category | Full Form | Purpose | Key Commands | Affects |
|----------|-----------|---------|-------------|---------|
| **DDL** | Data Definition Language | Define/modify schema | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` | Structure |
| **DQL** | Data Query Language | Read/fetch data | `SELECT` | Nothing (read-only) |
| **DML** | Data Manipulation Language | Insert/update/delete data | `INSERT`, `UPDATE`, `DELETE` | Data |
| **DCL** | Data Control Language | Manage permissions | `GRANT`, `REVOKE` | Access |
| **TCL** | Transaction Control Language | Manage transactions | `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT` | Transaction state |

> **Auto-commit note:** DDL commands (`CREATE`, `DROP`, `TRUNCATE`) are **auto-committed** — they take effect immediately and cannot be rolled back. DML commands (`INSERT`, `UPDATE`, `DELETE`) can be wrapped in transactions and rolled back if needed.

---
---

# MySQL Data Types

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
---

# ALTER TABLE in MySQL — Online DDL, Locking & Internals

`ALTER TABLE` is the DDL (Data Definition Language) command used to modify an existing table's structure — adding or dropping columns, changing data types, adding indexes, renaming columns, and more. It's one of the most common operations in production databases, and one of the most dangerous if you don't understand its locking behavior.

---

## ❓ What Happens Internally When We Run an ALTER Query? Does It Lock the Table?

**Short answer: it depends on the *algorithm* MySQL picks.** Modern MySQL (5.6+) supports **Online DDL**, which means most `ALTER TABLE` operations **do NOT fully lock** the table — reads and writes can continue while the schema change is happening.

### Before MySQL 5.6 — Full Table Lock (The Old Way)

In older MySQL versions, **every** `ALTER TABLE` operation worked like this:

```
1. Take a FULL TABLE LOCK (no reads or writes allowed)
2. Create a NEW temporary table with the new schema
3. Copy ALL rows from the old table to the new table (row by row)
4. Swap the old table with the new table
5. Drop the old table
6. Release the lock
```

For a table with 500 million rows, this could take **hours** — and during that entire time, **no queries could read or write to the table**. Your application would effectively be down.

### MySQL 5.6+ — Online DDL (The Modern Way)

MySQL 5.6 introduced **Online DDL**, which allows many `ALTER TABLE` operations to proceed **without blocking reads or writes**. MySQL 8.0 expanded this further with `INSTANT` operations.

There are three algorithms MySQL can use:

| Algorithm | How It Works | Locking | Speed |
|---|---|---|---|
| `INSTANT` (MySQL 8.0+) | Only modifies table **metadata** — no data is touched or copied | ⚡ No data lock (metadata lock only, held for microseconds) | Instant — regardless of table size |
| `INPLACE` (MySQL 5.6+) | Modifies data **in place** within the existing tablespace — no full copy | Concurrent reads ✅, concurrent writes ✅ (for most operations) | Proportional to table size, but the table stays online |
| `COPY` (legacy) | Creates a new table, copies all rows, swaps — the old behavior | ❌ Full table lock (or at best, read-only) | Slowest — must copy every row |

MySQL automatically picks the fastest algorithm available for each operation. You can also force one:

```sql
-- Force INSTANT (fails if not possible, instead of silently falling back to COPY)
ALTER TABLE users ADD COLUMN bio TEXT, ALGORITHM=INSTANT;

-- Force INPLACE with no locking at all
ALTER TABLE users ADD INDEX idx_email (email), ALGORITHM=INPLACE, LOCK=NONE;

-- Force COPY (you'd rarely want this)
ALTER TABLE users MODIFY COLUMN name VARCHAR(500), ALGORITHM=COPY;
```

> **Best practice:** Always specify `ALGORITHM` and `LOCK` explicitly in production.
> If the operation can't support your requested algorithm/lock level, MySQL will **fail immediately** instead of silently falling back to a full table copy that blocks your app.

### How Are Concurrent Writes Handled During an INPLACE ALTER?

This is the key internal detail — InnoDB uses an **online log** mechanism:

```
Timeline during ALTER TABLE (INPLACE):
────────────────────────────────────────────────────────────

1. BRIEF METADATA LOCK (exclusive)          ← blocks everything for milliseconds
   └─ MySQL prepares the ALTER operation

2. DDL RUNS (online, concurrent DML allowed)
   ├─ InnoDB rebuilds the table/index in the background
   ├─ Meanwhile, INSERTs/UPDATEs/DELETEs from other connections continue normally
   └─ All concurrent DML changes are captured in a temporary "online log"

3. APPLY ONLINE LOG
   └─ InnoDB replays all buffered DML changes onto the new structure

4. BRIEF METADATA LOCK (exclusive)          ← blocks everything for milliseconds
   └─ Swap old structure with new, update metadata, done!

────────────────────────────────────────────────────────────
Result: Table was altered WITHOUT blocking your application
```

### Which Operations Use Which Algorithm?

| Operation | Algorithm | Concurrent DML? | Notes |
|---|---|:---:|---|
| **Add column (at end)** | `INSTANT` (8.0+) ⚡ | ✅ Yes | Only metadata change — no data rewrite |
| **Add column (at position)** | `INSTANT` (8.0.29+) ⚡ | ✅ Yes | `ALTER TABLE t ADD COLUMN c INT AFTER b` |
| **Drop column** | `INSTANT` (8.0.29+) ⚡ | ✅ Yes | Metadata-only in newer versions |
| **Rename column** | `INSTANT` ⚡ | ✅ Yes | Just a metadata change |
| **Set/drop default value** | `INSTANT` ⚡ | ✅ Yes | Metadata only |
| **Add index** | `INPLACE` | ✅ Yes | Reads table data to build the index, but the table stays writable |
| **Drop index** | `INSTANT` ⚡ | ✅ Yes | Just metadata |
| **Add a foreign key** | `INPLACE` | ✅ Yes | Requires `foreign_key_checks=0` or `LOCK=NONE` |
| **Change `VARCHAR` size (within 255)** | `INPLACE` | ✅ Yes | Growing past the 255-byte length prefix forces a `COPY` |
| **Change column data type** | `COPY` 🐌 | ❌ No | Must rewrite every row — full lock |
| **Convert charset** | `COPY` 🐌 | ❌ No | Must rewrite every row |
| **Add `FULLTEXT` index** | `INPLACE` | ❌ No (blocks writes) | Reads are allowed, writes are blocked |
| **Change `ROW_FORMAT`** | `COPY` 🐌 | ❌ No | Full table rebuild |

### ⚠️ The Metadata Lock (MDL) Trap — This Catches Everyone

Even though the ALTER itself is "online", `INSTANT` and `INPLACE` operations still need a brief **metadata lock** at the start and end. It's usually held for microseconds — but here's the catch.

If there's a **long-running query or uncommitted transaction** on that table, the ALTER will **wait** for the metadata lock. And while the ALTER is waiting, **all new queries queue up behind it**:

```
Connection 1: SELECT * FROM big_table WHERE ...  (running for 30 seconds)
Connection 2: ALTER TABLE big_table ADD COLUMN ...  (WAITING for metadata lock)
Connection 3: SELECT * FROM big_table ...  (BLOCKED — queued behind ALTER!)
Connection 4: INSERT INTO big_table ...   (BLOCKED — queued behind ALTER!)
                ↑
        ALL new queries pile up behind the waiting ALTER
        → Application appears to hang! 💥
```

```
Timeline:
  T=0:   Slow SELECT starts (holds metadata lock in shared mode)
  T=5:   ALTER TABLE runs → waits for metadata lock
  T=5+:  ALL new SELECTs and INSERTs also wait (queue behind ALTER)
  T=30:  Slow SELECT finishes → ALTER gets lock → ALTER completes → everything unblocks

Result: 25 seconds of total downtime, even for an INSTANT ALTER!
```

**Prevention:**

- Set `lock_wait_timeout` so the ALTER gives up instead of blocking everything:

  ```sql
  SET SESSION lock_wait_timeout = 5;  -- Give up after 5 seconds
  ALTER TABLE users ADD COLUMN bio TEXT;
  -- If the metadata lock isn't available in 5 seconds, the ALTER fails
  -- instead of causing a cascading pile-up
  ```

- Kill long-running queries before running the ALTER
- Use `pt-online-schema-change` (Percona) or `gh-ost` (GitHub) for large production tables — these create a shadow copy and swap tables, avoiding metadata-lock issues entirely (see [Production Tools for Zero-Downtime ALTER](#production-tools-for-zero-downtime-alter) below)
- Always run ALTER during low-traffic windows

---

## Advantages of ALTER TABLE

| Advantage | Explanation |
|---|---|
| **Schema evolution** | Lets you adapt your database schema as requirements change — add new features, support new data, without recreating tables |
| **Data integrity** | Adding constraints (`NOT NULL`, `UNIQUE`, `FOREIGN KEY`) via ALTER ensures data quality at the database level |
| **Index management** | You can add or drop indexes to tune query performance based on real-world workload analysis |
| **Online DDL (5.6+)** | Most common operations (add column, add index) can run without downtime in modern MySQL |
| **INSTANT operations (8.0+)** | Adding a column is now instantaneous regardless of table size — just a metadata change |
| **Standardized** | Part of the SQL standard — every developer and ORM knows how to use it |

---

## Disadvantages of ALTER TABLE

| Disadvantage | Explanation |
|---|---|
| **Table lock for some operations** | Changing a column's data type, converting charset, or adding a `FULLTEXT` index still requires a full table copy with a lock — can mean hours of downtime on large tables |
| **Metadata lock cascading** | Even fast operations can cause cascading query pile-ups if a long-running query is holding the metadata lock (explained above) |
| **Replication lag** | On replicas (in statement-based replication), the `ALTER TABLE` runs again from scratch — a 2-hour ALTER on the primary means 2 hours of replication lag |
| **Disk space** | `COPY` and `INPLACE` operations need **extra disk space** equal to the table's size (for the temporary copy or rebuilt data). If your disk is 80% full, the ALTER may fail |
| **Cannot rollback DDL** | `ALTER TABLE` is auto-committed — there's no `ROLLBACK`. If you add a wrong column, you must run another `ALTER TABLE` to fix it |
| **Risk of data loss** | Changing a column from `VARCHAR(200)` to `VARCHAR(50)` silently truncates data. Changing `BIGINT` to `INT` can cause overflow errors |
| **Coordination required** | In large teams, uncoordinated schema changes can break application code that assumes the old schema |
| **Partitioned table overhead** | `ALTER TABLE` on partitioned tables is slower because it must modify every partition's data file |

### Production Tools for Zero-Downtime ALTER

For operations that still require a `COPY`, teams often use external tools that avoid locking:

| Tool | How It Works |
|---|---|
| **`pt-online-schema-change`** (Percona Toolkit) | Creates a new table with the desired schema, uses triggers to copy data and capture live changes, then swaps atomically |
| **`gh-ost`** (GitHub) | Similar concept but uses the binary log instead of triggers — no trigger overhead, more controllable |
| **`fb-mysql-osc`** (Facebook) | Facebook's variant, optimized for their scale |

These tools let you run even a full table rebuild (`COPY` operation) without locking the table — at the cost of additional complexity and longer total execution time.

---

## The "Future Columns" Strategy — Pre-Allocating Columns to Avoid ALTER

One strategy to avoid `ALTER TABLE` entirely is to **pre-create extra columns** upfront that you don't need yet — "reserving" them for future use.

### How It Works

```sql
CREATE TABLE users (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    name         VARCHAR(100),
    email        VARCHAR(255),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Reserved columns for future use
    extra_int_1    INT DEFAULT NULL,
    extra_int_2    INT DEFAULT NULL,
    extra_int_3    INT DEFAULT NULL,
    extra_str_1    VARCHAR(255) DEFAULT NULL,
    extra_str_2    VARCHAR(255) DEFAULT NULL,
    extra_str_3    VARCHAR(255) DEFAULT NULL,
    extra_text_1   TEXT DEFAULT NULL,
    extra_date_1   DATE DEFAULT NULL,
    extra_json_1   JSON DEFAULT NULL
);
```

Later, when you need a new column:

```sql
-- Instead of: ALTER TABLE users ADD COLUMN phone VARCHAR(20);
-- You just START USING an existing column:

-- Application code simply starts reading/writing extra_str_1 as "phone"
-- Maybe rename it for clarity (INSTANT operation, no data copy):
ALTER TABLE users RENAME COLUMN extra_str_1 TO phone;
```

You skip the `ALTER TABLE ADD COLUMN` entirely — the column already exists. You just start writing data to it. If the column's existing type doesn't match what you need exactly, at worst you rename it (which is `INSTANT`).

### Advantages of Future Columns

| Advantage | Explanation |
|---|---|
| **Zero downtime** | No `ALTER TABLE ADD COLUMN` needed — the column is already there. Just start using it. |
| **No metadata lock risk** | Since you're not running DDL, there's no metadata lock contention at all |
| **No replication lag** | Nothing to replicate — the schema hasn't changed |
| **No disk space spike** | No temporary table copy, no extra disk needed |
| **Works on any MySQL version** | Doesn't depend on Online DDL or `INSTANT` algorithm — even MySQL 5.5 works fine |
| **Predictable schema** | DevOps teams know the schema won't change unexpectedly, simplifying migration and deployment pipelines |
| **Good for high-frequency schema iterations** | If your product is evolving rapidly and you'd otherwise ALTER daily, pre-allocated columns save repeated DDL risk |

### Disadvantages of Future Columns

| Disadvantage | Explanation |
|---|---|
| **Unclear schema** | `extra_str_1`, `extra_int_2` are meaningless — developers can't understand the table by looking at the schema. Self-documenting column names are lost |
| **Type mismatch** | You reserved `INT` but now need `DECIMAL(10,2)`? You're stuck — either misuse the column or fall back to `ALTER TABLE` anyway |
| **Wasted storage** | Every `NULL` column in InnoDB costs 1 bit in the null bitmap per row, plus the column metadata. For `VARCHAR`/`TEXT` columns, the overhead is minimal when `NULL`, but it still adds up across billions of rows |
| **Row size bloat** | InnoDB has a row size limit (~8 KB for inline data). Pre-allocating many columns eats into this budget, especially if you reserve wide `VARCHAR` columns |
| **Guessing the future** | You can't predict what data types you'll need. Reserve too few columns → still need ALTER. Reserve too many → waste and confusion. Reserve the wrong types → useless |
| **No constraints** | You can't pre-add `NOT NULL`, `UNIQUE`, or `FOREIGN KEY` constraints on columns whose purpose you don't know yet. Adding these later requires ALTER anyway |
| **ORM and code confusion** | JPA/Hibernate entities would have fields like `extraStr1` and `extraInt2` — confusing to develop with. Column renames help but add churn |
| **Index limitations** | You can't pre-create useful indexes on columns whose query patterns are unknown. Adding indexes later still requires ALTER (though `ADD INDEX` is `INPLACE` and online) |
| **Anti-pattern in relational design** | It violates normalization principles. The schema should describe the data, not anticipate hypothetical future data. This approach trades schema clarity for operational convenience |

### A Better Alternative: The JSON Column Approach

Instead of reserving typed columns, a more flexible "future-proof" strategy is using a single `JSON` column for extensible attributes:

```sql
CREATE TABLE users (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    name         VARCHAR(100),
    email        VARCHAR(255),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    metadata     JSON DEFAULT NULL    -- Extensible attributes live here
);
```

When you need a new field:

```sql
-- No ALTER TABLE needed — just store it in the JSON column
UPDATE users SET metadata = JSON_SET(COALESCE(metadata, '{}'), '$.phone', '+1-555-1234')
WHERE id = 42;

-- Query it:
SELECT id, name, metadata->>'$.phone' AS phone FROM users WHERE id = 42;

-- When you're sure the field is permanent and heavily queried,
-- THEN promote it to a proper column via ALTER TABLE
ALTER TABLE users ADD COLUMN phone VARCHAR(20), ALGORITHM=INSTANT;
UPDATE users SET phone = metadata->>'$.phone' WHERE metadata->>'$.phone' IS NOT NULL;
```

**Why JSON is better than reserved columns:**

| Aspect | Reserved Columns | JSON Column |
|---|---|---|
| New field without ALTER? | ✅ Yes (if matching type exists) | ✅ Yes (always) |
| Type flexibility | ❌ Fixed — must match reserved type | ✅ Any type — strings, numbers, arrays, nested objects |
| Schema clarity | ❌ Poor — `extra_int_1` is meaningless | ⚠️ Moderate — field names are in the JSON keys (`$.phone`) |
| Number of future fields | ❌ Limited by how many you reserved | ✅ Unlimited |
| Query performance | ✅ Regular column — full index support | ⚠️ Slower — JSON extraction has overhead; needs generated columns for indexing |
| Storage efficiency | ⚠️ Null bitmap overhead per reserved column | ✅ Single column — only stores data that exists |
| Indexing | ✅ Standard indexes | ⚠️ Requires virtual generated column + index for fast queries |

**Indexing JSON fields (when they become hot):**

```sql
-- Create a virtual generated column from the JSON field
ALTER TABLE users ADD COLUMN phone VARCHAR(20)
    GENERATED ALWAYS AS (metadata->>'$.phone') VIRTUAL;

-- Index it
CREATE INDEX idx_phone ON users (phone);

-- Now this query uses the index:
SELECT * FROM users WHERE phone = '+1-555-1234';
```

### When to Use Each Strategy

| Scenario | Recommended Approach |
|---|---|
| MySQL 8.0+ with small-to-moderate tables | Just use `ALTER TABLE` with `INSTANT` — adding a column is instantaneous |
| MySQL 8.0+ with massive tables (billions of rows) | `ALTER TABLE` with `INSTANT` for adding columns; `pt-online-schema-change` or `gh-ost` for type changes |
| Rapidly evolving schema (startup, MVP phase) | **JSON column** for experimental fields → promote to real columns when stable |
| Legacy MySQL (5.5 or older) with large tables | Reserved columns may be justified if you truly can't afford the downtime of ALTER |
| Very high-traffic tables where even metadata locks are risky | **JSON column** avoids DDL entirely; combine with `lock_wait_timeout` for any eventual ALTER |

> **The bottom line:** In modern MySQL (8.0+), `ALTER TABLE ADD COLUMN` is `INSTANT` and there is almost **no reason** to pre-allocate future columns. The JSON column approach is strictly better when you need extensibility without DDL. Reserved columns are a legacy workaround from the era of full-table-locking ALTER — they trade schema clarity for a problem that modern MySQL has already solved.

---
---

# ❓ What is Schema Migration? (Prisma, Django, Rails, etc.)

**Schema migration** is the process of **versioning and applying changes to your database schema** (tables, columns, indexes, constraints) in a controlled, repeatable way — just like Git tracks changes to your code, migrations track changes to your database structure.

## The Problem Migrations Solve

Without migrations, schema changes are chaos:

```
❌ WITHOUT MIGRATIONS:
──────────────────────────────────────────────────
Developer A: "I added a 'phone' column to users table on my local DB"
Developer B: "My local DB doesn't have that column... app crashes"
Production:  "Nobody remembers what ALTER statements were run last month"
Staging:     "Is this DB up to date? Who knows 🤷"

✅ WITH MIGRATIONS:
──────────────────────────────────────────────────
Every schema change → a migration file (with timestamp)
Every environment   → runs the SAME migration files in the SAME order
Result: Local DB = Staging DB = Production DB (always in sync)
```

## What Happens Under the Hood When You Run a Migration?

Taking **Prisma** as an example:

```
You change schema.prisma:
  model User {
    id    Int    @id @default(autoincrement())
    name  String
+   phone String?    ← NEW FIELD
  }

Run: npx prisma migrate dev --name add_phone

Under the hood:
──────────────────────────────────────────────────

1. DIFF — Prisma compares your schema.prisma (desired state) 
          vs the actual database (current state)

2. GENERATE SQL — It produces the required SQL:
   → ALTER TABLE users ADD COLUMN phone VARCHAR(191) NULL;

3. SAVE MIGRATION FILE — Creates a timestamped file:
   prisma/migrations/
   └── 20260822_add_phone/
       └── migration.sql    ← contains the ALTER TABLE

4. EXECUTE — Runs the SQL against your database

5. RECORD — Inserts a row into _prisma_migrations table:
   | migration_name       | checksum (SHA256) | applied_at          |
   |---------------------|-------------------|---------------------|
   | 20260822_add_phone  | a3b8f1c2d9...     | 2026-08-22 19:30:00 |
```

## The Migration Tracking Table

Every ORM maintains a **migrations table** inside your database to track which migrations have been applied:

| ORM | Tracking Table | What It Stores |
|-----|:---:|---|
| **Prisma** | `_prisma_migrations` | migration name, checksum (SHA256), timestamp |
| **Django** | `django_migrations` | app name, migration name, timestamp |
| **Rails** | `schema_migrations` | version (timestamp) |
| **Sequelize** | `SequelizeMeta` | migration filename |
| **TypeORM** | `migrations` | migration name, timestamp |
| **Flyway** | `flyway_schema_history` | version, description, checksum, execution time |

**Why the checksum matters (Prisma):** If you edit a migration file that was already applied, the SHA256 hash won't match what's stored in `_prisma_migrations`. Prisma detects this **drift** and refuses to proceed — preventing silent corruption.

## Migration Commands Across ORMs

| Action | Prisma | Django | Rails | Sequelize |
|--------|--------|--------|-------|-----------|
| **Create migration** | `prisma migrate dev` | `python manage.py makemigrations` | `rails generate migration AddPhoneToUsers` | `npx sequelize migration:generate` |
| **Apply migrations** | `prisma migrate deploy` | `python manage.py migrate` | `rails db:migrate` | `npx sequelize db:migrate` |
| **Check status** | `prisma migrate status` | `python manage.py showmigrations` | `rails db:migrate:status` | `npx sequelize db:migrate:status` |
| **Rollback** | ❌ (manual) | `python manage.py migrate app_name 0003` | `rails db:rollback` | `npx sequelize db:migrate:undo` |
| **Reset DB** | `prisma migrate reset` | `python manage.py flush` | `rails db:reset` | `npx sequelize db:migrate:undo:all` |

## What SQL Does a Migration Actually Generate?

```sql
-- Adding a column
ALTER TABLE users ADD COLUMN phone VARCHAR(191) NULL;

-- Adding an index
CREATE INDEX idx_users_email ON users(email);

-- Renaming a column
ALTER TABLE users RENAME COLUMN name TO full_name;

-- Adding a foreign key
ALTER TABLE orders ADD CONSTRAINT fk_user 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Creating a new table
CREATE TABLE posts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  user_id INT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

> Every migration is just **DDL statements** (`ALTER`, `CREATE`, `DROP`) wrapped in a versioned, trackable file.

## Prisma: `migrate dev` vs `db push`

| | `prisma migrate dev` | `prisma db push` |
|--|:---:|:---:|
| **Creates migration files?** | ✅ Yes (versioned SQL) | ❌ No |
| **Uses tracking table?** | ✅ `_prisma_migrations` | ❌ Ignores it |
| **Safe for production?** | ✅ Yes | ❌ No |
| **Best for** | Teams, CI/CD, production | Quick prototyping, throwaway DBs |

> **Key Takeaway:** Schema migration = **version control for your database**. The ORM diffs your desired schema vs the current DB, generates the SQL, saves it in a timestamped file, executes it, and records it in a tracking table. Every environment runs the same migrations in the same order — ensuring your database is always in sync across dev, staging, and production.

---
---

# ❓ What Does "Seed a Database" Mean?

**Seeding** means **populating a database with initial/sample data** so it's not empty after creation. Think of it like planting seeds in a garden — you're putting the initial data in so your app has something to work with.

## Why Do We Need Seeding?

```
After running migrations, your database looks like this:

  ┌──────────────────────────┐
  │  users table             │
  │  ──────────────────────  │
  │  id | name | email       │
  │  ── | ──── | ─────       │
  │     (empty)              │   ← Tables exist but NO data!
  └──────────────────────────┘

After seeding:

  ┌──────────────────────────────────────────────┐
  │  users table                                  │
  │  ────────────────────────────────────────────  │
  │  id | name       | email                      │
  │  1  | Admin User | admin@example.com           │
  │  2  | John Doe   | john@example.com            │
  │  3  | Jane Smith | jane@example.com            │
  └──────────────────────────────────────────────┘
```

**Common use cases for seeding:**

| Use Case | What Gets Seeded | Example |
|----------|-----------------|---------|
| **Default/required data** | Data the app *needs* to function | Admin user, default roles (`admin`, `user`, `moderator`), countries list, categories |
| **Development data** | Fake data to test with locally | 100 fake users, 500 sample products, dummy orders |
| **Testing data** | Predictable data for automated tests | Specific users with known IDs for test assertions |
| **Demo data** | Showcase data for demos/sales | Pre-built dashboards, sample reports |

## How Seeding Works — Raw SQL

At its simplest, seeding is just `INSERT` statements:

```sql
-- Seed roles (required data — app won't work without these)
INSERT INTO roles (name) VALUES ('admin'), ('editor'), ('viewer');

-- Seed admin user
INSERT INTO users (name, email, role_id) 
VALUES ('Admin', 'admin@example.com', 1);

-- Seed categories
INSERT INTO categories (name, slug) VALUES 
  ('Electronics', 'electronics'),
  ('Clothing', 'clothing'),
  ('Books', 'books');
```

## How Seeding Works in Prisma

Prisma uses a dedicated `prisma/seed.ts` (or `.js`) file:

```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Seed roles (upsert = create if not exists, update if exists)
  await prisma.role.upsert({
    where: { name: 'admin' },
    update: {},
    create: { name: 'admin' },
  });

  await prisma.role.upsert({
    where: { name: 'user' },
    update: {},
    create: { name: 'user' },
  });

  // Seed admin user
  await prisma.user.upsert({
    where: { email: 'admin@example.com' },
    update: {},
    create: {
      name: 'Admin User',
      email: 'admin@example.com',
      role: { connect: { name: 'admin' } },
    },
  });

  console.log('✅ Database seeded!');
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
```

```bash
# Run the seed
npx prisma db seed
```

> **Why `upsert`?** It's **idempotent** — you can run the seed multiple times without creating duplicates. If the data already exists, it skips or updates. This is crucial because seeds often run automatically after `prisma migrate reset`.

## Seed Commands Across ORMs

| ORM / Framework | Seed Command | Seed File Location |
|----------------|-------------|-------------------|
| **Prisma** | `npx prisma db seed` | `prisma/seed.ts` |
| **Django** | `python manage.py loaddata fixtures.json` | `app/fixtures/*.json` |
| **Rails** | `rails db:seed` | `db/seeds.rb` |
| **Sequelize** | `npx sequelize db:seed:all` | `seeders/*.js` |
| **Laravel** | `php artisan db:seed` | `database/seeders/*.php` |
| **TypeORM** | Custom script (no built-in) | Your own script |

## Migration vs Seeding — What's the Difference?

| | Migration | Seeding |
|--|:---:|:---:|
| **Changes** | Database **structure** (tables, columns, indexes) | Database **data** (rows) |
| **SQL generated** | `CREATE TABLE`, `ALTER TABLE`, `DROP` | `INSERT INTO`, `UPDATE` |
| **When it runs** | Every environment (dev, staging, prod) | Usually dev/test only |
| **Tracked?** | ✅ Versioned in migration table | ❌ Usually not tracked |
| **Idempotent?** | ✅ (each migration runs once) | Should be (use `upsert` / `INSERT IGNORE`) |

```
Typical workflow:
─────────────────────────────────────────────────

1. prisma migrate dev     → Creates tables (structure)
2. prisma db seed         → Fills tables with initial data
3. Start coding!          → App has data to work with
```

> **Key Takeaway:** Migration creates the **container** (tables/columns). Seeding fills the container with **initial data**. Migrations are mandatory everywhere; seeding is mostly for dev/test environments. Always make seeds idempotent (safe to run multiple times).

---
---

# ❓ MySQL Pagination — OFFSET/LIMIT vs Cursor-Based (Keyset) Pagination

🔗 [PlanetScale — MySQL Pagination](https://planetscale.com/blog/mysql-pagination)

When you have millions of rows and need to show them page by page (like a product listing or infinite scroll feed), **how** you paginate matters enormously.

## Approach 1: OFFSET/LIMIT (The Naïve Way)

```sql
-- Page 1
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 0;

-- Page 2
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 20;

-- Page 500 (💥 SLOW!)
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 10000;
```

**The Problem:** MySQL must **scan and discard** all `OFFSET` rows before returning your `LIMIT` rows. So `OFFSET 10000` means MySQL reads 10,020 rows but throws away 10,000 of them.

```
OFFSET = 0       → Scan 20 rows      → Return 20  ✅ Fast
OFFSET = 1000    → Scan 1,020 rows   → Return 20  🔄 Okay
OFFSET = 100,000 → Scan 100,020 rows → Return 20  🐌 Very slow
OFFSET = 1M      → Scan 1,000,020    → Return 20  💀 Database crying
```

**Other issues with OFFSET/LIMIT:**
- **Data inconsistency** — If a row is inserted or deleted while the user is paginating, they may see **duplicate items** or **skip entries** entirely
- **Performance is O(OFFSET + LIMIT)** — gets linearly worse as you go deeper

## Approach 2: Deferred Join (Keep OFFSET/LIMIT, Just Make It Fast)

> Also known as a **"late row lookup"**. Real-world implementations: [FastPage](https://github.com/planetscale/fast_page) (Rails), [Fast Paginate](https://github.com/hammerstonedev/fast-paginate) (Laravel).

Cursor pagination (Approach 3) is strictly better — **but you can't always use it**. If the product demands numbered pages ("Page 47 of 2,000"), a "jump to last page" button, or a sortable admin grid, you're stuck with `OFFSET`. A **deferred join** keeps `OFFSET/LIMIT` semantics but strips out most of its cost.

### Step 1 — Understand What *Actually* Makes OFFSET Slow

It is **not** the counting. Counting to 450,000 is nothing for a CPU. The real cost is **what MySQL has to carry while it counts**.

Take this query, with an index on `(price, id)`:

```sql
SELECT * FROM products ORDER BY price, id LIMIT 20 OFFSET 450000;
```

Here is what InnoDB actually does, step by step:

```
1. Walk the secondary index (price, id) in sorted order.
   Each index entry is tiny: just [price | id]  ≈ 20 bytes.

2. For EVERY entry it walks — all 450,020 of them — MySQL needs
   the other columns (name, description, stock, created_at...)
   because you asked for SELECT *.
   Those columns are NOT in the index. So for each one it does a
   "bookmark lookup": take the id → descend the clustered (primary
   key) B+ Tree → read the full row.   ← 💀 THE KILLER

3. Hand all 450,020 fully-built rows up to the SQL layer.

4. The SQL layer applies LIMIT/OFFSET *here, at the very top* —
   throws away the first 450,000 rows and returns 20.
```

> **The critical detail:** MySQL applies `LIMIT`/`OFFSET` at the **top** of the execution plan, *after* rows have been materialized. It does **not** push "skip 450,000" down into the index scan. So every single skipped row still pays for a full random-I/O row fetch — and is then discarded.

### Step 2 — The Fix: Paginate the Index, Then Fetch the Rows

Split the query into two halves:

1. **The narrow half** — find *which* 20 IDs you need, touching only the index.
2. **The wide half** — fetch full rows for **only those 20 IDs**.

```sql
-- ✅ DEFERRED JOIN
SELECT p.*
FROM products AS p
INNER JOIN (
    SELECT id                    -- ← only the PK, nothing else
    FROM products
    ORDER BY price, id
    LIMIT 20 OFFSET 450000
) AS page USING (id)
ORDER BY p.price, p.id;          -- ← must repeat! (see gotchas)
```

**Query walkthrough, line by line:**

| Part | What it does | Why it matters |
|---|---|---|
| `SELECT id FROM products ORDER BY price, id` | The **inner/derived** query. Selects *only* the primary key. | Every column it needs (`price`, `id`) lives inside the index `(price, id)` → this is a **covering index scan**. MySQL never touches the table data at all. `EXPLAIN` shows `Using index`. |
| `LIMIT 20 OFFSET 450000` | Does the skipping **here**, on index entries. | Skipping 450,000 × ~20-byte entries that sit packed and pre-sorted in the same index pages. Sequential reads, no random I/O, no row assembly. |
| `AS page` | Names the derived table (MySQL requires an alias). | The `LIMIT` inside also **prevents MySQL from merging** this subquery back into the outer query — it's forced to materialize it first. That's exactly what we want. |
| `INNER JOIN products AS p USING (id)` | Joins those 20 IDs back to the real table. | 20 primary-key lookups. **Not 450,020.** |
| `ORDER BY p.price, p.id` (outer) | Re-sorts the final result. | A `JOIN` gives **no ordering guarantee** — dropping this returns the right 20 rows in the wrong order. Sorting 20 rows is free. |

### Step 3 — Why This Is *Actually* Faster (The Numbers)

`products` = 1M rows, avg row ≈ 600 bytes (name, description, etc.), index entry ≈ 20 bytes.

| | ❌ Naïve `OFFSET 450000` | ✅ Deferred Join |
|---|---|---|
| Index entries walked | 450,020 | 450,020 *(same!)* |
| **Full-row lookups** | **450,020** | **20** |
| Data actually read | ~450,020 × 600 B ≈ **270 MB** | ~450,020 × 20 B ≈ **9 MB** + 20 rows |
| I/O pattern | Random B+ Tree descents | Sequential scan within index pages |
| Rows returned | 20 | 20 |

**~30× less data, and almost none of it random I/O.** PlanetScale's benchmark shows deferred joins staying near-flat across 2,000 pages while plain offset degrades badly.

Verify it yourself with `EXPLAIN`:

```sql
-- The expensive half
EXPLAIN SELECT * FROM products ORDER BY price, id LIMIT 20 OFFSET 450000;
--   key: idx_price_id | rows: 450020 | Extra: (empty)
--   ↑ no "Using index"  → table lookups ARE happening

-- The cheap half (the deferred join's subquery)
EXPLAIN SELECT id FROM products ORDER BY price, id LIMIT 20 OFFSET 450000;
--   key: idx_price_id | rows: 450020 | Extra: Using index
--   ↑ "Using index" = COVERING → never touches the table  🎉
```

`Using index` in the `Extra` column is the whole trick. If you don't see it in your subquery, the deferred join won't help — your index doesn't cover the `ORDER BY`.

### 📚 The Analogy — The Library Card Catalog

You want the books ranked **#450,001 to #450,010** in alphabetical order by author.

```
❌ NAÏVE OFFSET — "carry every book to the desk"
────────────────────────────────────────────────────────────
Walk the stacks in order. For EVERY book, physically pull it
off the shelf, carry it to the front desk, look at it, say
"not yet", and walk it back to its shelf.
Do this 450,000 times. Then keep the last 10.

You are hauling encyclopedias across the building just to
count to 450,000.


✅ DEFERRED JOIN — "flip the cards, then fetch 10 books"
────────────────────────────────────────────────────────────
Go to the CARD CATALOG. One drawer. Thin cards, already
sorted by author, each card says only:
        "author name  →  shelf B-42"

Flip through 450,000 cards — fast, they're thin, ordered,
and all in one drawer you never leave. Read the 10 shelf
numbers you need. THEN walk into the stacks and pull
exactly 10 books.
```

The mapping is one-to-one:

| 📚 Library | 🗄️ MySQL |
|---|---|
| The card catalog drawer | The secondary index `(price, id)` — small, sorted, densely packed |
| One index card | One index entry: `[sort column \| primary key]` |
| The shelf number written on the card | The **primary key** stored in every InnoDB secondary index leaf |
| The actual book (heavy, 400 pages) | The **full row** in the clustered index |
| Walking into the stacks to fetch a book | A random B+ Tree descent by PK — **the expensive part** |
| Flipping through cards in one drawer | Sequential index scan — cheap |
| Repeating the sort after fetching | The outer `ORDER BY` (books come back in shelf order, not author order) |

> **The punchline:** The card catalog does **not** make the counting shorter — you still flip 450,000 cards. It makes **each count cheaper**. That single sentence *is* the deferred join.

### What Deferred Joins Do NOT Fix

This is a **constant-factor** optimization, not an algorithmic one — an important distinction for interviews:

| ⚠️ Still broken | Explanation |
|---|---|
| **Still O(OFFSET)** | You went from "walk 450K entries + fetch 450K rows" to "walk 450K entries". Page 5,000,000 will *still* hurt. Only cursor pagination (Approach 3) makes it O(log N). |
| **Still has duplicates/skips** | If someone inserts a product while the user browses, offsets shift. Deferred joins fix *speed*, not *correctness under concurrent writes*. |
| **Needs a covering index** | If `ORDER BY` can't be served by an index, the subquery does a `filesort` over the whole table anyway and you gain almost nothing. |
| **Two round trips of work** | Slightly more complex SQL, and the optimizer occasionally misbehaves on old MySQL versions — always `EXPLAIN` it. |

### When It's Worth It

| Situation | Verdict |
|---|:---:|
| Wide rows — many columns, `TEXT`/`BLOB`/JSON | 🔥 **Huge win** — that's exactly the payload you stop hauling |
| Deep offsets (> 10,000) | ✅ Win, and it grows with depth |
| Shallow offsets (< 1,000) | ⚪ Not worth the complexity |
| Narrow table (`id`, `user_id`, `status` only) | ⚪ Little to defer — rows are already tiny |
| Query already selects only indexed columns | ❌ No gain — you're *already* doing the fast half |
| `ORDER BY` has no usable index | ❌ Little gain — the subquery still sorts everything |
| You can switch to cursors instead | ✅ **Do that** — deferred joins are the fallback, not the goal |

> **Tip:** Prefer `INNER JOIN (...) USING (id)` over `WHERE id IN (SELECT ...)`. The `IN` form can trigger semi-join materialization strategies that lose the optimization on some MySQL versions.

## Approach 3: Cursor-Based / Keyset Pagination (The Right Way)

Instead of saying "skip N rows", you say "give me rows **after** this specific value":

```sql
-- Page 1 (first request, no cursor yet)
SELECT * FROM products ORDER BY id ASC LIMIT 20;
-- Returns rows with id: 1, 2, 3, ... 20
-- Last id = 20 → this becomes the "cursor" for the next page

-- Page 2 (cursor = 20)
SELECT * FROM products WHERE id > 20 ORDER BY id ASC LIMIT 20;
-- Returns rows with id: 21, 22, ... 40
-- MySQL jumps DIRECTLY to id=20 using the index → O(log N)

-- Page 500 (cursor = 9980)
SELECT * FROM products WHERE id > 9980 ORDER BY id ASC LIMIT 20;
-- Still just as fast! MySQL seeks to id=9980 in the B+ Tree index
```

**Why it's fast:** The `WHERE id > cursor` uses the **B+ Tree index** to jump directly to the right position — no scanning, no discarding. Performance is **O(log N)** regardless of how deep you are.

### Handling Non-Unique Sort Columns

If you're sorting by a non-unique column (like `price`), you need a **tiebreaker** to avoid skipping/duplicating rows with the same value:

```sql
-- ❌ WRONG — rows with same price can be skipped or duplicated
SELECT * FROM products WHERE price > 29.99 ORDER BY price ASC LIMIT 20;

-- ✅ CORRECT — use (price, id) as a compound cursor
SELECT * FROM products 
WHERE (price > 29.99) OR (price = 29.99 AND id > 1042)
ORDER BY price ASC, id ASC 
LIMIT 20;
```

### The API Contract — What You Send the Frontend, What the Frontend Sends Back

Cursor pagination only works if the **client and server agree on a contract**. This is the part interviews actually probe, and it's where most implementations go wrong.

**The round trip:**

```
FRONTEND                                 BACKEND
────────                                 ───────
1. First load — NO cursor
   GET /api/products?limit=20    ────▶   SELECT * FROM products
                                          ORDER BY price, id
                                          LIMIT 21;      ← note: limit + 1
                                          
                                         Got 21 rows → there IS more.
                                         Return 20, build cursor from row #20.
                                         
   ◀────  { data: [20 items],
            next_cursor: "eyJwcmlj...",
            has_more: true }

2. User scrolls / clicks "Load More"
   Echo the cursor back VERBATIM
   GET /api/products?limit=20
       &cursor=eyJwcmlj...        ────▶   Decode cursor → { price: 29.99, id: 1042 }
                                          
                                          SELECT * FROM products
                                          WHERE (price > 29.99)
                                             OR (price = 29.99 AND id > 1042)
                                          ORDER BY price, id
                                          LIMIT 21;
                                          
   ◀────  { data: [20 items],
            next_cursor: "eyJwcmlj...",
            has_more: true }

3. Last page
   ◀────  { data: [7 items],
            next_cursor: null,     ← null = you've hit the end
            has_more: false }
```

**➡️ What the BACKEND sends to the frontend:**

```json
{
  "data": [
    { "id": 1042, "name": "Wireless Mouse", "price": 29.99 },
    { "id": 1043, "name": "USB-C Hub",      "price": 30.50 }
  ],
  "pagination": {
    "next_cursor": "eyJ2IjoxLCJzb3J0IjoicHJpY2VfYXNjIiwicHJpY2UiOiIyOS45OSIsImlkIjoxMDQyfQ==",
    "has_more": true,
    "limit": 20
  }
}
```

| Field | Purpose | Notes |
|---|---|---|
| `data` | The actual page of rows | Always exactly `limit` rows (or fewer on the last page) |
| `next_cursor` | **Opaque** token pointing at the last row of this page | `null` when there are no more pages. The frontend must treat this as a **black box** |
| `has_more` | Is there a next page? | Drives whether the UI shows "Load More" / keeps the infinite scroll alive |
| `limit` | Echo of the page size actually used | Server clamps it (e.g. max 100) so a client can't ask for `limit=1000000` |

**⬅️ What the FRONTEND sends to the backend:**

```
# Page 1 — cursor is simply ABSENT (not empty string, not "null")
GET /api/products?limit=20&sort=price_asc

# Page 2+ — echo back next_cursor exactly as received
GET /api/products?limit=20&sort=price_asc&cursor=eyJ2IjoxLCJzb3J0Ijoi...
```

| Frontend rule | Why |
|---|---|
| **Omit `cursor` on the first page** | Absence of a cursor *is* the signal for "start from the beginning" |
| **Send `next_cursor` back verbatim** — never decode, edit, or construct it | It's opaque by design. If clients start parsing it, you can never change the sort key or add a tiebreaker without breaking them |
| **Resend the same `sort` + filters with every page** | The cursor is only valid for the exact query it was minted under |
| **Reset to page 1 (drop the cursor) whenever a filter or sort changes** | An old cursor means nothing under a new sort order |
| **Stop when `next_cursor` is `null`** | Don't rely on `data.length < limit` alone |

**🔍 What's actually INSIDE the cursor?**

Every column in your `ORDER BY`, in order — the sort key **plus the tiebreaker**. Nothing more:

```json
{ "v": 1, "sort": "price_asc", "price": "29.99", "id": 1042 }
```
↓ `base64(JSON)` ↓
```
eyJ2IjoxLCJzb3J0IjoicHJpY2VfYXNjIiwicHJpY2UiOiIyOS45OSIsImlkIjoxMDQyfQ==
```

| Key | Why it's in there |
|---|---|
| `price`, `id` | The actual position — feeds straight into the `WHERE` clause |
| `sort` | So the server can **reject** a cursor sent with a mismatched sort (`400 Bad Request`) instead of silently returning garbage rows |
| `v` | Version. When you change the cursor format next quarter, old in-flight cursors can be rejected cleanly instead of crashing your decoder |

> **Three production notes:**
> 1. **Base64 is encoding, not encryption.** Anyone can decode it. Never put secrets (user IDs of *other* users, internal flags) inside. If clients tampering with cursors is a concern, append an **HMAC signature** and verify it server-side.
> 2. **Fetch `limit + 1` rows to compute `has_more`.** One extra row costs nothing. A separate `SELECT COUNT(*)` costs a full scan — never do that just to fill in a boolean.
> 3. **For backwards pagination**, return a `prev_cursor` too. The frontend sends it as `?before=...`, and the server flips the comparison (`<` instead of `>`), flips the `ORDER BY` to `DESC`, then **re-reverses the rows in application code** before returning them.

### ⚠️ Problems with Cursor-Based Pagination

Cursor pagination is the right default for large datasets, but it is **not free**. Know these before you commit:

| # | Problem | Detail |
|---|---|---|
| 1 | **No "jump to page N"** | There is no `?page=47`. You can only walk forward/backward one page at a time. If the product needs numbered pages or a "last page" button, cursors are simply the wrong tool — use a [deferred join](#approach-2-deferred-join-keep-offsetlimit-just-make-it-fast) instead |
| 2 | **No total count** | "Showing 1–20 of 8,432 results" needs a separate `COUNT(*)`, which is a full scan on large tables — the exact cost you were trying to avoid. Most cursor APIs just drop the total, or show an approximate count |
| 3 | **Mutable sort columns break it** | Sorting by `price`? If a product's price changes from `10.00` to `500.00` mid-scroll, the user can see it **twice** (or never). Cursors are only truly stable on **immutable** sort keys like `id` or `created_at` |
| 4 | **Ties silently corrupt results** | Sorting on a non-unique column without a tiebreaker skips or duplicates rows — and it fails *quietly*, with no error. Always append the PK: `ORDER BY price, id` |
| 5 | **Every sort option needs its own index** | User-selectable sorts (price ↑, price ↓, newest, rating) each need their own composite index **and** their own cursor shape. `DESC` also flips the `WHERE` from `>` to `<`. This multiplies quickly |
| 6 | **Can't sort by computed/unindexed values** | `ORDER BY RAND()`, a live relevance score, or `ORDER BY (a + b)` cannot be cursor-paginated — there's no index to seek into. The sort key must be a real, indexed, stored column |
| 7 | **Ugly multi-column `WHERE`** | Three sort columns means a nested `OR` chain that's painful to write and easy to get wrong. MySQL **8.0.14+** supports the cleaner row-value form `WHERE (price, id) > (29.99, 1042)` and optimizes it as a range scan — on older versions it degrades to a full scan, so verify with `EXPLAIN` |
| 8 | **Backwards pagination is extra work** | Requires a mirrored query (`<`, `DESC`) plus re-reversing rows in the application layer. Roughly doubles the pagination code |
| 9 | **Bad for SEO / shareable URLs** | `?cursor=eyJ2IjoxLCJz...` isn't a stable, guessable, crawlable URL. Search engines can't reach page 50 of your catalog. Public, indexable listings often still need offset-based URLs |
| 10 | **Harder to debug and test** | Opaque tokens mean you can't eyeball a URL and know where you are. Reproducing a bug report means decoding the cursor first |

> **Not a problem (common misconception):** "What if the row the cursor points to gets deleted?" — Nothing breaks. `WHERE id > 1042` is a **value comparison**, not a row reference. If row `1042` is gone, the index seek simply lands on the next row after that position. This is precisely why cursors beat offsets on stability.

## Comparison

| | OFFSET/LIMIT | Deferred Join | Cursor-Based (Keyset) |
|--|:---:|:---:|:---:|
| **Performance** | Degrades with depth — O(OFFSET + LIMIT) | Still O(OFFSET), but ~10–30× smaller constant | Constant — O(log N) always |
| **What it optimizes** | Nothing | Avoids fetching rows it will discard | Avoids *reading* skipped rows entirely |
| **Data consistency** | ❌ Duplicates/skips if data changes | ❌ Same problem — it's still OFFSET | ✅ Stable for inserts/deletes (⚠️ not if the sort *value* changes) |
| **"Jump to page X"** | ✅ Easy (`OFFSET = (page-1) * size`) | ✅ Yes — keeps full OFFSET semantics | ❌ Not natively supported |
| **Total count available** | ✅ Yes (with a `COUNT(*)`) | ✅ Yes | ❌ Expensive / usually omitted |
| **Index requirement** | Helps, but OFFSET still scans | **Must** have an index covering the `ORDER BY` | **Must** have an index on the cursor columns |
| **UX style** | Numbered pages (1, 2, 3...) | Numbered pages, but fast | Infinite scroll / "Load More" |
| **Implementation** | Simple | Simple (SQL-only change, API unchanged) | Moderate (cursor encode/decode + API contract) |
| **Best for** | Admin panels, small datasets, static reports | Numbered-page UIs on large tables; wide rows | APIs, feeds, infinite scroll, large datasets |

> **Rule of Thumb:**
> - **< 10K rows** or need page numbers? → OFFSET/LIMIT is fine
> - **Need numbered pages *and* the table is large?** → **Deferred join** — it's a pure SQL change, your API contract doesn't move
> - **> 100K rows** or infinite scroll? → Always use cursor-based pagination
> - **Production API serving millions of rows?** → Cursor-based is the **only** sane choice
>
> **The one-line summary:** *Deferred join makes each skipped row cheaper. Cursor pagination stops skipping rows altogether.*

---

## Worked Implementation — Chat Messages (MySQL + Spring Boot)

The same keyset idea applied end to end against a real schema: messages inside a
conversation, from the SQL through to the repository and service layer.

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

> 🔗 Do not confuse this with a **SQL cursor** (`DECLARE ... CURSOR`), which is a
> server-side row-by-row iteration feature. See [Cursor in SQL](#cursor-in-sql).

---
---

# ❓ What is the N+1 Query Problem and How to Solve It?

🔗 [PlanetScale — What is N+1 Query Problem and How to Solve It](https://planetscale.com/blog/what-is-n-1-query-problem-and-how-to-solve-it)

The **N+1 query problem** is one of the most common performance killers in database-backed applications. It happens when your code executes **1 query** to fetch a list of parent records, and then **N additional queries** (one per parent) to fetch related child data.

## The Problem — A Concrete Example

Say you want to display 100 authors with their books:

```
❌ N+1 WAY (101 queries!)
──────────────────────────────────────────────────────

Query 1 (the "1"):
  SELECT * FROM authors;                          -- Returns 100 authors

Query 2 (the "N" — one per author):
  SELECT * FROM books WHERE author_id = 1;        -- Books for author 1
  SELECT * FROM books WHERE author_id = 2;        -- Books for author 2
  SELECT * FROM books WHERE author_id = 3;        -- Books for author 3
  ...
  SELECT * FROM books WHERE author_id = 100;      -- Books for author 100

Total: 1 + 100 = 101 queries 💀
Each query = 1 network round trip to the database
```

With 100 authors, this is 101 queries. With 10,000 authors → 10,001 queries. **Each query involves a separate network round trip**, so even if each query is fast (1ms), 10,001 queries = **10 seconds** of just network overhead.

## Solution 1: Use a JOIN (Best — 1 Query)

Fetch everything in a **single query** using a JOIN:

```sql
-- ✅ 1 query — gets ALL authors and ALL their books at once
SELECT a.name, b.title
FROM authors a
LEFT JOIN books b ON a.id = b.author_id;
```

MySQL fetches everything in one round trip. The database does the heavy lifting instead of your application code.

## Solution 2: Batch with IN Clause (2 Queries)

If a JOIN creates too many duplicate rows (e.g., authors with many books), use two queries with an `IN` clause:

```sql
-- Query 1: Get all authors
SELECT * FROM authors;

-- Query 2: Get ALL books for ALL those authors in ONE query
SELECT * FROM books WHERE author_id IN (1, 2, 3, ..., 100);
```

**Total: 2 queries** instead of 101. Your application code then groups the books by `author_id` in memory.

## Solution 3: ORM Eager Loading

Most ORMs have built-in solutions that generate the optimized queries for you:

| Framework | Lazy Loading (❌ N+1) | Eager Loading (✅ Fixed) |
|-----------|:---:|:---:|
| **Hibernate (Java)** | `author.getBooks()` in a loop | `JOIN FETCH` or `@EntityGraph` |
| **Django (Python)** | `author.books.all()` in a loop | `.select_related()` / `.prefetch_related()` |
| **Rails (Ruby)** | `author.books` in a loop | `.includes(:books)` |
| **Entity Framework (.NET)** | Navigation property access | `.Include(a => a.Books)` |
| **Sequelize (Node.js)** | `author.getBooks()` in a loop | `{ include: [Book] }` |

## How to Detect N+1 in Your App

```
Signs you have an N+1 problem:
─────────────────────────────────────────────────

1. Query logs show the SAME query template repeating hundreds of times
   e.g., "SELECT * FROM books WHERE author_id = ?" × 500

2. Page load time increases LINEARLY with the number of records
   10 authors → 100ms,  100 authors → 1s,  1000 authors → 10s

3. Database connection pool is exhausted under normal load

4. Your ORM is configured with "lazy loading" as default
```

> **Key Takeaway:** Never query inside a loop. If you're doing `for each parent → query children`, you have an N+1 problem. Always **batch** your queries using JOINs, IN clauses, or ORM eager loading.

---
---

# Instance, Schema & Sub-Schema in DBMS

## Instance (Database State)

An **instance** is a **snapshot of the database at a particular moment in time**. It is the actual collection of data stored in the database right now.

> **Think of it this way:** If the database is a photo album, an **instance** is one specific photo taken at one specific moment. Every time you insert, delete, or update a row — the photo changes. You get a new instance.

Every time the data changes (INSERT / DELETE / UPDATE), the database transitions from one instance (state) to another:

```
  Instance at T1         Instance at T2         Instance at T3
 ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
 │ Alice  | HR  │      │ Alice  | HR  │      │ Alice  | IT  │
 │ Bob    | Eng │  ──▶ │ Bob    | Eng │  ──▶ │ Bob    | Eng │
 │              │      │ Carol  | Mkt │      │ Carol  | Mkt │
 └──────────────┘      └──────────────┘      └──────────────┘
    (initial)           (INSERT Carol)        (UPDATE Alice)
```

### Real-World Example — Multiple Instances

An organization's `employees` database typically has three different instances running simultaneously:

| Instance | Purpose |
|----------|---------|
| **Production** | Live data — what users see right now |
| **Pre-production (Staging)** | Used to test new features before pushing to production |
| **Development** | Used by developers to build and test new functionality |

Each of these is at a *different state* (different data) even though they all share the same schema.

> **Important:** The DBMS ensures that **every instance is in a valid state** by enforcing all validations, constraints, and conditions that the database designers have imposed. An instance can never violate the rules defined by the schema.

---

## Schema (Database Design / Blueprint)

🔗 [Tutorialspoint — DBMS Data Schemas](https://www.tutorialspoint.com/dbms/dbms_data_schemas.htm)

A **schema** is the **overall structure or design** of the database. It defines *what* tables exist, *what* columns they have, and *what types* those columns are — but NOT the actual data values.

> **Think of it this way:** Schema = the **frame/blueprint** of a building. Instance = the **people and furniture** currently inside.

**Key points:**
- Schema is the **skeleton structure** of the database — it is designed **before the database exists**
- Once the database is operational, it is **very difficult to change** the schema
- It defines entities (tables), attributes (columns), relationships among them, and **all constraints** to be applied on the data
- A schema **does not contain any data** — only the structure
- **The values in a schema may change, but the structure does not**

### Example Schemas

**STORES table schema:**

| store_name | store_id | store_add | city | state | zip_code |
|------------|----------|-----------|------|-------|----------|
| *(structure only — column definitions, no data)* | | | | | |

**DISCOUNTS table schema:**

| discount_type | store_id | lowqty | highqty | discount |
|---------------|----------|--------|---------|----------|
| *(structure only — column definitions, no data)* | | | | |

> The schema tells you **what information is captured** (store name, address, zip code, discount type, etc.) but says nothing about the actual values or the relationships between these tables.

### Types of Schema

```
              ┌────────────────────────┐
              │    Database Schema     │
              └───────────┬────────────┘
                    ┌─────┴─────┐
                    ▼           ▼
           ┌──────────────┐  ┌──────────────────┐
           │Logical Schema│  │ Physical Schema   │
           │              │  │                   │
           │ What data is │  │ How data is       │
           │ stored and   │  │ actually stored   │
           │ its structure│  │ on disk (files,   │
           │ (tables,     │  │ indexes, pages,   │
           │  columns,    │  │ partitions)       │
           │  types)      │  │                   │
           └──────────────┘  └──────────────────┘
```

| | Logical Schema | Physical Schema |
|--|---------------|-----------------|
| **Concerned with** | Data structure — tables, columns, types, constraints | Storage — how data is stored on disk |
| **Visible to** | Users, application developers | Database administrators, DBMS internals |
| **Can be changed without affecting apps?** | ❌ Changes may break applications | ✅ Can be modified independently |

- The DBMS provides **DDL (Data Definition Language)** to define the logical schema
- The **physical schema is hidden** behind the logical schema — it can be changed (e.g., adding an index, changing storage engine) without affecting application programs

---

## Sub-Schema (External Schema / View)

A **sub-schema** is a **subset of the schema** — it defines what portion of the database a specific user or application can see.

> **Think of it this way:** The full schema is the entire house. A sub-schema is a **window** — each user looks through a different window and sees only the rooms relevant to them.

```
           Full Schema (employees table)
  ┌─────────────────────────────────────────────┐
  │ emp_id | name | dept | salary | SSN | phone │
  └───────────┬──────────────────┬──────────────┘
              │                  │
     ┌────────┴───────┐  ┌──────┴────────┐
     │  Sub-Schema 1  │  │ Sub-Schema 2  │
     │  (HR App)      │  │ (Manager App) │
     │                │  │               │
     │ emp_id, name,  │  │ emp_id, name, │
     │ SSN, salary    │  │ dept          │
     └────────────────┘  └───────────────┘
```

- Different applications have **different views** of the data
- The HR app can see salary and SSN, but the manager app cannot
- This provides **security** (hide sensitive data) and **simplicity** (show only relevant data)

### Quick Summary

| Concept | What It Is | Analogy |
|---------|-----------|---------|
| **Instance** | Snapshot of data at a moment in time | A photo of the building right now |
| **Schema** | Structure/blueprint of the database | The architectural plan of the building |
| **Sub-schema** | A user's partial view of the schema | A window showing only some rooms |

---
---

# Referential Integrity Rule in RDBMS

## What Is Referential Integrity?

🔗 [Tutorialspoint — Referential Integrity Rule in RDBMS](https://www.tutorialspoint.com/Referential-Integrity-Rule-in-RDBMS)

Referential Integrity is a rule that ensures **relationships between tables remain consistent**. Specifically:

> **A foreign key value in one table must either match an existing primary key value in the referenced table, or be NULL.**

In simple words — you can't reference something that doesn't exist.

### The Two Tables Involved

Every referential integrity constraint involves two tables:

| Term | Role |
|------|------|
| **Parent table** (Referenced table) | Contains the **primary key** being referenced |
| **Child table** (Referencing table) | Contains the **foreign key** that points to the parent |

---

## Example — Departments & Employees

### Parent Table: `departments`

| dept_id (PK) | dept_name |
|:---:|:---:|
| 10 | Engineering |
| 20 | Marketing |
| 30 | HR |

### Child Table: `employees`

| emp_id (PK) | emp_name | dept_id (FK) |
|:---:|:---:|:---:|
| 101 | Alice | 10 ✅ |
| 102 | Bob | 20 ✅ |
| 103 | Carol | 30 ✅ |
| 104 | Dave | NULL ✅ |
| 105 | Eve | **50** ❌ |

Let's walk through each row:

- **Alice → dept_id 10** → ✅ Valid. `10` exists in `departments`
- **Bob → dept_id 20** → ✅ Valid. `20` exists in `departments`
- **Carol → dept_id 30** → ✅ Valid. `30` exists in `departments`
- **Dave → dept_id NULL** → ✅ Valid. NULL is allowed (Dave hasn't been assigned to a department yet)
- **Eve → dept_id 50** → ❌ **VIOLATION!** `50` does not exist in `departments`. The database will **reject** this insert.

```
   departments (Parent)              employees (Child)
  ┌─────────┬─────────────┐        ┌────────┬───────┬──────────┐
  │ dept_id │ dept_name   │        │ emp_id │ name  │ dept_id  │
  ├─────────┼─────────────┤        ├────────┼───────┼──────────┤
  │   10    │ Engineering │◀───────│  101   │ Alice │   10 ✅  │
  │   20    │ Marketing   │◀───────│  102   │ Bob   │   20 ✅  │
  │   30    │ HR          │◀───────│  103   │ Carol │   30 ✅  │
  └─────────┴─────────────┘    ╳───│  105   │ Eve   │   50 ❌  │
         ▲                         └────────┴───────┴──────────┘
         │  No dept_id = 50 exists!
         │  REFERENTIAL INTEGRITY VIOLATION
```

---

## What Operations Can Violate Referential Integrity?

### On the Child Table (employees)

| Operation | Violation? | Example |
|-----------|-----------|---------|
| `INSERT` with non-existent FK | ❌ Rejected | `INSERT INTO employees VALUES (105, 'Eve', 50)` — dept 50 doesn't exist |
| `UPDATE` FK to non-existent value | ❌ Rejected | `UPDATE employees SET dept_id = 99 WHERE emp_id = 101` — dept 99 doesn't exist |

### On the Parent Table (departments)

| Operation | Violation? | Example |
|-----------|-----------|---------|
| `DELETE` a row referenced by child | ❌ Rejected (by default) | `DELETE FROM departments WHERE dept_id = 10` — Alice still references dept 10 |
| `UPDATE` PK that is referenced by child | ❌ Rejected (by default) | `UPDATE departments SET dept_id = 99 WHERE dept_id = 10` — Alice still points to 10 |

---

## Handling Violations — ON DELETE & ON UPDATE Actions

When defining a foreign key, you can specify what should happen if the parent row is deleted or updated:

```sql
CREATE TABLE employees (
    emp_id    INT PRIMARY KEY,
    emp_name  VARCHAR(50),
    dept_id   INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON DELETE CASCADE
        ON UPDATE SET NULL
);
```

| Action | On Delete | On Update |
|--------|-----------|-----------|
| **CASCADE** | Delete child rows too | Update child FK values too |
| **SET NULL** | Set child FK to NULL | Set child FK to NULL |
| **SET DEFAULT** | Set child FK to its default value | Set child FK to its default value |
| **RESTRICT / NO ACTION** | Block the delete (default) | Block the update (default) |

### CASCADE Example

If `ON DELETE CASCADE` is set and we delete department 10:

**Before:**

| emp_id | emp_name | dept_id |
|:---:|:---:|:---:|
| 101 | Alice | 10 |
| 102 | Bob | 20 |
| 103 | Carol | 30 |

```sql
DELETE FROM departments WHERE dept_id = 10;
```

**After (CASCADE):** Alice is automatically deleted:

| emp_id | emp_name | dept_id |
|:---:|:---:|:---:|
| 102 | Bob | 20 |
| 103 | Carol | 30 |

### SET NULL Example

If `ON DELETE SET NULL` is set and we delete department 10:

**After (SET NULL):** Alice's dept_id becomes NULL:

| emp_id | emp_name | dept_id |
|:---:|:---:|:---:|
| 101 | Alice | NULL |
| 102 | Bob | 20 |
| 103 | Carol | 30 |

---

## Summary

| Rule | Description |
|------|-------------|
| **Referential Integrity** | FK must match an existing PK in the parent table, or be NULL |
| **Purpose** | Prevent orphan records and ensure data consistency across related tables |
| **Enforced by** | `FOREIGN KEY` constraint in table definition |
| **Violation handling** | `CASCADE`, `SET NULL`, `SET DEFAULT`, or `RESTRICT` |

> **Interview tip:** Referential integrity is one of the two key integrity rules in RDBMS. The other is **Entity Integrity** — which states that the primary key can never be NULL. Together they ensure the database remains consistent and meaningful.

---
---

# Foreign Key Referential Actions (`ON DELETE` / `ON UPDATE`)

When you normalize a database, you split data into multiple related tables connected by **foreign keys**. A new question arises: *"What should happen to child rows when their referenced parent row is deleted or updated?"* Foreign key **referential actions** answer this question.

---

## Setup Example

```sql
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
```

Here, `employees.dept_id` → `departments.id`. Departments is the **parent**, employees is the **child**.

---

## All 5 Referential Actions

### 1. `CASCADE` — Propagate the change to children

**`ON DELETE CASCADE`** — When a parent row is deleted, **automatically delete all child rows** that reference it.

```sql
DELETE FROM departments WHERE id = 3;
-- ✅ All employees with dept_id = 3 are automatically deleted too
```

**`ON UPDATE CASCADE`** — When the parent's primary key is updated, **automatically update the foreign key** in all child rows.

```sql
UPDATE departments SET id = 30 WHERE id = 3;
-- ✅ All employees with dept_id = 3 are automatically changed to dept_id = 30
```

### 2. `SET NULL` — Set child FK to NULL

**`ON DELETE SET NULL`** — When the parent is deleted, set the FK column in child rows to `NULL`.

```sql
FOREIGN KEY (dept_id) REFERENCES departments(id) ON DELETE SET NULL

DELETE FROM departments WHERE id = 3;
-- Employees with dept_id = 3 now have dept_id = NULL (unassigned)
```

> ⚠️ The FK column **must allow NULLs** (`NOT NULL` will cause this to fail).

**Use case:** The employee still exists but is temporarily unassigned to a department.

### 3. `RESTRICT` — Block the operation (default)

**`ON DELETE RESTRICT`** — If any child rows reference the parent, **refuse to delete** the parent. Throws an error immediately.

```sql
FOREIGN KEY (dept_id) REFERENCES departments(id) ON DELETE RESTRICT

DELETE FROM departments WHERE id = 3;
-- ❌ ERROR 1451: Cannot delete or update a parent row:
-- a foreign key constraint fails
```

You must manually delete or reassign all employees first, then delete the department. **This is the default behavior** if you don't specify any action.

### 4. `NO ACTION` — Same as RESTRICT in MySQL

In MySQL, `NO ACTION` behaves **identically** to `RESTRICT`. Both block the operation if child rows exist.

> In some other databases (PostgreSQL), `NO ACTION` checks constraints at the **end of the transaction** (deferrable), while `RESTRICT` checks immediately. MySQL doesn't support deferred checks, so they're the same.

### 5. `SET DEFAULT` — Set FK to its default value

**`ON DELETE SET DEFAULT`** — Sets the FK to its column default value when parent is deleted.

> ⚠️ **InnoDB does NOT support `SET DEFAULT`**. MySQL parses it but will throw an error if you try to use it with InnoDB. This exists mainly in the SQL standard and in other databases.

---

## Side-by-Side Comparison

| Action | On Parent DELETE | On Parent UPDATE | When to Use |
|---|---|---|---|
| **`CASCADE`** | Delete all children | Update FK in all children | Child has no meaning without parent (order items → order) |
| **`SET NULL`** | Set FK to `NULL` | Set FK to `NULL` | Child can exist independently (employee → department) |
| **`RESTRICT`** (default) | ❌ Block the delete | ❌ Block the update | Must handle children explicitly before deleting parent |
| **`NO ACTION`** | Same as RESTRICT in MySQL | Same as RESTRICT in MySQL | Same as above |
| **`SET DEFAULT`** | Set FK to default | Set FK to default | ❌ Not supported in InnoDB |

---

## Real-World Examples

### E-Commerce — `CASCADE` makes sense

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    total DECIMAL(10,2)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT,
    product_name VARCHAR(100),
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES orders(id)
        ON DELETE CASCADE    -- Delete order → delete all its items
);
```

**Why CASCADE?** An order item has **no meaning** without its order. If the order is deleted, keeping orphaned items makes no sense.

### HR System — `SET NULL` makes sense

```sql
CREATE TABLE managers (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT NULL,
    FOREIGN KEY (manager_id) REFERENCES managers(id)
        ON DELETE SET NULL   -- Manager leaves → employees become unassigned
);
```

**Why SET NULL?** Employees don't get fired when their manager leaves. They just temporarily have no manager.

### Banking — `RESTRICT` makes sense

```sql
CREATE TABLE accounts (
    id INT PRIMARY KEY,
    balance DECIMAL(15,2)
);

CREATE TABLE transactions (
    id INT PRIMARY KEY,
    account_id INT,
    amount DECIMAL(10,2),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE RESTRICT   -- Cannot delete account if it has transactions
);
```

**Why RESTRICT?** Financial records must never be silently deleted. You must explicitly handle or archive transactions before closing an account.

---

## What Happens If You Don't Use FK Constraints?

If you don't specify `ON DELETE` / `ON UPDATE`, MySQL defaults to **`RESTRICT`**. But if you skip defining foreign keys entirely, things get worse:

### Problem 1: Orphaned rows (silent data corruption)

```sql
-- No FK defined — just a plain column
CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT,             -- no foreign key constraint!
    product_name VARCHAR(100)
);

DELETE FROM orders WHERE id = 42;
-- ✅ Succeeds... but order_items with order_id = 42 are now ORPHANS
-- They reference a non-existent order
-- JOINs return nothing, reports are wrong, data is silently broken
```

### Problem 2: Manual cleanup everywhere

```sql
-- Without CASCADE, deleting an order requires multiple steps:
DELETE FROM order_items WHERE order_id = 42;    -- Step 1
DELETE FROM order_shipping WHERE order_id = 42; -- Step 2
DELETE FROM order_payments WHERE order_id = 42; -- Step 3
DELETE FROM orders WHERE id = 42;               -- Step 4: FINALLY the parent

-- With CASCADE, it's just:
DELETE FROM orders WHERE id = 42;               -- Done. Everything cleaned up.
```

### Problem 3: Application-level enforcement is fragile

```java
// ❌ Fragile — what if someone runs raw SQL or a migration script?
@Transactional
public void deleteOrder(Long orderId) {
    orderItemRepository.deleteByOrderId(orderId);     // hope you didn't forget
    orderShippingRepository.deleteByOrderId(orderId);  // and this
    orderRepository.deleteById(orderId);
}
```

Anyone who bypasses your application (raw SQL, a DBA, another microservice) can break the data. **Database-level FK constraints are the last line of defense.**

---

## Do FK Actions Fix Anomalies?

**No.** They solve a **different problem**:

| Problem | Cause | Solution |
|---|---|---|
| **Anomalies** (insertion, deletion, update) | Everything crammed into one table with redundant data | **Normalization** — split into multiple tables |
| **Orphaned/inconsistent references** | Multiple tables exist but relationships aren't enforced | **FK constraints** with `CASCADE` / `SET NULL` / `RESTRICT` |

**Normalization** creates the proper multi-table structure (fixing anomalies). **FK actions** then protect that structure from breaking. They're **complementary** — normalization solves the design problem, FK constraints solve the integrity problem.

---

## Quick Decision Guide

| Relationship | Recommended Action | Reason |
|---|---|---|
| Order → Order Items | `ON DELETE CASCADE` | Items are meaningless without the order |
| User → Posts | `ON DELETE CASCADE` or `SET NULL` | CASCADE to remove; SET NULL to keep as "deleted user" |
| Employee → Department | `ON DELETE SET NULL` | Employee survives without a department |
| Account → Transactions | `ON DELETE RESTRICT` | Never silently delete financial records |
| Category → Products | `ON DELETE RESTRICT` | Force admin to reassign products first |
| Comment → Replies | `ON DELETE CASCADE` | Replies to a deleted comment should be removed |
| Parent PK changes | `ON UPDATE CASCADE` | Rare — avoid changing PKs. Use surrogate keys (auto-increment) |

> **Golden rule:** Use `CASCADE` when the child **cannot exist** without the parent. Use `SET NULL` when the child **can exist independently**. Use `RESTRICT` when you want to **force explicit handling** before deletion. And **always define foreign keys** — the alternative (no FK) leads to orphaned data and silent corruption.

---
---

# Three Relationship Types in ER Modeling

Entity-Relationship (ER) diagrams model how entities relate to each other. In practice, almost every design choice — keys, foreign keys, junction tables — follows from the **type of relationship** and whether participation is optional or mandatory.

🔗 [GeeksforGeeks — Introduction of ER Model](https://www.geeksforgeeks.org/dbms/introduction-of-er-model/)

---

## The Three Canonical Types

```
  1:1 (One-to-One)           1:N (One-to-Many)          M:N (Many-to-Many)
  ┌───┐       ┌───┐         ┌───┐       ┌───┐          ┌───┐       ┌───┐
  │ A │───────│ B │         │ A │───┬───│ B │          │ A │──┬──┬─│ B │
  └───┘       └───┘         └───┘   │   └───┘          └───┘  │  │ └───┘
  one A ↔ one B              one A   │   └───┐          many   │  │  many
                                     ├───│ B │            ◀────┘  └────▶
                                     │   └───┘
                                     └───│ B │
                                         └───┘
```

### 1. One-to-One (1:1)

One instance of A relates to **at most one** instance of B, and vice versa.

```
        Person                          Passport
  ┌──────────────────┐            ┌──────────────────┐
  │ person_id (PK)   │            │ passport_id (PK) │
  │ name             │──── 1:1 ───│ passport_no      │
  │ dob              │            │ person_id (FK,UQ) │
  └──────────────────┘            └──────────────────┘

  Alice  ◄────────────►  P12345
  Bob    ◄────────────►  P67890
  Carol  ◄────────────►  P11111
```

**Real example:** Each person has at most one passport; each passport belongs to at most one person.

**How to implement:**
- Put a foreign key on either side with a **UNIQUE constraint**
- Or share the same primary key across both tables

```sql
CREATE TABLE passport (
    passport_id   INT PRIMARY KEY,
    passport_no   VARCHAR(20) NOT NULL,
    person_id     INT UNIQUE NOT NULL,        -- FK + UNIQUE = 1:1
    FOREIGN KEY (person_id) REFERENCES person(person_id)
);
```

> **When do you use 1:1?** It's the rarest type. You use it when:
> - **Security** — separate sensitive data (e.g., salary in a different table)
> - **Sparsity** — only some rows need the extra columns (avoid NULLs)
> - **Lifecycle** — entities are created/deleted at different times

---

### 2. One-to-Many (1:N)

One instance of A relates to **zero or many** instances of B. Each instance of B relates to **at most one** A.

```
     Department                        Employee
  ┌──────────────────┐           ┌──────────────────┐
  │ dept_id (PK)     │           │ emp_id (PK)      │
  │ dept_name        │──── 1:N ──│ emp_name         │
  └──────────────────┘           │ dept_id (FK)     │
                                 └──────────────────┘

  Engineering ──┬──► Alice
                ├──► Bob
                └──► Carol
  Marketing   ──┬──► Dave
                └──► Eve
```

**Real example:** One department has many employees; each employee belongs to one department.

**How to implement:**
- Put a **foreign key on the "many" side** (Employee) referencing the "one" side (Department)

```sql
CREATE TABLE employee (
    emp_id     INT PRIMARY KEY,
    emp_name   VARCHAR(50),
    dept_id    INT NOT NULL,                  -- FK on the N-side
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);
```

> **Tip:** Index the foreign key column (`dept_id`) for better JOIN performance.

#### Many-to-One (N:1) — Just the Inverse View

N:1 is the same relationship as 1:N, just viewed from the other direction:

| Viewpoint | Description |
|-----------|-------------|
| 1:N (Department → Employees) | One department has many employees |
| N:1 (Employees → Department) | Many employees map to one department |

Same table design, same FK — just a different perspective.

---

### 3. Many-to-Many (M:N)

One instance of A relates to **zero or many** instances of B, **and** one instance of B relates to **zero or many** instances of A.

```
     Student                                        Course
  ┌────────────────┐                           ┌────────────────┐
  │ student_id(PK) │                           │ course_id (PK) │
  │ name           │──── M:N ──────────────────│ course_name    │
  └────────────────┘                           └────────────────┘

  Alice ──┬──► DBMS          DBMS    ◄──┬── Alice
          └──► OS            OS      ◄──┼── Alice
  Bob   ──┬──► DBMS                     ├── Bob
          └──► Networks      Networks◄──┘
```

**The problem:** You can't implement M:N directly with a single foreign key. A single FK column can only hold ONE value.

**The solution:** Create an **associative (junction) table** that breaks M:N into two 1:N relationships:

```
     Student              Enrollment              Course
  ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
  │student_id(PK)│    │ student_id (FK)  │    │course_id(PK) │
  │ name         │◄──1:N── course_id(FK) ──N:1──►│ course_name  │
  └──────────────┘    │ grade            │    └──────────────┘
                      │ enrolled_on      │
                      └──────────────────┘
                       (Associative Table)
```

**Enrollment table (the junction):**

| student_id (FK) | course_id (FK) | grade | enrolled_on |
|:---:|:---:|:---:|:---:|
| 1 (Alice) | 101 (DBMS) | A | 2024-01-15 |
| 1 (Alice) | 102 (OS) | B+ | 2024-01-15 |
| 2 (Bob) | 101 (DBMS) | A- | 2024-01-16 |
| 2 (Bob) | 103 (Networks) | B | 2024-01-16 |

```sql
CREATE TABLE enrollment (
    student_id   INT,
    course_id    INT,
    grade        VARCHAR(2),
    enrolled_on  DATE,
    PRIMARY KEY (student_id, course_id),       -- Composite PK
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);
```

> **Key design choice:** Use a composite primary key `(student_id, course_id)` to enforce that a student can't enroll in the same course twice. Alternatively, use a surrogate key and add a UNIQUE constraint on the pair. Store **relationship attributes** (grade, enrollment date) in this junction table — they don't belong to either Student or Course alone.

---

## Cardinality & Participation (Constraints)

When documenting a relationship, specify **two things**:

### 1. Cardinality Ratio — "How many?"

| Ratio | Meaning |
|-------|---------|
| 1:1 | One A → one B |
| 1:N | One A → many B |
| N:1 | Many A → one B |
| M:N | Many A → many B |

### 2. Participation — "Must or may?"

| Type | Meaning | Symbol |
|------|---------|--------|
| **Mandatory** (Total) | Every entity MUST participate | Min = 1 (e.g., `1..*`) |
| **Optional** (Partial) | An entity MAY participate | Min = 0 (e.g., `0..*`) |

```
  Example: Employee MUST belong to a Department (mandatory)
           Department MAY have zero employees (optional)

  Employee ══════════════ Department
  (mandatory/total)       (optional/partial)
  min 1, max 1            min 0, max N

  In UML notation:   Employee [1..1] ──── [0..*] Department
```

**Impact on schema:**
- **Mandatory participation** → use `NOT NULL` on the FK
- **Optional participation** → allow `NULL` on the FK

---

## Notation Cheat Sheet

| Concept | Chen Notation | Crow's Foot | UML |
|---------|:---:|:---:|:---:|
| One | `1` | Single bar `│` | `1` or `0..1` |
| Many | `N` or `M` | Crow's foot `>─` | `*` or `0..*` |
| Mandatory | Annotation | Single bar `│` | Lower bound ≥ 1 (e.g., `1..1`) |
| Optional | Annotation | Open circle `○` | Lower bound = 0 (e.g., `0..1`) |

> **FAQ:** `1..*` (UML) and `1:N` (ER) both mean one-to-many. UML makes optionality explicit via the lower bound (e.g., `0..*` = optional-many vs `1..*` = mandatory-many).

---

## Relational Implementation Patterns — Summary

| Relationship | Where to Put FK | Key Constraints | Notes |
|:---:|---|---|---|
| **1:N** | FK on the N-side referencing the 1-side | `NOT NULL` if mandatory; index the FK | Most common pattern |
| **1:1** | FK on either side with `UNIQUE` constraint | Or share the PK across both tables | Choose based on ownership/optionality |
| **M:N** | Create a junction table with two FKs | Composite PK `(A_id, B_id)` or surrogate key + UNIQUE | Store relationship attributes here |

---

## Everyday Examples

| Type | Example | Implementation |
|:---:|---------|----------------|
| **1:1** | A vehicle has at most one title; a title applies to at most one vehicle | FK with UNIQUE or shared PK |
| **1:N** | A customer places many orders; each order belongs to one customer | FK (`customer_id`) in `orders` table |
| **M:N** | A student enrolls in many classes; a class has many students | Junction table `enrollment(student_id, class_id)` |

> **In real systems**, 1:N and M:N dominate. True 1:1 is rarer and usually modeled for lifecycle, security, or sparsity reasons.

---
---

# Keys in DBMS

Keys are attributes (or sets of attributes) used to **uniquely identify rows**, **establish relationships** between tables, and **enforce data integrity**. Understanding keys is fundamental — they drive every table design decision.

🔗 [PlanetScale — Schema Design 101 for Relational Databases](https://planetscale.com/blog/schema-design-101-relational-databases)

We'll use this single table throughout to explain every key type:

### `students` Table

| roll_no | name | email | phone | dept |
|:---:|:---:|:---:|:---:|:---:|
| 1 | Alice | alice@uni.edu | 9876543210 | CSE |
| 2 | Bob | bob@uni.edu | 9876543211 | ECE |
| 3 | Carol | carol@uni.edu | 9876543212 | CSE |
| 4 | Dave | dave@uni.edu | 9876543213 | ME |

> In this table, `roll_no`, `email`, and `phone` are all unique for each student. `name` and `dept` can repeat.

---

## Key Hierarchy — How They Relate

```
                    ┌──────────────────────────────────┐
                    │          SUPER KEY                │
                    │  Any set of columns that can      │
                    │  uniquely identify a row           │
                    │                                   │
                    │  Examples:                        │
                    │  {roll_no}                        │
                    │  {email}                          │
                    │  {phone}                          │
                    │  {roll_no, name}                  │
                    │  {email, dept}                    │
                    │  {roll_no, name, email, phone}    │
                    └────────────┬─────────────────────┘
                                 │
                        Remove redundant
                        columns (minimal)
                                 │
                    ┌────────────▼─────────────────────┐
                    │       CANDIDATE KEY               │
                    │  Minimal super keys (no extras)   │
                    │                                   │
                    │  {roll_no}                        │
                    │  {email}                          │
                    │  {phone}                          │
                    └──┬──────────────────────┬────────┘
                       │                      │
                Pick one as                Remaining ones
                the identifier             become...
                       │                      │
              ┌────────▼────────┐    ┌────────▼────────┐
              │  PRIMARY KEY    │    │  ALTERNATE KEY   │
              │                 │    │                  │
              │  {roll_no}      │    │  {email}         │
              │  (chosen one)   │    │  {phone}         │
              └─────────────────┘    └──────────────────┘
```

---

## 1. Super Key

A **super key** is any set of one or more columns that can **uniquely identify every row** in a table. It may contain extra (redundant) columns.

> **Think of it as:** "Any combination that is enough to uniquely find a student — even if you're using more columns than necessary."

### Super Keys for `students`:

| Super Key | Unique? | Minimal? |
|-----------|:---:|:---:|
| `{roll_no}` | ✅ | ✅ (also a candidate key) |
| `{email}` | ✅ | ✅ (also a candidate key) |
| `{phone}` | ✅ | ✅ (also a candidate key) |
| `{roll_no, name}` | ✅ | ❌ (`name` is redundant — `roll_no` alone is enough) |
| `{roll_no, email}` | ✅ | ❌ (either one alone works) |
| `{email, dept}` | ✅ | ❌ (`dept` is redundant) |
| `{roll_no, name, email, phone, dept}` | ✅ | ❌ (all columns — way more than needed) |
| `{name}` | ❌ (names can repeat) | — |
| `{dept}` | ❌ (departments repeat) | — |

> **Key point:** Every candidate key is a super key, but NOT every super key is a candidate key. Super keys can have unnecessary extra columns.

---

## 2. Candidate Key

A **candidate key** is a **minimal super key** — it uniquely identifies rows, and removing any column from it would break uniqueness.

> **Think of it as:** "The leanest possible set of columns that still guarantees uniqueness."

### Candidate Keys for `students`:

| Candidate Key | Why it's minimal |
|:---:|---|
| `{roll_no}` | Single column, unique by itself |
| `{email}` | Single column, unique by itself |
| `{phone}` | Single column, unique by itself |

❌ `{roll_no, name}` is NOT a candidate key — remove `name` and `{roll_no}` still works.

> **Interview note:** A table can have multiple candidate keys — they are all "candidates" to become the primary key.

---

## 3. Primary Key

The **primary key** is the **one candidate key chosen** by the designer to be the main identifier for the table.

### Rules for Primary Key:
| Rule | Explanation |
|------|-------------|
| **Unique** | No two rows can have the same PK value |
| **NOT NULL** | PK can never be empty/null |
| **One per table** | Only one primary key allowed per table |
| **Immutable** (best practice) | Should rarely change once set |

### Choosing the Primary Key for `students`:

We have three candidate keys: `{roll_no}`, `{email}`, `{phone}`. Let's compare:

| Candidate | Stable? | Short? | Meaningful? | Choice |
|-----------|:---:|:---:|:---:|:---:|
| `roll_no` | ✅ Never changes | ✅ Integer | ✅ Clear identifier | ✅ **Best choice** |
| `email` | ❌ Students may change email | ❌ Long string | ✅ Readable | ❌ |
| `phone` | ❌ Students may change phone | ❌ Long | ❌ Not meaningful for students | ❌ |

```sql
CREATE TABLE students (
    roll_no   INT PRIMARY KEY,     -- ← Chosen as PK
    name      VARCHAR(50),
    email     VARCHAR(100) UNIQUE,  -- ← Alternate key (enforced)
    phone     VARCHAR(15) UNIQUE,   -- ← Alternate key (enforced)
    dept      VARCHAR(10)
);
```

### Composite Primary Key

Sometimes a single column isn't enough. A **composite PK** uses multiple columns together:

**`enrollment` table:**

| student_id | course_id | grade |
|:---:|:---:|:---:|
| 1 | 101 | A |
| 1 | 102 | B+ |
| 2 | 101 | A- |

Neither `student_id` alone nor `course_id` alone is unique. But `{student_id, course_id}` together is unique → composite PK.

```sql
PRIMARY KEY (student_id, course_id)
```


### Why UUID is Not Preferred as Primary Key

🔗 [PlanetScale — The Problem with Using a UUID Primary Key in MySQL](https://planetscale.com/blog/the-problem-with-using-a-uuid-primary-key-in-mysql)

---

### ❓ Is Declaring a PRIMARY KEY Mandatory in MySQL?

**Technically no. Practically, always yes.**

```sql
CREATE TABLE logs (message VARCHAR(255));   -- perfectly legal, MySQL accepts it
```

But InnoDB builds a clustered index **anyway** — it falls back to a hidden `GEN_CLUST_INDEX` (see [the fallback chain](#-does-declaring-a-key-in-mysql-automatically-create-an-index)). So skipping the PK doesn't avoid the cost. It just means you don't get to choose it, and you can never reference what it built.

#### What Actually Goes Wrong

**1. Replication falls over** — this is the big one

```
Replica applies a row-based DELETE affecting 10,000 rows:

  WITH a primary key    →  10,000 index lookups        ⚡ fast
  WITHOUT a primary key →  10,000 FULL TABLE SCANS     💀 replica lag: hours
```

With row-based binary logging (the default), the replica must **locate** each affected row before applying the change. No PK means no way to find it except scanning. This is the single most common cause of replica lag jumping from milliseconds to hours.

**2. The hidden row ID is a global contention point**

`GEN_CLUST_INDEX` uses a 6-byte `DB_ROW_ID` drawn from a counter **shared by every PK-less table in the entire MySQL instance**, protected by one global mutex. It also wraps silently at 2⁴⁸ and starts overwriting existing rows — no error, no warning, just corruption.

**3. Secondary indexes get poisoned**

Every secondary index appends the clustered key. With a real PK, `INDEX(price)` physically becomes `(price, id)` — which is exactly what makes covering indexes and the [deferred join](#approach-2-deferred-join-keep-offsetlimit-just-make-it-fast) work. Without a PK, it appends a row ID you can't reference, so you lose that benefit entirely.

**4. Tooling refuses to run**

`pt-online-schema-change`, `gh-ost`, Vitess, Debezium/CDC pipelines, and most ORMs all require a primary or unique key. You find this out the day you need an online schema change on a 500M-row table.

#### MySQL Ships Two Switches for This

```sql
-- 8.0.13+ : reject any CREATE TABLE that has no primary key
SET GLOBAL sql_require_primary_key = ON;

-- 8.0.30+ : auto-add an invisible `my_row_id` PK when none is declared
SET GLOBAL sql_generate_invisible_primary_key = ON;
```

Managed platforms (PlanetScale, Vitess, many RDS setups) commonly force `sql_require_primary_key = ON`.

#### The Nuance

If you declared a `UNIQUE NOT NULL` column, InnoDB promotes the first one to clustered index and you're *mostly* fine — but declare it as `PRIMARY KEY` explicitly anyway, so the intent is visible and the tooling recognizes it.

#### The Default That's Always Right

```sql
id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
```

**Sequential, narrow, immutable** — the three properties a clustered index wants. (See above for why UUID fails all three.)

> **Only real exception:** throwaway staging/scratch tables that get truncated wholesale and are never replicated. Even there, adding a PK costs nothing.

---

## 4. Alternate Key

An **alternate key** is any candidate key that was **NOT chosen** as the primary key. They're the "runner-up" identifiers.

### Alternate Keys for `students`:

| Key | Role |
|:---:|---|
| `{roll_no}` | **Primary Key** (chosen) |
| `{email}` | **Alternate Key** (not chosen as PK, but still unique) |
| `{phone}` | **Alternate Key** (not chosen as PK, but still unique) |

> **In practice:** Alternate keys are enforced using `UNIQUE` constraints. They can still be used to look up rows — they're just not the "official" identifier.

```
  Candidate Keys = {roll_no, email, phone}
                        │
              ┌─────────┼──────────┐
              ▼         ▼          ▼
         PRIMARY    ALTERNATE   ALTERNATE
         {roll_no}  {email}     {phone}
```

---

## 5. Foreign Key

A **foreign key** is a column (or set of columns) in one table that **references the primary key of another table**. It creates a link between two tables.

### Example — `students` and `departments`

**`departments` (Parent table):**

| dept_id (PK) | dept_name | hod |
|:---:|:---:|:---:|
| CSE | Computer Science | Dr. Smith |
| ECE | Electronics | Dr. Jones |
| ME | Mechanical | Dr. Brown |

**`students` (Child table):**

| roll_no (PK) | name | email | phone | dept (FK) |
|:---:|:---:|:---:|:---:|:---:|
| 1 | Alice | alice@uni.edu | 9876543210 | CSE ✅ |
| 2 | Bob | bob@uni.edu | 9876543211 | ECE ✅ |
| 3 | Carol | carol@uni.edu | 9876543212 | CSE ✅ |
| 4 | Dave | dave@uni.edu | 9876543213 | ME ✅ |

```
  departments (Parent)              students (Child)
 ┌─────────┬──────────────┐      ┌─────────┬───────┬──────┐
 │ dept_id │ dept_name    │      │ roll_no │ name  │ dept │
 ├─────────┼──────────────┤      ├─────────┼───────┼──────┤
 │  CSE    │ Comp. Sci.   │◄─────│  1      │ Alice │ CSE  │
 │         │              │◄─────│  3      │ Carol │ CSE  │
 │  ECE    │ Electronics  │◄─────│  2      │ Bob   │ ECE  │
 │  ME     │ Mechanical   │◄─────│  4      │ Dave  │ ME   │
 └─────────┴──────────────┘      └─────────┴───────┴──────┘
    PK: dept_id                     FK: dept → dept_id
```

### Foreign Key Properties:

| Property | Description |
|----------|-------------|
| Can have **duplicate values** | Multiple students can be in the same department |
| Can be **NULL** | A student might not be assigned to any department yet |
| Must match a **PK value** in the parent table (or be NULL) | Referential integrity |
| A table can have **multiple FKs** | e.g., `students` could also FK to an `advisor` table |

```sql
CREATE TABLE students (
    roll_no  INT PRIMARY KEY,
    name     VARCHAR(50),
    dept     VARCHAR(10),
    FOREIGN KEY (dept) REFERENCES departments(dept_id)
);
```

---

## 6. Secondary Key (Search Key)

A **secondary key** is any column used frequently for **searching or looking up** data, but which is NOT the primary key. It doesn't need to be unique.

> **Think of it as:** "Not the official ID, but a column you search by often — so you index it for speed."

### Secondary Keys for `students`:

| Column | PK? | Often searched? | Secondary Key? |
|:---:|:---:|:---:|:---:|
| `roll_no` | ✅ PK | — | No (it's the PK) |
| `name` | ❌ | ✅ "Find students named Alice" | ✅ **Secondary Key** |
| `dept` | ❌ | ✅ "Find all CSE students" | ✅ **Secondary Key** |
| `email` | ❌ | Sometimes | Possibly |

**In practice**, you create an **index** on secondary keys to speed up queries:

```sql
-- These columns are searched often, so index them
CREATE INDEX idx_student_name ON students(name);
CREATE INDEX idx_student_dept ON students(dept);
```

> **Key distinction:** Primary/candidate/alternate keys are about **uniqueness and identity**. Secondary keys are about **query performance** — any column you search on frequently.

---

## Complete Summary — All Keys at a Glance

| Key Type | Definition | Unique? | NULL allowed? | Example from `students` |
|----------|-----------|:---:|:---:|:---:|
| **Super Key** | Any column set that uniquely identifies rows (may have extras) | ✅ | — | `{roll_no}`, `{roll_no, name}`, `{email, dept}` |
| **Candidate Key** | Minimal super key (no redundant columns) | ✅ | ❌ | `{roll_no}`, `{email}`, `{phone}` |
| **Primary Key** | The chosen candidate key | ✅ | ❌ | `{roll_no}` |
| **Alternate Key** | Candidate keys not chosen as PK | ✅ | ❌ | `{email}`, `{phone}` |
| **Foreign Key** | References PK of another table | ❌ (can repeat) | ✅ | `dept` → `departments.dept_id` |
| **Secondary Key** | Any column used for frequent searching | ❌ (not required) | ✅ | `name`, `dept` |

### The Relationship Chain

```
  Super Key  ⊇  Candidate Key  =  Primary Key  +  Alternate Key(s)
                                        │
                                 Referenced by
                                        │
                                   Foreign Key (in another table)

  Secondary Key = any frequently searched column (orthogonal concept)
```

> **Interview tip:** The most common question is "What's the difference between a candidate key and a primary key?" Answer: *All* candidate keys are eligible to be the PK. The designer picks ONE → that becomes the PK. The rest become alternate keys.

---

## ❓ Does Declaring a KEY in MySQL Automatically Create an Index?

**Yes — for `PRIMARY KEY`, `UNIQUE`, and `FOREIGN KEY`. Not for anything else.**

First, a naming trap: in MySQL DDL, **`KEY` is literally a synonym for `INDEX`**. These two lines are the same statement:

```sql
KEY   idx_name (name)
INDEX idx_name (name)   -- identical
```

So "key" inside `CREATE TABLE` *is* an index declaration — there's nothing to build separately.

### What Creates an Index vs What Doesn't

| Declaration | Index? | What you actually get |
|---|:---:|---|
| `PRIMARY KEY` | ✅ | The **clustered index** in InnoDB — not a separate structure. The table *is* the index, physically stored in PK order |
| `UNIQUE` / `UNIQUE KEY` | ✅ | A secondary index. MySQL has **no** unique constraint without an index — the index is *how* uniqueness is enforced |
| `FOREIGN KEY` | ✅ | InnoDB **auto-creates** an index on the child column if none exists. The parent column must already have one (usually its PK), or MySQL rejects the constraint |
| `KEY` / `INDEX` | ✅ | The explicit form |
| `CHECK` | ❌ | Constraint only, no structure |
| `NOT NULL`, `DEFAULT` | ❌ | Column attributes, no structure |
| A plain column | ❌ | Nothing |

### See It Yourself

```sql
CREATE TABLE students (
    roll_no  INT          PRIMARY KEY,          -- → clustered index
    email    VARCHAR(100) UNIQUE,               -- → unique secondary index
    phone    VARCHAR(15)  UNIQUE,               -- → unique secondary index
    name     VARCHAR(50)  NOT NULL,             -- → nothing
    age      INT          CHECK (age >= 18),    -- → nothing
    dept_id  INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)  -- → auto-index on dept_id
);
```

```
SHOW INDEX FROM students;

+----------+------------+----------+-------------+
| Table    | Non_unique | Key_name | Column_name |
+----------+------------+----------+-------------+
| students |          0 | PRIMARY  | roll_no     |  ← clustered index
| students |          0 | email    | email       |  ← unique secondary
| students |          0 | phone    | phone       |  ← unique secondary
| students |          1 | dept_id  | dept_id     |  ← auto-created by the FK
+----------+------------+----------+-------------+

4 indexes — and we never typed the word INDEX once.
(Non_unique = 0 means the index enforces uniqueness.)
```

Note what's **missing**: `name`. The summary table above calls it a *secondary key*, but that's relational-theory vocabulary — MySQL creates nothing for it. If you want `WHERE name = ?` to be fast, you must declare `INDEX(name)` yourself.

### Three Things Worth Knowing

**1. No `PRIMARY KEY` declared? InnoDB builds one anyway.**

```
Did you declare a PRIMARY KEY?
   │
   ├── Yes → that becomes the clustered index
   │
   └── No → is there a UNIQUE NOT NULL index?
              │
              ├── Yes → InnoDB promotes the FIRST one to clustered index
              │
              └── No  → InnoDB creates a hidden GEN_CLUST_INDEX over a
                        synthetic 6-byte row ID (DB_ROW_ID) that you can
                        never query, reference, or use in a WHERE clause
```

You **always** have a clustered index. The only question is whether *you* chose it or InnoDB picked one for you.

**2. The FK auto-index is MySQL-specific.** PostgreSQL does **not** index the child column for you. Classic cross-database gotcha — people port a schema, and every join through that FK suddenly falls off a cliff.

**3. Every secondary index secretly ends with the primary key.** In InnoDB, a secondary index leaf stores `[indexed columns | primary key]` — that's how it finds the actual row. So declaring `INDEX(price)` on a table whose PK is `id` gives you an index physically sorted by `(price, id)` for free. Writing `INDEX(price, id)` is redundant.

This is exactly why `SELECT id FROM products ORDER BY price, id` shows `Using index` with only `INDEX(price)` declared — and therefore why the [deferred join](#approach-2-deferred-join-keep-offsetlimit-just-make-it-fast) works.

> **Interview tip:** "Is a key the same as an index?" — **No.** A *key* is a logical constraint (this identifies a row / this must be unique / this references another table). An *index* is a physical B+ Tree structure. MySQL happens to implement most key constraints *using* an index, which is why they're conflated — but you can have an index with no constraint (`INDEX(name)`), and in relational theory a key with no index (`name` as a secondary key).

---
---

# SQL Joins (INNER, LEFT, RIGHT, FULL, CROSS, SELF & NATURAL)

SQL Joins combine rows from two or more tables based on a related column. Without joins, your data would be trapped in isolated tables — joins are how you **reconnect** it.

---

## Sample Data (Used Throughout)

### `Student` Table

| ROLL_NO | NAME | AGE | DEPT |
|:---:|:---:|:---:|:---:|
| 1 | Alice | 20 | CSE |
| 2 | Bob | 21 | ECE |
| 3 | Carol | 20 | CSE |
| 4 | Dave | 22 | ME |

### `StudentCourse` Table

| COURSE_ID | ROLL_NO |
|:---:|:---:|
| C101 | 1 |
| C102 | 2 |
| C103 | 1 |
| C104 | 5 |

> Notice: `ROLL_NO = 5` in `StudentCourse` doesn't exist in `Student` (orphan). `ROLL_NO = 3, 4` in `Student` have no courses.

---

## Join Types — Visual Overview

```
      INNER JOIN              LEFT JOIN              RIGHT JOIN             FULL JOIN
   ┌─────┬─────┐          ┌─────┬─────┐          ┌─────┬─────┐         ┌─────┬─────┐
   │     │█████│          │█████│█████│          │     │█████│         │█████│█████│
   │  A  │█ B █│          │█ A █│█ B █│          │  A  │█ B █│         │█ A █│█ B █│
   │     │█████│          │█████│█████│          │     │█████│         │█████│█████│
   └─────┴─────┘          └─────┴─────┘          └─────┴─────┘         └─────┴─────┘
   Only matching           All of A +              Matching +            All of A +
   rows from both          matching B              all of B              All of B
```

---

## 1. INNER JOIN

Returns **only rows that have matching values in both tables**. Non-matching rows from both sides are excluded.

```sql
SELECT Student.NAME, Student.AGE, StudentCourse.COURSE_ID
FROM Student
INNER JOIN StudentCourse
ON Student.ROLL_NO = StudentCourse.ROLL_NO;
```

> `JOIN` is the same as `INNER JOIN` — the keyword `INNER` is optional.

**How it works — step by step:**

```
Student                    StudentCourse
ROLL_NO | NAME             COURSE_ID | ROLL_NO
--------|------            ----------|--------
  1     | Alice    ──────►   C101    |  1       ✅ match
  1     | Alice    ──────►   C103    |  1       ✅ match
  2     | Bob      ──────►   C102    |  2       ✅ match
  3     | Carol              C104    |  5       ❌ no match (5 not in Student)
  4     | Dave                                  ❌ no match (3,4 not in StudentCourse)
```

**Result:**

| NAME | AGE | COURSE_ID |
|:---:|:---:|:---:|
| Alice | 20 | C101 |
| Alice | 20 | C103 |
| Bob | 21 | C102 |

> Carol, Dave (no courses) and COURSE C104 (ROLL_NO 5 doesn't exist) are all excluded.

---

## 2. LEFT JOIN (LEFT OUTER JOIN)

Returns **all rows from the left table**, plus matching rows from the right table. If no match exists, the right-side columns show **NULL**.

```sql
SELECT Student.NAME, StudentCourse.COURSE_ID
FROM Student
LEFT JOIN StudentCourse
ON Student.ROLL_NO = StudentCourse.ROLL_NO;
```

> `LEFT JOIN` = `LEFT OUTER JOIN` — both are the same.

**How it works:**

```
  Keep ALL from LEFT (Student)     Match from RIGHT (StudentCourse)
  ─────────────────────────────    ─────────────────────────────────
  Alice  (ROLL_NO=1)        ────►  C101, C103    ✅ matched
  Bob    (ROLL_NO=2)        ────►  C102          ✅ matched
  Carol  (ROLL_NO=3)        ────►  NULL          ❌ no course found
  Dave   (ROLL_NO=4)        ────►  NULL          ❌ no course found
```

**Result:**

| NAME | COURSE_ID |
|:---:|:---:|
| Alice | C101 |
| Alice | C103 |
| Bob | C102 |
| Carol | **NULL** |
| Dave | **NULL** |

> Every student appears — even those without courses. C104 (ROLL_NO=5) is NOT shown because ROLL_NO=5 is not in the left table.

---

## 3. RIGHT JOIN (RIGHT OUTER JOIN)

Returns **all rows from the right table**, plus matching rows from the left table. If no match exists, the left-side columns show **NULL**.

```sql
SELECT Student.NAME, StudentCourse.COURSE_ID
FROM Student
RIGHT JOIN StudentCourse
ON Student.ROLL_NO = StudentCourse.ROLL_NO;
```

> `RIGHT JOIN` = `RIGHT OUTER JOIN` — both are the same.

**How it works:**

```
  Match from LEFT (Student)      Keep ALL from RIGHT (StudentCourse)
  ─────────────────────────      ──────────────────────────────────
  Alice    ◄──── ROLL_NO=1 ────  C101    ✅ matched
  Alice    ◄──── ROLL_NO=1 ────  C103    ✅ matched
  Bob      ◄──── ROLL_NO=2 ────  C102    ✅ matched
  NULL     ◄──── ROLL_NO=5 ────  C104    ❌ no student with ROLL_NO=5
```

**Result:**

| NAME | COURSE_ID |
|:---:|:---:|
| Alice | C101 |
| Alice | C103 |
| Bob | C102 |
| **NULL** | C104 |

> Every course appears — even C104 where the student doesn't exist. Carol and Dave don't appear because they have no courses in the right table.

---

## 4. FULL JOIN (FULL OUTER JOIN)

Returns **all rows from both tables**. Matches where possible, fills **NULL** where no match exists.

```sql
SELECT Student.NAME, StudentCourse.COURSE_ID
FROM Student
FULL JOIN StudentCourse
ON Student.ROLL_NO = StudentCourse.ROLL_NO;
```

**How it works:**

```
  LEFT (Student)           RIGHT (StudentCourse)
  ──────────────           ─────────────────────
  Alice (1) ◄──────────►  C101 (1)     ✅ match
  Alice (1) ◄──────────►  C103 (1)     ✅ match
  Bob   (2) ◄──────────►  C102 (2)     ✅ match
  Carol (3) ──────────►   NULL         ❌ no course
  Dave  (4) ──────────►   NULL         ❌ no course
  NULL      ◄──────────   C104 (5)     ❌ no student
```

**Result:**

| NAME | COURSE_ID |
|:---:|:---:|
| Alice | C101 |
| Alice | C103 |
| Bob | C102 |
| Carol | **NULL** |
| Dave | **NULL** |
| **NULL** | C104 |

> Everything from both sides — nothing is lost. This is LEFT JOIN + RIGHT JOIN combined (with duplicates removed).

---

## 5. CROSS JOIN (Cartesian Product)

Returns **every possible combination** of rows from both tables. No `ON` condition needed.

```sql
SELECT Student.NAME, StudentCourse.COURSE_ID
FROM Student
CROSS JOIN StudentCourse;
```

If Student has 4 rows and StudentCourse has 4 rows → result has **4 × 4 = 16 rows**.

```
  Alice × C101,  Alice × C102,  Alice × C103,  Alice × C104
  Bob   × C101,  Bob   × C102,  Bob   × C103,  Bob   × C104
  Carol × C101,  Carol × C102,  Carol × C103,  Carol × C104
  Dave  × C101,  Dave  × C102,  Dave  × C103,  Dave  × C104
```

> ⚠️ **Use with caution** — CROSS JOINs can produce massive result sets. Rarely used in practice, but useful for generating combinations (e.g., all product-color pairs).

---

## 6. SELF JOIN

A table is joined **with itself**. Used when rows in a table have a relationship with other rows in the **same table**.

### Example — Employee & Manager

| emp_id | name | manager_id |
|:---:|:---:|:---:|
| 1 | Alice | NULL |
| 2 | Bob | 1 |
| 3 | Carol | 1 |
| 4 | Dave | 2 |

```sql
SELECT e.name AS Employee, m.name AS Manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.emp_id;
```

**Result:**

| Employee | Manager |
|:---:|:---:|
| Alice | NULL (top-level) |
| Bob | Alice |
| Carol | Alice |
| Dave | Bob |

```
  Alice (CEO)
   ├── Bob
   │    └── Dave
   └── Carol
```

---

## 7. NATURAL JOIN

Automatically joins tables on **all columns with the same name and data type**. No `ON` clause needed — it figures out the join column itself.

### Example

**`Employee` Table:**

| emp_id | emp_name | dept_id |
|:---:|:---:|:---:|
| 1 | Alice | 10 |
| 2 | Bob | 20 |
| 3 | Carol | 10 |

**`Department` Table:**

| dept_id | dept_name |
|:---:|:---:|
| 10 | Engineering |
| 20 | Marketing |
| 30 | HR |

```sql
SELECT emp_name, dept_name
FROM Employee
NATURAL JOIN Department;
```

The database sees `dept_id` exists in both tables → automatically joins on it.

**Result:**

| emp_name | dept_name |
|:---:|:---:|
| Alice | Engineering |
| Bob | Marketing |
| Carol | Engineering |

> ⚠️ **Warning:** NATURAL JOIN is convenient but **dangerous** — if tables share column names by coincidence (e.g., both have a `name` column), the join condition will be wrong. Prefer explicit `INNER JOIN ... ON` in production code.

---

## Quick Reference — All Joins at a Glance

| Join Type | Returns | NULL Filling | Use Case |
|-----------|---------|:---:|---------|
| **INNER JOIN** | Only matching rows | None | "Show students WITH courses" |
| **LEFT JOIN** | All left + matching right | Right side → NULL | "Show ALL students, courses if any" |
| **RIGHT JOIN** | Matching left + all right | Left side → NULL | "Show ALL courses, student if any" |
| **FULL JOIN** | All from both sides | Both sides → NULL | "Show everything, match where possible" |
| **CROSS JOIN** | Every combination (A × B) | None | Generate all possible pairs |
| **SELF JOIN** | Table joined to itself | Depends on join type | Hierarchies (employee-manager) |
| **NATURAL JOIN** | Auto-match on shared column names | None | Quick joins (avoid in production) |

### When to Use Which?

```
  Need ONLY matches?                    → INNER JOIN
  Need ALL from left table?             → LEFT JOIN
  Need ALL from right table?            → RIGHT JOIN
  Need ALL from both tables?            → FULL JOIN
  Need every combination?               → CROSS JOIN
  Need rows related to other rows       → SELF JOIN
  in the SAME table?
```

> **Interview tip:** LEFT JOIN is the most commonly asked in interviews. The typical question is: *"Find all customers who have NOT placed any orders"* → Use `LEFT JOIN` + `WHERE order_id IS NULL`.
>
> ```sql
> SELECT c.name
> FROM customers c
> LEFT JOIN orders o ON c.id = o.customer_id
> WHERE o.id IS NULL;  -- customers with NO orders
> ```

---
---

# SQL Views

A **View** is a **virtual table** created from a `SELECT` query. It does NOT store data physically — it's just a saved query that behaves like a table. Every time you query a view, the underlying `SELECT` runs and fetches fresh data.

> **Think of it this way:** A view is like a **saved bookmark** for a complex query. Instead of writing the same long query every time, you give it a name and reuse it like a table.

```
  Actual Tables (physical)              View (virtual)
 ┌──────────────────┐                 ┌──────────────────┐
 │  StudentDetails  │                 │  DetailsView     │
 │  (stores data)   │────SELECT──────▶│  (no data stored)│
 └──────────────────┘   query         │  just a "window" │
 ┌──────────────────┐    │            │  into the tables │
 │  StudentMarks    │────┘            └──────────────────┘
 │  (stores data)   │
 └──────────────────┘
```

### Why Use Views?

| Benefit | Explanation |
|---------|-------------|
| **Simplify complex queries** | Wrap a 20-line JOIN query into `SELECT * FROM MyView` |
| **Security** | Expose only certain columns/rows to specific users (hide salary, SSN, etc.) |
| **Abstraction** | If table structure changes, update the view — applications don't need to change |
| **Reusability** | Write the logic once, use it everywhere |

---

## Sample Data

### `StudentDetails` Table

| S_ID | NAME | ADDRESS |
|:---:|:---:|:---:|
| 1 | Alice | Delhi |
| 2 | Bob | Mumbai |
| 3 | Carol | Chennai |
| 4 | Dave | Kolkata |
| 5 | Eve | Pune |

### `StudentMarks` Table

| NAME | MARKS | AGE |
|:---:|:---:|:---:|
| Alice | 85 | 20 |
| Bob | 92 | 21 |
| Carol | 78 | 20 |
| Dave | 88 | 22 |

---

## 1. Creating Views

### Syntax

```sql
CREATE VIEW view_name AS
SELECT column1, column2, ...
FROM table_name
WHERE condition;
```

### Example 1 — View from a Single Table

Create a view that shows only students with `S_ID < 5`:

```sql
CREATE VIEW DetailsView AS
SELECT NAME, ADDRESS
FROM StudentDetails
WHERE S_ID < 5;
```

```sql
SELECT * FROM DetailsView;
```

**Result:**

| NAME | ADDRESS |
|:---:|:---:|
| Alice | Delhi |
| Bob | Mumbai |
| Carol | Chennai |
| Dave | Kolkata |

> Eve is excluded because her `S_ID = 5` (not < 5).

### Example 2 — View from Multiple Tables

Create a view that combines student details with their marks:

```sql
CREATE VIEW MarksView AS
SELECT StudentDetails.NAME, StudentDetails.ADDRESS, StudentMarks.MARKS
FROM StudentDetails, StudentMarks
WHERE StudentDetails.NAME = StudentMarks.NAME;
```

```sql
SELECT * FROM MarksView;
```

**Result:**

| NAME | ADDRESS | MARKS |
|:---:|:---:|:---:|
| Alice | Delhi | 85 |
| Bob | Mumbai | 92 |
| Carol | Chennai | 78 |
| Dave | Kolkata | 88 |

> The view pulls from two tables and presents them as one — the user doesn't need to know about the underlying join.

---

## 2. Managing Views

### Listing All Views in a Database

```sql
-- MySQL
SHOW FULL TABLES WHERE table_type LIKE '%VIEW';

-- Using information_schema (works in most RDBMS)
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'your_database_name';
```

### Dropping (Deleting) a View

```sql
DROP VIEW MarksView;
```

> This only removes the view definition — the underlying tables and their data are **not affected**.

### Updating a View Definition — `CREATE OR REPLACE`

If you want to change what a view shows without dropping and recreating it:

```sql
CREATE OR REPLACE VIEW MarksView AS
SELECT StudentDetails.NAME, StudentDetails.ADDRESS,
       StudentMarks.MARKS, StudentMarks.AGE    -- added AGE
FROM StudentDetails, StudentMarks
WHERE StudentDetails.NAME = StudentMarks.NAME;
```

**Updated Result:**

| NAME | ADDRESS | MARKS | AGE |
|:---:|:---:|:---:|:---:|
| Alice | Delhi | 85 | 20 |
| Bob | Mumbai | 92 | 21 |
| Carol | Chennai | 78 | 20 |
| Dave | Kolkata | 88 | 22 |

---

## 3. Modifying Data Through Views

### INSERT Through a View

You can insert data through a view — it actually inserts into the underlying table:

```sql
INSERT INTO DetailsView (NAME, ADDRESS)
VALUES ('John', 'Berlin');
```

The row is inserted into `StudentDetails`. When you query the view, it appears.

### UPDATE Through a View

```sql
UPDATE DetailsView
SET ADDRESS = 'Bangalore'
WHERE NAME = 'Alice';
```

This updates the `ADDRESS` in the underlying `StudentDetails` table.

### DELETE Through a View

```sql
DELETE FROM DetailsView
WHERE NAME = 'John';
```

The row is removed from the underlying `StudentDetails` table.

---

## 4. Rules for Updatable Views

> ⚠️ **Not all views are updatable.** A view can be updated (INSERT/UPDATE/DELETE) only if it meets ALL of these conditions:

| Rule | Why |
|------|-----|
| No `GROUP BY` clause | Aggregated rows can't map back to individual rows |
| No `HAVING` clause | Same reason — it's tied to grouping |
| No `DISTINCT` keyword | Can't determine which duplicate row to update |
| No aggregate functions (`SUM`, `COUNT`, etc.) | Computed values can't be "un-computed" |
| Created from a **single table** | Multi-table views have ambiguous update targets |
| All `NOT NULL` columns must be included | Otherwise INSERT would fail on the base table |
| No subqueries in `SELECT` | Complex derived values can't be reversed |

```
  Updatable View?
  ───────────────
  Single table?        ─── No ──► ❌ Not updatable
       │ Yes
  No GROUP BY/HAVING?  ─── No ──► ❌ Not updatable
       │ Yes
  No DISTINCT?         ─── No ──► ❌ Not updatable
       │ Yes
  No aggregates?       ─── No ──► ❌ Not updatable
       │ Yes
       ▼
  ✅ Updatable!
```

---

## 5. WITH CHECK OPTION

The `WITH CHECK OPTION` clause ensures that any `INSERT` or `UPDATE` through the view **must satisfy the view's WHERE condition**. If the new/updated row would fall outside the view's filter, the operation is **rejected**.

### Example

```sql
CREATE VIEW CSE_Students AS
SELECT S_ID, NAME, ADDRESS
FROM StudentDetails
WHERE ADDRESS = 'Delhi'
WITH CHECK OPTION;
```

```sql
-- ✅ This works — ADDRESS is 'Delhi', satisfies the WHERE
INSERT INTO CSE_Students (S_ID, NAME, ADDRESS)
VALUES (6, 'Frank', 'Delhi');

-- ❌ This FAILS — ADDRESS is 'Mumbai', violates the WHERE
INSERT INTO CSE_Students (S_ID, NAME, ADDRESS)
VALUES (7, 'Grace', 'Mumbai');
-- ERROR: CHECK OPTION failed
```

```
  Without WITH CHECK OPTION:
  ──────────────────────────
  INSERT 'Mumbai' row → ✅ Silently inserted into base table
  But it won't appear in the view (confusing!)

  With WITH CHECK OPTION:
  ──────────────────────────
  INSERT 'Mumbai' row → ❌ Rejected with error
  Guarantees: if you can insert it, you can see it in the view
```

> **Why use it?** Without `WITH CHECK OPTION`, you could insert a row through a view that immediately "disappears" from that view because it doesn't match the `WHERE` clause. This is confusing and error-prone. The check option prevents this.

---

## 6. Views vs Tables — Quick Comparison

| Aspect | Table | View |
|--------|-------|------|
| **Stores data?** | ✅ Yes, physically on disk | ❌ No, just a saved query |
| **Takes storage space?** | ✅ Yes | ❌ No (only the query definition) |
| **Can be indexed?** | ✅ Yes | ❌ Not usually (some RDBMS support materialized views) |
| **Auto-updates when base data changes?** | N/A | ✅ Yes (always shows fresh data) |
| **Can INSERT/UPDATE/DELETE?** | ✅ Always | ⚠️ Only if updatable (see rules above) |
| **Performance** | Direct access | May be slower (runs underlying query each time) |

### Materialized Views (Bonus)

Some databases (PostgreSQL, Oracle) support **materialized views** — these actually **store the query result** physically and need to be **refreshed** periodically:

```sql
-- PostgreSQL
CREATE MATERIALIZED VIEW MatView AS
SELECT dept, COUNT(*) AS emp_count
FROM employees
GROUP BY dept;

-- Refresh when needed
REFRESH MATERIALIZED VIEW MatView;
```

| | Regular View | Materialized View |
|--|---|---|
| Stores data? | ❌ No | ✅ Yes |
| Always up-to-date? | ✅ Yes | ❌ No (must refresh) |
| Fast to query? | ❌ Runs query each time | ✅ Pre-computed |
| Use case | Real-time data | Analytics, dashboards, expensive queries |

> **Interview tip:** "What's the difference between a view and a materialized view?" is a common question. Regular views = virtual (no storage, always fresh). Materialized views = physical snapshot (fast reads, stale until refreshed).

---
---

# SQL Triggers

A **trigger** is a special stored procedure that **runs automatically** when an `INSERT`, `UPDATE`, or `DELETE` (or DDL) operation occurs on a table. You don't call a trigger — it fires on its own when the specified event happens.

> **Think of it this way:** A trigger is like a **motion sensor light** — you don't press a switch; it turns on automatically when it detects movement (an event).

```
  User runs:                          Trigger fires automatically:
  ─────────                           ──────────────────────────
  INSERT INTO users ...    ──────►    Log the insertion to audit_log
  UPDATE employees ...     ──────►    Recalculate total salary
  DELETE FROM orders ...   ──────►    Archive the deleted order
```

### Why Use Triggers?

| Use Case | Example |
|----------|---------|
| **Audit logging** | Record who changed what and when |
| **Auto-update related tables** | Update `total_scores` when `grades` changes |
| **Data validation** | Reject grades outside 0–100 |
| **Enforce business rules** | Prevent deleting a customer with active orders |
| **Auto-fill columns** | Set `updated_at = NOW()` on every update |

---

## Trigger Syntax

```sql
CREATE TRIGGER trigger_name
{BEFORE | AFTER}
{INSERT | UPDATE | DELETE}
ON table_name
FOR EACH ROW
BEGIN
    -- SQL statements
END;
```

| Part | Meaning |
|------|---------|
| `BEFORE / AFTER` | When to fire — before or after the event |
| `INSERT / UPDATE / DELETE` | Which event triggers it |
| `ON table_name` | Which table to watch |
| `FOR EACH ROW` | Fires once per affected row |
| `NEW` | Refers to the **new** row data (INSERT/UPDATE) |
| `OLD` | Refers to the **old** row data (UPDATE/DELETE) |

---

## BEFORE vs AFTER Triggers

| | BEFORE Trigger | AFTER Trigger |
|--|---------------|---------------|
| **When it runs** | Before the row is modified | After the row is modified |
| **Can modify the new data?** | ✅ Yes (`SET NEW.col = value`) | ❌ No (data already saved) |
| **Use case** | Validation, auto-fill, calculations | Logging, updating other tables |

```
  BEFORE Trigger                    AFTER Trigger
  ──────────────                    ─────────────
  User → INSERT                    User → INSERT
            │                                │
     ┌──────▼──────┐                  Row is saved
     │ BEFORE      │                         │
     │ trigger     │                  ┌──────▼──────┐
     │ (validate / │                  │ AFTER       │
     │  modify)    │                  │ trigger     │
     └──────┬──────┘                  │ (log /      │
            │                         │  cascade)   │
     Row is saved                     └─────────────┘
```

---

## Types of SQL Triggers

```
                    ┌──────────────────┐
                    │   SQL Triggers   │
                    └────────┬─────────┘
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌────────────┐
        │   DDL    │  │   DML    │  │   Logon    │
        │ Triggers │  │ Triggers │  │  Triggers  │
        └──────────┘  └──────────┘  └────────────┘
        CREATE/ALTER   INSERT/       User login
        DROP           UPDATE/       events
                       DELETE
```

### 1. DDL Triggers

Fire on **structure changes** — `CREATE`, `ALTER`, `DROP`.

```sql
-- Prevent anyone from dropping tables
CREATE TRIGGER prevent_table_drop
ON DATABASE
FOR CREATE_TABLE, ALTER_TABLE, DROP_TABLE
AS
BEGIN
    PRINT 'You cannot create, alter or drop tables in this database!';
    ROLLBACK;
END;
```

> Useful for protecting production databases from accidental schema changes.

### 2. DML Triggers

Fire on **data changes** — `INSERT`, `UPDATE`, `DELETE`. Most common type.

```sql
-- Prevent all modifications to a sensitive table
CREATE TRIGGER prevent_update
ON students
FOR UPDATE, INSERT, DELETE
AS
BEGIN
    RAISERROR('You cannot modify rows in this table.', 16, 1);
    ROLLBACK TRANSACTION;
END;
```

### 3. Logon Triggers

Fire when a **user logs in**. Used for tracking logins, limiting sessions, or blocking access.

```sql
CREATE TRIGGER track_logon
ON ALL SERVER
FOR LOGON
AS
BEGIN
    PRINT 'A new user has logged in.';
END;
```

---

## Real-World Examples

### Example 1 — Auto-Update Timestamp

Automatically set `updated_at` whenever a user record is modified:

```sql
CREATE TABLE users (
    id         INT PRIMARY KEY,
    name       VARCHAR(50),
    email      VARCHAR(100),
    updated_at TIMESTAMP
);

CREATE TRIGGER update_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END;
```

```sql
INSERT INTO users (id, name, email) VALUES (1, 'Amit', 'amit@example.com');
UPDATE users SET email = 'amit_new@example.com' WHERE id = 1;
```

**Result:** `updated_at` is automatically set — no manual intervention needed.

| id | name | email | updated_at |
|:---:|:---:|:---:|:---:|
| 1 | Amit | amit_new@example.com | 2026-03-04 01:58:00 |

### Example 2 — Data Validation

Reject grades outside the valid range:

```sql
CREATE TRIGGER validate_grade
BEFORE INSERT ON student_grades
FOR EACH ROW
BEGIN
    IF NEW.grade < 0 OR NEW.grade > 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid grade! Must be between 0 and 100.';
    END IF;
END;
```

```sql
INSERT INTO student_grades VALUES (1, 85);   -- ✅ Works
INSERT INTO student_grades VALUES (2, 150);  -- ❌ Rejected: "Invalid grade!"
```

### Example 3 — Auto-Calculate Totals (AFTER INSERT)

Automatically compute total marks and percentage when student marks are inserted:

```sql
CREATE TRIGGER stud_marks
AFTER INSERT ON Student
FOR EACH ROW
BEGIN
    UPDATE Student
    SET
        total = NEW.subj1 + NEW.subj2 + NEW.subj3,
        per = (NEW.subj1 + NEW.subj2 + NEW.subj3) / 3.0
    WHERE tid = NEW.tid;
END;
```

### Example 4 — Audit Log

Track every change to the `employees` table:

```sql
CREATE TABLE employee_audit (
    audit_id    INT AUTO_INCREMENT PRIMARY KEY,
    emp_id      INT,
    action      VARCHAR(10),
    old_salary  DECIMAL(10,2),
    new_salary  DECIMAL(10,2),
    changed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER log_salary_change
AFTER UPDATE ON employees
FOR EACH ROW
BEGIN
    IF OLD.salary <> NEW.salary THEN
        INSERT INTO employee_audit (emp_id, action, old_salary, new_salary)
        VALUES (NEW.emp_id, 'UPDATE', OLD.salary, NEW.salary);
    END IF;
END;
```

| audit_id | emp_id | action | old_salary | new_salary | changed_at |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 101 | UPDATE | 50000.00 | 55000.00 | 2026-03-04 02:00:00 |

---

## Viewing & Managing Triggers

```sql
-- List all triggers (SQL Server)
SELECT name, is_instead_of_trigger
FROM sys.triggers
WHERE type = 'TR';

-- List all triggers (MySQL)
SHOW TRIGGERS;

-- Drop a trigger
DROP TRIGGER trigger_name;

-- Drop a trigger (MySQL - specify table)
DROP TRIGGER IF EXISTS trigger_name;
```

---

## Trigger Summary

| Aspect | Details |
|--------|---------|
| **What** | Auto-executing stored procedure |
| **When** | BEFORE or AFTER an event |
| **Events** | INSERT, UPDATE, DELETE (DML) or CREATE, ALTER, DROP (DDL) |
| **Scope** | FOR EACH ROW or FOR EACH STATEMENT |
| **Access** | `NEW` (new data), `OLD` (old data) |
| **Can modify data?** | BEFORE triggers can modify `NEW`; AFTER triggers cannot |

> **Interview tip:** "What's the difference between a trigger and a stored procedure?" — A stored procedure is **called explicitly** by the user. A trigger **fires automatically** when an event occurs. You can't call a trigger manually.

---
---

# Stored Procedures in SQL

A **stored procedure** is a **precompiled set of SQL statements** saved in the database that you can call by name. Unlike triggers (which fire automatically), stored procedures are **invoked explicitly** by the user or application.

> **Think of it this way:** A stored procedure is like a **function** — you define it once, then call it whenever you need it. It can accept inputs, process data, and return results.

```
  Without Stored Procedure:           With Stored Procedure:
  ─────────────────────────           ──────────────────────
  App sends 10 SQL queries   ──►     App calls one procedure
  over the network                    CALL GetEmployeeReport(101)
  (slow, repetitive)                  (fast, reusable, secure)
```

### Why Use Stored Procedures?

| Benefit | Explanation |
|---------|-------------|
| **Performance** | Precompiled — no need to parse SQL every time |
| **Reusability** | Write once, call from anywhere |
| **Security** | Users call the procedure without knowing table structure |
| **Reduced network traffic** | One call instead of many queries |
| **Maintainability** | Change logic in one place, all callers benefit |

---

## Syntax

```sql
-- Create
CREATE PROCEDURE procedure_name (parameter1 datatype, parameter2 datatype, ...)
BEGIN
    -- SQL statements
END;

-- Call
CALL procedure_name(value1, value2, ...);

-- Drop
DROP PROCEDURE procedure_name;
```

---

## Examples

### Example 1 — Simple Procedure (No Parameters)

```sql
CREATE PROCEDURE GetAllEmployees()
BEGIN
    SELECT * FROM employees;
END;

-- Call it
CALL GetAllEmployees();
```

### Example 2 — Procedure with Input Parameters (IN)

```sql
CREATE PROCEDURE GetEmployeeByDept(IN dept_name VARCHAR(50))
BEGIN
    SELECT emp_id, name, salary
    FROM employees
    WHERE department = dept_name;
END;

-- Call it
CALL GetEmployeeByDept('Engineering');
```

**Result:**

| emp_id | name | salary |
|:---:|:---:|:---:|
| 101 | Alice | 75000 |
| 103 | Carol | 68000 |

### Example 3 — Procedure with Output Parameters (OUT)

```sql
CREATE PROCEDURE CountEmployees(IN dept_name VARCHAR(50), OUT emp_count INT)
BEGIN
    SELECT COUNT(*) INTO emp_count
    FROM employees
    WHERE department = dept_name;
END;

-- Call it
CALL CountEmployees('Engineering', @count);
SELECT @count;   -- Returns: 2
```

### Example 4 — Procedure with IN/OUT Parameter

```sql
CREATE PROCEDURE ApplyRaise(INOUT salary DECIMAL(10,2), IN raise_pct DECIMAL(5,2))
BEGIN
    SET salary = salary + (salary * raise_pct / 100);
END;

-- Call it
SET @sal = 50000;
CALL ApplyRaise(@sal, 10);    -- 10% raise
SELECT @sal;                   -- Returns: 55000.00
```

---

## Parameter Types

| Type | Direction | Description |
|:---:|:---:|---|
| `IN` | Caller → Procedure | Input value (default if not specified) |
| `OUT` | Procedure → Caller | Output value returned to the caller |
| `INOUT` | Both ways | Input that gets modified and returned |

---

## Variables & Control Flow

### Variables

```sql
CREATE PROCEDURE CalculateBonus(IN emp_id INT)
BEGIN
    DECLARE base_salary DECIMAL(10,2);
    DECLARE bonus DECIMAL(10,2);

    SELECT salary INTO base_salary FROM employees WHERE id = emp_id;
    SET bonus = base_salary * 0.10;

    SELECT emp_id, base_salary, bonus;
END;
```

### IF-ELSE

```sql
CREATE PROCEDURE CheckGrade(IN marks INT, OUT result VARCHAR(10))
BEGIN
    IF marks >= 90 THEN
        SET result = 'A';
    ELSEIF marks >= 75 THEN
        SET result = 'B';
    ELSEIF marks >= 60 THEN
        SET result = 'C';
    ELSE
        SET result = 'FAIL';
    END IF;
END;
```

### LOOP / WHILE

```sql
CREATE PROCEDURE InsertNumbers()
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= 10 DO
        INSERT INTO numbers_table (num) VALUES (i);
        SET i = i + 1;
    END WHILE;
END;
```

---

## Stored Procedure vs Function vs Trigger

| Aspect | Stored Procedure | Function | Trigger |
|--------|:---:|:---:|:---:|
| **How it runs** | Called explicitly (`CALL`) | Called in expressions (`SELECT fn()`) | Fires automatically on events |
| **Returns** | Zero or more result sets, OUT params | Exactly one value | Nothing (side effects only) |
| **Can modify data?** | ✅ Yes (INSERT/UPDATE/DELETE) | ❌ Usually no (read-only) | ✅ Yes |
| **Can use transactions?** | ✅ Yes (COMMIT/ROLLBACK) | ❌ No | ⚠️ Limited |
| **Can call each other?** | ✅ Yes | ✅ Yes | ❌ Cannot be called directly |
| **Use case** | Business logic, batch operations | Calculations, transformations | Auto-reactions to data changes |

---

## MySQL Trigger vs Stored Procedure — With Example

| Aspect | Trigger | Stored Procedure |
|---|---|---|
| **Invocation** | Fires **automatically** on `INSERT`/`UPDATE`/`DELETE` | Called **explicitly** with `CALL` |
| **Tied to a table event?** | ✅ Yes — always bound to a table + event | ❌ No — standalone, invoked whenever you want |
| **Accepts parameters?** | ❌ No (only gets `OLD`/`NEW` row values) | ✅ Yes (`IN`, `OUT`, `INOUT`) |
| **Returns values?** | ❌ No | ✅ Yes (`OUT` params, result sets) |
| **Called from application code?** | ❌ No — can't be invoked directly | ✅ Yes (`CALL proc_name(...)`) |
| **Can be forgotten/skipped?** | ❌ No — always runs, guaranteed | ⚠️ Yes — only runs if someone remembers to call it |
| **Typical use case** | Auditing, enforcing rules, keeping derived data in sync | Reusable business logic, batch jobs, reporting |

### Example — Auditing Salary Changes

**Trigger (runs automatically, can't be bypassed):**

```sql
CREATE TABLE salary_audit (
    audit_id    INT AUTO_INCREMENT PRIMARY KEY,
    emp_id      INT,
    old_salary  DECIMAL(10,2),
    new_salary  DECIMAL(10,2),
    changed_at  DATETIME
);

DELIMITER $$
CREATE TRIGGER trg_salary_audit
AFTER UPDATE ON employees
FOR EACH ROW
BEGIN
    IF OLD.salary <> NEW.salary THEN
        INSERT INTO salary_audit (emp_id, old_salary, new_salary, changed_at)
        VALUES (OLD.emp_id, OLD.salary, NEW.salary, NOW());
    END IF;
END$$
DELIMITER ;

-- Any UPDATE on employees.salary auto-logs itself — no extra call needed:
UPDATE employees SET salary = 75000 WHERE emp_id = 101;
```

**Stored Procedure (same result, but must be called explicitly):**

```sql
DELIMITER $$
CREATE PROCEDURE update_salary(IN p_emp_id INT, IN p_new_salary DECIMAL(10,2))
BEGIN
    DECLARE v_old_salary DECIMAL(10,2);

    SELECT salary INTO v_old_salary FROM employees WHERE emp_id = p_emp_id;
    UPDATE employees SET salary = p_new_salary WHERE emp_id = p_emp_id;

    INSERT INTO salary_audit (emp_id, old_salary, new_salary, changed_at)
    VALUES (p_emp_id, v_old_salary, p_new_salary, NOW());
END$$
DELIMITER ;

-- Must be called every time — a plain UPDATE bypasses it entirely:
CALL update_salary(101, 75000);
```

> **Key takeaway:** The trigger guarantees the audit **always** happens, no matter who/what updates `salary` (app code, a manual query, another procedure). The stored procedure only audits if every caller remembers to use `CALL update_salary(...)` instead of a raw `UPDATE` — a developer running `UPDATE employees SET salary = ...` directly would silently skip the audit.

---

## ❓ Why Do Most Companies Avoid Triggers & Stored Procedures and Keep Logic in the Application?

Triggers and stored procedures are powerful — yet most modern product companies (especially at scale) deliberately keep business logic **in the application layer** instead. Here's why.

### 1. Invisible / Hidden Logic — "Spooky Action at a Distance"

A trigger runs **without appearing anywhere in your codebase**. A new developer reads the app code, sees a simple `UPDATE`, and has no idea that three other tables just changed.

```
Developer reads the app code:
    UPDATE employees SET salary = 75000 WHERE emp_id = 101;
    ↓
    "Okay, this just updates one row." ✅ (what they think)

What ACTUALLY happens in the database:
    UPDATE employees ...
      ├─▶ trg_salary_audit      → INSERT into salary_audit
      ├─▶ trg_sync_payroll      → UPDATE payroll table
      └─▶ trg_notify_finance    → INSERT into notification_queue
                                     ↓
                              (another trigger fires!) 💥

Result: Debugging a production issue becomes a nightmare — the cause
        isn't in the code you're reading.
```

### 2. Not Version Controlled with the Code

This is arguably the biggest practical issue:

| | Application Logic | Trigger / Stored Procedure |
|---|---|---|
| **Lives in** | Git repository | Inside the database |
| **Code review** | ✅ Standard PR review | ❌ Often changed via direct SQL, unreviewed |
| **Rollback** | ✅ `git revert` + redeploy | ⚠️ Requires a reverse migration |
| **History / blame** | ✅ Full `git log`, `git blame` | ❌ "Who changed this proc and why?" — no answer |
| **Diff between environments** | ✅ Same commit = same code | ❌ Prod proc may silently differ from staging |

> Even *with* migration tooling, a DBA hotfixing a procedure directly in prod at 2 AM instantly desyncs the database from Git — and nobody finds out until something breaks.

### 3. Testing Is Painful

```
Testing application logic:              Testing a trigger/procedure:
─────────────────────────────           ──────────────────────────────
✅ Plain unit test, no DB needed        ❌ Needs a running database
✅ Mock the dependencies                ❌ Must set up real tables + data
✅ Runs in milliseconds                 ❌ Slow integration test
✅ Runs in CI out of the box            ❌ Needs DB container in CI
✅ Rich assertion libraries             ❌ Assert by querying tables afterwards
✅ Debugger, breakpoints, stack traces  ❌ Very limited debugging tools
```

### 4. Poor Scalability — The Database Is the Hardest Thing to Scale

```
   Application servers                    Database
   ──────────────────                     ────────
   ┌────┐ ┌────┐ ┌────┐ ┌────┐          ┌──────────────┐
   │ #1 │ │ #2 │ │ #3 │ │ #4 │ ...      │   PRIMARY    │  ← usually ONE writer
   └────┘ └────┘ └────┘ └────┘          └──────────────┘
        Add more anytime  ✅               Vertical scaling only  ❌
        (cheap, stateless)                 (expensive, hits a ceiling)
```

CPU spent running procedures and triggers is CPU **stolen from query execution** on your most expensive, least scalable, hardest-to-replace tier. Application servers are cheap and horizontally scalable; the database primary is not.

### 5. Vendor Lock-In

Stored procedure languages are **not portable** — each vendor has its own:

| Database | Procedural Language |
|---|---|
| MySQL | SQL/PSM (MySQL dialect) |
| PostgreSQL | PL/pgSQL |
| Oracle | PL/SQL |
| SQL Server | T-SQL |

Thousands of lines of PL/SQL make migrating off Oracle a multi-year project. Business logic in Java/Python/Go moves to any database.

### 6. Weak Ecosystem & Developer Tooling

| Application Code | Stored Procedures |
|---|---|
| Linters, formatters, static analysis | Almost none |
| Rich IDE support, refactoring tools | Minimal |
| Package managers & libraries (HTTP clients, JSON, crypto, date libs) | Very limited built-ins |
| Easy calls to external services/APIs | Effectively impossible |
| Deep talent pool | Shrinking pool of specialists |

### 7. Hidden Performance & Correctness Traps

```sql
-- Looks harmless: one statement
DELETE FROM orders WHERE order_date < '2020-01-01';   -- 5 million rows

-- But if a FOR EACH ROW trigger exists on orders:
--   → The trigger body executes 5,000,000 times
--   → Each execution may INSERT into an audit table
--   → All inside ONE transaction → huge lock + massive undo log
--   → Table locked for minutes → application times out 💥
```

Other traps: **cascading triggers** (trigger A fires trigger B fires trigger C), triggers silently breaking bulk imports, and trigger failures **rolling back the entire parent transaction** in ways callers never anticipated.

---

### So When ARE They Still the Right Choice?

They're a tool, not an anti-pattern — the argument is about *default placement* of business logic, not a ban.

| Good Use Case | Why It Wins |
|---|---|
| **Audit / history tables** | Must be unbypassable — even manual SQL and other apps get logged |
| **Multiple apps sharing one DB** | Logic enforced once at the DB, not duplicated in 4 codebases |
| **Data integrity constraints** | Rules too complex for `CHECK`/`FOREIGN KEY` but that must never be violated |
| **Legacy / enterprise systems** | Banking, insurance, ERP — decades of proven PL/SQL already in place |
| **Heavy data-local batch work** | Bulk aggregations where shipping millions of rows to the app is far slower |
| **Compliance requirements** | Regulators may require DB-level enforcement, not app-level trust |

### The Modern Consensus

```
Keep in the DATABASE:                Keep in the APPLICATION:
──────────────────────               ────────────────────────
✅ Constraints (PK, FK, UNIQUE,      ✅ Business rules & workflows
   NOT NULL, CHECK)                  ✅ Validation
✅ Indexes                            ✅ Orchestration / external API calls
✅ Transactions                       ✅ Pricing, permissions, state machines
✅ Occasionally: audit triggers       ✅ Anything that changes often
```

> **Key takeaway:** The database should guarantee **data integrity**; the application should own **business logic**. Companies avoid triggers and stored procedures mainly because that logic becomes invisible, untested, un-versioned, unscalable, and vendor-locked — not because the features are bad. Declarative constraints (`FOREIGN KEY`, `UNIQUE`, `CHECK`) are the exception: always push those into the database.

> **Interview tip:** Answer with the trade-off, not a blanket rule — "Most teams keep logic in the app because it's version-controlled, testable, horizontally scalable, and portable, while the DB primary is the hardest tier to scale. But I'd still use a trigger for audit logging that must be unbypassable, and I always enforce integrity with database constraints rather than app code alone."

---

## Viewing & Managing Procedures

```sql
-- List all procedures (MySQL)
SHOW PROCEDURE STATUS WHERE Db = 'your_database';

-- Show procedure code
SHOW CREATE PROCEDURE procedure_name;

-- Drop a procedure
DROP PROCEDURE IF EXISTS procedure_name;
```

> **Interview tip:** "When would you use a stored procedure vs writing SQL in the application?" — Use stored procedures when the logic is database-centric (complex joins, calculations on large datasets, security-sensitive operations). Keep business logic in the app when it involves external services, complex workflows, or needs to be testable outside the database.

---
---

# Primary Key vs Unique Key

Both Primary Key and Unique Key enforce **uniqueness**, but they serve different purposes and have different rules. This is one of the most frequently asked interview questions.

---

## Side-by-Side Comparison

| Aspect | Primary Key | Unique Key |
|--------|:---:|:---:|
| **Purpose** | Main identifier for the table | Enforces uniqueness on additional columns |
| **NULL allowed?** | ❌ Never (NOT NULL) | ✅ One NULL allowed (in most RDBMS) |
| **How many per table?** | Only **ONE** | **Multiple** unique keys allowed |
| **Creates index?** | ✅ Clustered index (by default) | ✅ Non-clustered index |
| **Can be Foreign Key reference?** | ✅ Yes (most common) | ✅ Yes (less common) |
| **Auto NOT NULL?** | ✅ Automatically adds NOT NULL | ❌ Must specify NOT NULL explicitly |
| **Duplicate values?** | ❌ Never | ❌ Never (except multiple NULLs in some RDBMS) |

---

## Example

```sql
CREATE TABLE employees (
    emp_id    INT PRIMARY KEY,           -- ← Only ONE primary key
    email     VARCHAR(100) UNIQUE,       -- ← Unique key #1
    phone     VARCHAR(15) UNIQUE,        -- ← Unique key #2
    aadhar_no VARCHAR(12) UNIQUE,        -- ← Unique key #3
    name      VARCHAR(50),
    dept      VARCHAR(50)
);
```

### Sample Data

| emp_id (PK) | email (UQ) | phone (UQ) | aadhar_no (UQ) | name | dept |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | alice@co.com | 9876543210 | 1234-5678-9012 | Alice | CSE |
| 2 | bob@co.com | 9876543211 | 2345-6789-0123 | Bob | ECE |
| 3 | carol@co.com | NULL | NULL | Carol | CSE |

**What's allowed and what's not:**

| Operation | Allowed? | Why |
|-----------|:---:|-----|
| `INSERT (emp_id=NULL, ...)` | ❌ | PK cannot be NULL |
| `INSERT (emp_id=1, ...)` | ❌ | PK must be unique (1 already exists) |
| `INSERT (emp_id=4, email=NULL, ...)` | ✅ | Unique key allows ONE NULL |
| `INSERT (emp_id=5, email='alice@co.com', ...)` | ❌ | Unique key violation (email already exists) |
| `INSERT (emp_id=6, phone=NULL, ...)` | ✅ | Another unique column can also be NULL |

---

## Visual Comparison

```
  PRIMARY KEY                         UNIQUE KEY
  ──────────                          ──────────
  ┌──────────────┐                   ┌──────────────┐
  │ emp_id       │                   │ email        │
  ├──────────────┤                   ├──────────────┤
  │ 1 ✅         │                   │ alice@co ✅  │
  │ 2 ✅         │                   │ bob@co   ✅  │
  │ 3 ✅         │                   │ NULL     ✅  │
  │ NULL ❌      │                   │ NULL     ❌  │ (second NULL)
  │ 1 ❌ (dup)   │                   │ alice@co ❌  │ (duplicate)
  └──────────────┘                   └──────────────┘
        │                                  │
   Clustered Index                  Non-Clustered Index
   (physical order)                 (logical order)
```

---

## Clustered vs Non-Clustered Index

| | Clustered Index (PK) | Non-Clustered Index (UQ) |
|--|---|---|
| **Data order** | Physically sorts the table data | Separate index structure pointing to data |
| **How many?** | Only ONE per table | Multiple allowed |
| **Speed** | Fastest for range queries | Slightly slower (extra lookup) |
| **Analogy** | Phone book sorted by name | Index at the back of a textbook |

```
  Clustered (PK = emp_id):
  ┌───┬───┬───┬───┐
  │ 1 │ 2 │ 3 │ 4 │  ← data physically in this order
  └───┴───┴───┴───┘

  Non-Clustered (UQ = email):
  ┌──────────┬─────┐
  │ alice@co │ → 1 │  ← index points to row location
  │ bob@co   │ → 2 │
  │ carol@co │ → 3 │
  └──────────┴─────┘
```

---

## When to Use Which?

| Scenario | Use |
|----------|-----|
| Main row identifier (emp_id, roll_no) | **Primary Key** |
| Must be unique but not the main ID (email, phone, SSN) | **Unique Key** |
| Column may have NULL values but still needs uniqueness | **Unique Key** |
| Referenced by foreign keys in other tables | **Primary Key** (preferred) or Unique Key |

---

## Quick Summary

```
  Primary Key:
    ✅ Unique
    ✅ NOT NULL (always)
    ✅ Only ONE per table
    ✅ Creates CLUSTERED index
    ✅ Main identifier

  Unique Key:
    ✅ Unique
    ⚠️ Allows ONE NULL
    ✅ MULTIPLE per table
    ✅ Creates NON-CLUSTERED index
    ✅ Secondary identifier
```

> **Interview tip:** If asked "Can a table have multiple primary keys?" — No, only ONE primary key (but it can be a composite PK with multiple columns). A table CAN have multiple UNIQUE keys though.

---
---

# UUID vs Auto-Increment Integer as Primary Key

Choosing between a UUID and an auto-increment integer (`INT`/`BIGINT`) as your primary key is one of the most impactful design decisions you'll make. It affects storage, query performance, insert throughput, index size, and how well your system scales across multiple databases. Let's break it down.

---

## What Each Option Looks Like

```sql
-- Auto-increment integer
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,    -- 1, 2, 3, 4, 5, ...
    customer_id INT,
    total DECIMAL(10,2)
);

-- UUID as CHAR(36)
CREATE TABLE orders (
    id CHAR(36) PRIMARY KEY,                 -- '550e8400-e29b-41d4-a716-446655440000'
    customer_id INT,
    total DECIMAL(10,2)
);

-- UUID as BINARY(16) (recommended if using UUID)
CREATE TABLE orders (
    id BINARY(16) PRIMARY KEY,               -- 16 raw bytes (no dashes, no hex encoding)
    customer_id INT,
    total DECIMAL(10,2)
);
```

---

## Storage Comparison

| Format | Size per Value | Example |
|---|---|---|
| `INT` | **4 bytes** | `2147483647` (max ~2.1 billion) |
| `BIGINT` | **8 bytes** | `9223372036854775807` (max ~9.2 quintillion) |
| `BINARY(16)` (UUID) | **16 bytes** | `0x550e8400e29b41d4a716446655440000` |
| `CHAR(36)` (UUID as string) | **36 bytes** | `'550e8400-e29b-41d4-a716-446655440000'` |
| `VARCHAR(36)` (UUID as string) | **37-38 bytes** | Same as above + 1-2 byte length prefix |

**Why this matters:** The primary key is stored in **every** secondary index (as a pointer back to the clustered index). A larger PK means every secondary index is larger.

| PK Type | PK Size | Table with 5 Secondary Indexes: Extra Storage per Row |
|---|---|---|
| `INT` | 4 bytes | 5 × 4 = **20 bytes** |
| `BIGINT` | 8 bytes | 5 × 8 = **40 bytes** |
| `BINARY(16)` | 16 bytes | 5 × 16 = **80 bytes** |
| `CHAR(36)` | 36 bytes | 5 × 36 = **180 bytes** |

For a table with 100 million rows and 5 secondary indexes:
- `BIGINT` PK → secondary indexes use ~4 GB for PK references
- `CHAR(36)` UUID PK → secondary indexes use ~18 GB — **4.5× more**

> **Rule:** If you use UUIDs, **always** store them as `BINARY(16)`, never as `CHAR(36)`. You save 20 bytes per primary key value and per secondary index entry.

---

## Insert Performance — The B+ Tree Problem

This is the **biggest** performance difference between the two, and it comes down to how InnoDB's clustered index (B+ Tree) handles inserts.

### Auto-Increment: Sequential Inserts (Fast)

Auto-increment IDs are **monotonically increasing**: 1, 2, 3, 4, 5, ... Each new row has a higher key than the last. In the B+ Tree, this means every insert goes to the **rightmost leaf page** — the same page, over and over, until it fills up and splits.

```
Insert id=1001:  goes to the END of the tree → append
Insert id=1002:  goes to the END of the tree → append
Insert id=1003:  goes to the END of the tree → append
...

B+ Tree leaf pages (sequential, orderly):
[1-500] → [501-1000] → [1001-1003, ...] ← always appending here
```

**Why this is fast:**
- **One hot page** — the rightmost leaf stays in the buffer pool (memory). Writes hit RAM, not disk.
- **No page splits in the middle** — splits only happen at the end, which is cheap.
- **Sequential I/O** — if the page does need to be flushed to disk, it's written sequentially (adjacent pages are next to each other on disk).
- **Pages fill up to ~90-95%** — minimal wasted space because data is inserted in order.

### UUID (v4): Random Inserts (Slow)

UUID v4 values are **completely random**: `a3b8d1b6...`, `f81d4fae...`, `0c8cfc82...`. Each new row's key lands at a **random position** in the B+ Tree — NOT at the end.

```
Insert id=a3b8d1b6...:  goes to the MIDDLE of the tree
Insert id=f81d4fae...:  goes to the END of the tree
Insert id=0c8cfc82...:  goes to the BEGINNING of the tree
...

B+ Tree leaf pages (fragmented, random):
[0c8f..., 0e2a...] → [..., a3b8...] → [..., f81d...]
     ↑ insert here        ↑ insert here       ↑ insert here
```

**Why this is slow:**
- **Random I/O** — every insert may touch a different leaf page, scattered across disk. Random reads are ~100× slower than sequential reads on HDDs, and ~10× slower on SSDs.
- **Buffer pool thrashing** — with random inserts, you need the entire B+ Tree in memory (buffer pool) for good performance. If the tree doesn't fit in RAM, almost every insert triggers a disk read to load the target page, modify it, and eventually flush it back.
- **Constant page splits in the middle** — when a random insert fills a page in the middle of the tree, it splits. Middle splits are more expensive than end-of-tree splits because they may cascade upward and cause page reorganization.
- **Pages fill only ~50-70%** — random inserts cause splits at random points, leaving pages half-empty (fragmentation). This wastes disk space and means more pages to scan for range queries.

### Real-World Benchmark Numbers

| Metric | `BIGINT` Auto-Increment | UUID v4 (`BINARY(16)`) | UUID v4 (`CHAR(36)`) |
|---|---|---|---|
| Insert rate (table fits in buffer pool) | ~30,000/sec | ~25,000/sec | ~20,000/sec |
| Insert rate (table exceeds buffer pool) | ~25,000/sec | **~5,000/sec** (5× slower) | **~3,000/sec** (8× slower) |
| B+ Tree page utilization | ~90-95% | ~50-70% | ~50-70% |
| Disk space for 100M rows (data only) | ~6 GB | ~9 GB | ~14 GB |
| Point lookup speed (by PK) | ~0.2 ms | ~0.3 ms | ~0.5 ms |
| Range scan speed (1000 rows) | ~1 ms | ~5-15 ms | ~8-20 ms |

*Numbers are approximate and depend on hardware, row size, and configuration. The key insight is the dramatic degradation when the table exceeds buffer pool size.*

**The critical threshold:** UUID inserts are "fine" when your entire B+ Tree fits in the buffer pool (RAM). The moment the tree exceeds available memory, performance **falls off a cliff** because every random insert now requires a disk read. With auto-increment, even if the tree doesn't fit in RAM, inserts are still fast because they only touch the rightmost page (which is always cached).

---

## UUID v7 / ULID — The Best of Both Worlds?

The performance problems above apply to **UUID v4** (fully random). Newer formats like **UUID v7** (RFC 9562, 2024) and **ULID** solve this by embedding a **timestamp** in the most significant bits:

```
UUID v4:  550e8400-e29b-41d4-a716-446655440000   ← fully random
UUID v7:  018e4f6c-5a00-7000-8000-1234567890ab   ← timestamp-prefixed (sortable!)
ULID:     01ARZ3NDEKTSV4RRFFQ69G5FAV             ← timestamp-prefixed (sortable!)
```

**UUID v7 structure:**
```
 48 bits: Unix timestamp in milliseconds (gives ordering)
  4 bits: Version (always 0111 for v7)
 12 bits: Random
  2 bits: Variant
 62 bits: Random
──────────
128 bits total (same as UUID v4)
```

Because the timestamp occupies the most significant bits, UUID v7 values generated **later** are always **greater** than earlier ones — they're **roughly sequential**, just like auto-increment IDs. This means:

- Inserts go to the **end** of the B+ Tree (no random page splits)
- Page utilization stays high (~85-90%)
- Performance is close to auto-increment

| Format | Sortable? | Insert Pattern | B+ Tree Friendly? |
|---|---|---|---|
| Auto-increment `BIGINT` | ✅ Yes | Sequential (append-only) | ✅ Best |
| UUID v7 / ULID | ✅ Yes (by time) | Roughly sequential | ✅ Very good |
| UUID v4 | ❌ No | Random | ❌ Worst |

```sql
-- Store UUID v7 as BINARY(16) for best performance
CREATE TABLE orders (
    id BINARY(16) PRIMARY KEY,    -- UUID v7 stored as raw bytes
    customer_id INT,
    total DECIMAL(10,2)
);

-- In Java, generate UUID v7 (Java 17+ doesn't have native v7, use a library):
-- UUID uuid = UUIDv7.generate();  // or use com.github.f4b6a3:uuid-creator
-- byte[] bytes = uuidToBytes(uuid);
```

---

## Advantages of Auto-Increment Integer

| Advantage | Explanation |
|---|---|
| **Fastest insert performance** | Sequential inserts always append to the end of the B+ Tree — no random I/O, no mid-tree page splits |
| **Smallest storage** | 4 bytes (`INT`) or 8 bytes (`BIGINT`) vs 16+ bytes for UUID — smaller PK = smaller indexes, more rows per page |
| **Best range scan performance** | Adjacent IDs are physically adjacent on disk — range queries read contiguous pages (sequential I/O) |
| **Human-readable** | `id = 42` is easy to type, remember, and debug. `id = '550e8400-e29b-41d4-a716-446655440000'` is not |
| **Efficient JOINs** | Integer comparisons are single CPU instructions. String/binary comparisons are byte-by-byte |
| **Natural ordering** | Higher ID = created later. You can `ORDER BY id` as a proxy for `ORDER BY created_at` |
| **Easy to communicate** | "Check order #12345" is something support teams, APIs, and users can work with |

## Disadvantages of Auto-Increment Integer

| Disadvantage | Explanation |
|---|---|
| **Predictable / enumerable** | Anyone can guess the next ID (`id + 1`), crawl all records by incrementing, or estimate your total volume. This is a security/privacy concern for public-facing IDs (e.g., `/api/users/42` → try `/api/users/43`) |
| **Single point of generation** | Auto-increment requires a centralized counter — only one database node can generate the next ID. In distributed systems with multiple write nodes, this causes **conflicts** (two nodes both generate `id = 1001`) |
| **Merging data is hard** | If you have two databases and you merge them, both have `id = 1`, `id = 2`, etc. You must remap all IDs and update every foreign key — a painful migration |
| **Sharding complexity** | Each shard needs a non-overlapping ID range (shard 1: 1-1M, shard 2: 1M-2M) or a global ID generator (like Twitter's Snowflake). Auto-increment alone doesn't work across shards |
| **Exposes business metrics** | If your latest order is `#1,000,000`, competitors know your total order count. VCs know your traction. This may be undesirable |
| **Limited range** | `INT` maxes out at ~2.1 billion — high-volume tables can exhaust this. `BIGINT` goes to ~9.2 quintillion, which is effectively unlimited |

---

## Advantages of UUID

| Advantage | Explanation |
|---|---|
| **Globally unique without coordination** | Any server, any shard, any microservice can generate a UUID independently — no central counter needed. Two servers will never generate the same UUID (collision probability is astronomically low: ~1 in 2¹²² for v4) |
| **Perfect for distributed systems** | In multi-master replication, sharded databases, or microservice architectures, every node generates its own IDs without conflict |
| **Merge-friendly** | You can merge data from multiple databases, services, or environments without ID collisions — every record has a universally unique identity |
| **Non-enumerable** | Users can't guess or crawl other records. `/api/users/550e8400-e29b-41d4-a716-446655440000` doesn't reveal how many users you have or let someone try the next ID |
| **Generate IDs before INSERT** | You can generate the UUID in application code, pass it to the frontend, create related records, and then insert — all before the database is touched. With auto-increment, you only know the ID after INSERT |
| **No business metric leakage** | A UUID reveals nothing about volume, growth rate, or ordering |
| **Cross-system identity** | The same UUID can identify an entity across databases, caches, message queues, event logs, and external APIs — a universal identifier |

## Disadvantages of UUID

| Disadvantage | Explanation |
|---|---|
| **Larger storage** | 16 bytes (`BINARY(16)`) or 36 bytes (`CHAR(36)`) vs 4-8 bytes for integers. Every secondary index stores a copy of the PK, so all indexes are larger |
| **Random insert performance (v4)** | UUID v4's randomness causes random B+ Tree insertions, page splits, fragmentation, and buffer pool thrashing. Dramatic performance degradation when data exceeds RAM |
| **Worse range scans** | Physically scattered data means range queries trigger random I/O instead of sequential reads |
| **Not human-friendly** | `550e8400-e29b-41d4-a716-446655440000` is impossible to type, remember, or communicate verbally. Debugging and support become harder |
| **Slower comparisons** | Comparing 16 bytes is slower than comparing 4 or 8 bytes. This impacts JOINs, WHERE clauses, and index traversals |
| **Index bloat** | Every secondary index entry includes the 16-36 byte PK. For tables with many indexes, this significantly increases total index size and reduces cache efficiency |
| **No natural ordering (v4)** | UUID v4 has no inherent order — you can't sort by UUID to get chronological order. You need a separate `created_at` column and index |
| **Formatting inconsistencies** | Different systems may store UUIDs with or without dashes, uppercase or lowercase, binary or string — leading to subtle bugs |

---

## Practical Performance Comparison Summary

| Aspect | `BIGINT` Auto-Increment | UUID v4 `BINARY(16)` | UUID v7 `BINARY(16)` |
|---|---|---|---|
| **Storage per PK** | 8 bytes | 16 bytes | 16 bytes |
| **Insert throughput** | ⚡ Best | 🔴 Worst (random I/O) | ✅ Good (sequential) |
| **Point lookup** | ⚡ Fastest | ✅ Good | ✅ Good |
| **Range scan** | ⚡ Fastest (sequential pages) | 🔴 Slow (scattered pages) | ✅ Good (roughly sequential) |
| **Secondary index size** | Smallest | 2× larger | 2× larger |
| **Distributed ID generation** | ❌ Needs coordination | ✅ No coordination | ✅ No coordination |
| **Merge/shard friendly** | ❌ Conflicts | ✅ No conflicts | ✅ No conflicts |
| **Security (non-enumerable)** | ❌ Predictable | ✅ Unpredictable | ⚠️ Partially (timestamp prefix leaks timing) |
| **Human readable** | ✅ Easy | ❌ Hard | ❌ Hard |
| **Natural sort order** | ✅ By creation time | ❌ Random | ✅ By creation time |

---

## Best Practice: Use Both (Hybrid Approach)

Many production systems use **both** — an internal auto-increment ID for performance and a public UUID for external exposure:

```sql
CREATE TABLE orders (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,     -- Internal: fast, sequential, used in JOINs and FKs
    public_id   BINARY(16) NOT NULL UNIQUE,            -- External: UUID exposed in APIs and URLs
    customer_id BIGINT,
    total       DECIMAL(10,2),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_public_id (public_id)
);
```

```java
@Entity
@Table(name = "orders")
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;                    // Internal — never exposed in APIs

    @Column(name = "public_id", columnDefinition = "BINARY(16)", unique = true)
    private UUID publicId;              // External — used in REST endpoints

    // ...
}
```

```java
// API uses the public UUID
@GetMapping("/orders/{publicId}")
public OrderResponse getOrder(@PathVariable UUID publicId) {
    return orderService.findByPublicId(publicId);
}
// URL: /api/orders/550e8400-e29b-41d4-a716-446655440000
// Internally: SELECT * FROM orders WHERE public_id = 0x550e8400...
```

**Why this works:**
- **JOINs, GROUP BY, and foreign keys** all use the fast `BIGINT` primary key internally
- **APIs, URLs, and external references** use the non-enumerable UUID
- The **clustered index** benefits from sequential auto-increment inserts
- The UUID column has a **secondary `UNIQUE` index** — lookups by UUID do one extra index hop, but this is acceptable since API lookups are typically by single ID

---

## Quick Decision Guide

| Scenario | Recommended Primary Key |
|---|---|
| Single database, internal system | `BIGINT AUTO_INCREMENT` — simplest and fastest |
| Single database, public-facing API | `BIGINT` PK + `UUID` public column (hybrid) |
| Distributed database / multi-master | `UUID v7` as `BINARY(16)` — sequential + no coordination |
| Microservices generating IDs independently | `UUID v7` or `ULID` as `BINARY(16)` |
| Sharded database (Vitess, CockroachDB) | `UUID v7` — avoids hot-spot on a single shard |
| High-volume analytics / time-series | `BIGINT AUTO_INCREMENT` — maximize insert throughput |
| Merging data from multiple sources | `UUID` — guaranteed unique across all sources |
| Legacy system, can't change PK | Keep `BIGINT` PK, add a `UUID` column for new integrations |

> **The golden rule:** Use `BIGINT AUTO_INCREMENT` as your primary key for maximum InnoDB performance. If you need non-enumerable external identifiers, add a separate `UUID` column (preferably v7, stored as `BINARY(16)`). If you're in a distributed system where centralized ID generation is impossible, use `UUID v7` as your primary key — it gives you global uniqueness with near-sequential insert performance.

---
---

# SQL Injection

SQL Injection is a **code injection attack** where a hacker inserts malicious SQL code through user input fields (login forms, search boxes, URLs) to manipulate the database. It's one of the **most common and dangerous** web vulnerabilities.

> **Think of it this way:** Imagine a bank teller who blindly follows any instruction written on a withdrawal slip. A normal customer writes "Withdraw ₹1000 from Account #123." An attacker writes "Withdraw ₹1000 from Account #123; **also transfer all money from every account to mine**." If the teller doesn't verify, the attack succeeds. SQL Injection works the same way.

---

## How It Works

```
  Normal Flow:
  ────────────
  User enters:  105
  SQL becomes:  SELECT * FROM Users WHERE UserId = 105
  Result:       Returns user #105 only ✅

  SQL Injection:
  ──────────────
  User enters:  105 OR 1=1
  SQL becomes:  SELECT * FROM Users WHERE UserId = 105 OR 1=1
  Result:       Returns ALL users ❌ (because 1=1 is always TRUE)
```

### The Vulnerable Code

```
txtUserId = getRequestString("UserId");           // User input
txtSQL = "SELECT * FROM Users WHERE UserId = " + txtUserId;   // String concatenation
```

The problem: **user input is directly concatenated** into the SQL query without any validation.

---

## Types of SQL Injection Attacks

### 1. Tautology Attack (1=1 is Always True)

```
  Input:  105 OR 1=1
  Query:  SELECT * FROM Users WHERE UserId = 105 OR 1=1;
```

Since `1=1` is always TRUE, the `WHERE` clause is effectively removed → **returns ALL rows**.

```
  Users Table
  ┌────────┬──────────┬──────────┐
  │ UserId │ Name     │ Password │
  ├────────┼──────────┼──────────┤
  │ 101    │ Alice    │ pass123  │ ◄── All returned!
  │ 102    │ Bob      │ secret   │ ◄── All returned!
  │ 103    │ Carol    │ qwerty   │ ◄── All returned!
  │ 105    │ Dave     │ mypass   │ ◄── All returned!
  └────────┴──────────┴──────────┘
  Attacker now has ALL usernames and passwords!
```

### 2. Login Bypass (" OR ""=")

Normal login:
```sql
SELECT * FROM Users WHERE Name = "John" AND Pass = "myPass"
-- Returns John's record if password matches
```

Injected login — user types `" OR ""="` in both fields:
```sql
SELECT * FROM Users WHERE Name = "" OR ""="" AND Pass = "" OR ""=""
```

Since `""=""` is always TRUE → **bypasses authentication entirely**.

```
  Login Form                    What the Server Sees
  ──────────                    ────────────────────
  Username: " OR ""="    →     Name = "" OR ""=""    (always TRUE)
  Password: " OR ""="   →     Pass = "" OR ""=""    (always TRUE)

  Result: Attacker is logged in as the FIRST user in the table!
```

### 3. Batched Statements (Destructive)

User input: `105; DROP TABLE Suppliers`

```sql
SELECT * FROM Users WHERE UserId = 105; DROP TABLE Suppliers;
```

This executes TWO statements:
1. Returns user 105 (harmless)
2. **Deletes the entire Suppliers table** (catastrophic!)

```
  Step 1: SELECT * FROM Users WHERE UserId = 105  ✅ Normal query
  Step 2: DROP TABLE Suppliers                     💀 TABLE DESTROYED!
```

### 4. UNION-Based Injection

```sql
-- Normal query
SELECT name, email FROM Users WHERE id = 1

-- Injected: 1 UNION SELECT username, password FROM admin_users
SELECT name, email FROM Users WHERE id = 1
UNION SELECT username, password FROM admin_users
```

The attacker **piggybacks a second query** to extract data from a completely different table.

---

## Prevention — Parameterized Queries

The **#1 defense** against SQL Injection is **parameterized queries** (prepared statements). Instead of concatenating user input into the SQL string, you use **placeholders** that the database engine treats as data, never as SQL code.

### How It Works

```
  Vulnerable (String Concatenation):
  ──────────────────────────────────
  sql = "SELECT * FROM Users WHERE UserId = " + userInput
  → Attacker input becomes part of the SQL structure ❌

  Safe (Parameterized Query):
  ───────────────────────────
  sql = "SELECT * FROM Users WHERE UserId = @id"
  → Attacker input is treated as a literal value ✅
  → Even "105 OR 1=1" is treated as the string "105 OR 1=1"
```

### Examples in Different Languages

**Java (PreparedStatement):**
```java
String sql = "SELECT * FROM Users WHERE UserId = ?";
PreparedStatement stmt = conn.prepareStatement(sql);
stmt.setInt(1, userId);     // Parameter is bound safely
ResultSet rs = stmt.executeQuery();
```

**Python (DB-API):**
```python
cursor.execute("SELECT * FROM Users WHERE UserId = %s", (user_id,))
```

**C# / ASP.NET:**
```csharp
string sql = "SELECT * FROM Users WHERE UserId = @0";
SqlCommand cmd = new SqlCommand(sql);
cmd.Parameters.AddWithValue("@0", userId);
cmd.ExecuteReader();
```

**PHP (PDO):**
```php
$stmt = $pdo->prepare("SELECT * FROM Users WHERE UserId = :id");
$stmt->bindParam(':id', $userId);
$stmt->execute();
```

**Node.js (MySQL2):**
```javascript
const [rows] = await connection.execute(
    'SELECT * FROM Users WHERE UserId = ?', [userId]
);
```

---

## Other Prevention Techniques

| Technique | How It Helps |
|-----------|-------------|
| **Parameterized queries** | Treats input as data, not SQL code (best defense) |
| **Input validation** | Reject special characters (`'`, `"`, `;`, `--`) |
| **Stored procedures** | Precompiled SQL — harder to inject |
| **Least privilege** | DB user should only have needed permissions (no DROP!) |
| **ORMs** | Frameworks like Hibernate, SQLAlchemy auto-parameterize |
| **WAF (Web Application Firewall)** | Blocks common injection patterns |
| **Escape special characters** | Last resort — less reliable than parameterization |

---

## Quick Summary

```
  SQL Injection Attack Types:
  ───────────────────────────
  1. Tautology (OR 1=1)        → Returns all rows
  2. Login Bypass (" OR ""=")  → Bypasses authentication
  3. Batched Statements (;DROP)→ Destroys tables
  4. UNION-Based               → Extracts data from other tables

  Prevention:
  ───────────
  ✅ Parameterized queries (BEST)
  ✅ Input validation
  ✅ Stored procedures
  ✅ Least privilege
  ❌ String concatenation (NEVER)
```

> **Interview tip:** If asked "How do you prevent SQL Injection?" — the answer is always **parameterized queries / prepared statements**. Input validation is a secondary defense, not a replacement.

---
---

# MySQL GRANT / REVOKE Privileges (Detailed)

The DCL section earlier covered the basics. Here we go deeper into the **MySQL-specific syntax**, privilege types, granting on functions/procedures, and checking grants.

---

## GRANT — Assigning Privileges

### Syntax

```sql
GRANT privilege_type ON object TO 'user'@'host';
```

> **User format:** Always specify as `'username'@'host'` — e.g., `'Amit'@'localhost'` or `'Amit'@'192.168.1.100'`.

### Common Privilege Types

| Privilege | What It Allows |
|-----------|---------------|
| `SELECT` | Read data from tables |
| `INSERT` | Add new rows |
| `UPDATE` | Modify existing rows |
| `DELETE` | Remove rows |
| `CREATE` | Create new tables/databases |
| `DROP` | Delete tables/databases |
| `ALTER` | Modify table structure |
| `INDEX` | Create/drop indexes |
| `EXECUTE` | Run stored procedures/functions |
| `GRANT OPTION` | Pass privileges to other users |
| `ALL PRIVILEGES` | Everything above |

### Examples

```sql
-- 1. Grant SELECT only
GRANT SELECT ON Users TO 'Amit'@'localhost';

-- 2. Grant multiple privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON Users TO 'Amit'@'localhost';

-- 3. Grant ALL privileges on a table
GRANT ALL ON Users TO 'Amit'@'localhost';

-- 4. Grant to ALL users (wildcard)
GRANT SELECT ON Users TO '*'@'localhost';

-- 5. Grant on entire database
GRANT ALL ON my_database.* TO 'Amit'@'localhost';

-- 6. Grant on all databases
GRANT ALL ON *.* TO 'Amit'@'localhost';
```

### Granting EXECUTE on Functions / Procedures

```sql
-- Grant EXECUTE on a function
GRANT EXECUTE ON FUNCTION CalculateSalary TO 'Amit'@'localhost';

-- Grant EXECUTE on a procedure
GRANT EXECUTE ON PROCEDURE DBMSProcedure TO 'Amit'@'localhost';

-- Grant EXECUTE to ALL users
GRANT EXECUTE ON FUNCTION CalculateSalary TO '*'@'localhost';
```

### Checking Granted Privileges

```sql
SHOW GRANTS FOR 'Amit'@'localhost';
```

**Output:**
```
+------------------------------------------------------+
| Grants for Amit@localhost                            |
+------------------------------------------------------+
| GRANT SELECT, INSERT ON Users TO 'Amit'@'localhost'  |
+------------------------------------------------------+
```

---

## REVOKE — Removing Privileges

### Syntax

```sql
REVOKE privilege_type ON object FROM 'user'@'host';
```

### Examples

```sql
-- 1. Revoke SELECT
REVOKE SELECT ON Users FROM 'Amit'@'localhost';

-- 2. Revoke multiple privileges
REVOKE SELECT, INSERT, UPDATE, DELETE ON Users FROM 'Amit'@'localhost';

-- 3. Revoke ALL privileges
REVOKE ALL ON Users FROM 'Amit'@'localhost';

-- 4. Revoke EXECUTE on a function
REVOKE EXECUTE ON FUNCTION CalculateSalary FROM 'Amit'@'localhost';

-- 5. Revoke EXECUTE on a procedure
REVOKE EXECUTE ON PROCEDURE DBMSProcedure FROM 'Amit'@'localhost';
```

---

## Privilege Scope Hierarchy

```
  *.* (Global)         →  All databases, all tables
    │
  database.*           →  All tables in one database
    │
  database.table       →  One specific table
    │
  database.table(col)  →  Specific column(s) in a table
```

```sql
-- Global: user can do everything everywhere
GRANT ALL ON *.* TO 'admin'@'localhost';

-- Database: user can read all tables in `shop` database
GRANT SELECT ON shop.* TO 'reader'@'localhost';

-- Table: user can only insert into `orders` table
GRANT INSERT ON shop.orders TO 'app_user'@'localhost';

-- Column: user can only update the `status` column
GRANT UPDATE (status) ON shop.orders TO 'support'@'localhost';
```

> **Best practice:** Follow the **principle of least privilege** — give users only the minimum permissions they need. Don't use `GRANT ALL ON *.*` unless absolutely necessary.

---
---

# Clustered vs Non-Clustered Index

Indexes are data structures that **speed up data retrieval**. Without indexes, the database must scan every row (full table scan). With indexes, it can jump directly to the relevant rows.

🔗 [PlanetScale — How Do Database Indexes Work](https://planetscale.com/blog/how-do-database-indexes-work)

---

## What Is an Index?

> **Think of it this way:** A database without an index is like a book without a table of contents — you'd have to read every page to find what you're looking for. An index is the table of contents that tells you exactly which page to go to.

```
  Without Index (Full Table Scan):
  ─────────────────────────────────
  "Find employee #500"
  → Scan row 1, row 2, row 3, ... row 500
  → O(n) — slow for large tables

  With Index:
  ───────────
  "Find employee #500"
  → Index lookup → directly go to row 500
  → O(log n) — fast even for millions of rows
```

---

## Clustered Index

A **clustered index** physically sorts and stores the **actual data rows** in the order of the index key. The table data IS the index.

```
  Clustered Index on emp_id:
  ┌─────────────────────────────────────────┐
  │ Data pages are physically sorted by PK  │
  ├─────┬─────┬─────┬─────┬─────┬─────────┤
  │  1  │  2  │  3  │  4  │  5  │  ...    │
  └─────┴─────┴─────┴─────┴─────┴─────────┘
    ▲
    The data IS the index (leaf nodes = data pages)
```

**Key characteristics:**
- **Only ONE** per table (data can only be physically sorted one way)
- By default, the **Primary Key** creates a clustered index
- Leaf nodes contain the **actual data rows**
- Best for **range queries** (e.g., `WHERE id BETWEEN 100 AND 200`)

> **Analogy:** A **phone book** sorted alphabetically by last name. The data itself is in order — you don't need a separate lookup.

---

## Non-Clustered Index

A **non-clustered index** is a **separate structure** that stores the index key + a pointer back to the actual data row. The table data stays in its original order.

```
  Non-Clustered Index on email:
  ┌──────────────────────┐         ┌──────────────────────┐
  │ Index (sorted)       │         │ Data (original order) │
  ├──────────────┬───────┤         ├─────┬────────────────┤
  │ alice@co     │ → Row 3│        │  1  │ Dave, dave@co  │
  │ bob@co       │ → Row 1│        │  2  │ Carol, carol@co│
  │ carol@co     │ → Row 2│        │  3  │ Alice, alice@co│
  │ dave@co      │ → Row 4│ ──────►│  4  │ Bob, bob@co    │
  └──────────────┴───────┘         └─────┴────────────────┘
    Index is sorted                  Data is NOT sorted
    by email                         by email
```

**Key characteristics:**
- **Multiple** non-clustered indexes allowed per table
- Leaf nodes contain **index keys + row pointers** (not actual data)
- Requires **additional disk space** for the index structure
- Requires an **extra lookup** (pointer → data row) called "bookmark lookup"

> **Analogy:** The **index at the back of a textbook**. It's sorted alphabetically by topic, and points you to the page number. The book's content is NOT in alphabetical order.

---

## Side-by-Side Comparison

| Parameter | Clustered Index | Non-Clustered Index |
|-----------|:---:|:---:|
| **How many per table?** | Only **ONE** | **Multiple** (up to 999 in SQL Server) |
| **Data order** | Physically sorts data rows | Separate structure, data stays unsorted |
| **Leaf nodes contain** | Actual data pages | Key + pointer to data row |
| **Additional disk space?** | ❌ No (data IS the index) | ✅ Yes (separate index structure) |
| **Speed** | ✅ Faster (direct data access) | ⚠️ Slower (extra pointer lookup) |
| **Default for** | Primary Key | UNIQUE constraints |
| **Best for** | Range queries, ORDER BY | Exact lookups, frequently searched columns |
| **Insert/Update overhead** | ⚠️ Higher (must maintain physical order) | ⚠️ Moderate (update index pointers) |

---

## How They Work Internally (B-Tree)

Both clustered and non-clustered indexes typically use a **B-Tree** (Balanced Tree) structure:


▶️ [B-Tree (Abdul Bari)](https://www.youtube.com/watch?v=aZjYr87r1b8&t=1657s)<br>
▶️ [B Tree Insert and Delete](https://www.youtube.com/watch?v=ownO77M4SWI)<br>
📚 [B-Trees & B+ Tree & DB Indexes (PlanetScale)](https://planetscale.com/blog/btrees-and-database-indexes)<br>
🕹️ [Interactive B+ Tree Visualizer](https://bplustree.app/)<br>
🕹️ [Interactive B Tree Visualizer](https://btree.app/)

🔗 [B-Trees and B+ Trees — Explained](https://medium.com/@akashsdas_dev/b-trees-and-b-trees-682d363df1f7)

```
  B-Tree Structure (Clustered Index on emp_id):
  ═══════════════════════════════════════════════

              ┌───────────┐
              │  Root     │
              │  [50]     │
              └─────┬─────┘
            ┌───────┴───────┐
            ▼               ▼
      ┌───────────┐   ┌───────────┐
      │ [10, 30]  │   │ [70, 90]  │
      └──┬──┬──┬──┘   └──┬──┬──┬──┘
         │  │  │         │  │  │
    ┌────┘  │  └────┐    │  │  └────┐
    ▼       ▼       ▼    ▼  ▼       ▼
  ┌─────┐┌─────┐┌─────┐   (leaf nodes)
  │1-9  ││10-29││30-49│   ← Clustered: actual data rows
  │DATA ││DATA ││DATA │   ← Non-clustered: key + pointer
  └─────┘└─────┘└─────┘

  Lookup for emp_id = 25:
  Root(50) → go left → Node(10,30) → middle → Leaf(10-29) → found!
  Only 3 steps instead of scanning all rows!
```

---

## When to Use Which?

| Scenario | Index Type | Why |
|----------|:---:|-----|
| Primary Key | Clustered | Default; best for range queries |
| Columns used in `WHERE` frequently | Non-Clustered | Speed up lookups |
| Columns used in `JOIN` conditions | Non-Clustered | Faster join performance |
| Foreign Key columns | Non-Clustered | Faster FK lookups |
| Columns rarely queried | ❌ No index | Index overhead not worth it |
| Tables with heavy inserts | Minimize indexes | Each index slows down writes |
| Columns used in `ORDER BY` / `GROUP BY` | Non-Clustered | Avoid sort operations |

---

## Advantages & Disadvantages

### Clustered Index

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Fast range queries (`BETWEEN`, `>`, `<`) | Only one per table |
| No extra disk space | Slow inserts in non-sequential order (page splits) |
| Data is always sorted | Updates to indexed columns are expensive |
| Cache-friendly (sequential reads) | Fragmentation over time |

### Non-Clustered Index

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Multiple per table | Extra disk space needed |
| Speeds up frequent lookups | Bookmark lookup overhead |
| Doesn't affect physical data order | Must update when clustering key changes |
| Can cover queries (covering index) | Maintenance cost on heavy write tables |

---

## Creating Indexes

```sql
-- Clustered index (usually auto-created with PRIMARY KEY)
CREATE CLUSTERED INDEX idx_emp_id ON employees(emp_id);

-- Non-clustered index
CREATE INDEX idx_emp_name ON employees(name);

-- Non-clustered index on multiple columns (composite)
CREATE INDEX idx_dept_salary ON employees(department, salary);

-- Unique non-clustered index
CREATE UNIQUE INDEX idx_email ON employees(email);

-- Drop an index
DROP INDEX idx_emp_name ON employees;
```

---

## Covering Index (Bonus)

A **covering index** includes all columns needed by a query, so the database doesn't need to look up the actual data row at all:

```sql
-- Query
SELECT name, salary FROM employees WHERE department = 'CSE';

-- Covering index (includes all columns in the query)
CREATE INDEX idx_covering ON employees(department, name, salary);
```

```
  Without Covering Index:
  Index lookup → find pointer → go to data row → read name, salary
  (two steps)

  With Covering Index:
  Index lookup → name and salary are IN the index → done!
  (one step — faster)
```

---

## Cardinality & Selectivity — How Duplicate Values Affect an Index

**Question:** Many people share the same `name`. If I create `INDEX(name)`, do the duplicates break it?

**Short answer:** No. Duplicates don't break an index — they make it **less useful**, and past a threshold the optimizer stops using it entirely.

### Structurally, Duplicates Are a Non-Issue

A non-unique secondary index in InnoDB stores `[indexed column | primary key]`. So `INDEX(name)` is physically sorted by `(name, id)` — every entry is still unique at the storage level. 500 people named "John Smith" = 500 index entries sitting contiguously, sorted by `id`. Nothing collides, nothing overflows.

```
  INDEX(name) leaf pages:
  ┌──────────────────────────────────────┐
  │ ("John Smith", 41)                   │
  │ ("John Smith", 892)   ← duplicates   │
  │ ("John Smith", 1503)     stored fine │
  │ ("Priya Nair", 77)                   │
  │ ("Priya Nair", 2201)                 │
  └──────────────────────────────────────┘
```

### The Real Issue Is Selectivity

Two terms that get confused:

| Term | Meaning | Formula |
|---|---|---|
| **Cardinality** | How many **distinct** values the column has | `COUNT(DISTINCT col)` |
| **Selectivity** | What fraction of the table one value narrows you down to | `COUNT(DISTINCT col) / COUNT(*)` |

Closer to **1.0** is better. On a 1M-row table:

| Column | Distinct values | Rows per value | Selectivity | Index worth it? |
|---|---:|---:|---:|:---:|
| `email` | 1,000,000 | 1 | 1.0 | ✅ Perfect |
| `name` | ~200,000 | ~5 | 0.2 | ✅ Great |
| `city` | ~500 | ~2,000 (0.2%) | 0.0005 | ✅ Still fine |
| `dept_id` | 10 | 100,000 (10%) | 0.00001 | ⚠️ Borderline |
| `gender` | 2 | 500,000 (50%) | 0.000002 | ❌ Never used |
| `is_active` | 2 | ~950,000 (95%) | 0.000002 | ❌ Never used |

> Note the table proves selectivity is only a **rough guide** — `city` has terrible raw selectivity but works great, because what actually matters is **rows matched per value**, not the ratio.

### Why the Optimizer Abandons a Low-Selectivity Index

```
WHERE gender = 'M'
        │
        ▼
  500,000 matching index entries (cheap — sequential in the index)
        │
        ▼
  500,000 RANDOM lookups into the clustered index
  (to fetch the columns not in the index)
        │
        ▼
  More expensive than just reading the whole table
  sequentially from start to finish
        │
        ▼
  ❌ Optimizer IGNORES the index → full table scan
```

The rough tipping point is **~20–30% of the table**. Past that, a sequential scan wins. `EXPLAIN` gives it away:

```sql
EXPLAIN SELECT * FROM students WHERE gender = 'M';
--   type: ALL   key: NULL     ← index exists but was NOT used
```

And you still pay for that index on **every** `INSERT`, `UPDATE`, and `DELETE`. Worst of both worlds — write cost with no read benefit.

**So for `name`: totally fine.** Even a very common name is a tiny fraction of the table. Duplicates only hurt when a **single value** covers a large share of rows.

### ⚠️ The Nuance That Bites — Data Skew

The decision is made **per value**, not per column. If `status` is 95% `'active'`:

```sql
WHERE status = 'active'     -- 950,000 rows → full table scan, index ignored
WHERE status = 'cancelled'  --     800 rows → index used
```

Same index, opposite decisions. By default MySQL assumes values are **uniformly distributed**, so it guesses wrong on skewed columns. Fix it by giving the optimizer real distribution data:

```sql
ANALYZE TABLE orders UPDATE HISTOGRAM ON status;   -- MySQL 8.0+
```

### How to Check Your Own Columns

```sql
-- Exact selectivity
SELECT COUNT(DISTINCT name) / COUNT(*) AS selectivity FROM students;

-- Rows per value — the number that actually matters
SELECT name, COUNT(*) AS cnt
FROM students GROUP BY name ORDER BY cnt DESC LIMIT 10;

-- What the optimizer currently believes (an estimate from sampled dives)
SHOW INDEX FROM students;   -- read the Cardinality column
ANALYZE TABLE students;     -- refresh those estimates
```

### The Fix for a Low-Selectivity Column

Don't index it alone — make it part of a **composite index**, with a selective column leading:

```sql
-- ❌ Useless on its own
CREATE INDEX idx_gender ON students(gender);

-- ✅ Selective column first, then the low-cardinality one
CREATE INDEX idx_dept_gender ON students(dept_id, gender);

-- ✅ Or pair it with something that makes the result set small
CREATE INDEX idx_status_created ON orders(status, created_at);
```

The **leading column** decides whether the index is seekable at all — see [Compound (Composite) Index](#compound-composite-index).

> **Interview tip:** "Should I index a boolean / status / gender column?" — Normally **no**, because one value matches most of the table and the optimizer will skip it. The **exception** is a heavily skewed column where you only ever query the *rare* value — e.g. `WHERE status = 'failed'` on a table that's 99.9% `'success'`. There the index is excellent, and a **partial/filtered index** would be ideal (though MySQL doesn't support those — PostgreSQL does).

---

## Quick Summary

```
  Clustered Index:
    📦 Data IS the index (physically sorted)
    1️⃣  Only ONE per table
    🚀 Fast range queries
    📖 Analogy: Phone book sorted by name

  Non-Clustered Index:
    📑 Separate structure (key + pointer)
    🔢 MULTIPLE per table
    🔍 Fast exact lookups
    📖 Analogy: Index at back of textbook
```

> **Interview tip:** "What happens if you create a table without a primary key?" — The table has no clustered index (called a **heap**). All queries require full table scans. Always define a primary key to get a clustered index.

---
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

### ⭐ The Core Rule

**Every index is a separate B+ Tree that must be maintained on every write.**

One `INSERT` into a table with 4 secondary indexes is really **5 B+ Tree insertions** — one clustered, four secondary. Each lands in a *different* tree, at a *different* place on disk.

```
INSERT INTO orders (id, user_id, status, created_at, total) VALUES (...);

        ┌──────────────────────────────────────────────┐
        │              ONE SQL statement                │
        └───────────────────────┬──────────────────────┘
                                ▼
   ┌───────────┬───────────┬───────────┬───────────┬───────────┐
   ▼           ▼           ▼           ▼           ▼
 PRIMARY   idx_user    idx_status  idx_created  idx_total
 (row data) (user_id,   (status,    (created_at, (total,
            id)          id)         id)          id)
   │           │           │           │           │
   └───────────┴───────────┴───────────┴───────────┴──────▶ 5 B+ Tree inserts
```

That is **write amplification**, and it is the real cost of "just add an index." Indexes are not free storage — they are a tax on every `INSERT`, `UPDATE` and `DELETE` forever.

### What Happens on Each Operation

| Operation | Impact on Indexes |
|---|---|
| **INSERT** | A new entry must be added to **every** index's B+ Tree. For each index: find the correct leaf page, insert the key, **split the leaf if it's full**. |
| **UPDATE** (non-indexed column) | **No secondary index impact** — only the clustered index (the row itself) is updated, usually in place. Cheapest case. |
| **UPDATE** (indexed column) | The old key is **delete-marked** in that index and a new key is inserted — effectively a **delete + insert** per affected index. |
| **UPDATE** (primary key) | ☠️ **Worst case.** A full delete + re-insert in the clustered index **and in every secondary index**, because every secondary entry stores the PK as its row pointer. |
| **DELETE** | The entry is **delete-marked** (flagged, *not* physically removed) in the clustered index and in **every** secondary index. A background **purge** thread removes it later. Leaf pages may then merge if they fall below `MERGE_THRESHOLD`. |

> ⚠️ **The most common misconception:** a `DELETE` does *not* remove index entries. It only flags them. See [DELETE — Nothing Is Removed Immediately](#delete--nothing-is-removed-immediately) below.

### INSERT — Where the Row Actually Lands

In InnoDB the **clustered index *is* the table** — the full row lives in the PK B+ Tree's leaf page. So the insert position is decided entirely by your primary key value:

```
Sequential PK (AUTO_INCREMENT / UUIDv7)      Random PK (UUID v4)
──────────────────────────────────────       ────────────────────────────
  ...│ 97 │ 98 │ 99 │  ◀── append              │ 12 │ 44 │ 91 │  ◀── lands mid-tree
         rightmost leaf                                ↓
                                               page is full → SPLIT
  ✅ pages fill to ~100%                       ❌ pages settle at ~50% fill
  ✅ one hot page stays in the buffer pool     ❌ random pages pulled from disk
  ✅ no mid-tree splits                        ❌ constant splits + fragmentation
```

🔗 This is the single biggest argument in [UUID vs Auto-Increment Integer as Primary Key](#uuid-vs-auto-increment-integer-as-primary-key).

### Page Splits — The Hidden Cost of a Random Primary Key

When the target 16 KB leaf page has no room left:

```
1. Allocate a new page
2. Move roughly half the records into it
3. Update the parent node's pointers
4. If the parent is now full too → split the parent as well (can cascade upward)
5. In the worst case the tree grows one level taller
```

Two consequences people miss:

- Both pages are now ~50% full, so the **table occupies roughly twice the disk** for the same rows.
- The split writes **three** dirty pages (old, new, parent) instead of one.

> **Optimization:** for strictly ascending inserts InnoDB detects the pattern and does a **right-hand split** — it leaves the old page full and starts a fresh page — instead of splitting 50/50. This is exactly why sequential keys pack so much better.

### The Change Buffer — and When It Can't Save You

To avoid a random disk read on every secondary index insert, InnoDB records the change in the **change buffer** and merges it into the real page later, when that page is read for some other reason (or by a background merge). But it is **not** always available:

| Index being modified | Change buffer usable? | Why |
|---|:---:|---|
| **Clustered index (PK)** | ❌ No | The page is needed *right now* — it's where the row is physically stored |
| **Secondary, non-unique** | ✅ Yes | Nothing needs checking, so the write can safely be deferred |
| **Secondary, UNIQUE** | ❌ No | Uniqueness must be verified *immediately*, which forces the page to be read from disk |

> **Practical consequence:** a `UNIQUE` secondary index is meaningfully more expensive on writes than an ordinary one — it forces a random read that a non-unique index defers. Don't add `UNIQUE` unless you actually need the constraint.

### ❓ If a Random UUID Hurts, Doesn't an Index on `email` Hurt Too?

A very fair question — and the **mechanism is identical**. Emails arrive in no order at all (`zoe@…`, then `adam@…`, then `mike@…`), so every insert lands at a random leaf of the email B+ Tree, causing the same page splits and the same ~50% page fill.

So why does nobody worry about it? Because the **blast radius** is completely different.

#### What Actually Moves During a Split

```
Clustered index (PK) leaf              Secondary index (email) leaf
─────────────────────────              ────────────────────────────
 THE WHOLE ROW                          just (email, PK)
 id, name, email, address,              "adam@x.com" → 4471
 bio, created_at, ... ~800 B            ~40 bytes
 ≈ 20 rows per 16 KB page               ≈ 400 entries per 16 KB page
```

A split in the clustered index relocates half a page of **full rows**. A split in a secondary index relocates half a page of **tiny pointers**.

#### Blast Radius — The Real Reason

| | Random **PK** (UUIDv4) | Random **secondary index** (email) |
|---|---|---|
| **What gets fragmented** | ☠️ **The entire table** | Only that one index |
| **Effect on other indexes** | ☠️ **Every** secondary index gets fatter — they all store the PK as their row pointer, so a 16-byte UUID bloats all of them | ✅ None |
| **Effect on range scans over the table** | ☠️ Destroyed — the table's physical order *is* the PK order | ✅ None — the table stays perfectly packed |
| **Can you undo it later?** | ❌ Only by rebuilding the whole table | ✅ `ALTER TABLE t DROP INDEX idx_email` — instant |

**The root cause of the asymmetry:** InnoDB's clustered index *forces the physical order of your rows* to follow the primary key. A secondary index has no such power — it's just a side tree. So a bad PK poisons **everything**; a bad secondary index poisons **only itself**.

#### The Same Percentage, a Wildly Different Bill

If your table is 100 GB and the email index is 3 GB, 50% fragmentation means:

| | Before | After |
|---|---|---|
| Random PK | 100 GB | **~200 GB** |
| Random email index | 3 GB | ~6 GB |

#### Where the Worry *Does* Have Teeth

`email` is almost always `UNIQUE` — and unique secondary indexes **cannot use the change buffer** (see the table above). Every insert must read the target page from disk *right now* to check for duplicates.

```sql
UNIQUE KEY uk_email (email)   -- ❌ no change buffer, forced random read per insert
KEY idx_email (email)         -- ✅ change buffer defers the write
```

So `UNIQUE(email)` genuinely is one of the more expensive secondary indexes you can have. It's still worth it — you want the database enforcing that constraint, not application code — but that's the honest cost.

#### The Contrast That Makes It Click

```
idx_created_at    →  values always increase  →  appends to the rightmost leaf
                     ✅ cheapest possible secondary index — no splits at all

idx_email         →  values are random       →  random leaf, splits
                     ⚠️ normal cost, entirely acceptable

PRIMARY KEY uuid  →  values are random       →  random leaf, splits,
                     ☠️ AND drags the entire row with it,
                        AND bloats every other index
```

#### ⭐ The Rule — Only the Primary Key Has to Be Sequential

> **Never let a random value be your clustered index. Anywhere else, randomness is a bounded, local cost you pay in exchange for a lookup you actually need.**
>
> | | Random value OK? | Why |
> |---|:---:|---|
> | **PRIMARY KEY** (clustered) | ❌ **No** | It dictates the physical order of your rows, and its size is copied into every secondary index |
> | **Secondary index / `UNIQUE` key** | ✅ **Yes** | It's just a side tree — the cost is local, bounded, and undoable with one `DROP INDEX` |

Every real schema has random-valued secondary indexes — email, username, phone, external references, API keys. That is **normal and correct**. The problem was never "random values in indexes"; it was only ever "random values in the *clustered* index."

#### It's "Random Bad", Not "UUID Bad"

Not every UUID is random. The time-ordered ones sort like an `AUTO_INCREMENT` and are perfectly fine as a primary key:

| ID type | Ordering | OK as PK? |
|---|---|:---:|
| **UUIDv4** | Fully random | ❌ No |
| **UUIDv7** | Timestamp-prefixed | ✅ Yes |
| **ULID** | Timestamp-prefixed | ✅ Yes |
| **Snowflake** | Timestamp-prefixed | ✅ Yes |

And if you're stuck with v4, you don't have to choose — keep a sequential PK for storage and expose the UUID through a secondary index, where randomness is affordable:

```sql
CREATE TABLE users (
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,   -- internal: sequential, clustered
    public_id  BINARY(16) NOT NULL,                 -- external: random UUID
    email      VARCHAR(255) NOT NULL,
    UNIQUE KEY uk_public_id (public_id),            -- random → but only a secondary index
    UNIQUE KEY uk_email (email)
);
```

🔗 Full treatment in [UUID v7 / ULID — The Best of Both Worlds?](#uuid-v7--ulid--the-best-of-both-worlds) and [Best Practice: Use Both (Hybrid Approach)](#best-practice-use-both-hybrid-approach).

### DELETE — Nothing Is Removed Immediately

```
Step 1  DELETE runs        → record is DELETE-MARKED in the clustered index
                             and in every secondary index. Bytes untouched.
Step 2  Transaction commits
Step 3  PURGE thread       → physically removes the marked records once no
                             active read view can still see them, and frees
                             the undo log pages
Step 4  Page merge         → if a page drops below MERGE_THRESHOLD (default
                             50%), it is merged with a sibling and freed
```

**Why delete-mark instead of deleting?** Two reasons:

- **MVCC** — an older transaction's read view may still legitimately need to see that row
- **Rollback** — the transaction isn't committed yet and may be undone

**And the space still doesn't return to the OS.** Freed pages go onto the tablespace's free list for reuse by that table; the `.ibd` file does not shrink. Only a full table rebuild reclaims it:

```sql
OPTIMIZE TABLE orders;        -- InnoDB maps this to a rebuild + ANALYZE
ALTER TABLE orders FORCE;     -- identical operation
```

🔗 See [TRUNCATE vs DROP vs DELETE](#truncate-vs-drop-vs-delete--a-common-confusion) — `TRUNCATE` drops and recreates the tablespace, returning all space instantly.

### ⚠️ Purge Lag — When DELETE Backfires

If a **long-running transaction** (even an idle-in-transaction `SELECT`) holds an old read view, the purge thread cannot advance. Delete-marked rows pile up, undo history grows, and the undo tablespace can bloat to hundreds of GB.

```sql
SHOW ENGINE INNODB STATUS\G     -- look for: History list length
```

A history list length in the millions means purge is starving — find and kill the long transaction:

```sql
SELECT * FROM information_schema.INNODB_TRX ORDER BY trx_started LIMIT 5;
```

### Real-World Write Overhead

| Indexes on Table | INSERT Relative Speed | Notes |
|---|---|---|
| 0 indexes (heap) | 1× (baseline) | Not possible in InnoDB (always has PK) |
| 1 (primary key only) | ~1× | Just the clustered index |
| 3 indexes | ~1.5-2× slower | Each index adds ~15-30% overhead |
| 5 indexes | ~2-3× slower | Noticeable on high-throughput writes |
| 10+ indexes | ~3-5× slower | Seriously impacts write performance |

### Best Practices for Write-Heavy Tables

1. **Use a sequential primary key** (`AUTO_INCREMENT`, UUIDv7/ULID) — this single choice eliminates most page splits and fragmentation
2. **Only create indexes you actually use** — run `SHOW INDEX FROM table` and check if any index is never hit
3. **Monitor unused indexes:**
   ```sql
   -- MySQL 8.0+ performance_schema
   SELECT OBJECT_SCHEMA, OBJECT_NAME, INDEX_NAME
   FROM performance_schema.table_io_waits_summary_by_index_usage
   WHERE INDEX_NAME IS NOT NULL
     AND COUNT_STAR = 0
     AND OBJECT_SCHEMA = 'your_database';
   ```
4. **Bulk insert tip:** insert in **primary key order**, and drop non-unique secondary indexes before bulk loading, then recreate them — building an index once from sorted data is much faster than inserting into an existing index row by row
5. **Prefer composite indexes over multiple single-column indexes** — one composite index replaces two or three single-column indexes, reducing write overhead
6. **Avoid `UNIQUE` on secondary indexes unless required** — it disables the change buffer for that index
7. **Never update the primary key** — treat it as immutable; it's the most expensive write in InnoDB
8. **Run `ANALYZE TABLE` after bulk inserts or deletes** — statistics go stale and the optimizer starts choosing bad plans
9. **Clearing a whole table?** Use `TRUNCATE`, not `DELETE` — no per-row undo, no purge backlog, space returned immediately

### Quick-Fire Q&A

| Question | Answer |
|---|---|
| How many B+ Trees does one INSERT touch? | 1 clustered + 1 per secondary index |
| Does DELETE remove the index entry? | **No** — it delete-marks it; the purge thread removes it later |
| Why doesn't the `.ibd` file shrink after a big DELETE? | Freed pages return to the table's free list, not to the OS. A file can only be truncated from the *end*, and free pages are scattered throughout. Only a rebuild reclaims it. |
| Which is cheapest: updating an indexed column, a non-indexed column, or the PK? | Non-indexed column (in place) < indexed column (delete+insert on that index) < PK (delete+insert on **every** index) |
| Why is a UNIQUE secondary index slower to write than a normal one? | It can't use the change buffer — uniqueness must be checked immediately, forcing a disk read |
| What causes a page split? | Inserting into a leaf page that is already full — typical with a random PK |
| If a random UUID is bad as a PK, is a random `email` index bad too? | Same mechanism, far smaller blast radius. Only the **clustered index** must be sequential; random secondary indexes are normal and correct |
| What is "History list length" telling you? | How far behind the purge thread is; a large value means a long transaction is blocking purge |

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
---

# Dense Index vs Sparse Index

Indexes can be classified by how many entries they maintain relative to the rows in the data file. A **dense index** has an entry for every row, while a **sparse index** has entries for only some rows (typically one per disk block/page). This distinction is fundamental to database internals and affects storage, lookup speed, and write overhead.

---

## What Is a Dense Index?

A dense index has an entry for **every single row** (every search key value) in the data file. Think of it as a complete phone book where every person has a listing.

```
Index                          Data File (sorted by ID)
┌────────┬─────────┐          ┌────────────────────────────┐
│ ID=1   │ → ptr   │────────→ │ ID=1, Alice, Engineering   │
│ ID=2   │ → ptr   │────────→ │ ID=2, Bob, Sales           │
│ ID=3   │ → ptr   │────────→ │ ID=3, Carol, Marketing     │
│ ID=4   │ → ptr   │────────→ │ ID=4, Dave, Engineering    │
│ ID=5   │ → ptr   │────────→ │ ID=5, Eve, Sales           │
│ ID=6   │ → ptr   │────────→ │ ID=6, Frank, Marketing     │
└────────┴─────────┘          └────────────────────────────┘
  6 index entries               6 data rows
```

---

## What Is a Sparse Index?

A sparse index has entries for only **some** rows — typically one entry per **disk block/page**. It points to the **first record in each block**. The data **must be sorted** on the search key for this to work.

```
Index                          Data File (sorted by ID, 3 rows per block)
┌────────┬─────────┐          ┌────────────────────────────┐
│ ID=1   │ → ptr   │────────→ │ Block 1:                   │
│        │         │          │   ID=1, Alice, Engineering  │
│        │         │          │   ID=2, Bob, Sales          │
│        │         │          │   ID=3, Carol, Marketing    │
├────────┼─────────┤          ├────────────────────────────┤
│ ID=4   │ → ptr   │────────→ │ Block 2:                   │
│        │         │          │   ID=4, Dave, Engineering   │
│        │         │          │   ID=5, Eve, Sales          │
│        │         │          │   ID=6, Frank, Marketing    │
└────────┴─────────┘          └────────────────────────────┘
  2 index entries               6 data rows (2 blocks)
```

To find **ID=5**: the index sees `ID=4 ≤ 5 < next entry`, so it jumps to Block 2 and does a **short linear scan** within that block.

---

## Advantages of Sparse Index Over Dense Index

| Advantage | Explanation |
|---|---|
| **Much smaller index size** | Only one entry per block instead of one per row. If a block holds 500 rows, the sparse index is **~500× smaller** |
| **Fits in memory** | Smaller index = more likely to fit entirely in RAM (buffer pool). A dense index on a billion-row table might be 20 GB; a sparse index might be 40 MB |
| **Faster index maintenance on writes** | Inserting/deleting a row usually doesn't change the sparse index at all — only if the **first record of a block** changes. A dense index must be updated on every single insert/delete |
| **Less disk I/O for the index itself** | Fewer index pages to read from disk during lookups. The index traversal is shorter |
| **Lower storage cost** | Takes up less disk space overall, which matters at massive scale |

---

## Disadvantages of Sparse Index vs Dense Index

| Disadvantage | Explanation |
|---|---|
| **Slower point lookups** | A dense index jumps **directly** to the exact row. A sparse index jumps to the block and then does a **linear scan** within it. For a single-row lookup, dense is faster (one pointer dereference vs. scan of up to N rows in a block) |
| **Data MUST be sorted** | Sparse index only works if the data file is physically sorted on the indexed column. If the data isn't sorted, a sparse index is **impossible**. Dense indexes work on any column regardless of sort order |
| **Only one per table** | Since a table can only be physically sorted one way, you can have **at most one** sparse index. Need to search by `email`, `phone`, AND `created_at`? Only one of those can have a sparse index — the rest need dense indexes |
| **Worse for non-contiguous matches** | If matching rows are scattered across many blocks (e.g., a range query that hits every other block), a sparse index still has to load each of those blocks and scan them. A dense index would point directly to each matching row |
| **Cannot cover queries** | A dense index can be a **covering index** (stores all needed columns, answering the query without touching the table). A sparse index only stores one key per block — you always have to read the actual data block |
| **Less precise statistics** | The optimizer has less granular information about data distribution. A dense index tells MySQL exactly how many rows match a value; a sparse index can only estimate at the block level |

---

## Why Would Anyone Use a Sparse Index?

The core reason: **the trade-off is worth it when data is sorted.**

1. **The scan within a block is nearly free** — a disk block is typically 4-16 KB. Once you load it into memory (one I/O), scanning 50–500 rows inside it is microseconds. The bottleneck is always the disk I/O, not the in-memory scan.

2. **Index fits in memory** — a dense index on a 1-billion-row table might not fit in RAM. A sparse index almost certainly does. An in-memory index lookup + one disk read for the block **beats** multiple disk reads to traverse a large dense index that spills to disk.

3. **Write-heavy workloads** — if your table gets millions of inserts per second (logs, events, time-series), updating a dense index on every insert is expensive. A sparse index only updates when block boundaries change — much cheaper.

4. **It's the natural design for clustered/sorted data** — if data is already physically sorted (like InnoDB's clustered index, or a log table sorted by timestamp), a sparse index is the obvious choice. You're just bookmarking the start of each page.

> **Real-world analogy:** A book's index is sparse — it tells you "Chapter 5 starts on page 87." It doesn't say "sentence 1 is on page 87, sentence 2 is on page 87, sentence 3 is on page 87..." You jump to page 87 and scan from there. That's fast enough.

---

## How Is a Sparse Index Created?

A sparse index **requires the data file to be sorted** on the indexed column. Here's the process:

### Step 1: Data Must Be Sorted on the Search Key

```
Data file sorted by employee_id:
Block 0: [1, 2, 3, ..., 500]
Block 1: [501, 502, ..., 1000]
Block 2: [1001, 1002, ..., 1500]
```

### Step 2: Pick the First Key from Each Block

```
Sparse index entries:
  (1,    → pointer to Block 0)
  (501,  → pointer to Block 1)
  (1001, → pointer to Block 2)
```

### Step 3: Store the Index as a Sorted Structure

The index itself is stored as a small sorted file (or B+ Tree). Since it's tiny, it usually fits in one or two disk pages.

### In Practice (InnoDB)

You don't explicitly say `CREATE SPARSE INDEX`. The database engine decides internally:

- **InnoDB's clustered index (B+ Tree)** is conceptually similar to a sparse index at the internal node level — internal nodes point to **pages** (blocks), not individual rows. Only the leaf level has per-row entries.
- **InnoDB's secondary indexes** are dense — they have one entry per row.

The sparse index concept is most visible in:
- **Database internals** (how B+ Tree internal nodes work)
- **SSTable files** in LSM-Tree databases (Cassandra, RocksDB, LevelDB) — they use sparse indexes on sorted data blocks
- **Academic/exam contexts** — the concept is taught as a fundamental indexing strategy

### Critical Constraint

> **A sparse index can ONLY be built on the column the data is physically sorted by.** You can have at most **one** sparse index per table (because a table can only be physically sorted one way). Any other column needs a dense index. This is exactly why InnoDB has one clustered index (sparse-like) and all secondary indexes are dense.

---

## Dense vs Sparse Index — Quick Comparison

| Aspect | Dense Index | Sparse Index |
|---|---|---|
| **Entries** | One per row | One per block/page |
| **Size** | Large (proportional to row count) | Small (proportional to block count) |
| **Lookup speed** | Direct — find exact row | Jump to block + short scan |
| **Insert/delete cost** | Must update index every time | Update only when block boundaries change |
| **Requires sorted data?** | No | **Yes** — mandatory |
| **Max per table** | Many | **One** (only on the sort column) |
| **Can cover queries?** | ✅ Yes (covering index) | ❌ No — must read data block |
| **Best for** | Any column, random access, covering queries | Sorted/clustered data, range scans, write-heavy workloads |

> **The key trade-off in one line:** Sparse index trades **lookup precision** (must scan within a block) for **smaller size** (fits in memory, cheaper writes). Dense index trades **size and write cost** for **exact, direct access** to every row.

---
---

# Compound (Composite) Index

A **compound index** (also called a **composite** or **multi-column** index) is one B-tree index built from two or more columns.

```sql
CREATE INDEX idx_orders_customer_status_created
    ON orders (customer_id, status, created_at);
```

The index is ordered lexicographically, like a phone book sorted by `(customer_id, status, created_at)`: first by `customer_id`; within the same customer by `status`; and within the same customer and status by `created_at`.

```
(customer_id, status, created_at)
(10, 'PAID',    2026-08-01)
(10, 'PAID',    2026-08-05)
(10, 'PENDING', 2026-08-02)
(11, 'PAID',    2026-08-03)
```

## Leftmost-Prefix Rule

For an index on `(customer_id, status, created_at)`, the database can efficiently use the leading, contiguous columns. This is called the **leftmost-prefix rule**.

| Query predicate / ordering | Uses this index efficiently? | Why |
|---|:---:|---|
| `WHERE customer_id = 10` | Yes | Uses the first column |
| `WHERE customer_id = 10 AND status = 'PAID'` | Yes | Uses the first two columns |
| `WHERE customer_id = 10 AND status = 'PAID' AND created_at >= '2026-08-01'` | Yes | Equality on leading columns, then a range on the next column |
| `WHERE status = 'PAID'` | Usually no | The leading `customer_id` is missing |
| `WHERE customer_id = 10 ORDER BY status, created_at` | Yes | The requested order matches the remaining index order |
| `WHERE customer_id = 10 AND status > 'PAID' AND created_at >= '2026-08-01'` | Partly | The range on `status` limits how usefully later columns can narrow/search or satisfy ordering |

> **Key idea:** An index on `(A, B, C)` is generally useful for `(A)`, `(A, B)`, and `(A, B, C)`, but not usually for `(B)` or `(C)` alone. It is not the same as three independent single-column indexes.

## Choosing Column Order

Design the index for the actual query pattern:

1. Put columns tested with equality (`=` or `IN`) first.
2. Put the range column (`>`, `<`, `BETWEEN`, prefix `LIKE`) after those equality columns.
3. Put columns used to satisfy `ORDER BY` next, when their direction/order can match the query.
4. Consider adding selected output columns last only when the database supports a covering index and the extra index size is justified.

For the earlier query, `(customer_id, status, created_at)` is better than `(created_at, customer_id, status)` because the query first fixes `customer_id` and `status`, then needs the matching rows ordered by `created_at`.

## Composite Index vs Separate Indexes

If a common query filters on both columns, a composite index is often better:

```sql
-- Common query
SELECT * FROM orders
WHERE customer_id = 42 AND status = 'PAID';

-- Usually preferable for this query pattern
CREATE INDEX idx_orders_customer_status ON orders (customer_id, status);
```

Separate indexes on `customer_id` and `status` may require the optimizer to use only one index or merge two index result sets. A composite index already stores the exact pair in useful order, so it usually reads fewer entries.

> **Trade-off:** Do not create every possible column combination. Composite indexes consume space and increase write overhead. Keep only indexes that support real, measured query patterns, and verify them with `EXPLAIN`.

---
---

# Types of Index — Quick Reference

🔗 **Reference:** [freeCodeCamp — Database Indexing at a Glance](https://www.freecodecamp.org/news/database-indexing-at-a-glance-bb50809d48bd/)

Almost all disk-based indexes are stored as a **B+ tree**: internal nodes hold only keys for navigation, and all keys live in sorted order in the leaf level, which is a linked list (so range scans are cheap).

| Type | What it is | Note |
|---|---|---|
| **Primary / Clustered** | The index **is** the table — leaf nodes hold the actual rows, physically ordered by the key | Only **one** per table. See [Clustered vs Non-Clustered](#clustered-vs-non-clustered-index-1) |
| **Secondary / Non-Clustered** | A separate structure whose leaves hold the key + a pointer to the row | Many per table. A lookup traverses **two** B+ trees (index, then clustered) |
| **Unique** | Like a primary key but **allows NULLs** — and multiple NULLs, since NULL ≠ NULL | See [Primary Key vs Unique Key](#primary-key-vs-unique-key) |
| **Composite** | One index over multiple columns (MySQL: up to 16) | Usable only by a **leftmost prefix**: `(a)`, `(a,b)`, `(a,b,c)` — see [Compound Index](#compound-composite-index) |
| **Covering** | A composite index that contains **every column the query needs** | The query is answered from the index alone — no table access ("index-only scan") |
| **Partial (prefix)** | Indexes only the **first N bytes** of a column | Much smaller; used for long `VARCHAR`/`BLOB` columns |

```sql
CREATE UNIQUE INDEX idx_email     ON users (email);            -- unique
CREATE INDEX        idx_cust_stat ON orders (customer_id, status);  -- composite
CREATE INDEX        idx_name_pfx  ON users (name(10));         -- partial: first 10 bytes
```

**Covering index in one example** — this index answers the query entirely on its own:

```sql
CREATE INDEX idx_cover ON orders (customer_id, status, total_amount);

SELECT status, total_amount FROM orders WHERE customer_id = 42;
--  ↑ every column here lives in the index → no table lookup needed
```

> **Cost reminder:** each index speeds up reads but slows every `INSERT`/`UPDATE`/`DELETE` and consumes storage. Verify with `EXPLAIN` before adding one — see [How to Optimize a SQL Query](#how-to-optimize-a-sql-query).

---
---

# Cursor in SQL

A **cursor** is a database object that allows you to process query results **one row at a time**, instead of all at once. Think of it as a pointer that moves through the result set row by row.

> **Think of it this way:** A normal `SELECT` gives you the entire result at once (like getting a full report). A cursor is like reading that report **line by line** — processing each row individually before moving to the next.

```
  Normal SELECT:                     Using a Cursor:
  ──────────────                     ───────────────
  SELECT * FROM employees            DECLARE cursor
  → Returns ALL rows at once         OPEN cursor
  → Can't process row-by-row         FETCH row 1 → process
                                     FETCH row 2 → process
                                     FETCH row 3 → process
                                     CLOSE cursor
```

---

## When Do You Need Cursors?

| Use Case | Why a Cursor Helps |
|----------|-------------------|
| Row-by-row processing | Need to apply different logic per row |
| Complex calculations | Result of one row depends on previous rows |
| Calling procedures per row | Need to call a stored procedure for each record |
| Generating sequential reports | Row-by-row output with running totals |

> ⚠️ **Important:** Cursors are **slower** than set-based operations. SQL is designed to work on sets of rows, not one at a time. **Always prefer set-based queries** (`UPDATE ... WHERE`, `INSERT ... SELECT`) when possible. Use cursors only as a last resort.

---

## Cursor Lifecycle — 5 Steps

```
  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────────┐
  │ DECLARE  │────▶│  OPEN    │────▶│  FETCH   │────▶│  CLOSE   │────▶│ DEALLOCATE │
  │          │     │          │     │  (loop)  │     │          │     │            │
  │ Define   │     │ Execute  │     │ Get one  │     │ Release  │     │ Free       │
  │ the      │     │ the      │     │ row at   │     │ the      │     │ memory     │
  │ cursor   │     │ query    │     │ a time   │     │ cursor   │     │            │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘     └────────────┘
```

| Step | What It Does | Syntax |
|------|-------------|--------|
| **DECLARE** | Define the cursor and its SELECT query | `DECLARE cursor_name CURSOR FOR SELECT ...` |
| **OPEN** | Execute the query and populate the result set | `OPEN cursor_name` |
| **FETCH** | Retrieve the next row from the result set | `FETCH NEXT FROM cursor_name INTO @variables` |
| **CLOSE** | Release the current result set (cursor can be reopened) | `CLOSE cursor_name` |
| **DEALLOCATE** | Free the cursor's memory completely | `DEALLOCATE cursor_name` |

---

## Basic Syntax

### MySQL Syntax

```sql
DECLARE cursor_name CURSOR FOR
    SELECT column1, column2 FROM table_name WHERE condition;

DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

OPEN cursor_name;

read_loop: LOOP
    FETCH cursor_name INTO @var1, @var2;
    IF done THEN
        LEAVE read_loop;
    END IF;
    -- Process each row here
END LOOP;

CLOSE cursor_name;
```

### SQL Server Syntax

```sql
DECLARE cursor_name CURSOR FOR
    SELECT column1, column2 FROM table_name WHERE condition;

OPEN cursor_name;

FETCH NEXT FROM cursor_name INTO @var1, @var2;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Process each row here
    FETCH NEXT FROM cursor_name INTO @var1, @var2;
END;

CLOSE cursor_name;
DEALLOCATE cursor_name;
```

---

## Complete Example — Process Employee Bonuses

### Scenario

Give a 10% bonus to employees earning < 50000 and a 5% bonus to everyone else, logging each action:

```sql
-- SQL Server Example
DECLARE @emp_id INT, @name VARCHAR(50), @salary DECIMAL(10,2), @bonus DECIMAL(10,2);

-- Step 1: DECLARE the cursor
DECLARE emp_cursor CURSOR FOR
    SELECT emp_id, name, salary FROM employees;

-- Step 2: OPEN the cursor
OPEN emp_cursor;

-- Step 3: FETCH first row
FETCH NEXT FROM emp_cursor INTO @emp_id, @name, @salary;

-- Step 4: LOOP through each row
WHILE @@FETCH_STATUS = 0
BEGIN
    -- Custom logic per row
    IF @salary < 50000
        SET @bonus = @salary * 0.10;    -- 10% bonus
    ELSE
        SET @bonus = @salary * 0.05;    -- 5% bonus

    -- Update the employee's record
    UPDATE employees SET bonus = @bonus WHERE emp_id = @emp_id;

    -- Log the action
    INSERT INTO bonus_log (emp_id, name, bonus_amount, processed_at)
    VALUES (@emp_id, @name, @bonus, GETDATE());

    -- Fetch next row
    FETCH NEXT FROM emp_cursor INTO @emp_id, @name, @salary;
END;

-- Step 5: CLOSE and DEALLOCATE
CLOSE emp_cursor;
DEALLOCATE emp_cursor;
```

### How It Processes

```
  employees table:
  ┌────────┬───────┬────────┐
  │ emp_id │ name  │ salary │
  ├────────┼───────┼────────┤
  │ 1      │ Alice │ 45000  │ ── FETCH → bonus = 4500 (10%)  → UPDATE
  │ 2      │ Bob   │ 60000  │ ── FETCH → bonus = 3000 (5%)   → UPDATE
  │ 3      │ Carol │ 38000  │ ── FETCH → bonus = 3800 (10%)  → UPDATE
  │ 4      │ Dave  │ 75000  │ ── FETCH → bonus = 3750 (5%)   → UPDATE
  └────────┴───────┴────────┘        ▲
                                     │
                              @@FETCH_STATUS = -1
                              (no more rows → exit loop)
```

---

## MySQL Cursor Example (Inside a Stored Procedure)

In MySQL, cursors can only be used inside **stored procedures or functions**:

```sql
DELIMITER //

CREATE PROCEDURE ProcessBonuses()
BEGIN
    DECLARE v_emp_id INT;
    DECLARE v_salary DECIMAL(10,2);
    DECLARE v_bonus DECIMAL(10,2);
    DECLARE done INT DEFAULT 0;

    -- Declare cursor
    DECLARE emp_cursor CURSOR FOR
        SELECT emp_id, salary FROM employees;

    -- Handler for end of result set
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN emp_cursor;

    read_loop: LOOP
        FETCH emp_cursor INTO v_emp_id, v_salary;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Custom logic
        IF v_salary < 50000 THEN
            SET v_bonus = v_salary * 0.10;
        ELSE
            SET v_bonus = v_salary * 0.05;
        END IF;

        UPDATE employees SET bonus = v_bonus WHERE emp_id = v_emp_id;
    END LOOP;

    CLOSE emp_cursor;
END //

DELIMITER ;

-- Call it
CALL ProcessBonuses();
```

---

## Types of Cursors

| Type | Description | Use Case |
|:---:|-------------|----------|
| **Forward-only** | Can only move forward (FETCH NEXT) | Most common, fastest |
| **Scrollable** | Can move forward, backward, or to any position | When you need random access |
| **Static** | Works on a snapshot — changes to base data aren't reflected | When you need a frozen copy |
| **Dynamic** | Reflects real-time changes to the base data | When you need live data |
| **Keyset** | Middle ground — structure is fixed, values can change | Moderate performance |

### Declaring Scrollable Cursor (SQL Server)

```sql
DECLARE scroll_cursor SCROLL CURSOR FOR
    SELECT emp_id, name FROM employees;

OPEN scroll_cursor;

FETCH FIRST   FROM scroll_cursor INTO @id, @name;  -- First row
FETCH LAST    FROM scroll_cursor INTO @id, @name;  -- Last row
FETCH NEXT    FROM scroll_cursor INTO @id, @name;  -- Next row
FETCH PRIOR   FROM scroll_cursor INTO @id, @name;  -- Previous row
FETCH ABSOLUTE 5 FROM scroll_cursor INTO @id, @name; -- 5th row

CLOSE scroll_cursor;
DEALLOCATE scroll_cursor;
```

---

## Implicit vs Explicit Cursors

| | Implicit Cursor | Explicit Cursor |
|--|---|---|
| **Created by** | Database engine automatically | Developer manually |
| **For** | Single-row queries (`SELECT INTO`) | Multi-row result processing |
| **Lifecycle** | Auto managed (open/close/deallocate) | You must manage manually |
| **Example** | `SELECT name INTO @v FROM emp WHERE id=1` | `DECLARE ... CURSOR FOR SELECT ...` |

> Most of what we discussed above are **explicit cursors**. Implicit cursors are created behind the scenes for single-row operations.

---

## Cursor vs Set-Based Operations

```
  ❌ Cursor Approach (slow):                    ✅ Set-Based Approach (fast):
  ──────────────────────────                    ────────────────────────────
  DECLARE cursor ...                            UPDATE employees
  OPEN cursor                                   SET bonus = CASE
  LOOP                                              WHEN salary < 50000
      FETCH row                                     THEN salary * 0.10
      UPDATE one row                                ELSE salary * 0.05
  END LOOP                                      END;
  CLOSE cursor
                                                (One statement, all rows at once!)
```

| | Cursor | Set-Based |
|--|:---:|:---:|
| **Speed** | ❌ Slow (row by row) | ✅ Fast (all at once) |
| **Code** | ❌ Verbose (10+ lines) | ✅ Concise (1-3 lines) |
| **Locking** | ❌ Holds locks longer | ✅ Minimal locking |
| **Memory** | ❌ Higher overhead | ✅ Optimized by engine |
| **When to use** | Complex row-by-row logic | Simple transformations |

---

## Quick Summary

```
  Cursor Lifecycle:  DECLARE → OPEN → FETCH (loop) → CLOSE → DEALLOCATE

  When to USE:
    ✅ Complex per-row logic that can't be expressed in SQL
    ✅ Calling stored procedures for each row
    ✅ Row-dependent calculations (running totals)

  When to AVOID:
    ❌ Simple updates/deletes (use WHERE clause)
    ❌ Bulk inserts (use INSERT ... SELECT)
    ❌ Anything that can be done with JOINs or CASE
```

> **Interview tip:** If asked "What is a cursor and when would you use one?" — A cursor processes query results row-by-row. Use it ONLY when set-based SQL can't handle the logic. Always mention that cursors are **slower than set-based operations** and should be a last resort.

---

## MySQL Cursors — Specifics & Limitations

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

## SQL Cursor vs Cursor-Based Pagination — Quick Comparison

| | SQL Cursor (`DECLARE CURSOR`) | Cursor-Based Pagination (`WHERE id < ?`) |
|---|---|---|
| **What it is** | Database feature for row-by-row iteration | API design pattern for efficient paging |
| **Where it runs** | Inside stored procedures on the DB server | Application code / API layer |
| **Scope** | Server-side only — never exposed to clients | Client-facing — cursor token travels in API responses |
| **Performance** | Fine for batch jobs; not for real-time APIs | Designed for low-latency, high-scale APIs |
| **Use case** | Data migration, batch processing | Chat history, feeds, search results, logs |

> 🔗 For the API-side pattern in full — deferred joins, keyset pagination and the
> cursor-token contract — see [❓ MySQL Pagination — OFFSET/LIMIT vs Cursor-Based (Keyset) Pagination](#-mysql-pagination--offsetlimit-vs-cursor-based-keyset-pagination).

---
---

# Functional Dependencies in DBMS

A **functional dependency (FD)** describes a relationship between attributes in a table where one attribute (or set of attributes) **uniquely determines** another attribute.

**Notation:** `X → Y` means "X functionally determines Y" — if you know X, you can determine exactly one value of Y.

> **Think of it this way:** If you know a student's `roll_no`, you can determine their `name`. So `roll_no → name`. But knowing the `name` doesn't tell you the `roll_no` (names can repeat). So `name → roll_no` is NOT a valid FD.

---

## Sample Table (Used Throughout)

### `student_course` Table

| roll_no | name | dept | course_id | course_name | instructor |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Alice | CSE | C101 | DBMS | Dr. Smith |
| 1 | Alice | CSE | C102 | OS | Dr. Jones |
| 2 | Bob | ECE | C101 | DBMS | Dr. Smith |
| 3 | Carol | CSE | C103 | Networks | Dr. Brown |

**Key:** `{roll_no, course_id}` is the composite primary key (a student can enroll in multiple courses).

### Functional Dependencies in This Table

```
  roll_no → name, dept              (knowing roll_no gives you name and dept)
  course_id → course_name, instructor   (knowing course_id gives course info)
  {roll_no, course_id} → ALL columns   (full PK determines everything)
```

---

## Types of Functional Dependencies

```
                ┌──────────────────────────┐
                │  Functional Dependencies │
                └────────────┬─────────────┘
        ┌────────────┬───────┼───────┬────────────┐
        ▼            ▼       ▼       ▼            ▼
   ┌─────────┐ ┌──────────┐ ┌───┐ ┌─────────┐ ┌──────────┐
   │ Trivial │ │Non-Trivial│ │Full│ │ Partial │ │Transitive│
   └─────────┘ └──────────┘ └───┘ └─────────┘ └──────────┘
```

---

## 1. Trivial Functional Dependency

A dependency `X → Y` is **trivial** if Y is a **subset of X** (i.e., Y is already part of X). It's always true — you're not learning anything new.

> **Think of it as:** "If you know someone's full name, you obviously know their first name." That's trivially true.

### Rule: `X → Y` is trivial if `Y ⊆ X`

### Examples

| Dependency | Trivial? | Why |
|-----------|:---:|-----|
| `{roll_no, name} → name` | ✅ Trivial | `name` is already in `{roll_no, name}` |
| `{roll_no, name} → roll_no` | ✅ Trivial | `roll_no` is already in `{roll_no, name}` |
| `{roll_no} → roll_no` | ✅ Trivial | Same attribute on both sides |
| `{roll_no, course_id} → roll_no` | ✅ Trivial | `roll_no` is a subset of the left side |

```
  Trivial FD:
  ┌─────────────────┐        ┌──────┐
  │ roll_no, name   │───────▶│ name │    Y ⊆ X → Trivial!
  └─────────────────┘        └──────┘
       X contains Y
```

> **Key point:** Trivial FDs are useless for normalization — they tell you nothing new about the data relationships.

---

## 2. Non-Trivial Functional Dependency

A dependency `X → Y` is **non-trivial** if Y is **NOT a subset of X** — i.e., Y contains at least one attribute that is NOT in X. These are the useful, meaningful dependencies.

### Rule: `X → Y` is non-trivial if `Y ⊄ X`

### Examples

| Dependency | Non-Trivial? | Why |
|-----------|:---:|-----|
| `roll_no → name` | ✅ Non-Trivial | `name` is NOT part of `roll_no` |
| `roll_no → name, dept` | ✅ Non-Trivial | `name, dept` are NOT part of `roll_no` |
| `course_id → course_name` | ✅ Non-Trivial | `course_name` is NOT part of `course_id` |
| `{roll_no, name} → name` | ❌ Trivial | `name` IS part of `{roll_no, name}` |

### Completely Non-Trivial

A special case — when there is **zero overlap** between X and Y:

| Dependency | Completely Non-Trivial? |
|-----------|:---:|
| `roll_no → name` | ✅ No overlap at all |
| `{roll_no, name} → dept` | ✅ `dept` has no overlap with `{roll_no, name}` |
| `{roll_no, name} → name, dept` | ❌ `name` overlaps (partially non-trivial) |

```
  Non-Trivial FD:
  ┌──────────┐        ┌──────────────┐
  │ roll_no  │───────▶│ name, dept   │    Y ⊄ X → Non-Trivial!
  └──────────┘        └──────────────┘
       X                  Y (new info)
```

---

## 3. Full Functional Dependency (Fully Functional)

A dependency `X → Y` is **full** if Y depends on the **entire** X, and removing any attribute from X breaks the dependency.

> **Think of it as:** "You need ALL the keys in the combination lock — removing any one key won't open it."

### Rule: `X → Y` is full if no proper subset of X can determine Y

### Example Using `student_course`

| Dependency | Full? | Why |
|-----------|:---:|-----|
| `{roll_no, course_id} → grade` | ✅ **Full** | Need BOTH roll_no AND course_id to determine grade. Neither alone works. |
| `{roll_no, course_id} → name` | ❌ **Not Full** (Partial) | `roll_no` alone determines `name`. Don't need `course_id`. |

```
  Full Dependency:
  ┌──────────────────────────┐           ┌───────┐
  │ {roll_no, course_id}     │──────────▶│ grade │
  └──────────────────────────┘           └───────┘
     Remove roll_no?  → Can't determine grade ❌
     Remove course_id? → Can't determine grade ❌
     Need BOTH → Full FD ✅
```

```
  Partial (NOT Full):
  ┌──────────────────────────┐           ┌──────┐
  │ {roll_no, course_id}     │──────────▶│ name │
  └──────────────────────────┘           └──────┘
     Remove course_id? → roll_no → name still works ✅
     Don't need full PK → Partial FD ❌ (not full)
```

> **Why it matters:** Full FDs are required for **2NF**. If a non-key attribute depends on only PART of the key, the table violates 2NF.

---

## 4. Partial Functional Dependency

A dependency `X → Y` is **partial** if Y depends on only a **proper subset** of X — i.e., you can remove some attribute(s) from X and the dependency still holds.

> **Think of it as:** The opposite of Full FD. "You don't need all the keys — a subset is enough."

### Rule: `X → Y` is partial if some proper subset of X can determine Y

### Examples from `student_course`

The PK is `{roll_no, course_id}`.

| Dependency | Partial? | Why |
|-----------|:---:|-----|
| `{roll_no, course_id} → name` | ✅ **Partial** | `roll_no → name` (don't need `course_id`) |
| `{roll_no, course_id} → dept` | ✅ **Partial** | `roll_no → dept` (don't need `course_id`) |
| `{roll_no, course_id} → course_name` | ✅ **Partial** | `course_id → course_name` (don't need `roll_no`) |
| `{roll_no, course_id} → grade` | ❌ **Full** | Need both — neither alone determines grade |

```
  Partial Dependency:
  ┌──────────────────────────┐           ┌──────┐
  │ {roll_no, course_id}     │──────────▶│ name │
  └──────────────────────────┘           └──────┘
                   ▲
                   │
      ┌────────────┘
      │ roll_no alone → name  ✅
      │ course_id is EXTRA, not needed
      └──▶ This is a PARTIAL dependency
```

> **Why it matters:** Partial FDs cause **redundancy**. Alice's name is repeated for every course she takes. Removing partial FDs is the goal of **2NF (Second Normal Form)**.

### Showing the Redundancy

| roll_no | name | course_id | course_name |
|:---:|:---:|:---:|:---:|
| 1 | **Alice** | C101 | DBMS |
| 1 | **Alice** | C102 | OS |
| 1 | **Alice** | C103 | Networks |

`name = "Alice"` is stored **3 times** because of the partial FD `roll_no → name`. Splitting into separate tables (Student + Enrollment) fixes this.

---

## 5. Transitive Functional Dependency

A dependency `X → Z` is **transitive** if there exists an intermediate attribute Y such that `X → Y` and `Y → Z`, but Y does NOT determine X.

> **Think of it as:** A chain — X determines Y, and Y determines Z. So X indirectly determines Z through Y.

### Rule: `X → Y → Z` where `Y ↛ X` → transitive

### Example from `student_course`

```
  roll_no → dept → dept_head

  Step 1: roll_no → dept       (knowing roll_no gives you dept)
  Step 2: dept → dept_head     (knowing dept gives you dept head)
  BUT:    dept ↛ roll_no       (dept doesn't determine roll_no — many students per dept)

  Therefore: roll_no → dept_head is a TRANSITIVE dependency
```

| roll_no | name | dept | dept_head |
|:---:|:---:|:---:|:---:|
| 1 | Alice | CSE | Dr. Smith |
| 2 | Bob | ECE | Dr. Jones |
| 3 | Carol | CSE | Dr. Smith |

The chain:
```
  roll_no ──→ dept ──→ dept_head
     │           │          │
     1     →    CSE   →   Dr. Smith
     2     →    ECE   →   Dr. Jones
     3     →    CSE   →   Dr. Smith   (Dr. Smith repeated!)
```

> **Why it matters:** Transitive FDs cause **redundancy** — `Dr. Smith` is stored for every CSE student. Removing transitive FDs is the goal of **3NF (Third Normal Form)**.

### How to Fix — Decompose

Split into two tables to remove the transitive dependency:

**`students` table:**

| roll_no | name | dept |
|:---:|:---:|:---:|
| 1 | Alice | CSE |
| 2 | Bob | ECE |
| 3 | Carol | CSE |

**`departments` table:**

| dept | dept_head |
|:---:|:---:|
| CSE | Dr. Smith |
| ECE | Dr. Jones |

Now `dept_head` is stored only ONCE per department — no redundancy!

---

## All 5 Types at a Glance

| Type | Rule | Example | Useful? |
|------|------|---------|:---:|
| **Trivial** | `Y ⊆ X` | `{roll_no, name} → name` | ❌ Obvious, useless |
| **Non-Trivial** | `Y ⊄ X` | `roll_no → name` | ✅ Meaningful |
| **Full** | No subset of X can determine Y | `{roll_no, course_id} → grade` | ✅ Required for 2NF |
| **Partial** | A subset of X can determine Y | `{roll_no, course_id} → name` | ❌ Causes redundancy |
| **Transitive** | `X → Y → Z` (Y ↛ X) | `roll_no → dept → dept_head` | ❌ Causes redundancy |

---

## Connection to Normalization

```
  1NF → Remove repeating groups (atomic values)
            │
            ▼
  2NF → Remove PARTIAL dependencies
        (every non-key attr must depend on the FULL primary key)
            │
            ▼
  3NF → Remove TRANSITIVE dependencies
        (non-key attr must depend ONLY on the key, not through another non-key attr)
            │
            ▼
  BCNF → Every determinant must be a candidate key
```

| Normal Form | Which FDs are Allowed? | Which FDs Must Be Removed? |
|:---:|---|---|
| **1NF** | Any | None (just atomic values) |
| **2NF** | Full FDs only | ❌ Partial FDs |
| **3NF** | Full + no transitive | ❌ Partial + Transitive FDs |
| **BCNF** | Only candidate key → non-key | ❌ Any FD where LHS is not a candidate key |

> **Interview tip:** The most common FD question is: "What is a transitive dependency and how does it relate to 3NF?" Answer: `X → Y → Z` where Y is not a candidate key. To achieve 3NF, you decompose the table to eliminate this chain. Similarly, "What is a partial dependency?" relates to 2NF — non-key attributes must depend on the **entire** primary key, not just part of it.

> 👉 The next section covers each normal form end-to-end: [Database Normalization — 1NF to BCNF](#database-normalization--1nf-2nf-3nf--bcnf).

---
---

# Database Anomalies

Anomalies are **problems that arise when a database table is not properly normalized**. They occur because of **redundant data** — the same piece of information is stored in multiple rows. When you try to insert, delete, or update data in such a table, you run into inconsistencies.

There are **three types** of anomalies: **Insertion**, **Deletion**, and **Update**.

---

## The Problematic Table (Unnormalized)

Consider this single table that stores student course enrollments along with department info:

| **StudentID** | **StudentName** | **CourseID** | **CourseName** | **Instructor** | **Department** | **DeptHead** |
|---|---|---|---|---|---|---|
| 101 | Alice | CS101 | Data Structures | Prof. Sharma | Computer Science | Dr. Gupta |
| 101 | Alice | CS102 | Algorithms | Prof. Verma | Computer Science | Dr. Gupta |
| 102 | Bob | CS101 | Data Structures | Prof. Sharma | Computer Science | Dr. Gupta |
| 103 | Carol | EE201 | Circuit Theory | Prof. Iyer | Electrical Eng | Dr. Rao |
| 103 | Carol | CS101 | Data Structures | Prof. Sharma | Computer Science | Dr. Gupta |

Notice the **redundancy**:
- `"Computer Science"` and `"Dr. Gupta"` appear in **4 rows**
- `"Data Structures"` and `"Prof. Sharma"` appear in **3 rows**
- Alice's name appears in **2 rows**

This redundancy is the root cause of all three anomalies.

---

## 1. Insertion Anomaly

> **Problem:** You **cannot insert** certain data without also inserting unrelated data that you don't have yet.

### Example

Suppose a **new department** is created: **"Mechanical Engineering"** with head **Dr. Joshi**. You want to record this in the database. But look at the table — every row requires a `StudentID`, `CourseID`, and `CourseName`.

**You can't insert the department without a student enrolled in a course in that department.**

| StudentID | StudentName | CourseID | CourseName | Instructor | Department | DeptHead |
|---|---|---|---|---|---|---|
| ??? | ??? | ??? | ??? | ??? | Mechanical Eng | Dr. Joshi |

You'd have to either:
- Insert `NULL` for `StudentID`, `CourseID`, etc. — violates the primary key constraint (if `StudentID + CourseID` is the composite PK)
- Wait until a student actually enrolls — but the department **already exists** in the real world!

**The anomaly:** A perfectly valid fact (a department exists) **cannot be represented** because it's forced to depend on unrelated data (student enrollment).

---

## 2. Deletion Anomaly

> **Problem:** Deleting a row causes you to **unintentionally lose** other important data.

### Example

Look at **Carol (103)** — she's the **only student** in the Electrical Engineering department:

| StudentID | StudentName | CourseID | CourseName | Instructor | Department | DeptHead |
|---|---|---|---|---|---|---|
| **103** | **Carol** | **EE201** | **Circuit Theory** | **Prof. Iyer** | **Electrical Eng** | **Dr. Rao** |

Now, if Carol **drops the course** (EE201), we delete this row.

**What we wanted to delete:** Carol's enrollment in Circuit Theory.

**What we also lost:**
- ❌ The fact that **"Circuit Theory"** is a course taught by **Prof. Iyer**
- ❌ The fact that **"Electrical Engineering"** department exists
- ❌ The fact that **Dr. Rao** is the head of Electrical Engineering

**The anomaly:** Removing one fact (student enrollment) accidentally **destroys** completely unrelated facts (department info, course info).

---

## 3. Update Anomaly

> **Problem:** Updating a piece of data requires changing it in **multiple rows**. If you miss even one row, the database becomes **inconsistent**.

### Example

Suppose **Dr. Gupta retires** and **Dr. Mehta** becomes the new head of Computer Science. You need to update every row where `Department = 'Computer Science'`:

| StudentID | StudentName | CourseID | CourseName | Instructor | Department | DeptHead |
|---|---|---|---|---|---|---|
| 101 | Alice | CS101 | Data Structures | Prof. Sharma | Computer Science | ~~Dr. Gupta~~ → **Dr. Mehta** |
| 101 | Alice | CS102 | Algorithms | Prof. Verma | Computer Science | ~~Dr. Gupta~~ → **Dr. Mehta** |
| 102 | Bob | CS101 | Data Structures | Prof. Sharma | Computer Science | ~~Dr. Gupta~~ → **Dr. Mehta** |
| 103 | Carol | CS101 | Data Structures | Prof. Sharma | Computer Science | ~~Dr. Gupta~~ → **Dr. Mehta** |

That's **4 rows** to update for a **single real-world change**. If you update only 3 of them:

| StudentID | StudentName | CourseID | CourseName | Instructor | Department | DeptHead |
|---|---|---|---|---|---|---|
| 101 | Alice | CS101 | Data Structures | Prof. Sharma | Computer Science | **Dr. Mehta** ✅ |
| 101 | Alice | CS102 | Algorithms | Prof. Verma | Computer Science | **Dr. Mehta** ✅ |
| 102 | Bob | CS101 | Data Structures | Prof. Sharma | Computer Science | **Dr. Gupta** ❌ |
| 103 | Carol | CS101 | Data Structures | Prof. Sharma | Computer Science | **Dr. Mehta** ✅ |

Now the database says **two different things** — Bob's row says Dr. Gupta is the head, while everyone else says Dr. Mehta. **Which is correct?** The database is now **inconsistent**.

**The anomaly:** A single fact is stored in multiple places, so updating it requires touching every copy. Missing one creates contradictory data.

---

## The Fix: Normalization

The solution is to **break the table into smaller, properly structured tables** where each fact is stored **exactly once**:

```
Students:        StudentID → StudentName
Courses:         CourseID  → CourseName, Instructor, DepartmentID
Departments:     DeptID    → Department, DeptHead
Enrollments:     StudentID, CourseID  (junction/relationship table)
```

**Students:**

| StudentID | StudentName |
|---|---|
| 101 | Alice |
| 102 | Bob |
| 103 | Carol |

**Departments:**

| DeptID | Department | DeptHead |
|---|---|---|
| 1 | Computer Science | Dr. Mehta |
| 2 | Electrical Eng | Dr. Rao |
| 3 | Mechanical Eng | Dr. Joshi ← no anomaly! |

**Courses:**

| CourseID | CourseName | Instructor | DeptID |
|---|---|---|---|
| CS101 | Data Structures | Prof. Sharma | 1 |
| CS102 | Algorithms | Prof. Verma | 1 |
| EE201 | Circuit Theory | Prof. Iyer | 2 |

**Enrollments:**

| StudentID | CourseID |
|---|---|
| 101 | CS101 |
| 101 | CS102 |
| 102 | CS101 |
| 103 | EE201 |
| 103 | CS101 |

Now:
- ✅ **Insertion:** Add Mechanical Eng without needing a student
- ✅ **Deletion:** Carol drops EE201 → delete from `Enrollments` only; Electrical Eng and Circuit Theory still exist
- ✅ **Update:** Change DeptHead → update **one row** in `Departments`, done

---

## Summary

| Anomaly | Problem | Cause |
|---|---|---|
| **Insertion** | Can't add data without unrelated data | Facts are bundled together in one table |
| **Deletion** | Removing a row destroys unrelated facts | Multiple independent facts share the same row |
| **Update** | Must change multiple rows for one real-world change; risk of inconsistency | Same fact is duplicated across many rows |
| **Fix** | **Normalize** — store each fact exactly once in its own table | |

> **The key insight:** Anomalies are a symptom of **poor table design** (redundancy). Normalization eliminates redundancy by ensuring each independent fact lives in exactly one place. This is why normalization (1NF → 2NF → 3NF → BCNF) exists — it systematically removes the structural flaws that cause these anomalies.

---
---

# Database Normalization — 1NF, 2NF, 3NF & BCNF

📖 **Reference:** [Database Normalization: 1NF, 2NF, 3NF & BCNF Examples — DigitalOcean](https://www.digitalocean.com/community/tutorials/database-normalization)

**Normalization** is the process of organizing the columns and tables of a relational database to **minimize data redundancy** and **eliminate update anomalies**. You do it by repeatedly **decomposing** a large table into smaller tables and linking them with **foreign keys**, so that every fact is stored in exactly **one place**.

> **One-line definition for interviews:** "Normalization is a step-by-step decomposition of tables, driven by functional dependencies, to remove redundancy and insert/update/delete anomalies — each normal form is a stricter rule about which dependencies are allowed to survive."

It was introduced by **E. F. Codd** (1NF/2NF/3NF in 1970–72) and refined into **BCNF** by Codd and Boyce (1974). Higher forms (4NF, 5NF) exist for multivalued and join dependencies, but real-world schemas are designed to **3NF**, occasionally **BCNF** — which is where this section stops.

---

## Why Normalize? — The Three Anomalies

Take an **unnormalized** table that stores everything about a student's enrolment in one place:

**`student_report` (bad design)**

| roll_no | student_name | phone | course_id | course_name | marks | dept | dept_head |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Alice | 9990001111, 9990002222 | C1 | DBMS | 88 | CSE | Dr. Smith |
| 1 | Alice | 9990001111, 9990002222 | C2 | OS | 91 | CSE | Dr. Smith |
| 2 | Bob | 8880003333 | C1 | DBMS | 75 | ECE | Dr. Jones |
| 3 | Carol | 7770004444 | C3 | Networks | 82 | CSE | Dr. Smith |

Notice `Alice`, `CSE`, and `Dr. Smith` repeated across rows. That redundancy creates three classic problems:

| Anomaly | What goes wrong | Example on the table above |
|---|---|---|
| **Insertion anomaly** | You cannot record a fact because unrelated data is missing | Can't add a new course `C4 — Compilers` until at least one student enrols in it (the PK needs `roll_no`) |
| **Update anomaly** | The same fact lives in many rows, so a partial update makes the data inconsistent | Alice changes her name → you must update **every** row for `roll_no = 1`; miss one and Alice has two names |
| **Deletion anomaly** | Deleting a row silently destroys an unrelated fact | Delete Bob's only enrolment row → you also lose the fact that `ECE`'s head is `Dr. Jones` |

```
  Redundancy  ──►  Anomalies  ──►  Inconsistent data
       │
       └──► Fix: decompose so every fact is stored EXACTLY ONCE
```

### Benefits vs Costs

| ✅ Benefits of normalizing | ❌ Costs of normalizing |
|---|---|
| Less redundancy → smaller storage | More tables → more **JOINs** per read query |
| No insert/update/delete anomalies | Reads can get slower (join cost) |
| Each fact updated in one place → consistency | More complex queries to write |
| Cleaner schema, easier to extend | Reporting/analytics queries may need denormalized copies |

---

## Anomalies Resolved by Normalization — Deep Dive

🔗 **Reference:** [DBA StackExchange — How does normalization fix the three types of update anomalies?](https://dba.stackexchange.com/questions/194631/how-does-normalization-fix-the-three-types-of-update-anomalies)

> **Terminology note:** all three are often grouped under the umbrella term **"update anomalies"** — because all three are symptoms of the *same* root cause. The three specific kinds are **insertion**, **deletion**, and **modification** (the last one is what most people mean by "update anomaly").

### The Root Cause — One Fact Stored in Many Places

```
  A non-key attribute depends on something that is NOT a key
                      │
                      ▼
  The DBMS cannot stop that value from repeating across rows
                      │
                      ▼
        REDUNDANCY  (the same fact stored N times)
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Insertion     Modification    Deletion
    anomaly        anomaly        anomaly
```

The key insight: **normalization does not "detect and repair" anomalies at runtime.** It restructures the schema so that each fact has exactly **one** home, which makes the anomaly *structurally impossible* — and turns the rule into a **key constraint the DBMS itself enforces**, instead of a convention your application code has to remember.

> **The single sentence that answers the interview question:** "An anomaly is a symptom of redundancy; redundancy is a symptom of a dependency on a non-key. Remove the dependency by decomposing, and all three anomalies disappear at once — because there's no longer more than one row that has to agree."

### The Faulty Table We'll Fix

**`student_report`** — PK is `{roll_no, course_id}`:

| roll_no | student_name | course_id | course_name | marks | dept | dept_head |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Alice | C1 | DBMS | 88 | CSE | Dr. Smith |
| 1 | Alice | C2 | OS | 91 | CSE | Dr. Smith |
| 2 | Bob | C1 | DBMS | 75 | ECE | Dr. Jones |
| 3 | Carol | C3 | Networks | 82 | CSE | Dr. Smith |

---

### 1. Insertion Anomaly

**Definition:** you cannot store a valid, standalone fact because the table's key forces you to supply unrelated data you don't have yet.

| Scenario | What blocks you |
|---|---|
| Add a new course `C4 — Compilers` that nobody has enrolled in yet | The PK requires `roll_no`, so there's no legal row for a course by itself |
| Register a new department `MECH` with head `Dr. Iyer` | You need at least one student in `MECH` first |
| Admit a student who hasn't picked courses yet | `course_id` is part of the PK and cannot be NULL |

```sql
-- ❌ Impossible on the unnormalized table: no student, no row
INSERT INTO student_report (course_id, course_name) VALUES ('C4', 'Compilers');
--   ERROR: Column 'roll_no' cannot be null (part of the primary key)

-- The ugly workaround people reach for — a fake placeholder row:
INSERT INTO student_report VALUES (NULL, NULL, 'C4', 'Compilers', NULL, NULL, NULL);
--   Illegal (PK can't be NULL), and pollutes the table if forced through
```

**✅ How normalization fixes it — 2NF/3NF give each entity its own table:**

```sql
INSERT INTO courses     VALUES ('C4', 'Compilers');        -- course exists on its own
INSERT INTO departments VALUES ('MECH', 'Dr. Iyer');       -- department exists on its own
INSERT INTO students    VALUES (4, 'Dave', 'MECH');        -- student with no enrolments yet
```

**Why it works:** an *independent entity* now has an *independent table* with its own primary key, so its existence no longer depends on a related row existing.

---

### 2. Modification (Update) Anomaly

**Definition:** the same fact is stored in multiple rows, so an update must touch **all** of them. Update some and not others → the database now holds **two contradictory versions of one truth**.

| Scenario | Rows that must all change together |
|---|---|
| Rename course `DBMS` → `Database Systems` | Every enrolment row for `C1` |
| CSE's head changes to `Dr. Nair` | Every row of every CSE student |
| Alice's name is corrected to `Alicia` | Every enrolment row for `roll_no = 1` |

```sql
-- ❌ On the unnormalized table this MUST hit every matching row
UPDATE student_report SET dept_head = 'Dr. Nair' WHERE dept = 'CSE';
```

If that statement is filtered wrongly, interrupted, or run as several statements and one fails, you get:

| roll_no | dept | dept_head |
|:---:|:---:|:---:|
| 1 | CSE | Dr. Nair | ← updated
| 3 | CSE | Dr. Smith | ← **missed — the database now contradicts itself**

Nothing in the schema forbids this state: `dept_head` is not determined by any key, so the DBMS has no basis to reject it.

**✅ How normalization fixes it — 3NF puts the fact in one row:**

```sql
UPDATE departments SET dept_head = 'Dr. Nair' WHERE dept = 'CSE';   -- exactly 1 row
UPDATE courses     SET course_name = 'Database Systems' WHERE course_id = 'C1';
UPDATE students    SET student_name = 'Alicia' WHERE roll_no = 1;
```

**Why it works:** a single-row update is **atomic by construction** — there is no second copy left behind to disagree with. Partial-update inconsistency becomes unrepresentable.

---

### 3. Deletion Anomaly

**Definition:** deleting a row destroys **unrelated** facts that happened to be co-located in it, because that row was the *only* place they were stored.

| Scenario | Collateral damage |
|---|---|
| Bob drops course `C1` (his only enrolment) | You also lose "Bob is a student" **and** "ECE's head is Dr. Jones" |
| Course `C3` is discontinued | You lose the fact that Carol is a student in CSE |
| Last CSE student graduates | The CSE department vanishes from the database |

```sql
-- ❌ Intent: "Bob dropped one course."  Actual effect: Bob and ECE cease to exist.
DELETE FROM student_report WHERE roll_no = 2 AND course_id = 'C1';
```

**✅ How normalization fixes it — separate lifetimes, separate tables:**

```sql
-- Intent maps exactly to one table; nothing else is touched
DELETE FROM enrollment WHERE roll_no = 2 AND course_id = 'C1';

-- students(2, 'Bob', 'ECE')          → still there ✅
-- departments('ECE', 'Dr. Jones')    → still there ✅
```

**Why it works:** each table now models one entity with its **own lifecycle**. Removing an enrolment removes only the enrolment. Foreign keys with `ON DELETE RESTRICT` / `CASCADE` then let you state deliberately what *should* cascade — instead of losing data by accident.

---

### Which Normal Form Fixes Which Anomaly?

| Normal Form | Dependency removed | Anomalies it eliminates |
|:---:|---|---|
| **1NF** | Multi-valued cells / repeating groups | Can't insert, search, or delete an individual value inside a cell |
| **2NF** | **Partial** (`part-of-key → non-key`) | Course/student facts duplicated per enrolment — insert a course with no students; rename a course once |
| **3NF** | **Transitive** (`non-key → non-key`) | Department facts duplicated per student — register a department with no students; change its head once; keep it when the last student leaves |
| **BCNF** | Any FD whose LHS isn't a super key | Residual anomalies when candidate keys overlap (e.g. record a teacher's subject before any student enrols) |

---

### Before ➜ After, Side by Side

| Operation | Unnormalized `student_report` | Normalized (3NF) schema |
|---|---|---|
| Add a course nobody takes | ❌ Impossible (PK needs `roll_no`) | ✅ 1 `INSERT` into `courses` |
| Add a department with no students | ❌ Impossible | ✅ 1 `INSERT` into `departments` |
| Rename a course | ⚠️ N rows; partial failure ⇒ inconsistency | ✅ 1 row in `courses` |
| Change a department head | ⚠️ N rows; partial failure ⇒ inconsistency | ✅ 1 row in `departments` |
| Student drops one course | ❌ May delete the student and the department too | ✅ 1 `DELETE` from `enrollment` |
| Who enforces the rule? | 🙋 Application code / developer discipline | 🔒 The DBMS, via primary and foreign keys |

> **Key takeaway:** anomalies aren't a separate problem to be patched — they're the *observable symptom* of redundancy. Normalization attacks the cause. Every normal form is really the same instruction restated at a stricter level: **store each fact exactly once, in the table whose key determines it.**

---

## The Ladder of Normal Forms

Each form **includes** the previous one — you cannot be in 3NF without already being in 2NF and 1NF.

```
  Unnormalized (UNF)
        │  remove multi-valued / repeating groups → atomic values
        ▼
      1NF
        │  remove PARTIAL dependencies (part of the composite key → non-key)
        ▼
      2NF
        │  remove TRANSITIVE dependencies (non-key → non-key)
        ▼
      3NF
        │  every determinant (LHS of an FD) must be a candidate key
        ▼
      BCNF
```

| Normal Form | Rule in one line | Removes |
|:---:|---|---|
| **1NF** | Every cell holds a **single atomic value**; no repeating groups | Multi-valued attributes |
| **2NF** | 1NF **+** every non-key attribute depends on the **whole** key | Partial dependencies |
| **3NF** | 2NF **+** no non-key attribute depends on another non-key attribute | Transitive dependencies |
| **BCNF** | For every non-trivial FD `X → Y`, **X must be a super key** | Anomalies from overlapping candidate keys |

---

## 1NF — First Normal Form

**Rule:** every attribute must be **atomic** (single-valued and indivisible), each column must hold one data type, and there must be **no repeating groups** or arrays inside a cell. Row order and column order must carry no meaning.

### ❌ Violates 1NF

`phone` stores two numbers in one cell:

| roll_no | student_name | phone |
|:---:|:---:|:---|
| 1 | Alice | 9990001111, 9990002222 |
| 2 | Bob | 8880003333 |

**Why it's a problem:** you can't index or search a single phone efficiently, `WHERE phone = '9990002222'` needs string matching, and adding/removing one number means rewriting the whole cell.

### The other bad "fix" — repeating columns

| roll_no | student_name | phone1 | phone2 | phone3 |
|:---:|:---:|:---:|:---:|:---:|
| 1 | Alice | 9990001111 | 9990002222 | NULL |

This is still wrong: it caps how many phones a student can have and fills the table with NULLs. **Repeating groups (`phone1..phoneN`) are a 1NF violation, not a solution.**

### ✅ In 1NF — one row per value

**`students`**

| roll_no (PK) | student_name |
|:---:|:---:|
| 1 | Alice |
| 2 | Bob |

**`student_phones`**

| roll_no (PK, FK) | phone (PK) |
|:---:|:---:|
| 1 | 9990001111 |
| 1 | 9990002222 |
| 2 | 8880003333 |

```sql
CREATE TABLE students (
    roll_no      INT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL
);

CREATE TABLE student_phones (
    roll_no INT,
    phone   VARCHAR(15),
    PRIMARY KEY (roll_no, phone),          -- composite key: a student can have many phones
    FOREIGN KEY (roll_no) REFERENCES students(roll_no) ON DELETE CASCADE
);
```

> **Gotcha:** a comma-separated list, a JSON array, or `tags = "sql,dbms,index"` inside a `VARCHAR` column all violate 1NF in the classical sense. Modern databases *support* JSON/array columns, and they're a pragmatic choice when the value is opaque to the database — but you lose per-element constraints, foreign keys, and clean indexing.

---

## 2NF — Second Normal Form

**Rule:** the table is in **1NF**, and **no non-prime attribute is partially dependent on any candidate key**. In practice: every non-key column must depend on the **entire** primary key, not just part of it.

> 2NF only becomes interesting when the primary key is **composite**. If the PK is a single column, no partial dependency is possible, so a 1NF table with a single-column PK is automatically in 2NF.

### ❌ Violates 2NF

**`enrollment`** with composite primary key `{roll_no, course_id}`:

| roll_no | course_id | student_name | course_name | marks |
|:---:|:---:|:---:|:---:|:---:|
| 1 | C1 | Alice | DBMS | 88 |
| 1 | C2 | Alice | OS | 91 |
| 2 | C1 | Bob | DBMS | 75 |
| 3 | C3 | Carol | Networks | 82 |

The functional dependencies:

```
  {roll_no, course_id} → marks         ✅ FULL dependency (needs both)
   roll_no             → student_name  ❌ PARTIAL (only part of the key)
   course_id           → course_name   ❌ PARTIAL (only part of the key)
```

**Consequences:** `Alice` repeats for every course she takes; `DBMS` repeats for every student who takes it. Rename the course `DBMS` → `Database Systems` and you must touch every enrolment row.

### ✅ In 2NF — one table per dependency

**`students`**

| roll_no (PK) | student_name |
|:---:|:---:|
| 1 | Alice |
| 2 | Bob |
| 3 | Carol |

**`courses`**

| course_id (PK) | course_name |
|:---:|:---:|
| C1 | DBMS |
| C2 | OS |
| C3 | Networks |

**`enrollment`**

| roll_no (PK, FK) | course_id (PK, FK) | marks |
|:---:|:---:|:---:|
| 1 | C1 | 88 |
| 1 | C2 | 91 |
| 2 | C1 | 75 |
| 3 | C3 | 82 |

```sql
CREATE TABLE courses (
    course_id   VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL
);

CREATE TABLE enrollment (
    roll_no   INT,
    course_id VARCHAR(10),
    marks     INT,
    PRIMARY KEY (roll_no, course_id),      -- marks depends on the FULL key
    FOREIGN KEY (roll_no)   REFERENCES students(roll_no),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

Now a course rename is a **single-row update** in `courses`, and a new course can be inserted before anyone enrols — the insertion anomaly is gone.

---

## 3NF — Third Normal Form

**Rule:** the table is in **2NF**, and **no non-prime attribute is transitively dependent** on the primary key. Equivalently, for every non-trivial FD `X → Y`, either **X is a super key** *or* **Y is a prime attribute** (part of some candidate key).

Plain English: **every non-key column must depend on the key, the whole key, and nothing but the key.**

### ❌ Violates 3NF

**`students`**

| roll_no (PK) | student_name | dept | dept_head |
|:---:|:---:|:---:|:---:|
| 1 | Alice | CSE | Dr. Smith |
| 2 | Bob | ECE | Dr. Jones |
| 3 | Carol | CSE | Dr. Smith |

The dependency chain:

```
  roll_no → dept → dept_head          (dept is NOT a candidate key)
      └────────────────► transitive dependency
```

`dept_head` doesn't really describe a *student* — it describes a *department*. So `Dr. Smith` is duplicated for every CSE student.

**Anomalies it causes:**
- **Update:** CSE gets a new head → update every CSE student row.
- **Delete:** remove the last CSE student → you lose the fact that CSE's head is Dr. Smith.
- **Insert:** you can't register a brand-new department until a student joins it.

### ✅ In 3NF

**`students`**

| roll_no (PK) | student_name | dept (FK) |
|:---:|:---:|:---:|
| 1 | Alice | CSE |
| 2 | Bob | ECE |
| 3 | Carol | CSE |

**`departments`**

| dept (PK) | dept_head |
|:---:|:---:|
| CSE | Dr. Smith |
| ECE | Dr. Jones |

```sql
CREATE TABLE departments (
    dept      VARCHAR(10) PRIMARY KEY,
    dept_head VARCHAR(100) NOT NULL
);

ALTER TABLE students
    ADD COLUMN dept VARCHAR(10),
    ADD FOREIGN KEY (dept) REFERENCES departments(dept);
```

> **Rule of thumb:** if a column would still make sense in a table *about something else*, it probably belongs in that other table. `dept_head` describes a department, so it lives in `departments`.

> **3NF is the practical target** for most OLTP schemas. It removes almost all redundancy while keeping the join count reasonable.

---

## BCNF — Boyce–Codd Normal Form (3.5NF)

**Rule:** for **every** non-trivial functional dependency `X → Y`, **X must be a super key**. BCNF is 3NF *without* the escape clause "…or Y is a prime attribute" — so it is strictly stronger.

BCNF only differs from 3NF when a table has **multiple overlapping candidate keys**.

### ❌ In 3NF but violates BCNF — the classic example

**`teaches`** — a student takes a subject from exactly one teacher, and each teacher teaches exactly one subject:

| student | subject | teacher |
|:---:|:---:|:---:|
| Alice | DBMS | Dr. Smith |
| Alice | OS | Dr. Rao |
| Bob | DBMS | Dr. Verma |
| Carol | DBMS | Dr. Smith |

Functional dependencies and keys:

```
  {student, subject} → teacher        (candidate key → non-prime)
   teacher           → subject        (teacher is NOT a super key!)

  Candidate keys: {student, subject}  and  {student, teacher}
  Prime attributes: student, subject, teacher   ← all of them!
```

**Why it's in 3NF:** in `teacher → subject`, the right-hand side `subject` *is* a prime attribute, so 3NF's escape clause is satisfied.
**Why it fails BCNF:** the determinant `teacher` is not a super key.

**The anomaly that survives 3NF:** you cannot record that `Dr. Kumar` teaches `Networks` until some student takes it, and if `Dr. Smith` switches to `Compilers` you must update multiple rows.

### ✅ In BCNF — decompose on the offending determinant

**`teacher_subject`**

| teacher (PK) | subject |
|:---:|:---:|
| Dr. Smith | DBMS |
| Dr. Rao | OS |
| Dr. Verma | DBMS |

**`student_teacher`**

| student (PK) | teacher (PK, FK) |
|:---:|:---:|
| Alice | Dr. Smith |
| Alice | Dr. Rao |
| Bob | Dr. Verma |
| Carol | Dr. Smith |

> ⚠️ **The BCNF trade-off:** this decomposition is **lossless**, but it is **not dependency-preserving** — the FD `{student, subject} → teacher` can no longer be enforced by a key inside a single table. Nothing stops the same student from being assigned two teachers for DBMS unless you add an application-level or trigger-based check.

### 3NF vs BCNF

| | 3NF | BCNF |
|---|---|---|
| Condition on `X → Y` | X is a super key **OR** Y is prime | X **must** be a super key |
| Strength | Weaker | Stronger (3NF ⊇ BCNF) |
| Lossless decomposition | Always achievable | Always achievable |
| Dependency preservation | **Always** achievable | **Not always** achievable |
| Redundancy left | Some (when candidate keys overlap) | Essentially none from FDs |

> **Interview answer:** "Every BCNF table is in 3NF, but not vice versa. 3NF allows an FD whose determinant isn't a super key as long as the dependent attribute is part of some candidate key. BCNF forbids that. The practical catch is that BCNF decomposition can lose dependency preservation, which is why real schemas often stop at 3NF."

---

## Two Rules Every Decomposition Must Respect

When you split a table `R` into `R1` and `R2`, check both properties:

### 1. Lossless Join (mandatory)

`R1 ⋈ R2` must give back **exactly** `R` — no lost rows, no spurious extra rows.

```
  Condition:  attributes(R1) ∩ attributes(R2)  must contain a
              super key of R1 or of R2
```

**Lossy example:** splitting `student_report(roll_no, course_id, marks)` into `(roll_no, marks)` and `(course_id, marks)` and joining on `marks` produces garbage rows — `marks` is not a key of either part.

### 2. Dependency Preservation (desirable)

Every FD of `R` should be checkable inside **one** of the decomposed tables, without needing a join. If not, the constraint has to move into application logic or a trigger.

| Property | 3NF | BCNF |
|---|:---:|:---:|
| Lossless join | ✅ Always | ✅ Always |
| Dependency preservation | ✅ Always | ⚠️ Not guaranteed |

> **This is exactly why 3NF is the industry default:** it's the strongest form you can always reach while keeping *both* properties.

---

## Denormalization — Deliberately Going Backwards

**Denormalization** is intentionally reintroducing redundancy to make reads faster: fewer joins, precomputed aggregates, duplicated columns.

| Technique | Example | Cost |
|---|---|---|
| Duplicate a column | Store `customer_name` on `orders` to avoid a join | Must keep both copies in sync |
| Precomputed aggregate | Store `order_count` on `customers` | Needs a trigger / batch job / app-level update |
| Materialized view | Nightly refreshed report table | Data is stale until the next refresh |
| Wide/flattened table | One analytics table instead of 8 joined ones | Large storage, expensive writes |

**When denormalization is justified**

- Read-heavy workload where the join is provably the bottleneck (confirm with `EXPLAIN` first — see [How to Optimize a SQL Query](#how-to-optimize-a-sql-query)).
- Analytics / reporting / dashboards where staleness is acceptable.
- Aggregates too expensive to compute per request (feed counts, leaderboards).

**When it is not**

- Before measuring. Indexing usually beats denormalizing.
- On write-heavy, correctness-critical tables (money, inventory) — every duplicated copy is a chance to be inconsistent.

> **Interview answer:** "Normalize first for correctness, then denormalize selectively where measurements show a join or aggregate is the bottleneck — and always with a clear plan for keeping the duplicated data in sync."

---

## Full Walkthrough — UNF ➜ 3NF in One Pass

Starting from the very first table on this page:

```
  UNF:  student_report(roll_no, student_name, phone(multi), course_id,
                       course_name, marks, dept, dept_head)

  Step 1 — 1NF: phone has multiple values in one cell
     ➜ students(roll_no, student_name, dept, dept_head)
       student_phones(roll_no, phone)
       enrollment(roll_no, course_id, course_name, marks)

  Step 2 — 2NF: in enrollment, PK = {roll_no, course_id},
                but course_id → course_name is PARTIAL
     ➜ courses(course_id, course_name)
       enrollment(roll_no, course_id, marks)

  Step 3 — 3NF: in students, roll_no → dept → dept_head is TRANSITIVE
     ➜ departments(dept, dept_head)
       students(roll_no, student_name, dept)
```

**Final schema (3NF)**

```sql
CREATE TABLE departments (
    dept      VARCHAR(10)  PRIMARY KEY,
    dept_head VARCHAR(100) NOT NULL
);

CREATE TABLE students (
    roll_no      INT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    dept         VARCHAR(10),
    FOREIGN KEY (dept) REFERENCES departments(dept)
);

CREATE TABLE student_phones (
    roll_no INT,
    phone   VARCHAR(15),
    PRIMARY KEY (roll_no, phone),
    FOREIGN KEY (roll_no) REFERENCES students(roll_no) ON DELETE CASCADE
);

CREATE TABLE courses (
    course_id   VARCHAR(10)  PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL
);

CREATE TABLE enrollment (
    roll_no   INT,
    course_id VARCHAR(10),
    marks     INT,
    PRIMARY KEY (roll_no, course_id),
    FOREIGN KEY (roll_no)   REFERENCES students(roll_no),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

```
  departments 1───N students 1───N student_phones
                      │
                      N
                      │
                  enrollment  N───1 courses
```

Every fact now lives in exactly one place: a student's name in `students`, a course's title in `courses`, a department's head in `departments`, and a grade in `enrollment`.

---

## How to Normalize — A Practical Checklist

1. **List the attributes** and the real-world facts they represent.
2. **Write down the functional dependencies** (see [Functional Dependencies](#functional-dependencies-in-dbms)).
3. **Find all candidate keys** using the attribute-closure method.
4. **1NF** — is every cell atomic? Any list, array, or `col1..colN` group?
5. **2NF** — is the PK composite? Does any non-key column depend on only *part* of it?
6. **3NF** — does any non-key column depend on another *non-key* column?
7. **BCNF** — is the LHS of every FD a super key? If not, decide whether losing dependency preservation is acceptable.
8. **Verify** each decomposition is **lossless**, and note any FD you can no longer enforce with a key.
9. **Measure**, then denormalize only where reads demand it.

---

## Quick-Fire Q&A

| Question | Answer |
|---|---|
| **What is normalization?** | Decomposing tables to remove redundancy and insert/update/delete anomalies, guided by functional dependencies |
| **Which normal form do real systems use?** | **3NF** (sometimes BCNF) for OLTP; deliberately denormalized star/snowflake schemas for analytics |
| **Can a 1NF table with a single-column PK violate 2NF?** | No — partial dependencies require a **composite** key |
| **Difference between 2NF and 3NF?** | 2NF removes **partial** dependencies; 3NF removes **transitive** ones |
| **Is every 3NF table in BCNF?** | No. 3NF allows `X → Y` where X isn't a super key if Y is a prime attribute |
| **Why not always go to BCNF?** | BCNF decomposition may not be **dependency-preserving**, forcing constraints into application code |
| **What must every decomposition guarantee?** | **Lossless join** — rejoining the parts reproduces the original relation exactly |
| **Downside of normalization?** | More tables → more joins → potentially slower reads and more complex queries |
| **What is denormalization?** | Deliberately adding redundancy (duplicated columns, precomputed aggregates) to speed up reads |
| **Higher normal form ⇒ better performance?** | No. It improves **integrity**; read performance often *drops* because of extra joins |

> **Interview strategy:** define normalization in one sentence, name the anomaly it prevents, then walk one table from 1NF → 3NF using a concrete example (the `student_report` table above works well). Finish by mentioning that 3NF is the practical stopping point and that BCNF can cost dependency preservation — that last point is what separates a memorized answer from an understood one.

---
---

# Transactions in DBMS

🔗 **Reference:** [Tutorialspoint — DBMS Transaction](https://www.tutorialspoint.com/dbms/dbms_transaction.htm)

A **transaction** is a logical unit of work that consists of one or more SQL operations executed as a **single, indivisible unit**. Either ALL operations complete successfully, or NONE of them take effect.

> **Think of it this way:** A bank transfer from A to B involves two steps — debit A and credit B. If the system crashes after debiting A but before crediting B, money vanishes. A transaction guarantees that both steps succeed together or both fail together.

---

## Bank Transfer Example

Transfer ₹500 from Account A to Account B:

```
  Transaction T:
  ─────────────
  Step 1:  Read(A)           → A = 1000
  Step 2:  A = A - 500       → A = 500
  Step 3:  Write(A)          → Save A = 500
  Step 4:  Read(B)           → B = 2000
  Step 5:  B = B + 500       → B = 2500
  Step 6:  Write(B)          → Save B = 2500
  Step 7:  COMMIT            → Make permanent
```

```
  Before:  A = 1000,  B = 2000   (Total = 3000)
  After:   A = 500,   B = 2500   (Total = 3000) ✅ Consistent!

  If crash after Step 3 (without transaction):
           A = 500,   B = 2000   (Total = 2500) ❌ ₹500 lost!
```

---

## ACID Properties

🔗 **Reference:** [GeeksforGeeks — ACID Properties in DBMS](https://www.geeksforgeeks.org/acid-properties-in-dbms/)

Every transaction must satisfy these four properties to ensure data integrity:

```
  ┌──────────────────────────────────────────────────┐
  │                 A C I D                          │
  ├──────────┬──────────┬──────────┬─────────────────┤
  │ Atomicity│Consistency│Isolation │   Durability    │
  │          │          │          │                 │
  │ All or   │ Valid    │ Txns     │ Committed data  │
  │ Nothing  │ state   │ don't    │ survives        │
  │          │ always  │ interfere│ crashes         │
  └──────────┴──────────┴──────────┴─────────────────┘
```

### 1. Atomicity — "All or Nothing"

Either ALL operations of a transaction are executed, or NONE are. No partial execution.

```
  ✅ Success: All steps complete → COMMIT
  ┌───────────────────────────────────────┐
  │  Read(A) → A-500 → Write(A)          │
  │  Read(B) → B+500 → Write(B)          │ → COMMIT ✅
  │  All steps done                       │
  └───────────────────────────────────────┘

  ❌ Failure: Crash after step 3 → ROLLBACK everything
  ┌───────────────────────────────────────┐
  │  Read(A) → A-500 → Write(A)          │
  │  💥 CRASH!                            │ → ROLLBACK ❌
  │  Undo Write(A) → A back to 1000      │
  └───────────────────────────────────────┘
```

> Managed by the **Transaction Management** component and **Undo Log**.

### 2. Consistency — "Valid State to Valid State"

The database must go from one **consistent state** to another. All integrity constraints (PK, FK, CHECK, etc.) must hold before and after the transaction.

```
  Before:  A + B = 3000  (consistent)
  After:   A + B = 3000  (still consistent) ✅

  If A + B ≠ 3000 after transaction → inconsistent → violation!
```

> The application/developer is responsible for writing correct transaction logic. The DBMS enforces constraints.

### 3. Isolation — "Transactions Don't Interfere"

Even when multiple transactions run **concurrently**, each transaction must behave as if it's the **only one** running. One transaction's intermediate state must NOT be visible to another.

```
  Without Isolation (problem):
  ─────────────────────────────
  T1: Read(A) = 1000
  T1: A = A - 500 = 500
                              T2: Read(A) = 1000  ← reads OLD value!
  T1: Write(A) = 500
                              T2: A = A - 200 = 800
                              T2: Write(A) = 800  ← overwrites T1's change!
  Result: A = 800 (₹500 deducted by T1 is LOST!)

  With Isolation (correct):
  ──────────────────────────
  T1 runs completely FIRST, then T2 runs
  OR they run concurrently but produce the SAME result as serial execution
```

> Managed by **Concurrency Control** (locks, MVCC, timestamps).

### 4. Durability — "Committed Data Survives Crashes"

Once a transaction is **committed**, its changes are **permanent** — even if the system crashes, loses power, or restarts.

```
  T1: Write(A) = 500
  T1: Write(B) = 2500
  T1: COMMIT ✅

  💥 System crash!

  After restart: A = 500, B = 2500  ← data is safe ✅
```

> Managed by **Write-Ahead Logging (WAL)** — changes are written to a log on disk BEFORE they're applied to the database.

### ACID Summary Table

| Property | Meaning | Ensures | Managed By |
|:---:|---------|---------|-----------|
| **Atomicity** | All or nothing | No partial transactions | Transaction Manager, Undo Log |
| **Consistency** | Valid state → Valid state | Integrity constraints hold | Application + DBMS constraints |
| **Isolation** | Transactions don't interfere | Concurrent = Serial result | Concurrency Control (Locks/MVCC) |
| **Durability** | Committed = Permanent | Survives crashes | WAL, Redo Log |

---

## Transaction States

🔗 **Reference:** [Gate Vidyalay — Transaction States in DBMS](https://www.gatevidyalay.com/transaction-states-in-dbms/)

A transaction goes through the following states during its lifecycle:

```
                        ┌─────────────────────┐
                        │      Active         │ ← Initial state
                        │  (executing ops)    │
                        └──────────┬──────────┘
                                   │
                          (last operation done)
                                   │
                        ┌──────────▼──────────┐
                        │ Partially Committed │ ← All ops done,
                        │  (awaiting commit)  │   not yet permanent
                        └──────────┬──────────┘
                         ┌─────────┴─────────┐
                    (success)             (failure)
                         │                   │
              ┌──────────▼──────┐  ┌─────────▼─────────┐
              │    Committed    │  │      Failed        │
              │  (permanent)   │  │  (cannot proceed)  │
              └─────────────────┘  └─────────┬─────────┘
                                             │
                                      (rollback all)
                                             │
                                   ┌─────────▼─────────┐
                                   │     Aborted        │
                                   │ (rolled back)      │
                                   └─────────┬─────────┘
                                      ┌──────┴──────┐
                                      │             │
                                  Restart        Kill
                                  (retry)       (cancel)
```

| State | Description |
|:---:|-------------|
| **Active** | Transaction is executing. Initial state of every transaction. |
| **Partially Committed** | Final operation has been executed, but not yet written to disk permanently. |
| **Committed** | All changes are permanently saved. Transaction is complete. ✅ |
| **Failed** | An error or check failure occurs. Transaction cannot proceed. |
| **Aborted** | All changes are rolled back. Database restored to pre-transaction state. After abort: restart or kill. |
| **Terminated** | The final state. The transaction has left the system — reached either via **Committed** or via **Aborted** (and then killed rather than restarted). |

> **Why "Terminated" matters:** it's the single exit state of the lifecycle. `Committed → Terminated` is the happy path; `Aborted → Terminated` is the give-up path. A restarted transaction is a **brand-new** transaction, not a continuation of the aborted one.

### Example State Transitions

```
  Successful Transaction:
  Active → Partially Committed → Committed ✅

  Failed Transaction:
  Active → Failed → Aborted (→ Restart or Kill) ❌

  Failure during commit:
  Active → Partially Committed → Failed → Aborted ❌
```

---

## Schedules

A **schedule** is the chronological order in which operations from multiple transactions are executed.

### Serial Schedule

Transactions are executed **one after another** — no interleaving. Always **correct** but **slow**.

```
  Serial Schedule (T1 then T2):
  ────────────────────────────
  T1: Read(A)
  T1: Write(A)
  T1: Read(B)
  T1: Write(B)
  T1: COMMIT
  ─────────────── T1 done
  T2: Read(A)
  T2: Write(A)
  T2: COMMIT
  ─────────────── T2 done
```

> ✅ Always produces correct results
> ❌ Very slow — no parallelism

### Concurrent (Non-Serial) Schedule

Operations from different transactions are **interleaved**. Fast, but could produce **incorrect results** if not managed properly.

```
  Concurrent Schedule (T1 and T2 interleaved):
  ─────────────────────────────────────────────
  T1: Read(A)
  T2: Read(A)      ← interleaved!
  T1: Write(A)
  T2: Write(A)     ← might overwrite T1's change!
  T1: Read(B)
  T1: Write(B)
  T1: COMMIT
  T2: COMMIT
```

> The question is: **Is this concurrent schedule equivalent to some serial schedule?** If yes → it's **serializable** → safe to use.

---

## Serializability

A concurrent schedule is **serializable** if it produces the same result as some serial schedule. Serializability is the **gold standard** for correctness.

```
  Serial Schedule S1:         Serial Schedule S2:       Concurrent Schedule S3:
  T1 then T2                  T2 then T1                T1 & T2 interleaved

  If S3 produces same         If S3 produces same
  result as S1 → ✅           result as S2 → ✅         S3 is serializable!
  serializable                serializable
```

### Types of Serializability

| Type | Definition |
|:---:|-----------|
| **Conflict Serializable** | Can be converted to a serial schedule by swapping **non-conflicting** operations |
| **View Serializable** | Produces the same "view" (same reads, same final writes) as a serial schedule |

> All conflict-serializable schedules are view-serializable, but NOT vice versa.

```
  ┌───────────────────────────┐
  │   View Serializable       │
  │  ┌─────────────────────┐  │
  │  │ Conflict Serializable│  │
  │  │                     │  │
  │  └─────────────────────┘  │
  └───────────────────────────┘
  Conflict ⊂ View (Conflict is stricter)
```

---

## Conflicting Operations

Two operations **conflict** if ALL three conditions are met:

1. They belong to **different transactions**
2. They access the **same data item**
3. At least one is a **write** operation

| T1 Op | T2 Op | Same Item? | Conflict? | Why |
|:---:|:---:|:---:|:---:|-----|
| Read(A) | Read(A) | ✅ | ❌ | Both are reads — no conflict |
| Read(A) | Write(A) | ✅ | ✅ | One is write — **Read-Write conflict** |
| Write(A) | Read(A) | ✅ | ✅ | One is write — **Write-Read conflict** |
| Write(A) | Write(A) | ✅ | ✅ | Both are writes — **Write-Write conflict** |
| Read(A) | Write(B) | ❌ | ❌ | Different items — no conflict |

### Non-Conflicting Operations Can Be Swapped

If two adjacent operations are **non-conflicting**, you can swap their order without changing the result. By repeatedly swapping, you can try to convert a concurrent schedule into a serial one.

```
  Schedule S:                  After swapping non-conflicting ops:
  T1: Read(A)                  T1: Read(A)
  T2: Read(B)    ← swap       T1: Write(A)    ← T1 ops together
  T1: Write(A)       ↑        T2: Read(B)
  T2: Write(B)                T2: Write(B)

  → Equivalent to serial schedule (T1 then T2) ✅
  → S is CONFLICT SERIALIZABLE
```

---

## Conflict Serializability — Precedence Graph

🔗 **References:** [GeeksforGeeks — Conflict Serializability in DBMS](https://www.geeksforgeeks.org/dbms/conflict-serializability-in-dbms/) · [Javatpoint — Conflict Serializable Schedule](https://www.javatpoint.com/dbms-conflict-serializable-schedule)

To test if a schedule is conflict-serializable, build a **precedence (dependency) graph**:

1. Create a node for each transaction
2. Draw an edge `Ti → Tj` if Ti has a conflicting operation that appears **before** Tj's conflicting operation
3. If the graph has **no cycle** → **conflict serializable** ✅
4. If the graph has a **cycle** → **NOT conflict serializable** ❌

### Example

```
  Schedule:
  T1: Read(A)
  T2: Read(A)
  T1: Write(A)     ← T1 writes A, T2 read A before → T2 → T1? No...
  T2: Write(A)     ← T1 writes A before T2 writes A → T1 → T2

  Precedence Graph:
  T1 ──────→ T2

  No cycle → ✅ Conflict Serializable!
  Equivalent to serial schedule: T1, T2
```

### Example with a Cycle (NOT Serializable)

```
  Schedule:
  T1: Read(A)
  T2: Write(A)    ← T1 read A, T2 writes A → T1 → T2
  T2: Read(B)
  T1: Write(B)    ← T2 read B, T1 writes B → T2 → T1

  Precedence Graph:
  T1 ──→ T2
  T2 ──→ T1   (CYCLE!)

  Cycle detected → ❌ NOT Conflict Serializable
```

---

## View Equivalence

Two schedules S1 and S2 are **view equivalent** if:

1. **Initial Read:** If Ti reads the initial value of X in S1, Ti also reads the initial value of X in S2
2. **Updated Read:** If Ti reads a value written by Tj in S1, Ti also reads the value written by Tj in S2
3. **Final Write:** If Ti performs the final write on X in S1, Ti also performs the final write on X in S2

> View serializability is **less restrictive** than conflict serializability. Some schedules that are NOT conflict-serializable may still be view-serializable.

---

## Equivalence Schedules Summary

| Type | Definition | How to Check |
|------|-----------|-------------|
| **Result Equivalent** | Produce same final result | Not reliable — may vary with different data |
| **View Equivalent** | Same initial reads, same read-from, same final writes | Check 3 conditions (complex) |
| **Conflict Equivalent** | Same order of conflicting operations | Precedence graph (no cycle = ✅) |

---

## Transaction Control SQL Statements

```sql
-- Start a transaction
BEGIN TRANSACTION;

-- Save work permanently
COMMIT;

-- Undo all changes since BEGIN
ROLLBACK;

-- Create a checkpoint within the transaction
SAVEPOINT sp1;

-- Rollback to a specific savepoint (partial undo)
ROLLBACK TO sp1;
```

### Example

```sql
BEGIN TRANSACTION;

UPDATE accounts SET balance = balance - 500 WHERE id = 'A';
SAVEPOINT after_debit;

UPDATE accounts SET balance = balance + 500 WHERE id = 'B';

-- Oops, something went wrong with credit
ROLLBACK TO after_debit;  -- only undoes the credit, keeps the debit

-- Fix and retry
UPDATE accounts SET balance = balance + 500 WHERE id = 'B';

COMMIT;  -- make everything permanent
```

```
  BEGIN
    │
    ├── UPDATE A (debit)
    │      │
    │   SAVEPOINT ──────────────────┐
    │      │                        │
    │   UPDATE B (credit) — ERROR!  │
    │      │                        │
    │   ROLLBACK TO SAVEPOINT ◄─────┘  (undo only credit)
    │      │
    │   UPDATE B (retry credit)
    │      │
    └── COMMIT ✅
```

---

## Quick Summary

```
  Transaction = Group of operations treated as ONE unit

  ACID:
    A = Atomicity     → All or Nothing
    C = Consistency   → Valid state → Valid state
    I = Isolation     → Concurrent txns don't interfere
    D = Durability    → Committed data survives crashes

  States:
    Active → Partially Committed → Committed ✅
    Active → Failed → Aborted (Restart/Kill) ❌

  Schedules:
    Serial        → One txn at a time (correct but slow)
    Concurrent    → Interleaved (fast but risky)
    Serializable  → Concurrent but equivalent to serial (best of both)

  Serializability:
    Conflict Serializable ⊂ View Serializable
    Test: Precedence Graph — no cycle = conflict serializable
```

> **Interview tip:** The most-asked transaction question is: "Explain ACID properties with an example." Use the bank transfer example — ₹500 from A to B. Show how each property prevents a specific problem: Atomicity prevents partial transfers, Consistency preserves total balance, Isolation prevents dirty reads, Durability preserves data after crashes.

---
---

# COMMIT, ROLLBACK & SAVEPOINT — In Detail

🔗 **Reference:** [StudyTonight — TCL Commands in DBMS](https://www.studytonight.com/dbms/tcl-command.php)

These three TCL (Transaction Control Language) commands control the lifecycle of a transaction.

---

## 1. COMMIT

**Makes all changes permanent.** Once committed, the changes cannot be undone by `ROLLBACK`. The data is written to disk and survives crashes.

```sql
COMMIT;
```

### Example — Bank Transfer

```sql
BEGIN TRANSACTION;

UPDATE accounts SET balance = balance - 500 WHERE name = 'Alice';  -- Debit
UPDATE accounts SET balance = balance + 500 WHERE name = 'Bob';    -- Credit

COMMIT;   -- Both changes are now PERMANENT
```

**Account balances at each step:**

| Step | Operation | Alice | Bob | Status |
|:---:|-----------|:---:|:---:|:---:|
| 0 | Before transaction | 1000 | 2000 | Saved on disk |
| 1 | Debit Alice | **500** | 2000 | In memory only |
| 2 | Credit Bob | 500 | **2500** | In memory only |
| 3 | **COMMIT** | 500 | 2500 | ✅ **Saved to disk permanently** |

```
  Before COMMIT:
  ┌──────────────────┐     ┌──────────────────┐
  │   Memory (RAM)   │     │   Disk           │
  │ Alice = 500      │     │ Alice = 1000     │ ← still old values!
  │ Bob = 2500       │     │ Bob = 2000       │
  └──────────────────┘     └──────────────────┘

  After COMMIT:
  ┌──────────────────┐     ┌──────────────────┐
  │   Memory (RAM)   │     │   Disk           │
  │ Alice = 500      │ ──► │ Alice = 500      │ ← updated!
  │ Bob = 2500       │     │ Bob = 2500       │ ← updated!
  └──────────────────┘     └──────────────────┘
```

> **After COMMIT:** Changes are permanent. Even if the system crashes right after, the data is safe.

---

## 2. ROLLBACK

**Undoes all changes** made since the `BEGIN TRANSACTION` (or since the last `COMMIT`). The database reverts to its previous consistent state.

```sql
ROLLBACK;
```

### Example — Failed Transfer

```sql
BEGIN TRANSACTION;

UPDATE accounts SET balance = balance - 500 WHERE name = 'Alice';  -- Debit ✅
-- Oops! Bob's account is frozen, credit fails
UPDATE accounts SET balance = balance + 500 WHERE name = 'Bob';    -- ERROR! ❌

ROLLBACK;   -- Undo EVERYTHING — Alice gets her ₹500 back
```

**Account balances at each step:**

| Step | Operation | Alice | Bob | Status |
|:---:|-----------|:---:|:---:|:---:|
| 0 | Before transaction | 1000 | 2000 | Saved on disk |
| 1 | Debit Alice | **500** | 2000 | In memory |
| 2 | Credit Bob | 500 | ❌ ERROR | Bob's account frozen |
| 3 | **ROLLBACK** | **1000** | **2000** | ✅ **Reverted to original** |

```
  After ERROR:                       After ROLLBACK:
  ┌──────────────────┐              ┌──────────────────┐
  │   Memory (RAM)   │              │   Memory (RAM)   │
  │ Alice = 500  ⚠️  │    ──────►  │ Alice = 1000 ✅  │
  │ Bob = ERROR      │   ROLLBACK  │ Bob = 2000   ✅  │
  └──────────────────┘              └──────────────────┘
  Money seems lost!                  Money restored!
```

> **Without ROLLBACK:** Alice loses ₹500 but Bob never receives it — money vanishes!
> **With ROLLBACK:** Alice's debit is undone — everything goes back to the original state.

---

## 3. SAVEPOINT

Creates a **checkpoint** within a transaction. You can `ROLLBACK TO` a savepoint to undo only the changes made **after** that savepoint, while keeping earlier changes intact.

```sql
SAVEPOINT savepoint_name;              -- Create checkpoint
ROLLBACK TO savepoint_name;            -- Undo to checkpoint
RELEASE SAVEPOINT savepoint_name;      -- Delete checkpoint (optional)
```

### Example — Partial Rollback

```sql
BEGIN TRANSACTION;

-- Step 1: Transfer from Alice to Bob
UPDATE accounts SET balance = balance - 500 WHERE name = 'Alice';
UPDATE accounts SET balance = balance + 500 WHERE name = 'Bob';

SAVEPOINT transfer_done;   -- ← Checkpoint: Alice→Bob is safe

-- Step 2: Transfer from Bob to Carol (this fails)
UPDATE accounts SET balance = balance - 200 WHERE name = 'Bob';
UPDATE accounts SET balance = balance + 200 WHERE name = 'Carol';   -- ERROR!

ROLLBACK TO transfer_done;  -- ← Undo only Step 2, keep Step 1

COMMIT;   -- Alice→Bob transfer is committed
```

**Account balances at each step:**

| Step | Operation | Alice | Bob | Carol | Savepoint? |
|:---:|-----------|:---:|:---:|:---:|:---:|
| 0 | Start | 1000 | 2000 | 500 | |
| 1 | Alice → Bob (debit) | **500** | 2000 | 500 | |
| 2 | Alice → Bob (credit) | 500 | **2500** | 500 | |
| 3 | **SAVEPOINT** | 500 | 2500 | 500 | ✅ `transfer_done` |
| 4 | Bob → Carol (debit) | 500 | **2300** | 500 | |
| 5 | Bob → Carol (credit) | 500 | 2300 | ❌ ERROR | |
| 6 | **ROLLBACK TO** | 500 | **2500** | **500** | Reverted to savepoint |
| 7 | **COMMIT** | 500 | 2500 | 500 | ✅ Permanent |

```
  Timeline:
  ─────────
  BEGIN ──── Step 1 ──── Step 2 ──── SAVEPOINT ──── Step 4 ──── Step 5 (ERROR!)
                                         │                         │
                                         │     ROLLBACK TO ◄───────┘
                                         │     (undo steps 4-5 only)
                                         │
                                      COMMIT ✅
                                      (steps 1-2 are permanent)
```

### Multiple Savepoints

You can create multiple savepoints within a single transaction:

```sql
BEGIN TRANSACTION;

INSERT INTO orders VALUES (1, 'Laptop', 50000);
SAVEPOINT sp1;

INSERT INTO orders VALUES (2, 'Mouse', 500);
SAVEPOINT sp2;

INSERT INTO orders VALUES (3, 'Keyboard', 1500);
SAVEPOINT sp3;

-- Oops, keyboard order was wrong
ROLLBACK TO sp2;   -- Undoes order #3 only

-- Mouse order was also wrong
ROLLBACK TO sp1;   -- Undoes order #2 as well

COMMIT;   -- Only order #1 (Laptop) is saved!
```

```
  sp1          sp2          sp3
   │            │            │
   ▼            ▼            ▼
  Laptop ──── Mouse ──── Keyboard
   ✅          ❌           ❌
              ▲             ▲
        ROLLBACK TO sp1  ROLLBACK TO sp2
        (undoes #2 & #3) (undoes #3 only)
```

---

## TCL Commands — Quick Reference

| Command | What It Does | Can Undo? |
|---------|-------------|:---:|
| `COMMIT` | Make all changes permanent | ❌ Cannot undo after commit |
| `ROLLBACK` | Undo ALL changes since BEGIN | ✅ Restores original state |
| `SAVEPOINT name` | Create a checkpoint | — |
| `ROLLBACK TO name` | Undo changes back to checkpoint | ✅ Partial undo |
| `RELEASE SAVEPOINT name` | Delete a savepoint | — |

---
---

# How Each ACID Property Is Achieved — Deep Dive

Each ACID property requires specific **mechanisms** in the DBMS to enforce it. Here's exactly how each one is implemented.

---

## 1. Atomicity — How It's Achieved

### Mechanism: **Transaction Manager + Undo Log (Rollback Log)**

The DBMS maintains an **undo log** (also called rollback log) that records the **old values** of every data item before it's modified. If the transaction fails, the undo log is used to restore everything.

```
  Transaction T: Transfer ₹500 from A to B

  Undo Log:                              Database:
  ┌────────────────────────────┐        ┌──────────┐
  │ (T, A, old_value = 1000)  │   ←──  │ A = 500  │  (modified)
  │ (T, B, old_value = 2000)  │   ←──  │ B = 2500 │  (modified)
  └────────────────────────────┘        └──────────┘

  If T fails:
  → Read undo log in REVERSE
  → Restore A = 1000, B = 2000
  → Transaction "never happened"
```

| Scenario | Action |
|----------|--------|
| Transaction succeeds | COMMIT → discard undo log entries |
| Transaction fails | ROLLBACK → apply undo log in reverse order |
| System crash during transaction | Recovery → apply undo log to undo partial changes |

### Shadow Copy Scheme (Simple Implementation)

🔗 **Reference:** [Ashutosh Tripathi — Implementation of Atomicity and Durability using Shadow Copy](https://ashutoshtripathi.com/2017/11/27/implementation-of-atomicity-and-durability-using-shadow-copy/)

For small databases, **shadow copy** provides atomicity + durability in one scheme:

```
  Before Transaction:
  ┌────────────────┐
  │  db-pointer    │────────────► Original DB (on disk)
  └────────────────┘              (shadow copy)

  During Transaction:
  ┌────────────────┐
  │  db-pointer    │────────────► Original DB (untouched)
  └────────────────┘
                                  New DB Copy (all updates go here)

  After COMMIT:
  ┌────────────────┐
  │  db-pointer    │────────────► New DB Copy (now current)
  └────────────────┘
                                  Old DB (deleted)

  After FAILURE:
  ┌────────────────┐
  │  db-pointer    │────────────► Original DB (still intact!)
  └────────────────┘
                                  New DB Copy (deleted)
```

**How it works:**

1. Before modifying anything, create a **complete copy** of the database
2. Apply all changes to the **new copy only** — original (shadow) is untouched
3. **On COMMIT:** Update `db-pointer` to point to the new copy → atomic switch
4. **On FAILURE:** Delete the new copy → original is still intact

> ⚠️ **Limitation:** Extremely inefficient for large databases (copies entire DB). Real systems use **Write-Ahead Logging (WAL)** instead.

---

## 2. Consistency — How It's Achieved

### Mechanism: **Application Logic + DBMS Constraints**

Consistency is a **shared responsibility** — partly the developer's job, partly the DBMS's job.

| Enforced By | How |
|------------|-----|
| **Application logic** | Developer writes correct transaction logic (e.g., debit + credit = 0) |
| **Integrity constraints** | PK, FK, UNIQUE, NOT NULL, CHECK constraints |
| **Triggers** | Auto-validate data on INSERT/UPDATE |
| **Domain constraints** | Data type checks (INT, VARCHAR, etc.) |

### Example

```sql
-- DBMS enforces these constraints automatically:
CREATE TABLE accounts (
    id      INT PRIMARY KEY,                          -- PK constraint
    name    VARCHAR(50) NOT NULL,                     -- NOT NULL constraint
    balance DECIMAL(10,2) CHECK (balance >= 0)        -- CHECK constraint
);

-- This transaction maintains consistency:
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 500 WHERE id = 1;  -- ₹500 deducted
UPDATE accounts SET balance = balance + 500 WHERE id = 2;  -- ₹500 added
-- Total balance unchanged → CONSISTENT ✅
COMMIT;

-- This would FAIL consistency:
UPDATE accounts SET balance = -100 WHERE id = 1;
-- ERROR: CHECK constraint violated (balance >= 0) ❌
```

```
  Consistency Check Flow:
  ───────────────────────
  Transaction starts
       │
  Execute operations
       │
  Check constraints ──── Violation? ──► ROLLBACK ❌
       │
  No violation
       │
  COMMIT ✅
```

---

## 3. Isolation — How It's Achieved

### Mechanism: **Concurrency Control (Locks, MVCC, Timestamps)**

Isolation is the most complex ACID property. Multiple mechanisms exist:

### Method 1: Locking (Lock-Based Protocols)

Transactions acquire **locks** on data items before accessing them:

| Lock Type | Allows | Blocks |
|:---:|---------|--------|
| **Shared Lock (S)** | Multiple readers | Writers |
| **Exclusive Lock (X)** | One writer | Everyone else |

```
  T1 wants to READ A → Acquires Shared Lock(A)
  T2 wants to READ A → Acquires Shared Lock(A) ✅ (multiple readers OK)
  T3 wants to WRITE A → Blocked! ❌ (must wait for T1 & T2 to release)

  T1 wants to WRITE A → Acquires Exclusive Lock(A)
  T2 wants to READ A → Blocked! ❌ (must wait for T1)
  T3 wants to WRITE A → Blocked! ❌ (must wait for T1)
```

**Lock Compatibility Matrix:**

| | Shared (S) | Exclusive (X) |
|--|:---:|:---:|
| **Shared (S)** | ✅ Compatible | ❌ Conflict |
| **Exclusive (X)** | ❌ Conflict | ❌ Conflict |

### Method 2: MVCC (Multi-Version Concurrency Control)

Instead of locking, the database keeps **multiple versions** of each row. Readers see a **snapshot** — they never block writers, and writers never block readers.

```
  MVCC Versions of Row A:
  ┌──────────────────────────────────────────────┐
  │ Version 1: A = 1000  (committed by T0)       │ ← T2 reads this
  │ Version 2: A = 500   (being written by T1)   │ ← not yet committed
  └──────────────────────────────────────────────┘

  T1 is modifying A → creates Version 2
  T2 wants to read A → reads Version 1 (last committed)
  T2 is NOT blocked! Both run concurrently ✅
```

> Used by: PostgreSQL, MySQL (InnoDB), Oracle

### Method 3: Timestamp Ordering

Each transaction gets a **timestamp** when it starts. Operations are allowed/rejected based on timestamp order.

---

## 4. Durability — How It's Achieved

### Mechanism: **Write-Ahead Logging (WAL) + Redo Log**

Before any change is applied to the database, a **log entry** is first written to a durable **log file on disk**. This ensures that even if the system crashes, the changes can be **replayed** from the log.

```
  WAL Rule: "Write the LOG before writing the DATA"

  Step 1: Write to LOG (on disk) ──── "T1: A changed from 1000 to 500"
  Step 2: Write to DATABASE         ──── A = 500

  If crash after Step 1 but before Step 2:
  → On restart, READ the log → REDO the change → A = 500 ✅

  If crash before Step 1:
  → No log entry → change was never applied → A remains 1000 ✅
```

```
  Normal Operation:
  ┌──────┐    ┌──────────┐    ┌───────────┐
  │ App  │───▶│ WAL Log  │───▶│ Database  │
  │      │    │ (disk)   │    │ (disk)    │
  └──────┘    └──────────┘    └───────────┘
               Write FIRST     Write SECOND

  After Crash + Recovery:
  ┌──────────┐    ┌───────────┐
  │ WAL Log  │───▶│ Database  │
  │ (disk)   │    │ (disk)    │
  └──────────┘    └───────────┘
  Read log         Replay (redo) committed changes
                   Undo uncommitted changes
```

### Redo vs Undo During Recovery

| Log Entry | Transaction Status | Recovery Action |
|-----------|:---:|:---:|
| Change logged, T committed | ✅ Committed | **REDO** — replay the change |
| Change logged, T not committed | ❌ Not committed | **UNDO** — reverse the change |
| Change not logged | — | Nothing to do (change never happened) |

---

## ACID — Who Is Responsible?

| Property | Responsibility | DBMS Component |
|:---:|:---:|:---:|
| **Atomicity** | DBMS | Transaction Manager + Undo Log |
| **Consistency** | Developer + DBMS | Application logic + Constraints |
| **Isolation** | DBMS | Concurrency Control Manager |
| **Durability** | DBMS | Recovery Manager + WAL |

---
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

---
---

# ❓ What Is Consistency and Integrity in DBMS?

These two terms are constantly used interchangeably — but they mean different things. The cleanest way to separate them:

> - **Integrity** = the **RULES** that define what "valid data" means.
> - **Consistency** = the **GUARANTEE** that the database never violates those rules.

**Analogy:** In chess, **integrity** is the rulebook (a bishop moves diagonally, a king can't move into check). **Consistency** is the promise that after *every* move, the board is still in a legal position.

```
      INTEGRITY (the rules)              CONSISTENCY (the guarantee)
   ┌───────────────────────────┐      ┌───────────────────────────────┐
   │ • PK must be unique/NOT   │      │  Valid State  ──[TXN]──▶  Valid State │
   │   NULL                    │      │                                │
   │ • FK must reference an    │ ───▶ │  Every transaction takes the   │
   │   existing PK             │      │  DB from one rule-obeying      │
   │ • age BETWEEN 0 AND 150   │      │  state to another — never      │
   │ • balance >= 0            │      │  leaving it half-broken.       │
   └───────────────────────────┘      └───────────────────────────────┘
      Static — a property of DATA        Dynamic — a property of TRANSACTIONS
```

---

## Integrity — The Rules

**Integrity** means the data in the database is **accurate, valid, and trustworthy**. It's enforced through **integrity constraints** — rules you declare at schema-design time.

### The Four Types of Integrity Constraints

| Type | Rule | Enforced By | Example |
|---|---|---|---|
| **Entity Integrity** | Every row must be uniquely identifiable — the primary key can never be `NULL` or duplicated | `PRIMARY KEY` | `emp_id` cannot be NULL |
| **Referential Integrity** | A foreign key must match an existing primary key in the parent table, or be `NULL` | `FOREIGN KEY` | `employees.dept_id` must exist in `departments` |
| **Domain Integrity** | Every value must belong to the column's allowed set of values | Data type, `NOT NULL`, `CHECK`, `DEFAULT` | `age INT CHECK (age BETWEEN 18 AND 65)` |
| **User-Defined (Business) Integrity** | Custom business rules that don't fit the above | `CHECK`, triggers, application code | "A savings account balance can never go below ₹500" |

```sql
CREATE TABLE employees (
    emp_id   INT PRIMARY KEY,                              -- Entity Integrity
    name     VARCHAR(50) NOT NULL,                         -- Domain Integrity
    age      INT CHECK (age BETWEEN 18 AND 65),            -- Domain Integrity
    salary   DECIMAL(10,2) CHECK (salary > 0),             -- Domain Integrity
    dept_id  INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)  -- Referential Integrity
);
```

> **Key point:** Integrity is about the **data at rest**. At any given moment, you can inspect the database and ask: "does every row obey every rule?" If yes → integrity holds.

---

## Consistency — The Guarantee

**Consistency** (the **C** in ACID) means a transaction takes the database from **one valid state to another valid state**. It never leaves the database in a half-finished, rule-violating state.

### Example — Bank Transfer

The business rule (an integrity constraint): **the total money in the system must never change during a transfer.**

```
BEFORE:  Alice = ₹1000   Bob = ₹500   ──▶  TOTAL = ₹1500  ✅ valid state

BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 200 WHERE name = 'Alice';
    ─────────────────────────────────────────────────────────────────
    ⚠️ INTERMEDIATE STATE:  Alice = ₹800   Bob = ₹500  →  TOTAL = ₹1300
       Money vanished! This state is INVALID — but it's invisible to
       everyone else (that's Isolation's job to hide it).
    ─────────────────────────────────────────────────────────────────
    UPDATE accounts SET balance = balance + 200 WHERE name = 'Bob';
COMMIT;

AFTER:   Alice = ₹800    Bob = ₹700   ──▶  TOTAL = ₹1500  ✅ valid state
```

Consistency guarantees that **no observer ever sees the ₹1300 state as a committed reality** — the transaction either completes fully (₹1500 preserved) or rolls back entirely (₹1500 preserved).

> **Note the dependency:** Consistency isn't achieved alone — it rides on the other three ACID properties. **Atomicity** prevents half-done transactions, **Isolation** hides intermediate states from other transactions, and **Durability** ensures the valid final state survives a crash.

---

## Side-by-Side Comparison

| Aspect | Integrity | Consistency |
|---|---|---|
| **What it is** | The **rules** defining valid data | The **guarantee** those rules are never violated |
| **Nature** | Static — a property of the stored **data** | Dynamic — a property of **transactions** |
| **Scope** | Individual rows, columns, and relationships | The database as a whole, across a transaction |
| **When checked** | On every `INSERT` / `UPDATE` / `DELETE` | At transaction boundaries (commit) |
| **Enforced by** | `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, `NOT NULL`, `UNIQUE` | The transaction manager + all constraints + app logic |
| **Who's responsible** | Database (once you declare the constraints) | **Shared** — DBMS enforces constraints, developer writes correct transaction logic |
| **Failure looks like** | An orphan row, a NULL primary key, `age = -5` | Money disappearing mid-transfer, a booked seat with no booking record |
| **Relationship** | Integrity defines *what* valid means | Consistency ensures every transaction *preserves* it |

> **The link between them:** Consistency is enforced **by** integrity constraints. If a transaction would leave the database violating any integrity constraint, the DBMS aborts and rolls it back — that rollback *is* consistency in action.

---

## ⚠️ Gotcha — "Consistency" in ACID ≠ "Consistency" in CAP

This trips up almost everyone in system design interviews. Same word, completely different meanings:

| | **C** in **ACID** | **C** in **CAP** |
|---|---|---|
| **Means** | The database obeys all defined rules/constraints | All nodes return the same data at the same time |
| **Context** | Single-node transactions | Distributed systems / replication |
| **Concerned with** | Data **validity** | Data **freshness across replicas** |
| **Violated when** | A constraint is broken (orphan FK, negative balance) | A read hits a stale replica and returns old data |
| **Also called** | Correctness | Linearizability / Strong consistency |

```
  ACID Consistency:                    CAP Consistency:
  ─────────────────                    ────────────────
  Is the data VALID?                   Is the data the SAME everywhere?

  balance = -500  ❌                   Node A: balance = 800  ┐
  (violates CHECK balance >= 0)        Node B: balance = 1000 ┘ ❌ mismatch
```

---

## Summary

| Question | Answer |
|---|---|
| What is **integrity**? | The correctness and validity of data, enforced by constraints (Entity, Referential, Domain, User-defined) |
| What is **consistency**? | The guarantee that every transaction moves the DB from one valid state to another, never breaking any rule |
| How are they related? | Integrity defines the rules; consistency enforces them across transactions |
| Which ACID property is *partly the developer's job*? | **Consistency** — the DBMS enforces declared constraints, but you must write transaction logic that actually preserves business rules |

> **Interview tip:** "Integrity is the *what* — the rules that define valid data, like a foreign key needing to reference a real row. Consistency is the *guarantee* that a transaction never leaves the database in a state where those rules are broken. And I'd flag that ACID consistency (data validity) is a completely different concept from CAP consistency (all replicas agreeing) — the shared name is purely coincidental."

---
---

# Concurrency Problems (Without Proper Isolation)

🔗 **Reference:** [GeeksforGeeks — Concurrency Problems in DBMS Transactions](https://www.geeksforgeeks.org/dbms/concurrency-problems-in-dbms-transactions/)

When multiple transactions run concurrently WITHOUT proper isolation, these problems can occur:

**The four problems, by conflict type** (the naming used in most textbooks and interviews):

| Problem | Conflict type | What happens |
|---|:---:|---|
| **Dirty Read** (temporary update) | **W-R** | T2 reads data that T1 wrote but never committed |
| **Lost Update** | **W-W** | T1's write is silently overwritten by T2 |
| **Unrepeatable Read** | **R-W** | T1 reads the same row twice and gets different values |
| **Incorrect Summary / Phantom Read** | **R-W** | An aggregate reads a set while another transaction inserts/deletes rows in it |

**Why we allow concurrency at all** — the trade-off these problems buy us:

| Advantage | Why |
|---|---|
| **Reduced waiting time** | A short transaction isn't stuck behind a long one |
| **High throughput** | More transactions complete per second |
| **High resource utilization** | While one transaction waits on disk I/O, another uses the CPU |

> The job of **isolation levels** and **concurrency control protocols** is to keep these advantages while eliminating the problems above.

---

## 1. Dirty Read (Reading Uncommitted Data)

Transaction T2 reads a value that T1 has modified but **NOT YET COMMITTED**. If T1 later rolls back, T2 has read data that never existed.

```
  T1                              T2
  ──                              ──
  Read(A) = 1000
  A = A - 500
  Write(A) = 500
                                  Read(A) = 500   ← DIRTY READ! (T1 not committed)
  ROLLBACK ❌
  (A goes back to 1000)
                                  T2 uses A = 500  ← WRONG! A is actually 1000
```

| Time | T1 | T2 | A (actual) | Problem |
|:---:|---|---|:---:|:---:|
| 1 | Write(A) = 500 | | 500 (uncommitted) | |
| 2 | | Read(A) = 500 | 500 | **Dirty Read!** |
| 3 | ROLLBACK | | 1000 | T2 has stale data |

---

## 2. Lost Update

Two transactions read the same value and update it independently. The **second write overwrites the first**, losing T1's update.

```
  T1                              T2
  ──                              ──
  Read(A) = 1000
                                  Read(A) = 1000
  A = A - 500
  Write(A) = 500
                                  A = A - 200
                                  Write(A) = 800  ← Overwrites T1's change!
```

| Time | T1 | T2 | A | Problem |
|:---:|---|---|:---:|:---:|
| 1 | Read(A) = 1000 | | 1000 | |
| 2 | | Read(A) = 1000 | 1000 | |
| 3 | Write(A) = 500 | | 500 | |
| 4 | | Write(A) = 800 | 800 | **Lost Update!** T1's ₹500 deduction is lost |

> Expected: A = 1000 - 500 - 200 = **300**. Got: A = **800**. ₹500 lost!

---

## 3. Non-Repeatable Read

T1 reads the same data item **twice**, but gets **different values** because T2 modified it in between.

```
  T1                              T2
  ──                              ──
  Read(A) = 1000   ← First read
                                  Write(A) = 500
                                  COMMIT
  Read(A) = 500    ← Second read — different value!
```

---

## 4. Phantom Read

T1 reads a set of rows that satisfy a condition. T2 **inserts/deletes** rows. T1 re-reads and gets a **different number of rows**.

```
  T1                                    T2
  ──                                    ──
  SELECT COUNT(*) WHERE dept='CSE'
  → Returns 3 students

                                        INSERT ('Dave', 'CSE')
                                        COMMIT

  SELECT COUNT(*) WHERE dept='CSE'
  → Returns 4 students   ← PHANTOM! A new row "appeared"
```

---

## SQL Isolation Levels

SQL defines **4 isolation levels** that control which concurrency problems are allowed:

| Isolation Level | Dirty Read | Lost Update | Non-Repeatable Read | Phantom Read |
|---|:---:|:---:|:---:|:---:|
| **READ UNCOMMITTED** | ⚠️ Possible | ⚠️ Possible | ⚠️ Possible | ⚠️ Possible |
| **READ COMMITTED** | ✅ Prevented | ⚠️ Possible | ⚠️ Possible | ⚠️ Possible |
| **REPEATABLE READ** | ✅ Prevented | ✅ Prevented | ✅ Prevented | ⚠️ Possible |
| **SERIALIZABLE** | ✅ Prevented | ✅ Prevented | ✅ Prevented | ✅ Prevented |

```
  Isolation Level Spectrum:
  ──────────────────────────────────────────────────────────────►
  READ UNCOMMITTED    READ COMMITTED    REPEATABLE READ    SERIALIZABLE
  (fastest,           (default in       (default in        (slowest,
   least safe)         Oracle/SQL Srvr)  MySQL/PostgreSQL)   safest)

  ◄── More performance                           More safety ──►
  ◄── Less isolation                        More isolation ──►
```

### Setting Isolation Level

```sql
-- Set for current session
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Set for current transaction only
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;
-- ... operations ...
COMMIT;
```

### Which Level to Use?

| Use Case | Recommended Level |
|----------|:---:|
| Analytics / reporting (read-only, stale data OK) | READ COMMITTED |
| Most web applications | READ COMMITTED or REPEATABLE READ |
| Banking / financial transactions | SERIALIZABLE |
| High-traffic reads, eventual consistency OK | READ UNCOMMITTED (rarely) |

> **Interview tip:** "What isolation level does your database use by default?" — MySQL (InnoDB) defaults to **REPEATABLE READ**. PostgreSQL defaults to **READ COMMITTED**. Oracle defaults to **READ COMMITTED**. SQL Server defaults to **READ COMMITTED**.

---
---

# Concurrency Control in DBMS

🔗 **Reference:** [Tutorialspoint — DBMS Concurrency Control](https://www.tutorialspoint.com/dbms/dbms_concurrency_control.htm)

Concurrency control is the mechanism that allows **multiple transactions to execute simultaneously** while still maintaining the ACID properties. Without it, concurrent transactions can corrupt data, produce wrong results, and leave the database in an inconsistent state.

> **Why not just run transactions one at a time?** Serial execution is correct but extremely slow. In a banking system handling thousands of transactions per second, serial execution would mean each user has to wait for ALL previous users to finish. Concurrency control lets us run transactions in parallel **safely**.

---

## All 5 Concurrency Problems

We covered Dirty Read, Lost Update, Non-Repeatable Read, and Phantom Read in the previous section. Here's the complete list with the **Incorrect Summary Problem** added:

### 1. Dirty Read (Temporary Update Problem)

T2 reads a value that T1 modified but **hasn't committed yet**. If T1 rolls back, T2 has used a value that never actually existed.

```
  T1                              T2
  ──                              ──
  Read(X) = 100
  X = X - 50
  Write(X) = 50
                                  Read(X) = 50  ← Dirty Read!
  ROLLBACK ❌
  X reverts to 100
                                  Uses X = 50   ← WRONG! X is actually 100
```

### 2. Lost Update Problem

Two transactions read the same value and update it. The **last write overwrites** the first, losing T1's change.

```
  T1                              T2
  ──                              ──
  Read(X) = 100
                                  Read(X) = 100
  X = X - 30
  Write(X) = 70                   X = X + 50
                                  Write(X) = 150  ← T1's deduction (70) is LOST!
```

> Expected final X = 100 - 30 + 50 = **120**. Got X = **150**. T1's -30 vanished!

### 3. Incorrect Summary Problem (NEW)

One transaction is computing an **aggregate** (SUM, COUNT, AVG) while another transaction is **modifying** the same records. The aggregate mixes old and new values.

```
  Accounts:  A = 100,  B = 200,  C = 300    (Total should be 600)

  T1 (updating)                    T2 (summing)
  ──                               ──
                                   Sum = 0
                                   Read(A) = 100    Sum = 100
  Read(A) = 100
  A = A - 50
  Write(A) = 50
  Read(B) = 200
  B = B + 50
  Write(B) = 250
                                   Read(B) = 250    Sum = 350  ← new value!
                                   Read(C) = 300    Sum = 650  ← WRONG!
```

| Account | Before T1 | After T1 | Read By T2 |
|:---:|:---:|:---:|:---:|
| A | 100 | 50 | 100 (old ✅) |
| B | 200 | 250 | **250 (new ❌)** |
| C | 300 | 300 | 300 |
| **Sum** | **600** | **600** | **650 ❌** |

> T2 read A's old value (100) but B's new value (250). The sum (650) is **wrong** — the correct total is 600.

### 4. Non-Repeatable Read Problem

T1 reads the same variable **twice** and gets **different values** because T2 modified it between the two reads.

```
  T1                              T2
  ──                              ──
  Read(X) = 100  ← First read
                                  X = X + 50
                                  Write(X) = 150
                                  COMMIT
  Read(X) = 150  ← Second read — different!
```

### 5. Phantom Read Problem

T1 queries rows matching a condition. T2 **inserts or deletes** rows. T1 re-queries and gets a **different set of rows**.

```
  T1                                    T2
  ──                                    ──
  SELECT * WHERE salary > 50000
  → Returns {Alice, Bob}
                                        INSERT (Carol, 60000)
                                        COMMIT
  SELECT * WHERE salary > 50000
  → Returns {Alice, Bob, Carol}  ← Phantom row appeared!
```

---

## Concurrency Control Protocols

```
                  ┌──────────────────────────┐
                  │ Concurrency Control      │
                  │ Protocols                │
                  └────────────┬─────────────┘
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
     ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
     │  Lock-Based  │  │  Timestamp-  │  │    Optimistic    │
     │  Protocols   │  │  Based       │  │    Concurrency   │
     └──────┬───────┘  └──────────────┘  │    Control       │
            │                            └──────────────────┘
     ┌──────┴──────┐
     │ Two-Phase   │
     │ Locking(2PL)│
     └─────────────┘
```

---

## 1. Lock-Based Concurrency Control

Transactions must acquire a **lock** on a data item before accessing it. The lock prevents other transactions from interfering.

### Lock Types

| Lock | Symbol | Allows | Usage |
|:---:|:---:|---------|-------|
| **Shared Lock** (read lock) | S | Multiple readers simultaneously | `SELECT` (read) |
| **Exclusive Lock** (write lock) | X | Only one writer, blocks everyone | `UPDATE`, `DELETE` (write) |
| **Binary Lock** | — | Only two states: **locked** or **unlocked** — no distinction between read and write | Theoretical/simplest model; too restrictive in practice because it blocks concurrent readers |

### Lock Compatibility Matrix

| Request ↓ / Held → | No Lock | Shared (S) | Exclusive (X) |
|:---:|:---:|:---:|:---:|
| **Shared (S)** | ✅ Grant | ✅ Grant | ❌ Wait |
| **Exclusive (X)** | ✅ Grant | ❌ Wait | ❌ Wait |

```
  Scenario 1: Multiple Readers (OK)
  T1: S-Lock(A) ✅
  T2: S-Lock(A) ✅    Both can read simultaneously
  T3: S-Lock(A) ✅

  Scenario 2: Reader + Writer (BLOCKED)
  T1: S-Lock(A) ✅
  T2: X-Lock(A) ❌ WAIT   T2 must wait for T1 to release

  Scenario 3: Writer + Writer (BLOCKED)
  T1: X-Lock(A) ✅
  T2: X-Lock(A) ❌ WAIT   Only one writer at a time
```

### Lock Upgrading & Downgrading

```
  Upgrade:   S-Lock → X-Lock   (reader wants to write)
  Downgrade: X-Lock → S-Lock   (writer done, allows readers)
```

---

## 2. Two-Phase Locking (2PL)

The most widely used protocol. A transaction has **two phases**:

1. **Growing Phase** — can acquire locks, **cannot release** any
2. **Shrinking Phase** — can release locks, **cannot acquire** any

```
  Number of Locks
       │
       │        ┌──── Lock Point (maximum locks)
       │       ╱│╲
       │      ╱ │ ╲
       │     ╱  │  ╲
       │    ╱   │   ╲
       │   ╱    │    ╲
       │  ╱     │     ╲
       │ ╱      │      ╲
       │╱       │       ╲
  ─────┼────────┼────────╲──────► Time
       │ Growing│Shrinking
       │  Phase │  Phase
       │(acquire│(release
       │ locks) │ locks)
```

### Example

```
  T1 (Two-Phase Locking):
  ────────────────────────
  Growing Phase:
    S-Lock(A)        ✅ acquire
    S-Lock(B)        ✅ acquire
    Upgrade to X-Lock(A)  ✅ acquire
    ──── Lock Point ────
  Shrinking Phase:
    Unlock(B)        ✅ release
    Unlock(A)        ✅ release

  INVALID (violates 2PL):
    S-Lock(A)        ✅ acquire
    Unlock(A)        ✅ release
    S-Lock(B)        ❌ CANNOT acquire after releasing!
```

### Guarantees

> **2PL guarantees conflict serializability** — if all transactions follow 2PL, the resulting schedule is always equivalent to some serial schedule.

### Variants of 2PL

| Variant | Rule | Prevents |
|---------|------|----------|
| **Basic 2PL** | Growing then shrinking | Conflict serializability |
| **Strict 2PL** | Hold ALL exclusive (X) locks until COMMIT/ABORT | Cascading rollbacks + serializability |
| **Rigorous 2PL** | Hold ALL locks (S and X) until COMMIT/ABORT | Cascading rollbacks + strictest serializability |
| **Conservative 2PL** (Pre-Claiming) | Acquire **ALL** locks **before** the transaction starts; if any is unavailable, acquire none and wait | **Deadlocks** (no hold-and-wait) — but poor concurrency |

> **Conservative 2PL is the only deadlock-free variant** — it breaks the *hold and wait* condition by claiming every lock up front. The cost is that locks are held for the entire transaction even if a row is only touched at the very end, and you must know all the locks in advance (often impossible). See [Pre-Claiming Lock Protocol](#2-pre-claiming-lock-protocol) for the same idea in the lock-protocol taxonomy.

```
  Basic 2PL:
  ──────────
  Acquire → → → Lock Point → → → Release → → → COMMIT
                                    ↑
                            (can release before commit)

  Strict 2PL:
  ────────────
  Acquire → → → Lock Point → → → → → → → COMMIT → Release X-Locks
                                            ↑
                              (X-locks held until commit)

  Rigorous 2PL:
  ──────────────
  Acquire → → → Lock Point → → → → → → → COMMIT → Release ALL Locks
                                            ↑
                              (ALL locks held until commit)
```

---

## 3. Timestamp-Based Concurrency Control

Each transaction gets a **unique timestamp** when it starts. The DBMS ensures transactions execute in **timestamp order** — older transactions have priority.

### Each data item X stores:

| Timestamp | Meaning |
|-----------|---------|
| `W-TS(X)` | Timestamp of the **last transaction that wrote** X |
| `R-TS(X)` | Timestamp of the **last transaction that read** X |

### Rules

**Read Operation by Ti:**
```
  If TS(Ti) < W-TS(X):
    → Ti is trying to read a value written by a LATER transaction
    → REJECT (rollback Ti and restart with new timestamp)

  If TS(Ti) >= W-TS(X):
    → ALLOW the read
    → Update R-TS(X) = max(R-TS(X), TS(Ti))
```

**Write Operation by Ti:**
```
  If TS(Ti) < R-TS(X):
    → A LATER transaction already read the old value of X
    → Ti's write would invalidate that read
    → REJECT (rollback Ti)

  If TS(Ti) < W-TS(X):
    → A LATER transaction already wrote X
    → Ti's write is outdated
    → REJECT (rollback Ti)

  Otherwise:
    → ALLOW the write
    → Update W-TS(X) = TS(Ti)
```

### Example

```
  T1 (TS=1)    T2 (TS=2)         W-TS(X)   R-TS(X)
  ──────────   ──────────         ───────   ───────
                                    0         0
  Read(X)                           0         1       ✅ (TS(T1)=1 >= W-TS=0)
                Read(X)             0         2       ✅ (TS(T2)=2 >= W-TS=0)
  Write(X)                          ?         ?       ❌ REJECT!
                                                     (TS(T1)=1 < R-TS=2)
                                                     T2 already read old X
```

> **Advantage:** No locks → no deadlocks. **Disadvantage:** More rollbacks if conflicts are frequent.

---

## 4. Optimistic Concurrency Control (Validation-Based)

Assumes conflicts are **rare**. Transactions execute freely without any locks or checks. Only at the **end** (validation phase), the system checks if any conflict occurred.

### Three Phases

```
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │   Read       │───▶│   Validate   │───▶│   Write      │
  │   Phase      │    │   Phase      │    │   Phase      │
  │              │    │              │    │              │
  │ Execute all  │    │ Check for    │    │ Apply changes│
  │ operations   │    │ conflicts    │    │ to database  │
  │ on local     │    │              │    │              │
  │ copies       │    │ Conflict? ──►│    │              │
  └──────────────┘    │ YES: Abort   │    └──────────────┘
                      │ NO: Proceed  │
                      └──────────────┘
```

| Phase | What Happens |
|:---:|-------------|
| **Read Phase** | Reads from DB, all writes go to a **local buffer** (not the actual DB) |
| **Validation Phase** | Check if any other transaction modified the same data → conflict? |
| **Write Phase** | If validation passes, apply local changes to the database |

> **Best for:** Systems where reads dominate and write conflicts are rare (e.g., read-heavy web apps).

---

## Deadlocks

🔗 **References:** [GeeksforGeeks — Deadlock in DBMS](https://www.geeksforgeeks.org/deadlock-in-dbms/) · [Timestamp & Deadlock Prevention Schemes](https://www.geeksforgeeks.org/introduction-to-timestamp-and-deadlock-prevention-schemes-in-dbms/) · [Starvation in DBMS](https://www.geeksforgeeks.org/starvation-in-dbms/) · [Recovery from Deadlock](https://www.geeksforgeeks.org/recovery-from-deadlock-in-operating-system/)

A **deadlock** occurs when two or more transactions are **waiting for each other** to release locks, creating a circular wait. None can proceed.

```
  T1: X-Lock(A) ✅
  T2: X-Lock(B) ✅
  T1: X-Lock(B) ❌ WAIT (T2 holds B)
  T2: X-Lock(A) ❌ WAIT (T1 holds A)

  T1 waits for T2 → T2 waits for T1 → DEADLOCK! 💀

  ┌─────────────────────────────┐
  │         DEADLOCK            │
  │                             │
  │   T1 ──(waiting for B)──►  │
  │   ▲                     T2 │
  │   └──(waiting for A)────┘  │
  └─────────────────────────────┘
```

### The 4 Necessary Conditions

A deadlock can occur **only if all four hold simultaneously**. Break any one and deadlock becomes impossible — that's exactly what prevention schemes do.

| Condition | Meaning | In DBMS terms |
|---|---|---|
| **1. Mutual Exclusion** | A resource can be held by only one transaction at a time | An exclusive (X) lock on a row can't be shared |
| **2. Hold and Wait** | A transaction holding a resource requests another one and waits | T1 holds `X-Lock(A)` and waits for `X-Lock(B)` |
| **3. No Preemption** | A resource can't be forcibly taken; it must be released voluntarily | The DBMS won't yank T1's lock away mid-transaction |
| **4. Circular Wait** | A closed chain of transactions each waiting on the next | T1 → T2 → T3 → T1 |

```
  Break the condition ──► deadlock prevented

  Mutual Exclusion  → use shared (S) locks where possible / MVCC (readers don't block)
  Hold and Wait     → Pre-Claiming / Conservative 2PL (grab ALL locks up front)
  No Preemption     → Wound-Wait (the older transaction preempts the younger)
  Circular Wait     → order resources; always lock A before B
```

---

### Handling Deadlocks — Three Strategies

| Strategy | How It Works | When to use |
|---|---|---|
| **Prevention** | Rules make a deadlock structurally impossible (Wait-Die, Wound-Wait, Conservative 2PL, resource ordering) | High-contention systems where rollbacks are cheap |
| **Detection & Recovery** | Let deadlocks happen, detect them with a wait-for graph, then abort a victim | The common choice in real databases (MySQL, PostgreSQL) |
| **Timeout (avoidance)** | If a transaction waits longer than a threshold, assume deadlock and roll it back | Simple, no graph needed — but may kill innocent slow transactions |

---

### Deadlock Detection — The Wait-For Graph (WFG)

1. Create a **node** for every active transaction.
2. Draw an edge `Ti → Tj` if **Ti is waiting for a lock held by Tj**.
3. **A cycle in the graph = a deadlock.**
4. Run the check periodically, or on every lock-wait event.

```
  T1 holds A, wants B          Wait-For Graph:
  T2 holds B, wants C
  T3 holds C, wants A               T1 ──► T2
                                    ▲       │
                                    │       ▼
                                    └────── T3

  Cycle T1 → T2 → T3 → T1  →  💀 DEADLOCK
```

> **How often to check?** Too frequent = CPU overhead. Too rare = transactions sit blocked longer. Real databases (e.g. InnoDB) check on lock-wait, and also have an overall `innodb_lock_wait_timeout` as a backstop.

---

### Prevention Schemes (Timestamp-Based)

Each transaction gets a **timestamp** at start — a smaller timestamp means **older**. The scheme then decides who waits and who dies.

| Scheme | Rule | Action | Preemptive? |
|:---:|---|---|:---:|
| **Wait-Die** | Older **waits**, younger **dies** | If Ti is older than Tj → Ti waits. If Ti is younger → Ti is rolled back (dies) and restarts with the **same** timestamp | ❌ Non-preemptive |
| **Wound-Wait** | Older **wounds**, younger **waits** | If Ti is older than Tj → Tj is rolled back (wounded). If Ti is younger → Ti waits | ✅ Preemptive |
| **Timeout-Based** | Wait only up to a limit | If the wait exceeds the threshold → roll the waiter back. No timestamps or graph needed | ✅ Preemptive |

```
  Wait-Die (older waits, younger dies):
  ──────────────────────────────────────
  T1 (old) requests lock held by T2 (young)  → T1 WAITS (old can wait)
  T2 (young) requests lock held by T1 (old)  → T2 DIES (young must rollback)

  Wound-Wait (older wounds, younger waits):
  ──────────────────────────────────────────
  T1 (old) requests lock held by T2 (young)  → T2 is WOUNDED (rolled back)
  T2 (young) requests lock held by T1 (old)  → T2 WAITS (young can wait)
```

| | Wait-Die | Wound-Wait |
|---|---|---|
| Who rolls back | Always the **younger** requester | The **younger holder** gets preempted |
| Number of rollbacks | More (a young transaction may die repeatedly) | Fewer |
| Waiting time | Longer waits for old transactions | Shorter waits |
| Starvation risk | Higher — restart keeps the same timestamp, so it eventually becomes the oldest and survives | Lower |

> **Why restart with the same timestamp?** Because it guarantees the transaction eventually becomes the oldest in the system, so it can no longer be the one chosen to die — this is what prevents indefinite starvation.

---

### Deadlock Recovery

Once detected, the DBMS must break the cycle by aborting something.

**1. Selection of a Victim**

Pick the transaction whose rollback is **cheapest**:

| Factor | Prefer to abort the transaction that… |
|---|---|
| Work done so far | Has executed the **fewest** operations |
| Data touched | Holds the **fewest** locks / has written the least |
| Remaining work | Is **furthest** from completing |
| Rollback count | Has been rolled back the **fewest** times (starvation guard) |
| Transaction age | Is the **youngest** (least invested) |

**2. Rollback — How Far Back?**

| Type | What happens | Trade-off |
|---|---|---|
| **Total rollback** | Abort the victim completely and restart it from the beginning | Simple; wastes all the work done |
| **Partial rollback** | Roll back only to the point where the offending lock was requested (needs savepoints / a detailed log) | Saves work; complex bookkeeping |

**3. Starvation Avoidance**

If victim selection always picks the same transaction, that transaction may **never** finish. Guard against it by including the **rollback count in the cost function** — each time a transaction is victimized, its cost of being chosen again goes up, so eventually it is allowed to complete.

---

### Starvation (Livelock)

**Starvation** is when a transaction waits indefinitely while others keep progressing. Unlike deadlock, nothing is *stuck in a cycle* — the victim is simply always passed over.

| Cause | Explanation |
|---|---|
| **Bad victim-selection policy** | The same transaction is repeatedly chosen as the deadlock victim |
| **Unfair lock granting** | A queue that lets newly-arriving readers keep acquiring an S-lock, so a waiting X-lock writer never gets its turn |
| **Priority-based scheduling** | Low-priority transactions are perpetually overtaken by high-priority ones |
| **Resource never released** | A long-running transaction holds a lock for an extended period |

| | Deadlock | Starvation |
|---|---|---|
| What's happening | Circular wait — **nobody** progresses | **Others** progress; one transaction never does |
| Detection | Cycle in the wait-for graph | Watch wait time / rollback counters |
| Fix | Abort a victim to break the cycle | Aging / priority boost / fair FIFO lock queue / rollback-count in cost |

**Solutions:** FIFO lock queues (first-requested, first-granted), **aging** (a transaction's priority rises the longer it waits), capping rollback counts, and setting an upper bound on transaction lifetime.

---

## Recoverable & Cascadeless Schedules

### Recoverable Schedule

A schedule where a transaction commits **only after all transactions it has read from** have committed.

```
  ❌ Non-Recoverable (DANGEROUS):
  T1: Write(X) = 50
  T2: Read(X) = 50         ← T2 reads T1's uncommitted value
  T2: COMMIT                ← T2 commits BEFORE T1!
  T1: ROLLBACK              ← T1 rolls back... but T2 already committed with T1's value!
                              Can't undo T2 → IRRECOVERABLE!

  ✅ Recoverable:
  T1: Write(X) = 50
  T2: Read(X) = 50
  T1: COMMIT ✅              ← T1 commits FIRST
  T2: COMMIT ✅              ← T2 commits AFTER T1 → safe to depend on T1's value
```

### Cascading Rollback

If T1 rolls back, and T2 read T1's data, then T2 must also rollback. If T3 read T2's data, T3 also rolls back → **cascade**.

```
  Cascading Rollback:
  T1: Write(X) = 50
  T2: Read(X) = 50          T2 depends on T1
  T3: Read from T2           T3 depends on T2
  T1: ROLLBACK ❌
     → T2 must ROLLBACK ❌   (read T1's data)
        → T3 must ROLLBACK ❌ (read T2's data)
           → ... cascade continues!
```

### Cascadeless Schedule

A schedule where transactions **only read committed values**. This prevents cascading rollbacks entirely.

```
  ✅ Cascadeless:
  T1: Write(X) = 50
  T1: COMMIT ✅
  T2: Read(X) = 50           ← reads only COMMITTED value → no cascade risk
```

### Schedule Hierarchy

```
  ┌─────────────────────────────────────────────┐
  │              All Schedules                  │
  │  ┌───────────────────────────────────────┐  │
  │  │          Recoverable                  │  │
  │  │  ┌─────────────────────────────────┐  │  │
  │  │  │        Cascadeless              │  │  │
  │  │  │  ┌───────────────────────────┐  │  │  │
  │  │  │  │        Strict             │  │  │  │
  │  │  │  │  ┌─────────────────────┐  │  │  │  │
  │  │  │  │  │      Serial         │  │  │  │  │
  │  │  │  │  └─────────────────────┘  │  │  │  │
  │  │  │  └───────────────────────────┘  │  │  │
  │  │  └─────────────────────────────────┘  │  │
  │  └───────────────────────────────────────┘  │
  └─────────────────────────────────────────────┘
  Serial ⊂ Strict ⊂ Cascadeless ⊂ Recoverable ⊂ All Schedules
```

---

## Advantages & Disadvantages of Concurrency Control

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Reduced waiting time — transactions run in parallel | Overhead from managing locks/timestamps |
| Higher throughput — more transactions per second | Deadlocks possible (lock-based) |
| Better resource utilization — CPU/disk shared | More rollbacks (timestamp-based) |
| Improved response time — users don't wait | Complexity in distributed systems |
| Data consistency maintained | Locking reduces parallelism |

---

## Complete Comparison — All Protocols

| Aspect | Lock-Based (2PL) | Timestamp-Based | Optimistic (Validation) |
|--------|:---:|:---:|:---:|
| **Mechanism** | Locks on data items | Timestamps on transactions | Validate at end |
| **Blocking?** | ✅ Yes (waits for locks) | ❌ No (rollback instead) | ❌ No (rollback if conflict) |
| **Deadlock?** | ⚠️ Possible | ✅ Impossible | ✅ Impossible |
| **Rollbacks** | Few (only on deadlock) | Many (timestamp violations) | Few (only on validation fail) |
| **Best for** | Write-heavy workloads | Mixed workloads | Read-heavy workloads |
| **Used by** | SQL Server, MySQL (InnoDB) | Some research systems | PostgreSQL (SSI), Git |

> **Interview tip:** "How does your database handle concurrency?" — MySQL InnoDB uses **MVCC + 2PL**. PostgreSQL uses **MVCC + Serializable Snapshot Isolation (SSI)**. Oracle uses **MVCC**. SQL Server uses **Lock-based (2PL) with optional MVCC** (snapshot isolation). Understanding that real databases combine multiple techniques is key.

---
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
---

# Types of Schedules in DBMS

🔗 **Reference:** [GeeksforGeeks — Types of Schedules in DBMS](https://www.geeksforgeeks.org/types-of-schedules-in-dbms/)

A **schedule** is the chronological order in which operations (read/write) of multiple concurrent transactions are executed. Choosing the right schedule ensures correctness and consistency.

> **Complete schedule:** a schedule is *complete* when every transaction in it has ended with either a **commit** or an **abort** — no transaction is left in-flight. All the types below are discussed as complete schedules.

---

## Complete Schedule Taxonomy

```
                          ┌──────────────┐
                          │   Schedule   │
                          └──────┬───────┘
                       ┌─────────┴─────────┐
                       ▼                   ▼
               ┌──────────────┐    ┌───────────────┐
               │    Serial    │    │  Non-Serial   │
               │ (no overlap) │    │ (interleaved) │
               └──────────────┘    └───────┬───────┘
                                    ┌──────┴──────┐
                                    ▼             ▼
                            ┌──────────────┐ ┌──────────────────┐
                            │ Serializable │ │ Non-Serializable │
                            └──────┬───────┘ └────────┬─────────┘
                           ┌───────┴───────┐          │
                           ▼               ▼          ▼
                    ┌────────────┐  ┌────────────┐ ┌────────────────┐
                    │  Conflict  │  │    View    │ │  Recoverable/  │
                    │Serializable│  │Serializable│ │Non-Recoverable │
                    └────────────┘  └────────────┘ └────────────────┘
```

---

## 1. Serial Schedule

Transactions execute **one after another** with NO interleaving. Transaction T2 starts only after T1 finishes completely.

```
  Serial Schedule: T1 → T2

  Time    T1           T2
  ────    ──           ──
   1      R(A)
   2      W(A)
   3      R(B)
   4      W(B)
   5      COMMIT
   6                   R(A)
   7                   W(A)
   8                   R(B)
   9                   W(B)
  10                   COMMIT
```

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Always correct and consistent | Very slow — no parallelism |
| No concurrency problems | Poor resource utilization |
| Simple to understand | Not practical for real systems |

> For `n` transactions, there are `n!` possible serial schedules. For T1, T2, T3 → 3! = 6 possible serial orders.

---

## 2. Non-Serial Schedule

Operations from different transactions are **interleaved**. Faster, but must be checked for correctness.

```
  Non-Serial Schedule: T1 and T2 interleaved

  Time    T1           T2
  ────    ──           ──
   1      R(A)
   2                   R(A)
   3      W(A)
   4                   W(A)
   5      R(B)
   6      W(B)
   7      COMMIT
   8                   R(B)
   9                   W(B)
  10                   COMMIT
```

Non-serial schedules are divided into **serializable** and **non-serializable**.

---

## 3. Serializable Schedule

A non-serial schedule that produces the **same result** as some serial schedule. This is the **gold standard** — concurrent but correct.

### 3a. Conflict Serializable

A schedule is **conflict serializable** if it can be converted into a serial schedule by **swapping non-conflicting operations**.

**Two operations conflict when:**
1. They belong to **different** transactions
2. They operate on the **same** data item
3. At least one is a **write**

```
  Conflict pairs:       Non-conflict pairs:
  R(A) and W(A)  ✅     R(A) and R(A)  ❌ (both reads)
  W(A) and R(A)  ✅     R(A) and W(B)  ❌ (different items)
  W(A) and W(A)  ✅     R(A) and R(B)  ❌ (both reads + diff items)
```

**How to test — Precedence Graph:**

1. Create a node for each transaction
2. Add edge Ti → Tj if Ti has a conflicting operation **before** Tj
3. **No cycle** → Conflict Serializable ✅
4. **Cycle** → NOT Conflict Serializable ❌

```
  Example Schedule S:
  T1: R(A)  T2: R(A)  T1: W(A)  T2: W(A)  T1: R(B)  T2: R(B)  T1: W(B)  T2: W(B)

  Conflicts:
  T1:R(A) before T2:W(A) → T1 → T2
  T1:W(A) before T2:R(A)? No, T2:R(A) is at time 2, T1:W(A) is at time 3 → T2 → T1
  
  Precedence Graph:
  T1 ──→ T2
  T2 ──→ T1   ← CYCLE! ❌

  → NOT Conflict Serializable
```

### 3b. View Serializable

A schedule S is **view equivalent** to a serial schedule S' if:

| Condition | Rule |
|-----------|------|
| **Initial Read** | If Ti reads the initial value of X in S, Ti also reads the initial value of X in S' |
| **Updated Read** | If Ti reads a value written by Tj in S, Ti also reads the value written by Tj in S' |
| **Final Write** | If Ti performs the last write on X in S, Ti also performs the last write on X in S' |

```
  Relationship:
  ┌────────────────────────────┐
  │    View Serializable       │
  │  ┌──────────────────────┐  │
  │  │ Conflict Serializable │  │
  │  └──────────────────────┘  │
  └────────────────────────────┘

  Every Conflict Serializable ⊂ View Serializable
  (but NOT vice versa)
```

> **Key insight:** View serializability is harder to test (NP-complete) but allows more schedules than conflict serializability.

---

## 4. Non-Serializable Schedules

Schedules that are NOT equivalent to any serial schedule. They may or may not be safe depending on their **recoverability**.

### 4a. Non-Recoverable Schedule ❌ (Must AVOID)

T2 reads T1's uncommitted data and **commits before T1**. If T1 later aborts, T2 has committed with invalid data — **cannot be undone**.

```
  Time    T1           T2
  ────    ──           ──
   1      R(A)
   2      W(A)
   3                   R(A)     ← reads T1's uncommitted value
   4                   W(A)
   5                   COMMIT   ← T2 commits BEFORE T1!
   6      ABORT ❌               ← T1 rolls back...
                                   but T2 already committed!
                                   IRRECOVERABLE! 💀
```

> ⚠️ Non-recoverable schedules must ALWAYS be avoided. If T1 aborts, we can't undo T2's commit.

### 4b. Recoverable Schedule ✅

T2 commits **only after** T1 (the transaction it read from) has committed.

```
  Time    T1           T2
  ────    ──           ──
   1      R(A)
   2      W(A)
   3                   R(A)     ← reads T1's value
   4      COMMIT ✅              ← T1 commits FIRST
   5                   COMMIT ✅ ← T2 commits AFTER T1 → safe!
```

> **Rule:** If T2 reads data written by T1, then T1 must commit **before** T2.

### 4c. Cascading Schedule (Recoverable but Risky)

Recoverable, but failure of one transaction causes a **chain of rollbacks** (cascade abort).

```
  Time    T1           T2           T3
  ────    ──           ──           ──
   1      R(A)
   2      W(A) = 50
   3                   R(A) = 50    ← reads T1's uncommitted data
   4                   W(A) = 70
   5                                R(A) = 70  ← reads T2's uncommitted data
   6      ABORT ❌
   7                   ABORT ❌      ← must abort (read from T1)
   8                                ABORT ❌   ← must abort (read from T2)

  Cascade: T1 fails → T2 fails → T3 fails → ... 💥
```

> Cascading aborts are expensive — they waste all the work done by dependent transactions.

### 4d. Cascadeless Schedule ✅ (No Cascading Aborts)

Transactions **only read committed values**. If T1 writes X, T2 can read X only **after T1 commits**.

```
  Time    T1           T2
  ────    ──           ──
   1      R(A)
   2      W(A)
   3      COMMIT ✅
   4                   R(A)     ← reads ONLY committed value → safe!
   5                   W(A)
   6                   COMMIT ✅
```

> **Rule:** Dirty reads are completely eliminated → no cascading abort possible.

### 4e. Strict Schedule ✅ (Strongest)

Neither **read NOR write** a data item until the transaction that last wrote it has committed or aborted.

```
  Time    T1           T2
  ────    ──           ──
   1      W(A)
   2      COMMIT ✅
   3                   R(A)     ← read after commit ✅
   4                   W(A)     ← write after commit ✅
   5                   COMMIT ✅
```

**Difference from Cascadeless:**

| | Cascadeless | Strict |
|--|:---:|:---:|
| Dirty **reads** prevented | ✅ | ✅ |
| Dirty **writes** prevented | ❌ | ✅ |

```
  Cascadeless but NOT Strict:
  T1: W(A)
  T2: W(A)         ← writes BEFORE T1 commits (dirty write!) ❌ for strict
  T1: COMMIT
  T2: COMMIT

  Strict:
  T1: W(A)
  T1: COMMIT ✅
  T2: W(A)         ← writes AFTER T1 commits ✅
  T2: COMMIT ✅
```

---

## Schedule Hierarchy (Venn Diagram)

```
  ┌─────────────────────────────────────────────────────────┐
  │                    All Schedules                        │
  │                                                         │
  │   ┌───────────────────────────────────────────────┐     │
  │   │              Recoverable                      │     │
  │   │                                               │     │
  │   │   ┌───────────────────────────────────────┐   │     │
  │   │   │           Cascadeless                 │   │     │
  │   │   │                                       │   │     │
  │   │   │   ┌───────────────────────────────┐   │   │     │
  │   │   │   │           Strict              │   │   │     │
  │   │   │   │                               │   │   │     │
  │   │   │   │   ┌───────────────────────┐   │   │   │     │
  │   │   │   │   │       Serial          │   │   │   │     │
  │   │   │   │   └───────────────────────┘   │   │   │     │
  │   │   │   └───────────────────────────────┘   │   │     │
  │   │   └───────────────────────────────────────┘   │     │
  │   └───────────────────────────────────────────────┘     │
  │                                                         │
  │   Non-Recoverable (outside Recoverable) ← AVOID!       │
  └─────────────────────────────────────────────────────────┘

  Serial ⊂ Strict ⊂ Cascadeless ⊂ Recoverable ⊂ All Schedules
```

---

## All Schedule Types at a Glance

| Schedule Type | Interleaved? | Correct? | Dirty Reads? | Dirty Writes? | Cascading Abort? |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **Serial** | ❌ No | ✅ Always | ✅ No | ✅ No | ✅ No |
| **Conflict Serializable** | ✅ Yes | ✅ Yes | Depends | Depends | Depends |
| **View Serializable** | ✅ Yes | ✅ Yes | Depends | Depends | Depends |
| **Strict** | ✅ Yes | ✅ If recoverable | ✅ No | ✅ No | ✅ No |
| **Cascadeless** | ✅ Yes | ✅ If recoverable | ✅ No | ⚠️ Possible | ✅ No |
| **Recoverable** | ✅ Yes | ✅ Recoverable | ⚠️ Possible | ⚠️ Possible | ⚠️ Possible |
| **Non-Recoverable** | ✅ Yes | ❌ INVALID | ⚠️ Possible | ⚠️ Possible | N/A (broken) |

---

## Lock-Based Protocol Types

```
  ┌────────────────────────────────┐
  │     Lock-Based Protocols       │
  └───────────────┬────────────────┘
    ┌─────────────┼─────────────┬──────────────┐
    ▼             ▼             ▼              ▼
  Simplistic   Pre-Claiming   2PL        Strict 2PL
```

### 1. Simplistic Lock Protocol

Acquire lock on an item **before writing** it. Unlock **after** the write is done.

```
  T1: Lock(A) → Write(A) → Unlock(A)
```

> Very basic. Doesn't prevent all concurrency problems.

### 2. Pre-Claiming Lock Protocol

Before execution, the transaction requests **ALL locks it will need** at once.
- If ALL locks are granted → execute the transaction → release all at end
- If ANY lock is denied → **rollback** and wait → retry later

```
  T1 needs: Lock(A), Lock(B), Lock(C)

  Request all three at once:
    All granted? → Execute T1 → Release all locks ✅
    Any denied?  → Rollback → Wait → Retry later ❌
```

> **Advantage:** No deadlocks (all-or-nothing). **Disadvantage:** Poor concurrency (holds locks for entire duration, even if some items are used only at the end).

### 3. Two-Phase Locking (2PL) — Recap

```
  Growing Phase:                    Shrinking Phase:
  ─────────────                     ────────────────
  Acquire locks                     Release locks
  Cannot release any                Cannot acquire any

    Locks held
       │     ╱╲
       │    ╱  ╲
       │   ╱    ╲
       │  ╱      ╲
       │ ╱  Lock  ╲
       │╱   Point  ╲
  ─────┼─────┬──────╲────────► Time
       │ Growing  Shrinking
```

> ✅ Guarantees **conflict serializability**. ⚠️ Can have cascading aborts. ⚠️ Deadlocks possible.

### 4. Strict Two-Phase Locking (Strict 2PL)

Same as 2PL, but **holds ALL locks until COMMIT or ABORT**. No early release.

```
  Strict 2PL:
       Locks held
       │          ┌────────────────┐
       │          │                │
       │          │ All locks held │
       │          │ until COMMIT   │
       │          │                │
  ─────┼──────────┼────────────────┼───► Time
       │  Growing │                │
       │  Phase   │   COMMIT ──► Release ALL
```

> ✅ Conflict serializable. ✅ **No cascading aborts.** ⚠️ Deadlocks still possible.

---

## Thomas' Write Rule

An **optimization** for timestamp-based protocols that avoids unnecessary rollbacks.

### Normal Timestamp Rule for Write:

```
  If TS(Ti) < W-TS(X):
    → A later transaction already wrote X
    → Ti's write is OUTDATED
    → Normal rule: ROLLBACK Ti ❌
```

### Thomas' Write Rule:

```
  If TS(Ti) < W-TS(X):
    → A later transaction already wrote X
    → Ti's write is outdated
    → Thomas' Rule: Just IGNORE Ti's write (skip it, don't rollback) ✅
    → Ti continues executing
```

**Why it works:** Ti's write would be overwritten anyway by the later transaction, so there's no point in rolling back — just skip it.

```
  Example:
  T1 (TS=1)     T2 (TS=2)        W-TS(X)
  ──────────     ──────────       ───────
                 Write(X)           2        T2 writes X
  Write(X)                          ?

  Normal rule:  TS(T1)=1 < W-TS(X)=2 → ROLLBACK T1 ❌
  Thomas' rule: TS(T1)=1 < W-TS(X)=2 → IGNORE T1's write, continue ✅

  Result: X keeps T2's value (which would have overwritten T1 anyway)
```

> **Key point:** Thomas' Write Rule produces **view serializable** schedules (not necessarily conflict serializable).

---

## Practice Question

```
  Schedule S: R1(A), W2(A), Commit2, W1(A), W3(A), Commit3, Commit1
```

**Step 1: Draw the timeline**

| Time | T1 | T2 | T3 |
|:---:|:---:|:---:|:---:|
| 1 | R(A) | | |
| 2 | | W(A) | |
| 3 | | COMMIT | |
| 4 | W(A) | | |
| 5 | | | W(A) |
| 6 | | | COMMIT |
| 7 | COMMIT | | |

**Step 2: Is it Serializable?**

Check for **conflict serializability** (precedence graph):
- T1:R(A) before T2:W(A) → `T1 → T2`
- T2:W(A) before T1:W(A) → `T2 → T1`
- Cycle! T1 → T2 → T1 → ❌ **NOT conflict serializable**

Check for **view serializability**:
- Initial read of A: T1 reads initial value ✅ (matches T1 → T2 → T3)
- Final write of A: T3 does the last write ✅
- View equivalent to serial order T1 → T2 → T3 ✅ → **View Serializable**

**Step 3: Is it Strict?**

- T1 writes A (time 4) and T3 writes A (time 5) before T1 commits (time 7)
- ❌ **NOT strict** (T3 writes A before T1 commits)

**Step 4: Is it Recoverable?**

- T2 commits at time 3 — T2 wrote A but didn't read from anyone → OK
- T3 commits at time 6 — T3 wrote A but didn't read from anyone → OK
- T1 commits at time 7 → OK

✅ **Recoverable** (no transaction committed with uncommitted dependent data)

**Answer:** The schedule is **view serializable** and **recoverable but NOT strict**. ✅ Option (D)

---

## Quick Summary

```
  Schedule Hierarchy:
    Serial ⊂ Strict ⊂ Cascadeless ⊂ Recoverable ⊂ All Schedules

  Serializability Check:
    Conflict: Precedence Graph → no cycle = ✅
    View:     Check 3 conditions (initial read, updated read, final write)
    Conflict ⊂ View

  Lock Protocols:
    Simplistic → lock before write, unlock after
    Pre-Claiming → all locks upfront (no deadlock, low concurrency)
    2PL → growing + shrinking phases (serializable, cascading aborts)
    Strict 2PL → hold all locks until commit (no cascading aborts)

  Thomas' Write Rule:
    If older write is outdated → IGNORE it instead of rolling back
    Produces view-serializable schedules
```

> **Interview tip:** "What is the difference between Cascadeless and Strict schedules?" — Cascadeless prevents dirty reads (transactions read only committed data). Strict prevents both dirty reads AND dirty writes (no transaction reads OR writes data written by an uncommitted transaction). Strict ⊂ Cascadeless.

---
---

# What Is the Meaning of the Word "Relational" in RDBMS?

**Common misconception ❌:** "Relational means tables are related to each other via foreign keys/joins." That's not where the word comes from.

**Actual origin:** It comes from **E. F. Codd's 1970 paper**, borrowing the mathematical term **"relation"** — a set of **tuples** drawn from the Cartesian product of **domains**. In plain English: a **relation** is just a table, where each row is a tuple of values from fixed columns.

| Mathematical Term | DBMS Equivalent |
|---|---|
| **Relation** | Table |
| **Tuple** | Row |
| **Attribute** | Column |
| **Domain** | Valid value set for a column |

So "the `employees` relation" means the table itself — not its relationships to other tables.

> **Why it matters:** Because a relation is mathematically a *set*, it's the reason relational databases support **Relational Algebra** (σ select, π project, ∪ union, − difference, × product, ⋈ join) — the theoretical basis for SQL.

> **Interview tip:** Lead with the correction — "It's commonly misunderstood as tables being related via foreign keys, but it actually comes from the mathematical term *relation* (a set of tuples over a Cartesian product of domains), which is also why relational databases support relational algebra."

---
---

# MySQL Query Pipeline — Parser, Precompiler & the Cost-Based Optimizer

Before MySQL returns a single row, your SQL text goes through a fixed pipeline. Knowing the stages tells you **where** a problem lives: a syntax error dies in the parser, an "unknown column" dies in the preprocessor, and a slow-but-correct query is almost always an **optimizer** decision you disagree with.

---

## The Whole Pipeline

```
   SQL text
      │
      ▼
┌─────────────────────┐
│ 1. Connection /     │  authenticate, assign a thread, check privileges
│    Thread handling  │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 2. PARSER           │  tokenize → build a parse tree
│    (lexer + syntax) │  ❌ dies here on: "You have an error in your SQL syntax"
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 3. PREPROCESSOR     │  semantic validation ("the precompile step")
│    (resolver)       │  ❌ dies here on: "Unknown column 'x' in 'field list'"
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 4. OPTIMIZER        │  cost-based: pick indexes, join order, join algorithm
│    (cost-based)     │  ⚠️ slow-but-correct queries are decided HERE
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 5. EXECUTION ENGINE │  walk the chosen plan, call the storage engine
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 6. STORAGE ENGINE   │  InnoDB: buffer pool → B+ tree lookups → disk
└──────────┬──────────┘
           ▼
       Result set
```

---

## Stage 2 — The Parser

The parser does two mechanical jobs and nothing else:

| Step | What Happens |
|---|---|
| **Lexical analysis** | Chops the SQL string into tokens: `SELECT`, `name`, `,`, `FROM`, `users`, `WHERE`, … |
| **Syntax analysis** | Feeds tokens through MySQL's grammar to build a **parse tree** |

The parser knows the *grammar* of SQL but nothing about **your** database — it has never heard of your tables.

```sql
SELCT * FROM users;
-- ❌ ERROR 1064 (42000): You have an error in your SQL syntax near 'SELCT'
--    Caught by the PARSER — 'SELCT' is not a valid token.
```

---

## Stage 3 — The Preprocessor (the "precompiler" step)

The preprocessor takes the parse tree and checks it against **reality**:

| Check | Example Failure |
|---|---|
| Do the tables exist? | `ERROR 1146: Table 'shop.userz' doesn't exist` |
| Do the columns exist? | `ERROR 1054: Unknown column 'emial' in 'field list'` |
| Is a column name ambiguous? | `ERROR 1052: Column 'id' in field list is ambiguous` |
| Does this user have privileges? | `ERROR 1142: SELECT command denied to user...` |
| Expand views into their underlying query | `SELECT * FROM v_active_users` → the view's `SELECT` is inlined |

```sql
SELECT emial FROM users;
-- ✅ Passes the PARSER  (syntactically perfect)
-- ❌ Dies in the PREPROCESSOR: Unknown column 'emial' in 'field list'
```

> **Two meanings of "precompiler" — know both for interviews:**
>
> | Meaning | What It Refers To |
> |---|---|
> | **Classic DBMS textbook** | An **embedded-SQL precompiler** (Pro\*C, SQLJ, ESQL/C). You write `EXEC SQL SELECT ...` inside C/COBOL; the precompiler runs *before* the C compiler, replacing those blocks with database API calls. Largely historical — modern apps use JDBC/ODBC/ORMs instead. |
> | **MySQL practical** | The **parse + preprocess phase**, and specifically **prepared statements** — where MySQL parses and plans a statement once, then executes it many times with different values. |

### Prepared Statements — "Precompile Once, Execute Many"

```sql
-- 1. PREPARE: parse + preprocess + plan ONCE, store as a handle
PREPARE stmt FROM 'SELECT id, name FROM users WHERE country = ? AND age > ?';

-- 2. EXECUTE: reuse the plan, only the values change
SET @c = 'IN', @a = 25;
EXECUTE stmt USING @c, @a;

SET @c = 'US', @a = 40;
EXECUTE stmt USING @c, @a;      -- no re-parsing

-- 3. Clean up
DEALLOCATE PREPARE stmt;
```

In application code you almost never write `PREPARE` by hand — the driver does it:

```java
// JDBC — this IS a prepared statement
PreparedStatement ps = conn.prepareStatement(
    "SELECT id, name FROM users WHERE country = ? AND age > ?");
ps.setString(1, "IN");
ps.setInt(2, 25);
ResultSet rs = ps.executeQuery();
```

| Benefit | Why It Matters |
|---|---|
| **SQL injection immunity** | Values travel **separately** from the SQL text — they can never be parsed as SQL. This is the #1 reason to use them. See [SQL Injection](#sql-injection). |
| **Skip re-parsing** | Parse + preprocess happen once per handle instead of once per execution |
| **Smaller network payload** | After the first call, only the parameter values go over the wire |
| **Type safety** | The driver sends typed values instead of stringified SQL literals |

**Gotchas:**

- A prepared statement is **scoped to one connection**. Connection pools re-prepare per physical connection.
- MySQL's Connector/J defaults to **client-side** prepared statements. Set `useServerPrepStmts=true` to get real server-side `PREPARE`.
- The plan is chosen at `PREPARE` time on some paths, so a plan that suits `country = 'IN'` (500M rows) may be reused for `country = 'MC'` (200 rows). This is the classic **parameter-sniffing** trade-off.
- MySQL 8.0 **removed the query cache** entirely — prepared statements save *parsing*, not *result* reuse.

---

## Stage 4 — The Cost-Based Optimizer

The optimizer's job: given one SQL statement, choose the **cheapest execution plan** among many equivalent ones. MySQL's optimizer is **cost-based**, not rule-based — it assigns a number to each candidate plan and picks the smallest.

### What the Optimizer Actually Decides

| Decision | Options It Weighs |
|---|---|
| **Access method** per table | Full table scan / index scan / index range scan / index lookup / covering index |
| **Which index** to use | Any usable index — or none, if a scan looks cheaper |
| **Join order** | For `A JOIN B JOIN C`, which table is scanned first (`A→B→C`? `C→A→B`?) |
| **Join algorithm** | Nested-Loop, Block Nested-Loop, or **Hash Join** (8.0.18+) |
| **Subquery strategy** | Rewrite to a join / semi-join, or materialize into a temp table |
| **Sort strategy** | Read in index order (free) vs an explicit `filesort` |
| **Aggregation strategy** | Loose index scan vs temporary table |

### How Cost Is Estimated

Cost is computed from **statistics**, not from your data itself:

```
plan cost  ≈  (rows examined × cpu_cost)  +  (pages read × io_cost)
```

| Source | What It Provides |
|---|---|
| **Index cardinality** | Estimated number of distinct values per index — drives selectivity guesses |
| `ANALYZE TABLE t;` | Recomputes those statistics. Run it after bulk loads/deletes. |
| **Histograms** (8.0+) | `ANALYZE TABLE t UPDATE HISTOGRAM ON col;` — real value distributions for **non-indexed** columns; fixes skew misestimates |
| `mysql.server_cost` / `mysql.engine_cost` | Tunable cost constants (e.g. `io_block_read_cost`, `memory_block_read_cost`) |

```sql
-- Look at what the optimizer thinks it knows
SHOW INDEX FROM orders;              -- Cardinality column
SELECT * FROM information_schema.STATISTICS WHERE TABLE_NAME = 'orders';
```

> ⚠️ Cardinality in InnoDB is **sampled and approximate**, not exact. That's why a stale-statistics table can suddenly get a terrible plan after a big data change — and why `ANALYZE TABLE` sometimes "magically fixes" a slow query.

### Optimizer Rewrites (Transformations)

Before costing, the optimizer rewrites your query into an equivalent-but-friendlier form:

| Transformation | Example |
|---|---|
| **Constant folding** | `WHERE price > 10 * 5` → `WHERE price > 50` |
| **Constant propagation** | `WHERE a = 5 AND b = a` → `WHERE a = 5 AND b = 5` |
| **Impossible-WHERE detection** | `WHERE 1 = 0` → plan becomes "Impossible WHERE", table never read |
| **Subquery → semi-join** | `WHERE id IN (SELECT user_id FROM orders)` → a semi-join |
| **Derived table merging** | `FROM (SELECT ...) d` merged into the outer query when possible |
| **Index Condition Pushdown (ICP)** | Pushes `WHERE` filters down into the storage engine so non-matching rows are discarded *before* being read into the server |
| **Multi-Range Read (MRR)** | Sorts row-IDs from an index before fetching, converting random I/O into sequential I/O |
| **`ORDER BY` elimination** | If an index already returns rows in the requested order, skip the sort entirely |

### Seeing the Plan

```sql
EXPLAIN SELECT ...;                  -- the chosen plan
EXPLAIN FORMAT=JSON SELECT ...;      -- same, plus the actual cost numbers
EXPLAIN ANALYZE SELECT ...;          -- 8.0.18+: runs it, shows ESTIMATED vs ACTUAL rows
```

`EXPLAIN ANALYZE` is the most valuable of the three: when **estimated rows** and **actual rows** differ by orders of magnitude, you've found your bad plan's root cause — bad statistics.

🔗 For the full column-by-column guide to reading plans, see [EXPLAIN — Reading Query Execution Plans](#explain--reading-query-execution-plans).

### Watching the Optimizer Think — `optimizer_trace`

```sql
SET optimizer_trace = 'enabled=on';
SELECT ... ;                          -- run the query
SELECT * FROM information_schema.OPTIMIZER_TRACE\G
SET optimizer_trace = 'enabled=off';
```

The trace is a JSON document listing every plan considered, the cost assigned to each, and **why** the rejected ones lost. This is the definitive answer to "why isn't it using my index?".

### Overriding the Optimizer

Use these as a **last resort** — a hint you add today becomes a wrong hint after the data grows.

```sql
-- Index hints (older syntax, applies to one table)
SELECT * FROM orders USE INDEX (idx_created)    WHERE ...;
SELECT * FROM orders FORCE INDEX (idx_created)  WHERE ...;   -- "scan is basically never allowed"
SELECT * FROM orders IGNORE INDEX (idx_status)  WHERE ...;

-- Optimizer hints (8.0+, comment syntax, more granular)
SELECT /*+ JOIN_ORDER(o, c) */        ... FROM orders o JOIN customers c ...;
SELECT /*+ NO_INDEX(orders idx_status) */ ...;
SELECT /*+ MAX_EXECUTION_TIME(1000) */ ...;   -- kill after 1s

-- Toggle whole optimizer features for a session
SET SESSION optimizer_switch = 'index_condition_pushdown=off';
```

### ❓ Why Doesn't MySQL Use My Index?

| Cause | Fix |
|---|---|
| **Low selectivity** — the index matches too large a fraction of rows | Nothing to fix; a scan genuinely is cheaper. See [Cardinality & Selectivity](#cardinality--selectivity--how-duplicate-values-affect-an-index). |
| **Stale statistics** | `ANALYZE TABLE t;` |
| **Data skew** — `status='active'` is 99% of rows but average cardinality says otherwise | Add a histogram: `ANALYZE TABLE t UPDATE HISTOGRAM ON status;` |
| **Function wrapping the column** — `WHERE YEAR(created_at) = 2024` | Rewrite as a range: `WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'` |
| **Type mismatch** — `WHERE varchar_col = 123` | Compare like types; an implicit cast disables the index |
| **Leading-column violation** on a composite index | See [Leftmost-Prefix Rule](#leftmost-prefix-rule) |
| **Leading wildcard** — `LIKE '%abc'` | Only `LIKE 'abc%'` can use a B+ tree; consider `FULLTEXT` |

---

## Quick-Fire Q&A

| Question | Answer |
|---|---|
| Which stage catches a typo in a keyword? | The **parser** (syntax) |
| Which stage catches a typo in a column name? | The **preprocessor** (semantic) |
| Is MySQL's optimizer rule-based or cost-based? | **Cost-based** — it prices candidate plans and picks the cheapest |
| What does `PREPARE` actually save? | Re-parsing and re-planning — **not** result caching (the query cache is gone in 8.0) |
| Why are prepared statements the fix for SQL injection? | Values are sent **separately** from the SQL text, so they can never be parsed as SQL |
| How do you see estimated vs actual row counts? | `EXPLAIN ANALYZE` (MySQL 8.0.18+) |
| How do you find out *why* an index was rejected? | `optimizer_trace` |
| First thing to try when a good plan suddenly goes bad? | `ANALYZE TABLE` — stale statistics are the usual culprit |

🔗 Next: [How to Optimize a SQL Query](#how-to-optimize-a-sql-query) turns these mechanics into a practical checklist.

---
---

# How to Optimize a SQL Query

Query optimization means reducing the amount of data the database reads, joins, sorts, and returns. Start with evidence: inspect the execution plan before changing the query or adding an index.

```sql
EXPLAIN ANALYZE
SELECT order_id, total_amount
FROM orders
WHERE customer_id = 42
  AND status = 'PAID'
ORDER BY created_at DESC
LIMIT 20;
```

`EXPLAIN` shows the plan the optimizer chose. Look for full table scans, a very large estimated or actual row count, expensive sorts, and joins that process many more rows than expected. `EXPLAIN ANALYZE` also runs the query and reports actual timings; availability and exact syntax vary by database.

## Practical Checklist

| Check | Why it helps | Example |
|---|---|---|
| Index filter and join columns | Lets the database find matching rows instead of scanning every row | `WHERE customer_id = ?`, `JOIN orders.customer_id = customers.id` |
| Use a selective composite index for filters used together | Narrows rows quickly and can avoid a sort | `INDEX(customer_id, status, created_at)` |
| Select only required columns | Reduces I/O, network transfer, and memory use | Prefer `SELECT order_id, total_amount` over `SELECT *` |
| Keep indexed columns bare in predicates | A function or calculation can prevent an index range lookup | Prefer `created_at >= '2026-08-01'` over `DATE(created_at) = '2026-08-01'` |
| Avoid a leading wildcard | `LIKE '%phone'` usually cannot seek efficiently in a B-tree index | Prefer `LIKE 'phone%'`; use full-text search for contains search |
| Filter early and join on indexed keys | Reduces rows carried into later joins | Filter `orders` before joining large detail tables |
| Avoid unnecessary `DISTINCT`, `ORDER BY`, and large `OFFSET` | They may require sorting or scanning many rows | Use keyset pagination: `WHERE id > ? ORDER BY id LIMIT 20` |
| Keep table statistics current | The optimizer needs accurate row-count estimates | Run the database's `ANALYZE` or statistics maintenance command |

### Example: From Scan and Sort to Index Lookup

```sql
-- Query: fetch a customer's newest paid orders
SELECT order_id, total_amount, created_at
FROM orders
WHERE customer_id = 42
  AND status = 'PAID'
ORDER BY created_at DESC
LIMIT 20;

CREATE INDEX idx_orders_customer_status_created
    ON orders (customer_id, status, created_at DESC);
```

With this index, the database can navigate directly to the rows for one customer and status, read them in `created_at` order, and stop after 20 rows. Confirm the benefit with `EXPLAIN`: indexes add storage cost and make `INSERT`, `UPDATE`, and `DELETE` slower.

> **Interview answer:** "I first use `EXPLAIN ANALYZE` to find the costly scan, join, or sort. Then I reduce rows and columns early, ensure predicates and join keys are indexed, design composite indexes for the query pattern, and re-check the actual plan. I avoid adding indexes blindly because every index increases write cost."

---
---

# The Buffer Pool — How Data Actually Flows Between Disk and Memory

The **buffer pool** is the database's in-memory cache of **disk pages**. It is the single most important performance structure in any DBMS, and the reason a query on a 500 GB table can return in a millisecond.

> **The one rule to remember:** the database engine **never** reads or writes a row directly on disk. It reads the **page** containing that row into the buffer pool, works on the copy in RAM, and writes the page back **later**.

**The unit is a page, not a row:**

| Engine | Page size | Buffer pool name |
|---|:---:|---|
| MySQL / InnoDB | 16 KB | Buffer Pool (`innodb_buffer_pool_size`) |
| PostgreSQL | 8 KB | Shared Buffers (`shared_buffers`) |
| SQL Server | 8 KB | Buffer Cache |
| Oracle | 8 KB | Database Buffer Cache |

Asking for one 200-byte row still loads the whole 16 KB page — which is *good*, because the neighbouring rows are usually the ones you want next.

---

## Key Terms — Page, Frame, Dirty, Clean, Pinned

### Page (block)

A **page** is the **fixed-size unit of I/O** — the smallest chunk the database will ever read from or write to disk. Your table file is simply a long array of these pages, and a page holds many rows plus some bookkeeping:

```
   One 16 KB InnoDB page
   ┌────────────────────────────────────────────┐
   │ Header (page id, type, checksum, LSN …)    │
   ├────────────────────────────────────────────┤
   │ Row 1 │ Row 2 │ Row 3 │ Row 4 │ …          │
   ├────────────────────────────────────────────┤
   │            free space                      │
   ├────────────────────────────────────────────┤
   │ Slot directory (offsets to each row)       │
   └────────────────────────────────────────────┘
```

> There is **no such thing as reading one row from disk.** You read its page. Index nodes are pages too — a B+ tree is a tree *of pages*.

### Frame

A **frame** is one page-sized slot **inside the buffer pool**. A buffer pool of 8 GB with 16 KB pages has ~524,000 frames. Each frame either sits empty or holds a copy of one disk page.

### Clean vs Dirty — the important pair

The distinction is simply: **does the in-memory copy still match the on-disk copy?**

| | **Clean page** | **Dirty page** |
|---|---|---|
| Definition | The RAM copy is **identical** to the disk copy | The RAM copy has been **modified**; disk still holds the old version |
| Created by | Reading a page in, or flushing a dirty page | Any `INSERT` / `UPDATE` / `DELETE` touching that page |
| Cost to evict | **Free** — just drop it, disk already has the truth | **Expensive** — must be written to disk first |
| Lost on crash? | Doesn't matter — disk has the same bytes | ⚠️ Yes — recovered by **replaying the WAL** |

```
   Page lifecycle inside the buffer pool
   ─────────────────────────────────────

   (not in memory)
        │  read from disk (page miss)
        ▼
   ┌──────────┐    UPDATE / INSERT / DELETE     ┌──────────┐
   │  CLEAN   │ ──────────────────────────────► │  DIRTY   │
   │ RAM=disk │                                 │ RAM≠disk │
   └────┬─────┘ ◄────────────────────────────── └────┬─────┘
        │           background flush /               │
        │           checkpoint writes it out         │
        │                                            │
        │ evict: just drop it ✅          evict: MUST flush first ⏳
        ▼                                            ▼
   (frame reused)                              (frame reused)
```

### Pinned page

While a query is actively reading or writing a page, the page is **pinned** (its pin/reference count is > 0) so the eviction algorithm cannot steal it mid-operation. Once the operation finishes the page is unpinned and becomes a candidate for eviction again.

### Why these terms matter

| Concept | Consequence |
|---|---|
| Too many dirty pages | Eviction and checkpoints stall, because each victim must be written out first — writes start blocking |
| Mostly clean pool | Evictions are instant, so a read-heavy workload stays fast |
| Dirty pages at crash time | Exactly what WAL replay has to reconstruct — more dirty pages means longer crash recovery |
| **Checkpoint** | The periodic operation that flushes dirty pages and records "everything before this point is safely on disk", so recovery doesn't have to replay the whole log |

> **In one line:** a page is the unit of transfer; *dirty* means "changed in memory, not yet on disk"; *clean* means "memory and disk agree"; a checkpoint is what turns dirty pages back into clean ones.

---

### The Whole Picture

```
        Client
          │  SELECT / UPDATE
          ▼
  ┌───────────────────────────────────────────────────────────┐
  │  SQL layer:  parser → optimizer → executor                │
  └────────────────────────┬──────────────────────────────────┘
                           │  "give me page #4711"
                           ▼
  ┌───────────────────────────────────────────────────────────┐
  │                    B U F F E R   P O O L   (RAM)          │
  │                                                           │
  │   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │
  │   │page 12 │ │page 4711│ │page 88 │ │page 301│  …         │
  │   │ clean  │ │  DIRTY │ │ clean  │ │  DIRTY │            │
  │   └────────┘ └────────┘ └────────┘ └────────┘            │
  │        ▲          │                     │                 │
  │        │ miss:    │ modified in memory  │                 │
  │        │ load     ▼                     ▼                 │
  │        │     ┌─────────────┐   ┌──────────────────┐       │
  │        │     │  Log buffer │   │ Background flush │       │
  │        │     └──────┬──────┘   │ (at checkpoint)  │       │
  └────────┼────────────┼──────────┴────────┬─────────┘       │
           │            │                   │
           │      fsync │ at COMMIT         │ later, batched
           │       (sequential)             │  (random)
           ▼            ▼                   ▼
  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐
  │ Table/index │ │  WAL / redo  │ │   Table/index    │
  │ files (read)│ │  log  (D!)   │ │  files  (write)  │
  └─────────────┘ └──────────────┘ └──────────────────┘
                        D I S K
```

Two things to notice: **reads** come *up* into the pool, and a **commit** goes down the *log* path — never straight to the table file.

---

## The Read Path — Page Hit vs Page Miss

```
  SELECT * FROM users WHERE id = 42;
             │
             ▼
   ┌──────────────────────┐
   │  Is the page already │
   │  in the buffer pool? │
   └──────┬────────┬──────┘
      YES │        │ NO
          │        │
          ▼        ▼
   ┌───────────┐  ┌────────────────────────────────────┐
   │ PAGE HIT  │  │ PAGE MISS (or "hard fault")        │
   │ ~100 ns   │  │ 1. Find a free frame in the pool   │
   │ read from │  │    (evict a victim page if full)   │
   │ RAM ✅    │  │ 2. Read the 16 KB page from disk   │
   └───────────┘  │ 3. Place it in the buffer pool     │
                  │ 4. Now serve the row from RAM      │
                  │ ~100 µs on SSD / ~10 ms on HDD 🐢  │
                  └────────────────────────────────────┘
```

A **page hit** is ~1,000× faster than a page miss on SSD. That ratio is the whole reason the buffer pool exists.

---

## The Write Path — Why a Write Doesn't Touch the Table File

This is the part most people get wrong. `UPDATE` does **not** write to the table file on disk.

```
  UPDATE users SET city = 'Pune' WHERE id = 42;

  Step 1  Load the page into the buffer pool (if not already there)
             │
  Step 2  Modify the row IN MEMORY
             │  → the page is now a DIRTY PAGE
             │    (memory version ≠ disk version)
             ▼
  Step 3  Append the change to the WAL / redo log  ──► fsync to disk ✅
             │    THIS is what makes COMMIT durable
             ▼
  Step 4  COMMIT returns to the client  ← the data page is STILL only in RAM
             │
  Step 5  Later, a background thread flushes dirty pages to the table file
             │    (at a checkpoint, or under memory pressure)
             ▼
  Step 6  Page is clean again — memory matches disk
```

| | Written at COMMIT? | Access pattern |
|---|:---:|---|
| **WAL / redo log** | ✅ Yes — synchronously `fsync`ed | **Sequential** append — fast even on HDD |
| **Data pages** | ❌ No — flushed later in the background | **Random** writes — slow, so we batch them |

> **Why this is a huge win:** if the same page is updated 100 times in a minute, it's written to disk **once** at the next flush instead of 100 times. This is called **write coalescing**. And durability isn't compromised, because the WAL already has every change — see [Durability — How It's Achieved](#4-durability--how-its-achieved).

> **On crash:** the buffer pool is volatile, so all dirty pages are lost. On restart, recovery **replays the WAL** to rebuild them. This is why the rule is *"write the log before the data"* (Write-Ahead Logging).

---

## `fsync()` — What "Written to Disk" Actually Means

Calling `write()` does **not** put your data on disk. It copies the bytes into a **kernel buffer (the OS page cache)** and returns immediately. The data is still in **volatile RAM** — a power cut loses it. `fsync(fd)` is the system call that says *"push everything for this file all the way down to persistent media, and don't return until it's there."*

### The Layers a Write Must Cross

```
   ┌──────────────────────────────────────────┐
   │  Database process (buffer pool, log buf) │  ← volatile
   └────────────────────┬─────────────────────┘
                        │  write()   → returns in ~µs, NOT durable
                        ▼
   ┌──────────────────────────────────────────┐
   │  OS Page Cache  (kernel RAM)             │  ← volatile
   └────────────────────┬─────────────────────┘
                        │  fsync()   → BLOCKS until done ⏳
                        ▼
   ┌──────────────────────────────────────────┐
   │  Disk write-back cache (controller DRAM) │  ← volatile*
   └────────────────────┬─────────────────────┘
                        │  FLUSH CACHE / FUA command
                        ▼
   ┌──────────────────────────────────────────┐
   │  Persistent media (NAND / platters)      │  ← ✅ SURVIVES POWER LOSS
   └──────────────────────────────────────────┘

   * unless the drive has battery- or capacitor-backed cache
     (power-loss protection), in which case it is effectively durable
```

`COMMIT` cannot return until the WAL record has reached the **bottom** layer. That is the entire cost of the **D** in ACID.

### Without fsync vs With fsync

```
  ── WITHOUT fsync ──────────────────────────────────────────────

  T1: write(log) ──► OS page cache ──► "COMMIT OK" returned to user ✅
                            │
                       💥 POWER LOSS (before the kernel flushed)
                            │
                            ▼
                     Log record GONE.
      The user was told "committed" but the change vanished.
                  ❌ DURABILITY VIOLATED

  ── WITH fsync ─────────────────────────────────────────────────

  T1: write(log) ──► OS page cache
      fsync(log)  ──────────────────► persistent media ✅
                            │
                  ◄─── returns (0.1–10 ms later)
                            │
                    "COMMIT OK" returned to user ✅
                            │
                       💥 POWER LOSS
                            │
                            ▼
       On restart, recovery finds the log record and REPLAYS it.
                  ✅ DURABILITY HELD
```

### Why fsync Is Expensive

| Storage | Typical `fsync` cost | Max durable commits/sec (no batching) |
|---|---|---|
| Spinning HDD | ~5–10 ms (waits for a platter rotation) | ~100–200 |
| Consumer SSD | ~0.5–2 ms | ~500–2,000 |
| Enterprise NVMe with power-loss protection | ~50–200 µs | ~5,000–20,000 |

It's a **synchronous stall** — the committing thread can do nothing while it waits. This one call is usually the hard ceiling on a database's write throughput.

### Group Commit — Amortizing the Cost

Since the WAL is a single sequential file, many transactions' records sit adjacent in the log buffer. So the engine batches them into **one** `fsync`:

```
  Without group commit:              With group commit:
  ─────────────────────              ──────────────────
  T1 ─ fsync ─┐                      T1 ┐
  T2 ─ fsync ─┤  3 fsyncs            T2 ├─── one fsync ──► disk
  T3 ─ fsync ─┘                      T3 ┘
     3 × 1 ms = 3 ms                    1 × 1 ms = 1 ms
                                     (all 3 commits durable together)
```

Each transaction still waits for a real `fsync`, so durability is intact — the *cost* is just shared. This is why database write throughput can far exceed "1 ÷ fsync latency".

### The Tuning Knobs (and What You Trade Away)

**MySQL / InnoDB — `innodb_flush_log_at_trx_commit`:**

| Value | Behaviour at COMMIT | Survives process crash? | Survives OS crash / power loss? |
|:---:|---|:---:|:---:|
| **1** (default, ACID) | `write()` + `fsync()` the log | ✅ | ✅ |
| **2** | `write()` to OS cache only; `fsync` once per second | ✅ | ❌ lose up to ~1 s |
| **0** | `write()` + `fsync` once per second | ❌ lose up to ~1 s | ❌ lose up to ~1 s |

**PostgreSQL:** `synchronous_commit = on` (default) does the equivalent of value 1; `off` returns before the flush and can lose recent commits. `fsync = off` disables it entirely and risks **unrecoverable corruption**, not just lost transactions — never use it on data you care about.

```sql
SELECT @@innodb_flush_log_at_trx_commit;   -- MySQL: 1 means fully durable
SHOW synchronous_commit;                   -- PostgreSQL: on means fully durable
```

> **Related calls:** `fdatasync()` flushes the file's data but skips metadata that isn't needed for readability — slightly cheaper, and what many engines actually use. `O_DIRECT` (MySQL's `innodb_flush_method=O_DIRECT`) bypasses the OS page cache for **data pages** to avoid double-buffering with the buffer pool, but the **log still needs an explicit flush**.

> **Interview soundbite:** "`write()` only reaches the OS page cache — it's not durable. `fsync()` forces those bytes through the kernel cache and the drive's write cache onto persistent media, and blocks until they're there. It's the most expensive operation in the commit path, which is why engines batch transactions into a single `fsync` via group commit, and why relaxing `innodb_flush_log_at_trx_commit` to 2 buys throughput at the cost of losing up to a second of committed transactions in a power failure."

---

## Why We Need It — The Latency Gap

| Operation | Typical latency | Relative |
|---|---|---|
| Read from RAM (buffer pool hit) | ~100 ns | **1×** |
| Read from NVMe SSD | ~50–100 µs | ~1,000× slower |
| Random read from spinning HDD (seek) | ~10 ms | ~100,000× slower |

Three compounding reasons the buffer pool pays off:

1. **Locality** — real workloads are wildly skewed. A tiny "hot" subset (recent orders, active users, the upper levels of every B+ tree) serves most queries. Cache that subset and almost every read is a hit.
2. **Index pages stay resident** — a B+ tree's root and internal nodes are touched by *every* lookup. Keeping them in memory turns a 4-level index traversal from 4 disk reads into 1 (or 0).
3. **Write batching** — random page writes are the most expensive thing a disk does. Deferring and coalescing them is what lets a DBMS sustain thousands of writes per second.

---

## What If We Had No Buffer Pool?

Suppose every read and write went straight to disk:

| Consequence | Why |
|---|---|
| **Every row read = a disk I/O** | A query scanning 10,000 rows would do thousands of physical reads instead of a handful |
| **Index lookups become brutal** | A 4-level B+ tree = 4 separate disk reads *per row lookup*, every single time |
| **Every `UPDATE` = a random 16 KB disk write** | Updating one row 100 times = 100 physical writes to the same block |
| **Throughput collapses** | From ~10⁵–10⁶ page accesses/sec to ~10²–10⁴ — three to four orders of magnitude |
| **Joins and sorts become impractical** | A nested-loop join re-reads the inner table's pages repeatedly — with no cache, each pass hits the disk again |
| **Concurrency gets worse too** | Transactions hold locks while waiting on disk, so lock wait times explode and deadlocks become far more likely |
| **The disk wears out faster** | On SSDs, the write amplification from un-coalesced writes directly shortens device life |

**Concrete arithmetic:** a query touching 1,000 pages —

```
  With buffer pool (99% hit rate):  990 × 100 ns  +  10 × 100 µs  ≈  1.1 ms
  With no buffer pool:             1000 × 100 µs                  ≈  100 ms

  ~90× slower — and that's on fast SSD. On an HDD it would be ~10 seconds.
```

> **Bottom line:** without a buffer pool, a database is just a slow file system. It's the component that makes the difference between "a query is a memory operation" and "a query is a disk operation."

---

## Eviction — Which Page Gets Thrown Out?

The pool is finite, so when a new page must come in, an existing one must go. If the victim is **dirty**, it must be flushed to disk first; if **clean**, it can simply be dropped.

**Plain LRU** (evict the Least Recently Used page) is the starting point, but it has a fatal flaw: **one big table scan evicts the entire hot working set**, because thousands of pages that will never be read again get inserted at the "most recent" end.

**InnoDB's fix — a midpoint-insertion LRU** splits the list in two:

```
  ┌──────────── LRU List ─────────────┐
  │  YOUNG (~5/8)      │  OLD (~3/8)  │
  │  hot, frequently   │  newly read  │
  │  accessed pages    │  pages       │
  └────────────────────┴──────────────┘
                       ▲            │
        new page enters HERE        ▼ evicted from the tail
        (the midpoint, not the head)

  A page is promoted to YOUNG only if it is accessed AGAIN
  while sitting in the OLD sublist.
```

A one-off full scan's pages enter the old sublist, are never re-read, and get evicted from there — leaving the hot young pages untouched. PostgreSQL solves the same problem differently, with a clock-sweep algorithm and a small ring buffer for sequential scans.

---

## Sizing & Monitoring

| Engine | Typical setting | Note |
|---|---|---|
| MySQL / InnoDB | `innodb_buffer_pool_size` = **70–80% of RAM** on a dedicated server | InnoDB bypasses the OS cache, so it wants the memory itself |
| PostgreSQL | `shared_buffers` = **~25% of RAM** | Postgres deliberately leans on the OS page cache too |

**Measure the hit ratio** — aim for >99% on an OLTP workload:

```sql
-- MySQL: hit ratio = (1 - reads / read_requests) × 100
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';
--   Innodb_buffer_pool_read_requests  → logical reads (from the pool)
--   Innodb_buffer_pool_reads          → physical reads (had to hit disk)
```

> **Interview answer:** "The buffer pool is the DBMS's cache of disk pages. Reads check it first — a hit is served from RAM in nanoseconds, a miss costs a physical page read. Writes modify the page in memory, marking it dirty, and durability comes from `fsync`ing the WAL at commit, not from writing the data page; dirty pages are flushed in the background at checkpoints. Without it every row access would be a disk I/O and throughput would drop by orders of magnitude. The main tuning knobs are its size and the eviction policy — InnoDB uses a midpoint-insertion LRU specifically so a full table scan can't evict the hot working set."

---
---

# File System vs DBMS — Why Do We Need a DBMS at All?

🔗 **References:** [Javatpoint — DBMS vs File System](https://www.javatpoint.com/dbms-vs-files-system) · [GeeksforGeeks — Need for DBMS](https://www.geeksforgeeks.org/need-for-dbms/)

This is the **very first question** in most DBMS interviews, and it's really asking: *"do you understand what a database actually gives you that a folder of files does not?"*

---

## The Setup — How the Pre-DBMS World Worked

Before DBMSs, applications stored data in **flat files** (`.txt`, `.csv`, binary records) managed directly by the operating system's file system. Every program had to open the file, parse the bytes, find its record, and write it back itself.

Imagine a bank in the 1970s. Each department writes its own program and keeps its own file:

```
  📁 bank/
     ├── savings_accounts.txt      ← owned by the Savings dept program
     ├── loan_accounts.txt         ← owned by the Loans dept program
     └── customer_mailing.csv      ← owned by the Marketing dept program

  Alice's address is stored in ALL THREE files.
  Each file has a different format, written by a different programmer.
```

Every one of the problems below falls out of this picture.

---

## The 8 Problems with a Plain File System

### 1. Data Redundancy & Inconsistency

The same fact lives in multiple files, in different formats.

```
  savings_accounts.txt :  Alice | 12 MG Road, Pune
  loan_accounts.txt    :  Alice | 12 M.G. Rd, Pune 411001
  customer_mailing.csv  :  Alice | 45 FC Road, Pune     ← she moved; only this one updated

  Which address is correct? The database cannot tell you.
```

Redundancy wastes space; worse, it guarantees **inconsistency** the moment one copy is updated and the others aren't. A DBMS solves this by **normalization** (store each fact once — see [Database Normalization](#database-normalization--1nf-2nf-3nf--bcnf)) and **foreign keys**.

### 2. Difficulty in Accessing Data

A file system has **no query language**. Every new question needs a **new program**.

| Request from the manager | File system | DBMS |
|---|---|---|
| "List customers in Pune" | Write a new program to scan and filter the file | `SELECT * FROM customers WHERE city = 'Pune';` |
| "…now only those with balance > 50000" | Write *another* program | Add ` AND balance > 50000` |
| "…sorted by balance, top 10" | Write *another* program | Add ` ORDER BY balance DESC LIMIT 10` |

The file system gives you *bytes*; a DBMS gives you a **declarative language** plus a **query optimizer** that figures out *how* to get the answer efficiently.

### 3. Data Isolation (Scattered, Incompatible Data)

Data is spread across many files in many formats, so writing a program that combines them is painful — there's no `JOIN`. You'd hand-code the matching logic, and get it subtly wrong.

### 4. Integrity Problems

Business rules like "balance must never go below zero" live **inside application code**. Add a second program that forgets the rule, and the data is corrupt. There's no way to state the constraint once, centrally.

```
  File system:  every program must remember every rule 🙋
  DBMS:         the rule is declared once and enforced by the engine 🔒
```

```sql
CREATE TABLE accounts (
    acc_no  INT PRIMARY KEY,
    balance DECIMAL(12,2) NOT NULL CHECK (balance >= 0)   -- enforced for EVERY writer
);
```

A DBMS gives you domain, entity, referential, and key constraints — see [Integrity — The Rules](#integrity--the-rules).

### 5. Atomicity Problems

A file system has **no transactions**. If the machine crashes halfway through a multi-step operation, you're left with a corrupt half-state.

```
  Transfer ₹500 from A to B:
  Step 1: read A = 1000, write A = 500     ✅ done, flushed to file
  💥 CRASH
  Step 2: read B = 2000, write B = 2500    ❌ never happened

  Result: ₹500 has vanished from the bank. No way to undo Step 1.
```

A DBMS guarantees **all-or-nothing** via undo logs and `COMMIT`/`ROLLBACK` — see [ACID Properties](#acid-properties).

### 6. Concurrent Access Anomalies

Multiple programs writing the same file at once corrupt each other's work. There's no locking, no isolation.

```
  Balance = 1000. Two withdrawals of ₹500 run at the same time:

  P1: read 1000  ──────────► compute 500 ──► write 500
  P2:      read 1000 ──────────► compute 500 ──► write 500

  Two ₹500 withdrawals happened but the balance is 500, not 0.
  → LOST UPDATE (see the Concurrency Problems section)
```

A DBMS provides **locks, MVCC, and isolation levels** — see [Concurrency Control in DBMS](#concurrency-control-in-dbms).

### 7. Security & Access Control Problems

File-system permissions are **all-or-nothing per file**. If a clerk needs to read customer names, they get access to the whole file — salaries, account numbers and all. There's no way to say "this user may read these *columns* of these *rows*".

A DBMS gives per-object, per-operation privileges plus **views** to expose only a slice:

```sql
GRANT SELECT (name, city) ON customers TO clerk_role;
CREATE VIEW clerk_view AS SELECT name, city FROM customers WHERE branch = 'Pune';
```

See [GRANT / REVOKE Privileges](#mysql-grant--revoke-privileges-detailed) and [SQL Views](#sql-views).

### 8. No Backup, Recovery, or Crash Resilience

If a file is corrupted or a disk dies mid-write, you restore last night's copy and lose the day. A DBMS has **WAL, redo/undo logs, checkpoints, and point-in-time recovery** — see [Durability — How It's Achieved](#4-durability--how-its-achieved).

---

## File System vs DBMS — Side-by-Side Comparison

| Aspect | File System | DBMS |
|---|---|---|
| **Data access** | Custom program per query | Declarative SQL + query optimizer |
| **Redundancy** | High — same data in many files | Controlled via normalization & foreign keys |
| **Consistency** | Manual; breaks easily | Enforced by constraints |
| **Integrity rules** | Coded in every application | Declared once in the schema |
| **Transactions (ACID)** | ❌ None | ✅ Atomicity, Consistency, Isolation, Durability |
| **Concurrency** | ❌ No locking → corruption | ✅ Locks / MVCC / isolation levels |
| **Recovery after crash** | Restore from backup, lose recent work | Redo/undo logs, point-in-time recovery |
| **Security** | Per-file, all-or-nothing | Per-table / per-column / per-row, views, roles |
| **Relationships** | Hand-coded matching | Foreign keys + `JOIN` |
| **Data independence** | ❌ Change the format → rewrite every program | ✅ Physical & logical independence via abstraction levels |
| **Indexing / performance** | Manual, if at all | B-tree/hash indexes, statistics-driven optimizer |
| **Concurrent users** | Effectively one writer | Thousands |
| **Setup cost & overhead** | ✅ Almost none | ⚠️ Server, schema design, tuning, licence |
| **Best for** | Config, logs, media blobs, one-off scripts | Shared, structured, concurrently-updated business data |

---

## When a File System Is Still the Right Choice

An honest answer here scores well in interviews — "always use a database" is not true.

| Use a plain file when… | Why |
|---|---|
| Config / `.env` / YAML | Read once at startup; a DBMS is pure overhead |
| Application logs | Append-only, write-heavy, rarely queried by key |
| Images, video, PDFs (blobs) | Store the **bytes** on disk/S3, the **metadata** in the DBMS |
| Data interchange (CSV export, batch feeds) | The file *is* the transport format |
| A single-user throwaway script | Nothing to coordinate, no concurrency |

> **Important nuance:** a DBMS is **not an alternative to files — it's built on top of them.** MySQL stores InnoDB tablespaces as `.ibd` files; PostgreSQL keeps one file per relation. What the DBMS adds is the **layer of guarantees** (ACID, concurrency, constraints, query processing, recovery) over those raw files. Saying "a DBMS doesn't use files" is a common interview slip.

---

## Quick-Fire Q&A

| Question | Answer |
|---|---|
| **Why not just use a file system?** | No transactions, no concurrency control, no query language, no enforced integrity, weak security, painful recovery |
| **Single biggest advantage of a DBMS?** | **ACID transactions** — correctness under crashes and concurrent access |
| **What causes inconsistency in file systems?** | Redundancy — the same fact stored in several files, updated in only some |
| **What is data independence?** | Changing the physical storage or logical schema doesn't force a rewrite of every application |
| **Does a DBMS eliminate redundancy completely?** | No — it *controls* it. Some redundancy is kept deliberately (denormalization, replicas) |
| **Is a DBMS always faster?** | No. For a single sequential scan of one flat file, raw file I/O can be faster. The DBMS wins on selective queries, joins, and concurrent access |
| **Does a DBMS store data in files?** | Yes — it manages its own files and adds guarantees on top of them |
| **Main disadvantages of a DBMS?** | Cost, complexity, setup and tuning effort, higher memory/CPU footprint, and it becomes a single point of failure without replication |

> **Interview answer:** "A file system stores bytes; a DBMS stores *managed data*. Concretely, the file system gives me no transactions, no concurrency control, no declarative querying, and no way to enforce integrity centrally — so every application has to re-implement all of that, and any bug corrupts shared data. A DBMS centralizes those guarantees. I'd still use plain files for config, logs, and blobs, where none of those guarantees are worth the overhead — and it's worth remembering the DBMS itself is built on files."

---
---

# Database Partitioning

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
---

# Multikey / Composite Sharding (e.g. `user_id` + `order_id`)

**Sharding** splits one logical table across many physical databases or nodes. A **shard key** (or partition key) decides which node stores a row. **Multikey sharding** means the routing rule uses **more than one logical attribute** — often written as a composite such as `(user_id, order_id)` — but the critical detail is **how** those keys are combined: one column may define *which shard*, another may define *order within the shard*, or both may be hashed together (which changes query patterns completely).

---

## Two Different Meanings of "`user_id` + `order_id`"

### A) Good pattern — **Shard by `user_id` only**; `order_id` is local identity + sort key

All rows for a given user live on **one** shard. `order_id` (or `created_at`) is used for uniqueness and `ORDER BY`, not for picking the shard.

```
shard_id = hash(user_id) % NUM_SHARDS
```

**Effect on "last 5 orders for user 42":** One round-trip to the correct shard. The database can use an index on `(user_id, created_at DESC)` or `(user_id, order_id DESC)` and stop after 5 rows.

```sql
-- Router sends this to shard = hash(42) % N only
SELECT order_id, total, created_at
FROM orders
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 5;
```

This is the usual design for an **order history** feature.

### B) Risky pattern — **Shard by a function of both** (e.g. `hash(user_id, order_id)`)

Each *order* may land on a different shard even for the same user. No single shard has "all orders for user 42."

**Effect on "last 5 orders for user 42":** You must **scatter-gather**: run the same query (or index lookup) on **every** shard, collect up to 5 rows from each, then **merge and sort** in the application or a coordinator to produce the true "last 5 globally." Cost grows with shard count (latency, CPU, open connections).

```sql
-- Per shard k (app or proxy runs this N times)
SELECT order_id, total, created_at
FROM orders
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 5;
-- Then: merge all N result sets, sort by created_at, take top 5
```

So **`user_id` + `order_id` in the shard function** is rarely what you want for **per-user lists**; it can make sense when your hot path is always **point lookups** by both keys (e.g. "fetch this exact order") and you accept expensive user-scoped scans.

---

## Example Schema on One Shard (same SQL shape everywhere)

```sql
CREATE TABLE orders (
    user_id     BIGINT NOT NULL,
    order_id    BIGINT NOT NULL,      -- unique per user, or globally unique (Snowflake/UUID)
    total       DECIMAL(10,2),
    created_at  TIMESTAMP(3) NOT NULL,
    PRIMARY KEY (user_id, order_id),
    KEY idx_user_created (user_id, created_at DESC)
);
```

- **Shard by `user_id`:** Primary key and secondary index both start with `user_id` → efficient **single-shard** access for that user.
- If the **physical** DB is sharded, the router adds `AND user_id = ?` so each query is sent to one node.

---

## SQL Patterns After Sharding

| Need | Shard by `user_id` | Shard by `hash(user_id, order_id)` |
|---|---|---|
| Last 5 orders for user | One shard; `WHERE user_id = ? ORDER BY created_at DESC LIMIT 5` | All shards + merge |
| Order by id for known user | One shard; `WHERE user_id = ? AND order_id = ?` | Must know shard or query all (if only order_id known, **bad**) |
| Admin: recent orders globally | Expensive anyway; may need **OLAP** / search index / separate read model | Same problem |

**Lookup by `order_id` alone** when the shard key is only `user_id`: you need either a **secondary routing table** (`order_id → user_id` or `order_id → shard_id`), a **global index** service, or **duplicate storage** (e.g. order details keyed by `order_id` on a different sharding scheme). Otherwise the system does not know which shard to hit.

```sql
-- If you maintain order_id -> user_id in Redis or a tiny lookup table:
-- 1) SELECT user_id FROM order_index WHERE order_id = 9001;
-- 2) SELECT * FROM orders WHERE user_id = ? AND order_id = 9001;  -- single shard
```

---

## Practical Takeaways

1. **Align the shard key with your hottest queries.** For "my order history," that is almost always **`user_id` (or `tenant_id`)**, not `hash(user_id, order_id)`.
2. **`user_id` + `order_id` as a composite primary key** is normal; it does **not** mean both must participate in the **shard** function.
3. **Multikey sharding** that hashes both dimensions often optimizes **even spread** or **point reads** at the cost of **range/list queries** — document that trade-off in design reviews.
4. **Scatter-gather** for "last N per user" is correct but costly; cap shard count impact with caching, a **per-user recent orders** cache, or a **CQRS** read model fed by events.
