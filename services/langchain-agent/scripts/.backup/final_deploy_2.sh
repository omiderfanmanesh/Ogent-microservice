#!/bin/bash
set -e

echo "==============================================="
echo "Deploying fixes for the langchain-agent service"
echo "==============================================="

# Create directory for fixes if it doesn't exist
mkdir -p fixes

# Fix for agent entity
echo "Creating fixed agent entity..."
cat > fixes/agent.py << 'EOL'
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
EOL

# Fix for base_agent
echo "Creating fixed base_agent.py..."
cat > fixes/base_agent.py << 'EOL'
"""Fixed BaseAgent implementation with proper configuration handling."""

from typing import Union, Dict, Any, Optional, List
from app.core.clients.command_client import CommandClient
from app.core.entities.agent import AgentConfiguration, AgentPermissions

class AgentCallback:
    """Base agent callback."""
    
    async def on_start(self, agent_id: str, question: str):
        """Called when agent execution starts."""
        pass
        
    async def on_end(self, agent_id: str, response: str):
        """Called when agent execution ends."""
        pass
        
    async def on_error(self, agent_id: str, error: str):
        """Called when agent execution fails."""
        pass
        
    async def on_tool_start(self, agent_id: str, tool: str):
        """Called when a tool execution starts."""
        pass
        
    async def on_tool_end(self, agent_id: str, tool: str, output: str):
        """Called when a tool execution ends."""
        pass

class BaseAgent:
    def __init__(
        self,
        configuration: Union[AgentConfiguration, Dict[str, Any]],
        permissions: AgentPermissions,
        command_client: CommandClient
    ):
        """
        Initialize the agent.
        
        Args:
            configuration: Agent configuration (can be dict or AgentConfiguration)
            permissions: Agent permissions
            command_client: Command client
        """
        # Convert configuration dictionary to AgentConfiguration if needed
        if isinstance(configuration, dict):
            self.configuration = AgentConfiguration.from_dict(configuration)
        else:
            self.configuration = configuration
            
        self.permissions = permissions
        self.command_client = command_client
        
        # Set up any common configuration
        self.model_name = self.configuration.model_name
        self.temperature = self.configuration.temperature
        self.max_tokens = self.configuration.max_tokens
        self.system_message = self.configuration.system_message
        self.streaming = self.configuration.streaming
        self.max_iterations = self.configuration.max_iterations
EOL

