"""
STTS MongoDB Ticket Repository
────────────────────────────────
Concrete implementation of TicketRepositoryInterface using Motor.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.interfaces.ticket_repo import TicketRepositoryInterface
from app.core.models.ticket import (
    TicketCreate,
    TicketResponse,
    TicketStatus,
    TriageResult,
)


class MongoTicketRepository(TicketRepositoryInterface):
    """MongoDB-backed ticket repository."""

    COLLECTION = "tickets"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[self.COLLECTION]

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _to_response(doc: dict) -> TicketResponse:
        """Convert a MongoDB document to a TicketResponse model."""
        return TicketResponse(
            id=str(doc["_id"]),
            title=doc["title"],
            description=doc["description"],
            customer_email=doc["customer_email"],
            status=doc.get("status", TicketStatus.OPEN),
            priority=doc.get("priority"),
            category=doc.get("category"),
            ai_confidence=doc.get("ai_confidence"),
            ai_reasoning=doc.get("ai_reasoning"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            resolved_at=doc.get("resolved_at"),
        )

    @staticmethod
    def _build_filters(filters: dict[str, Any]) -> dict:
        """Build MongoDB query filter from API filter params."""
        query: dict = {}
        if "status" in filters and filters["status"]:
            query["status"] = filters["status"]
        if "priority" in filters and filters["priority"]:
            query["priority"] = filters["priority"]
        return query

    # ── Interface Implementation ──────────────────────────────

    async def create(self, ticket_data: TicketCreate) -> TicketResponse:
        now = datetime.now(timezone.utc)
        doc = {
            "title": ticket_data.title,
            "description": ticket_data.description,
            "customer_email": ticket_data.customer_email,
            "status": TicketStatus.OPEN.value,
            "priority": None,
            "category": None,
            "ai_confidence": None,
            "ai_reasoning": None,
            "created_at": now,
            "updated_at": now,
            "resolved_at": None,
        }

        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._to_response(doc)

    async def get_by_id(self, ticket_id: str) -> Optional[TicketResponse]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(ticket_id)})
        except Exception:
            return None
        return self._to_response(doc) if doc else None

    async def list(
        self,
        filters: dict[str, Any],
        skip: int = 0,
        limit: int = 20,
    ) -> list[TicketResponse]:
        query = self._build_filters(filters)
        cursor = (
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._to_response(doc) for doc in docs]

    async def count(self, filters: dict[str, Any]) -> int:
        query = self._build_filters(filters)
        return await self.collection.count_documents(query)

    async def update_status(self, ticket_id: str, status: str) -> Optional[TicketResponse]:
        now = datetime.now(timezone.utc)
        update: dict = {
            "$set": {
                "status": status,
                "updated_at": now,
            }
        }

        # Set resolved_at timestamp when resolving
        if status == TicketStatus.RESOLVED.value:
            update["$set"]["resolved_at"] = now

        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(ticket_id)},
                update,
                return_document=True,
            )
        except Exception:
            return None

        return self._to_response(result) if result else None

    async def update_triage(self, ticket_id: str, triage: TriageResult) -> Optional[TicketResponse]:
        now = datetime.now(timezone.utc)
        update_data: dict[str, Any] = {"updated_at": now}

        if triage.category:
            update_data["category"] = triage.category.value
        if triage.priority:
            update_data["priority"] = triage.priority.value
        if triage.confidence is not None:
            update_data["ai_confidence"] = triage.confidence
        if triage.reasoning:
            update_data["ai_reasoning"] = triage.reasoning

        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(ticket_id)},
                {"$set": update_data},
                return_document=True,
            )
        except Exception:
            return None

        return self._to_response(result) if result else None
