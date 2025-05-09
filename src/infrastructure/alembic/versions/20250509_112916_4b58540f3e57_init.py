"""init

Revision ID: 4b58540f3e57
Revises:
Create Date: 2025-05-09 11:29:16.040871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b58540f3e57'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('agent_name', sa.String(length=128), nullable=False, unique=True, index=True),
        sa.Column('provider', sa.String(length=64), nullable=False, server_default='openai'),
        sa.Column('model_name', sa.String(length=64), nullable=False, server_default='gpt-4.1'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instruction', sa.Text(), nullable=True),
        sa.Column('tools', sa.JSON(), nullable=False,
                  server_default=sa.text("'{\"tools\": [{\"name\": \"\", \"params\": {}}]}'::jsonb")),
        sa.Column('num_history_responses', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('add_history_to_messages', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('show_tool_calls', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('markdown', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('debug', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('add_datetime_to_instructions', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('agents')
