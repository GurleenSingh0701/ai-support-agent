from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from users.user_crud import User, update_user
from users.auth_utils import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class UserProfileUpdate(BaseModel):
    new_username: Optional[str] = None
    new_password: Optional[str] = None

@router.patch("/profile")
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated = update_user(
        db=db,
        username=current_user.username,
        new_username=profile_data.new_username,
        new_password=profile_data.new_password
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update user profile")
    return {"message": "Profile updated successfully", "username": updated.username, "role": updated.role}