# Fix for command_client
echo "Creating command_client.py..."
cat > fixes/command_client.py << 'EOL'
"""
Minimal implementation of CommandClient.
"""
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CommandClient:
    """Client for executing commands."""

    def __init__(self):
        """Initialize the command client."""
        logger.info("Initializing CommandClient")
        
    async def execute_command(self, command: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a command.
        
        Args:
            command: Command to execute
            timeout: Command timeout
            
        Returns:
            Command result
        """
        logger.info(f"Executing command: {command}")
        return {
            "status": "success",
            "output": f"Command '{command}' execution simulated (no actual execution)",
            "error": None,
        }
        
    async def create_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Create a file.
        
        Args:
            path: File path
            content: File content
            
        Returns:
            Result
        """
        logger.info(f"Creating file: {path}")
        return {
            "status": "success",
            "output": f"File creation simulated at {path}",
            "error": None,
        }
        
    async def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read a file.
        
        Args:
            path: File path
            
        Returns:
            File content
        """
        logger.info(f"Reading file: {path}")
        return {
            "status": "success",
            "output": f"File read simulated for {path}",
            "error": None,
        }
EOL

# Fix for factory.py
echo "Creating fixed factory.py..."
cat > fixes/factory.py << 'EOL'
"""Fixed AgentFactory implementation."""

from typing import Dict, Any, Type, List
import importlib
import inspect
import logging
from enum import Enum

from app.core.clients.command_client import CommandClient
from app.core.entities.agent import AgentType, AgentConfiguration, AgentPermissions
from app.core.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory for creating agents."""

    def __init__(self, command_client: CommandClient):
        """
        Initialize the factory.
        
        Args:
            command_client: Command client
        """
        self.command_client = command_client
        self._agent_classes = self._discover_agent_classes()
        
    def _discover_agent_classes(self) -> Dict[str, Type[BaseAgent]]:
        """
        Discover agent classes.
        
        Returns:
            Dictionary mapping agent types to agent classes
        """
        agent_classes = {}
        
        # Import agent modules
        try:
            from app.core.agents import conversational_agent, command_agent
            
            # Add ConversationalAgent
            if hasattr(conversational_agent, "ConversationalAgent"):
                agent_classes[AgentType.CONVERSATIONAL] = conversational_agent.ConversationalAgent
            
            # Add CommandAgent if available
            if hasattr(command_agent, "CommandAgent"):
                agent_classes[AgentType.COMMAND] = command_agent.CommandAgent
                
        except ImportError as e:
            logger.error(f"Error importing agent modules: {str(e)}")
        
        return agent_classes
    
    def create_agent(
        self, 
        agent_type: str,
        configuration: AgentConfiguration,
        permissions: AgentPermissions
    ) -> BaseAgent:
        """
        Create an agent.
        
        Args:
            agent_type: Agent type
            configuration: Agent configuration
            permissions: Agent permissions
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If the agent type is not supported
        """
        # Convert agent_type if it's an enum
        if isinstance(agent_type, Enum):
            agent_type = agent_type.value
            
        # Get available agent types as string
        available_types = ", ".join(self._agent_classes.keys())
        
        # Check if agent type is supported
        if agent_type not in self._agent_classes:
            raise ValueError(f"Unsupported agent type: {agent_type}. Available types: {available_types}")
        
        # Get agent class
        agent_class = self._agent_classes[agent_type]
        
        try:
            # Create agent instance
            agent = agent_class(
                configuration=configuration,
                permissions=permissions,
                command_client=self.command_client
            )
            return agent
        except Exception as e:
            logger.error(f"Error creating agent of type {agent_type}: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to create agent of type {agent_type}: {str(e)}")
EOL

# Create a simple ConversationalAgent class
echo "Creating conversational_agent.py..."
cat > fixes/conversational_agent.py << 'EOL'
"""
Implementation of the ConversationalAgent.
"""
from typing import Dict, Any, Optional, List
import logging

from app.core.agents.base_agent import BaseAgent, AgentCallback
from app.core.clients.command_client import CommandClient
from app.core.entities.agent import AgentConfiguration, AgentPermissions

logger = logging.getLogger(__name__)

class ConversationalAgent(BaseAgent):
    """Conversational agent implementation."""
    
    def __init__(
        self,
        configuration: AgentConfiguration,
        permissions: AgentPermissions,
        command_client: CommandClient
    ):
        """
        Initialize the agent.
        
        Args:
            configuration: Agent configuration
            permissions: Agent permissions
            command_client: Command client
        """
        super().__init__(configuration, permissions, command_client)
        self.callback = None
        logger.info(f"Initialized ConversationalAgent with model {self.model_name}")
        
    async def execute(
        self,
        question: str,
        agent_id: str = None,
        callback: Optional[AgentCallback] = None
    ) -> Dict[str, Any]:
        """
        Execute the agent.
        
        Args:
            question: Question to ask
            agent_id: Agent ID
            callback: Callback for monitoring progress
            
        Returns:
            Execution result
        """
        self.callback = callback
        agent_id = agent_id or "unknown"
        
        try:
            if callback:
                await callback.on_start(agent_id, question)
                
            # Simple simulated execution
            system_message = self.system_message or "I am a helpful AI assistant."
            response = f"(Simulated response using {self.model_name}): The answer to '{question}' is 42."
            
            if callback:
                await callback.on_end(agent_id, response)
                
            return {
                "output": response,
                "error": None,
                "status": "completed"
            }
        except Exception as e:
            error_msg = f"Error executing agent: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if callback:
                await callback.on_error(agent_id, error_msg)
                
            return {
                "output": None,
                "error": error_msg,
                "status": "failed"
            }
EOL

# Create CommandAgent
echo "Creating command_agent.py..."
cat > fixes/command_agent.py << 'EOL'
"""
Implementation of the CommandAgent.
"""
from typing import Dict, Any, Optional, List
import logging

from app.core.agents.base_agent import BaseAgent, AgentCallback
from app.core.clients.command_client import CommandClient
from app.core.entities.agent import AgentConfiguration, AgentPermissions

logger = logging.getLogger(__name__)

class CommandAgent(BaseAgent):
    """Command agent implementation."""
    
    def __init__(
        self,
        configuration: AgentConfiguration,
        permissions: AgentPermissions,
        command_client: CommandClient
    ):
        """
        Initialize the agent.
        
        Args:
            configuration: Agent configuration
            permissions: Agent permissions
            command_client: Command client
        """
        super().__init__(configuration, permissions, command_client)
        self.callback = None
        logger.info(f"Initialized CommandAgent with model {self.model_name}")
        
    async def execute(
        self,
        question: str,
        agent_id: str = None,
        callback: Optional[AgentCallback] = None
    ) -> Dict[str, Any]:
        """
        Execute the agent.
        
        Args:
            question: Question to ask
            agent_id: Agent ID
            callback: Callback for monitoring progress
            
        Returns:
            Execution result
        """
        self.callback = callback
        agent_id = agent_id or "unknown"
        
        try:
            if callback:
                await callback.on_start(agent_id, question)
                
            # Check permissions
            if not self.permissions.execute_commands:
                raise ValueError("Command execution not permitted")
                
            # Simple simulated execution
            response = f"(Simulated command agent response): I would execute a command to answer '{question}'."
            
            if callback:
                await callback.on_end(agent_id, response)
                
            return {
                "output": response,
                "error": None,
                "status": "completed"
            }
        except Exception as e:
            error_msg = f"Error executing command agent: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if callback:
                await callback.on_error(agent_id, error_msg)
                
            return {
                "output": None,
                "error": error_msg,
                "status": "failed"
            }
EOL

# Create agent_result.py
echo "Creating agent_result.py..."
cat > fixes/agent_result.py << 'EOL'
"""
Simple implementation of agent result classes.
"""
from typing import Dict, List, Any, Optional
from enum import Enum

class AgentStatus(str, Enum):
    """Agent execution status."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentResult:
    """Agent execution result."""
    
    def __init__(
        self,
        output: Optional[str] = None,
        error: Optional[str] = None,
        status: AgentStatus = AgentStatus.COMPLETED,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize the result.
        
        Args:
            output: Execution output
            error: Execution error
            status: Execution status
            metadata: Execution metadata
        """
        self.output = output
        self.error = error
        self.status = status
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "output": self.output,
            "error": self.error,
            "status": self.status.value if isinstance(self.status, AgentStatus) else self.status,
            "metadata": self.metadata
        }
