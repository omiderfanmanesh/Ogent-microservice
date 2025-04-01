#!/usr/bin/env python
"""
Script to test the agent API.

This script tests the agent API endpoints.
"""

import uuid
import json
import socket
import logging
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Determine if we're running inside a container
def is_running_in_container():
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return any('docker' in line for line in f)
    except:
        return False

# Configure the base URL based on environment
BASE_URL = "http://localhost:8000" if is_running_in_container() else "http://localhost:8002"
print(f"Using base URL: {BASE_URL}")

def test_agent_creation():
    """Test agent creation API endpoint."""
    # Generate a unique user ID for testing
    user_id = f"test-user-{uuid.uuid4().hex[:8]}"
    
    print(f"\nTesting agent creation with user ID: {user_id}")
    
    # Construct the agent data
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:6]}",
        "type": "conversational",
        "description": "A test agent created by the verification script",
        "user_id": user_id,
        "configuration": {
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "system_message": "You are a helpful assistant for testing.",
            "max_iterations": 10
        },
        "permissions": {
            "network_access": False,
            "allowed_commands": [],
            "allowed_paths": []
        },
        "metadata": {
            "test": True,
            "source": "verification_script"
        }
    }
    
    # Print request details
    endpoint = f"{BASE_URL}/api/v1/agents"
    print(f"Sending request to {endpoint}")
    print(f"Request payload: {json.dumps(agent_data, indent=2)}")
    
    try:
        # Send the request
        response = requests.post(endpoint, json=agent_data)
        
        # Print response details
        print(f"Response status code: {response.status_code}")
        
        # Pretty print the response if it's JSON
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response: {response.text}")
        
        # Check if the request was successful
        if response.status_code == 201:
            print("✅ Agent creation successful!")
            return True
        else:
            print("❌ Agent creation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent creation: {str(e)}")
        return False


def main():
    """Main function."""
    print("Testing Agent API Endpoints")
    print("=========================\n")
    
    # Test agent creation
    if test_agent_creation():
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n👎 Some tests failed!")
        return False
    

if __name__ == "__main__":
    main()
