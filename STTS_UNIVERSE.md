# 🌌 The STTS Universe
### Smart Triage Ticketing System — Engineering Blueprint

> **Bismillahi Rahmani Rahim** · *La hawla wala quwwata illa billah*
>
> We begin in the name of Allah, the Most Gracious, the Most Merciful.
> There is no power nor strength except with Allah.

---

## 🎯 Mission

Build a **production-grade Smart Triage Ticketing System** that automatically classifies and prioritizes customer support tickets using LLM intelligence, presenting them to authenticated agents via an elegant dashboard — engineered to **surpass FAANG standards**.

## 🏛️ Vision

A system where **every ticket finds its rightful place** — automatically categorized, intelligently prioritized, and seamlessly routed — so support agents can focus on what matters: **helping people**.

---

## 📐 Architecture at a Glance

```
┌──────────────────────────────────────────────────────────────────┐
│                         STTS UNIVERSE                            │
├──────────────┬──────────────────────────┬────────────────────────┤
│   FRONTEND   │        BACKEND           │      DATA LAYER        │
│              │                          │                        │
│  Next.js 14  │      FastAPI             │     MongoDB 7          │
│  App Router  │   (Clean Architecture)   │                        │
│  Tailwind    │                          │  tickets collection    │
│  Shadcn/ui   │   API → Service → Repo   │  agents collection     │
│              │                          │                        │
│  ┌────────┐  │   ┌──────────────────┐   │  ┌──────────────────┐  │
│  │ Submit │──│──→│  Ticket Router   │───│──│  tickets         │  │
│  │  Page  │  │   └──────┬───────────┘   │  │  - _id           │  │
│  └────────┘  │          │               │  │  - title         │  │
│  ┌────────┐  │   ┌──────▼───────────┐   │  │  - description   │  │
│  │ Login  │──│──→│  Ticket Service  │   │  │  - status        │  │
│  │  Page  │  │   └──────┬───────────┘   │  │  - category (AI) │  │
│  └────────┘  │          │               │  │  - priority (AI) │  │
│  ┌────────┐  │   ┌──────▼───────────┐   │  └──────────────────┘  │
│  │ Agent  │──│──→│  Triage Service  │   │                        │
│  │ Dash   │  │   │  (LLM Gateway)   │   │  ┌──────────────────┐  │
│  └────────┘  │   └──────┬───────────┘   │  │  agents          │  │
│              │          │               │  │  - _id           │  │
│              │   ┌──────▼───────────┐   │  │  - email         │  │
│              │   │  Circuit Breaker │   │  │  - hashed_pwd    │  │
│              │   │  + Retry Logic   │   │  │  - role          │  │
│              │   └──────┬───────────┘   │  └──────────────────┘  │
│              │          │               │                        │
│              │   ┌──────▼───────────┐   │                        │
│              │   │  Gemini / OpenAI │   │                        │
│              │   └──────────────────┘   │                        │
└──────────────┴──────────────────────────┴────────────────────────┘
```

---

## 🔧 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend** | FastAPI (Python 3.12) | Async-first, auto-docs, type-safe, production-proven |
| **Database** | MongoDB 7 (via Motor) | Document flexibility, async driver, schema evolution |
| **AI/LLM** | Google Gemini 1.5 Flash | Fast, cost-effective, excellent classification accuracy |
| **Auth** | JWT (python-jose + bcrypt) | Stateless, scalable, industry standard |
| **Frontend** | Next.js 14 + App Router | SSR/CSR hybrid, edge-ready, React ecosystem |
| **Styling** | Tailwind CSS + Shadcn/ui | Consistent design system, accessible components |
| **DevOps** | Docker Compose | Single-command local setup, portable |
| **Testing** | Pytest + httpx + coverage | Async-native, 80%+ coverage target |

---

## 🎭 User Journeys

### Journey 1: Customer Submits a Ticket

```
1. Customer visits the public submission page
2. Fills in: Title, Description, Email
3. Clicks "Submit" → loading animation
4. Backend creates ticket → triggers LLM classification
5. LLM returns: category="Billing", priority="High"
6. Customer sees: "✅ Ticket #12345 received!"
7. Ticket appears on agent dashboard with AI badges
```

### Journey 2: Agent Triages Tickets

