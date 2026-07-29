from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from users.user_crud import User
from users.auth_utils import get_current_user
from tickets.ticket_crud import Ticket

router = APIRouter(prefix="/users/history", tags=["user_history"])

@router.get("/")
def get_user_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).filter(Ticket.user_id == current_user.id).order_by(Ticket.created_at.desc()).all()
    history_records = []
    for t in tickets:
        history_records.append({
            "ticket_id": t.id,
            "title": t.query[:50] + "..." if len(t.query) > 50 else t.query,
            "status": getattr(t, "status", "OPEN"),
            "category": getattr(t, "category", "GENERAL"),
            "created_at": t.created_at.isoformat() if t.created_at else None
        })
    return {"user_id": current_user.id, "username": current_user.username, "total_tickets": len(tickets), "tickets": history_records}
