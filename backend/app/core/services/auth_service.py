"""
STTS Authentication Service
─────────────────────────────
Business logic for agent registration, login, and JWT token management.
"""

import logging

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.common.exceptions import AuthenticationException, DuplicateException, STTSException
from app.core.interfaces.agent_repo import AgentRepositoryInterface
from app.core.models.agent import (
    AgentCreate,
    AgentLogin,
    AgentResponse,
    TokenResponse,
)
from app.config import get_settings
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

        # Block Google-auth agents from email/password login
        if agent_doc.get("google_id") and agent_doc.get("hashed_password") is None:
            raise AuthenticationException(
                "This account uses Google Sign-In. Please use the Google login button."
            )

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

    async def google_login(self, token: str) -> TokenResponse:
        """
        Verify Google ID token and return/create agent session.
        This handles both login and JIT registration for Google users.
        """
        try:
            settings = get_settings()
            
            # Verify the ID token using Google's libraries
            id_info = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )

            # Token is valid. Get user info.
            google_id = id_info['sub']
            email = id_info['email']
            name = id_info.get('name', email.split('@')[0])
            picture = id_info.get('picture')

            # Check if agent exists by Google ID
            agent_doc = await self.agent_repo.get_by_google_id(google_id)
            
            if not agent_doc:
                # Check if agent exists by email (link accounts)
                existing_email_agent = await self.agent_repo.get_by_email(email)
                if existing_email_agent:
                    # Link account strategy
                    agent_id = existing_email_agent["id"]
                    agent_data = existing_email_agent
                    # Update with google_id
                    # Note: Repo might need an 'update_google_id' method, but for now we continue
                else:
                    # JIT Create new agent
                    agent_create = AgentCreate(
                        email=email,
                        full_name=name,
                        password="GOOGLE_AUTH_SESSION_ONLY" 
                    )
                    agent_response = await self.agent_repo.create(
                        agent_create, 
                        google_id=google_id,
                        picture_url=picture
                    )
                    agent_id = agent_response.id
                    agent_data = agent_response
            else:
                agent_id = agent_doc["id"]
                agent_data = agent_doc

            # Prepare response profile
            if hasattr(agent_data, 'model_dump'):
                agent_profile = agent_data
            elif isinstance(agent_data, dict):
                agent_profile = AgentResponse(
                    id=agent_data.get("id") or str(agent_data.get("_id")),
                    email=agent_data["email"],
                    full_name=agent_data["full_name"],
                    role=agent_data.get("role", "agent"),
                    is_active=agent_data.get("is_active", True),
                    google_id=agent_data.get("google_id"),
                    picture_url=agent_data.get("picture_url"),
                    created_at=agent_data["created_at"],
                )
            else:
                raise STTSException("Internal error: Could not process agent profile")

            access_token = create_access_token(subject=agent_profile.id)
            
            logger.info("Agent logged in via Google: %s", agent_profile.email)
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                agent=agent_profile
            )
            
        except ValueError as e:
            logger.warning("Invalid Google token: %s", str(e))
            raise AuthenticationException(f"Invalid Google token: {str(e)}")
        except (AuthenticationException, STTSException):
            raise  # Don't re-wrap our own exceptions
        except Exception as e:
            logger.error("Google login failed: %s", str(e))
            raise STTSException(f"Google login failed: {str(e)}")

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
