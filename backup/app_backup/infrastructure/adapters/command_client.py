"""
Command client adapter.

This module provides a client for executing commands via an external service.
"""

import logging
import aiohttp
from typing import Dict, Any, Optional


class CommandClient:
    """
    Command client for executing commands via HTTP.
    
    This class is responsible for communicating with the command execution service.
    """
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize the command client.
        
        Args:
            base_url: Base URL of the command service
        """
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
        self.logger = logging.getLogger(__name__)
    
    async def close(self):
        """
        Close the HTTP session.
        """
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def execute_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """
        Execute a command.
        
        Args:
            command: Command to execute
            cwd: Working directory
            env: Environment variables
            timeout: Timeout in seconds
            
        Returns:
            Command execution result
        """
        try:
            url = f"{self.base_url}/api/v1/commands"
            payload = {
                "command": command,
                "cwd": cwd,
                "env": env,
                "timeout": timeout,
            }
            
            self.logger.info(f"Executing command: {command}")
            
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                
                self.logger.info(f"Command executed with status: {result.get('status')}")
                
                return result
        
        except aiohttp.ClientError as e:
            self.logger.error(f"Command execution error: {str(e)}")
            return {
                "status": "failed",
                "exit_code": 1,
                "stdout": "",
                "stderr": f"Command service error: {str(e)}",
                "duration_ms": 0,
            }
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                "status": "failed",
                "exit_code": 1,
                "stdout": "",
                "stderr": f"Internal error: {str(e)}",
                "duration_ms": 0,
            } 