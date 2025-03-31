"""
Agent entity module.

Defines the Agent entity representing a LangChain agent in the system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid


class AgentPermissions(BaseModel):
    """
    Defines the permissions for agent execution.
    """
    allowed_commands: List[str] = Field(
        default_factory=list,
        description="List of commands this agent is allowed to execute"
    )
    allowed_paths: List[str] = Field(
        default_factory=list,
        description="List of file system paths this agent is allowed to access"
    )
    max_execution_time: int = Field(
        default=60,
        description="Maximum execution time in seconds"
    )
    memory_quota: int = Field(
        default=512,
        description="Memory quota in MB"
    )
    network_access: bool = Field(
        default=False,
        description="Whether the agent has network access"
    )


class AgentConfiguration(BaseModel):
    """
    Configuration for a LangChain agent.
    """
    model: str = Field(
        default="gpt-3.5-turbo",
        description="LLM model used by this agent"
    )
    temperature: float = Field(
        default=0.7,
        description="Temperature parameter for the LLM"
    )
    max_tokens: int = Field(
        default=4096,
        description="Maximum tokens for the LLM response"
    )
    tools: List[str] = Field(
        default_factory=list,
        description="List of tools available to this agent"
    )
    memory_type: str = Field(
        default="buffer",
        description="Type of memory to use (buffer, summary, etc.)"
    )
    memory_k: int = Field(
        default=5,
        description="Number of interactions to keep in memory"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Custom system prompt for the agent"
    )


class Agent(BaseModel):
    """
    Represents a LangChain agent in the system.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Name of the agent")
    description: Optional[str] = Field(
        default=None,
        description="Description of the agent's purpose"
    )
    type: str = Field(..., description="Type of agent (e.g., command_execution, research)")
    configuration: AgentConfiguration = Field(
        default_factory=AgentConfiguration,
        description="Agent's LLM and behavior configuration"
    )
    permissions: AgentPermissions = Field(
        default_factory=AgentPermissions,
        description="Agent's execution permissions"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the agent"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None, description="ID of the user who created this agent")
    
    class Config:
        """Pydantic config"""
        model_config = ConfigDict(
            json_schema_extra = {
                "example": {
                    "id": "agent-123456",
                    "name": "File System Manager",
                    "description": "Agent for managing file system operations",
                    "type": "command_execution",
                    "configuration": {
                        "model": "gpt-4",
                        "temperature": 0.2,
                        "max_tokens": 8192,
                        "tools": ["file_system", "search"]
                    },
                    "permissions": {
                        "allowed_commands": ["ls", "find", "grep"],
                        "allowed_paths": ["/home/user/data"],
                        "max_execution_time": 120
                    },
                    "metadata": {
                        "tags": ["file-system", "search"],
                        "version": "1.0.0"
                    },
                    "created_at": "2023-06-15T14:30:00Z",
                    "updated_at": "2023-06-15T14:30:00Z",
                    "created_by": "user-789"
                }
            }
        )
