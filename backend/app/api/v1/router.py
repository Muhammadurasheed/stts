"""
STTS API v1 Router
───────────────────
Aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.tickets import router as tickets_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(tickets_router)
