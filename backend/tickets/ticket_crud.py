from typing import Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id: Any = Column(Integer, primary_key=True, index=True)
    query: Any = Column(Text, nullable=False)
    response: Any = Column(Text, nullable=False)
    category: Any = Column(String(50), default="GENERAL")
    priority: Any = Column(String(20), default="MEDIUM")
    status: Any = Column(String(20), default="OPEN")
    created_at: Any = Column(DateTime, default=datetime.utcnow)
    user_id: Any = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_agent_id: Any = Column(Integer, ForeignKey("users.id"), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "query": self.query,
            "response": self.response,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
            "assigned_agent_id": self.assigned_agent_id
        }
