"""
STTS Test Configuration & Shared Fixtures
───────────────────────────────────────────
Provides reusable fixtures for all tests.
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_current_agent, get_database, get_llm_gateway
from app.core.models.agent import AgentResponse, AgentRole
from app.infrastructure.llm.gateway import LLMGateway
from app.main import app


# ── Event Loop ─────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Mock Database ──────────────────────────────────────────────
@pytest.fixture
def mock_db():
    """Create a mock MongoDB database."""
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=MagicMock())
    return db


# ── Mock LLM Gateway ──────────────────────────────────────────
@pytest.fixture
def mock_llm_gateway():
    """Create a mock LLM Gateway."""
    gateway = MagicMock(spec=LLMGateway)
    gateway.classify_ticket = AsyncMock()
    return gateway


# ── Mock Authenticated Agent ──────────────────────────────────
@pytest.fixture
def mock_agent():
    """Create a mock authenticated agent."""
    return AgentResponse(
        id="507f1f77bcf86cd799439011",
        email="agent@stts.com",
        full_name="Test Agent",
        role=AgentRole.AGENT,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


# ── Async HTTP Client ─────────────────────────────────────────
@pytest_asyncio.fixture
async def async_client(mock_db, mock_llm_gateway, mock_agent):
    """
    Create an async HTTP test client with mocked dependencies.

    Overrides:
    - Database → mock MongoDB
    - LLM Gateway → mock (no real API calls)
    - Authentication → mock agent (bypass JWT)
    """

    # Override dependencies
    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_llm_gateway] = lambda: mock_llm_gateway
    app.dependency_overrides[get_current_agent] = lambda: mock_agent

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clean up overrides
    app.dependency_overrides.clear()


# ── Sample Data ────────────────────────────────────────────────
@pytest.fixture
def sample_ticket_data():
    """Sample ticket creation data."""
    return {
        "title": "Cannot access billing dashboard",
        "description": "When I click on Billing in the sidebar, the page shows a 500 error. "
        "I've tried refreshing and clearing cache but the issue persists.",
        "customer_email": "customer@example.com",
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent registration data."""
    return {
        "email": "newagent@stts.com",
        "password": "secureP@ss123",
        "full_name": "New Agent",
    }
