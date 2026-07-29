from typing import Dict, Any, Optional
from router.router_agent import router_agent

class ResolutionEngine:
    def process_message(
        self,
        user_message: str,
        ticket_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        user_tier: str = "STANDARD",
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Delegates processing to the LangGraph RouterAgent Orchestrator.
        """
        return router_agent.route_message(
            user_message=user_message,
            ticket_id=ticket_id,
            customer_id=customer_id,
            user_tier=user_tier
        )

resolution_engine = ResolutionEngine()
