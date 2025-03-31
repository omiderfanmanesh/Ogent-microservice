import pytest
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.execution import Execution
from app.infrastructure.persistence.repositories.execution_repository import ExecutionRepository
from app.infrastructure.persistence.repositories.agent_repository import AgentRepository
from app.domain.models.agent import Agent


@pytest.mark.asyncio
async def test_execution_create(db_session: AsyncSession):
    """Test creating a new execution record."""
    # Setup - first create a test agent
    agent_id = f"agt_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        name="Test Execution Agent",
        description="Agent for execution tests",
        type="conversational",
        configuration={"model": "gpt-3.5-turbo"},
        permissions={"users": ["*"]},
        meta_data={"test": True},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test_user"
    )
    
    agent_repo = AgentRepository(db_session)
    await agent_repo.create(agent)
    
    # Create an execution
    execution_id = f"exec_{uuid.uuid4().hex[:10]}"
    execution = Execution(
        id=execution_id,
        agent_id=agent_id,
        user_id="test_user",
        status="pending",
        input="Hello, how can you help me?",
        tokens_used=None,
        meta_data={"test": True, "source": "test_execution_create"},
        created_at=datetime.utcnow()
    )
    
    # Execute
    repo = ExecutionRepository(db_session)
    created_execution = await repo.create(execution)
    
    # Verify
    assert created_execution is not None
    assert created_execution.id == execution_id
    assert created_execution.agent_id == agent_id
    assert created_execution.status == "pending"
    
    # Cleanup
    await repo.delete(execution_id)
    await agent_repo.delete(agent_id)


@pytest.mark.asyncio
async def test_execution_get_by_id(db_session: AsyncSession):
    """Test retrieving an execution by ID."""
    # Setup - first create a test agent
    agent_id = f"agt_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        name="Test Execution Agent",
        description="Agent for execution tests",
        type="conversational",
        configuration={"model": "gpt-3.5-turbo"},
        permissions={"users": ["*"]},
        meta_data={"test": True},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test_user"
    )
    
    agent_repo = AgentRepository(db_session)
    await agent_repo.create(agent)
    
    # Create an execution
    execution_id = f"exec_{uuid.uuid4().hex[:10]}"
    execution = Execution(
        id=execution_id,
        agent_id=agent_id,
        user_id="test_user",
        status="completed",
        input="Tell me a joke",
        output="Why did the chicken cross the road? To get to the other side!",
        tokens_used=20,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        meta_data={"test": True, "source": "test_execution_get_by_id"},
        created_at=datetime.utcnow()
    )
    
    repo = ExecutionRepository(db_session)
    await repo.create(execution)
    
    # Execute
    retrieved_execution = await repo.get_by_id(execution_id)
    
    # Verify
    assert retrieved_execution is not None
    assert retrieved_execution.id == execution_id
    assert retrieved_execution.status == "completed"
    assert "chicken" in retrieved_execution.output
    
    # Cleanup
    await repo.delete(execution_id)
    await agent_repo.delete(agent_id)


@pytest.mark.asyncio
async def test_execution_update(db_session: AsyncSession):
    """Test updating an execution."""
    # Setup - first create a test agent
    agent_id = f"agt_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        name="Test Execution Agent",
        description="Agent for execution tests",
        type="conversational",
        configuration={"model": "gpt-3.5-turbo"},
        permissions={"users": ["*"]},
        meta_data={"test": True},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test_user"
    )
    
    agent_repo = AgentRepository(db_session)
    await agent_repo.create(agent)
    
    # Create an execution - initially pending
    execution_id = f"exec_{uuid.uuid4().hex[:10]}"
    execution = Execution(
        id=execution_id,
        agent_id=agent_id,
        user_id="test_user",
        status="pending",
        input="What's the weather like?",
        meta_data={"test": True, "source": "test_execution_update"},
        created_at=datetime.utcnow()
    )
    
    repo = ExecutionRepository(db_session)
    await repo.create(execution)
    
    # Execute - update to completed with output
    execution.status = "completed"
    execution.output = "The weather is sunny and 75 degrees."
    execution.tokens_used = 15
    execution.completed_at = datetime.utcnow()
    
    updated_execution = await repo.update(execution)
    
    # Verify
    assert updated_execution is not None
    assert updated_execution.id == execution_id
    assert updated_execution.status == "completed"
    assert "sunny" in updated_execution.output
    assert updated_execution.tokens_used == 15
    
    # Re-fetch to confirm persistence
    re_fetched = await repo.get_by_id(execution_id)
    assert re_fetched.status == "completed"
    
    # Cleanup
    await repo.delete(execution_id)
    await agent_repo.delete(agent_id)


@pytest.mark.asyncio
async def test_execution_delete(db_session: AsyncSession):
    """Test deleting an execution."""
    # Setup - first create a test agent
    agent_id = f"agt_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        name="Test Execution Agent",
        description="Agent for execution tests",
        type="conversational",
        configuration={"model": "gpt-3.5-turbo"},
        permissions={"users": ["*"]},
        meta_data={"test": True},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test_user"
    )
    
    agent_repo = AgentRepository(db_session)
    await agent_repo.create(agent)
    
    # Create an execution
    execution_id = f"exec_{uuid.uuid4().hex[:10]}"
    execution = Execution(
        id=execution_id,
        agent_id=agent_id,
        user_id="test_user",
        status="completed",
        input="Delete me",
        output="I will be deleted",
        meta_data={"test": True, "source": "test_execution_delete"},
        created_at=datetime.utcnow()
    )
    
    repo = ExecutionRepository(db_session)
    await repo.create(execution)
    
    # Verify it exists
    pre_delete = await repo.get_by_id(execution_id)
    assert pre_delete is not None
    
    # Execute
    deleted = await repo.delete(execution_id)
    
    # Verify
    assert deleted is True
    
    # Confirm it's gone
    post_delete = await repo.get_by_id(execution_id)
    assert post_delete is None
    
    # Cleanup agent
    await agent_repo.delete(agent_id)


@pytest.mark.asyncio
async def test_executions_by_agent(db_session: AsyncSession):
    """Test getting executions for a specific agent."""
    # Setup - create a test agent
    agent_id = f"agt_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        name="Test Agent For Executions",
        description="Agent to test execution filtering",
        type="conversational",
        configuration={"model": "gpt-3.5-turbo"},
        permissions={"users": ["*"]},
        meta_data={"test": True},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="test_user"
    )
    
    agent_repo = AgentRepository(db_session)
    await agent_repo.create(agent)
    
    # Create multiple executions for this agent
    repo = ExecutionRepository(db_session)
    execution_ids = []
    
    for i in range(3):
        execution_id = f"exec_agent_{uuid.uuid4().hex[:5]}"
        execution = Execution(
            id=execution_id,
            agent_id=agent_id,
            user_id="test_user",
            status="completed",
            input=f"Test input {i}",
            output=f"Test output {i}",
            meta_data={"test": True, "index": i},
            created_at=datetime.utcnow()
        )
        await repo.create(execution)
        execution_ids.append(execution_id)
    
    # Execute
    executions = await repo.get_by_agent_id(agent_id)
    
    # Verify
    assert len(executions) >= 3
    
    # Verify our test executions are in the results
    agent_executions = [e for e in executions if e.agent_id == agent_id]
    assert len(agent_executions) >= 3
    
    # Cleanup
    for execution_id in execution_ids:
        await repo.delete(execution_id)
    await agent_repo.delete(agent_id) 