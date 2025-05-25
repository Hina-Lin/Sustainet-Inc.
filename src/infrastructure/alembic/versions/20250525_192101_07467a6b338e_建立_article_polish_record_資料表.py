"""建立 article_polish_record 資料表

Revision ID: 07467a6b338e
Revises: 3e3973af9d66
Create Date: 2025-05-25 19:21:01.013420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07467a6b338e'
down_revision: Union[str, None] = '3e3973af9d66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'article_polish_records',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, comment="主鍵，自動遞增"),
        sa.Column('session_id', sa.String(length=64), nullable=False, comment="對應的遊戲 session ID"),
        sa.Column('round_number', sa.Integer(), nullable=False, comment="對應的回合編號"),
        sa.Column('original_content', sa.Text(), nullable=False, comment="原始文章內容"),
        sa.Column('polished_content', sa.Text(), nullable=False, comment="潤飾後的文章內容"),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_sessionid_round', 'article_polish_records', ['session_id', 'round_number'])

def downgrade():
    op.drop_index('idx_sessionid_round', table_name='article_polish_records')
    op.drop_table('article_polish_records')
