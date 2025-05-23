"""add available_from_round 

Revision ID: 3e3973af9d66
Revises: d703abc30de2
Create Date: 2025-05-23 11:33:10.741903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e3973af9d66'
down_revision: Union[str, None] = 'd703abc30de2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tools', sa.Column('available_from_round', sa.Integer(), nullable=False, server_default=sa.text('1')))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tools', 'available_from_round')
