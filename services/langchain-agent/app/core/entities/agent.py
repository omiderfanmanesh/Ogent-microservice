"""
Agent entity.

This module provides the agent entity model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional


class AgentType(Enum):
    """
    Agent type enum.
    
    Defines the available agent types.
    """
    CONVERSATIONAL = "conversational"
    COMMAND = "command"
    SQL = "sql"
    CUSTOM = "custom"


@dataclass
class AgentConfiguration:
    """
    Agent configuration.
    
    Contains configurable settings for an agent.
    """
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_message: Optional[str] = None
    streaming: bool = False
    tools: List[Dict[str, Any]] = field(default_factory=list)
    max_iterations: int = 10


@dataclass
class AgentPermissions:
    """
    Agent permissions.
    
    Defines what actions an agent is allowed to perform.
    """
    execute_commands: bool = False
    allowed_commands: List[str] = field(default_factory=list)
    allowed_paths: List[str] = field(default_factory=list)
    network_access: bool = False
    memory_limit: Optional[int] = None


@dataclass
class Agent:
    """
    Agent entity.
    
    Represents an agent in the system.
    """
    name: str
    user_id: str
    agent_type: AgentType
    id: Optional[str] = None
    description: Optional[str] = None
    configuration: AgentConfiguration = field(default_factory=AgentConfiguration)
    permissions: AgentPermissions = field(default_factory=AgentPermissions)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None 