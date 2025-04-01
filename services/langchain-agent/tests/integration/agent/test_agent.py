import requests
import json

# Test the agent service health endpoint via API Gateway
def test_health():
    try:
        response = requests.get("http://localhost:8080/agents/health")
        print(f"Health endpoint response (status {response.status_code}): {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False

# Test the agent service info endpoint via API Gateway
def test_info():
    try:
        response = requests.get("http://localhost:8080/agents/info")
        print(f"Info endpoint response (status {response.status_code}): {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing info endpoint: {e}")
        return False

# Test listing agents via API Gateway
def test_list_agents():
    try:
        headers = {"x-user-id": "test-user"}
        response = requests.get("http://localhost:8080/agents/v1/agents", headers=headers)
        print(f"List agents endpoint response (status {response.status_code}): {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing list agents endpoint: {e}")
        return False

# Run all tests
if __name__ == "__main__":
    print("Testing Agent Service API via API Gateway...")
    health_result = test_health()
    info_result = test_info()
    agents_result = test_list_agents()
    
    print("\nTest Results:")
    print(f"Health Endpoint: {'PASS' if health_result else 'FAIL'}")
    print(f"Info Endpoint: {'PASS' if info_result else 'FAIL'}")
    print(f"List Agents Endpoint: {'PASS' if agents_result else 'FAIL'}") 