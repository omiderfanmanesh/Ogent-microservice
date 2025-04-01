"""
Test schema compatibility between models and migrations.

This module checks if the table definitions in models.py match the migrations.
"""

import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from app.infrastructure.persistence.models import Base, AgentModel
from app.core.config import settings

@pytest.mark.asyncio
async def test_agent_model_columns():
    """Test that the agent model columns match the database schema."""
    # Create an async engine for testing
    engine = create_async_engine(settings.DATABASE_URL)
    
    # Connect to the database and get inspector
    async with engine.connect() as conn:
        inspector = inspect(conn)
        
        # Get the columns from the database
        columns = await inspector.get_columns("agents")
        db_column_names = [col["name"] for col in columns]
        
        # Get the columns from the model
        model_column_names = [c.name for c in AgentModel.__table__.columns]
        
        # Print for debugging
        print("Database columns:", db_column_names)
        print("Model columns:", model_column_names)
        
        # Check if the agent_type column exists in the database
        assert "agent_type" in db_column_names, "agent_type column is missing in the database"
        
        # Check if all model columns exist in the database
        for col_name in model_column_names:
            assert col_name in db_column_names, f"Column {col_name} from model not found in database" 