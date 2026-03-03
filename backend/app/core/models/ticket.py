"""
STTS Ticket Domain Models
──────────────────────────
Pydantic models for the Ticket entity — the core of the system.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Enums ──────────────────────────────────────────────────────


class TicketStatus(str, Enum):
    """Possible states in the ticket lifecycle."""

    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class TicketPriority(str, Enum):
    """AI-assigned priority levels."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TicketCategory(str, Enum):
    """AI-assigned ticket categories."""

    BILLING = "Billing"
    TECHNICAL_BUG = "Technical Bug"
    FEATURE_REQUEST = "Feature Request"
    ACCOUNT = "Account"
    GENERAL = "General"


# ── Request Schemas ────────────────────────────────────────────


class TicketCreate(BaseModel):
    """Schema for creating a new ticket (customer-facing)."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Brief summary of the issue",
        examples=["Cannot access my billing dashboard"],
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Detailed description of the issue",
        examples=["When I click on Billing in the sidebar, the page shows a 500 error..."],
    )
    customer_email: EmailStr = Field(
        ...,
        description="Customer's email address for follow-up",
        examples=["customer@example.com"],
    )


class TicketStatusUpdate(BaseModel):
    """Schema for updating ticket status (agent-facing)."""

    status: TicketStatus = Field(
        ...,
        description="The new status for the ticket",
        examples=["In Progress"],
    )


# ── AI Triage Result ──────────────────────────────────────────


class TriageResult(BaseModel):
    """Result from the AI triage service."""

    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reasoning: Optional[str] = None


# ── Response Schemas ───────────────────────────────────────────


class TicketResponse(BaseModel):
    """Full ticket representation returned by the API."""

    id: str = Field(..., description="Unique ticket identifier")
    title: str
    description: str
    customer_email: EmailStr
    status: TicketStatus = TicketStatus.OPEN
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    ai_confidence: Optional[float] = None
    ai_reasoning: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    """Paginated list of tickets."""

    items: list[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
