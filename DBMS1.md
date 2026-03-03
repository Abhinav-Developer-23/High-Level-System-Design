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

### ACID Properties (Why Transactions Matter)

Transactions guarantee four critical properties:

| Property | Meaning | TCL Role |
|----------|---------|----------|
| **A**tomicity | All-or-nothing — either all operations succeed, or none do | `COMMIT` / `ROLLBACK` |
| **C**onsistency | Database moves from one valid state to another | Constraints + transaction logic |
| **I**solation | Concurrent transactions don't interfere with each other | Isolation levels (Read Committed, etc.) |
| **D**urability | Once committed, changes survive crashes/power failures | `COMMIT` flushes to disk |

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

# Three Relationship Types in ER Modeling

Entity-Relationship (ER) diagrams model how entities relate to each other. In practice, almost every design choice — keys, foreign keys, junction tables — follows from the **type of relationship** and whether participation is optional or mandatory.

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

---
---

# Transactions in DBMS

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

# Concurrency Problems (Without Proper Isolation)

When multiple transactions run concurrently WITHOUT proper isolation, these problems can occur:

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
| **Shared Lock** | S | Multiple readers simultaneously | `SELECT` (read) |
| **Exclusive Lock** | X | Only one writer, blocks everyone | `UPDATE`, `DELETE` (write) |

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

### Handling Deadlocks

| Method | How It Works |
|--------|-------------|
| **Detection** | Build a wait-for graph. If cycle → deadlock. Kill one transaction (the "victim"). |
| **Prevention** | Use rules to prevent circular waits before they happen |
| **Timeout** | If a transaction waits too long, assume deadlock → rollback |

### Prevention Schemes

| Scheme | Rule | Action |
|:---:|------|--------|
| **Wait-Die** | Older waits, younger dies | If Ti is older than Tj → Ti waits. If Ti is younger → Ti is rolled back (dies). |
| **Wound-Wait** | Older wounds, younger waits | If Ti is older than Tj → Tj is rolled back (wounded). If Ti is younger → Ti waits. |

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

# Types of Schedules in DBMS

A **schedule** is the chronological order in which operations (read/write) of multiple concurrent transactions are executed. Choosing the right schedule ensures correctness and consistency.

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
