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
from app.core.models.ticket import TriageResult, TicketCategory, TicketPriority
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

    Supports two authentication modes:
    - Vertex AI (GCP billing — reliable, production-grade)
    - API Key (free tier — rate-limited, development use)
    """

    def __init__(self):
        settings = get_settings()

        # ── Gemini Client ──────────────────────────────────────
        if settings.USE_VERTEX_AI and settings.GCP_PROJECT:
            self.client = genai.Client(
                vertexai=True,
                project=settings.GCP_PROJECT,
                location=settings.GCP_LOCATION,
            )
            logger.info(
                "🚀 LLM Gateway initialized with Vertex AI (project=%s, location=%s)",
                settings.GCP_PROJECT,
                settings.GCP_LOCATION,
            )
        else:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            logger.info("🔑 LLM Gateway initialized with API Key (free tier)")

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

    # Model Fallback Chain
    MODEL_FALLBACKS = [
        "gemini-2.0-flash",
        "gemini-1.5-flash", 
        "gemini-1.5-pro",
        "gemini-1.0-pro"
    ]

    async def classify_ticket(self, title: str, description: str) -> Optional[TriageResult]:
        """
        Classify a support ticket using LLM with multi-model fallback and mock safety net.
        """
        # Check circuit breaker
        if not self._can_execute():
            logger.warning("Circuit breaker OPEN — using Mock Triage safety net")
            return self._mock_triage(title, description)

        # Try models in sequence
        for model in self.MODEL_FALLBACKS:
            # Skip if we already know this model is likely failing (could add model-specific state later)
            
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info("Attempting triage with model: %s (Attempt %d)", model, attempt)
                    result = await self._call_llm(title, description, model_name=model)
                    self._on_success()
                    return result

                except Exception as e:
                    # If it's a 429/403/Exhausted/Billing error, pivot to next model immediately
                    error_msg = str(e).upper()
                    is_quota_error = any(k in error_msg for k in [
                        "429", "403", "QUOTA", "EXHAUSTED", 
                        "PERMISSION_DENIED", "BILLING", "RESOURCE_EXHAUSTED"
                    ])
                    
                    logger.warning(
                        "Model %s failed (Attempt %d): %s",
                        model, attempt, str(e)
                    )

                    if is_quota_error:
                        logger.warning("Quota exhausted for %s. Pivoting to next model...", model)
                        break # Break retry loop, move to next model in MODEL_FALLBACKS

                    if attempt < self.max_retries:
                        delay = self._calculate_backoff(attempt)
                        await asyncio.sleep(delay)

        # All models and retries exhausted
        self._on_failure()
        logger.error("All Gemini models exhausted. Triggering Mock Triage safety net.")
        return self._mock_triage(title, description)

    # ── Mock Triage (Keyword Heuristic) ────────────────────────
    
    def _mock_triage(self, title: str, description: str) -> TriageResult:
        """Deterministic keyword-based triage for when AI is unavailable."""
        text = (title + " " + description).lower()
        
        # Default
        category = TicketCategory.GENERAL
        priority = TicketPriority.MEDIUM
        
        # Category Heuristics
        if any(w in text for w in ["billing", "invoice", "payment", "charge", "refund"]):
            category = TicketCategory.BILLING
        elif any(w in text for w in ["bug", "error", "broken", "crash", "fail", "issue"]):
            category = TicketCategory.TECHNICAL_BUG
        elif any(w in text for w in ["feature", "request", "suggest", "improve", "add"]):
            category = TicketCategory.FEATURE_REQUEST
        elif any(w in text for w in ["account", "login", "password", "access", "permission"]):
            category = TicketCategory.ACCOUNT
            
        # Priority Heuristics
        if any(w in text for w in ["urgent", "critical", "blocking", "emergency", "immediately", "asap"]):
            priority = TicketPriority.HIGH
        elif any(w in text for w in ["slow", "minor", "question", "eventually"]):
            priority = TicketPriority.LOW
            
        return TriageResult(
            category=category,
            priority=priority,
            confidence=0.5,
            reasoning="Classified via Keyword Heuristic (AI Safety Net active)."
        )

    # ── LLM Call ───────────────────────────────────────────────

    async def _call_llm(self, title: str, description: str, model_name: str) -> Optional[TriageResult]:
        """Make the actual LLM API call and parse the response."""
        user_prompt = build_triage_prompt(title, description)

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=model_name,
            contents=user_prompt,
            config=GenerateContentConfig(
                system_instruction=TRIAGE_SYSTEM_PROMPT,
                temperature=0.1,
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
