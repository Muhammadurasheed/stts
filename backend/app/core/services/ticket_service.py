"""
STTS Ticket Service
────────────────────
Core business logic for ticket lifecycle management.
"""

import logging
from typing import Any, Optional

from app.common.exceptions import NotFoundException, ValidationException
from app.core.interfaces.ticket_repo import TicketRepositoryInterface
from app.core.models.ticket import (
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketStatus,
    TicketStatusUpdate,
)
from app.core.services.triage_service import TriageService

logger = logging.getLogger(__name__)


class TicketService:
    """
    Ticket Service — orchestrates the complete ticket lifecycle.

    - Create ticket → trigger AI triage
    - List tickets with filtering and pagination
    - Update ticket status with validation
    """

    def __init__(
        self,
        ticket_repo: TicketRepositoryInterface,
        triage_service: TriageService,
    ):
        self.ticket_repo = ticket_repo
        self.triage_service = triage_service

    async def create_ticket(self, data: TicketCreate) -> TicketResponse:
        """
        Create a new ticket and run AI triage classification.

        The ticket is always saved, even if AI triage fails (graceful degradation).
        """
        logger.info("Creating ticket: '%s' from %s", data.title, data.customer_email)

        # 1. Create the ticket in the database
        ticket = await self.ticket_repo.create(data)
        logger.info("Ticket created with ID: %s", ticket.id)

        # 2. Run AI triage (non-blocking — ticket already saved)
        try:
            triage_result = await self.triage_service.classify_ticket(
                title=data.title,
                description=data.description,
            )

            # 3. Update ticket with AI classification results
            if triage_result:
                updated_ticket = await self.ticket_repo.update_triage(ticket.id, triage_result)
                if updated_ticket:
                    ticket = updated_ticket
                    logger.info(
                        "Ticket %s triaged — %s / %s",
                        ticket.id,
                        triage_result.category,
                        triage_result.priority,
                    )
            else:
                logger.warning("Ticket %s saved as untriaged (AI unavailable)", ticket.id)

        except Exception as e:
            # AI triage failure should NEVER prevent ticket creation
            logger.error("AI triage failed for ticket %s: %s", ticket.id, str(e))

        return ticket

    async def get_ticket(self, ticket_id: str) -> TicketResponse:
        """Get a single ticket by ID."""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket", ticket_id)
        return ticket

    async def list_tickets(
        self,
        filters: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
    ) -> TicketListResponse:
        """List tickets with optional filtering and pagination."""
        skip = (page - 1) * page_size

        items = await self.ticket_repo.list(filters, skip=skip, limit=page_size)
        total = await self.ticket_repo.count(filters)
        total_pages = max(1, (total + page_size - 1) // page_size)

        return TicketListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def update_ticket_status(
        self,
        ticket_id: str,
        update: TicketStatusUpdate,
    ) -> TicketResponse:
        """
        Update ticket status with lifecycle validation.

        Valid transitions:
        - Open → In Progress
        - Open → Resolved
        - In Progress → Resolved
        - In Progress → Open (reopen)
        - Resolved → Open (reopen)
        """
        # Verify ticket exists
        existing = await self.ticket_repo.get_by_id(ticket_id)
        if not existing:
            raise NotFoundException("Ticket", ticket_id)

        # Validate status transition
        self._validate_status_transition(existing.status, update.status)

        # Perform update
        updated = await self.ticket_repo.update_status(ticket_id, update.status.value)
        if not updated:
            raise NotFoundException("Ticket", ticket_id)

        logger.info(
            "Ticket %s status changed: %s → %s",
            ticket_id,
            existing.status.value,
            update.status.value,
        )

        return updated

    @staticmethod
    def _validate_status_transition(current: TicketStatus, new: TicketStatus) -> None:
        """Validate that the status transition is allowed."""
        if current == new:
            raise ValidationException(f"Ticket is already '{current.value}'")

        # All transitions are allowed in this system
        # (Open ↔ In Progress ↔ Resolved, with reopening)
        valid_transitions = {
            TicketStatus.OPEN: {TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED},
            TicketStatus.IN_PROGRESS: {TicketStatus.RESOLVED, TicketStatus.OPEN},
            TicketStatus.RESOLVED: {TicketStatus.OPEN},
        }

        if new not in valid_transitions.get(current, set()):
            raise ValidationException(
                f"Cannot transition from '{current.value}' to '{new.value}'"
            )
