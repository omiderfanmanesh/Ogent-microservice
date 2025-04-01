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
