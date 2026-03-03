"""
STTS MongoDB Index Manager
────────────────────────────
Creates database indexes on application startup for query performance.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    """
    Create all required indexes for optimal query performance.
    
    MongoDB index creation is idempotent — safe to call on every startup.
    """
    logger.info("Creating MongoDB indexes...")

    # ── Tickets Collection ─────────────────────────────────────
    tickets = db["tickets"]

    await tickets.create_index("status", name="idx_tickets_status")
    await tickets.create_index("priority", name="idx_tickets_priority")
    await tickets.create_index(
        [("created_at", -1)],
        name="idx_tickets_created_at_desc",
    )
    await tickets.create_index(
        [("status", 1), ("priority", 1)],
        name="idx_tickets_status_priority",
    )
    await tickets.create_index("customer_email", name="idx_tickets_customer_email")

    # ── Agents Collection ──────────────────────────────────────
    agents = db["agents"]

    await agents.create_index(
        "email",
        unique=True,
        name="idx_agents_email_unique",
    )

    logger.info("✅ MongoDB indexes created successfully")
