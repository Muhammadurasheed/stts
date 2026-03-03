"""
STTS LLM Response Parser
──────────────────────────
Validates and parses LLM responses into structured TriageResult.
"""

import json
import logging
import re
from typing import Optional

from app.core.models.ticket import TicketCategory, TicketPriority, TriageResult

logger = logging.getLogger(__name__)


def parse_triage_response(raw_response: str) -> Optional[TriageResult]:
    """
    Parse the raw LLM response into a validated TriageResult.

    Handles:
    - Clean JSON responses
    - JSON wrapped in markdown code blocks
    - Malformed responses (returns None)
    """
    try:
        # Strip markdown code block wrappers if present
        cleaned = raw_response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

        data = json.loads(cleaned)

        # Validate and extract fields
        category = _parse_category(data.get("category"))
        priority = _parse_priority(data.get("priority"))
        confidence = _parse_confidence(data.get("confidence"))
        reasoning = data.get("reasoning", "")

        if category is None and priority is None:
            logger.warning("LLM response missing both category and priority")
            return None

        return TriageResult(
            category=category,
            priority=priority,
            confidence=confidence,
            reasoning=str(reasoning)[:500],  # Cap reasoning length
        )

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error("Failed to parse LLM triage response: %s | Raw: %s", e, raw_response[:200])
        return None


def _parse_category(value: Optional[str]) -> Optional[TicketCategory]:
    """Safely parse category from LLM response."""
    if not value:
        return None
    try:
        return TicketCategory(value)
    except ValueError:
        # Try case-insensitive match
        for cat in TicketCategory:
            if cat.value.lower() == value.lower():
                return cat
        logger.warning("Unknown category from LLM: %s", value)
        return None


def _parse_priority(value: Optional[str]) -> Optional[TicketPriority]:
    """Safely parse priority from LLM response."""
    if not value:
        return None
    try:
        return TicketPriority(value)
    except ValueError:
        for pri in TicketPriority:
            if pri.value.lower() == value.lower():
                return pri
        logger.warning("Unknown priority from LLM: %s", value)
        return None


def _parse_confidence(value) -> Optional[float]:
    """Safely parse confidence score."""
    if value is None:
        return None
    try:
        conf = float(value)
        return max(0.0, min(1.0, conf))  # Clamp to [0, 1]
    except (ValueError, TypeError):
        return None
