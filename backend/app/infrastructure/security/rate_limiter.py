"""
STTS Rate Limiter
──────────────────
Centralized rate limiter configuration using slowapi.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter — keyed by client IP
# Default: 60 requests/minute per IP across all endpoints
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
