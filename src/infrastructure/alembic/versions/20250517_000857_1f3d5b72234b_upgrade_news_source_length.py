"""upgrade news source length

Revision ID: 1f3d5b72234b
Revises: 1320421e7d82
Create Date: 2025-05-17 00:08:57.179969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f3d5b72234b'
down_revision: Union[str, None] = '1320421e7d82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('news', 'source', type_=sa.String(1280))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('news', 'source', type_=sa.String(128))
