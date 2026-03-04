"""
STTS FastAPI Application
──────────────────────────
Application factory with async lifespan, middleware, and exception handlers.
"""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import router as v1_router
from app.common.exceptions import STTSException
from app.common.logging import setup_logging
from app.config import get_settings
from app.infrastructure.database.indexes import create_indexes
from app.infrastructure.database.mongodb import MongoDB
from app.infrastructure.security.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Initial logger for startup (will be replaced by setup_logging in app factory)
logger = logging.getLogger(__name__)

# --- STARTUP ENVIRONMENT SANITY CHECK ---
import os
# Force fix environment variables if they have literal quotes
for key in ["MONGODB_URL", "JWT_SECRET_KEY", "GEMINI_API_KEY", "GOOGLE_CLIENT_ID", "ALLOWED_ORIGINS"]:
    val = os.environ.get(key, "")
    if val.startswith('"') and val.endswith('"'):
        # Only print for real fixes to keep logs clean
        os.environ[key] = val[1:-1]
# ------------------------------------


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

    # Initialize logging (JSON in prod, clean fmt in dev)
    setup_logging(json_output=not settings.DEBUG)

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

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Request ID middleware for distributed tracing
    class RequestIdMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
            request.state.request_id = request_id
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

    app.add_middleware(RequestIdMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
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
        """Deep health check — verifies MongoDB connectivity and service status."""
        health = {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": "1.0.0",
            "dependencies": {},
        }

        # Check MongoDB
        try:
            db = MongoDB.get_database()
            await db.client.admin.command("ping")
            health["dependencies"]["mongodb"] = "connected"
        except Exception:
            health["status"] = "degraded"
            health["dependencies"]["mongodb"] = "disconnected"

        # Check LLM circuit breaker state
        from app.api.deps import get_llm_gateway
        try:
            gw = get_llm_gateway()
            health["dependencies"]["llm_gateway"] = gw.get_status()
        except Exception:
            health["dependencies"]["llm_gateway"] = "unknown"

        status_code = 200 if health["status"] == "healthy" else 503
        return JSONResponse(content=health, status_code=status_code)

    return app


# Create the app instance
app = create_app()