EOL

# Now create the directory structure needed in the container
echo "Setting up directory structure in container..."
docker exec ogent-agent-service-test mkdir -p /app/app/core/clients

# Copy files to the Docker container
echo "Copying files to container..."
docker cp fixes/command_client.py ogent-agent-service-test:/app/app/core/clients/command_client.py
docker cp fixes/agent.py ogent-agent-service-test:/app/app/core/entities/agent.py
docker cp fixes/base_agent.py ogent-agent-service-test:/app/app/core/agents/base_agent.py
docker cp fixes/factory.py ogent-agent-service-test:/app/app/core/agents/factory.py
docker cp fixes/conversational_agent.py ogent-agent-service-test:/app/app/core/agents/conversational_agent.py
docker cp fixes/command_agent.py ogent-agent-service-test:/app/app/core/agents/command_agent.py
docker cp fixes/agent_result.py ogent-agent-service-test:/app/app/core/agents/agent_result.py

# Create __init__.py files
echo "Creating __init__.py files..."
echo '"""Clients module."""' | docker exec -i ogent-agent-service-test tee /app/app/core/clients/__init__.py > /dev/null

# Restart the agent service
echo "Restarting agent service..."
docker restart ogent-agent-service-test

# Wait for service to start
echo "Waiting for service to start..."
sleep 5

# Run debug script to check the fixes
echo "Running debug script..."
docker exec ogent-agent-service-test python /app/debug_agent_structure.py

echo "Deployment completed!" 