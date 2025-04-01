#!/usr/bin/env python3
import requests
import json
import time
import uuid
import sys
import getpass

def test_authenticated_socket():
    """Test Socket Service with authentication"""
    api_gateway_url = "http://localhost:8081"
    
    print("===== Testing Socket Service with Authentication =====")
    
    # Step 1: Login to get authentication token
    print("\n1. Getting authentication token...")
    
    # Ask for credentials
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    
    try:
        auth_response = requests.post(
            f"{api_gateway_url}/auth/login", 
            json={"email": email, "password": password},
            timeout=10
        )
        
        print(f"Auth status code: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            token = auth_data.get('token', '')
            
            if not token:
                print("Authentication failed: No token returned")
                return
                
            print("Authentication successful!")
            
            # Print user info
            user = auth_data.get('user', {})
            print(f"Logged in as: {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
            
            # Get user ID for socket room
            user_id = user.get('id', 'unknown')
        else:
            print(f"Authentication failed: {auth_response.text}")
            return
    except Exception as e:
        print(f"Error during authentication: {e}")
        return
    
    # Step 2: Test socket service API with the token
    print("\n2. Testing Socket Service API with authentication...")
    
    # Generate unique execution ID
    execution_id = str(uuid.uuid4())
    
    # Test start-execution endpoint with authentication
    start_payload = {
        "executionId": execution_id,
        "agent": "authenticated-test-agent",
        "input": "Test command with authentication",
        "userId": user_id
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        start_response = requests.post(
            f"{api_gateway_url}/socket-http/api/start-execution", 
            json=start_payload,
            headers=headers,
            timeout=5
        )
        
        print(f"Start execution status code: {start_response.status_code}")
        print(f"Start execution response: {start_response.text}")
    except Exception as e:
        print(f"Error starting execution: {e}")
    
    # Step 3: Send status updates
    print("\n3. Sending status updates for the execution...")
    
    statuses = [
        {"status": "running", "progress": 33, "output": "Starting execution with authentication..."},
        {"status": "running", "progress": 66, "output": "Processing with authenticated user..."},
        {"status": "completed", "progress": 100, "output": "Authenticated execution completed!"}
    ]
    
    for i, status in enumerate(statuses):
        status_payload = {
            "executionId": execution_id,
            **status
        }
        
        try:
            status_response = requests.post(
                f"{api_gateway_url}/socket-http/api/execution-status", 
                json=status_payload,
                headers=headers,
                timeout=5
            )
            
            print(f"Status update {i+1}/{len(statuses)} - Status code: {status_response.status_code}")
            print(f"Response: {status_response.text}")
            
            if i < len(statuses) - 1:
                print("Waiting 2 seconds before next update...")
                time.sleep(2)
        except Exception as e:
            print(f"Error sending status update: {e}")
    
    print("\nAuthentication test complete. Check WebSocket client for updates.")

if __name__ == "__main__":
    test_authenticated_socket() 