```
1. Agent navigates to /login
2. Enters credentials → JWT token issued
3. Redirected to /dashboard (protected)
4. Sees Kanban board: Open | In Progress | Resolved
5. Tickets show: title, AI category, AI priority, customer email
6. Agent drags ticket from "Open" → "In Progress"
7. UI updates instantly (optimistic) → API confirms
8. Agent resolves ticket → moves to "Resolved" column
```

### Journey 3: LLM Goes Down (Resilience)

```
1. Customer submits ticket
2. LLM Gateway detects: 5 consecutive failures
3. Circuit breaker OPENS → stops calling LLM
4. Ticket saved as "untriaged" (no category/priority)
5. Agent sees ticket without AI badges → manually classifies
6. Circuit breaker probes every 60s → auto-recovers
7. New tickets get AI classification again
```

---

## 🧱 Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│              API Layer                   │
│   Routers + Input Validation + Auth     │
├─────────────────────────────────────────┤
│            Service Layer                 │
│   Business Logic + Orchestration        │
├─────────────────────────────────────────┤
│          Repository Layer                │
│   Data Access (MongoDB via Motor)       │
├─────────────────────────────────────────┤
│        Infrastructure Layer              │
│   LLM Gateway + JWT + Password Hash     │
└─────────────────────────────────────────┘
```

**Dependency Rule**: Inner layers NEVER depend on outer layers. The `TicketService` talks to `TicketRepository` through an **abstract interface** — not the concrete MongoDB implementation. This means we could swap MongoDB for PostgreSQL without touching a single line of business logic.

---

## 🔐 Security Model

| Aspect | Implementation |
|--------|---------------|
| **Password Storage** | bcrypt via `passlib.CryptContext` (auto-salted) |
| **Token Format** | JWT with HS256, 30-min expiry |
| **Auth Flow** | `OAuth2PasswordBearer` → FastAPI `Depends()` chain |
| **CORS** | Whitelisted frontend origin only |
| **Input Validation** | Pydantic models with `Field` constraints |
| **Rate Limiting** | Configurable per-endpoint limits |
| **Secrets** | `.env` file (never committed), `pydantic.BaseSettings` |

---

## 🧪 Testing Strategy

| Type | Tool | Coverage |
|------|------|----------|
| **Unit Tests** | Pytest + AsyncMock | Services, models, LLM gateway |
| **Integration Tests** | httpx.AsyncClient | Full API endpoint flows |
| **Coverage** | pytest-cov | ≥80% on `app/core/` |
| **LLM Mocking** | unittest.mock.patch | Deterministic, zero API cost |

```bash
# Run all tests with coverage
cd backend && pytest --cov=app --cov-report=term-missing -v

# Generate HTML coverage report
cd backend && pytest --cov=app --cov-report=html
```

---

## 📦 One-Command Setup

```bash
# Clone → Build → Run (entire stack)
docker-compose up --build

# Access:
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
# MongoDB:   localhost:27017
```

---

## 🔮 RBAC Extension (Future-Ready)

The system is architectured for RBAC from day one:

```python
class UserRole(str, Enum):
    ADMIN = "admin"         # Full access + agent management
    AGENT = "agent"         # View + update tickets
    READ_ONLY = "read_only" # View tickets only

# Permission decorator pattern
@router.patch("/tickets/{id}")
async def update_ticket(
    ticket_id: str,
    agent: Agent = Depends(require_role(UserRole.ADMIN, UserRole.AGENT))
):
    ...
```

## ⚡ LLM Failure Handling (Production-Grade)

```
                ┌──────────┐
     Request ──→│  CLOSED  │──→ LLM API
                └────┬─────┘
                     │ 5 failures
                ┌────▼─────┐
     Request ──→│   OPEN   │──→ Fallback (save untriaged)
                └────┬─────┘
                     │ 60s cooldown
                ┌────▼─────┐
   1 test req ──│HALF-OPEN │──→ LLM API (probe)
                └──────────┘
                     │ success → CLOSED
                     │ failure → OPEN
```

---

## 📋 Deliverables Summary

1. ✅ **GitHub Repository** — Complete codebase
2. ✅ **AI_JOURNEY.md** — 3 complex prompts + 1 hallucination fix
3. ✅ **docker-compose.yml** — Single-command setup
4. ✅ **80%+ Test Coverage** — Core business logic
5. ✅ **README.md** — RBAC + LLM failure explanations

---

*Allahu Musta'an — Allah is the One whose help is sought.*
*May Allah grant us success in this endeavor. Ameen.*
