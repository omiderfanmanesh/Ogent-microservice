import requests
import json
import time

# First, let's create a test agent
def create_test_agent():
    try:
        url = "http://localhost:8080/agents/v1/agents"
        headers = {
            "Content-Type": "application/json",
            "x-user-id": "test-user"
        }
        payload = {
            "name": "Test Conversation Agent",
            "agent_type": "conversational",
            "description": "A test agent for conversation",
            "configuration": {
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "system_message": "You are a helpful assistant."
            },
            "permissions": {
                "execute_commands": False,
                "network_access": False
            },
            "metadata": {}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            print(f"Agent created successfully: {response.json()}")
            return response.json()["id"]
        else:
            print(f"Failed to create agent: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error creating agent: {e}")
        return None

# Test the agent with a simple question
def test_agent_question(agent_id, question="Who are you?"):
    try:
        url = f"http://localhost:8080/agents/v1/agents/{agent_id}/execute"
        headers = {
            "Content-Type": "application/json",
            "x-user-id": "test-user"
        }
        payload = {
            "input": question
        }
        
        print(f"Sending question: '{question}'")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response received with status: {result.get('status', 'unknown')}")
            return result
        else:
            print(f"Failed to execute agent: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error executing agent: {e}")
        return None

# Run the test
if __name__ == "__main__":
    print("Testing Agent with a simple question...")
    
    # First check if we have any existing agents
    headers = {"x-user-id": "test-user"}
    response = requests.get("http://localhost:8080/agents/v1/agents", headers=headers)
    agents = response.json()
    
    if agents.get("total", 0) > 0 and len(agents.get("items", [])) > 0:
        agent_id = agents["items"][0]["id"]
        print(f"Using existing agent with ID: {agent_id}")
    else:
        print("No existing agent found. Creating a new one...")
        agent_id = create_test_agent()
        
    if agent_id:
        print("\nExecuting agent with question 'Who are you?'")
        result = test_agent_question(agent_id)
        
        if result:
            print("\nAgent Response:")
            print("-" * 50)
            print(result.get("output", "No output received"))
            print("-" * 50)
    else:
        print("Could not find or create an agent to test.") 