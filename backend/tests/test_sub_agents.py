import pytest
from unittest.mock import patch, MagicMock
from sub_agents.main_arch import AgentState
from sub_agents.order_agent import OrderAgent
from sub_agents.payment_agent import PaymentAgent
from sub_agents.return_refund_agent import ReturnRefundAgent

@pytest.fixture
def base_state():
    return AgentState(
        ticket_id=1,
        customer_id=100,
        user_message="Test message",
        intent="TEST",
        confidence=0.9,
        entities={"order_id": "ORD-55555"}
    )

def test_order_agent_fallback(base_state, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    agent = OrderAgent()
    updated_state = agent.execute(base_state)
    
    assert updated_state.sub_agent_output is not None
    assert "ORD-55555" in updated_state.sub_agent_output
    assert "Order Status Update" in updated_state.sub_agent_output

def test_payment_agent_fallback(base_state, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    agent = PaymentAgent()
    updated_state = agent.execute(base_state)
    
    assert updated_state.sub_agent_output is not None
    assert "Billing & Payment Audit" in updated_state.sub_agent_output
    assert "Verified / Settled" in updated_state.sub_agent_output

def test_return_refund_agent_fallback(base_state, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    agent = ReturnRefundAgent()
    updated_state = agent.execute(base_state)
    
    assert updated_state.sub_agent_output is not None
    assert "Return & Refund Request Processed" in updated_state.sub_agent_output
    assert "RMA-99201" in updated_state.sub_agent_output

@patch("google.genai.Client")
def test_order_agent_llm_execution(mock_genai_client, base_state, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    mock_response = MagicMock()
    mock_response.text = "Your order ORD-55555 is arriving tomorrow!"
    
    mock_instance = MagicMock()
    mock_instance.models.generate_content.return_value = mock_response
    mock_genai_client.return_value = mock_instance
    
    agent = OrderAgent()
    updated_state = agent.execute(base_state)
    
    assert updated_state.sub_agent_output == "Your order ORD-55555 is arriving tomorrow!"
