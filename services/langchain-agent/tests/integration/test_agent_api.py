"""
Test the agent API endpoints.

This module provides tests for the agent service REST API.
"""

import os
import pytest
import httpx
import json
from typing import Dict, Any

# Base URL for the API
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8002")

# Test user ID for authentication
TEST_USER_ID = "test-user-1"

# Sample agent data for testing
SAMPLE_AGENT = {
    "name": "Test Agent",
    "agent_type": "conversational",
    "description": "A test agent for API testing",
    "configuration": {
        "temperature": 0.7,
        "model": "gpt-3.5-turbo"
    },
    "permissions": {
        "allowed_tools": ["web_search", "calculator"]
    },
    "metadata": {
        "created_for": "api_testing"
    }
}


async def test_health_endpoint():
    """Test the health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"


async def test_info_endpoint():
    """Test the info endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/info")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "agent_types" in data
        assert isinstance(data["agent_types"], list)


@pytest.mark.asyncio
async def test_agent_crud_operations():
    """Test CRUD operations for agents."""
    created_agent_id = None
    
    # Create a new agent
    async with httpx.AsyncClient() as client:
        headers = {"x-user-id": TEST_USER_ID}
        response = await client.post(
            f"{API_BASE_URL}/api/v1/agents",
            json=SAMPLE_AGENT,
            headers=headers
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        created_agent_id = data["id"]
        
        # Verify agent data
        assert data["name"] == SAMPLE_AGENT["name"]
        assert data["agent_type"] == SAMPLE_AGENT["agent_type"]
        assert data["description"] == SAMPLE_AGENT["description"]
    
    # Skip other tests if agent creation failed
    if not created_agent_id:
        pytest.skip("Agent creation failed, skipping remaining tests")
        
    # Get the created agent
    async with httpx.AsyncClient() as client:
        headers = {"x-user-id": TEST_USER_ID}
        response = await client.get(
            f"{API_BASE_URL}/api/v1/agents/{created_agent_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_agent_id
        
    # List agents
    async with httpx.AsyncClient() as client:
        headers = {"x-user-id": TEST_USER_ID}
        response = await client.get(
            f"{API_BASE_URL}/api/v1/agents",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0
        
        # Check if our created agent is in the list
        agent_ids = [agent["id"] for agent in data["items"]]
        assert created_agent_id in agent_ids
    
    # Update the agent
    updated_data = {
        "name": "Updated Test Agent",
        "description": "Updated description",
        "configuration": {
            "temperature": 0.5,
            "model": "gpt-4"
        }
    }
    
    async with httpx.AsyncClient() as client:
        headers = {"x-user-id": TEST_USER_ID}
        response = await client.put(
            f"{API_BASE_URL}/api/v1/agents/{created_agent_id}",
            json=updated_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == updated_data["name"]
        assert data["description"] == updated_data["description"]
    
    # Delete the agent
    async with httpx.AsyncClient() as client:
        headers = {"x-user-id": TEST_USER_ID}
        response = await client.delete(
            f"{API_BASE_URL}/api/v1/agents/{created_agent_id}",
            headers=headers
        )
        assert response.status_code == 204
    
    # Verify agent is deleted
    async with httpx.AsyncClient() as client:
        headers = {"x-user-id": TEST_USER_ID}
        response = await client.get(
            f"{API_BASE_URL}/api/v1/agents/{created_agent_id}",
            headers=headers
        )
        assert response.status_code == 404 