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
2. [Transaction Management](#2-transaction-management)
3. [Concurrency Control](#3-concurrency-control)
4. [Deadlock Management](#4-deadlock-management)
5. [Must Do — System Design & Advanced Database Concepts](#5-must-do--system-design--advanced-database-concepts)

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

## 2. Transaction Management

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

## 3. Concurrency Control

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

## 4. Deadlock Management

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

## 5. Must Do — System Design & Advanced Database Concepts

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
