"""
Authentication routes.

This module provides routes for user authentication and management.
"""

import logging
from typing import Dict, Any, Optional
from datetime import timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field

from app.api.auth import create_access_token, get_current_user
from app.api.dependencies import get_session
from app.core.entities.user import User
from app.infrastructure.persistence.repositories.user_repository import SQLUserRepository
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


# Schema models
class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    """User creation schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: Optional[str] = None

    class Config:
        """Pydantic config."""
        from_attributes = True


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Args:
        form_data: OAuth2 password request form
        db: Database session
        
    Returns:
        Access token
        
    Raises:
        HTTPException: If authentication fails
    """
    # Create user repository
    user_repo = SQLUserRepository(db)
    
    # Authenticate user
    user = await user_repo.authenticate(
        username=form_data.username,
        password=form_data.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        user_id=str(user.id),
        username=user.username,
        is_superuser=user.is_superuser,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_session),
):
    """
    Register a new user.
    
    Args:
        user_data: User creation data
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If user creation fails
    """
    # Create user repository
    user_repo = SQLUserRepository(db)
    
    # Check if username exists
    existing_user = await user_repo.get_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email exists
    existing_email = await user_repo.get_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    user_id = str(uuid4())
    user = await user_repo.create(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )
    
    return user


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user details
    """
    return current_user


@router.post("/reset-password", response_model=Dict[str, Any])
async def reset_password(
    email: EmailStr,
    db: AsyncSession = Depends(get_session),
):
    """
    Request password reset.
    
    Args:
        email: User email
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found
    """
    # Create user repository
    user_repo = SQLUserRepository(db)
    
    # Check if email exists
    user = await user_repo.get_by_email(email)
    if not user:
        # Return success even if user doesn't exist for security reasons
        return {"message": "Password reset email sent if account exists"}
    
    # In a real implementation, you would generate a reset token and send an email
    # For now, we'll just return a success message
    logger.info(f"Password reset requested for email: {email}")
    
    return {"message": "Password reset email sent if account exists"} 