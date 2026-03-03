"""
STTS FastAPI Application
──────────────────────────
Application factory with async lifespan, middleware, and exception handlers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.common.exceptions import STTSException
from app.config import get_settings
from app.infrastructure.database.indexes import create_indexes
from app.infrastructure.database.mongodb import MongoDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Application Lifespan ──────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle — startup and shutdown."""
    # STARTUP
    logger.info("🚀 Starting STTS API...")
    await MongoDB.connect()
    await create_indexes(MongoDB.get_database())
    logger.info("✅ STTS API is ready!")

    yield

    # SHUTDOWN
    logger.info("🔌 Shutting down STTS API...")
    await MongoDB.disconnect()
    logger.info("👋 STTS API shutdown complete")


# ── App Factory ───────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Smart Triage Ticketing System — AI-powered ticket classification and management. "
            "Built with FastAPI, MongoDB, and Google Gemini."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── Middleware ──────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://frontend:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ─────────────────────────────────
    @app.exception_handler(STTSException)
    async def stts_exception_handler(request: Request, exc: STTSException):
        """Handle all custom STTS exceptions with structured JSON responses."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Catch-all handler for unexpected errors."""
        logger.exception("Unhandled exception: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "An unexpected error occurred",
                "status_code": 500,
            },
        )

    # ── Routes ─────────────────────────────────────────────
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for Docker and monitoring."""
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": "1.0.0",
        }

    return app


# Create the app instance
app = create_app()
