from sqlalchemy import Column, String, Integer, Text
from .base import Base, TimeStampMixin

class GameRecord(Base, TimeStampMixin):
    """
    遊戲紀錄表：以 session_id 作為主鍵
    """
    session_id = Column(String(64), primary_key=True)
    round_number = Column(Integer, nullable=False)
    actor = Column(String(32), nullable=False)
    platform = Column(String(32), nullable=False)
    input_text = Column(Text, nullable=False)
    used_tool = Column(String(64), nullable=True)
    result = Column(Text, nullable=True)

    def __repr__(self):
        return f"<GameRecord session={self.session_id}, round={self.round_number}>"
