"""
Alembic environment configuration file for database migrations.
"""

import asyncio
from logging.config import fileConfig
import os
import sys
from typing import Optional, List

from sqlalchemy import pool, MetaData, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Add the application root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application models and settings
from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.models import AgentModel, ExecutionModel, ExecutionStepModel, CommandModel
from app.domain.entities.execution import ExecutionStatus
from app.core.config import settings

# This is the Alembic Config object
config = context.config

# Override the SQLAlchemy URL with the one from settings
# For the synchronous engine
sync_url = settings.DATABASE_URL
# For the async engine
async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
config.set_main_option("sqlalchemy.url", sync_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter objects for autogenerate.
    """
    # Include all tables by default
    return True


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    # In offline mode, we'll generate a migration script
    # without connecting to the database
    if context.get_x_argument(as_dictionary=True).get('autogenerate', False):
        # Create an initial migration
        from alembic.autogenerate import produce_migrations
        engine = create_engine(sync_url, echo=False)
        
        # Configure alembic context
        context.configure(
            url=sync_url,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
        )
        
        with context.begin_transaction():
            context.run_migrations()
    else:
        # Regular offline mode for applying migrations
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            include_object=include_object,
        )
        
        with context.begin_transaction():
            context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Run migrations with given connection.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    try:
        connectable = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Falling back to offline mode")
        run_migrations_offline()


if context.is_offline_mode():
    run_migrations_offline()
else:
    try:
        asyncio.run(run_migrations_online())
    except Exception as e:
        print(f"Error in online migrations: {e}")
        print("Falling back to offline mode")
        run_migrations_offline()
