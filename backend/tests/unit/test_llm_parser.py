"""
Unit tests for the LLM Response Parser.
"""

import pytest
from app.infrastructure.llm.parser import parse_triage_response
from app.core.models.ticket import TicketCategory, TicketPriority

def test_parse_clean_json():
    raw = '{"category": "Billing", "priority": "High", "confidence": 0.9, "reasoning": "Test"}'
    res = parse_triage_response(raw)
    assert res.category == TicketCategory.BILLING
    assert res.priority == TicketPriority.HIGH
    assert res.confidence == 0.9
    assert res.reasoning == "Test"

def test_parse_markdown_wrapped():
    raw = '```json\n{"category": "Technical Bug", "priority": "Medium", "confidence": 0.5, "reasoning": "Bug report"}\n```'
    res = parse_triage_response(raw)
    assert res.category == TicketCategory.TECHNICAL_BUG
    assert res.priority == TicketPriority.MEDIUM

def test_parse_case_insensitive():
    raw = '{"category": "billing", "priority": "high", "confidence": 1.0}'
    res = parse_triage_response(raw)
    assert res.category == TicketCategory.BILLING
    assert res.priority == TicketPriority.HIGH

def test_parse_confidence_clamping():
    # Over 1.0
    res = parse_triage_response('{"category": "General", "priority": "Low", "confidence": 1.5}')
    assert res.confidence == 1.0
    # Under 0.0
    res = parse_triage_response('{"category": "General", "priority": "Low", "confidence": -0.5}')
    assert res.confidence == 0.0

def test_parse_invalid_json():
    res = parse_triage_response("Not a JSON")
    assert res is None

def test_parse_missing_fields():
    # Only reasoning
    res = parse_triage_response('{"reasoning": "No category or priority"}')
    assert res is None

def test_parse_huge_reasoning():
    raw = '{"category": "General", "priority": "Low", "reasoning": "' + ("A" * 1000) + '"}'
    res = parse_triage_response(raw)
    assert len(res.reasoning) == 500
