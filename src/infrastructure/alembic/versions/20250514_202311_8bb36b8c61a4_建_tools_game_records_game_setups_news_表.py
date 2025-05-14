"""建 tools, game_records, game_setups, news 表

Revision ID: 8bb36b8c61a4
Revises: 707b80235ea7
Create Date: 2025-05-14 20:23:11.371520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bb36b8c61a4'
down_revision: Union[str, None] = '707b80235ea7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 建立 tools 表
    op.create_table(
        'tools',
        sa.Column('tool_name', sa.String(64), primary_key=True),
        sa.Column('role', sa.String(32), nullable=False),
        sa.Column('effect', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )

    # 建立 game_records 表
    op.create_table(
        'game_records',
        sa.Column('session_id', sa.String(64), primary_key=True),
        sa.Column('round_number', sa.Integer, nullable=False),
        sa.Column('actor', sa.String(32), nullable=False),
        sa.Column('platform', sa.String(32), nullable=False),
        sa.Column('input_text', sa.Text, nullable=False),
        sa.Column('used_tool', sa.String(64), nullable=True),
        sa.Column('result', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )

    # 建立 game_setups 表
    op.create_table(
        'game_setups',
        sa.Column('session_id', sa.String(64), primary_key=True),
        sa.Column('platform', sa.String(32), nullable=False),
        sa.Column('audience_group', sa.String(64), nullable=False),
        sa.Column('platform_user_state', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )

    # 建立 news 表
    op.create_table(
        'news',
        sa.Column('news_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('image_url', sa.Text, nullable=True),
        sa.Column('source', sa.String(128), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 刪除 news 表
    op.drop_table('news')

    # 刪除 game_setups 表
    op.drop_table('game_setups')

    # 刪除 game_records 表
    op.drop_table('game_records')

    # 刪除 tools 表
    op.drop_table('tools')
