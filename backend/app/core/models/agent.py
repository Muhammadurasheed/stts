"""
STTS Agent Domain Models
────────────────────────
Pydantic models for the Support Agent entity.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class AgentRole(str, Enum):
    """Role-based access control roles (future-ready)."""

    ADMIN = "admin"
    AGENT = "agent"
    READ_ONLY = "read_only"


# ── Request Schemas ────────────────────────────────────────────


class AgentCreate(BaseModel):
    """Schema for registering a new support agent."""

    email: EmailStr = Field(
        ...,
        description="Agent's email address (used for login)",
        examples=["agent@stts.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 characters)",
        examples=["secureP@ss123"],
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Agent's full name",
        examples=["Muhammad Rasheed"],
    )


class AgentLogin(BaseModel):
    """Schema for agent login."""

    email: EmailStr = Field(..., examples=["agent@stts.com"])
    password: str = Field(..., examples=["secureP@ss123"])


# ── Response Schemas ───────────────────────────────────────────


class AgentResponse(BaseModel):
    """Agent profile returned by the API (never includes password)."""

    id: str
    email: EmailStr
    full_name: str
    role: AgentRole = AgentRole.AGENT
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response after successful login."""

    access_token: str
    token_type: str = "bearer"
    agent: AgentResponse
