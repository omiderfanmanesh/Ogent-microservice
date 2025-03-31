"""
Database models.

This module provides SQLAlchemy models for database tables.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, 
    DateTime, ForeignKey, JSON, Float,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Create base model
Base = declarative_base()


class AgentModel(Base):
    """
    Database model for agents.
    
    This model represents the agents table in the database.
    """
    
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(50), nullable=False)
    config = Column(JSON, nullable=False, default=dict)
    permissions = Column(JSON, nullable=False, default=dict)
    user_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("ExecutionModel", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Agent id={self.id} name={self.name} type={self.agent_type}>"


class ExecutionModel(Base):
    """
    Database model for executions.
    
    This model represents the executions table in the database.
    """
    
    __tablename__ = "executions"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    input = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    output = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    execution_metadata = Column(JSON, nullable=True)
    user_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="executions")
    steps = relationship("ExecutionStepModel", back_populates="execution", cascade="all, delete-orphan")
    commands = relationship("CommandModel", back_populates="execution", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Execution id={self.id} agent_id={self.agent_id} status={self.status}>"


class ExecutionStepModel(Base):
    """
    Database model for execution steps.
    
    This model represents the execution_steps table in the database.
    """
    
    __tablename__ = "execution_steps"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    step_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    execution = relationship("ExecutionModel", back_populates="steps")
    
    def __repr__(self) -> str:
        return f"<ExecutionStep id={self.id} execution_id={self.execution_id} type={self.step_type}>"


class CommandModel(Base):
    """
    Database model for commands.
    
    This model represents the commands table in the database.
    """
    
    __tablename__ = "commands"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    command = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    exit_code = Column(Integer, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    execution = relationship("ExecutionModel", back_populates="commands")
    
    def __repr__(self) -> str:
        return f"<Command id={self.id} execution_id={self.execution_id} status={self.status}>"
