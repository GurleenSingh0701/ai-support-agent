import pytest
from unittest.mock import patch, MagicMock
from escalation.escalation_handler import compile_and_escalate

def test_compile_and_escalate_payload_structure():
    payload = compile_and_escalate(
        ticket_id=101,
        customer_id=55,
        user_message="I demand a refund right now!",
        sentiment="VERY_NEGATIVE",
        urgency="CRITICAL",
        reason="HIGH_CUSTOMER_FRUSTRATION"
    )
    
    assert payload["event_type"] == "TICKET_ESCALATION"
    assert payload["ticket_id"] == 101
    assert payload["customer_id"] == 55
    assert payload["customer_message"] == "I demand a refund right now!"
    assert payload["sentiment"] == "VERY_NEGATIVE"
    assert payload["urgency"] == "CRITICAL"
    assert payload["escalation_reason"] == "HIGH_CUSTOMER_FRUSTRATION"
    assert "Ticket #101 escalated due to HIGH_CUSTOMER_FRUSTRATION" in payload["summary"]
    assert len(payload["attempted_steps"]) == 3

@patch("escalation.escalation_handler.redis_client")
def test_compile_and_escalate_redis_publish(mock_redis):
    payload = compile_and_escalate(
        ticket_id=202,
        customer_id=88,
        user_message="Low confidence intent query",
        sentiment="NEUTRAL",
        urgency="MEDIUM",
        reason="LOW_CONFIDENCE"
    )
    
    assert mock_redis.publish.called
    args, kwargs = mock_redis.publish.call_args
    assert args[0] == "agent_queue"
    assert '"ticket_id": 202' in args[1]

@patch("escalation.escalation_handler.redis_client")
def test_compile_and_escalate_redis_exception_handling(mock_redis):
    mock_redis.publish.side_effect = Exception("Redis network error")
    
    # Should not raise exception, should handle gracefully
    payload = compile_and_escalate(
        ticket_id=303,
        customer_id=99,
        user_message="Test query",
        sentiment="NEUTRAL",
        urgency="LOW"
    )
    assert payload["ticket_id"] == 303
