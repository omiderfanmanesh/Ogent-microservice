"""
Client for interacting with the Command Execution Service.
"""

import json
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from aiohttp import ClientSession

from app.core.config import settings

logger = logging.getLogger(__name__)


class CommandClient:
    """
    Client for executing commands via the Command Execution Service.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the command client.
        
        Args:
            base_url: Optional base URL for the Command Execution Service.
                     If not provided, will use settings.
        """
        self.base_url = base_url or settings.COMMAND_SERVICE_URL
        self._session: Optional[ClientSession] = None
    
    async def _get_session(self) -> ClientSession:
        """
        Get an HTTP session, creating one if needed.
        
        Returns:
            aiohttp ClientSession
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Content-Type": "application/json"}
            )
        return self._session
    
    async def close(self) -> None:
        """
        Close the HTTP session.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def execute_command(
        self,
        command: str,
        timeout: int = 60,
        allowed_paths: Optional[List[str]] = None,
        memory_limit: Optional[int] = None,
        network_access: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a command via the Command Execution Service.
        
        Args:
            command: The command to execute.
            timeout: Maximum execution time in seconds.
            allowed_paths: List of file system paths the command can access.
            memory_limit: Memory limit in MB.
            network_access: Whether the command has network access.
            
        Returns:
            Command execution result with stdout, stderr, exit_code, etc.
            
        Raises:
            Exception: If the command execution fails.
        """
        session = await self._get_session()
        
        # Prepare request payload
        payload = {
            "command": command,
            "timeout": timeout,
            "network_access": network_access
        }
        
        if allowed_paths:
            payload["allowed_paths"] = allowed_paths
        
        if memory_limit:
            payload["memory_limit"] = memory_limit
        
        # Send request to Command Execution Service
        try:
            async with session.post(
                f"{self.base_url}/api/commands/execute",
                json=payload
            ) as response:
                # Check for successful response
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Command execution failed: {error_text}")
                    raise Exception(f"Command execution failed with status {response.status}: {error_text}")
                
                # Parse response
                result = await response.json()
                return result
        except aiohttp.ClientError as e:
            logger.error(f"Error connecting to Command Execution Service: {str(e)}")
            raise Exception(f"Error connecting to Command Execution Service: {str(e)}")
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get the status of a command execution.
        
        Args:
            execution_id: ID of the command execution.
            
        Returns:
            Execution status.
            
        Raises:
            Exception: If the request fails.
        """
        session = await self._get_session()
        
        try:
            async with session.get(
                f"{self.base_url}/api/commands/{execution_id}"
            ) as response:
                # Check for successful response
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Get execution status failed: {error_text}")
                    raise Exception(f"Get execution status failed with status {response.status}: {error_text}")
                
                # Parse response
                result = await response.json()
                return result
        except aiohttp.ClientError as e:
            logger.error(f"Error connecting to Command Execution Service: {str(e)}")
            raise Exception(f"Error connecting to Command Execution Service: {str(e)}")
    
    async def cancel_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Cancel a command execution.
        
        Args:
            execution_id: ID of the command execution to cancel.
            
        Returns:
            Cancellation result.
            
        Raises:
            Exception: If the cancellation fails.
        """
        session = await self._get_session()
        
        try:
            async with session.post(
                f"{self.base_url}/api/commands/{execution_id}/cancel"
            ) as response:
                # Check for successful response
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Cancel execution failed: {error_text}")
                    raise Exception(f"Cancel execution failed with status {response.status}: {error_text}")
                
                # Parse response
                result = await response.json()
                return result
        except aiohttp.ClientError as e:
            logger.error(f"Error connecting to Command Execution Service: {str(e)}")
            raise Exception(f"Error connecting to Command Execution Service: {str(e)}")
    
    async def get_allowed_commands(self) -> List[str]:
        """
        Get the list of allowed commands from the Command Execution Service.
        
        Returns:
            List of allowed command patterns.
            
        Raises:
            Exception: If the request fails.
        """
        session = await self._get_session()
        
        try:
            async with session.get(
                f"{self.base_url}/api/commands/allowed"
            ) as response:
                # Check for successful response
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Get allowed commands failed: {error_text}")
                    raise Exception(f"Get allowed commands failed with status {response.status}: {error_text}")
                
                # Parse response
                result = await response.json()
                return result.get("allowed_commands", [])
        except aiohttp.ClientError as e:
            logger.error(f"Error connecting to Command Execution Service: {str(e)}")
            raise Exception(f"Error connecting to Command Execution Service: {str(e)}")
    
    async def validate_command(self, command: str) -> Dict[str, Any]:
        """
        Validate a command without executing it.
        
        Args:
            command: The command to validate.
            
        Returns:
            Validation result with is_valid and reason fields.
            
        Raises:
            Exception: If the validation request fails.
        """
        session = await self._get_session()
        
        try:
            async with session.post(
                f"{self.base_url}/api/commands/validate",
                json={"command": command}
            ) as response:
                # Check for successful response
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Command validation failed: {error_text}")
                    raise Exception(f"Command validation failed with status {response.status}: {error_text}")
                
                # Parse response
                result = await response.json()
                return result
        except aiohttp.ClientError as e:
            logger.error(f"Error connecting to Command Execution Service: {str(e)}")
            raise Exception(f"Error connecting to Command Execution Service: {str(e)}")
