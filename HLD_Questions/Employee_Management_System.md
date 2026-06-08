# High Level Design: Employee Management System (EMS)

## 1. Problem Statement
Design an internal Employee Management System (like Workday, BambooHR, or internal tools used by large corporations) to manage the employee lifecycle, organizational hierarchy, department data, payroll integrations, and directory search.

---

## 2. Requirements

### Functional Requirements
- **Employee Lifecycle Management:** Onboard, update, promote, and offboard employees.
- **Directory & Search:** Fast fuzzy search for employees by name, skills, location, department, or title.
- **Organizational Hierarchy:** Fetch and display reporting lines (managers, direct reports, peers).
- **Access Control (RBAC):** Role-based access control (Global Admin, HR Admin, Manager, Employee).
- **Core HR & Payroll Integration:** Maintain salary history, payment details, and export to external payroll providers.
- **Leave & Attendance Management:** Request, approve, and track time-off balances.
- **Audit Trails:** Securely track all changes to sensitive employee data (salary changes, promotions, manager reassignments).
- **Document Management:** Store and retrieve employee documents (resumes, tax forms, offer letters).

### Non-Functional Requirements
- **High Availability:** System should be highly available, especially during working hours (99.9% uptime).
- **Security & Privacy:** Employee data (PII, salary) must be encrypted at rest and in transit.
- **Low Latency for Search:** Employee directory searches should be `< 100ms`.
- **Consistency:** Eventual consistency is fine for search, but strong consistency is strictly required for payroll, roles, and leave deductions.
- **Read-Heavy System:** The ratio of reads (viewing profiles, searching) to writes (updating details, onboarding) is approximately 100:1.

---

## 3. Back-of-the-Envelope Calculations (Capacity Estimation)

Assumptions: A large enterprise with **100,000 employees**.

**Scale & Traffic:**
- **Active Users:** ~50,000 daily active users.
- **Reads:** `50,000 users * 10 profile/search views per day = 500,000 reads/day`.
  - Average QPS = `500,000 / 86400 ≈ 6 QPS`
  - Peak QPS (during morning hours) = `~50 QPS`
- **Writes:** Very low (onboarding, leaves, profile updates) -> `< 1 QPS`.
- **System Profile:** Extremely Read-Heavy (100:1 Read-to-Write ratio).

**Storage Estimation:**
- **Relational Data (PostgreSQL):** Basic profile data & metadata: ~2KB per employee -> `100,000 * 2KB = 200 MB`.
- **Audit Logs:** Fast growing, ~100 bytes per log, 1000 actions/day -> `36 MB/year`.
- **Blob Storage (S3/GCS):** Profile pictures & PDF documents: ~5MB per employee -> `100,000 * 5MB = 500 GB`.
- **Network Bandwidth:** For 50 QPS returning 2KB JSON payloads -> `100 KB/sec` (negligible).

**Conclusion:** 
Traffic and storage are not massive. The core system challenge lies in **data complexity (hierarchy trees)**, **strict RBAC/security**, and **consistency for payroll/HR events**.

---

## 4. API Design

### 1. Create/Onboard Employee
**`POST /v1/employees`**
- **Payload:** 
  ```json
  {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@company.com",
    "department_id": "DEP-123",
    "manager_id": "EMP-456",
    "role_id": "ROLE-789"
  }
  ```
- **Response:** `201 Created` with `{"id": "EMP-101", "status": "ACTIVE"}`

### 2. Get Employee Profile
**`GET /v1/employees/{employee_id}`**
- **Response:** `200 OK`
  ```json
  {
    "id": "EMP-101",
    "name": "John Doe",
    "title": "Software Engineer",
    "manager": {"id": "EMP-456", "name": "Jane Smith"},
    "department": "Engineering"
  }
  ```

### 3. Search Directory
**`GET /v1/employees/search`**
- **Query Params:** `?q=John+Doe&department=Engineering&limit=10&offset=0`
- **Response:** `200 OK` (Returns an array of matched employee summaries)

### 4. Fetch Hierarchy (Up or Down)
**`GET /v1/employees/{employee_id}/hierarchy`**
- **Query Params:** `?direction=down&depth=2` (Used to render org charts)
- **Response:** `200 OK` (Returns nested JSON tree of direct and indirect reports)

---

## 5. Database Schema & Selection

**Primary Database: Relational Database (PostgreSQL)**
Why? 
- ACID properties are critical for HR and Payroll data.
- Structured relationships (Departments, Teams, Roles).
- Flexible support for JSONB (to store custom unstructured fields like skills or certifications if needed).

### Tables

**Employee Table**
- `id` (UUID, Primary Key)
- `first_name` (VARCHAR)
- `last_name` (VARCHAR)
- `email` (VARCHAR, Unique, Indexed)
- `phone` (VARCHAR)
- `department_id` (UUID, Foreign Key)
- `manager_id` (UUID, Foreign Key) -> *Self-referencing for hierarchy*
- `role_id` (UUID, Foreign Key)
- `status` (ENUM: ACTIVE, ONLEAVE, TERMINATED)
- `created_at` (TIMESTAMP)

**Department Table**
- `id` (UUID, Primary Key)
- `name` (VARCHAR)
- `head_id` (UUID, FK to Employee)

