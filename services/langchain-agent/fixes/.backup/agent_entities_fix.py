"""
Fixed version of the agent entity classes with from_dict method.
"""

from typing import List, Optional

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