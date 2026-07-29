import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, redis_client
from tickets.ticket_crud import Ticket
from users.user_crud import User
from users.auth_utils import get_optional_current_user, get_current_user, require_role
from resolution import resolution_engine

router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketCreate(BaseModel):
    query: str
    response: Optional[str] = None
    category: Optional[str] = "GENERAL"
    priority: Optional[str] = "MEDIUM"

class StatusUpdate(BaseModel):
    status: str

class AssignAgentRequest(BaseModel):
    agent_id: int

class TicketResponse(BaseModel):
    id: int
    query: str
    response: str
    category: Optional[str] = "GENERAL"
    priority: Optional[str] = "MEDIUM"
    status: Optional[str] = "OPEN"
    created_at: datetime
    user_id: Optional[int] = None
    assigned_agent_id: Optional[int] = None

    class Config:
        from_attributes = True

@router.post("/create-ticket", response_model=TicketResponse)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    user_id = current_user.id if current_user else None
    
    # If response is not provided, process through AI Resolution Engine
    if not ticket_data.response:
        res = resolution_engine.process_message(
            user_message=ticket_data.query,
            customer_id=user_id,
            user_tier="VIP" if (current_user and current_user.role == "ADMIN") else "STANDARD"
        )
        ai_response = res["response"]
        status = res["status"]
        priority = res["priority"]
        category = res["intent"]
    else:
        ai_response = ticket_data.response
        status = "OPEN"
        priority = ticket_data.priority or "MEDIUM"
        category = ticket_data.category or "GENERAL"

    db_ticket = Ticket(
        query=ticket_data.query,
        response=ai_response,
        category=category,
        priority=priority,
        status=status,
        user_id=user_id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    if redis_client:
        try:
            redis_client.delete("tickets:all")
        except Exception as e:
            print(f"Redis cache error: {e}")
            
    return db_ticket

@router.get("/my-tickets", response_model=List[TicketResponse])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    if not current_user:
        return []
    return db.query(Ticket).filter(Ticket.user_id == current_user.id).order_by(Ticket.created_at.desc()).all()

@router.get("/all-tickets", response_model=List[TicketResponse])
def get_all_tickets(db: Session = Depends(get_db)):
    cache_key = "tickets:all"
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                tickets_list = json.loads(cached_data)
                for t in tickets_list:
                    if t.get("created_at"):
                        t["created_at"] = datetime.fromisoformat(t["created_at"])
                return tickets_list
        except Exception:
            pass

    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
    
    if redis_client:
        try:
            serialized = [t.to_dict() for t in tickets]
            redis_client.setex(cache_key, 60, json.dumps(serialized))
        except Exception:
            pass

    return tickets

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket

@router.patch("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    payload: StatusUpdate,
    current_user: User = Depends(require_role(["SUPPORT_AGENT", "ADMIN"])),
    db: Session = Depends(get_db)
):
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    db_ticket.status = payload.status
    db.commit()
    db.refresh(db_ticket)
    
    if redis_client:
        try:
            redis_client.delete("tickets:all")
        except Exception:
            pass
            
    return {"message": "Status updated successfully", "ticket_id": ticket_id, "new_status": db_ticket.status}

@router.post("/{ticket_id}/assign")
def assign_ticket_agent(
    ticket_id: int,
    payload: AssignAgentRequest,
    current_user: User = Depends(require_role(["SUPPORT_AGENT", "ADMIN"])),
    db: Session = Depends(get_db)
):
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    db_ticket.assigned_agent_id = payload.agent_id
    db_ticket.status = "IN_PROGRESS"
    db.commit()
    db.refresh(db_ticket)
    
    return {"message": "Agent assigned successfully", "ticket_id": ticket_id, "assigned_agent_id": payload.agent_id}