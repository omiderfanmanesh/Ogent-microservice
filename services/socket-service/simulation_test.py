#!/usr/bin/env python3
import requests
import json
import time
import uuid
import sys

def simulate_execution():
    """Simulate an execution and send updates to the Socket Service"""
    api_gateway_url = "http://localhost:8081"
    
    # Generate a unique execution ID
    execution_id = str(uuid.uuid4())
    print(f"Starting simulation with execution ID: {execution_id}")
    
    # Simulate different execution statuses
    statuses = [
        {"status": "queued", "progress": 0, "output": ""},
        {"status": "preparing", "progress": 10, "output": "Setting up execution environment..."},
        {"status": "running", "progress": 25, "output": "Starting execution...\nProcessing input..."},
        {"status": "running", "progress": 50, "output": "Processing input...\nAnalyzing data..."},
        {"status": "running", "progress": 75, "output": "Processing input...\nAnalyzing data...\nGenerating results..."},
        {"status": "completed", "progress": 100, "output": "Processing input...\nAnalyzing data...\nGenerating results...\nExecution completed successfully!"}
    ]
    
    for i, status_update in enumerate(statuses):
        print(f"\nSending status update {i+1}/{len(statuses)}:")
        payload = {
            "executionId": execution_id,
            **status_update
        }
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{api_gateway_url}/socket-http/api/execution-status", 
                json=payload,
                timeout=5  # Set a timeout to prevent hanging
            )
            print(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text}")
            else:
                print(f"Error: {response.text}")
        except requests.exceptions.Timeout:
            print("Request timed out. The server might be processing the request or there might be connectivity issues.")
        except Exception as e:
            print(f"Error sending update: {e}")
        
        # Wait between updates
        if i < len(statuses) - 1:
            print(f"Waiting 2 seconds before next update...")
            time.sleep(2)
    
    print("\nSimulation complete. Check the WebSocket client for updates.")

if __name__ == "__main__":
    simulate_execution() 