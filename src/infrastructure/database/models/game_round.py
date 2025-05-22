"""
GameRound 模型定義。
記錄每一回合的新聞來源與是否完成狀態。
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .base import Base, TimeStampMixin

class GameRound(Base, TimeStampMixin):
    """
    遊戲回合表。

    - **session_id**: 遊戲識別碼，對應 GameSetup 表（複合主鍵之一）。
    - **round_number**: 回合編號（從 1 開始）（複合主鍵之一）。
    - **news_id**: 對應新聞資料表中的主鍵。
    - **is_completed**: 回合是否已完成，預設為 False。

    範例：
    ```python
    GameRound(
        session_id="game123",
        round_number=1,
        news_id=12,
        is_completed=False
    )
    ```
    """

    session_id = Column(
        String(64),
        ForeignKey("game_setups.session_id"),
        primary_key=True, # Part of composite primary key
        nullable=False,
        comment="對應的遊戲 session ID"
    )

    round_number = Column(
        Integer,
        primary_key=True, # Part of composite primary key
        nullable=False,
        comment="回合編號（從 1 開始）"
    )

    news_id = Column(
        Integer,
        ForeignKey("news.news_id"),
        nullable=True, 
        comment="本回合所使用的新聞 ID"
    )

    is_completed = Column(
        Boolean,
        default=False,
        comment="該回合是否已完成（預設 False）"
    )

    def __repr__(self):
        return f"<GameRound session_id={self.session_id}, round={self.round_number}, news_id={self.news_id}>"
