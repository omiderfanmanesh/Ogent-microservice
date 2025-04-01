#!/usr/bin/env python3
"""
Test script for creating agents directly with the LangChain agent service.
"""

import asyncio
import os
import json
import requests
from typing import Dict, Any
from uuid import UUID

# Base URL for the agent service API
BASE_URL = "http://localhost:8002/api/v1"
USER_ID = "test-user-123"  # Test user ID

async def create_test_agent() -> Dict[str, Any]:
    """Create a test agent using the REST API."""
    print("\n=== Creating test agent ===")
    
    # Agent configuration
    agent_data = {
        "name": "Test Conversational Agent",
        "agent_type": "conversational",
        "description": "A test agent for direct API tests",
        "configuration": {
            "model_name": "gpt-4o-mini",
            "temperature": 0.7,
            "system_message": "You are a helpful AI assistant. Be concise in your answers."
        },
        "permissions": {
            "execute_commands": False,
            "network_access": False
        },
        "metadata": {"test": True}
    }
    
    # Send POST request to create agent
    response = requests.post(
        f"{BASE_URL}/agents",
        json=agent_data,
        headers={"X-User-ID": USER_ID}
    )
    
    # Process response
    if response.status_code == 201:
        agent = response.json()
        print(f"Successfully created agent with ID: {agent['id']}")
        print(f"Agent name: {agent['name']}")
        print(f"Using model: {agent['configuration']['model_name']}")
        return agent
    else:
        print(f"Failed to create agent. Status code: {response.status_code}")
        print(f"Error: {response.text}")
        return None

async def execute_agent(agent_id: str) -> None:
    """Execute the agent with a simple question."""
    print("\n=== Executing agent ===")
    
    # Execution data
    execution_data = {
        "input": "Who are you and what can you do?",
        "metadata": {"test": True}
    }
    
    # Send POST request to execute agent
    response = requests.post(
        f"{BASE_URL}/agents/{agent_id}/execute",
        json=execution_data,
        headers={"X-User-ID": USER_ID}
    )
    
    # Process response
    if response.status_code == 200:
        execution = response.json()
        print(f"Execution started with ID: {execution['id']}")
        print(f"Status: {execution['status']}")
        
        # If execution is running, wait for completion
        if execution["status"] == "running":
            await wait_for_completion(agent_id, execution["id"])
        else:
            print(f"Output: {execution.get('output', 'No output available')}")
            print(f"Error: {execution.get('error', 'No errors')}")
    else:
        print(f"Failed to execute agent. Status code: {response.status_code}")
        print(f"Error: {response.text}")

async def wait_for_completion(agent_id: str, execution_id: str) -> None:
    """Wait for an execution to complete."""
    print("Waiting for execution to complete...")
    
    # Poll with timeout
    max_attempts = 15
    attempt = 0
    
    while attempt < max_attempts:
        # Get execution status
        response = requests.get(
            f"{BASE_URL}/agents/{agent_id}/executions/{execution_id}",
            headers={"X-User-ID": USER_ID}
        )
        
        if response.status_code == 200:
            status_data = response.json()
            status = status_data.get("status")
            
            if status in ["completed", "failed"]:
                print(f"Execution {status}!")
                print(f"Output: {status_data.get('output', 'No output available')}")
                print(f"Error: {status_data.get('error', 'No errors')}")
                break
        
        # Wait before next check
        await asyncio.sleep(2)
        attempt += 1
    else:
        print("Timeout waiting for execution to complete")

async def main():
    """Main entry point."""
    # Create an agent
    agent = await create_test_agent()
    
    if agent:
        agent_id = agent["id"]
        # Execute the agent
        await execute_agent(agent_id)
    else:
        print("Skipping execution since agent creation failed")

if __name__ == "__main__":
    asyncio.run(main()) 