import pytest
from unittest.mock import patch, MagicMock
from router.router_agent import RouterAgent, router_agent

@pytest.fixture
def router():
    return RouterAgent()

def test_router_agent_instance():
    assert router_agent is not None
    assert isinstance(router_agent, RouterAgent)

@patch("router.router_agent.classify_intent")
@patch("router.router_agent.calculate_priority")
def test_router_agent_escalation_flow(mock_priority, mock_intent, router):
    mock_intent.return_value = {
        "intent": "PAYMENT_ISSUE",
        "confidence": 0.95,
        "entities": {},
        "is_multi_intent": False
    }
    mock_priority.return_value = {
        "sentiment": "VERY_NEGATIVE",
        "urgency_score": 95,
        "priority": "CRITICAL"
    }
    
    result = router.route_message("This is fraud!", ticket_id=99, customer_id=12)
    
    assert result["status"] == "ESCALATED"
    assert result["escalated"] is True
    assert result["escalation_reason"] == "HIGH_CUSTOMER_FRUSTRATION"
    assert "Issue Escalated to Support Agent" in result["response"]

@patch("router.router_agent.classify_intent")
@patch("router.router_agent.calculate_priority")
def test_router_agent_order_routing(mock_priority, mock_intent, router):
    mock_intent.return_value = {
        "intent": "ORDER_INQUIRY",
        "confidence": 0.92,
        "entities": {"order_id": "ORD-77112"},
        "is_multi_intent": False
    }
    mock_priority.return_value = {
        "sentiment": "NEUTRAL",
        "urgency_score": 50,
        "priority": "MEDIUM"
    }
    
    result = router.route_message("Check my order status ORD-77112")
    
    assert result["status"] == "RESOLVED"
    assert result["escalated"] is False
    assert "ORD-77112" in result["response"] or "Order Status" in result["response"]

@patch("router.router_agent.classify_intent")
@patch("router.router_agent.calculate_priority")
def test_router_agent_kb_fallback(mock_priority, mock_intent, router):
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
    
    result = router.route_message("What is your shipping policy?")
    
    assert result["status"] == "RESOLVED"
    assert result["escalated"] is False
    assert "Store Policy Information" in result["response"]
