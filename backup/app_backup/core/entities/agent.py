"""
Agent entity module.

This module defines the agent entity and related types.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AgentType(str, Enum):
    """
    Enumeration of supported agent types.
    """
    COMMAND = "command"
    SQL = "sql"
    CUSTOM = "custom"


class AgentConfiguration(BaseModel):
    """
    Configuration for an agent.
    """
    model_name: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2000)
    streaming: bool = Field(default=False)
    tools: list = Field(default_factory=list)
    max_iterations: int = Field(default=10)


class AgentPermissions(BaseModel):
    """
    Permissions for an agent.
    """
    execute_commands: bool = Field(default=False)
    allowed_commands: list = Field(default_factory=list)
    allowed_paths: list = Field(default_factory=list)
    network_access: bool = Field(default=False)
    memory_limit: int = Field(default=1024)  # MB


class Agent(BaseModel):
    """
    Agent entity.
    """
    id: str
    name: str
    user_id: str
    agent_type: AgentType
    description: Optional[str] = None
    configuration: AgentConfiguration = Field(default_factory=AgentConfiguration)
    permissions: AgentPermissions = Field(default_factory=AgentPermissions)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 