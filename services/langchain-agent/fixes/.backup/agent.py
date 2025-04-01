"""
Complete agent entity module with all necessary classes.
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from uuid import uuid4

class AgentType(str, Enum):
    """Agent type enumeration."""
    CONVERSATIONAL = "conversational"
    COMMAND = "command"

class AgentConfiguration:
    """Agent configuration."""

    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_message: Optional[str] = None
    streaming: bool = False
    tools: List[str] = []
    max_iterations: int = 10

    @classmethod
    def from_dict(cls, config_dict: dict) -> "AgentConfiguration":
        """
        Create an AgentConfiguration instance from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            AgentConfiguration instance
        """
        config = cls()
        
        # Set attributes from dictionary if they exist
        if "model_name" in config_dict:
            config.model_name = config_dict["model_name"]
        if "temperature" in config_dict:
            config.temperature = config_dict["temperature"]
        if "max_tokens" in config_dict:
            config.max_tokens = config_dict["max_tokens"]
        if "system_message" in config_dict:
            config.system_message = config_dict["system_message"]
        if "streaming" in config_dict:
            config.streaming = config_dict["streaming"]
        if "tools" in config_dict:
            config.tools = config_dict["tools"]
        if "max_iterations" in config_dict:
            config.max_iterations = config_dict["max_iterations"]
            
        return config

class AgentPermissions:
    """Agent permissions."""

    execute_commands: bool = False
    network_access: bool = False

class Agent:
    """Agent entity."""

    def __init__(
        self,
        id: str = None,
        name: str = None,
        description: str = None,
        user_id: str = None,
        agent_type: Union[AgentType, str] = None,
        configuration: Union[AgentConfiguration, Dict[str, Any]] = None,
        permissions: Union[AgentPermissions, Dict[str, bool]] = None,
        metadata: Dict[str, Any] = None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        """
        Initialize the agent.
        
        Args:
            id: Agent ID
            name: Agent name
            description: Agent description
            user_id: User ID
            agent_type: Agent type
            configuration: Agent configuration
            permissions: Agent permissions
            metadata: Agent metadata
            created_at: Creation timestamp
            updated_at: Update timestamp
        """
        self.id = id or str(uuid4())
        self.name = name
        self.description = description
        self.user_id = user_id
        
        # Handle agent_type being either string or enum
        if isinstance(agent_type, str):
            try:
                self.agent_type = AgentType(agent_type)
            except ValueError:
                self.agent_type = agent_type
        else:
            self.agent_type = agent_type

        # Handle configuration
        if isinstance(configuration, dict):
            self.configuration = AgentConfiguration.from_dict(configuration)
        else:
            self.configuration = configuration or AgentConfiguration()

        # Handle permissions
        if isinstance(permissions, dict):
            perm = AgentPermissions()
            if "execute_commands" in permissions:
                perm.execute_commands = permissions["execute_commands"]
            if "network_access" in permissions:
                perm.network_access = permissions["network_access"]
            self.permissions = perm
        else:
            self.permissions = permissions or AgentPermissions()

        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent to dictionary.
        
        Returns:
            Dictionary representation of agent
        """
        configuration_dict = {
            "model_name": self.configuration.model_name,
            "temperature": self.configuration.temperature,
            "max_tokens": self.configuration.max_tokens,
            "system_message": self.configuration.system_message,
            "streaming": self.configuration.streaming,
            "tools": self.configuration.tools,
            "max_iterations": self.configuration.max_iterations
        }
        
        permissions_dict = {
            "execute_commands": self.permissions.execute_commands,
            "network_access": self.permissions.network_access
        }
        
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "agent_type": self.agent_type.value if isinstance(self.agent_type, AgentType) else self.agent_type,
            "configuration": configuration_dict,
            "permissions": permissions_dict,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """
        Create agent from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            Agent instance
        """
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            user_id=data.get("user_id"),
            agent_type=data.get("agent_type"),
            configuration=data.get("configuration"),
            permissions=data.get("permissions"),
            metadata=data.get("metadata"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
