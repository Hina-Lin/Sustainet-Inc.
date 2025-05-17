"""add toolusage, update tools, drop game_records

Revision ID: 1320421e7d82
Revises: 02949813d101
Create Date: 2025-05-16 22:41:33.461601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1320421e7d82'
down_revision: Union[str, None] = '02949813d101'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升級資料庫結構，添加工具使用表、更新工具表及添加索引。"""
    
    # 1. 更新 tools 表結構
    
    # 先檢查 tools 表是否存在，如果不存在則創建
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'tools' not in inspector.get_table_names():
        # 創建 tools 表
        op.create_table(
            'tools',
            sa.Column('tool_name', sa.String(length=64), primary_key=True, comment="工具名稱（主鍵）"),
            sa.Column('description', sa.Text(), nullable=False, comment="工具描述"),
            sa.Column('trust_effect', sa.Integer(), nullable=True, server_default="0", comment="對信任值的基本效果"),
            sa.Column('spread_effect', sa.Integer(), nullable=True, server_default="0", comment="對傳播率的基本效果"),
            sa.Column('applicable_to', sa.String(length=32), nullable=False, server_default="both", comment="適用對象（player/ai/both）"),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text("now()"), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
        )
    else:
        # 檢查 tools 表欄位，添加缺少的欄位
        columns = [c['name'] for c in inspector.get_columns('tools')]
        
        if 'description' not in columns:
            op.add_column('tools', sa.Column('description', sa.Text(), nullable=True, comment="工具描述"))
        
        if 'trust_effect' not in columns:
            op.add_column('tools', sa.Column('trust_effect', sa.Integer(), nullable=True, server_default="0", comment="對信任值的基本效果"))
        
        if 'spread_effect' not in columns:
            op.add_column('tools', sa.Column('spread_effect', sa.Integer(), nullable=True, server_default="0", comment="對傳播率的基本效果"))
        
        if 'applicable_to' not in columns:
            op.add_column('tools', sa.Column('applicable_to', sa.String(length=32), nullable=True, server_default="both", comment="適用對象（player/ai/both）"))

        op.drop_column('tools', 'effect')
        op.drop_column('tools', 'role')
    # 2. 創建 tool_usages 表
    op.create_table(
        'tool_usages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, comment="工具使用記錄主鍵"),
        sa.Column('action_id', sa.Integer(), sa.ForeignKey('action_records.id'), nullable=False, comment="關聯的行動記錄 ID"),
        sa.Column('tool_name', sa.String(length=64), sa.ForeignKey('tools.tool_name'), nullable=False, comment="使用的工具名稱"),
        sa.Column('trust_effect', sa.Integer(), nullable=True, comment="對信任值的實際效果"),
        sa.Column('spread_effect', sa.Integer(), nullable=True, comment="對傳播率的實際效果"),
        sa.Column('is_effective', sa.Boolean(), server_default=sa.text("true"), comment="工具是否有效"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )
    
    # 3. 刪除 game_records 表
    op.drop_table('game_records')

def downgrade() -> None:
    """還原資料庫結構。"""

    # 還原 game_records 表
    op.create_table(
        'game_records',
        sa.Column('session_id', sa.String(length=64), primary_key=True, nullable=False, comment="遊戲會話 ID"),
        sa.Column('round_number', sa.Integer(), nullable=False, comment="遊戲回合數"),
        sa.Column('actor', sa.String(length=32), nullable=False, comment="行動者（player/ai）"),
        sa.Column('platform', sa.String(length=32), nullable=False, comment="平台名稱"),
        sa.Column('input_text', sa.Text(), nullable=False, comment="輸入文字"),
        sa.Column('used_tool', sa.String(length=64), nullable=True, comment="使用的工具名稱"),
        sa.Column('result', sa.Text(), nullable=True, comment="結果"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )
    
    # 刪除 tool_usages 表
    op.drop_table('tool_usages')
    
    # 還原 tools 表（如果進行了修改）
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'tools' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('tools')]
        
        if 'applicable_to' in columns:
            op.drop_column('tools', 'applicable_to')
        
        if 'spread_effect' in columns:
            op.drop_column('tools', 'spread_effect')
        
        if 'trust_effect' in columns:
            op.drop_column('tools', 'trust_effect')
        
        if 'description' in columns and 'effect' not in columns:
            op.add_column('tools', sa.Column('effect', sa.Text(), nullable=True))
            op.drop_column('tools', 'description')
        
        op.add_column('tools', sa.Column('role', sa.String(length=32), nullable=True))
