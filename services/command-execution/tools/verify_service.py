#!/usr/bin/env python3
"""
Command Execution Service Verification Tool

This script verifies the functionality of the Command Execution Service by:
1. Checking the health endpoint
2. Testing basic command execution
3. Verifying command validation (allowed vs disallowed commands)
4. Testing the execution status retrieval

Usage:
    python verify_service.py

Requirements:
    requests
"""

import requests
import time
import json
import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = os.getenv("COMMAND_SERVICE_URL", "http://localhost:5001")
if not BASE_URL.startswith("http"):
    BASE_URL = f"http://{BASE_URL}"

def check_health():
    """Check if the command execution service is healthy"""
    logger.info("Checking service health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info("Health check successful ✅")
            return True
        else:
            logger.error(f"Health check failed with status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"Health check failed with error: {str(e)}")
        return False

def test_execute_allowed_command():
    """Test execution of an allowed command"""
    logger.info("Testing execution of allowed command: echo 'Hello World'...")
    try:
        payload = {
            "command": "echo 'Hello World'",
            "timeout": 10
        }
        response = requests.post(f"{BASE_URL}/api/execute", json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            data = response.json()
            execution_id = data.get("execution_id")
            logger.info(f"Command execution initiated with ID: {execution_id}")
            
            # Wait for execution to complete
            return check_execution_status(execution_id)
        else:
            logger.error(f"Command execution failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Command execution request failed with error: {str(e)}")
        return False

def test_execute_disallowed_command():
    """Test execution of a disallowed command - should be rejected"""
    logger.info("Testing execution of disallowed command: rm -rf /...")
    try:
        payload = {
            "command": "rm -rf /",
            "timeout": 10
        }
        response = requests.post(f"{BASE_URL}/api/execute", json=payload, timeout=10)
        
        # We expect this to be rejected (status code 400 or 403)
        if response.status_code in [400, 403]:
            logger.info("Disallowed command correctly rejected ✅")
            return True
        else:
            logger.error(f"Disallowed command not properly rejected. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Command execution request failed with error: {str(e)}")
        return False

def check_execution_status(execution_id, max_retries=10, retry_delay=1):
    """Check the status of an execution until completion or failure"""
    logger.info(f"Checking execution status for ID: {execution_id}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/api/execution/{execution_id}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                progress = data.get("progress", 0)
                output = data.get("output", "")
                
                logger.info(f"Execution status: {status}, progress: {progress}%")
                
                if status == "completed":
                    logger.info(f"Command execution completed successfully ✅")
                    logger.info(f"Output: {output}")
                    return True
                elif status == "failed":
                    error = data.get("error", "Unknown error")
                    logger.error(f"Command execution failed with error: {error}")
                    return False
                elif status == "running" and attempt == max_retries - 1:
                    logger.warning("Command execution still running after maximum retries")
                    return False
                # If still running, wait and retry
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to get execution status. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except requests.RequestException as e:
            logger.error(f"Execution status check failed with error: {str(e)}")
            return False
    
    logger.error("Exceeded maximum retries while checking execution status")
    return False

def test_complex_command():
    """Test execution of a more complex command with piping"""
    logger.info("Testing execution of complex command: ls -la | grep '.'...")
    try:
        payload = {
            "command": "ls -la | grep '.'",
            "timeout": 10
        }
        response = requests.post(f"{BASE_URL}/api/execute", json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            data = response.json()
            execution_id = data.get("execution_id")
            logger.info(f"Complex command execution initiated with ID: {execution_id}")
            
            # Wait for execution to complete
            return check_execution_status(execution_id)
        else:
            logger.error(f"Complex command execution failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Complex command execution request failed with error: {str(e)}")
        return False

def main():
    """Main function to run all verification tests"""
    logger.info("Starting Command Execution Service verification...")
    logger.info(f"Using base URL: {BASE_URL}")
    
    # Test results
    results = {
        "health_check": False,
        "allowed_command": False,
        "disallowed_command": False,
        "complex_command": False
    }
    
    # Run tests
    results["health_check"] = check_health()
    
    if results["health_check"]:
        results["allowed_command"] = test_execute_allowed_command()
        results["disallowed_command"] = test_execute_disallowed_command()
        results["complex_command"] = test_complex_command()
    
    # Print summary
    logger.info("\n=========== Verification Summary ===========")
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Return overall success/failure
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 