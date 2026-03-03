"""
STTS Configuration Module
─────────────────────────
Centralized, type-safe configuration using Pydantic Settings.
All values are loaded from environment variables / .env file.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable binding."""

    # ── Application ──────────────────────────────────────────
    APP_NAME: str = "STTS API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── MongoDB ──────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "stts"

    # ── JWT Authentication ───────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE_ME_TO_A_STRONG_SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Google Gemini AI ─────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # ── LLM Resilience ───────────────────────────────────────
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_BASE_DELAY: float = 1.0
    LLM_CIRCUIT_BREAKER_THRESHOLD: int = 5
    LLM_CIRCUIT_BREAKER_TIMEOUT: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — created once, reused everywhere."""
    return Settings()
