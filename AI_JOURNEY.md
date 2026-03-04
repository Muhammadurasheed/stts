# 🚀 AI Journey — STTS Development

> This document captures my collaboration with AI coding assistants during the development of STTS. The methodology is deliberate: I drive every architectural and design decision, and use AI to accelerate implementation of those decisions, never the other way around.

---

## 🧠 Complex Prompts I Used

### 1. Resilient LLM Gateway — Circuit Breaker Architecture

I've seen AI integrations go down in production before, and every time it happens the entire experience breaks. My instinct from building distributed systems was to never let a third-party API be a single point of failure. I designed the three-layer resilience architecture myself first:

- **Layer 1** — Exponential backoff with jitter for transient errors
- **Layer 2** — Circuit breaker (Closed → Open → Half-Open state machine)
- **Layer 3** — Keyword-based Mock Triage as the final safety net

Then I prompted AI with this specific design:

> *"Implement a production-grade LLM Gateway around Google Gemini's API. Use a three-layer resilience model: (1) retry with exponential backoff and jitter capped at 10s, (2) a circuit breaker with configurable threshold and timeout that transitions through Closed, Open, and Half-Open states, and (3) graceful degradation where a ticket is saved untriaged if all layers fail. The circuit breaker state must be externally observable for health checks."*

**My correction**: The initial AI-generated code had the circuit breaker only monitoring generic exceptions, it wasn't distinguishing between 429 quota errors (where I should pivot to a different model) vs. 500 server errors (where I'll retry). I caught this and directed the fix: quota errors should trigger an immediate model pivot, not a retry on the same exhausted endpoint.

---

### 2. Google OAuth2 — Real Verification vs. Simulated Decoding

Security is something I've always taken seriously. Early in development I reviewed what the AI produced for the Google login flow and immediately recognized a critical flaw, it was using a placeholder that simply decoded the JWT without verifying the signature against Google's public keys. That's not authentication, that's just base64 decoding.

I directed the implementation:

> *"Replace the placeholder token decoder with real Google ID token verification using the google-auth library's id_token.verify_oauth2_token(). It must check the audience claim against our client ID and handle JIT provisioning — if an existing email-based account logs in with Google for the first time, link the google_id to the existing record rather than creating a duplicate."*

**Outcome**: A proper auth flow that verifies cryptographic signatures with Google's servers, handles account linking, and supports both email/password and Google OAuth flows without duplication.

---

### 3. DPE-Level Security Audit

Before shipping any backend I run through a mental security checklist. For this project I explicitly commissioned a full-codebase audit with specific threat categories in mind:

> *"Perform a line-by-line security audit as a Google Distinguished Principal Engineer would. Flag any CORS misconfiguration, missing rate limiting on public endpoints, JWT secret defaults, password bypass vectors for OAuth accounts, and input sanitization gaps. Then implement the fixes."*

**My corrections**:

- The AI initially left a fallback default for `JWT_SECRET_KEY` in config — I flagged this immediately. A secret with a default isn't a secret. Made it a hard-required field so the app crashes at startup rather than silently using a known default.
- CORS was initially set to `allow_origins=["*"]` — I tightened it to `["http://localhost:3000"]` for development with a clear production extension path.

---

## 🐛 Where AI Went Wrong — And How I Fixed It

### 1. The página_size Blind Spot

The most impactful bug in the project was silent and hard to trace: tickets were being created and saved to MongoDB correctly, but the dashboard always showed 0 after a refresh. The AI generated a frontend that requested `page_size=200` and a backend that validated `le=100`, and never caught the mismatch.

I approached this systematically the way I would in production, I added diagnostic logging to both the frontend (`console.log` around fetch) and the backend (request/response logging on the list endpoint), then used the browser's Network tab to catch the `HTTP 422` response. Once I saw the validation error in the response body, the fix was obvious. Changed `le=100` to `le=200`.

This is a classic integration mismatch that static analysis misses. Experience told me to add observability first, trace the problem to the wire, and *then* fix. But then, this really took my time to figure out, it was very subtle but critical challenge

### 2. The Double-Start Race Condition

The AI initially placed Docker container startup logic inside `ensure_venv()`, the function responsible for re-launching the script with the virtualenv Python. Because the script re-launches itself, this caused MongoDB to be stopped and restarted on every startup. I caught the execution flow trace and restructured the entry point: `ensure_mongodb()` only runs inside `main()`, after the re-launch has settled.

### 3. The Vertex AI Billing Misconfiguration

The AI suggested migrating from free-tier Gemini API to Vertex AI using project `stts-489117`. The connection worked but all requests returned `403 BILLING_DISABLED`. The AI's retry logic was treating this as a transient error and wasting 12 retry attempts (4 models × 3 retries) before reaching Mock Triage.

My fix was two-fold:

1. Create a new GCP project with billing enabled (`gen-lang-client-0669834943`)
2. Correct the error classification: `403/BILLING/PERMISSION_DENIED` errors should trigger an immediate model pivot, not retries

---

## 🛡️ The Verification Task

See [README.md](./README.md) for the full breakdown of:

- **RBAC Scaling Strategy** — How to extend to Admin/Agent/Reader roles
- **Graceful LLM Degradation** — How the system stays 100% available when AI is down
