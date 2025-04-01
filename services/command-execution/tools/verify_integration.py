#!/usr/bin/env python3
"""
Command Execution Service Integration Verification Tool

This script verifies the integration between the Command Execution Service and the Agent Service by:
1. Setting up a test environment
2. Testing command execution from an agent
3. Verifying the results are correctly passed back to the agent

Usage:
    python verify_integration.py

Requirements:
    requests
"""

import requests
import time
import json
import sys
import os
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
COMMAND_SERVICE_URL = os.getenv("COMMAND_SERVICE_URL", "http://localhost:5001")
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://localhost:8002")

if not COMMAND_SERVICE_URL.startswith("http"):
    COMMAND_SERVICE_URL = f"http://{COMMAND_SERVICE_URL}"
if not AGENT_SERVICE_URL.startswith("http"):
    AGENT_SERVICE_URL = f"http://{AGENT_SERVICE_URL}"

def check_services_health():
    """Check if both the command execution service and agent service are healthy"""
    logger.info("Checking services health...")
    
    # Check command service
    try:
        response = requests.get(f"{COMMAND_SERVICE_URL}/health", timeout=5)
        if response.status_code != 200:
            logger.error(f"Command service health check failed with status code: {response.status_code}")
            return False
        else:
            logger.info("Command service health check successful ✅")
    except requests.RequestException as e:
        logger.error(f"Command service health check failed with error: {str(e)}")
        return False
    
    # Check agent service
    try:
        response = requests.get(f"{AGENT_SERVICE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            logger.error(f"Agent service health check failed with status code: {response.status_code}")
            return False
        else:
            logger.info("Agent service health check successful ✅")
    except requests.RequestException as e:
        logger.error(f"Agent service health check failed with error: {str(e)}")
        return False
    
    return True

def create_command_agent():
    """Create a command agent that can execute system commands"""
    logger.info("Creating command agent...")
    
    agent_id = f"test-cmd-agent-{uuid.uuid4().hex[:8]}"
    
    try:
        payload = {
            "name": f"Test Command Agent {agent_id}",
            "agent_type": "command",
            "description": "A test agent for command execution",
            "user_id": "test-user-1",
            "configuration": {
                "model_name": "gpt-4o-mini",
                "temperature": 0.7,
                "system_message": "You are a helpful assistant that can run system commands.",
                "max_iterations": 5
            },
            "permissions": {
                "execute_commands": True,
                "network_access": True
            },
            "metadata": {
                "test": True,
                "source": "verification_script"
            }
        }
        
        response = requests.post(f"{AGENT_SERVICE_URL}/api/agents", json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            data = response.json()
            agent_id = data.get("id", agent_id)
            logger.info(f"Command agent created successfully with ID: {agent_id} ✅")
            return agent_id
        else:
            logger.error(f"Failed to create command agent. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except requests.RequestException as e:
        logger.error(f"Command agent creation failed with error: {str(e)}")
        return None

def test_agent_command_execution(agent_id):
    """Test executing a command through the agent"""
    logger.info(f"Testing command execution through agent {agent_id}...")
    
    try:
        # Simple command to execute
        prompt = "Run the command 'echo Hello from command agent' and show me the result"
        
        payload = {
            "prompt": prompt,
            "max_tokens": 1000
        }
        
        response = requests.post(
            f"{AGENT_SERVICE_URL}/api/agents/{agent_id}/execute", 
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            output = data.get("output", "")
            
            # Check if the output contains the expected result
            if "Hello from command agent" in output:
                logger.info("Agent successfully executed the command ✅")
                logger.info(f"Agent response: {output}")
                return True
            else:
                logger.error("Agent execution did not contain expected output")
                logger.error(f"Agent response: {output}")
                return False
        else:
            logger.error(f"Agent execution failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        logger.error(f"Agent execution request failed with error: {str(e)}")
        return False

def test_complex_agent_command(agent_id):
    """Test executing a more complex command through the agent"""
    logger.info(f"Testing complex command execution through agent {agent_id}...")
    
    try:
        # More complex command with piping
        prompt = "Run a command to list files in the current directory, sorted by size, and show me only the top 3 largest files"
        
        payload = {
            "prompt": prompt,
            "max_tokens": 1000
        }
        
        response = requests.post(
            f"{AGENT_SERVICE_URL}/api/agents/{agent_id}/execute", 
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            output = data.get("output", "")
            
            # We just check if the agent executed something and returned output
            # The exact output will depend on the directory contents
            if len(output) > 0 and ("file" in output.lower() or "directory" in output.lower()):
                logger.info("Agent successfully executed the complex command ✅")
                logger.info(f"Agent response: {output}")
                return True
            else:
                logger.error("Agent execution did not produce meaningful output")
                logger.error(f"Agent response: {output}")
                return False
        else:
            logger.error(f"Complex agent execution failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        logger.error(f"Complex agent execution request failed with error: {str(e)}")
        return False

def main():
    """Main function to run integration verification tests"""
    logger.info("Starting Command Execution Service integration verification...")
    logger.info(f"Command Service URL: {COMMAND_SERVICE_URL}")
    logger.info(f"Agent Service URL: {AGENT_SERVICE_URL}")
    
    # Test results
    results = {
        "services_health": False,
        "agent_creation": False,
        "simple_command_execution": False,
        "complex_command_execution": False
    }
    
    # Run tests
    results["services_health"] = check_services_health()
    
    if results["services_health"]:
        agent_id = create_command_agent()
        if agent_id:
            results["agent_creation"] = True
            results["simple_command_execution"] = test_agent_command_execution(agent_id)
            results["complex_command_execution"] = test_complex_agent_command(agent_id)
    
    # Print summary
    logger.info("\n=========== Integration Verification Summary ===========")
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Return overall success/failure
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 