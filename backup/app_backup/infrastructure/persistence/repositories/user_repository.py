"""
User repository implementation using SQLAlchemy.

This module provides repository implementation for user operations.
"""

import logging
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.core.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.persistence.models import UserModel


# Configure logging
logger = logging.getLogger(__name__)

# Password context for hashing and verifying
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SQLUserRepository(UserRepository):
    """
    SQLAlchemy implementation of UserRepository.
    
    This class provides methods to interact with user data in the database.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize with a database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def create(
        self,
        user: User
    ) -> User:
        """
        Create a new user.
        
        Args:
            user: User entity to create
            
        Returns:
            Created user
        """
        # Create user model
        user_model = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,  # Should already be hashed
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=datetime.utcnow(),
        )
        
        # Add to session
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        
        # Return entity
        return self._model_to_entity(user_model)
    
    async def get(self, id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            id: User ID
            
        Returns:
            User if found, None otherwise
        """
        # Query user
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == id)
        )
        user_model = result.scalars().first()
        
        # Convert to entity if found
        if user_model:
            return self._model_to_entity(user_model)
        
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        # Query user
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user_model = result.scalars().first()
        
        # Convert to entity if found
        if user_model:
            return self._model_to_entity(user_model)
        
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email address
            
        Returns:
            User if found, None otherwise
        """
        # Query user
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user_model = result.scalars().first()
        
        # Convert to entity if found
        if user_model:
            return self._model_to_entity(user_model)
        
        return None
    
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
        # Query users
        result = await self.session.execute(
            select(UserModel)
            .offset(skip)
            .limit(limit)
        )
        user_models = result.scalars().all()
        
        # Convert to entities
        return [self._model_to_entity(user_model) for user_model in user_models]
    
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
        # Query user
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == id)
        )
        user_model = result.scalars().first()
        
        # Update if found
        if user_model:
            # Update fields if provided
            if username is not None:
                user_model.username = username
            if email is not None:
                user_model.email = email
            if password is not None:
                user_model.hashed_password = pwd_context.hash(password)
            if full_name is not None:
                user_model.full_name = full_name
            if is_active is not None:
                user_model.is_active = is_active
            if is_superuser is not None:
                user_model.is_superuser = is_superuser
            
            # Update timestamp
            user_model.updated_at = datetime.utcnow()
            
            # Commit changes
            await self.session.commit()
            await self.session.refresh(user_model)
            
            # Convert to entity
            return self._model_to_entity(user_model)
        
        return None
    
    async def delete(self, id: str) -> bool:
        """
        Delete a user.
        
        Args:
            id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        # Query user
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == id)
        )
        user_model = result.scalars().first()
        
        # Delete if found
        if user_model:
            await self.session.delete(user_model)
            await self.session.commit()
            return True
        
        return False
    
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
        # Get user by username
        user = await self.get_by_username(username)
        
        # Check if user exists and verify password
        if user and self.verify_password(password, user.hashed_password):
            return user
        
        return None
    
    @staticmethod
    def verify_password(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        """
        Verify a password.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def _model_to_entity(model: UserModel) -> User:
        """
        Convert a user model to a user entity.
        
        Args:
            model: User model
            
        Returns:
            User entity
        """
        return User(
            id=str(model.id),
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            created_at=model.created_at.isoformat() if model.created_at else None,
            updated_at=model.updated_at.isoformat() if model.updated_at else None,
        ) 