## Notification Template System

> Templates allow the system to maintain **consistent, reusable, and dynamic** notification messages across all channels. Instead of hardcoding content in every request, clients reference a `templateId` and pass dynamic variables — the system renders the final message.

### Template Database Schema

#### `notification_templates` Table

| Column | Type | Description |
|---|---|---|
| `template_id` | `UUID` (PK) | Unique identifier for the template |
| `template_name` | `VARCHAR(255)` | Human-readable name (e.g., `order_confirmation`) |
| `category` | `ENUM` | `transactional`, `promotional`, `system_alert` |
| `channel` | `ENUM` | `email`, `sms`, `push`, `in_app` |
| `subject_template` | `TEXT` | Subject line with placeholders (email/push) |
| `body_template` | `TEXT` | Body content with placeholders (supports HTML for email) |
| `language` | `VARCHAR(10)` | Locale code (`en`, `hi`, `es`, etc.) |
| `version` | `INT` | Template version for A/B testing and rollbacks |
| `is_active` | `BOOLEAN` | Whether this template version is currently active |
| `created_by` | `VARCHAR(100)` | Creator (admin/system) |
| `created_at` | `TIMESTAMP` | Creation timestamp |
| `updated_at` | `TIMESTAMP` | Last update timestamp |

#### `template_audit_log` Table

| Column | Type | Description |
|---|---|---|
| `audit_id` | `UUID` (PK) | Unique identifier |
| `template_id` | `UUID` (FK) | References `notification_templates.template_id` |
| `action` | `ENUM` | `created`, `updated`, `activated`, `deactivated` |
| `old_version` | `INT` | Previous version number |
| `new_version` | `INT` | New version number |
| `changed_by` | `VARCHAR(100)` | Who made the change |
| `changed_at` | `TIMESTAMP` | When the change was made |

---

### Sample Template Records

#### Email Template — Order Confirmation

```json
{
  "template_id": "tmpl-001",
  "template_name": "order_confirmation",
  "category": "transactional",
  "channel": "email",
  "subject_template": "Order Confirmed — #{{order_id}}",
  "body_template": "<html><body><h1>Hi {{user_name}},</h1><p>Your order <b>#{{order_id}}</b> worth <b>{{currency}}{{order_total}}</b> has been confirmed!</p><p>Track your order: <a href='{{tracking_url}}'>Click here</a></p></body></html>",
  "language": "en",
  "version": 2,
  "is_active": true
}
```

#### SMS Template — OTP Verification

```json
{
  "template_id": "tmpl-002",
  "template_name": "otp_verification",
  "category": "transactional",
  "channel": "sms",
  "subject_template": null,
  "body_template": "Your verification code is {{otp_code}}. Valid for {{expiry_minutes}} minutes. Do not share this with anyone.",
  "language": "en",
  "version": 1,
  "is_active": true
}
```

#### Push Template — Flash Sale

```json
{
  "template_id": "tmpl-003",
  "template_name": "flash_sale_alert",
  "category": "promotional",
  "channel": "push",
  "subject_template": "🔥 {{sale_name}} is LIVE!",
  "body_template": "Up to {{discount_percent}}% off on {{category}}. Ends in {{hours_left}} hours. Shop now!",
  "language": "en",
  "version": 1,
  "is_active": true
}
```

---

### Template Management APIs

#### Create Template

```
POST /api/v1/templates
```

**Request Body:**
```json
{
  "template_name": "password_reset",
  "category": "transactional",
  "channel": "email",
  "subject_template": "Reset Your Password — {{app_name}}",
  "body_template": "<html><body><p>Hi {{user_name}},</p><p>Click <a href='{{reset_link}}'>here</a> to reset your password. This link expires in {{expiry_minutes}} minutes.</p></body></html>",
  "language": "en",
  "variables": [
    { "variable_name": "user_name", "variable_type": "string", "is_required": true },
    { "variable_name": "reset_link", "variable_type": "url", "is_required": true },
    { "variable_name": "expiry_minutes", "variable_type": "number", "is_required": true, "default_value": "15" },
    { "variable_name": "app_name", "variable_type": "string", "is_required": false, "default_value": "MyApp" }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "template_id": "tmpl-004",
  "version": 1,
  "message": "Template created successfully"
}
```

