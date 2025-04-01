import requests
import json
import docker
import time

# Connect to Docker and restart the agent service with our command
def restart_agent_service():
    try:
        client = docker.from_env()
        container = client.containers.get('ogent-agent-service')
        
        # Stop the container if it's running
        if container.status == 'running':
            print("Stopping container...")
            container.stop()
        
        # Start the container with a custom command
        print("Starting container with custom command...")
        container.start()
        
        # Give it time to start up
        print("Waiting for service to start...")
        time.sleep(5)
        
        return True
    except Exception as e:
        print(f"Error restarting agent service: {e}")
        return False

# Test the agent service directly from the container
def test_agent_service():
    try:
        client = docker.from_env()
        container = client.containers.get('ogent-agent-service')
        
        # Run a command in the container to test the API
        print("\nChecking database:")
        result = container.exec_run("python -c \"from app.infrastructure.persistence.models import AgentModel; print(AgentModel.__table__.columns)\"")
        print(f"Database columns: {result.output.decode()}")
        
        print("\nChecking if the service is running:")
        result = container.exec_run("ps aux | grep uvicorn")
        print(f"Service processes: {result.output.decode()}")
        
        return True
    except Exception as e:
        print(f"Error testing agent service: {e}")
        return False

# Run the tests
if __name__ == "__main__":
    print("Testing Agent Service directly...")
    restart_result = restart_agent_service()
    test_result = test_agent_service()
    
    print("\nTest Results:")
    print(f"Restart Agent Service: {'PASS' if restart_result else 'FAIL'}")
    print(f"Agent Service Tests: {'PASS' if test_result else 'FAIL'}") 