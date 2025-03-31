"""
Domain entities.

This module provides the domain entities for the LangChain Agent Service.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class AgentPermissions:
    """
    Agent permissions.
    
    This class defines what operations an agent is allowed to perform.
    """
    
    def __init__(
        self,
        execute_commands: bool = False,
        allowed_commands: Optional[List[str]] = None,
        allowed_paths: Optional[List[str]] = None,
        memory_limit: Optional[int] = None,
        network_access: bool = False
    ):
        """
        Initialize agent permissions.
        
        Args:
            execute_commands: Whether the agent can execute commands
            allowed_commands: List of allowed commands (if None, all commands are allowed)
            allowed_paths: List of allowed filesystem paths (if None, no path restrictions)
            memory_limit: Memory limit in MB (if None, no memory limit)
            network_access: Whether the agent has network access
        """
        self.execute_commands = execute_commands
        self.allowed_commands = allowed_commands or []
        self.allowed_paths = allowed_paths or []
        self.memory_limit = memory_limit
        self.network_access = network_access
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert permissions to a dictionary.
        
        Returns:
            Dictionary representation of permissions
        """
        return {
            "execute_commands": self.execute_commands,
            "allowed_commands": self.allowed_commands,
            "allowed_paths": self.allowed_paths,
            "memory_limit": self.memory_limit,
            "network_access": self.network_access
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentPermissions":
        """
        Create permissions from a dictionary.
        
        Args:
            data: Dictionary representation of permissions
            
        Returns:
            Agent permissions instance
        """
        return cls(
            execute_commands=data.get("execute_commands", False),
            allowed_commands=data.get("allowed_commands", []),
            allowed_paths=data.get("allowed_paths", []),
            memory_limit=data.get("memory_limit"),
            network_access=data.get("network_access", False)
        )


class Agent:
    """
    Agent entity.
    
    This class represents an agent in the system.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        agent_type: str,
        config: Dict[str, Any],
        permissions: AgentPermissions,
        user_id: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize an agent.
        
        Args:
            name: Agent name
            description: Agent description
            agent_type: Type of the agent
            config: Agent configuration
            permissions: Agent permissions
            user_id: ID of the user who owns the agent
            id: Agent ID (generated if not provided)
            created_at: Creation timestamp (current time if not provided)
            updated_at: Update timestamp (current time if not provided)
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.agent_type = agent_type
        self.config = config
        self.permissions = permissions
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent to a dictionary.
        
        Returns:
            Dictionary representation of the agent
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_type": self.agent_type,
            "config": self.config,
            "permissions": self.permissions.to_dict(),
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """
        Create an agent from a dictionary.
        
        Args:
            data: Dictionary representation of an agent
            
        Returns:
            Agent instance
        """
        permissions = AgentPermissions.from_dict(data.get("permissions", {}))
        
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
            
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            agent_type=data.get("agent_type", ""),
            config=data.get("config", {}),
            permissions=permissions,
            user_id=data.get("user_id"),
            created_at=created_at,
            updated_at=updated_at
        )


class ExecutionStep:
    """
    Execution step entity.
    
    This class represents a step in an execution.
    """
    
    def __init__(
        self,
        execution_id: str,
        step_type: str,
        content: str,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize an execution step.
        
        Args:
            execution_id: ID of the execution this step belongs to
            step_type: Type of the step (thought, action, observation, etc.)
            content: Content of the step
            id: Step ID (generated if not provided)
            created_at: Creation timestamp (current time if not provided)
        """
        self.id = id or str(uuid.uuid4())
        self.execution_id = execution_id
        self.step_type = step_type
        self.content = content
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert execution step to a dictionary.
        
        Returns:
            Dictionary representation of the execution step
        """
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "step_type": self.step_type,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionStep":
        """
        Create an execution step from a dictionary.
        
        Args:
            data: Dictionary representation of an execution step
            
        Returns:
            Execution step instance
        """
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        return cls(
            id=data.get("id"),
            execution_id=data.get("execution_id", ""),
            step_type=data.get("step_type", ""),
            content=data.get("content", ""),
            created_at=created_at
        )


class Command:
    """
    Command entity.
    
    This class represents a command execution.
    """
    
    def __init__(
        self,
        execution_id: str,
        command: str,
        status: str,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        duration_ms: Optional[int] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a command.
        
        Args:
            execution_id: ID of the execution this command belongs to
            command: Command string
            status: Command status (running, completed, failed)
            exit_code: Command exit code
            stdout: Command standard output
            stderr: Command standard error
            duration_ms: Command duration in milliseconds
            id: Command ID (generated if not provided)
            created_at: Creation timestamp (current time if not provided)
            updated_at: Update timestamp (current time if not provided)
        """
        self.id = id or str(uuid.uuid4())
        self.execution_id = execution_id
        self.command = command
        self.status = status
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert command to a dictionary.
        
        Returns:
            Dictionary representation of the command
        """
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "command": self.command,
            "status": self.status,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Command":
        """
        Create a command from a dictionary.
        
        Args:
            data: Dictionary representation of a command
            
        Returns:
            Command instance
        """
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
            
        return cls(
            id=data.get("id"),
            execution_id=data.get("execution_id", ""),
            command=data.get("command", ""),
            status=data.get("status", ""),
            exit_code=data.get("exit_code"),
            stdout=data.get("stdout"),
            stderr=data.get("stderr"),
            duration_ms=data.get("duration_ms"),
            created_at=created_at,
            updated_at=updated_at
        )


class Execution:
    """
    Execution entity.
    
    This class represents an agent execution.
    """
    
    def __init__(
        self,
        agent_id: str,
        input: str,
        status: str = "pending",
        output: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        steps: Optional[List[ExecutionStep]] = None,
        commands: Optional[List[Command]] = None,
        user_id: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize an execution.
        
        Args:
            agent_id: ID of the agent
            input: Input for the execution
            status: Execution status (pending, running, completed, failed)
            output: Execution output
            error: Execution error
            metadata: Execution metadata
            steps: Execution steps
            commands: Executed commands
            user_id: ID of the user who started the execution
            id: Execution ID (generated if not provided)
            created_at: Creation timestamp (current time if not provided)
            updated_at: Update timestamp (current time if not provided)
        """
        self.id = id or str(uuid.uuid4())
        self.agent_id = agent_id
        self.input = input
        self.status = status
        self.output = output
        self.error = error
        self.metadata = metadata or {}
        self.steps = steps or []
        self.commands = commands or []
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert execution to a dictionary.
        
        Returns:
            Dictionary representation of the execution
        """
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "input": self.input,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
            "steps": [step.to_dict() for step in self.steps],
            "commands": [command.to_dict() for command in self.commands],
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Execution":
        """
        Create an execution from a dictionary.
        
        Args:
            data: Dictionary representation of an execution
            
        Returns:
            Execution instance
        """
        steps = []
        for step_data in data.get("steps", []):
            steps.append(ExecutionStep.from_dict(step_data))
            
        commands = []
        for command_data in data.get("commands", []):
            commands.append(Command.from_dict(command_data))
            
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
            
        return cls(
            id=data.get("id"),
            agent_id=data.get("agent_id", ""),
            input=data.get("input", ""),
            status=data.get("status", "pending"),
            output=data.get("output"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
            steps=steps,
            commands=commands,
            user_id=data.get("user_id"),
            created_at=created_at,
            updated_at=updated_at
        ) 