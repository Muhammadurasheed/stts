# STTS — Smart Triage Ticketing System: Full Project Walkthrough

> *This document walks through the entire STTS application from first principles, what it does, how it's built, why each decision was made, and what it took to get here.*

---

## What Is STTS?

**STTS** stands for **Smart Triage Ticketing System**. The idea is simple but the problem it solves is real: customer support teams are drowning in tickets. Someone submits a complaint about a failed payment side by side with a feature request for dark mode, and both land in the same queue with no priority, no category, nothing. An agent has to read every single one before they even know which fires to put out first.

STTS changes that. The moment a customer submits a ticket, our AI engine reads it, decides what kind of problem it is (billing, technical bug, feature request, account issue, or general), how urgent it is (high, medium, low), and writes a one-sentence explanation of why. All of this happens within seconds, automatically, before any human touches it.

---

## The Architecture

The system is broken into three clean layers:

**Backend**: Python + FastAPI, structured around clean architecture principles. The domain layer (business logic) has zero dependency on web frameworks or database drivers. That separation means every piece of core logic can be tested independently.

**Database**: MongoDB with Motor for async operations. The schema is document-oriented, which maps perfectly to the way tickets evolve — they start simple and accumulate triage data, status updates, and timestamps over time.

**Frontend**: Next.js 14 with TypeScript and Tailwind. App Router for file-based routing, server components where they help, and a deliberately premium dark-mode-first design.

**AI Engine**: Google Gemini via the `google-genai` SDK with a custom LLM Gateway sitting in between. The gateway is where the magic and the engineering happen — more on that below.

---

## The User Journey — Start to Finish

### Submitting a Ticket (Public User)

A customer lands on the STTS homepage. There's no account required. They hit "Submit a Ticket," fill in three fields — a title, a description, and their email — and click Submit.

On the backend, the `POST /api/v1/tickets` endpoint receives the payload, validates it through Pydantic (type-safe, email-validated, length-constrained), and immediately writes the ticket to MongoDB. The customer gets an instant confirmation. That part is synchronous and always fast.

Then, asynchronously, the AI triage kicks in. The `TriageService` calls the `LLMGateway`, which sends the ticket title and description to Gemini with a carefully engineered system prompt. Gemini responds with a JSON object: category, priority, confidence score (0.0–1.0), and a brief reasoning. The gateway parses and validates this response, then updates the ticket in the database with those fields.

If Gemini is unavailable, slow, or rate-limited, the full resilience stack kicks in — but the customer never knows. Their ticket is already saved.

### Logging In as an Agent

Support agents authenticate via email/password or Google Sign-In. The email/password path uses bcrypt hashing with an adaptive salt. The Google path verifies the ID token's cryptographic signature against Google's public keys using `google-auth`'s `id_token.verify_oauth2_token()` — not a placeholder decode, real verification.

On successful login, the backend issues a JWT with a 24-hour expiry. The frontend stores this token and the agent's profile in `localStorage`. On every subsequent page load, the auth context reads the cached profile immediately (for instant UI), then silently validates the token against `/api/v1/auth/me` in the background. If the token has expired, the cache is cleared and the user is redirected to login. If it's still valid, the fresh profile is pulled from the database.

Once logged in, navigating to `localhost:3000` auto-redirects directly to the dashboard — no extra step.

### The Agent Dashboard

The dashboard is the heart of the product for support teams. It opens in Kanban view by default — three columns: Open, In Progress, Resolved. Every ticket card shows the AI-assigned category and priority as color-coded badges, the customer email, the time since submission, and the AI confidence score as a progress bar.

**Instant Search**: Typing in the search bar filters tickets in real time, client-side, across title, email, and ID — no API round trips.

**Status Updates**: Dragging or clicking "Move to In Progress" optimistically updates the UI immediately, then syncs to the backend. If the backend call fails, the ticket snaps back to its previous state.

**Full CRUD**: Agents can edit ticket content, manually override the AI's category or priority, and delete tickets. Edit and delete are protected behind confirmation modals.

**Table View**: Toggling to table view shows the same data in a dense, sortable format — useful when working through a large backlog.

---

## The LLM Gateway — The Engineering Core

This is the piece I'm most proud of. A naive implementation just calls the Gemini API and hopes for the best. That breaks in production. The LLM Gateway wraps the API call in three defensive layers:

**Layer 1: Multi-Model Fallback with Instant Pivoting**

The gateway maintains an ordered list of models: `gemini-2.0-flash → gemini-1.5-flash → gemini-1.5-pro → gemini-1.0-pro`. When any model returns a quota error, billing error, or permission error (not a transient 500), the gateway immediately pivots to the next model — no wasted retries. For transient errors, it retries the current model with exponential backoff and jitter (capped at 10 seconds) before moving on.

**Layer 2: Circuit Breaker**

After 5 consecutive failures, the circuit opens. For 60 seconds, all LLM calls are skipped and tickets go straight to the fallback. After the timeout, the circuit enters half-open state — one probe request is allowed through. If it succeeds, the circuit closes. If it fails, it reopens for another 60 seconds.

**Layer 3: Mock Triage**

If every model fails and the circuit opens, the system doesn't crash and it doesn't return untriaged tickets. Instead it runs a deterministic keyword analysis: "billing," "invoice," "payment" → Billing category; "bug," "error," "broken" → Technical Bug; "urgent," "critical," "blocking" → High priority. The confidence score is set to 0.5 to signal to agents that this was a heuristic classification, not AI.

**The result**: A ticket is never left without a category and priority. Ever.

