import pytest
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.agent import Agent
from app.infrastructure.persistence.repositories.agent_repository import AgentRepository


@pytest.mark.asyncio
async def test_agent_create(db_session: AsyncSession):
    """Test creating a new agent in the database."""
    # Setup
    agent_id = f"agt_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        name="Test Create Agent",
        description="Agent created in test",
        type="conversational",
        configuration={"model": "gpt-3.5-turbo", "temperature": 0.5},
        permissions={"users": ["*"], "roles": ["admin"]},
        meta_data={"test": True, "created_by_test": "test_agent_create"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test_user"
    )
    
    # Execute
    repo = AgentRepository(db_session)
    created_agent = await repo.create(agent)
    
    # Verify
    assert created_agent is not None
    assert created_agent.id == agent_id
    assert created_agent.name == "Test Create Agent"
    
    # Cleanup
    await repo.delete(agent_id)


@pytest.mark.asyncio
async def test_agent_get_by_id(db_session: AsyncSession):
    """Test retrieving an agent by ID."""
    # Setup
    agent_id = f"agt_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        name="Test Get Agent",
        description="Agent for get test",
        type="command",
        configuration={"model": "gpt-4", "temperature": 0.2},
        permissions={"users": ["test_user"], "roles": ["admin", "user"]},
        meta_data={"test": True, "created_by_test": "test_agent_get_by_id"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test_user"
    )
    
    repo = AgentRepository(db_session)
    await repo.create(agent)
    
    # Execute
    retrieved_agent = await repo.get_by_id(agent_id)
    
    # Verify
    assert retrieved_agent is not None
    assert retrieved_agent.id == agent_id
    assert retrieved_agent.name == "Test Get Agent"
    assert retrieved_agent.type == "command"
    
    # Cleanup
    await repo.delete(agent_id)


@pytest.mark.asyncio
async def test_agent_update(db_session: AsyncSession):
    """Test updating an agent."""
    # Setup
    agent_id = f"agt_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        name="Original Name",
        description="Original description",
        type="conversational",
        configuration={"model": "gpt-3.5-turbo", "temperature": 0.7},
        permissions={"users": ["test_user"], "roles": ["admin"]},
        meta_data={"test": True, "created_by_test": "test_agent_update"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test_user"
    )
    
    repo = AgentRepository(db_session)
    await repo.create(agent)
    
    # Execute - update the agent
    agent.name = "Updated Name"
    agent.description = "Updated description"
    agent.configuration = {"model": "gpt-4", "temperature": 0.5}
    agent.updated_at = datetime.utcnow()
    
    updated_agent = await repo.update(agent)
    
    # Verify
    assert updated_agent is not None
    assert updated_agent.id == agent_id
    assert updated_agent.name == "Updated Name"
    assert updated_agent.description == "Updated description"
    assert updated_agent.configuration["model"] == "gpt-4"
    
    # Re-fetch to confirm persistence
    re_fetched = await repo.get_by_id(agent_id)
    assert re_fetched.name == "Updated Name"
    
    # Cleanup
    await repo.delete(agent_id)


@pytest.mark.asyncio
async def test_agent_delete(db_session: AsyncSession):
    """Test deleting an agent."""
    # Setup
    agent_id = f"agt_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        name="Agent To Delete",
        description="This agent will be deleted",
        type="conversational",
        configuration={"model": "gpt-3.5-turbo"},
        permissions={"users": ["*"]},
        meta_data={"test": True, "created_by_test": "test_agent_delete"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test_user"
    )
    
    repo = AgentRepository(db_session)
    await repo.create(agent)
    
    # Verify it exists
    pre_delete = await repo.get_by_id(agent_id)
    assert pre_delete is not None
    
    # Execute
    deleted = await repo.delete(agent_id)
    
    # Verify
    assert deleted is True
    
    # Confirm it's gone
    post_delete = await repo.get_by_id(agent_id)
    assert post_delete is None


@pytest.mark.asyncio
async def test_agent_list(db_session: AsyncSession):
    """Test listing all agents."""
    # Setup - create multiple agents
    repo = AgentRepository(db_session)
    
    # Create several test agents
    test_agents = []
    for i in range(3):
        agent_id = f"agt_list_{uuid.uuid4().hex[:5]}"
        agent = Agent(
            id=agent_id,
            name=f"List Test Agent {i}",
            description=f"Test agent {i} for list test",
            type="conversational",
            configuration={"model": "gpt-3.5-turbo"},
            permissions={"users": ["*"]},
            meta_data={"test": True, "created_by_test": "test_agent_list", "index": i},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="test_user"
        )
        await repo.create(agent)
        test_agents.append(agent_id)
    
    # Execute
    agents = await repo.list()
    
    # Verify - should at least contain our 3 test agents
    assert len(agents) >= 3
    
    # Check if our test agents are in the list
    found_count = 0
    for agent in agents:
        if agent.id in test_agents:
            found_count += 1
    
    assert found_count >= 3
    
    # Cleanup
    for agent_id in test_agents:
        await repo.delete(agent_id) 