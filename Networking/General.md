# Networking - General

---

### Q1. What is the difference between HTTP and HTTPS?

<details>
<summary>Answer</summary>

| Feature | HTTP | HTTPS |
|---|---|---|
| Full Form | HyperText Transfer Protocol | HyperText Transfer Protocol **Secure** |
| Port | 80 | 443 |
| Encryption | ❌ None — data is sent in **plain text** | ✅ Data is encrypted using **TLS (Transport Layer Security)** |
| Security | Vulnerable to **Man-in-the-Middle (MITM)** attacks, eavesdropping, and data tampering | Protected against MITM attacks; data integrity and confidentiality ensured |
| Authentication | No server identity verification | Server identity verified via **SSL/TLS certificates** issued by a trusted CA (Certificate Authority) |
| Performance | Slightly faster (no encryption overhead) | Marginally slower, though **TLS 1.3** and **HTTP/2** have minimised this gap |
| SEO | Ranked lower by search engines | Preferred by search engines (Google ranks HTTPS sites higher) |
| Use Case | Internal tools, local dev environments | Any public-facing website, especially those handling sensitive data |

#### How HTTPS Works (TLS Handshake — simplified)
1. **Client Hello** — Browser sends supported TLS versions and cipher suites.
2. **Server Hello** — Server responds with its chosen cipher suite and its **SSL certificate** (contains the server's public key).
3. **Certificate Verification** — Browser verifies the certificate against trusted CAs.
4. **Key Exchange** — Both parties derive a shared **session key** (symmetric) using asymmetric cryptography.
5. **Encrypted Communication** — All subsequent data is encrypted with the symmetric session key.

#### Key Takeaway
> HTTP is **fast but insecure**. HTTPS adds a **TLS layer** on top of HTTP, providing encryption, server authentication, and data integrity — making it the standard for all modern web communication.

</details>

---

### Q2. How does HTTPS encryption work? Walk through each step and how it protects against Man-in-the-Middle (MITM) attacks.

<details>
<summary>Answer</summary>

HTTPS = HTTP + **TLS (Transport Layer Security)**. TLS uses a combination of **asymmetric** and **symmetric** cryptography to establish a secure channel.

---

#### � Symmetric vs Asymmetric Encryption — The Foundation

Before understanding HTTPS, you need to know the two types of encryption it uses:

##### Symmetric Encryption
- **One key** is used to both encrypt and decrypt data
- The same secret key must be shared between sender and receiver
- **Very fast** — suitable for encrypting large amounts of data
- **Problem:** How do you securely share the key in the first place? If intercepted, everything is compromised
- Example algorithms: **AES-128, AES-256, ChaCha20**

```
Encrypt:  plaintext  + secret_key  →  ciphertext
Decrypt:  ciphertext + secret_key  →  plaintext
```

##### Asymmetric Encryption
- **Two mathematically linked keys:** a **Public Key** (shared openly) and a **Private Key** (kept secret)
- Data encrypted with the public key can **only be decrypted by the private key**
- Data signed with the private key can be **verified using the public key**
- **Slow** — not suitable for bulk data, but perfect for safely exchanging a shared secret
- Example algorithms: **RSA, ECDHE (Elliptic Curve Diffie-Hellman)**

```
Encrypt:  plaintext  + public_key   →  ciphertext   (anyone can encrypt)
Decrypt:  ciphertext + private_key  →  plaintext    (only owner can decrypt)
```

##### Why HTTPS Uses Both
| Phase | Encryption Type | Why |
|---|---|---|
| **TLS Handshake** | Asymmetric (ECDHE/RSA) | Safely establish a shared secret without transmitting it |
| **Data Transfer** | Symmetric (AES) | Fast bulk encryption once both sides share the session key |

> Asymmetric encryption solves the **key distribution problem**, then symmetric encryption takes over for **speed**.

---

#### Step-by-Step: TLS 1.3 Handshake

**Step 1 — Client Hello**
- Browser sends:
  - Supported **TLS versions** (e.g., TLS 1.3)
  - Supported **cipher suites** (e.g., AES-256-GCM, ChaCha20)
  - A random value: `client_random`
  - Key share (for ECDHE — so the handshake can be done in **1 round trip**)

**Step 2 — Server Hello**
- Server responds with:
  - Chosen **TLS version** and **cipher suite**
  - A random value: `server_random`
  - Its own key share (ECDHE)
  - **SSL/TLS Certificate** — contains the server's **public key**, domain name, issuer (CA), and expiry

**Step 3 — Certificate Verification**
- Browser checks:
  - Is the certificate issued by a **trusted CA** (e.g., DigiCert, Let's Encrypt)?
  - Is the **domain name** on the cert matching the URL?
  - Is the certificate **within its validity period** and **not revoked** (via OCSP/CRL)?
- If any check fails → browser shows a **security warning** and aborts

**Step 4 — Key Exchange (ECDHE)**
- Both client and server independently compute the same **pre-master secret** using their key shares — **without ever sending it over the wire**
- From `client_random` + `server_random` + `pre-master secret`, both sides derive the identical **session key** (symmetric)

**Step 5 — Handshake Finished**
- Both sides send a **Finished** message encrypted with the session key to confirm the handshake succeeded

**Step 6 — Encrypted Data Transfer**
- All HTTP data is now encrypted with the **session key** (AES)
- Each message also carries a **MAC (Message Authentication Code)** to detect any tampering

---

#### 🛡️ Why MITM Attacks Fail — Step by Step

A MITM attacker (Eve) positions herself between the browser (Alice) and the server (Bob) and tries to intercept or tamper with traffic.

**Attack Attempt 1 — Just Listen (Passive Eavesdropping)**
- Eve intercepts all packets
- ❌ **Fails:** All data is encrypted with AES using a session key Eve never had access to. She sees only meaningless ciphertext.

**Attack Attempt 2 — Pretend to Be the Server**
- Eve intercepts Alice's connection and presents her own certificate
- ❌ **Fails:** Eve's certificate is not signed by a trusted CA for `bank.com`. Alice's browser immediately detects the mismatch and aborts with a security warning. Eve cannot forge a valid CA-signed certificate for a domain she doesn't own.

**Attack Attempt 3 — Intercept the Key Exchange**
- Eve tries to intercept the ECDHE key exchange to steal the session key
- ❌ **Fails:** With ECDHE, the session key is **never transmitted**. Both sides independently compute the same key using publicly shared values + their own private values. Eve can see the public values but cannot compute the secret without solving the mathematically hard **Elliptic Curve Discrete Logarithm Problem** (computationally infeasible).

**Attack Attempt 4 — Tamper with Data in Transit**
- Eve modifies encrypted packets mid-flight
- ❌ **Fails:** Every TLS record carries a **MAC**. If even a single byte is changed, the MAC verification fails and the receiver immediately discards the packet and tears down the connection.

**Attack Attempt 5 — Record Now, Decrypt Later**
- Eve records all encrypted traffic today, hoping to steal the server's private key in the future
- ❌ **Fails (with ECDHE):** Because ECDHE generates a **fresh, ephemeral key pair per session**, stealing the server's long-term private key later gives Eve nothing useful. The session keys are gone. This is **Perfect Forward Secrecy (PFS)**.

| Attack | Why It Fails |
|---|---|
| Passive eavesdropping | AES-encrypted session key they never possessed |
| Impersonate the server | Can't forge a CA-signed certificate for a domain they don't own |
| Steal the session key | ECDHE — key never transmitted, mathematically infeasible to derive |
| Tamper with packets | MAC on every record detects byte-level changes |
| Record & decrypt later | Perfect Forward Secrecy — ephemeral keys, nothing to steal |

---

#### Key Takeaway
> HTTPS uses **asymmetric encryption** (ECDHE) to solve the key distribution problem — safely establishing a shared secret without transmitting it. It then switches to fast **symmetric encryption** (AES) for all data. **CA-signed certificates** authenticate the server's identity, making impersonation impossible. The combination of these three mechanisms is what makes MITM attacks practically infeasible.

</details>

---

### Q3. What are the differences between HTTP/1.1, HTTP/2, and HTTP/3? How does each work, and what are the trade-offs?

<details>
<summary>Answer</summary>

#### High-Level Comparison

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| Released | 1997 | 2015 | 2022 |
| Underlying Protocol | TCP | TCP | **QUIC (UDP-based)** |
| Encryption | Optional (HTTP) | Optional (but HTTPS in practice) | **Always encrypted (TLS 1.3)** |
| Multiplexing | ❌ No | ✅ Yes | ✅ Yes |
| Head-of-Line Blocking | ❌ At request level | ❌ At TCP level | ✅ Eliminated |
| Header Compression | ❌ No | ✅ HPACK | ✅ QPACK |
| Server Push | ❌ No | ✅ Yes | ✅ Yes |
| Connection Setup | 1-3 RTT | 1-2 RTT | **0-1 RTT** |

---

#### HTTP/1.1 — How It Works

- Each request requires its own **TCP connection** (or reuses one serially via Keep-Alive)
- Requests are processed **one at a time per connection** — the next request can only be sent after the previous response is received (**Head-of-Line blocking**)
- Workaround: browsers open **6–8 parallel TCP connections** per domain

**Advantages:**
- Simple and universally supported
- Easy to debug (plain text)

**Disadvantages:**
- **Head-of-Line blocking** — one slow response blocks all others on that connection
- High **connection overhead** (multiple TCP handshakes)
- **No header compression** — repeated headers (cookies, user-agent) waste bandwidth

---

#### HTTP/2 — How It Works

- Introduces **binary framing** — data is split into binary **frames** instead of plain text
- **Multiplexing** — multiple requests and responses are interleaved over a **single TCP connection** using streams
- **HPACK header compression** — headers are compressed and indexed to avoid repetition
- **Server Push** — server can proactively send resources (e.g., CSS, JS) before the client requests them

**Advantages:**
- **Eliminates request-level HOL blocking** — multiple streams on one connection
- Faster due to **header compression** and reduced connection overhead
- **Stream prioritisation** — critical resources can be prioritised

**Disadvantages:**
- Still suffers from **TCP-level Head-of-Line blocking** — if a TCP packet is lost, ALL streams on that connection stall waiting for retransmission
- Server Push proved complex in practice and was often misused; **Chrome deprecated it in 2022**
- Binary protocol makes debugging harder

---

#### HTTP/3 — How It Works

- Replaces TCP with **QUIC** (Quick UDP Internet Connections), a protocol built on **UDP** but with reliability, ordering, and congestion control built on top at the **stream level**
- **TLS 1.3 is built into QUIC** — encryption is not optional
- **0-RTT connection establishment** — returning visitors can send data in the very first packet (using cached session info)
- **Per-stream loss recovery** — a lost UDP packet only affects the stream it belongs to, not all streams (HOL blocking fully eliminated)
- **Connection Migration** — if your IP changes (e.g., switching from Wi-Fi to 4G), the QUIC connection survives using a **Connection ID** rather than the IP+port tuple

**Advantages:**
- **No Head-of-Line blocking** — packet loss only stalls the affected stream
- **Faster connection setup** — 0-RTT for returning clients
- **Connection migration** — seamless network changes (critical for mobile)
- Always encrypted

**Disadvantages:**
- **UDP is often blocked** by firewalls and middleware (VPNs, corporate networks)
- Higher **CPU/resource usage** — QUIC logic runs in user space, not the OS kernel
- Still maturing — tooling and server support less widespread than HTTP/2
- **0-RTT replay attacks** — cached early data can be replayed by attackers; mitigated by using 0-RTT only for idempotent requests (GET)

---

#### Evolution Summary

```
HTTP/1.1  →  Serial requests, plain text, multiple TCP connections
HTTP/2    →  Multiplexing over 1 TCP, binary, header compression
HTTP/3    →  Multiplexing over QUIC (UDP), no HOL blocking, 0-RTT, always encrypted
```

#### Key Takeaway
> **HTTP/2** solved request-level HOL blocking with multiplexing but is still limited by TCP. **HTTP/3** solves the fundamental TCP problem by moving to **QUIC over UDP**, making it ideal for high-latency, lossy, or mobile networks. For most applications today, **HTTP/2 is the default**; HTTP/3 adoption is growing rapidly.

</details>
