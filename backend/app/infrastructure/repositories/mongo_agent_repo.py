"""
STTS MongoDB Agent Repository
───────────────────────────────
Concrete implementation of AgentRepositoryInterface using Motor.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.interfaces.agent_repo import AgentRepositoryInterface
from app.core.models.agent import AgentCreate, AgentResponse, AgentRole


class MongoAgentRepository(AgentRepositoryInterface):
    """MongoDB-backed agent repository."""

    COLLECTION = "agents"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[self.COLLECTION]

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _to_response(doc: dict) -> AgentResponse:
        """Convert a MongoDB document to an AgentResponse model."""
        return AgentResponse(
            id=str(doc["_id"]),
            email=doc["email"],
            full_name=doc["full_name"],
            role=doc.get("role", AgentRole.AGENT),
            is_active=doc.get("is_active", True),
            created_at=doc["created_at"],
        )

    # ── Interface Implementation ──────────────────────────────

    async def create(self, agent_data: AgentCreate, hashed_password: str) -> AgentResponse:
        now = datetime.now(timezone.utc)
        doc = {
            "email": agent_data.email,
            "full_name": agent_data.full_name,
            "hashed_password": hashed_password,
            "role": AgentRole.AGENT.value,
            "is_active": True,
            "created_at": now,
        }

        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._to_response(doc)

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Returns raw dict with hashed_password for authentication."""
        doc = await self.collection.find_one({"email": email})
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    async def get_by_id(self, agent_id: str) -> Optional[AgentResponse]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(agent_id)})
        except Exception:
            return None
        return self._to_response(doc) if doc else None
