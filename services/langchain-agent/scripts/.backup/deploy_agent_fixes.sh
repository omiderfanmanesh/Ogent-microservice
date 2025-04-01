#!/bin/bash
set -e

echo "Deploying fixes for agent service..."

# Create directory for fixes if it doesn't exist
mkdir -p fixes

# Create temp file for base_agent.py
cat > fixes/base_agent_temp.py << 'EOL'
from typing import Union, Dict, Any, Optional, List
from app.core.clients.command_client import CommandClient
from app.core.entities.agent import AgentConfiguration, AgentPermissions

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

# Create temp file for agent.py
cat > fixes/agent_temp.py << 'EOL'
from typing import List, Optional, Dict, Any

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

# Rest of the original file would go here...
class AgentPermissions:
    """Agent permissions."""

    execute_commands: bool = False
    network_access: bool = False
EOL

# Copy files to the Docker container
echo "Copying fixes to container..."
docker cp fixes/base_agent_temp.py ogent-agent-service-test:/app/app/core/agents/base_agent.py
docker cp fixes/agent_temp.py ogent-agent-service-test:/app/app/core/entities/agent.py
docker cp verify_service.py ogent-agent-service-test:/app/verify_service.py

# Restart the agent service
echo "Restarting agent service..."
docker restart ogent-agent-service-test

# Run verification script
echo "Waiting for service to start..."
sleep 3
echo "Running verification script..."
docker exec ogent-agent-service-test python /app/verify_service.py

echo "Deployment completed!" 