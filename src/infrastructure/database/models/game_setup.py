"""
GameSetup 模型定義。
記錄每場遊戲的初始設定，包括信任值與平台配置。
"""

from sqlalchemy import Column, Integer, String, JSON
from .base import Base, TimeStampMixin

class GameSetup(Base, TimeStampMixin):
    """
    遊戲初始設置表。

    - **session_id**: 主鍵，對應一場遊戲的唯一識別碼。
    - **player_initial_trust**: 玩家初始信任度，預設為 50。
    - **ai_initial_trust**: AI 初始信任度，預設為 50。
    - **platforms**: 平台與受眾設定，JSON 格式。

    範例 JSON 結構：
    ```json
    [
        {"name": "Facebook", "audience": "年輕族群"},
        {"name": "Instagram", "audience": "學生"}
    ]
    ```
    """

    session_id = Column(
        String(64),
        primary_key=True,
        comment="遊戲 session ID，主鍵"
    )

    player_initial_trust = Column(
        Integer,
        nullable=False,
        default=50,
        comment="玩家初始信任度（預設為 50）"
    )

    ai_initial_trust = Column(
        Integer,
        nullable=False,
        default=50,
        comment="AI 初始信任度（預設為 50）"
    )

    platforms = Column(
        JSON,
        nullable=False,
        comment="平台與受眾設定，JSON 格式（例：[{'name': 'Facebook', 'audience': '年輕族群'}]）"
    )

    def __repr__(self):
        return f"<GameSetup session_id={self.session_id}, platforms={self.platforms}>"
