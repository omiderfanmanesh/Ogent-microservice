"""
User repository interface.

This module defines the interface for user repositories.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.core.entities.user import User


class UserRepository(ABC):
    """
    User repository interface.
    
    This interface defines methods for user operations.
    """
    
    @abstractmethod
    async def create(
        self,
        id: str,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        """
        Create a new user.
        
        Args:
            id: User ID
            username: Username
            email: Email address
            password: Plain text password
            full_name: Full name (optional)
            is_active: Whether the user is active
            is_superuser: Whether the user is a superuser
            
        Returns:
            Created user
        """
        pass
    
    @abstractmethod
    async def get(self, id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            id: User ID
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email address
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        List users with pagination.
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of users
        """
        pass
    
    @abstractmethod
    async def update(
        self,
        id: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ) -> Optional[User]:
        """
        Update a user.
        
        Args:
            id: User ID
            username: New username (optional)
            email: New email address (optional)
            password: New plain text password (optional)
            full_name: New full name (optional)
            is_active: New active status (optional)
            is_superuser: New superuser status (optional)
            
        Returns:
            Updated user if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """
        Delete a user.
        
        Args:
            id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def authenticate(
        self,
        username: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User if authentication successful, None otherwise
        """
        pass 