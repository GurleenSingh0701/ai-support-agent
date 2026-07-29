import logging
from typing import Dict, Any
from database import redis_client

logging.basicConfig(level=logging.INFO)

def compile_and_escalate(
    ticket_id: int,
    customer_id: int,
    user_message: str,
    sentiment: str,
    urgency: str,
    reason: str = "LOW_CONFIDENCE"
) -> Dict[str, Any]:
    """
    Compiles full context-rich handoff payload and broadcasts escalation event
    via Redis Pub/Sub to online support agents.
    """
    payload = {
        "event_type": "TICKET_ESCALATION",
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "customer_message": user_message,
        "sentiment": sentiment,
        "urgency": urgency,
        "escalation_reason": reason,
        "summary": f"Ticket #{ticket_id} escalated due to {reason}. Customer sentiment is {sentiment}.",
        "attempted_steps": [
            "Intent & Urgency Classified",
            "Checked AI Confidence Score",
            "Triggered Context-Rich Human Escalation Handoff"
        ]
    }
    
    # Broadcast to Redis channel if available
    if redis_client:
        try:
            import json
            redis_client.publish("agent_queue", json.dumps(payload))
            logging.info(f"Published escalation payload for Ticket #{ticket_id} to Redis 'agent_queue'.")
        except Exception as e:
            logging.error(f"Failed to publish Redis escalation event: {e}")
            
    return payload
