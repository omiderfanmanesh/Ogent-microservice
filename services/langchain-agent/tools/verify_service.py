#!/usr/bin/env python3
"""
Verification script for the agent service.
Tests basic functionality and agent creation.
"""
import requests
import json
import sys
import os
import socket

# Configure the base URL based on our environment
hostname = socket.gethostname()
if hostname == '43227b73abbf' or hostname.startswith('ogent-agent-service'):
    # Inside Docker container, use internal service port
    BASE_URL = "http://localhost:8000/api"
    print(f"Running inside container {hostname}")
else:
    # From host machine, use mapped port
    BASE_URL = "http://localhost:8002/api"
    print(f"Running on host machine {hostname}")

print(f"Using API base URL: {BASE_URL}")

def check_health():
    """Check if the service is healthy."""
    print("\n[ Testing Health Endpoint ]")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print(f"✅ Health check passed: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def check_info():
    """Check if the service info is available."""
    print("\n[ Testing Info Endpoint ]")
    try:
        response = requests.get(f"{BASE_URL}/info")
        response.raise_for_status()
        print(f"✅ Info check passed: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Info check failed: {str(e)}")
        return False

def test_agent_creation():
    """Test creating an agent."""
    print("\n[ Testing Agent Creation ]")
    try:
        payload = {
            "user_id": "test-user",
            "agent_type": "conversational",
            "configuration": {
                "model_name": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 1000,
                "system_message": "You are a helpful assistant.",
                "streaming": False,
                "max_iterations": 10
            },
            "permissions": {
                "execute_commands": False,
                "network_access": False
            }
        }
        
        print(f"Request payload: {json.dumps(payload, indent=2)}")
        response = requests.post(f"{BASE_URL}/agents", json=payload)
        response.raise_for_status()
        
        print(f"✅ Agent creation successful: {response.json()}")
        return True
    except Exception as e:
        if hasattr(e, 'response') and e.response:
            print(f"❌ Agent creation failed: {e.response.status_code} - {e.response.text}")
        else:
            print(f"❌ Agent creation failed: {str(e)}")
        return False

def test_agent_query():
    """Test querying an agent."""
    print("\n[ Testing Agent Query ]")
    try:
        # Create agent first
        payload = {
            "user_id": "test-user",
            "agent_type": "conversational",
            "configuration": {
                "model_name": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 1000,
                "system_message": "You are a helpful assistant.",
                "streaming": False,
                "max_iterations": 10
            },
            "permissions": {
                "execute_commands": False,
                "network_access": False
            }
        }
        
        create_response = requests.post(f"{BASE_URL}/agents", json=payload)
        create_response.raise_for_status()
        agent_id = create_response.json()["id"]
        
        # Now query the agent
        query_payload = {
            "question": "Who are you?"
        }
        
        response = requests.post(f"{BASE_URL}/agents/{agent_id}/query", json=query_payload)
        response.raise_for_status()
        
        print(f"✅ Agent query successful: {response.json()}")
        return True
    except Exception as e:
        if hasattr(e, 'response') and e.response:
            print(f"❌ Agent query failed: {e.response.status_code} - {e.response.text}")
        else:
            print(f"❌ Agent query failed: {str(e)}")
        return False

def main():
    """Run all tests and report results."""
    print("🔍 Verifying agent service...")
    
    health_ok = check_health()
    info_ok = check_info()
    creation_ok = test_agent_creation()
    
    if health_ok and info_ok and creation_ok:
        query_ok = test_agent_query()
    else:
        query_ok = False
        print("\n[ Skipping Agent Query Test ]")
        print("Skipping query test since basic functionality failed.")
    
    print("\n📊 Test Results Summary:")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Info Check: {'✅ PASS' if info_ok else '❌ FAIL'}")
    print(f"Agent Creation: {'✅ PASS' if creation_ok else '❌ FAIL'}")
    print(f"Agent Query: {'✅ PASS' if query_ok else '❌ FAIL' if not health_ok or not info_ok or not creation_ok else '⚠️ SKIPPED'}")
    
    all_passed = health_ok and info_ok and creation_ok and query_ok
    
    if all_passed:
        print("\n✅ All tests passed! The agent service is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 