#### Update Template (Creates New Version)

```
PUT /api/v1/templates/{template_id}
```

**Request Body:**
```json
{
  "body_template": "<html><body><p>Hello {{user_name}},</p><p>We received a request to reset your password. Click <a href='{{reset_link}}'>Reset Password</a>.</p><p>Link expires in {{expiry_minutes}} min.</p></body></html>",
  "activate": true
}
```

**Response:**
```json
{
  "status": "success",
  "template_id": "tmpl-004",
  "old_version": 1,
  "new_version": 2,
  "is_active": true
}
```

#### Get Template

```
GET /api/v1/templates/{template_id}?version=latest&channel=email
```

#### List Templates

```
GET /api/v1/templates?category=transactional&channel=email&language=en&page=1&limit=20
```

#### Delete / Deactivate Template

```
DELETE /api/v1/templates/{template_id}
```

> Soft-deletes (sets `is_active = false`) rather than hard-deleting, so historical notifications can still reference the template.

---

### Template Rendering Flow (End-to-End)

```
┌────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Client    │──────▶│ Notification     │──────▶│ Template Service │
│  Request   │       │ Service (API)    │       │ (Fetch + Render) │
│            │       │                  │       │                  │
│ templateId │       │ 1. Validate      │       │ 3. Fetch template│
│ + variables│       │ 2. Auth check    │       │    from DB/cache │
│            │       │                  │       │ 4. Validate vars │
└────────────┘       └────────┬─────────┘       │ 5. Render message│
                              │                 └────────┬─────────┘
                              │                          │
                              │◀─── Rendered message ────┘
                              │
                    ┌─────────▼──────────┐
                    │ User Preference    │
                    │ Service            │
                    │ 6. Check opt-in    │
                    │ 7. Check rate limit│
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ Notification Queue  │
                    │ 8. Enqueue per     │
                    │    channel topic   │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ Channel Processor  │
                    │ 9. Deliver via     │
                    │    provider        │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ Delivery Log       │
                    │ 10. Log status     │
                    └────────────────────┘
```

#### Step-by-Step Flow

| Step | Component | Action |
|---|---|---|
| **1** | **Client** | Sends notification request with `template_id` + `variables` (dynamic data) |
| **2** | **Notification Service** | Authenticates the request via API Gateway, validates required fields |
| **3** | **Template Service** | Fetches the active template from DB (or **Redis cache** for hot templates) |
| **4** | **Template Service** | Validates that all required variables are provided; fills defaults for optional ones |
| **5** | **Template Service** | Renders the final message by replacing `{{placeholders}}` with actual values |
| **6** | **User Preference Service** | Checks if the user has opted into this notification type and channel |
| **7** | **User Preference Service** | Checks rate limits (e.g., promotional limit not exceeded) |
| **8** | **Notification Queue** | Rendered message is enqueued into the channel-specific topic (Email/SMS/Push) |
| **9** | **Channel Processor** | Consumes the message, sends it via the external provider (SendGrid, Twilio, FCM) |
| **10** | **Delivery Log** | Logs the delivery status (`sent`, `delivered`, `failed`, `bounced`) |

---

### Notification Request Using Template (API Example)

#### Send Notification via Template

```
POST /api/v1/notifications/send
```

**Request Body:**
```json
{
  "request_id": "req-98765",
  "template_id": "tmpl-001",
  "recipient": {
    "user_id": "user-789",
    "email": "john@example.com",
    "phone": "+1234567890",
    "device_token": "fcm_token_abc123"
  },
  "channels": ["email", "push"],
  "variables": {
    "user_name": "John Doe",
    "order_id": "ORD-123456",
    "order_total": "2,499.00",
    "currency": "₹",
    "tracking_url": "https://example.com/track/ORD-123456"
  },
  "schedule": {
    "send_at": null
  },
  "metadata": {
    "priority": "high",
    "max_retries": 3,
    "source": "OrderService"
  }
}
```

**What happens internally:**

