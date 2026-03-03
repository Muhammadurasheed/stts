"""
STTS Triage Service
────────────────────
Orchestrates LLM-powered ticket classification with graceful degradation.
"""

import logging
from typing import Optional

from app.core.models.ticket import TriageResult
from app.infrastructure.llm.gateway import LLMGateway

logger = logging.getLogger(__name__)


class TriageService:
    """
    AI Triage Service — the "Smart" in Smart Triage.

    Calls the LLM Gateway to classify tickets. If the LLM is unavailable,
    returns None and the ticket is saved as "untriaged" for manual classification.
    """

    def __init__(self, llm_gateway: LLMGateway):
        self.llm_gateway = llm_gateway

    async def classify_ticket(self, title: str, description: str) -> Optional[TriageResult]:
        """
        Classify a ticket using AI.

        Returns:
            TriageResult with category, priority, confidence, and reasoning.
            None if classification fails (LLM unavailable or unparseable response).
        """
        try:
            result = await self.llm_gateway.classify_ticket(title, description)

            if result:
                logger.info(
                    "Ticket classified — Category: %s | Priority: %s | Confidence: %.2f",
                    result.category,
                    result.priority,
                    result.confidence or 0.0,
                )
            else:
                logger.warning("Triage returned None — ticket will be saved as untriaged")

            return result

        except Exception as e:
            logger.error("Unexpected error in triage service: %s", str(e))
            return None
