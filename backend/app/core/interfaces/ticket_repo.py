"""
STTS Abstract Ticket Repository Interface
───────────────────────────────────────────
Defines the contract for ticket data access.
Business logic depends on this interface, not the concrete MongoDB implementation.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.core.models.ticket import TicketCreate, TicketResponse, TriageResult


class TicketRepositoryInterface(ABC):
    """Abstract interface for ticket persistence operations."""

    @abstractmethod
    async def create(self, ticket_data: TicketCreate) -> TicketResponse:
        """Create a new ticket and return it."""
        ...

    @abstractmethod
    async def get_by_id(self, ticket_id: str) -> Optional[TicketResponse]:
        """Find a ticket by its ID. Returns None if not found."""
        ...

    @abstractmethod
    async def list(
        self,
        filters: dict[str, Any],
        skip: int = 0,
        limit: int = 20,
    ) -> list[TicketResponse]:
        """List tickets with optional filters, pagination."""
        ...

    @abstractmethod
    async def count(self, filters: dict[str, Any]) -> int:
        """Count tickets matching the given filters."""
        ...

    @abstractmethod
    async def update_status(self, ticket_id: str, status: str) -> Optional[TicketResponse]:
        """Update the status of a ticket. Returns updated ticket or None."""
        ...

    @abstractmethod
    async def update_triage(self, ticket_id: str, triage: TriageResult) -> Optional[TicketResponse]:
        """Update AI triage results for a ticket."""
        ...
