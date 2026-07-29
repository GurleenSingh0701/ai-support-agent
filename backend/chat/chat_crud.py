from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session
from database import Base

class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    ticket_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "message": self.message,
            "response": self.response,
            "ticket_id": self.ticket_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# CRUD Operations

def create_chat(
    db: Session,
    conversation_id: str,
    message: str,
    response: str,
    ticket_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> Chat:
    """Create and persist a new chat message entry."""
    chat = Chat(
        conversation_id=conversation_id,
        message=message,
        response=response,
        ticket_id=ticket_id,
        user_id=user_id
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_chat_by_id(db: Session, chat_id: int) -> Optional[Chat]:
    """Retrieve a single chat entry by its primary key ID."""
    return db.query(Chat).filter(Chat.id == chat_id).first()

def get_chats_by_conversation(db: Session, conversation_id: str) -> List[Chat]:
    """Retrieve all chat messages associated with a conversation ID."""
    return db.query(Chat).filter(Chat.conversation_id == conversation_id).order_by(Chat.created_at.asc()).all()

def get_chats_by_user(db: Session, user_id: int) -> List[Chat]:
    """Retrieve all chat messages created by a specific user."""
    return db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).all()

def get_chats_by_ticket(db: Session, ticket_id: int) -> List[Chat]:
    """Retrieve all chat messages associated with a specific ticket ID."""
    return db.query(Chat).filter(Chat.ticket_id == ticket_id).order_by(Chat.created_at.asc()).all()

def get_all_chats(db: Session, skip: int = 0, limit: int = 100) -> List[Chat]:
    """Retrieve a paginated list of all chat entries."""
    return db.query(Chat).offset(skip).limit(limit).all()

def update_chat(
    db: Session,
    chat_id: int,
    message: Optional[str] = None,
    response: Optional[str] = None,
    ticket_id: Optional[int] = None
) -> Optional[Chat]:
    """Update an existing chat entry's message, response, or ticket ID."""
    chat = get_chat_by_id(db, chat_id)
    if not chat:
        return None
    if message is not None:
        chat.message = message
    if response is not None:
        chat.response = response
    if ticket_id is not None:
        chat.ticket_id = ticket_id
    db.commit()
    db.refresh(chat)
    return chat

def delete_chat(db: Session, chat_id: int) -> Optional[Chat]:
    """Delete a single chat entry by ID."""
    chat = get_chat_by_id(db, chat_id)
    if not chat:
        return None
    db.delete(chat)
    db.commit()
    return chat

def delete_conversation(db: Session, conversation_id: str) -> int:
    """Delete all chat entries for a given conversation ID."""
    deleted_count = db.query(Chat).filter(Chat.conversation_id == conversation_id).delete()
    db.commit()
    return deleted_count
