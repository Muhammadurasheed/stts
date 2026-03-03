"""
STTS Triage Service Tests
───────────────────────────
Tests for the AI triage classification pipeline.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.models.ticket import TicketCategory, TicketPriority, TriageResult
from app.core.services.triage_service import TriageService
from app.infrastructure.llm.gateway import LLMGateway


@pytest.fixture
def triage_service_with_gateway():
    """Create a TriageService with a mocked LLM Gateway."""
    mock_gateway = MagicMock(spec=LLMGateway)
    mock_gateway.classify_ticket = AsyncMock()
    service = TriageService(mock_gateway)
    return service, mock_gateway


class TestTriageService:
    """Test suite for TriageService."""

    @pytest.mark.asyncio
    async def test_classify_ticket_success(self, triage_service_with_gateway):
        """Test successful ticket classification."""
        service, mock_gateway = triage_service_with_gateway

        expected_result = TriageResult(
            category=TicketCategory.BILLING,
            priority=TicketPriority.HIGH,
            confidence=0.95,
            reasoning="Customer reports a billing dashboard error (500 status).",
        )
        mock_gateway.classify_ticket.return_value = expected_result

        result = await service.classify_ticket(
            title="Cannot access billing dashboard",
            description="Page shows a 500 error when clicking Billing.",
        )

        assert result is not None
        assert result.category == TicketCategory.BILLING
        assert result.priority == TicketPriority.HIGH
        assert result.confidence == 0.95
        mock_gateway.classify_ticket.assert_called_once()

    @pytest.mark.asyncio
    async def test_classify_ticket_llm_unavailable(self, triage_service_with_gateway):
        """Test graceful degradation when LLM is unavailable."""
        service, mock_gateway = triage_service_with_gateway
        mock_gateway.classify_ticket.return_value = None

        result = await service.classify_ticket(
            title="Some issue",
            description="Some details about the issue.",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_classify_ticket_exception_handling(self, triage_service_with_gateway):
        """Test that exceptions are caught and don't propagate."""
        service, mock_gateway = triage_service_with_gateway
        mock_gateway.classify_ticket.side_effect = Exception("API Error")

        result = await service.classify_ticket(
            title="Some issue",
            description="Some details.",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_classify_ticket_feature_request(self, triage_service_with_gateway):
        """Test classification of a feature request."""
        service, mock_gateway = triage_service_with_gateway

        expected = TriageResult(
            category=TicketCategory.FEATURE_REQUEST,
            priority=TicketPriority.LOW,
            confidence=0.88,
            reasoning="Customer is requesting a new feature.",
        )
        mock_gateway.classify_ticket.return_value = expected

        result = await service.classify_ticket(
            title="Add dark mode",
            description="It would be great to have a dark mode option.",
        )

        assert result.category == TicketCategory.FEATURE_REQUEST
        assert result.priority == TicketPriority.LOW

    @pytest.mark.asyncio
    async def test_classify_ticket_technical_bug(self, triage_service_with_gateway):
        """Test classification of a technical bug."""
        service, mock_gateway = triage_service_with_gateway

        expected = TriageResult(
            category=TicketCategory.TECHNICAL_BUG,
            priority=TicketPriority.HIGH,
            confidence=0.97,
            reasoning="System crash with data loss risk.",
        )
        mock_gateway.classify_ticket.return_value = expected

        result = await service.classify_ticket(
            title="Application crashes on startup",
            description="The app crashes immediately after login. My data might be corrupted.",
        )

        assert result.category == TicketCategory.TECHNICAL_BUG
        assert result.priority == TicketPriority.HIGH
        assert result.confidence == 0.97
