from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from .base import Base, TimeStampMixin

class ArticlePolishRecord(Base, TimeStampMixin):
    __tablename__ = "article_polish_records"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主鍵，自動遞增"
    )
    
    session_id = Column(
        String(64),
        ForeignKey("article_polish_records.session_id"),
        nullable=False,
        comment="對應的遊戲 session ID"
    )
    
    round_number = Column(
        Integer,
        nullable=False,
        comment="對應的回合編號"
    )
    
    original_content = Column(
        Text,
        nullable=False,
        comment="原始文章內容"
    )
    
    polished_content = Column(
        Text,
        nullable=False,
        comment="潤飾後的文章內容"
    )

    __table_args__ = (
        Index('idx_sessionid_round', 'session_id', 'round_number'),
    )

    def __repr__(self):
        return f"<ArticlePolishRecord(id={self.id}, session_id={self.session_id}, round_number={self.round_number}, original_content={self.original_content}, polished_content={self.polished_content})>"