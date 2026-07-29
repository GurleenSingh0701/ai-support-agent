import pytest
from datetime import datetime, timedelta, timezone
import jwt
from users.auth_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    require_role,
    SECRET_KEY,
    ALGORITHM
)
from users.user_crud import User
from fastapi import HTTPException

def test_create_access_token():
    token = create_access_token("testuser", role="ADMIN")
    payload = decode_token(token)
    
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["role"] == "ADMIN"
    assert payload["type"] == "access"

def test_create_refresh_token():
    token = create_refresh_token("testuser")
    payload = decode_token(token)
    
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["type"] == "refresh"

def test_decode_token_invalid():
    assert decode_token("invalid.jwt.token") is None

def test_decode_token_expired():
    expired_payload = {
        "sub": "testuser",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10)
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    assert decode_token(expired_token) is None

def test_require_role_allowed():
    user = User(id=1, username="admin_user", role="ADMIN")
    checker = require_role(["ADMIN", "SUPPORT"])
    result = checker(current_user=user)
    assert result.username == "admin_user"

def test_require_role_denied():
    user = User(id=2, username="customer_user", role="CUSTOMER")
    checker = require_role(["ADMIN", "SUPPORT"])
    
    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=user)
    
    assert exc_info.value.status_code == 403
    assert "Permission denied" in exc_info.value.detail
