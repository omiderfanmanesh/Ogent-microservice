"""
Command agent implementation.

This module provides a command-focused agent that can execute system commands.
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.schema.runnable import Runnable

from app.core.agents.base_agent import BaseAgent, AgentResult
from app.core.entities.agent import Agent
from app.domain.repositories.execution_repository import ExecutionRepository
from app.infrastructure.adapters.command_client import CommandClient
from app.core.tools.command_tool import create_command_tool

# Configure logging
logger = logging.getLogger(__name__)


class CommandAgent(BaseAgent):
    """
    Command agent implementation.
    
    This agent specializes in executing and reasoning about system commands.
    """
    
    async def run(self, input_text: str) -> AgentResult:
        """
        Run the command agent with the given input.
        
        Args:
            input_text: The input text/query for the agent
            
        Returns:
            The result of the agent execution
            
        Raises:
            Exception: If an error occurs during execution
        """
        logger.info(f"Running command agent with input: {input_text[:100]}...")
        
        # Check command permissions
        if not self.command_config["execute_commands"]:
            return AgentResult(
                output="This agent is not configured to execute commands. Please enable command execution in agent permissions."
            )
        
        # Create callback
        callback, callback_manager = await self._create_callback(self.execution_id)
        
        # Create LLM
        llm = ChatOpenAI(
            model_name=self.llm_config["model_name"],
            temperature=self.llm_config["temperature"],
            max_tokens=self.llm_config["max_tokens"],
            streaming=self.llm_config["streaming"],
            openai_api_key=self.llm_config["openai_api_key"],
            callbacks=[callback_manager]
        )
        
        # Set up tools
        tools = self._create_tools()
        
        # Create the agent
        agent = initialize_agent(
            llm=llm,
            tools=tools,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=self.agent.configuration.max_iterations
        )
        
        # Get configuration
        config = self._get_runnable_config(callback_manager)
        
        try:
            # Run the agent
            response = await agent.ainvoke(
                {"input": input_text},
                config=config
            )
            
            # Get output
            output = response.get("output", "")
            tokens_used = callback.tokens_used
            
            logger.info(f"Agent run completed, tokens used: {tokens_used}")
            
            return AgentResult(
                output=output,
                tokens_used=tokens_used
            )
        except Exception as e:
            logger.error(f"Error running command agent: {str(e)}")
            raise
    
    def _create_tools(self) -> List[Runnable]:
        """
        Create the tools for the agent.
        
        Returns:
            List of tools for the agent to use
        """
        tools = []
        
        # Add command tool
        command_tool = create_command_tool(
            self.command_client,
            allowed_commands=self.command_config["allowed_commands"],
            allowed_paths=self.command_config["allowed_paths"],
            memory_limit=self.command_config["memory_limit"],
            network_access=self.command_config["network_access"]
        )
        tools.append(command_tool)
        
        # Add custom tools from configuration
        for tool_config in self.agent.configuration.tools:
            # TODO: Implement custom tool creation from config
            pass
        
        return tools 