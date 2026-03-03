"""
STTS LLM Gateway
──────────────────
Production-grade LLM integration with 3-layer resilience:
1. Retry with exponential backoff + jitter
2. Circuit breaker (Closed → Open → Half-Open)
3. Graceful degradation fallback

Uses Google Gemini via the google-genai SDK.
"""

import asyncio
import logging
import random
import time
from enum import Enum
from typing import Optional

from google import genai
from google.genai.types import GenerateContentConfig

from app.config import get_settings
from app.core.models.ticket import TriageResult
from app.infrastructure.llm.parser import parse_triage_response
from app.infrastructure.llm.prompts import TRIAGE_SYSTEM_PROMPT, build_triage_prompt

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"       # Normal operation — requests pass through
    OPEN = "open"           # Failures exceeded threshold — requests blocked
    HALF_OPEN = "half_open" # Cooldown expired — testing with probe request


class LLMGateway:
    """
    Production-grade LLM Gateway with resilience patterns.

    This gateway wraps the Google Gemini API and provides:
    - Automatic retry with exponential backoff + jitter
    - Circuit breaker to prevent cascading failures
    - Graceful degradation when the LLM is unavailable
    """

    def __init__(self):
        settings = get_settings()

        # ── Gemini Client ──────────────────────────────────────
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

        # ── Retry Config ───────────────────────────────────────
        self.max_retries = settings.LLM_MAX_RETRIES
        self.base_delay = settings.LLM_RETRY_BASE_DELAY

        # ── Circuit Breaker State ──────────────────────────────
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = settings.LLM_CIRCUIT_BREAKER_THRESHOLD
        self.cooldown_timeout = settings.LLM_CIRCUIT_BREAKER_TIMEOUT
        self.last_failure_time: float = 0.0
        self.successful_probe = False

    # ── Public API ─────────────────────────────────────────────

    async def classify_ticket(self, title: str, description: str) -> Optional[TriageResult]:
        """
        Classify a support ticket using LLM with full resilience.

        Returns:
            TriageResult if successful, None if LLM unavailable (graceful degradation).
        """
        # Check circuit breaker
        if not self._can_execute():
            logger.warning("Circuit breaker OPEN — skipping LLM call")
            return None

        # Retry loop with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                result = await self._call_llm(title, description)
                self._on_success()
                return result

            except Exception as e:
                logger.warning(
                    "LLM call attempt %d/%d failed: %s",
                    attempt,
                    self.max_retries,
                    str(e),
                )

                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    logger.info("Retrying in %.2fs...", delay)
                    await asyncio.sleep(delay)

        # All retries exhausted
        self._on_failure()
        logger.error("All %d LLM retry attempts exhausted", self.max_retries)
        return None

    # ── LLM Call ───────────────────────────────────────────────

    async def _call_llm(self, title: str, description: str) -> Optional[TriageResult]:
        """Make the actual LLM API call and parse the response."""
        user_prompt = build_triage_prompt(title, description)

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=user_prompt,
            config=GenerateContentConfig(
                system_instruction=TRIAGE_SYSTEM_PROMPT,
                temperature=0.1,          # Low temp for consistent classification
                max_output_tokens=256,
            ),
        )

        if not response or not response.text:
            raise ValueError("Empty response from LLM")

        result = parse_triage_response(response.text)
        if result is None:
            raise ValueError(f"Failed to parse LLM response: {response.text[:200]}")

        return result

    # ── Circuit Breaker Logic ──────────────────────────────────

    def _can_execute(self) -> bool:
        """Determine if a request should be allowed through."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if cooldown has passed → transition to HALF_OPEN
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.cooldown_timeout:
                logger.info(
                    "Circuit breaker transitioning OPEN → HALF_OPEN (cooldown: %.0fs elapsed)",
                    elapsed,
                )
                self.state = CircuitState.HALF_OPEN
                return True  # Allow probe request
            return False

        if self.state == CircuitState.HALF_OPEN:
            return True  # Allow probe requests

        return False

    def _on_success(self) -> None:
        """Handle successful LLM call — reset circuit breaker."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker transitioning HALF_OPEN → CLOSED (probe succeeded)")

        self.state = CircuitState.CLOSED
        self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed LLM call — update circuit breaker state."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker transitioning HALF_OPEN → OPEN (probe failed)")
            self.state = CircuitState.OPEN

        elif self.failure_count >= self.failure_threshold:
            logger.warning(
                "Circuit breaker transitioning CLOSED → OPEN (failures: %d >= threshold: %d)",
                self.failure_count,
                self.failure_threshold,
            )
            self.state = CircuitState.OPEN

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        delay = self.base_delay * (2 ** (attempt - 1))
        jitter = random.uniform(0, delay * 0.5)
        return min(delay + jitter, 10.0)  # Cap at 10 seconds

    # ── Status ─────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Get current gateway status for health checks."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "cooldown_timeout": self.cooldown_timeout,
        }
