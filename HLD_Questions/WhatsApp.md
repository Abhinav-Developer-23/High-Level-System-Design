# 💬 WhatsApp

## ❓ Questions to Ask the Interviewer

> Pin down chat type, scale, and delivery rules before drawing anything.

---

### 1. Do we need only one-on-one chat, or group chat too? If groups, what is the maximum group size?

**Why ask:** Groups bring fan-out: one incoming message becomes N outgoing deliveries. A small cap lets us simply deliver to each member (Alex Xu, p.193: WeChat caps groups at 500 for this reason). Groups of 100,000 would need a completely different design.

**Interviewer Answer:** Both. Groups have up to 500 members.

### 2. What is the expected scale? How many daily users, and how many messages per user?

**Why ask:** Sets how many chat servers we need (each holds only about 50,000 open WebSocket connections), the message write rate, and the storage per day.

**Interviewer Answer:** 500M DAU, about 40 messages per user per day = 20 billion messages/day (about 230K/sec on average, about 700K/sec at peak). About 10% of users are online at any moment = 50M open connections.

### 3. What content do messages carry: only text, or also images, videos and voice notes? Is there a size limit?

**Why ask:** A text message is about 100 bytes; a video is many MBs. Media needs its own path: upload to object storage (S3) behind a CDN, and the message carries only a link.

**Interviewer Answer:** Design for text; the limit is 100,000 characters. Mention media only at a high level.

### 4. What are the delivery guarantees? Can a message be lost, delivered twice, or shown out of order?

**Why ask:**

1. "Never lost" means we save the message before we acknowledge it.
2. Client retries can create duplicates, so we need a client-generated `clientMessageId` for dedup.
3. "In order" decides how we create message IDs: IDs that sort by time, assigned by the server, never taken from the phone's clock.

**Interviewer Answer:** Messages must never be lost and never appear twice. Within one chat, everyone sees them in the same order. No global order across chats is needed.

### 5. What happens when the receiver is offline? Do we need push notifications?

**Why ask:** We must hold messages on the server and deliver them when the user reconnects. That needs a per-user "last delivered" marker, plus a push integration (APNs/FCM) to wake the phone.

**Interviewer Answer:** Yes. Store the message, send a push notification ("New message from Alice"), and deliver everything pending when the user comes back, whether that's 10 seconds or 10 days later.

### 6. Do users need delivery status: sent, delivered and read ticks?

**Why ask:** For a one-on-one chat, one status per message is enough. In a group, each member receives and reads at a different time, so we need per-recipient status, and every tick is an extra event sent back to the sender.

**Interviewer Answer:** Yes. ✓ sent (saved on the server), ✓✓ delivered (on the receiver's device), blue ✓✓ read.

### 7. Do we need online status, "last seen" and typing indicators?

**Why ask:** Presence changes constantly (tunnels, Wi-Fi to 4G). It needs heartbeats and a TTL store (Redis). Sending every status change to all contacts doesn't scale, so it shapes the design.

**Interviewer Answer:** Online/offline and "last seen" are required. Typing indicators are nice-to-have.

### 8. How long do we keep chat history, and must it sync across a user's devices?

**Why ask:** Keeping history long-term at 20B messages/day (about 2 TB/day) pushes us toward a wide-column NoSQL store. Multi-device means each device tracks its own sync point, and one message is pushed to several connections.

**Interviewer Answer:** Keep messages until the user deletes them. One phone plus up to 4 linked devices (web/desktop), all with the same history.

### 9. Is end-to-end encryption required?

**Why ask:** With E2EE the server can't read messages, so there's no server-side search or moderation, and multi-device sync means encrypting the message separately for each device.

**Interviewer Answer:** Mention it conceptually; the cryptography details are out of scope.

---

## ⚙️ Functional Requirements

> Core capabilities the chat system must provide.

---

### 1. One-on-One Chat

Users can send and receive messages in real-time with other users.

### 2. Group Chat

Users can create groups and send messages to multiple recipients (up to 500 members).

### 3. Message Delivery Status

Users can see delivery receipts (sent, delivered, read).

### 4. Online Presence

Users can see if their contacts are online, offline, or their last seen time.

### 5. Message History

Users can access their message history and sync across multiple devices.

### 6. Push Notifications

Offline users receive push notifications for new messages.

---

## 🛡️ Non-Functional Requirements

> Quality attributes: latency, availability, reliability, scale, ordering and consistency.

---

### 1. Low Latency

Messages should be delivered within milliseconds for online users. Target: p99 < 100ms for delivery when the recipient is online.

### 2. High Availability

The system must be highly available (99.99% uptime). Users expect messaging to work 24/7.

### 3. Reliability

Messages must never be lost. Once sent, a message should eventually be delivered, even if the recipient is offline.

### 4. Scalability

Support 500M+ daily active users and 20B+ messages per day.

### 5. Ordering

Messages within a conversation should appear in the correct order.

### 6. Consistency

Eventually consistent for presence. Message delivery is at-least-once with no duplicates, and messages within a conversation are ordered.

---

## 🚫 Out of Scope

> Features we set aside to keep the interview focused.

---

### Out of Scope

To keep our discussion focused, we will set aside a few features that, while important, would expand the scope beyond a single interview:

1. **Media Messages:** Images, videos, voice notes (mentioned conceptually only).
2. **Voice/Video Calls:** Real-time audio and video communication.
3. **End-to-End Encryption:** Detailed cryptographic implementation.
4. **Stories/Status Updates:** Ephemeral content sharing.

---

## 💬 Would you like me to cover back-of-the-envelope calculations as well, or focus on the high-level design?

---
