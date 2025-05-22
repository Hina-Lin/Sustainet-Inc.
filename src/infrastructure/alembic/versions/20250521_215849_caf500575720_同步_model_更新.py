"""同步 model 更新

Revision ID: caf500575720
Revises: 1f3d5b72234b
Create Date: 2025-05-21 21:58:49.760069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'caf500575720'
down_revision: Union[str, None] = '1f3d5b72234b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # 將 game_rounds.news_id 改成 nullable
    op.alter_column(
        'game_rounds',                   
        'news_id',                       
        existing_type=sa.Integer(),      
        nullable=True                    # 允許為 NULL
    ) # 將 news_id 改為可為 None（等新聞生出來再更新）


def downgrade() -> None:
    """Downgrade schema."""
    # 將 game_rounds.news_id 改成 not nullable
    op.alter_column(
        'game_rounds',                   
        'news_id',                       
        existing_type=sa.Integer(),      
        nullable=False                   # 不允許為 NULL
    ) # 將 news_id 改為不可以 None
