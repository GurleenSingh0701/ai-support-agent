from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from users.user_crud import User, create_user, get_user, authenticate_user
from users.auth_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    require_role
)
from tickets.ticket_crud import Ticket

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "CUSTOMER"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    username: str
    role: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    role = user_data.role if user_data.role in ["CUSTOMER", "SUPPORT_AGENT", "ADMIN"] else "CUSTOMER"
    new_user = create_user(db, user_data.username, user_data.password, role=role)
    if not new_user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return new_user

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(user.username, role=user.role)
    refresh_token = create_refresh_token(user.username)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    username = data.get("sub")
    user = get_user(db, username) if username else None
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token(user.username, role=user.role)
    new_refresh = create_refresh_token(user.username)
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/admin/users", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    return db.query(User).all()