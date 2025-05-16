"""重建 news / game_setup，新增 game_round / platform_state / action_record

Revision ID: 02949813d101
Revises: 8bb36b8c61a4
Create Date: 2025-05-16 19:26:35.732767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02949813d101'
down_revision: Union[str, None] = '8bb36b8c61a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升級資料庫結構。"""

    # 重建 news 表
    op.create_table(
        'news',
        sa.Column('news_id', sa.Integer(), primary_key=True, autoincrement=True, comment="新聞 ID（主鍵）"),
        sa.Column('title', sa.String(length=256), nullable=False, comment="新聞標題"),
        sa.Column('content', sa.Text(), nullable=False, comment="新聞內容"),
        sa.Column('veracity', sa.String(length=32), nullable=False, comment="真實性標籤（true / false / partial）"),
        sa.Column('category', sa.String(length=64), nullable=False, comment="新聞分類（如 energy, environment）"),
        sa.Column('source', sa.String(length=128), nullable=False, comment="新聞來源"),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text("true"), comment="是否啟用"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )

    # 重建 game_setups 表
    op.create_table(
        'game_setups',
        sa.Column('session_id', sa.String(length=64), primary_key=True, comment="遊戲 session ID（主鍵）"),
        sa.Column('player_initial_trust', sa.Integer(), nullable=False, server_default="50", comment="玩家初始信任值（預設 50）"),
        sa.Column('ai_initial_trust', sa.Integer(), nullable=False, server_default="50", comment="AI 初始信任值（預設 50）"),
        sa.Column('platforms', sa.JSON(), nullable=False, comment="平台與受眾設定，JSON 陣列"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )

    # 新增 game_rounds 表
    op.create_table(
        'game_rounds',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, comment="回合主鍵"),
        sa.Column('session_id', sa.String(length=64), sa.ForeignKey('game_setups.session_id'), nullable=False, comment="對應遊戲場次 ID"),
        sa.Column('round_number', sa.Integer(), nullable=False, comment="回合編號（從第 1 回合開始）"),
        sa.Column('news_id', sa.Integer(), sa.ForeignKey('news.news_id'), nullable=False, comment="使用的新聞 ID"),
        sa.Column('is_completed', sa.Boolean(), server_default=sa.text("false"), comment="是否完成該回合"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )

    # 新增 platform_states 表
    op.create_table(
        'platform_states',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, comment="平台狀態主鍵"),
        sa.Column('session_id', sa.String(length=64), sa.ForeignKey('game_setups.session_id'), nullable=False, comment="對應遊戲場次 ID"),
        sa.Column('round_number', sa.Integer(), nullable=False, comment="回合數"),
        sa.Column('platform_name', sa.String(length=32), nullable=False, comment="平台名稱（如 Facebook、Twitter）"),
        sa.Column('player_trust', sa.Integer(), nullable=False, comment="玩家在此平台的信任值（0~100）"),
        sa.Column('ai_trust', sa.Integer(), nullable=False, comment="AI 在此平台的信任值（0~100）"),
        sa.Column('spread_rate', sa.Integer(), nullable=False, comment="訊息傳播率，百分比（整數 0~100）"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )

    # 新增 action_records 表
    op.create_table(
        'action_records',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, comment="行動紀錄主鍵"),
        sa.Column('session_id', sa.String(length=64), sa.ForeignKey('game_setups.session_id'), nullable=False, comment="對應遊戲場次 ID"),
        sa.Column('round_number', sa.Integer(), nullable=False, comment="回合數"),
        sa.Column('actor', sa.String(length=32), nullable=False, comment="行動者（player / ai）"),
        sa.Column('platform', sa.String(length=32), nullable=False, comment="發布的平台名稱"),
        sa.Column('content', sa.Text(), nullable=False, comment="行動內容文字"),
        sa.Column('reach_count', sa.Integer(), nullable=True, comment="觸及人數（由 GM 評估）"),
        sa.Column('trust_change', sa.Integer(), nullable=True, comment="信任值變化"),
        sa.Column('spread_change', sa.Integer(), nullable=True, comment="傳播率變化"),
        sa.Column('effectiveness', sa.String(length=32), nullable=True, comment="效果評估（Low / Medium / High）"),
        sa.Column('simulated_comments', sa.JSON(), nullable=True, comment="模擬留言（JSON 陣列）"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    """還原資料庫結構。"""
    op.drop_table('action_records')
    op.drop_table('platform_states')
    op.drop_table('game_rounds')
    op.drop_table('game_setups')
    op.drop_table('news')
