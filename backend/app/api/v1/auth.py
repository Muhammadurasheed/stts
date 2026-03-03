"""
STTS Authentication API Endpoints
───────────────────────────────────
REST endpoints for agent auth (register, login, profile).
"""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service, get_current_agent
from app.core.models.agent import (
    AgentCreate,
    AgentLogin,
    AgentResponse,
    TokenResponse,
)
from app.core.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new support agent",
    description="Create a new support agent account. Returns the agent profile.",
)
async def register(
    data: AgentCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> AgentResponse:
    """Register a new support agent (public)."""
    return await auth_service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get JWT token",
    description="Authenticate with email/password. Returns a JWT access token.",
)
async def login(
    data: AgentLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Login with email and password, receive JWT token."""
    return await auth_service.login(data)


@router.get(
    "/me",
    response_model=AgentResponse,
    summary="Get current agent profile",
    description="Returns the profile of the currently authenticated agent.",
)
async def get_me(
    agent: AgentResponse = Depends(get_current_agent),
) -> AgentResponse:
    """Get the current authenticated agent's profile."""
    return agent
