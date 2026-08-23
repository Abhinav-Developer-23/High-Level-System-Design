# 🗺️ DBMS Roadmap — by Love Babbar

> **Original Mindmap:** [Whimsical Board](https://whimsical.com/dbms-roadmap-by-love-babbar-FmUi8ffVop33t3MmpVxPCo)  
> **Author Channel:** [Love Babbar YouTube](https://www.youtube.com/c/LoveBabbar1)

---

## 📌 Interview Perspective & Overview

> [!NOTE]
> - **Tech Giants (FAANG / Big Tech):** Usually focus on core DBMS fundamentals like **Normalization**, **ACID properties (very important)**, **Transactions & Concurrency**, and **SQL Queries / Nested Queries**.
> - **Startups:** Focus heavily on **System Design** along with DBMS internals (scaling, replication, SQL vs NoSQL, caching). Best way to prepare for these is following the **System Design Primer (Database Section)**.

- **Primary Resource:** [SystemDesign Primer — Database Section](https://github.com/donnemartin/system-design-primer#database)

---

## 📑 Table of Contents

1. [Introduction to DBMS](#1-introduction-to-dbms)
2. [RDBMS Concepts & Architecture](#2-rdbms-concepts--architecture)
3. [Relational Model & Relational Algebra](#3-relational-model--relational-algebra)
4. [SQL (Structured Query Language)](#4-sql-structured-query-language)
5. [Relational Database Design & Normalization](#5-relational-database-design--normalization)
6. [Storage & File Structure](#6-storage--file-structure)
7. [Transaction Management](#7-transaction-management)
8. [Concurrency Control](#8-concurrency-control)
9. [Deadlock Management](#9-deadlock-management)
10. [Must Do — System Design & Advanced Database Concepts](#10-must-do--system-design--advanced-database-concepts)

---

## 1. Introduction to DBMS

- **What is a Database?**  
  🔗 [Javatpoint — What is Database](https://www.javatpoint.com/what-is-database)
- **What is DBMS?**  
  🔗 [Guru99 — What is DBMS?](https://www.guru99.com/what-is-dbms.html)
- **Why do we need DBMS?**  
  🔗 [GeeksforGeeks — Need for DBMS](https://www.geeksforgeeks.org/need-for-dbms/)
- **File Management System vs DBMS**  
  🔗 [Javatpoint — DBMS vs File System](https://www.javatpoint.com/dbms-vs-files-system)
- **What is Database Admin (DBA) & its Functions?**  
  🔗 [GeeksforGeeks Practice — Functions of a DBA](https://practice.geeksforgeeks.org/problems/what-are-the-functions-of-a-dba)
- **Database 2-Tier vs 3-Tier Architecture**  
  🔗 [GeeksforGeeks — 2-Tier vs 3-Tier Database Architecture](https://www.geeksforgeeks.org/difference-between-two-tier-and-three-tier-database-architecture/)
- **Database Languages (DDL, DQL, DML, DCL, TCL)**  
  🔗 [GeeksforGeeks — SQL DDL, DQL, DML, DCL, TCL Commands](https://www.geeksforgeeks.org/sql-ddl-dql-dml-dcl-tcl-commands/)
  - **DDL** (Data Definition Language)
  - **DML** (Data Manipulation Language)
  - **DCL** (Data Control Language)
  - **TCL** (Transaction Control Language)
- **Important Terms (Instance, Schema, Sub-Schema)**  
  🔗 [WhatIsDBMS — Instances, Schema and Sub-Schema in DBMS with Examples](https://whatisdbms.com/instances-schema-and-sub-schema-in-dbms-with-examples/)
- **How DBMS is Implemented?** `[HOMEWORK]`
- **Data Abstraction in DBMS & 3 Levels of Data Abstraction**  
  🔗 [AfterAcademy — What is Data Abstraction in DBMS and 3 Levels](https://afteracademy.com/blog/what-is-data-abstraction-in-dbms-and-what-are-its-three-levels)
  - Physical / Internal Level
  - Conceptual / Logical Level
  - View / External Level

---

## 2. RDBMS Concepts & Architecture

- **What is RDBMS & How is it Stored in Memory? (B-Trees / Internal Structures)**  
  ▶️ [B-Tree (Abdul Bari)](https://www.youtube.com/watch?v=aZjYr87r1b8&t=1657s)  
  ▶️ [B Tree Insert and Delete](https://www.youtube.com/watch?v=ownO77M4SWI)  
  📚 [B-Trees & DB Indexes (PlanetScale)](https://planetscale.com/blog/btrees-and-database-indexes)  
  🕹️ [Interactive B+ Tree Visualizer](https://bplustree.app/)  
  🕹️ [Interactive B Tree Visualizer](https://btree.app/)
- **What is the meaning of the word "Relational" in RDBMS?**  
  📝 [DBMS1.md — What Is the Meaning of the Word "Relational" in RDBMS?](DBMS1.md#what-is-the-meaning-of-the-word-relational-in-rdbms)
- **Degree of Relation / Cardinality / Relationship Types (1:1, 1:M, M:M)**  
  🔗 [ER Relationship Types — Binary](https://medium.com/@kushanaam/er-relationship-types-binary-8cd84cfdb983)
  - $1:1$ (One-to-One)
  - $1:M$ (One-to-Many)
  - $M:M$ (Many-to-Many)
- **Keys in Relational Model**  
  🔗 [GeeksforGeeks — Types of Keys in Relational Model (Candidate, Super, Primary, Alternate, Foreign, Secondary)](https://www.geeksforgeeks.org/types-of-keys-in-relational-model-candidate-super-primary-alternate-and-foreign/)
  - Super Key
  - Candidate Key
  - Primary Key
  - Alternate Key
  - Foreign Key
  - Secondary Key
- **Database Schema (Physical vs Logical Schema & Schema Diagrams)**  
  🔗 [Tutorialspoint — DBMS Data Schemas](https://www.tutorialspoint.com/dbms/dbms_data_schemas.htm)

---

## 3. Relational Model & Relational Algebra

- **ER Model to Relational Model Conversion**  
  🔗 [GeeksforGeeks — Mapping from ER Model to Relational Model](https://www.geeksforgeeks.org/mapping-from-er-model-to-relational-model/)

---

## 4. SQL (Structured Query Language)

- **What is SQL?**  
  🔗 [W3Schools — SQL Introduction](https://www.w3schools.com/sql/sql_intro.asp)
- **Difference between SQL and MySQL**  
  🔗 [upGrad — SQL vs MySQL](https://www.upgrad.com/blog/sql-vs-mysql/)
- **Important SQL Keywords**  
  🔗 [EDUCBA — SQL Keywords](https://www.educba.com/sql-keywords/)
- **SQL Cheatsheet**  
  🔗 [EDUCBA — SQL Cheat Sheet](https://www.educba.com/cheat-sheet-sql/?source=leftnav)
- **Composite Key in SQL**  
  🔗 [EDUCBA — Composite Key in SQL](https://www.educba.com/composite-key-in-sql/?source=leftnav)
- **What is a JOIN & its Types?**  
  🔗 [GeeksforGeeks — SQL Joins (Inner, Left, Right, Full, Self)](https://www.geeksforgeeks.org/sql-join-set-1-inner-left-right-and-full-joins/)
  - Inner Join
  - Left Join
  - Right Join
  - Full Join
  - Self Join
- **What is a View?**  
  🔗 [GeeksforGeeks — SQL Views](https://www.geeksforgeeks.org/sql-views/)
- **What is a Trigger?**  
  🔗 [GeeksforGeeks — SQL Triggers](https://www.geeksforgeeks.org/sql-trigger-student-database/)
- **Difference Between Primary Key and Unique Key**  
  🔗 [GeeksforGeeks — Difference between Primary Key and Unique Key](https://www.geeksforgeeks.org/difference-between-primary-key-and-unique-key/)
- **What is SQL Injection?**  
  🔗 [W3Schools — SQL Injection](https://www.w3schools.com/sql/sql_injection.asp)
- **DELETE vs TRUNCATE (vs DROP)**  
  🔗 [GeeksforGeeks — Difference between DELETE and TRUNCATE](https://www.geeksforgeeks.org/difference-between-delete-and-truncate/)
- **SQL Privileges (GRANT & REVOKE)**  
  🔗 [GeeksforGeeks — MySQL GRANT and REVOKE Privileges](https://www.geeksforgeeks.org/mysql-grant-revoke-privileges/)
- **What is a Subquery? (Nested & Correlated Subqueries)**  
  🔗 [Tutorialspoint — SQL Subqueries](https://www.tutorialspoint.com/sql/sql-sub-queries.htm)
- **Clustered vs Non-Clustered Indexes**  
  🔗 [Guru99 — Clustered vs Non-Clustered Index](https://www.guru99.com/clustered-vs-non-clustered-index.html)
- **What is a Cursor in SQL?**  
  🔗 [GeeksforGeeks — What is Cursor in SQL](https://www.geeksforgeeks.org/what-is-cursor-in-sql/)
- **What is an Index in DBMS & its Types?**  
  🔗 [Guru99 — Indexing in Databases](https://www.guru99.com/indexing-in-database.html)

### 💡 Practice Query Questions `[DO BY YOURSELF]`
1. Write an SQL query to get the third maximum salary of an employee from a table named `employee_table`.
2. Write an SQL query to find names of employees starting with `'A'`.
3. How can you create an empty table from an existing table?
4. How to fetch common records from two tables?
5. How to fetch alternate records from a table?
6. How to select unique records from a table?
7. What is the command used to fetch the first 5 characters of a string?
8. Which operator is used in a query for pattern matching?

---

## 5. Relational Database Design & Normalization

- **Features of Good Relational Design**  
  🔗 [Micro Focus — Features of Good Relational Design](https://www.microfocus.com/documentation/xdbc/win20/GUID-82D58958-278F-482C-B76F-AAF94A28DCCF.html)
- **Functional Dependency & Types (Trivial, Non-Trivial, Full, Partial, Transitive)**  
  🔗 [Guru99 — Functional Dependency in DBMS](https://www.guru99.com/dbms-functional-dependency.html)
- **What is Normalization?**  
  🔗 [Guru99 — Database Normalization](https://www.guru99.com/database-normalization.html)
- **Purpose of Normalization**  
  🔗 [Medium — What is the Purpose of Database Normalisation?](https://medium.com/@bbrumm/what-is-the-purpose-of-database-normalisation-8070b2948d70)
- **3 Anomalies Resolved by Normalization (Insertion, Deletion, Update)**  
  🔗 [DBA StackExchange — How does Normalization fix the three types of update anomalies?](https://dba.stackexchange.com/questions/194631/how-does-normalization-fix-the-three-types-of-update-anomalies)
- **Normal Forms (Definitions, Purpose, and Conversion Steps):**
  - **1NF (First Normal Form):** 🔗 [GeeksforGeeks — 1NF](https://www.geeksforgeeks.org/first-normal-form-1nf/)
  - **2NF (Second Normal Form):** 🔗 [GeeksforGeeks — 2NF](https://www.geeksforgeeks.org/second-normal-form-2nf/)
  - **3NF (Third Normal Form):** 🔗 [GeeksforGeeks — 3NF](https://www.geeksforgeeks.org/third-normal-form-3nf/)
  - **BCNF (Boyce-Codd Normal Form):** 🔗 [GeeksforGeeks — BCNF](https://www.geeksforgeeks.org/boyce-codd-normal-form-bcnf/)

---

## 6. Storage & File Structure

- **Storage System in DBMS (Primary, Secondary, Tertiary Storage)**  
  🔗 [Tutorialspoint — DBMS Storage System](https://www.tutorialspoint.com/dbms/dbms_storage_system.htm)
- **File Structure in DBMS (Heap, Sorted, Hash Organizations)**  
  🔗 [Tutorialspoint — DBMS File Structure](https://www.tutorialspoint.com/dbms/dbms_file_structure.htm)

---

## 7. Transaction Management

- **What is a Transaction?**  
  🔗 [Tutorialspoint — DBMS Transaction](https://www.tutorialspoint.com/dbms/dbms_transaction.htm)
- **States of a Transaction (Active, Partially Committed, Committed, Failed, Aborted, Terminated)**  
  🔗 [Gate Vidyalay — Transaction States in DBMS](https://www.gatevidyalay.com/transaction-states-in-dbms/)
- **Important TCL Commands (COMMIT, ROLLBACK, SAVEPOINT)**  
  🔗 [StudyTonight — TCL Commands in DBMS](https://www.studytonight.com/dbms/tcl-command.php)
- **ACID Properties (Atomicity, Consistency, Isolation, Durability)**  
  🔗 [GeeksforGeeks — ACID Properties in DBMS](https://www.geeksforgeeks.org/acid-properties-in-dbms/)
- **How to Implement Atomicity & Durability (Shadow Copy / WAL Scheme)?**  
  🔗 [Ashutosh Tripathi — Implementation of Atomicity and Durability using Shadow Copy](https://ashutoshtripathi.com/2017/11/27/implementation-of-atomicity-and-durability-using-shadow-copy/)

---

## 8. Concurrency Control

- **Concurrent Transactions & Concurrency Problems**  
  🔗 [GeeksforGeeks — Concurrency Problems in DBMS Transactions](https://www.geeksforgeeks.org/concurrency-problems-in-dbms-transactions/)
  - *Problems:* Lost Update Conflict ($W-W$), Dirty Read Problem ($W-R$), Unrepeatable Read Problem ($R-W$), Incorrect Summary Problem / Phantom Read
  - *Advantages:* Reduced Wait Time, High Throughput, High Resource Utilization
- **Schedules & Types (Serial, Complete, Recoverable, Cascadeless, Strict)**  
  🔗 [GeeksforGeeks — Types of Schedules in DBMS](https://www.geeksforgeeks.org/types-of-schedules-in-dbms/)
- **Conflict Serializability & Conflict Operations**  
  🔗 [Javatpoint — Conflict Serializable Schedule in DBMS](https://www.javatpoint.com/dbms-conflict-serializable-schedule)
- **Concurrency Control Protocols & Lock-Based Protocols**  
  🔗 [Tutorialspoint — DBMS Concurrency Control](https://www.tutorialspoint.com/dbms/dbms_concurrency_control.htm)
  - Shared Lock ($S$-Lock / Read Lock)
  - Exclusive Lock ($X$-Lock / Write Lock)
  - **Two-Phase Locking Protocol (2PL)** `[IMP]` (Strict 2PL, Rigorous 2PL, Conservative 2PL)

---

## 9. Deadlock Management

- **What is Deadlock? (Examples, 4 Necessary Conditions)**  
  🔗 [GeeksforGeeks — Deadlock in DBMS](https://www.geeksforgeeks.org/deadlock-in-dbms/)
  - Deadlock Detection `[HOMEWORK]`
  - Prevention Conditions: *Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait*
- **Timestamp & Deadlock Prevention Schemes**  
  🔗 [GeeksforGeeks — Timestamp and Deadlock Prevention Schemes in DBMS](https://www.geeksforgeeks.org/introduction-to-timestamp-and-deadlock-prevention-schemes-in-dbms/)
  - **Wait-Die Scheme** (Non-preemptive)
  - **Wound-Wait Scheme** (Preemptive)
  - **Timeout-Based Scheme**
- **What is Starvation and its Causes?**  
  🔗 [GeeksforGeeks — Starvation in DBMS](https://www.geeksforgeeks.org/starvation-in-dbms/)
- **Deadlock Recovery Methods**  
  🔗 [GeeksforGeeks — Recovery from Deadlock](https://www.geeksforgeeks.org/recovery-from-deadlock-in-operating-system/)
  - Selection of Victim
  - Rollback (Total vs Partial Rollback)
  - Starvation Avoidance

---

## 10. Must Do — System Design & Advanced Database Concepts

- **SQL vs NoSQL**  
  🔗 [MongoDB — NoSQL Explained: NoSQL vs SQL](https://www.mongodb.com/nosql-explained/nosql-vs-sql)
- **Which Modern Database Is Right for Your Use Case?**  
  🔗 [Xplenty / Integrate.io — Which Modern Database is Right for You?](https://www.xplenty.com/blog/which-database/)
- **Understanding Database Scaling Patterns**  
  🔗 [freeCodeCamp — Understanding Database Scaling Patterns](https://www.freecodecamp.org/news/understanding-database-scaling-patterns/)
- **A Beginner's Guide to CAP Theorem for Data Engineering**  
  🔗 [Analytics Vidhya — CAP Theorem Guide](https://www.analyticsvidhya.com/blog/2020/08/a-beginners-guide-to-cap-theorem-for-data-engineering/)
- **Scaling SQL and NoSQL Databases**  
  🔗 [Medium (Better Programming) — Scaling SQL and NoSQL Databases](https://medium.com/better-programming/scaling-sql-nosql-databases-1121b24506df)
- **What Database to Use? (Decision Guide)**  
  🔗 [Jon Lamere — Database Comparison & Guide](http://jlamere.github.io/databases/)
- **In-Memory Databases & Efficient Persistence**  
  🔗 [Medium — What an In-Memory Database is & How it Persists Data](https://medium.com/@denisanikin/what-an-in-memory-database-is-and-how-it-persists-data-efficiently-f43868cff4c1)
- **Graph Databases**  
  🔗 [Neo4j — Graph Database Developer Guide](https://neo4j.com/developer/graph-database/)
- **In-Depth Indexing at a Glance `[Optional]`**  
  🔗 [freeCodeCamp — Database Indexing at a Glance](https://www.freecodecamp.org/news/database-indexing-at-a-glance-bb50809d48bd/)
- **Master-Slave Database Concept for Beginners**  
  🔗 [DataDrivenInvestor — Master-Slave Database Concept](https://www.datadriveninvestor.com/2020/05/28/the-master-slave-database-concept-for-beginners/)
- **Master-Master vs Master-Slave Architecture**  
  🔗 [Intellipaat — Master-Master vs Master-Slave Architecture](https://intellipaat.com/community/6605/master-master-vs-master-slave-database-architecture)
- **ACID vs BASE: The Shifting pH of Database Transaction Processing**  
  🔗 [Dataversity — ACID vs BASE Transaction Processing](https://www.dataversity.net/acid-vs-base-the-shifting-ph-of-database-transaction-processing/)
