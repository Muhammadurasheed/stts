# 🏦 STTS — Smart Triage Ticketing System

> **"Engineering like Google, Designing like Apple."** 

STTS is a high-performance, AI-driven support ticketing architecture built to solve the chaos of high-volume customer inquiries. It leverages **Google Gemini 2.0 Flash** to instantly triage tickets with a robust multi-layer resilience strategy.

---

## 🏗 System Architecture

STTS follows a strict **Clean Architecture** pattern to ensure maintainability, testability, and scalability.

- **Frontend**: Next.js 16 (App Router) + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python 3.12)
- **Database**: MongoDB (Motor for Async IO)
- **AI Engine**: Google Gemini 2.0 via LLM Gateway
- **Auth**: JWT (Stateless) + Google Identity Services (OAuth)

---

## ✨ Premium Features

### 🧠 Intelligent Triage
Every ticket is analyzed by our LLM Gateway.
- **Auto-Priority**: Categorizes issues as High, Medium, or Low.
- **Auto-Categorization**: Routes tickets to Billing, Technical, General, or Feature Request.
- **AI Reasoning**: Explains *why* the AI chose the classification with a confidence score.
- **Graceful Degradation**: If the AI engine is down, the system falls back to a manual queue without interrupting the customer flow.

### 🛡 LLM Resilience Strategy
1. **Exponential Backoff**: Automatic retries for transient API failures.
2. **Circuit Breaker**: Stops sending requests to a failing AI engine to conserve resources and prevent cascading failures.
3. **Semantic Fallback**: Uses pre-defined heuristics if classification fails.

### 🎨 Apple-Grade UI/UX
- **Glassmorphism**: Subtle blur effects and transparent layers.
- **Micro-Animations**: Smooth transitions using CSS Keyframes and Framer-like motion.
- **Kanban Board**: Drag-and-drop workflow for agents.
- **Dark Mode Native**: A curated deep-zinc palette for reduced eye strain.

---

## 🚀 Quick Setup

### Backend
```bash
cd backend
python run.py  # Auto-activates venv!
```

### Frontend
```bash
cd frontend
npm run dev
```

### Environment Variables
Configure your `.env` with:
- `MONGODB_URL`
- `GEMINI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `JWT_SECRET_KEY`

---

## 🛡️ Situational Verification Tasks

### 1. Scaling to RBAC (Role-Based Access Control)
If we added **Admins** and **Read-Only** users, the architecture would evolve as follows:
- **Unified Identity**: Extend the `Agent` model with a `role: UserRole` enum ([Admin, Agent, Reader]).
- **Policy Enforcement**: Implement a centralized `requires_role(role)` dependency in [deps.py](file:///c:/Users/HP/Documents/stts/backend/app/api/deps.py).
- **Endpoint Protection**:
    - `POST /tickets`: Public Access (No change).
    - `GET /tickets`: Accessible by all authenticated roles.
    - `PATCH/PUT /tickets`: Restricted to `Agent` and `Admin`.
    - `DELETE /tickets`: Restricted to `Admin` only.
- **Frontend**: Conditionally render the "Resolve" and "Delete" actions based on the agent's role claim in the JWT.

### 2. Handling LLM Failure (Graceful Degradation)
Our system is built with a "Safety-First" AI integration:
- **Resilient Circuit Breaker**: The [LLMGateway](file:///c:/Users/HP/Documents/stts/backend/app/infrastructure/llm/gateway.py) monitors failure rates. If the Gemini API returns errors or times out 5 times, the circuit opens for 60 seconds.
- **Async Execution**: Triage happens asynchronously. Even if the LLM call is slow, the initial ticket submission remains instant.
- **State Fallback**: If triage fails (due to timeout, error, or open circuit), the `TicketService` catches the exception and saves the ticket as `Untriaged`.
- **Result**: The system remains **100% available** for customers to submit tickets. Agents can later manually refresh the triage once the service recovers.

---

## 🔐 Auth & Security
- **RBAC**: Role-Based Access Control ready.
- **Password Hashing**: Bcrypt with adaptive salt.
- **Sanitization**: Pydantic v2 validation for all API inputs.
- **Stateless**: Secured by JWT with token persistence.

---

## 📊 Testing & Coverage
- **Unit Tests**: 75+ tests covering all core logic.
- **Coverage**: **88.19%** (Focusing on business logic and security).

---

Built with ❤️ for the **Codematic Technical Assessment**.
