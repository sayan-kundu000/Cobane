import bcrypt
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import jwt
from app.core.config import settings
from app.utils.datetime_helpers import get_utc_now

ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Hashes a plain password using native bcrypt library to bypass passlib bugs."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hashed value using native bcrypt."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:  # pylint: disable=broad-exception-caught
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates an HS256 access token containing specific claim payloads."""
    to_encode = data.copy()
    expire = get_utc_now() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates an HS256 refresh token with longer expiration durations."""
    to_encode = data.copy()
    expire = get_utc_now() + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decodes a JWT token signature. Raises JWTError if signature validation fails."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
