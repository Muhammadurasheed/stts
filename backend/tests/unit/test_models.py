"""
STTS Model Validation Tests
─────────────────────────────
Tests for Pydantic model validation — ensures data integrity.
"""

import pytest
from pydantic import ValidationError

from app.core.models.ticket import (
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketStatus,
    TicketStatusUpdate,
    TriageResult,
)
from app.core.models.agent import AgentCreate, AgentLogin


class TestTicketCreate:
    """Tests for TicketCreate model validation."""

    def test_valid_ticket(self):
        """Test creating a valid ticket."""
        ticket = TicketCreate(
            title="Cannot login to my account",
            description="I keep getting a 401 error when trying to log in with my credentials.",
            customer_email="user@example.com",
        )
        assert ticket.title == "Cannot login to my account"
        assert ticket.customer_email == "user@example.com"

    def test_title_too_short(self):
        """Test that title must be at least 3 characters."""
        with pytest.raises(ValidationError) as exc_info:
            TicketCreate(
                title="Hi",
                description="Valid description that is long enough for validation.",
                customer_email="user@example.com",
            )
        assert "String should have at least 3 characters" in str(exc_info.value)

    def test_description_too_short(self):
        """Test that description must be at least 10 characters."""
        with pytest.raises(ValidationError):
            TicketCreate(
                title="Valid title",
                description="Short",
                customer_email="user@example.com",
            )

    def test_invalid_email(self):
        """Test that email must be valid."""
        with pytest.raises(ValidationError):
            TicketCreate(
                title="Valid title",
                description="Valid description that is long enough.",
                customer_email="not-an-email",
            )

    def test_missing_required_fields(self):
        """Test that all required fields must be present."""
        with pytest.raises(ValidationError):
            TicketCreate()


class TestTicketStatusUpdate:
    """Tests for TicketStatusUpdate model."""

    def test_valid_status_update(self):
        """Test valid status update."""
        update = TicketStatusUpdate(status=TicketStatus.IN_PROGRESS)
        assert update.status == TicketStatus.IN_PROGRESS

    def test_invalid_status(self):
        """Test invalid status value."""
        with pytest.raises(ValidationError):
            TicketStatusUpdate(status="Invalid Status")


class TestTriageResult:
    """Tests for TriageResult model."""

    def test_full_triage_result(self):
        """Test complete triage result."""
        result = TriageResult(
            category=TicketCategory.TECHNICAL_BUG,
            priority=TicketPriority.HIGH,
            confidence=0.92,
            reasoning="Critical system error reported.",
        )
        assert result.category == TicketCategory.TECHNICAL_BUG
        assert result.confidence == 0.92

    def test_empty_triage_result(self):
        """Test triage result with no classification (LLM failed)."""
        result = TriageResult()
        assert result.category is None
        assert result.priority is None
        assert result.confidence is None

    def test_confidence_clamping_bounds(self):
        """Test that confidence must be between 0 and 1."""
        with pytest.raises(ValidationError):
            TriageResult(confidence=1.5)

        with pytest.raises(ValidationError):
            TriageResult(confidence=-0.1)


class TestAgentCreate:
    """Tests for AgentCreate model."""

    def test_valid_agent(self):
        """Test creating a valid agent."""
        agent = AgentCreate(
            email="agent@stts.com",
            password="secureP@ss123",
            full_name="Test Agent",
        )
        assert agent.email == "agent@stts.com"

    def test_password_too_short(self):
        """Test that password must be at least 8 characters."""
        with pytest.raises(ValidationError):
            AgentCreate(
                email="agent@stts.com",
                password="short",
                full_name="Test Agent",
            )

    def test_invalid_email(self):
        """Test that agent email must be valid."""
        with pytest.raises(ValidationError):
            AgentCreate(
                email="not-valid",
                password="secureP@ss123",
                full_name="Test Agent",
            )


class TestAgentLogin:
    """Tests for AgentLogin model."""

    def test_valid_login(self):
        """Test valid login payload."""
        login = AgentLogin(email="agent@stts.com", password="secureP@ss123")
        assert login.email == "agent@stts.com"


class TestEnums:
    """Test enum values and coverage."""

    def test_ticket_statuses(self):
        assert TicketStatus.OPEN.value == "Open"
        assert TicketStatus.IN_PROGRESS.value == "In Progress"
        assert TicketStatus.RESOLVED.value == "Resolved"

    def test_ticket_priorities(self):
        assert TicketPriority.HIGH.value == "High"
        assert TicketPriority.MEDIUM.value == "Medium"
        assert TicketPriority.LOW.value == "Low"

    def test_ticket_categories(self):
        assert len(TicketCategory) == 5
        assert TicketCategory.BILLING.value == "Billing"
        assert TicketCategory.TECHNICAL_BUG.value == "Technical Bug"
