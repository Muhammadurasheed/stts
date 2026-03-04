"""
Unit tests for the LLM Gateway resilient architecture.
"""

import time
import pytest
from unittest.mock import MagicMock, patch
from app.infrastructure.llm.gateway import LLMGateway, CircuitState, CircuitState
from app.core.models.ticket import TicketCategory, TicketPriority

@pytest.fixture
def mock_settings():
    with patch("app.infrastructure.llm.gateway.get_settings") as mock:
        settings = MagicMock()
        settings.USE_VERTEX_AI = False
        settings.GCP_PROJECT = "test-project"
        settings.GCP_LOCATION = "us-central1"
        settings.GEMINI_API_KEY = "test-key"
        settings.GEMINI_MODEL = "gemini-1.5-flash"
        settings.LLM_MAX_RETRIES = 3
        settings.LLM_RETRY_BASE_DELAY = 1.0
        settings.LLM_CIRCUIT_BREAKER_THRESHOLD = 3
        settings.LLM_CIRCUIT_BREAKER_TIMEOUT = 60
        mock.return_value = settings
        yield settings

@pytest.fixture
def gateway(mock_settings):
    with patch("google.genai.Client"):
        return LLMGateway()

class TestLLMGatewayResilience:
    """Test suite for LLM Gateway resilience patterns."""

    def test_initialization(self, gateway):
        """Verify gateway initializes in CLOSED state."""
        assert gateway.state == CircuitState.CLOSED
        assert gateway.failure_count == 0

    def test_circuit_breaker_threshold(self, gateway):
        """Verify circuit opens after threshold is reached."""
        for _ in range(gateway.failure_threshold):
            gateway._on_failure()
        
        assert gateway.state == CircuitState.OPEN
        assert gateway.failure_count == gateway.failure_threshold
        assert not gateway._can_execute()

    def test_circuit_breaker_cooldown(self, gateway):
        """Verify circuit moves to HALF_OPEN after cooldown."""
        gateway.state = CircuitState.OPEN
        gateway.last_failure_time = time.time() - 70 # Exceed 60s timeout
        
        assert gateway._can_execute()
        assert gateway.state == CircuitState.HALF_OPEN

    def test_circuit_breaker_reset_on_success(self, gateway):
        """Verify circuit closes on success in HALF_OPEN state."""
        gateway.state = CircuitState.HALF_OPEN
        gateway.failure_count = 5
        
        gateway._on_success()
        
        assert gateway.state == CircuitState.CLOSED
        assert gateway.failure_count == 0

    def test_mock_triage_fallback(self, gateway):
        """Verify keyword-based mock triage logic."""
        # Billing
        res = gateway._mock_triage("Payment failed", "I was charged twice.")
        assert res.category == TicketCategory.BILLING
        assert res.priority == TicketPriority.MEDIUM
        
        # Urgent Bug
        res = gateway._mock_triage("CRITICAL ERROR", "The app is crashing ASAP!")
        assert res.category == TicketCategory.TECHNICAL_BUG
        assert res.priority == TicketPriority.HIGH

    def test_calculate_backoff(self, gateway):
        """Verify exponential backoff calculation."""
        delay1 = gateway._calculate_backoff(1)
        delay2 = gateway._calculate_backoff(2)
        
        assert 1.0 <= delay1 <= 1.5
        assert 2.0 <= delay2 <= 3.0

    def test_get_status(self, gateway):
        """Verify status reporting."""
        status = gateway.get_status()
        assert status["state"] == "closed"
        assert status["failure_threshold"] == 3
