"""
Conversational agent.

This module provides a conversational agent implementation using LangChain.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AgentAction, AgentFinish, AIMessage, HumanMessage
from langchain.schema.runnable import RunnableConfig
from langchain.callbacks.base import BaseCallbackHandler
from langchain.tools.base import BaseTool

from app.core.agents.base_agent import BaseAgent, AgentCallback
from app.core.agents.agent_result import AgentResult
from app.core.tools.command_tool import CommandTool

# Configure logging
logger = logging.getLogger(__name__)


class AgentCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler.
    
    This handler captures events from LangChain and forwards them to our callback.
    """
    
    def __init__(self, callback: Optional[AgentCallback] = None):
        """
        Initialize the handler.
        
        Args:
            callback: Agent callback
        """
        self.callback = callback
    
    async def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """
        Handle agent action.
        
        Args:
            action: LangChain agent action
            **kwargs: Additional arguments
        """
        if self.callback:
            await self.callback.on_step(
                step_type="action",
                content=f"{action.tool}: {action.tool_input}",
                metadata={"tool": action.tool, "input": action.tool_input}
            )
    
    async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """
        Handle agent finish.
        
        Args:
            finish: LangChain agent finish
            **kwargs: Additional arguments
        """
        if self.callback:
            await self.callback.on_step(
                step_type="final_answer",
                content=finish.return_values.get("output", ""),
                metadata=finish.return_values
            )
    
    async def on_tool_start(
        self, 
        serialized: Dict[str, Any], 
        input_str: str, 
        **kwargs: Any
    ) -> None:
        """
        Handle tool start.
        
        Args:
            serialized: Serialized tool
            input_str: Tool input
            **kwargs: Additional arguments
        """
        tool_name = serialized.get("name", "unknown_tool")
        if tool_name == "execute_command" and self.callback:
            await self.callback.on_command(
                command=input_str,
                status="running",
                metadata={"tool": tool_name}
            )
    
    async def on_tool_end(
        self,
        output: str,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Handle tool end.
        
        Args:
            output: Tool output
            observation_prefix: Observation prefix
            llm_prefix: LLM prefix
            **kwargs: Additional arguments
        """
        if self.callback:
            await self.callback.on_step(
                step_type="observation",
                content=output
            )
    
    async def on_tool_error(
        self, 
        error: Exception, 
        **kwargs: Any
    ) -> None:
        """
        Handle tool error.
        
        Args:
            error: Exception
            **kwargs: Additional arguments
        """
        if self.callback:
            await self.callback.on_step(
                step_type="observation",
                content=f"Error: {str(error)}"
            )
    
    async def on_chat_model_start(
        self, 
        serialized: Dict[str, Any], 
        messages: List[List[Dict[str, Any]]], 
        **kwargs: Any
    ) -> None:
        """
        Handle chat model start.
        
        Args:
            serialized: Serialized model
            messages: Messages
            **kwargs: Additional arguments
        """
        pass
    
    async def on_text(self, text: str, **kwargs: Any) -> None:
        """
        Handle text.
        
        Args:
            text: Text
            **kwargs: Additional arguments
        """
        if self.callback and text.strip():
            await self.callback.on_step(
                step_type="thought",
                content=text
            )


class ConversationalAgent(BaseAgent):
    """
    Conversational agent.
    
    This agent uses LangChain and LLMs to have conversations and perform actions.
    """
    
    async def run(
        self,
        input: str,
        callback: Optional[AgentCallback] = None,
    ) -> AgentResult:
        """
        Run the agent.
        
        Args:
            input: User input
            callback: Optional callback for execution events
            
        Returns:
            Agent result
        """
        # Record start time
        start_time = time.time()
        
        try:
            # Set up tools
            tools = self._create_tools()
            
            # Create LLM
            llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=self.streaming
            )
            
            # Create system message
            system_message = self.system_message or (
                "You are a helpful AI assistant that can have conversations and execute commands. "
                "When a user asks you to perform an action, use the appropriate tool."
            )
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create agent
            agent = create_openai_tools_agent(llm, tools, prompt)
            
            # Create agent executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                max_iterations=self.max_iterations,
                handle_parsing_errors=True,
            )
            
            # Create callback handler
            handler = AgentCallbackHandler(callback)
            
            # Set up config for streaming
            config = RunnableConfig(
                callbacks=[handler],
            )
            
            # Initialize chat history
            chat_history = []
            
            # Execute agent
            result = await agent_executor.ainvoke(
                {"input": input, "chat_history": chat_history},
                config=config
            )
            
            # Add AI message to chat history
            chat_history.append(HumanMessage(content=input))
            chat_history.append(AIMessage(content=result["output"]))
            
            # Calculate tokens
            tokens_used = None  # Would need to get from LLM response
            
            # Create result
            return AgentResult(
                output=result["output"],
                tokens_used=tokens_used,
                metadata={
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "iterations": result.get("intermediate_steps", [])
                }
            )
        
        except Exception as e:
            logger.error(f"Error running conversational agent: {str(e)}", exc_info=True)
            
            # Create error result
            return AgentResult(
                output="I encountered an error while processing your request.",
                error=str(e),
                metadata={
                    "duration_ms": int((time.time() - start_time) * 1000),
                }
            )
    
    def _create_tools(self) -> List[BaseTool]:
        """
        Create tools for the agent.
        
        Returns:
            List of tools
        """
        tools = []
        
        # Add command tool if allowed
        if self.permissions.execute_commands:
            command_tool = CommandTool(
                command_client=self.command_client,
                allowed_commands=self.permissions.allowed_commands,
                allowed_paths=self.permissions.allowed_paths,
                memory_limit=self.permissions.memory_limit,
                network_access=self.permissions.network_access
            )
            tools.append(command_tool)
        
        # Add more tools as needed...
        
        return tools 