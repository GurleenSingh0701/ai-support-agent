import logging
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, Session
from database import Base
import bcrypt

try:
    from pwdlib import PasswordHash
    from pwdlib.hashers.argon2 import Argon2Hasher
    from pwdlib.hashers.bcrypt import BcryptHasher
    pwd = PasswordHash((Argon2Hasher(), BcryptHasher()))
except Exception:
    pwd = None

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), unique=False)
    role: Mapped[str] = mapped_column(String(50), default="CUSTOMER")

logging.basicConfig(level=logging.INFO)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or not plain_password:
        return False

    # Check bcrypt hash ($2a$, $2b$, $2y$)
    if hashed_password.startswith("$2"):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception as e:
            logging.error(f"Bcrypt verify error: {e}")

    # Fallback to pwdlib if hashed with argon2 or other scheme
    if pwd:
        try:
            return pwd.verify(plain_password, hashed_password)
        except Exception as e:
            logging.error(f"Pwdlib verify error: {e}")

    # Fallback for plain text password comparison (legacy)
    if plain_password == hashed_password:
        return True

    return False

def create_user(db: Session, username: str, password: str, role: str = "CUSTOMER"):
    user_exists = get_user(db, username)
    if user_exists:
        return None
    hashed_pwd = hash_password(password)
    user = User(username=username, password=hashed_pwd, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User created with username {user.username} and role {user.role}")
    return user

def get_user(db: Session, username: Optional[str] = None):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def update_user(db: Session, username: str, new_username: Optional[str] = None, new_password: Optional[str] = None, new_role: Optional[str] = None):
    user = get_user(db, username)
    if not user:
        logging.info("User not found")
        return None

    if new_username:
        user.username = new_username
    if new_password:
        user.password = hash_password(new_password)
    if new_role:
        user.role = new_role
    
    db.commit()
    db.refresh(user)
    logging.info(f"User updated with username {user.username}")
    return user   

def delete_user(db: Session, username: str):
    user = get_user(db, username)
    if not user:
        logging.info("User not found")
        return None
    deleted_username = user.username
    db.delete(user)
    db.commit()
    logging.info(f"User deleted with username {deleted_username}")
    return user