1. Template `tmpl-001` (order_confirmation, email) is fetched.
2. Placeholders are replaced:
   - `{{user_name}}` → `John Doe`
   - `{{order_id}}` → `ORD-123456`
   - `{{order_total}}` → `2,499.00`
   - `{{currency}}` → `₹`
   - `{{tracking_url}}` → `https://example.com/track/ORD-123456`
3. Final rendered email is enqueued to the Email Topic.
4. Similarly, the push template for `order_confirmation` is fetched, rendered, and enqueued to the Push Topic.

**Response:**
```json
{
  "status": "accepted",
  "request_id": "req-98765",
  "notifications": [
    { "channel": "email", "status": "queued", "message_id": "msg-e-001" },
    { "channel": "push", "status": "queued", "message_id": "msg-p-001" }
  ]
}
```

---

### Template Caching Strategy

| Layer | What's Cached | TTL | Invalidation |
|---|---|---|---|
| **Redis / Memcached** | Active template content by `template_id` + `channel` + `language` | 5–15 min | On template update via API (publish invalidation event) |
| **Application-level (in-memory)** | Top 100 most-used templates | 1–2 min | Short TTL auto-refresh |
| **CDN (for email assets)** | Images, logos, CSS used in email templates | 24 hrs | Manual purge on asset update |

---

### Template Versioning & Rollback

```
Template: order_confirmation (email)
├── v1 (created 2024-01-01) — INACTIVE
├── v2 (created 2024-03-15) — INACTIVE   ← can rollback to this
└── v3 (created 2024-09-01) — ACTIVE     ← currently in use
```

- Every update creates a **new version**, old versions are preserved.
- **Rollback**: Activate an older version via `PUT /api/v1/templates/{id}/activate?version=2`.
- **A/B Testing**: Route a percentage of users to a different template version to compare engagement metrics.

---

## FAQ: Partitioning vs Indexing on Timestamp

### Why partition the `scheduled_notifications` table on `scheduled_time` instead of just using an index?

**Short Answer:** Partitioning provides better scalability and query performance for time-series data, especially with millions of rows.

#### Detailed Comparison:

| Aspect | Index-Based Approach | Partitioning-Based Approach |
|---|---|---|
| **Query Scope** | Index narrows down which rows to scan, but still searches across the entire table structure | Partitioning physically separates data by time range; only the relevant partition(s) are accessed |
| **Data Volume** | With 250GB+ notifications daily, an index becomes a bottleneck as it must traverse a massive index tree | Partitions keep data organized by time, reducing the working set size dramatically |
| **Disk I/O** | Even with an index, scanning millions of matching rows requires significant I/O operations | Partitions reduce I/O by only reading the partition containing the time range needed |
| **Maintenance** | Index updates are required on every insert; slows down write operations | Partitions don't require index maintenance; new data goes directly to the appropriate partition |
| **Archiving & Cleanup** | Deleting old records requires individual row deletions; slow and resource-intensive | Old partitions can be dropped/archived as whole units; instant operation |
| **Scaling** | Index tree grows with data volume, slowing traversal over time | Partitions stabilize in size; adding new partitions is a constant-time operation |

#### Example:

**With Index Only:**
```
Table: scheduled_notifications (millions of rows)
Index on scheduled_time
Query: SELECT * FROM scheduled_notifications WHERE scheduled_time BETWEEN now AND now+5min

Backend: Traverse entire B-tree index → Find matching rows scattered across the table
I/O Cost: High (reading from multiple locations on disk)
```

**With Partitioning:**
```
Table: scheduled_notifications (partitioned by day or hour)
├── partition_2026_03_29 (contains only today's scheduled notifications)
├── partition_2026_03_30 (contains tomorrow's data)
├── partition_2026_03_31 
└── ...

Query: SELECT * FROM scheduled_notifications WHERE scheduled_time BETWEEN now AND now+5min

Backend: Identify relevant partition(s) → Scan only that partition
I/O Cost: Low (data is physically grouped together)
```

#### When to Use Each:

- **Index-Based**: When the query range is selective and the table is small to medium-sized (< 10GB)
- **Partitioning**: When dealing with large time-series data (100GB+), frequent range queries, or heavy write loads

For a **notification system with 250GB daily storage**, partitioning is the superior choice.
