"""
Agent entity module.

Defines the Agent entity and related models.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid


class AgentPermissions(BaseModel):
    """
    Permissions for an agent.
    
    Defines what the agent is allowed to do.
    """
    execute_commands: bool = Field(
        default=False,
        description="Whether the agent can execute commands"
    )
    allowed_commands: List[str] = Field(
        default_factory=list,
        description="List of allowed command patterns"
    )
    allowed_paths: List[str] = Field(
        default_factory=list,
        description="List of filesystem paths the agent is allowed to access"
    )
    network_access: bool = Field(
        default=False,
        description="Whether the agent has network access"
    )
    memory_limit: Optional[int] = Field(
        default=None,
        description="Optional memory limit in MB for agent processes"
    )


class AgentConfiguration(BaseModel):
    """
    Configuration for an agent.
    
    Defines agent settings and parameters.
    """
    model_name: str = Field(
        default="gpt-4",
        description="LLM model name to use for this agent"
    )
    temperature: float = Field(
        default=0.7,
        description="Temperature for LLM generation"
    )
    max_tokens: int = Field(
        default=1024,
        description="Maximum tokens for LLM responses"
    )
    system_message: Optional[str] = Field(
        default=None,
        description="Custom system message for the agent"
    )
    streaming: bool = Field(
        default=False,
        description="Whether to stream LLM responses"
    )
    tools: List[str] = Field(
        default_factory=lambda: ["execute_command"],
        description="Tools available to the agent"
    )
    max_iterations: int = Field(
        default=15,
        description="Maximum iterations for agent execution"
    )


class Agent(BaseModel):
    """
    Agent entity.
    
    Represents an agent that can execute commands and respond to user queries.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Name of the agent")
    description: Optional[str] = Field(default=None, description="Description of the agent")
    type: str = Field(..., description="Type of agent (e.g., 'conversational', 'command')")
    configuration: AgentConfiguration = Field(default_factory=AgentConfiguration)
    permissions: AgentPermissions = Field(default_factory=AgentPermissions)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None, description="User ID of creator")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "agent-123456",
                "name": "Terminal Assistant",
                "description": "Assistant for executing terminal commands",
                "type": "command",
                "configuration": {
                    "model_name": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "system_message": "You are a helpful assistant for executing terminal commands."
                },
                "permissions": {
                    "execute_commands": True,
                    "allowed_commands": ["ls", "find", "grep"],
                    "allowed_paths": ["/home/user/data"],
                    "network_access": False
                },
                "metadata": {
                    "tags": ["terminal", "commands"],
                    "version": "1.0"
                },
                "created_at": "2023-06-15T14:30:50Z",
                "updated_at": "2023-06-15T14:30:50Z",
                "created_by": "user-345678"
            }
        }
    ) 