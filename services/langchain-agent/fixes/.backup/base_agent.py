"""
Fixed version of the BaseAgent class that properly handles configuration.
"""

from typing import Union, Dict, Any

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