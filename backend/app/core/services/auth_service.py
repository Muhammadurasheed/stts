"""
STTS Authentication Service
─────────────────────────────
Business logic for agent registration, login, and JWT token management.
"""

import logging

from app.common.exceptions import AuthenticationException, DuplicateException
from app.core.interfaces.agent_repo import AgentRepositoryInterface
from app.core.models.agent import (
    AgentCreate,
    AgentLogin,
    AgentResponse,
    TokenResponse,
)
from app.infrastructure.security.jwt_handler import create_access_token
from app.infrastructure.security.password import hash_password, verify_password

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication Service — handles agent registration, login, and identity.
    """

    def __init__(self, agent_repo: AgentRepositoryInterface):
        self.agent_repo = agent_repo

    async def register(self, data: AgentCreate) -> AgentResponse:
        """
        Register a new support agent.

        Raises:
            DuplicateException: If an agent with this email already exists.
        """
        # Check if email is already taken
        existing = await self.agent_repo.get_by_email(data.email)
        if existing:
            raise DuplicateException("Agent", "email")

        # Hash password and create agent
        hashed = hash_password(data.password)
        agent = await self.agent_repo.create(data, hashed)

        logger.info("New agent registered: %s (%s)", agent.full_name, agent.email)
        return agent

    async def login(self, data: AgentLogin) -> TokenResponse:
        """
        Authenticate an agent and return a JWT token.

        Raises:
            AuthenticationException: If credentials are invalid.
        """
        # Look up agent by email
        agent_doc = await self.agent_repo.get_by_email(data.email)
        if not agent_doc:
            raise AuthenticationException("Invalid email or password")

        # Verify password
        if not verify_password(data.password, agent_doc["hashed_password"]):
            raise AuthenticationException("Invalid email or password")

        # Check if agent is active
        if not agent_doc.get("is_active", True):
            raise AuthenticationException("Account is deactivated")

        # Create agent response (without password)
        agent_response = AgentResponse(
            id=agent_doc["id"],
            email=agent_doc["email"],
            full_name=agent_doc["full_name"],
            role=agent_doc.get("role", "agent"),
            is_active=agent_doc.get("is_active", True),
            created_at=agent_doc["created_at"],
        )

        # Issue JWT token
        access_token = create_access_token(subject=agent_response.id)

        logger.info("Agent logged in: %s", agent_response.email)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            agent=agent_response,
        )

    async def get_current_agent(self, agent_id: str) -> AgentResponse:
        """
        Get the agent profile by ID (used after JWT verification).

        Raises:
            AuthenticationException: If the agent is not found.
        """
        agent = await self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise AuthenticationException("Agent not found")
        return agent
