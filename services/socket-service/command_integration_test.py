#!/usr/bin/env python3
import requests
import json
import time
import uuid
import sys

def test_command_socket_integration():
    """Test integration between Command Execution and Socket services"""
    api_gateway_url = "http://localhost:8081"
    command_service_url = "http://localhost:5001"  # Direct to command service
    
    # Generate test data
    execution_id = str(uuid.uuid4())
    user_id = "test-user-123"
    command = "echo 'Hello from socket integration test'"
    
    print(f"===== Testing Command Service + Socket Service Integration =====")
    print(f"Execution ID: {execution_id}")
    print(f"User ID: {user_id}")
    print(f"Command: {command}")
    
    # Step 1: Notify Socket Service about new execution
    print("\n1. Notifying Socket Service about new execution...")
    socket_payload = {
        "executionId": execution_id,
        "agent": "test-agent",
        "input": command,
        "userId": user_id
    }
    
    try:
        socket_response = requests.post(
            f"{api_gateway_url}/socket-http/api/start-execution", 
            json=socket_payload,
            timeout=5
        )
        print(f"Socket notification status code: {socket_response.status_code}")
        print(f"Socket notification response: {socket_response.text}")
    except Exception as e:
        print(f"Error notifying Socket Service: {e}")
    
    # Step 2: Schedule command execution
    print("\n2. Scheduling command execution...")
    command_payload = {
        "command": command,
        "executionId": execution_id
    }
    
    try:
        command_response = requests.post(
            f"{command_service_url}/api/commands", 
            json=command_payload,
            timeout=5
        )
        print(f"Command scheduling status code: {command_response.status_code}")
        if command_response.status_code == 200:
            print(f"Command scheduling response: {command_response.text}")
        else:
            print(f"Error in command scheduling: {command_response.text}")
            return
    except Exception as e:
        print(f"Error scheduling command: {e}")
        return
    
    # Step 3: Poll execution status
    print("\n3. Polling execution status...")
    max_polls = 10
    poll_interval = 1
    
    for i in range(max_polls):
        try:
            status_response = requests.get(
                f"{command_service_url}/api/commands/{execution_id}", 
                timeout=5
            )
            print(f"Poll {i+1}/{max_polls} - Status code: {status_response.status_code}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Execution status: {status_data.get('status', 'unknown')}")
                print(f"Progress: {status_data.get('progress', 0)}%")
                
                # If execution is complete, break out of polling loop
                if status_data.get('status') in ['completed', 'failed', 'cancelled']:
                    print(f"Execution completed with status: {status_data.get('status')}")
                    break
            else:
                print(f"Error checking status: {status_response.text}")
                
        except Exception as e:
            print(f"Error polling status: {e}")
        
        print(f"Waiting {poll_interval} seconds before next poll...")
        time.sleep(poll_interval)
    
    # Step 4: Send final status update to Socket Service
    print("\n4. Sending final status to Socket Service...")
    final_status = {
        "executionId": execution_id,
        "status": "completed",
        "progress": 100,
        "output": f"Command '{command}' executed successfully."
    }
    
    try:
        final_update = requests.post(
            f"{api_gateway_url}/socket-http/api/execution-status", 
            json=final_status,
            timeout=5
        )
        print(f"Final update status code: {final_update.status_code}")
        print(f"Final update response: {final_update.text}")
    except Exception as e:
        print(f"Error sending final update: {e}")
    
    print("\nIntegration test complete - Check WebSocket client for real-time updates")

if __name__ == "__main__":
    test_command_socket_integration() 