**Document (Salary Slips, Tax Forms, Offer Letters)**
- `id` (UUID, Primary Key)
- `employee_id` (UUID, Foreign Key)
- `document_type` (ENUM: SALARY_SLIP, TAX_FORM, OFFER_LETTER)
- `file_name` (VARCHAR)
- `s3_object_key` (VARCHAR) -> *Crucial for locating the file in the bucket*
- `uploaded_at` (TIMESTAMP)

**Audit_Log** (Important for Compliance)
- `id` (UUID)
- `entity_id` (UUID - e.g., Employee ID)
- `action` (VARCHAR - e.g., "SALARY_UPDATE", "ROLE_CHANGE")
- `previous_value` (JSONB)
- `new_value` (JSONB)
- `performed_by` (UUID - Admin/HR ID)
- `timestamp` (TIMESTAMP)

---

## 6. High Level Architecture

```text
[Client Web/Mobile]
       |
  [Load Balancer / API Gateway] ----- [Auth Service / Identity Provider (Okta/AD)]
       |
     (API)
       |
  +-------------------------------------------------------------+
  |                   App Application Services                  |
  |                                                             |
  |  [Employee Svc]   [Directory/Search Svc]   [Hierarchy Svc]  |
  +-------------------------------------------------------------+
       |                        |                     |
   (Writes/Reads)        (Search Queries)         (Graph Traversal / CTE)
       |                        |                     |
[Primary DB (Postgres)] <---+ [ElasticSearch]    [Redis (Caching)]
       |                    |
   (CDC via Debezium)       |
       |                    |
  [Kafka Event Bus] --------+
       |
  [Audit Log Sink / Analytics / Payroll Services]
```

---

## 7. Deep Dives & Core Mechanisms

### 7.1. Fast Directory Search (ElasticSearch)
- PostgreSQL `LIKE` or `ILIKE` queries will not scale well for fuzzy matching, typos, and multifield search (e.g., searching "Java Engineer NY").
- **Solution:** We use **ElasticSearch**. 
- **Synchronization:** Whenever an employee record is created or updated in Postgres, an event is emitted (either via application-level events or Change Data Capture tools like **Debezium**). Kafka consumes this event and updates the ElasticSearch index asynchronously to provide near real-time search.

### 7.2. Organizational Hierarchy Queries
Finding the management chain or direct reports involves traversing a tree structure.
- **SQL CTE (Common Table Expressions):** In PostgreSQL, `WITH RECURSIVE` queries can efficiently traverse the `manager_id` self-referential chain up to a certain depth.

  **Example Query: Fetch all direct and indirect reports for a Manager (Downward):**
  ```sql
  WITH RECURSIVE subordinates AS (
      -- Base Case: Direct reports assigned to the target manager
      SELECT id, first_name, last_name, manager_id, 1 as depth
      FROM Employee
      WHERE manager_id = 'TARGET_MANAGER_UUID'
      
      UNION ALL
      
      -- Recursive Step: Reports of those reports
      SELECT e.id, e.first_name, e.last_name, e.manager_id, s.depth + 1
      FROM Employee e
      INNER JOIN subordinates s ON s.id = e.manager_id
      WHERE s.depth < 5 -- Safety limit for maximum depth (e.g., max 5 levels down)
  )
  SELECT * FROM subordinates;
  ```

- **Caching:** Since org hierarchies do not change every minute, the hierarchy view for an employee or department is heavily cached in **Redis** (e.g., TTL of 24 hours, actively invalidated upon manager reassignment).
- **Graph DB (Optional):** If the hierarchy rules are incredibly complex (matrix organizations, multiple reporting lines), a Graph DB like Neo4j can be considered, but Postgres Recursive CTEs are generally sufficient for standard trees.

### 7.3. Audit Trails & Event Sourcing
Because it's an HR system, tracking "who changed what and when" is legally required.
- **Approach:** We implement the Outbox Pattern or use CDC (Debezium). Every modification to the `Employee` table is recorded in an `Audit_Log` table. Furthermore, events are published to Kafka for downstream consumers (like the Payroll system to adjust payouts based on a title change).

### 7.4. Role Based Access Control (RBAC)
- A regular employee can only invoke `GET /v1/employees/self` or basic public directory fields.
- HR Admins can invoke `POST /v1/employees` or `PATCH` salary info.
- This is enforced at the API Gateway or Middleware layer by validating JWT scopes against the user's role mapping.

### 7.5. Document Management & Salary Slips (S3 Integration)
Since storing binary files (PDFs, images) directly in a relational database is an anti-pattern (causes database bloat and performance degradation), we use **Object Storage (Amazon S3)**.

- **Storage Flow:** 
  1. The Payroll system generates the Monthly Salary Slip (PDF).
  2. The Employee Svc uploads the PDF to an S3 Bucket (e.g., `s3://company-hr-documents/{employee_id}/salary_slips/2026_04.pdf`).
  3. A new row is inserted into the `Document` Postgres table containing the `s3_object_key` and mapping it to the `employee_id`.
  
- **Retrieval via Pre-Signed URLs:**
  - Salary slips contain highly sensitive PII. The S3 bucket is **private** and strictly blocked from public access.
  - When an employee requests their salary slip (`GET /v1/employees/self/documents/{doc_id}`), the Employee Service verifies their identity (RBAC).
  - The Service queries the `Document` table to find the corresponding `s3_object_key`.
  - The Service uses the AWS SDK to generate a **Pre-Signed URL** (which is a temporary, securely signed URL valid for only ~5-15 minutes).
  - The client receives the Pre-Signed URL and downloads the PDF directly from S3, offloading the heavy network bandwidth from our API servers.
