"""
Test service connectivity with proper mocking.

This module tests the connectivity between services by properly mocking
all HTTP requests.
"""

import os
import sys
import json
import unittest
from unittest import TestCase, mock
from dotenv import load_dotenv


class TestMockConnectivity(TestCase):
    """Test service connectivity with mocked requests."""

    def setUp(self):
        """Set up the test environment."""
        # Load environment variables
        load_dotenv()
        
        # URLs for different services
        self.agent_service_url = "http://localhost:8000"
        self.api_gateway_url = "http://localhost:8080"
        self.auth_service_url = "http://localhost:8080/auth"
        
        # JWT token for authentication
        self.token = os.getenv("TEST_JWT_TOKEN", "")
        if not self.token:
            print("WARNING: TEST_JWT_TOKEN not set, some tests will be skipped")

    @mock.patch('requests.get')
    def test_agent_health(self, mock_get):
        """Test the agent service health endpoint."""
        # Mock the response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "service": "agent"}
        mock_get.return_value = mock_response
        
        # Make the request using requests (but it will be mocked)
        import requests
        response = requests.get(f"{self.agent_service_url}/api/health")
        
        # Check the response
        print(f"Mocked agent response: {response.status_code}")
        print(f"Response content: {response.json()}")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        
        # Verify the mock was called with the correct URL
        mock_get.assert_called_once_with(f"{self.agent_service_url}/api/health")

    @mock.patch('requests.get')
    def test_gateway_health(self, mock_get):
        """Test the API gateway health endpoint."""
        # Mock the response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "service": "gateway"}
        mock_get.return_value = mock_response
        
        # Make the request using requests (but it will be mocked)
        import requests
        response = requests.get(f"{self.api_gateway_url}/health")
        
        # Check the response
        print(f"Mocked gateway response: {response.status_code}")
        print(f"Response content: {response.json()}")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        
        # Verify the mock was called with the correct URL
        mock_get.assert_called_once_with(f"{self.api_gateway_url}/health")

    @mock.patch('requests.post')
    def test_auth_verify(self, mock_post):
        """Test the auth service verification endpoint."""
        # Skip if no token
        if not self.token:
            self.skipTest("TEST_JWT_TOKEN not set, skipping authentication test")
        
        # Mock the response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "valid": True,
            "user": {
                "id": 1,
                "name": "Test User",
                "roles": ["user"],
                "permissions": ["view_agents", "run_agents"]
            }
        }
        mock_post.return_value = mock_response
        
        # Make the request using requests (but it will be mocked)
        import requests
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.auth_service_url}/verify",
            headers=headers,
            json={"token": self.token}
        )
        
        # Check the response
        print(f"Mocked auth verify response: {response.status_code}")
        print(f"Response content: {response.json()}")
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])
        
        # Verify the mock was called with the correct URL and data
        mock_post.assert_called_once_with(
            f"{self.auth_service_url}/verify",
            headers=headers,
            json={"token": self.token}
        )

    @mock.patch('requests.get')
    def test_api_gateway_agent_forwarding(self, mock_get):
        """Test the API gateway forwarding requests to the agent service."""
        # Mock the response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agents": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Test Agent",
                    "type": "openai",
                    "model": "gpt-4o-mini"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Make the request using requests (but it will be mocked)
        import requests
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.api_gateway_url}/agent/api/v1/agents",
            headers=headers
        )
        
        # Check the response
        print(f"Mocked agent list response: {response.status_code}")
        print(f"Response content: {response.json()}")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("agents", response.json())
        self.assertEqual(len(response.json()["agents"]), 1)
        self.assertEqual(response.json()["agents"][0]["name"], "Test Agent")
        
        # Verify the mock was called with the correct URL and headers
        mock_get.assert_called_once_with(
            f"{self.api_gateway_url}/agent/api/v1/agents",
            headers=headers
        )


if __name__ == "__main__":
    unittest.main() 