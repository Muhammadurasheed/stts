"""
STTS Abstract Agent Repository Interface
──────────────────────────────────────────
Defines the contract for agent data access.
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.core.models.agent import AgentCreate, AgentResponse


class AgentRepositoryInterface(ABC):
    """Abstract interface for agent persistence operations."""

    @abstractmethod
    async def create(self, agent_data: AgentCreate, hashed_password: str) -> AgentResponse:
        """Create a new agent. Returns the created agent."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[dict]:
        """Find agent by email. Returns raw dict including hashed_password."""
        ...

    @abstractmethod
    async def get_by_id(self, agent_id: str) -> Optional[AgentResponse]:
        """Find agent by ID. Returns agent without password."""
        ...
