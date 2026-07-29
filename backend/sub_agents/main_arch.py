from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class AgentState(BaseModel):
    ticket_id: Optional[int] = None
    customer_id: Optional[int] = None
    user_message: str
    user_tier: str = "STANDARD"
    conversation_history: List[Dict[str, str]] = []
    intent: str = "OTHER"
    confidence: float = 1.0
    entities: Dict[str, Any] = {}
    sentiment: str = "NEUTRAL"
    priority: str = "MEDIUM"
    sub_agent_output: Optional[str] = None
    requires_escalation: bool = False
    escalation_reason: Optional[str] = None

class BaseSubAgent:
    def execute(self, state: AgentState) -> AgentState:
        raise NotImplementedError("Sub-agents must implement execute method.")
