from app.infrastructure.persistence.database import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.clients.command_client import CommandClient
from app.api.dependencies import get_command_client


class SQLAgent:
    def __init__(self, db: AsyncSession, command_client: CommandClient):
        self.db = db
        self.command_client = command_client


async def get_sql_agent(
    db: AsyncSession = Depends(get_session),
    command_client: CommandClient = Depends(get_command_client),
) -> SQLAgent:
    return SQLAgent(db=db, command_client=command_client) 