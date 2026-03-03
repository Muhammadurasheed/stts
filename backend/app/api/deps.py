"""
STTS API Dependency Injection
──────────────────────────────
FastAPI `Depends()` chain for injecting services and authentication.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.common.exceptions import AuthenticationException
from app.core.models.agent import AgentResponse
from app.core.services.auth_service import AuthService
from app.core.services.ticket_service import TicketService
from app.core.services.triage_service import TriageService
from app.infrastructure.database.mongodb import get_database
from app.infrastructure.llm.gateway import LLMGateway
from app.infrastructure.repositories.mongo_agent_repo import MongoAgentRepository
from app.infrastructure.repositories.mongo_ticket_repo import MongoTicketRepository
from app.infrastructure.security.jwt_handler import decode_access_token

# OAuth2 scheme — extracts Bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Singleton LLM Gateway (shared across requests)
_llm_gateway: LLMGateway | None = None


def get_llm_gateway() -> LLMGateway:
    """Get or create the singleton LLM Gateway instance."""
    global _llm_gateway
    if _llm_gateway is None:
        _llm_gateway = LLMGateway()
    return _llm_gateway


# ── Repository Dependencies ───────────────────────────────────


def get_ticket_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> MongoTicketRepository:
    """Inject MongoTicketRepository."""
    return MongoTicketRepository(db)


def get_agent_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> MongoAgentRepository:
    """Inject MongoAgentRepository."""
    return MongoAgentRepository(db)


# ── Service Dependencies ──────────────────────────────────────


def get_triage_service(
    llm_gateway: LLMGateway = Depends(get_llm_gateway),
) -> TriageService:
    """Inject TriageService."""
    return TriageService(llm_gateway)


def get_ticket_service(
    ticket_repo: MongoTicketRepository = Depends(get_ticket_repo),
    triage_service: TriageService = Depends(get_triage_service),
) -> TicketService:
    """Inject TicketService with its dependencies."""
    return TicketService(ticket_repo, triage_service)


def get_auth_service(
    agent_repo: MongoAgentRepository = Depends(get_agent_repo),
) -> AuthService:
    """Inject AuthService."""
    return AuthService(agent_repo)


# ── Authentication Dependencies ───────────────────────────────


async def get_current_agent(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> AgentResponse:
    """
    Decode the JWT token and return the authenticated agent.

    Used as a dependency on protected endpoints.
    """
    try:
        agent_id = decode_access_token(token)
        return await auth_service.get_current_agent(agent_id)
    except AuthenticationException:
        raise
    except Exception:
        raise AuthenticationException("Could not validate credentials")
