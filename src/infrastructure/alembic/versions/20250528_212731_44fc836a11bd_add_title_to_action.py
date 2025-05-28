"""add_title_to_action

Revision ID: 44fc836a11bd
Revises: 07467a6b338e
Create Date: 2025-05-28 21:27:31.405439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44fc836a11bd'
down_revision: Union[str, None] = '07467a6b338e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('action_records', sa.Column('title', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('action_records', 'title')
