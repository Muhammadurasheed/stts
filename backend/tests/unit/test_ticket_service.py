"""
STTS Ticket Service Tests
───────────────────────────
Tests for the ticket lifecycle orchestration.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import NotFoundException, ValidationException
from app.core.models.ticket import (
    TicketCategory,
    TicketCreate,
    TicketListResponse,
    TicketPriority,
    TicketResponse,
    TicketStatus,
    TicketStatusUpdate,
    TriageResult,
)
from app.core.services.ticket_service import TicketService
from app.core.services.triage_service import TriageService


@pytest.fixture
def mock_dependencies():
    """Create mocked ticket repository and triage service."""
    ticket_repo = MagicMock()
    ticket_repo.create = AsyncMock()
    ticket_repo.get_by_id = AsyncMock()
    ticket_repo.list = AsyncMock()
    ticket_repo.count = AsyncMock()
    ticket_repo.update_status = AsyncMock()
    ticket_repo.update_triage = AsyncMock()

    triage_svc = MagicMock(spec=TriageService)
    triage_svc.classify_ticket = AsyncMock()

    service = TicketService(ticket_repo, triage_svc)
    return service, ticket_repo, triage_svc


def _make_ticket(**overrides) -> TicketResponse:
    """Helper to create a TicketResponse with defaults."""
    now = datetime.now(timezone.utc)
    defaults = {
        "id": "507f1f77bcf86cd799439011",
        "title": "Test ticket",
        "description": "Test description for validation purposes.",
        "customer_email": "user@example.com",
        "status": TicketStatus.OPEN,
        "priority": None,
        "category": None,
        "ai_confidence": None,
        "ai_reasoning": None,
        "created_at": now,
        "updated_at": now,
        "resolved_at": None,
    }
    defaults.update(overrides)
    return TicketResponse(**defaults)


class TestTicketService:
    """Test suite for TicketService."""

    @pytest.mark.asyncio
    async def test_create_ticket_with_triage(self, mock_dependencies):
        """Test ticket creation with successful AI triage."""
        service, repo, triage = mock_dependencies

        created = _make_ticket()
        triaged = _make_ticket(
            category=TicketCategory.BILLING,
            priority=TicketPriority.HIGH,
            ai_confidence=0.95,
        )

        repo.create.return_value = created
        triage.classify_ticket.return_value = TriageResult(
            category=TicketCategory.BILLING,
            priority=TicketPriority.HIGH,
            confidence=0.95,
            reasoning="Billing issue",
        )
        repo.update_triage.return_value = triaged

        data = TicketCreate(
            title="Cannot access billing",
            description="Getting a 500 error on the billing page since yesterday.",
            customer_email="user@example.com",
        )

        result = await service.create_ticket(data)

        repo.create.assert_called_once_with(data)
        triage.classify_ticket.assert_called_once()
        repo.update_triage.assert_called_once()
        assert result.category == TicketCategory.BILLING

    @pytest.mark.asyncio
    async def test_create_ticket_triage_fails_gracefully(self, mock_dependencies):
        """Test ticket is still created when AI triage fails."""
        service, repo, triage = mock_dependencies

        created = _make_ticket()
        repo.create.return_value = created
        triage.classify_ticket.return_value = None  # LLM unavailable

        data = TicketCreate(
            title="Some issue",
            description="Some description with enough characters.",
            customer_email="user@example.com",
        )

        result = await service.create_ticket(data)

        repo.create.assert_called_once()
        assert result.id == created.id
        # Triage update should NOT be called when result is None
        repo.update_triage.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_ticket_triage_exception(self, mock_dependencies):
        """Test ticket creation succeeds even with triage exception."""
        service, repo, triage = mock_dependencies

        created = _make_ticket()
        repo.create.return_value = created
        triage.classify_ticket.side_effect = Exception("LLM crash")

        data = TicketCreate(
            title="Another issue",
            description="Some description for the ticket creation test.",
            customer_email="user@example.com",
        )

        result = await service.create_ticket(data)
        assert result.id == created.id  # Ticket still created

    @pytest.mark.asyncio
    async def test_get_ticket_success(self, mock_dependencies):
        """Test getting existing ticket by ID."""
        service, repo, _ = mock_dependencies

        ticket = _make_ticket()
        repo.get_by_id.return_value = ticket

        result = await service.get_ticket("507f1f77bcf86cd799439011")
        assert result.id == ticket.id

    @pytest.mark.asyncio
    async def test_get_ticket_not_found(self, mock_dependencies):
        """Test getting non-existent ticket raises NotFoundException."""
        service, repo, _ = mock_dependencies
        repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_ticket("nonexistent_id")

    @pytest.mark.asyncio
    async def test_list_tickets(self, mock_dependencies):
        """Test listing tickets with pagination."""
        service, repo, _ = mock_dependencies

        tickets = [_make_ticket(id=f"id_{i}") for i in range(3)]
        repo.list.return_value = tickets
        repo.count.return_value = 3

        result = await service.list_tickets(filters={}, page=1, page_size=20)

        assert isinstance(result, TicketListResponse)
        assert len(result.items) == 3
        assert result.total == 3
        assert result.page == 1
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_list_tickets_with_filters(self, mock_dependencies):
        """Test listing tickets with status and priority filters."""
        service, repo, _ = mock_dependencies

        repo.list.return_value = []
        repo.count.return_value = 0

        result = await service.list_tickets(
            filters={"status": "Open", "priority": "High"},
            page=1,
            page_size=10,
        )

        assert result.total == 0
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_update_ticket_status_open_to_in_progress(self, mock_dependencies):
        """Test transitioning ticket from Open to In Progress."""
        service, repo, _ = mock_dependencies

        existing = _make_ticket(status=TicketStatus.OPEN)
        updated = _make_ticket(status=TicketStatus.IN_PROGRESS)

        repo.get_by_id.return_value = existing
        repo.update_status.return_value = updated

        update = TicketStatusUpdate(status=TicketStatus.IN_PROGRESS)
        result = await service.update_ticket_status("507f1f77bcf86cd799439011", update)

        assert result.status == TicketStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_update_ticket_status_to_resolved(self, mock_dependencies):
        """Test resolving a ticket."""
        service, repo, _ = mock_dependencies

        existing = _make_ticket(status=TicketStatus.IN_PROGRESS)
        updated = _make_ticket(status=TicketStatus.RESOLVED)

        repo.get_by_id.return_value = existing
        repo.update_status.return_value = updated

        update = TicketStatusUpdate(status=TicketStatus.RESOLVED)
        result = await service.update_ticket_status("507f1f77bcf86cd799439011", update)

        assert result.status == TicketStatus.RESOLVED

    @pytest.mark.asyncio
    async def test_update_ticket_status_reopen(self, mock_dependencies):
        """Test reopening a resolved ticket."""
        service, repo, _ = mock_dependencies

        existing = _make_ticket(status=TicketStatus.RESOLVED)
        updated = _make_ticket(status=TicketStatus.OPEN)

        repo.get_by_id.return_value = existing
        repo.update_status.return_value = updated

        update = TicketStatusUpdate(status=TicketStatus.OPEN)
        result = await service.update_ticket_status("507f1f77bcf86cd799439011", update)

        assert result.status == TicketStatus.OPEN

    @pytest.mark.asyncio
    async def test_update_ticket_not_found(self, mock_dependencies):
        """Test updating non-existent ticket raises NotFoundException."""
        service, repo, _ = mock_dependencies
        repo.get_by_id.return_value = None

        update = TicketStatusUpdate(status=TicketStatus.IN_PROGRESS)
        with pytest.raises(NotFoundException):
            await service.update_ticket_status("nonexistent", update)

    @pytest.mark.asyncio
    async def test_update_ticket_same_status(self, mock_dependencies):
        """Test that updating to the same status raises ValidationException."""
        service, repo, _ = mock_dependencies
        existing = _make_ticket(status=TicketStatus.OPEN)
        repo.get_by_id.return_value = existing

        update = TicketStatusUpdate(status=TicketStatus.OPEN)
        with pytest.raises(ValidationException):
            await service.update_ticket_status("507f1f77bcf86cd799439011", update)

    @pytest.mark.asyncio
    async def test_invalid_status_transition(self, mock_dependencies):
        """Test that invalid transitions raise ValidationException."""
        service, repo, _ = mock_dependencies
        existing = _make_ticket(status=TicketStatus.RESOLVED)
        repo.get_by_id.return_value = existing

        # Resolved → In Progress is not valid
        update = TicketStatusUpdate(status=TicketStatus.IN_PROGRESS)
        with pytest.raises(ValidationException):
            await service.update_ticket_status("507f1f77bcf86cd799439011", update)

    @pytest.mark.asyncio
    async def test_update_status_repo_returns_none(self, mock_dependencies):
        """Test that update failing at repo level raises NotFoundException."""
        service, repo, _ = mock_dependencies
        existing = _make_ticket(status=TicketStatus.OPEN)
        repo.get_by_id.return_value = existing
        repo.update_status.return_value = None  # Repo couldn't update

        update = TicketStatusUpdate(status=TicketStatus.IN_PROGRESS)
        with pytest.raises(NotFoundException):
            await service.update_ticket_status("507f1f77bcf86cd799439011", update)
