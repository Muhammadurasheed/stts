# STTS — Smart Triage Ticketing System

**STTS** is an AI-powered support ticketing platform that eliminates manual ticket sorting. When a customer submits a ticket, the system reads the description, assigns a category (Billing, Technical Bug, Feature Request, Account, General), sets a priority level (High, Medium, Low), and delivers a confidence-scored reasoning — all in under 3 seconds — before any human agent touches it.

> The system is fully functional end-to-end: customers submit tickets, Vertex AI classifies them, and authenticated agents manage them from a real-time dashboard.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend** | Python 3.12 · FastAPI | Async-first, auto-docs (OpenAPI), Pydantic validation |
| **Frontend** | Next.js 14 · TypeScript · Tailwind CSS | App Router, SSR-ready, type-safe |
| **Database** | MongoDB · Motor (async driver) | Document model fits ticket evolution, async IO |
| **AI Engine** | Google Vertex AI (Gemini 2.0 Flash) | Production-grade, GCP-billed, low-latency |
| **Auth** | JWT + Google OAuth 2.0 | Stateless sessions, Google Sign-In with JIT provisioning |
| **Infra** | Docker (local) · MongoDB Atlas (prod) | Environment-agnostic via `MONGODB_URL` |

---

## Core Features

### AI-Powered Triage (Vertex AI)
Every submitted ticket is analyzed by **Gemini 2.0 Flash** through our custom LLM Gateway. The AI returns:
- **Category**: Billing, Technical Bug, Feature Request, Account, or General
- **Priority**: High, Medium, or Low
- **Confidence Score**: 0.0–1.0 indicating classification certainty
- **Reasoning**: A one-sentence explanation of why

The triage runs asynchronously — customers get instant confirmation while AI classifies in the background.

### 3-Layer LLM Resilience
The [LLM Gateway](backend/app/infrastructure/llm/gateway.py) protects the system from AI failures with three defensive layers:

1. **Multi-Model Fallback**: `gemini-2.0-flash → 1.5-flash → 1.5-pro → 1.0-pro` with instant pivot on quota/billing errors
2. **Circuit Breaker**: Opens after 5 consecutive failures, blocks LLM calls for 60s to prevent cascading failure
3. **Mock Triage (Keyword Heuristic)**: If all models fail, a deterministic keyword analyzer ensures every ticket still gets a category and priority

**Result**: Tickets are never left unclassified, regardless of LLM availability.

### Authentication & Security
- **JWT-based stateless auth** with 24-hour expiry and persistent login
- **Google Sign-In** with real token verification via `google-auth` (not placeholder decoding)
- **JIT Provisioning**: First-time Google users are auto-registered; existing email accounts are linked
- **Rate limiting** on public endpoints (10 req/min) to prevent abuse
- **CORS lockdown** with configurable `ALLOWED_ORIGINS`
- Auto-redirect: logged-in users visiting `/` are sent straight to `/dashboard`

### Agent Dashboard
- **Kanban View**: Drag tickets between Open → In Progress → Resolved
- **Table View**: Dense, sortable format for backlog management
- **Real-Time Search**: Client-side filtering across title, email, and ID
- **Optimistic Updates**: Status changes reflect instantly, sync in background
- **Full CRUD**: Create, edit, delete tickets with confirmation modals

### Environment-Aware Database
The backend connects to whatever `MONGODB_URL` points to — zero conditional logic:
- **Local**: `run.py` auto-starts a Docker container (`mongo:7`) with a persistent named volume
- **Production**: `MONGODB_URL` points to a MongoDB Atlas cluster

---

## Quick Start

```bash
# Prerequisite: Docker Desktop running

# 1. Backend
cd backend
python run.py        # Starts MongoDB + activates venv + launches FastAPI on :8000

# 2. Frontend (new terminal)
cd frontend
npm run dev          # http://localhost:3000
```

### Environment Variables

**Backend** (`.env`):
```
MONGODB_URL=mongodb://localhost:27017
JWT_SECRET_KEY=<required — no default>
GOOGLE_CLIENT_ID=<your Google OAuth client ID>
GEMINI_API_KEY=<your Gemini API key>
USE_VERTEX_AI=true
GCP_PROJECT=gen-lang-client-0669834943
GCP_LOCATION=us-central1
```

**Frontend** (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=<your Google OAuth client ID>
```

---

## Architecture

```
frontend/                     backend/
├── src/app/                  ├── app/
│   ├── page.tsx (home)       │   ├── api/v1/          ← REST endpoints
│   ├── submit/               │   ├── core/
│   ├── login/                │   │   ├── models/      ← Pydantic domain models
│   ├── dashboard/            │   │   └── services/    ← Business logic
│   └── layout.tsx            │   ├── infrastructure/
├── src/lib/                  │   │   ├── database/    ← MongoDB (Motor)
│   ├── api.ts                │   │   ├── llm/         ← LLM Gateway + Circuit Breaker
│   └── auth.tsx              │   │   └── security/    ← JWT, rate limiter
└── src/types/                │   └── config.py        ← Pydantic Settings
                              └── run.py               ← Entrypoint (venv + Docker)
```

Clean Architecture: domain layer has zero dependency on frameworks or database drivers. Every piece of core logic is independently testable.

---

## Testing

```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

**Coverage: 88.19%** across 75+ unit tests — covering ticket CRUD, AI parsing, service logic, and security edge cases.

---

## Verification Tasks

### 1. Scaling to RBAC (Role-Based Access Control)

If we added **Admins** and **Read-Only** users:

- **Model**: Extend `Agent` with `role: UserRole` enum (Admin, Agent, Reader)
- **Policy**: Centralized `requires_role(role)` dependency in [deps.py](backend/app/api/deps.py)
- **Enforcement**:
  - `POST /tickets` → Public (unchanged)
  - `GET /tickets` → All authenticated roles
  - `PATCH/PUT /tickets` → Agent + Admin
  - `DELETE /tickets` → Admin only
- **Frontend**: Conditionally render actions based on JWT role claim

### 2. Handling LLM Failure (Graceful Degradation)

The system stays **100% available** when AI is down:

1. **Circuit Breaker** detects consecutive failures → opens circuit
2. **Tickets save immediately** — triage is async, never blocks creation
3. **Mock Triage** classifies using keyword heuristics (confidence set to 0.5 to flag heuristic origin)
4. **Auto-Recovery**: Circuit enters half-open after 60s → probes LLM → closes if successful

Customers never know the AI is down. Agents see lower confidence scores as a signal.

---

## Documentation

| Document | What It Covers |
|----------|---------------|
| [AI_JOURNEY.md](AI_JOURNEY.md) | AI collaboration log — prompts used, hallucinations caught, corrections made |
| [PROJECT_WALKTHROUGH.md](PROJECT_WALKTHROUGH.md) | Full system walkthrough — user journeys, LLM Gateway internals, auth architecture, challenges |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Step-by-step deployment guide — MongoDB Atlas, Render (backend), Vercel (frontend) |

---

## Deployment

| Layer | Platform | Status |
|-------|----------|--------|
| Frontend | Vercel | Config ready (`frontend/vercel.json`) |
| Backend | Render | Config ready (`backend/render.yaml`) |
| Database | MongoDB Atlas | Cluster provisioned |
| AI | Vertex AI (GCP) | `gen-lang-client-0669834943` with billing enabled |

See [DEPLOYMENT.md](DEPLOYMENT.md) for the full setup guide.

---

Built for the **Codematic Full-Stack Assessment** · FastAPI · Next.js · Vertex AI · MongoDB
