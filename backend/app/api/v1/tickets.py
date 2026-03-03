"""
STTS Ticket API Endpoints
──────────────────────────
REST endpoints for ticket CRUD operations.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_agent, get_ticket_service
from app.core.models.agent import AgentResponse
from app.core.models.ticket import (
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketStatusUpdate,
)
from app.core.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new support ticket",
    description="Public endpoint — creates a new ticket and triggers AI triage classification.",
)
async def create_ticket(
    data: TicketCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    """Create a new support ticket (public — no auth required)."""
    return await ticket_service.create_ticket(data)


@router.get(
    "",
    response_model=TicketListResponse,
    summary="List all tickets (paginated)",
    description="Protected endpoint — returns paginated tickets with optional filtering.",
)
async def list_tickets(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filter by status: Open, In Progress, Resolved",
    ),
    priority_filter: Optional[str] = Query(
        default=None,
        alias="priority",
        description="Filter by priority: High, Medium, Low",
    ),
    _agent: AgentResponse = Depends(get_current_agent),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketListResponse:
    """List tickets with filtering and pagination (requires authentication)."""
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    if priority_filter:
        filters["priority"] = priority_filter

    return await ticket_service.list_tickets(filters, page=page, page_size=page_size)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Get a single ticket",
    description="Protected endpoint — returns full ticket details by ID.",
)
async def get_ticket(
    ticket_id: str,
    _agent: AgentResponse = Depends(get_current_agent),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    """Get a ticket by its ID (requires authentication)."""
    return await ticket_service.get_ticket(ticket_id)


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Update ticket status",
    description="Protected endpoint — update the status of a ticket (Open, In Progress, Resolved).",
)
async def update_ticket_status(
    ticket_id: str,
    update: TicketStatusUpdate,
    _agent: AgentResponse = Depends(get_current_agent),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    """Update ticket status (requires authentication)."""
    return await ticket_service.update_ticket_status(ticket_id, update)
