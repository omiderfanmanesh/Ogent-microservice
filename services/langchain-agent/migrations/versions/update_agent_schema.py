"""Update agent schema to use agent_type

Revision ID: 39ad7b47df59
Revises: 38ad6a36cf48
Create Date: 2024-03-31T00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39ad7b47df59'
down_revision = '38ad6a36cf48'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename the type column to agent_type in agents table
    op.alter_column('agents', 'type', new_column_name='agent_type')
    
    # Rename meta_data to metadata for consistency
    op.alter_column('agents', 'meta_data', new_column_name='metadata')
    op.alter_column('executions', 'meta_data', new_column_name='metadata')
    op.alter_column('execution_steps', 'meta_data', new_column_name='metadata')
    op.alter_column('execution_commands', 'meta_data', new_column_name='metadata')


def downgrade() -> None:
    # Revert changes
    op.alter_column('agents', 'agent_type', new_column_name='type')
    
    op.alter_column('agents', 'metadata', new_column_name='meta_data')
    op.alter_column('executions', 'metadata', new_column_name='meta_data')
    op.alter_column('execution_steps', 'metadata', new_column_name='meta_data')
    op.alter_column('execution_commands', 'metadata', new_column_name='meta_data') 