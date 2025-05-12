from sqlalchemy import Column, String
from .base import Base, TimeStampMixin

class GameSetup(Base, TimeStampMixin):
    """
    遊戲初始設置表：以 session_id 作為主鍵
    """
    session_id = Column(String(64), primary_key=True)
    platform = Column(String(32), nullable=False)
    audience_group = Column(String(64), nullable=False)
    platform_user_state = Column(String(64), nullable=False)

    def __repr__(self):
        return f"<GameSetup session={self.session_id}, platform={self.platform}>"
