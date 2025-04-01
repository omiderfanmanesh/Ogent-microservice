#!/usr/bin/env python3
"""
Command Execution Service API Test

This script tests the Command Execution Service API endpoints directly.

Usage:
    python test_command_api.py
"""

import requests
import time
import json
import sys
import os
import logging
import unittest

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

class CommandExecutionServiceTest(unittest.TestCase):
    """Test case for the Command Execution Service API"""
    
    def setUp(self):
        """Setup test environment"""
        self.base_url = BASE_URL
        logger.info(f"Using base URL: {self.base_url}")
    
    def test_health_endpoint(self):
        """Test the health endpoint"""
        url = f"{self.base_url}/health"
        response = requests.get(url, timeout=5)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")
    
    def test_execute_simple_command(self):
        """Test executing a simple command"""
        url = f"{self.base_url}/api/execute"
        payload = {
            "command": "echo 'Hello Test'",
            "timeout": 10
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        self.assertIn(response.status_code, [200, 201])
        data = response.json()
        self.assertIn("execution_id", data)
        self.assertIn("status", data)
        
        # Get the execution ID
        execution_id = data["execution_id"]
        
        # Wait for execution to complete
        self._wait_for_execution(execution_id)
        
        # Check execution status
        status_url = f"{self.base_url}/api/execution/{execution_id}"
        status_response = requests.get(status_url, timeout=5)
        
        self.assertEqual(status_response.status_code, 200)
        status_data = status_response.json()
        
        self.assertEqual(status_data["status"], "completed")
        self.assertIn("Hello Test", status_data["output"])
    
    def test_execute_disallowed_command(self):
        """Test executing a disallowed command"""
        url = f"{self.base_url}/api/execute"
        payload = {
            "command": "sudo rm -rf /",
            "timeout": 10
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        # Should be rejected
        self.assertIn(response.status_code, [400, 403])
    
    def test_execute_with_arguments(self):
        """Test executing a command with arguments"""
        url = f"{self.base_url}/api/execute"
        payload = {
            "command": "echo 'Argument 1' 'Argument 2'",
            "timeout": 10
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        self.assertIn(response.status_code, [200, 201])
        data = response.json()
        
        # Get the execution ID
        execution_id = data["execution_id"]
        
        # Wait for execution to complete
        self._wait_for_execution(execution_id)
        
        # Check execution status
        status_url = f"{self.base_url}/api/execution/{execution_id}"
        status_response = requests.get(status_url, timeout=5)
        
        self.assertEqual(status_response.status_code, 200)
        status_data = status_response.json()
        
        self.assertEqual(status_data["status"], "completed")
        self.assertIn("Argument 1", status_data["output"])
        self.assertIn("Argument 2", status_data["output"])
    
    def test_execute_command_with_pipes(self):
        """Test executing a command with pipes"""
        url = f"{self.base_url}/api/execute"
        payload = {
            "command": "echo 'line1\nline2\nline3' | grep 'line2'",
            "timeout": 10
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        self.assertIn(response.status_code, [200, 201])
        data = response.json()
        
        # Get the execution ID
        execution_id = data["execution_id"]
        
        # Wait for execution to complete
        self._wait_for_execution(execution_id)
        
        # Check execution status
        status_url = f"{self.base_url}/api/execution/{execution_id}"
        status_response = requests.get(status_url, timeout=5)
        
        self.assertEqual(status_response.status_code, 200)
        status_data = status_response.json()
        
        self.assertEqual(status_data["status"], "completed")
        self.assertIn("line2", status_data["output"])
        self.assertNotIn("line1", status_data["output"])
        self.assertNotIn("line3", status_data["output"])
    
    def test_execute_and_cancel(self):
        """Test executing a command and then canceling it"""
        url = f"{self.base_url}/api/execute"
        payload = {
            "command": "sleep 10",
            "timeout": 20
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        self.assertIn(response.status_code, [200, 201])
        data = response.json()
        
        # Get the execution ID
        execution_id = data["execution_id"]
        
        # Wait a bit to ensure the command has started
        time.sleep(1)
        
        # Cancel the execution
        cancel_url = f"{self.base_url}/api/execution/{execution_id}/cancel"
        cancel_response = requests.post(cancel_url, timeout=5)
        
        self.assertEqual(cancel_response.status_code, 200)
        
        # Check that the execution was canceled
        status_url = f"{self.base_url}/api/execution/{execution_id}"
        status_response = requests.get(status_url, timeout=5)
        
        self.assertEqual(status_response.status_code, 200)
        status_data = status_response.json()
        
        # The status should be 'canceled' or 'failed'
        self.assertIn(status_data["status"], ["canceled", "failed"])
    
    def _wait_for_execution(self, execution_id, max_retries=10, retry_delay=0.5):
        """Wait for an execution to complete"""
        url = f"{self.base_url}/api/execution/{execution_id}"
        
        for _ in range(max_retries):
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status in ["completed", "failed", "canceled"]:
                    return
            
            time.sleep(retry_delay)
        
        # If we reach here, the execution didn't complete in time
        logger.warning(f"Execution {execution_id} did not complete within the expected time")

if __name__ == "__main__":
    unittest.main() 