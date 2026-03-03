"""
STTS LLM Gateway Tests
────────────────────────
Tests for the circuit breaker, retry logic, and response parsing.
"""

import pytest

from app.core.models.ticket import TicketCategory, TicketPriority
from app.infrastructure.llm.gateway import CircuitState, LLMGateway
from app.infrastructure.llm.parser import parse_triage_response


class TestResponseParser:
    """Tests for the LLM response parser."""

    def test_parse_valid_json(self):
        """Test parsing a clean JSON response."""
        raw = '{"category": "Billing", "priority": "High", "confidence": 0.95, "reasoning": "Payment issue"}'
        result = parse_triage_response(raw)

        assert result is not None
        assert result.category == TicketCategory.BILLING
        assert result.priority == TicketPriority.HIGH
        assert result.confidence == 0.95

    def test_parse_markdown_wrapped_json(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        raw = '```json\n{"category": "Technical Bug", "priority": "Medium", "confidence": 0.8, "reasoning": "Bug"}\n```'
        result = parse_triage_response(raw)

        assert result is not None
        assert result.category == TicketCategory.TECHNICAL_BUG
        assert result.priority == TicketPriority.MEDIUM

    def test_parse_case_insensitive_category(self):
        """Test case-insensitive category matching."""
        raw = '{"category": "billing", "priority": "high", "confidence": 0.9, "reasoning": "Test"}'
        result = parse_triage_response(raw)

        assert result is not None
        assert result.category == TicketCategory.BILLING
        assert result.priority == TicketPriority.HIGH

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON returns None."""
        result = parse_triage_response("This is not JSON at all")
        assert result is None

    def test_parse_empty_response(self):
        """Test parsing empty response returns None."""
        result = parse_triage_response("")
        assert result is None

    def test_parse_missing_both_fields(self):
        """Test parsing response missing both category and priority."""
        raw = '{"confidence": 0.5, "reasoning": "unclear"}'
        result = parse_triage_response(raw)
        assert result is None

    def test_parse_confidence_clamping(self):
        """Test that confidence is clamped to [0, 1]."""
        raw = '{"category": "General", "priority": "Low", "confidence": 2.5, "reasoning": "Test"}'
        result = parse_triage_response(raw)

        assert result is not None
        assert result.confidence == 1.0  # Clamped

    def test_parse_unknown_category(self):
        """Test handling of unknown category from LLM."""
        raw = '{"category": "Unknown Category", "priority": "High", "confidence": 0.9, "reasoning": "Test"}'
        result = parse_triage_response(raw)

        # Should still return result with None category but valid priority
        assert result is not None
        assert result.category is None
        assert result.priority == TicketPriority.HIGH


class TestCircuitBreaker:
    """Tests for the circuit breaker state machine."""

    def test_initial_state_is_closed(self):
        """Circuit breaker should start in CLOSED state."""
        gateway = LLMGateway.__new__(LLMGateway)
        gateway.state = CircuitState.CLOSED
        gateway.failure_count = 0
        gateway.failure_threshold = 5
        gateway.cooldown_timeout = 60
        gateway.last_failure_time = 0.0

        assert gateway.state == CircuitState.CLOSED
        assert gateway._can_execute() is True

    def test_transitions_to_open_after_threshold(self):
        """Circuit breaker opens after reaching failure threshold."""
        gateway = LLMGateway.__new__(LLMGateway)
        gateway.state = CircuitState.CLOSED
        gateway.failure_count = 0
        gateway.failure_threshold = 3
        gateway.cooldown_timeout = 60
        gateway.last_failure_time = 0.0

        for _ in range(3):
            gateway._on_failure()

        assert gateway.state == CircuitState.OPEN

    def test_open_blocks_requests(self):
        """OPEN state should block requests."""
        import time

        gateway = LLMGateway.__new__(LLMGateway)
        gateway.state = CircuitState.OPEN
        gateway.failure_count = 5
        gateway.failure_threshold = 5
        gateway.cooldown_timeout = 60
        gateway.last_failure_time = time.time()

        assert gateway._can_execute() is False

    def test_success_resets_to_closed(self):
        """Success should reset the circuit breaker to CLOSED."""
        gateway = LLMGateway.__new__(LLMGateway)
        gateway.state = CircuitState.HALF_OPEN
        gateway.failure_count = 5
        gateway.failure_threshold = 5
        gateway.cooldown_timeout = 60
        gateway.last_failure_time = 0.0

        gateway._on_success()

        assert gateway.state == CircuitState.CLOSED
        assert gateway.failure_count == 0

    def test_half_open_failure_reopens(self):
        """Failure in HALF_OPEN should transition back to OPEN."""
        gateway = LLMGateway.__new__(LLMGateway)
        gateway.state = CircuitState.HALF_OPEN
        gateway.failure_count = 5
        gateway.failure_threshold = 5
        gateway.cooldown_timeout = 60
        gateway.last_failure_time = 0.0

        gateway._on_failure()

        assert gateway.state == CircuitState.OPEN

    def test_backoff_calculation(self):
        """Test exponential backoff with jitter."""
        gateway = LLMGateway.__new__(LLMGateway)
        gateway.base_delay = 1.0

        delay_1 = gateway._calculate_backoff(1)
        delay_2 = gateway._calculate_backoff(2)
        delay_3 = gateway._calculate_backoff(3)

        # Delays should generally increase (with jitter)
        assert delay_1 <= 2.0   # 1 * 2^0 + jitter ≤ 1.5
        assert delay_2 <= 4.0   # 1 * 2^1 + jitter ≤ 3.0
        assert delay_3 <= 10.0  # Capped at 10s

    def test_gateway_status(self):
        """Test gateway status reporting."""
        gateway = LLMGateway.__new__(LLMGateway)
        gateway.state = CircuitState.CLOSED
        gateway.failure_count = 2
        gateway.failure_threshold = 5
        gateway.cooldown_timeout = 60

        status = gateway.get_status()
        assert status["state"] == "closed"
        assert status["failure_count"] == 2
