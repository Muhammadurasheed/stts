"""
STTS MongoDB Connection Manager
─────────────────────────────────
Async MongoDB client via Motor with proper lifecycle management.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

logger = logging.getLogger(__name__)


class MongoDB:
    """Singleton-style MongoDB connection manager."""

    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls) -> None:
        """Initialize MongoDB connection on application startup."""
        settings = get_settings()
        logger.info("Connecting to MongoDB at %s...", settings.MONGODB_URL)

        cls.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
        cls.database = cls.client[settings.MONGODB_DB_NAME]

        # Verify connection
        await cls.client.admin.command("ping")
        logger.info("✅ Connected to MongoDB database: %s", settings.MONGODB_DB_NAME)

    @classmethod
    async def disconnect(cls) -> None:
        """Close MongoDB connection on application shutdown."""
        if cls.client:
            cls.client.close()
            logger.info("🔌 Disconnected from MongoDB")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get the active database instance."""
        if cls.database is None:
            raise RuntimeError("MongoDB is not connected. Call MongoDB.connect() first.")
        return cls.database


def get_database() -> AsyncIOMotorDatabase:
    """Dependency injection helper for FastAPI."""
    return MongoDB.get_database()
