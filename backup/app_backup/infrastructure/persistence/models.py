"""
Database models.

This module provides SQLAlchemy models for database tables.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, 
    DateTime, ForeignKey, JSON, Float, MetaData,
    create_engine, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Create base model with explicit naming convention
meta = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})
Base = declarative_base(metadata=meta)


class UserModel(Base):
    """
    User model.
    
    Represents a user in the system with authentication information.
    """
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    
    # Relationships
    agents = relationship("AgentModel", back_populates="user", cascade="all, delete-orphan")
    executions = relationship("ExecutionModel", back_populates="user", cascade="all, delete-orphan")


class AgentModel(Base):
    """
    Agent database model.
    """
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Store JSON data in these columns
    config = Column(JSON, nullable=False, default=lambda: {})
    permissions = Column(JSON, nullable=False, default=lambda: {})
    agent_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    executions = relationship("ExecutionModel", back_populates="agent", cascade="all, delete-orphan")
    user = relationship("UserModel", back_populates="agents")


class ExecutionModel(Base):
    """
    Execution database model.
    """
    __tablename__ = "executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    execution_metadata = Column(JSON, nullable=False, default=lambda: {})
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="executions")
    steps = relationship("ExecutionStepModel", back_populates="execution", cascade="all, delete-orphan")
    commands = relationship("CommandModel", back_populates="execution", cascade="all, delete-orphan")
    user = relationship("UserModel", back_populates="executions")


class ExecutionStepModel(Base):
    """
    Execution step database model.
    """
    __tablename__ = "execution_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    step_metadata = Column(JSON, nullable=False, default=lambda: {})
    
    # Relationships
    execution = relationship("ExecutionModel", back_populates="steps")


class CommandModel(Base):
    """
    Command database model.
    """
    __tablename__ = "commands"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    command = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    exit_code = Column(Integer, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    command_metadata = Column(JSON, nullable=False, default=lambda: {})
    
    # Relationships
    execution = relationship("ExecutionModel", back_populates="commands") 