#!/usr/bin/env python3
import requests
import json
import sys

def test_socket_service():
    """Test the socket service API endpoints"""
    api_gateway_url = "http://localhost:8081"
    
    print("Testing Socket Service API...")
    
    # Test health endpoint
    print("\n1. Testing health endpoint:")
    try:
        response = requests.get(f"{api_gateway_url}/socket-http/health")
        print(f"✅ Health check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test start-execution endpoint without authentication (expect failure)
    print("\n2. Testing start-execution endpoint (without auth - should fail):")
    try:
        execution_data = {
            "executionId": "test-execution-123",
            "agent": "test-agent",
            "input": "test command",
            "userId": "test-user-123"
        }
        response = requests.post(
            f"{api_gateway_url}/socket-http/api/start-execution", 
            json=execution_data
        )
        print(f"Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Start execution test failed: {e}")
    
    # Test execution-status endpoint
    print("\n3. Testing execution-status endpoint:")
    try:
        status_data = {
            "executionId": "test-execution-123",
            "status": "running",
            "progress": 50,
            "output": "Test output"
        }
        response = requests.post(
            f"{api_gateway_url}/socket-http/api/execution-status", 
            json=status_data
        )
        print(f"Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Execution status test failed: {e}")
    
    print("\nTests completed.")

if __name__ == "__main__":
    test_socket_service() 