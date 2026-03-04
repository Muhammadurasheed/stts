"""
STTS Auth Service Tests
────────────────────────
Tests for agent registration, login, and token management.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.common.exceptions import AuthenticationException, DuplicateException
from app.core.models.agent import AgentCreate, AgentLogin, AgentResponse, AgentRole
from app.core.services.auth_service import AuthService


@pytest.fixture
def mock_agent_repo():
    """Create a mock agent repository."""
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def auth_service(mock_agent_repo):
    """Create AuthService with mocked repository."""
    return AuthService(mock_agent_repo), mock_agent_repo


class TestAuthService:
    """Test suite for AuthService."""

    @pytest.mark.asyncio
    async def test_register_success(self, auth_service):
        """Test successful agent registration."""
        service, repo = auth_service
        repo.get_by_email.return_value = None  # No existing agent
        repo.create.return_value = AgentResponse(
            id="507f1f77bcf86cd799439011",
            email="agent@stts.com",
            full_name="Test Agent",
            role=AgentRole.AGENT,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        data = AgentCreate(
            email="agent@stts.com",
            password="secureP@ss123",
            full_name="Test Agent",
        )

        result = await service.register(data)

        assert result.email == "agent@stts.com"
        assert result.full_name == "Test Agent"
        repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, auth_service):
        """Test registration fails with duplicate email."""
        service, repo = auth_service
        repo.get_by_email.return_value = {"email": "agent@stts.com"}  # Already exists

        data = AgentCreate(
            email="agent@stts.com",
            password="secureP@ss123",
            full_name="Test Agent",
        )

        with pytest.raises(DuplicateException):
            await service.register(data)

    @pytest.mark.asyncio
    @patch("app.core.services.auth_service.verify_password", return_value=True)
    @patch("app.core.services.auth_service.create_access_token", return_value="mock_jwt_token")
    async def test_login_success(self, mock_token, mock_verify, auth_service):
        """Test successful login returns a JWT token."""
        service, repo = auth_service
        repo.get_by_email.return_value = {
            "id": "507f1f77bcf86cd799439011",
            "email": "agent@stts.com",
            "full_name": "Test Agent",
            "hashed_password": "hashed_value",
            "role": "agent",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }

        data = AgentLogin(email="agent@stts.com", password="secureP@ss123")
        result = await service.login(data)

        assert result.access_token == "mock_jwt_token"
        assert result.token_type == "bearer"
        assert result.agent.email == "agent@stts.com"

    @pytest.mark.asyncio
    async def test_login_agent_not_found(self, auth_service):
        """Test login fails when agent doesn't exist."""
        service, repo = auth_service
        repo.get_by_email.return_value = None

        data = AgentLogin(email="unknown@stts.com", password="secureP@ss123")

        with pytest.raises(AuthenticationException):
            await service.login(data)

    @pytest.mark.asyncio
    @patch("app.core.services.auth_service.verify_password", return_value=False)
    async def test_login_wrong_password(self, mock_verify, auth_service):
        """Test login fails with wrong password."""
        service, repo = auth_service
        repo.get_by_email.return_value = {
            "id": "507f1f77bcf86cd799439011",
            "email": "agent@stts.com",
            "full_name": "Test Agent",
            "hashed_password": "hashed_value",
            "role": "agent",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }

        data = AgentLogin(email="agent@stts.com", password="wrongpassword")

        with pytest.raises(AuthenticationException):
            await service.login(data)

    @pytest.mark.asyncio
    async def test_get_current_agent_success(self, auth_service):
        """Test getting current agent by ID."""
        service, repo = auth_service
        repo.get_by_id.return_value = AgentResponse(
            id="507f1f77bcf86cd799439011",
            email="agent@stts.com",
            full_name="Test Agent",
            role=AgentRole.AGENT,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        result = await service.get_current_agent("507f1f77bcf86cd799439011")
        assert result.email == "agent@stts.com"

    @pytest.mark.asyncio
    async def test_get_current_agent_not_found(self, auth_service):
        """Test getting current agent fails when not found."""
        service, repo = auth_service
        repo.get_by_id.return_value = None

        with pytest.raises(AuthenticationException):
            await service.get_current_agent("nonexistent_id")

    @pytest.mark.asyncio
    @patch("app.core.services.auth_service.id_token.verify_oauth2_token")
    @patch("app.core.services.auth_service.create_access_token", return_value="mock_jwt_token")
    async def test_google_login_new_user_success(self, mock_jwt, mock_verify, auth_service):
        """Test Google login with a new user (JIT creation)."""
        service, repo = auth_service
        
        # Mock Google Token content
        mock_verify.return_value = {
            "sub": "google_123",
            "email": "new@gmail.com",
            "name": "New User",
            "picture": "http://image.com/pic.jpg"
        }

        # Mock repo: User not found by ID, not found by email
        repo.get_by_google_id = AsyncMock(return_value=None)
        repo.get_by_email.return_value = None
        
        repo.create.return_value = AgentResponse(
            id="new_id",
            email="new@gmail.com",
            full_name="New User",
            role=AgentRole.AGENT,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        result = await service.google_login("valid_token")

        assert result.access_token == "mock_jwt_token"
        assert result.agent.email == "new@gmail.com"
        repo.create.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.core.services.auth_service.verify_password", return_value=True)
    async def test_login_blocks_google_user_password_bypass(self, mock_verify, auth_service):
        """Test that Google-auth agents cannot log in via email/password."""
        service, repo = auth_service
        
        # An agent that has a google_id but NO hashed_password
        repo.get_by_email.return_value = {
            "id": "google_user_id",
            "email": "google@gmail.com",
            "hashed_password": None,  # Critical: no password set
            "google_id": "google_123",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }

        data = AgentLogin(email="google@gmail.com", password="some_password")

        with pytest.raises(AuthenticationException) as exc:
            await service.login(data)
        
        assert "uses Google Sign-In" in str(exc.value)
