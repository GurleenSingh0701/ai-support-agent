import pytest
from unittest.mock import patch, MagicMock
from resolution.resolution_engine import ResolutionEngine

@pytest.fixture
def engine():
    return ResolutionEngine()

@patch("router.router_agent.classify_intent")
@patch("router.router_agent.calculate_priority")
def test_process_message_low_confidence_escalation(mock_priority, mock_intent, engine):
    mock_intent.return_value = {
        "intent": "ORDER_INQUIRY",
        "confidence": 0.50,
        "entities": {},
        "is_multi_intent": False
    }
    mock_priority.return_value = {
        "sentiment": "NEUTRAL",
        "urgency_score": 50,
        "priority": "MEDIUM"
    }
    
    result = engine.process_message("Unclear request", ticket_id=1, customer_id=10)
    
    assert result["status"] == "ESCALATED"
    assert result["escalated"] is True
    assert "Issue Escalated to Support Agent" in result["response"]

@patch("router.router_agent.classify_intent")
@patch("router.router_agent.calculate_priority")
def test_process_message_very_negative_sentiment_escalation(mock_priority, mock_intent, engine):
    mock_intent.return_value = {
        "intent": "ORDER_INQUIRY",
        "confidence": 0.90,
        "entities": {},
        "is_multi_intent": False
    }
    mock_priority.return_value = {
        "sentiment": "VERY_NEGATIVE",
        "urgency_score": 90,
        "priority": "CRITICAL"
    }
    
    result = engine.process_message("This is a total scam!", ticket_id=2, customer_id=11)
    
    assert result["status"] == "ESCALATED"
    assert result["escalated"] is True

@patch("router.router_agent.classify_intent")
@patch("router.router_agent.calculate_priority")
def test_process_message_order_sub_agent_dispatch(mock_priority, mock_intent, engine):
    mock_intent.return_value = {
        "intent": "ORDER_INQUIRY",
        "confidence": 0.95,
        "entities": {"order_id": "ORD-123"},
        "is_multi_intent": False
    }
    mock_priority.return_value = {
        "sentiment": "NEUTRAL",
        "urgency_score": 50,
        "priority": "MEDIUM"
    }
    
    result = engine.process_message("Track my order ORD-123")
    
    assert result["status"] == "RESOLVED"
    assert result["escalated"] is False
    assert "Order Agent" in result["response"] or "ORD-123" in result["response"]

@patch("router.router_agent.classify_intent")
@patch("router.router_agent.calculate_priority")
def test_process_message_kb_rag_fallback(mock_priority, mock_intent, engine):
    mock_intent.return_value = {
        "intent": "POLICY_QUESTION",
        "confidence": 0.85,
        "entities": {},
        "is_multi_intent": False
    }
    mock_priority.return_value = {
        "sentiment": "POSITIVE",
        "urgency_score": 30,
        "priority": "LOW"
    }
    
    result = engine.process_message("What is your return policy?")
    
    assert result["status"] == "RESOLVED"
    assert result["escalated"] is False
    assert "Store Policy Information" in result["response"]
