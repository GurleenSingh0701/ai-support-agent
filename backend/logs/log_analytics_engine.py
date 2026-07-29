import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)

class AnalyticsLogEngine:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log_ticket_metrics(
        self,
        ticket_id: int,
        intent: str,
        resolution_time_sec: float,
        escalated: bool,
        sentiment: str
    ):
        entry = {
            "ticket_id": ticket_id,
            "intent": intent,
            "resolution_time_sec": resolution_time_sec,
            "escalated": escalated,
            "sentiment": sentiment,
            "timestamp": time.time()
        }
        self.logs.append(entry)
        logging.info(f"Logged analytics entry for Ticket #{ticket_id}")

    def get_summary_metrics(self) -> Dict[str, Any]:
        total = len(self.logs)
        if total == 0:
            return {
                "total_tickets": 0,
                "ai_resolution_rate": "100%",
                "escalation_rate": "0%",
                "avg_resolution_time_sec": 0.0
            }
        
        escalated_count = sum(1 for l in self.logs if l["escalated"])
        avg_time = sum(l["resolution_time_sec"] for l in self.logs) / total
        ai_resolved = total - escalated_count
        
        return {
            "total_tickets": total,
            "ai_resolution_rate": f"{(ai_resolved / total) * 100:.1f}%",
            "escalation_rate": f"{(escalated_count / total) * 100:.1f}%",
            "avg_resolution_time_sec": round(avg_time, 2)
        }

analytics_engine = AnalyticsLogEngine()
