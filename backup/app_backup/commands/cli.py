#!/usr/bin/env python
"""
Command-line interface for Ogent.

This script provides a command-line interface for working with agents.
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Load environment variables
load_dotenv()

# Constants
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

# Create console
console = Console()

async def get_token(username: str, password: str) -> Optional[str]:
    """
    Get an authentication token from the API.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/auth/token",
                data={"username": username, "password": password},
            )
            
            if response.status_code != 200:
                console.print(f"[red]Error: {response.json().get('detail', 'Authentication failed')}")
                return None
                
            return response.json().get("access_token")
    except Exception as e:
        console.print(f"[red]Error connecting to API: {e}")
        return None

async def list_agents(token: str) -> None:
    """
    List all agents.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/agents",
                headers={"Authorization": f"Bearer {token}"},
            )
            
            if response.status_code != 200:
                console.print(f"[red]Error: {response.json().get('detail', 'Failed to list agents')}")
                return
                
            agents = response.json()
            
            if not agents:
                console.print("[yellow]No agents found.")
                return
                
            console.print(Panel("[bold green]Available Agents", expand=False))
            
            for agent in agents:
                console.print(Panel(
                    f"[bold]{agent['name']}[/bold] ({agent['id']})\n"
                    f"[italic]{agent['description']}[/italic]\n"
                    f"Type: {agent['agent_type']}\n"
                    f"Created: {agent['created_at'][:10]}",
                    title=f"Agent {agent['id'][:8]}",
                    expand=False
                ))
    except Exception as e:
        console.print(f"[red]Error connecting to API: {e}")

async def create_agent(token: str, name: str, description: str, 
                       agent_type: str, model_name: str) -> None:
    """
    Create a new agent.
    """
    try:
        agent_data = {
            "name": name,
            "description": description,
            "agent_type": agent_type,
            "config": {
                "model_name": model_name,
                "temperature": 0.7,
                "max_tokens": 1000,
                "streaming": True
            },
            "permissions": {
                "can_execute_commands": agent_type == "command",
                "allowed_commands": ["ls", "cat", "echo", "pwd"] if agent_type == "command" else [],
                "allowed_paths": ["/tmp"] if agent_type == "command" else [],
                "network_access": False,
                "memory_limit_mb": 500
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/agents",
                headers={"Authorization": f"Bearer {token}"},
                json=agent_data
            )
            
            if response.status_code != 201:
                console.print(f"[red]Error: {response.json().get('detail', 'Failed to create agent')}")
                return
                
            agent = response.json()
            console.print(f"[green]Agent created successfully with ID: {agent['id']}")
    except Exception as e:
        console.print(f"[red]Error connecting to API: {e}")

async def execute_agent(token: str, agent_id: str, input_text: str, stream: bool) -> None:
    """
    Execute an agent with input text.
    """
    try:
        execution_data = {
            "input": input_text,
            "stream": stream,
            "metadata": {}
        }
        
        if not stream:
            # Non-streaming execution
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_URL}/agents/{agent_id}/execute",
                    headers={"Authorization": f"Bearer {token}"},
                    json=execution_data
                )
                
                if response.status_code != 200:
                    console.print(f"[red]Error: {response.json().get('detail', 'Failed to execute agent')}")
                    return
                    
                execution = response.json()
                console.print(Panel(
                    Markdown(execution["output"]),
                    title="Agent Response",
                    expand=False
                ))
        else:
            # Streaming execution via WebSocket
            import websockets
            
            console.print("[yellow]Connecting to WebSocket for streaming...[/yellow]")
            
            try:
                async with websockets.connect(
                    f"ws://{API_URL.replace('http://', '')}/executions/{agent_id}/stream?token={token}"
                ) as websocket:
                    # Send initial execution request
                    await websocket.send(json.dumps(execution_data))
                    
                    console.print("[bold]Agent is thinking...[/bold]")
                    
                    current_completion = ""
                    
                    while True:
                        data = await websocket.recv()
                        event = json.loads(data)
                        
                        event_type = event.get("type")
                        
                        if event_type == "status":
                            if event.get("status") != "running":
                                console.print(f"[yellow]Status: {event.get('status')}[/yellow]")
                                
                        elif event_type == "completion":
                            content = event.get("content", "")
                            current_completion += content
                            console.print(content, end="")
                            
                        elif event_type == "step":
                            step_content = event.get("content", "")
                            console.print(f"\n[dim]{step_content}[/dim]")
                            
                        elif event_type == "command":
                            cmd = event.get("command", "")
                            status = event.get("status", "")
                            console.print(f"\n[blue]Command: {cmd} ({status})[/blue]")
                            
                            if "output" in event:
                                console.print(f"[dim]{event.get('output')}[/dim]")
                                
                        elif event_type == "error":
                            console.print(f"\n[red]Error: {event.get('message')}[/red]")
                            break
                            
                        elif event_type == "end":
                            break
                    
                    console.print("\n[green]Execution completed[/green]")
                    
            except websockets.exceptions.ConnectionClosed:
                console.print("[red]WebSocket connection closed unexpectedly[/red]")
            except Exception as e:
                console.print(f"[red]Error during streaming: {e}[/red]")
                
    except Exception as e:
        console.print(f"[red]Error connecting to API: {e}")

async def main():
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(description="Ogent Command-line Interface")
    
    # Authentication arguments
    parser.add_argument("--username", help="Username for authentication")
    parser.add_argument("--password", help="Password for authentication")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List agents command
    list_parser = subparsers.add_parser("list", help="List all agents")
    
    # Create agent command
    create_parser = subparsers.add_parser("create", help="Create a new agent")
    create_parser.add_argument("--name", required=True, help="Name of the agent")
    create_parser.add_argument("--description", required=True, help="Description of the agent")
    create_parser.add_argument("--type", required=True, choices=["conversational", "command"], 
                              help="Type of agent")
    create_parser.add_argument("--model", default="gpt-4o", 
                              help="Model name (default: gpt-4o)")
    
    # Execute agent command
    execute_parser = subparsers.add_parser("execute", help="Execute an agent")
    execute_parser.add_argument("--agent-id", required=True, help="ID of the agent to execute")
    execute_parser.add_argument("--input", required=True, help="Input text for the agent")
    execute_parser.add_argument("--stream", action="store_true", help="Stream results via WebSocket")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Get username and password if not provided
    username = args.username or Prompt.ask("Username", default="admin")
    password = args.password or Prompt.ask("Password", password=True)
    
    # Get token
    token = await get_token(username, password)
    
    if not token:
        return
    
    # Execute command
    if args.command == "list":
        await list_agents(token)
    elif args.command == "create":
        await create_agent(token, args.name, args.description, args.type, args.model)
    elif args.command == "execute":
        await execute_agent(token, args.agent_id, args.input, args.stream)
    
if __name__ == "__main__":
    asyncio.run(main()) 