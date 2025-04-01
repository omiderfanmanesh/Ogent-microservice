import os
import sys
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agent-service")

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create the FastAPI app
app = FastAPI(title="LangChain Agent Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

# Info endpoint
@app.get("/api/info")
async def get_info():
    return {
        "name": "LangChain Agent Service",
        "version": "1.0.0",
        "agent_types": ["conversational", "command", "sql", "custom"]
    }

# Simple mock implementation for testing
@app.post("/api/agents", status_code=201)
async def create_agent(request: Request):
    agent_data = await request.json()
    return {
        "id": "test-agent-123",
        "name": agent_data.get("name", "Test Agent"),
        "agent_type": agent_data.get("agent_type", "conversational"),
        "status": "created"
    }

@app.post("/api/agents/{agent_id}/execute")
async def execute_agent(agent_id: str, request: Request):
    execution_data = await request.json()
    prompt = execution_data.get("prompt", "")
    
    return {
        "agent_id": agent_id,
        "execution_id": "test-execution-456",
        "input": prompt,
        "output": f"This is a mock response to: {prompt}",
        "status": "completed"
    }

if __name__ == "__main__":
    logger.info("Starting agent service in no-db mode...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 