---

## Authentication Architecture

JWT-based, stateless, 24-hour expiry. Tokens are issued at login and verified on every protected endpoint by decoding and validating the signature against `JWT_SECRET_KEY`.

Google OAuth support uses JIT (Just-In-Time) provisioning: if a Google user's email matches an existing email/password account, the systems link automatically. If it's a new email, a new agent account is created on the spot. Google-authenticated accounts are blocked from the email/password login path (and vice versa) to prevent credential confusion.

Rate limiting is applied to the public endpoints — 10 requests per minute on register, login, and ticket creation — to prevent abuse without blocking legitimate traffic.

---

## Data Persistence

MongoDB with a named Docker volume (`stts-mongo-data`) ensures data survives container restarts. The volume is shared between `run.py` (local development) and `docker-compose.yml` (containerized deployment) so data is consistent regardless of how you start the stack.

Indexes are created on startup — on `created_at` for sort performance and on `status`/`priority` for filter performance. This runs idempotently every time the app starts.

### Environment-Aware Database Strategy

One of the more practical design choices was making the database layer completely environment-agnostic. The backend doesn't care whether it's talking to a local Docker container or a cloud-hosted Atlas cluster — it reads `MONGODB_URL` from the environment and connects. That's it.

- **Local development**: `run.py` spins up a Docker container (`mongo:7`) with a persistent named volume. Zero setup for developers beyond having Docker Desktop running.
- **Production (Render/Cloud Run)**: `MONGODB_URL` points to a MongoDB Atlas connection string (`mongodb+srv://...`). No Docker needed on the server.

This means the same codebase, the same config file structure, the same connection logic — just a different URL depending on the environment. No `if environment == "prod"` conditionals anywhere in the database code. Clean separation through environment variables, the way infrastructure should work.

---

## Challenges Encountered

**The Silent 422 Bug**: Tickets were being created and saved correctly. But after every page refresh, the dashboard showed 0 tickets. MongoDB was connected, the API was responding, everything looked fine. The actual problem was a mismatch between the frontend (`page_size=200`) and the backend's query parameter validation (`le=100`). FastAPI was rejecting every list request with a 422 Unprocessable Content error. The UI was catching the error silently and showing an empty state. Added diagnostic logging on both ends, caught it in the Network tab, fixed the validation limit. The data was always there.

**Vertex AI 403 BILLING_DISABLED**: After migrating from the free-tier Gemini API to Vertex AI (to get past the `limit: 0` quota wall), every request returned 403. The error handling was treating this as a generic error and retrying the same model 3 times before pivoting. Wasting 30+ seconds per ticket submission. Fixed by: (1) creating a billing-enabled GCP project and (2) classifying `403/BILLING/PERMISSION_DENIED` as an instant-pivot error rather than a retry candidate.

**Docker Race Condition in run.py**: The MongoDB container was being stopped and started on every run because the Docker lifecycle code was executing twice — once in the outer process and once in the re-launched venv process. Moved `ensure_mongodb()` to execute only after the venv re-launch has settled.

---

## What's Left / Future Work

1. **Email Notifications**: When a ticket's status changes, the customer should get an email. The architecture — with the ticket service as the orchestration layer — makes this easy to drop in.
2. **Real-Time Dashboard**: WebSocket or SSE push for ticket updates. Right now the dashboard refreshes on demand. In a team environment you'd want agents to see updates as they happen.
3. **RBAC**: The verification section in `README.md` outlines exactly how Admin/Agent/Reader roles would be added to the existing architecture.
4. **Billing on Vertex AI**: The triage feature currently falls back to Mock Triage because the free-tier GCP project has no billing. With `gen-lang-client-0669834943` (billing-enabled), the full AI triage should work end-to-end.

---

## Quick Start (Local)

```bash
# 1. Start Docker Desktop

# 2. Backend
cd backend
python run.py          # Auto-starts MongoDB, activates venv, starts FastAPI

# 3. Frontend (separate terminal)
cd frontend
npm run dev            # http://localhost:3000
```

Everything boots with a single command per layer. The `run.py` script handles venv activation and MongoDB container startup automatically, no manual steps.

### 4. The Cloud Run Migration

Midway through the deployment phase, we pivoted from Render to **Google Cloud Run** for the backend infrastructure. 

**The Challenge**: 
The initial plan with Render hit a "friction wall" regarding Vertex AI integration. External platforms require managing **Google Application Credentials** via JSON key files injected into the container. This created two problems:
1. **Security Overhead**: Storing sensitive service account keys in environment variables or volume mounts increases the attack surface.
2. **Authentication Lag**: Every request to Vertex AI required an explicit token exchange across network boundaries, which added millisecond latency to our <3s triage goal.
3. **Complexity**: Configuring a local Docker container to act like a production cloud instance while talking to a remote GCP project created a "parity gap."

**The Solution**: 
By moving to Cloud Run, we Gains **Zero-Configuration Identity**. Since the backend now runs natively on Google's infrastructure:
- It uses the **Compute Engine Default Service Account** out of the box.
- It authenticates to Vertex AI via the **internal Metadata Server** — no keys, no passwords, just seamless project-level permissions.
- **Latency reduction**: Requests stay within Google's backbone, shaving off precious milliseconds.

This also unlock **Cloud Build**, allowing us to define the infrastructure-as-code in `cloudbuild.yaml`. It transformed the project from a "packaged app" to a **Cloud-Native Solution** that scales to zero when not in use, saving costs while delivering Google-grade performance.

---
