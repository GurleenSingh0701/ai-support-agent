import os
import uuid
import time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, redis_client
from chat.chat_crud import create_chat, get_chats_by_conversation, get_chats_by_user, get_chats_by_ticket
from users.user_crud import User
from users.auth_utils import get_optional_current_user, get_current_user
from tickets.ticket_crud import Ticket
from resolution import resolution_engine
from logs.log_analytics_engine import analytics_engine

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    ticket_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    ticket_id: Optional[int] = None
    intent: Optional[str] = "GENERAL"
    priority: Optional[str] = "MEDIUM"
    status: Optional[str] = "OPEN"

@router.post("", response_model=ChatResponse)
def chat_endpoint(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    start_time = time.time()
    user_id = current_user.id if current_user else None
    
    # Check ticket_id or auto-create a new ticket
    ticket_id = payload.ticket_id
    if ticket_id:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required to chat about a ticket")
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if getattr(ticket, "user_id") and getattr(ticket, "user_id") != current_user.id and getattr(current_user, "role", "CUSTOMER") not in ["SUPPORT_AGENT", "ADMIN"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this ticket")
    else:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required to start a ticket")
        
        message = payload.message
        db_ticket = Ticket(
            query=message[:100] if len(message) > 100 else message,
            response="Processing...",
            user_id=current_user.id,
            status="OPEN"
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        ticket_id = int(getattr(db_ticket, "id"))

    conversation_id = payload.conversation_id or str(uuid.uuid4())
    message = payload.message
    
    # Run through Resolution Engine
    res = resolution_engine.process_message(
        user_message=message,
        ticket_id=ticket_id,
        customer_id=user_id,
        user_tier="VIP" if (current_user and current_user.role == "ADMIN") else "STANDARD"
    )
    
    response_text = res["response"]
    intent = res["intent"]
    priority = res["priority"]
    status = res["status"]
    escalated = res["escalated"]
    
    # Update Ticket state
    ticket_obj = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket_obj:
        ticket_obj.response = response_text
        ticket_obj.category = intent
        ticket_obj.priority = priority
        ticket_obj.status = status
        db.commit()

    # Log metrics
    duration = time.time() - start_time
    analytics_engine.log_ticket_metrics(
        ticket_id=ticket_id,
        intent=intent,
        resolution_time_sec=duration,
        escalated=escalated,
        sentiment=res.get("sentiment", "NEUTRAL")
    )
        
    try:
        create_chat(
            db=db,
            conversation_id=conversation_id,
            message=message,
            response=response_text,
            ticket_id=ticket_id,
            user_id=user_id
        )
    except Exception as err:
        print(f"Failed to persist chat entry: {err}")

    return {
        "response": response_text,
        "conversation_id": conversation_id,
        "ticket_id": ticket_id,
        "intent": intent,
        "priority": priority,
        "status": status
    }

@router.get("/my-chats")
def get_my_chats(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    if not current_user:
        return []
    chats = get_chats_by_user(db, current_user.id)
    return [c.to_dict() for c in chats]

@router.get("/history/{conversation_id}")
def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    chats = get_chats_by_conversation(db, conversation_id)
    return [c.to_dict() for c in chats]

@router.get("/ticket/{ticket_id}")
def get_ticket_chat_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if getattr(ticket, "user_id") and getattr(ticket, "user_id") != current_user.id and current_user.role not in ["SUPPORT_AGENT", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket's chat")

    chats = get_chats_by_ticket(db, ticket_id)
    return [c.to_dict() for c in chats]
