"""
Fixed version of the Agent class to properly handle dictionary configurations.
This ensures that when a dictionary is passed as configuration, it gets converted to AgentConfiguration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Union, cast


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
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_message: Optional[str] = None
    streaming: bool = False
    tools: List[Dict[str, Any]] = field(default_factory=list)
    max_iterations: int = 10
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfiguration':
        """
        Create an AgentConfiguration from a dictionary.
        
        Args:
            data: Dictionary with configuration values
            
        Returns:
            AgentConfiguration instance
        """
        # Filter out None values and unknown fields
        filtered_data = {}
        for key, value in data.items():
            if key in cls.__annotations__ and value is not None:
                filtered_data[key] = value
        
        return cls(**filtered_data)


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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentPermissions':
        """
        Create an AgentPermissions from a dictionary.
        
        Args:
            data: Dictionary with permissions values
            
        Returns:
            AgentPermissions instance
        """
        # Filter out None values and unknown fields
        filtered_data = {}
        for key, value in data.items():
            if key in cls.__annotations__ and value is not None:
                filtered_data[key] = value
        
        return cls(**filtered_data)


@dataclass
class Agent:
    """
    Agent entity.
    
    Represents an agent in the system.
    """
    name: str
    user_id: str
    agent_type: Union[AgentType, str]
    id: Optional[str] = None
    description: Optional[str] = None
    configuration: Union[AgentConfiguration, Dict[str, Any]] = field(default_factory=AgentConfiguration)
    permissions: Union[AgentPermissions, Dict[str, Any]] = field(default_factory=AgentPermissions)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """
        Post-initialization processing.
        
        Converts string agent_type to enum and dictionary configurations to proper objects.
        """
        # Convert agent_type string to enum if needed
        if isinstance(self.agent_type, str):
            try:
                self.agent_type = AgentType(self.agent_type)
            except ValueError:
                # Keep as string if not a valid enum value
                pass
        
        # Convert configuration dictionary to AgentConfiguration if needed
        if isinstance(self.configuration, dict):
            self.configuration = AgentConfiguration.from_dict(self.configuration)
        
        # Convert permissions dictionary to AgentPermissions if needed
        if isinstance(self.permissions, dict):
            self.permissions = AgentPermissions.from_dict(self.permissions) 