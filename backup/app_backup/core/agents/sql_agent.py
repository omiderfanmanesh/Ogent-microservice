"""
SQL agent implementation.

This module provides the SQL agent implementation for executing SQL queries.
"""

from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agents.base_agent import BaseAgent
from app.core.entities.agent import Agent
from app.core.entities.execution import ExecutionResult
from app.infrastructure.persistence.database import get_session


class SQLAgent(BaseAgent):
    """
    SQL agent implementation for executing SQL queries.
    """
    
    def __init__(self, agent: Agent, db_session: AsyncSession):
        """
        Initialize the SQL agent.
        
        Args:
            agent: Agent entity
            db_session: Database session
        """
        super().__init__(agent)
        self.db_session = db_session
    
    async def run(self, input_text: str, execution_id: Optional[str] = None) -> ExecutionResult:
        """
        Run the SQL agent.
        
        Args:
            input_text: SQL query to execute
            execution_id: Optional execution ID for tracking
            
        Returns:
            Execution result
        """
        try:
            # Execute SQL query
            result = await self.db_session.execute(text(input_text))
            
            # Fetch results
            rows = result.fetchall()
            
            # Convert rows to list of dicts
            columns = result.keys()
            results = [dict(zip(columns, row)) for row in rows]
            
            return ExecutionResult(
                output=str(results),
                metadata={
                    "row_count": len(results),
                    "column_count": len(columns),
                    "columns": list(columns)
                }
            )
        except Exception as e:
            return ExecutionResult(
                output=None,
                error=str(e),
                metadata={"error_type": type(e).__name__}
            )
    
    @classmethod
    async def create(cls, agent: Agent) -> "SQLAgent":
        """
        Create a new SQL agent instance.
        
        Args:
            agent: Agent entity
            
        Returns:
            SQL agent instance
        """
        db_session = await anext(get_session())
        return cls(agent=agent, db_session=db_session) 