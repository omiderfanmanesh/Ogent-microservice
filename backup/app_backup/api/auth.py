"""
Authentication module.

This module provides utilities for user authentication and authorization.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings
from app.core.entities.user import User

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 password bearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password is valid, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


# Token payload model
class TokenPayload(BaseModel):
    """Token payload model."""
    sub: str
    exp: int
    iat: int
    user_id: str
    username: str
    is_superuser: bool


def create_access_token(
    user_id: str,
    username: str,
    is_superuser: bool = False,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User ID to encode in the token
        username: Username to encode in the token
        is_superuser: Whether the user is a superuser
        expires_delta: Optional expiration time delta
        
    Returns:
        JWT token as a string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    
    expires_at = datetime.utcnow() + expires_delta
    
    # Create payload
    payload = {
        "sub": user_id,
        "exp": expires_at.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "user_id": user_id,
        "username": username,
        "is_superuser": is_superuser,
    }
    
    # Create token
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current authenticated user from the JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        User instance
        
    Raises:
        HTTPException: If authentication fails
    """
    authenticate_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )
        
        # Extract user info
        user_id = payload.get("user_id")
        username = payload.get("username")
        is_superuser = payload.get("is_superuser", False)
        
        if not user_id or not username:
            raise authenticate_exception
        
        # Create user instance
        return User(
            id=user_id,
            username=username,
            email=f"{username}@example.com",  # Placeholder email
            is_active=True,
            is_superuser=is_superuser,
        )
        
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise authenticate_exception


async def validate_token_ws(token: str) -> Optional[User]:
    """
    Validate a JWT token for WebSocket connections.
    
    Args:
        token: JWT token
        
    Returns:
        User instance if token is valid, None otherwise
    """
    try:
        # Decode token
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )
        
        # Extract user info
        user_id = payload.get("user_id")
        username = payload.get("username")
        is_superuser = payload.get("is_superuser", False)
        
        if not user_id or not username:
            return None
        
        # Create user instance
        return User(
            id=user_id,
            username=username,
            email=f"{username}@example.com",  # Placeholder email
            is_active=True,
            is_superuser=is_superuser,
        )
        
    except JWTError as e:
        logger.error(f"WebSocket JWT error: {str(e)}")
        return None 