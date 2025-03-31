"""
User entity.

This module defines the User entity for authentication.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class User:
    """
    User entity for authentication.
    """
    id: str
    username: str
    email: str
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    hashed_password: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def create_system_user(cls) -> "User":
        """
        Create a system user.
        
        Returns:
            A system user with superuser privileges
        """
        return cls(
            id="system",
            username="system",
            email="system@example.com",
            is_active=True,
            is_superuser=True
        )
    
    @classmethod
    def create_anonymous_user(cls) -> "User":
        """
        Create an anonymous user.
        
        Returns:
            An anonymous user with limited privileges
        """
        return cls(
            id="anonymous",
            username="anonymous",
            email=None,
            is_active=True,
            is_superuser=False
        ) 