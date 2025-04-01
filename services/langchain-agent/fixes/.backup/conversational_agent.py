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
