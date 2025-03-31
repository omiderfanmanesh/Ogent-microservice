"""
Tests for the API Gateway service.
"""

from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Ogent API Gateway"}


def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("main.auth_client")
def test_login(mock_auth_client):
    """Test login endpoint."""
    # Configure mock
    mock_response = MagicMock()
    mock_response.content = b'{"access_token": "test_token", "token_type": "bearer"}'
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_auth_client.post.return_value = mock_response

    # Test login endpoint
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@patch("main.auth_client")
def test_register(mock_auth_client):
    """Test register endpoint."""
    # Configure mock
    mock_response = MagicMock()
    mock_response.content = b'{"id": "123", "username": "testuser"}'
    mock_response.status_code = 201
    mock_response.headers = {"Content-Type": "application/json"}
    mock_auth_client.post.return_value = mock_response

    # Test register endpoint
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 201
    assert "id" in response.json()


@patch("main.app_client")
def test_api_gateway(mock_app_client):
    """Test generic API gateway endpoint."""
    # Configure mock
    mock_response = MagicMock()
    mock_response.content = b'{"data": "test"}'
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_app_client.request.return_value = mock_response

    # Test API gateway endpoint
    response = client.get("/api/test")
    assert response.status_code == 200
    assert response.json() == {"data": "test"} 