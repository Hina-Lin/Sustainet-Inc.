"""
PlatformState 模型定義。
記錄每個回合中，各平台的信任狀態與傳播率。
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base, TimeStampMixin

class PlatformState(Base, TimeStampMixin):
    """
    平台狀態表。

    每筆紀錄對應特定回合中的某一個平台，記錄該平台上玩家與 AI 的信任度變化，
    以及該平台當下的訊息傳播率。

    欄位說明：
    - **id**: 主鍵，自動遞增。
    - **session_id**: 對應遊戲場次 ID，對應 GameSetup 表的主鍵。
    - **round_number**: 當前回合數。
    - **platform_name**: 平台名稱（如 "Facebook", "Instagram", "Thread"）。
    - **player_trust**: 玩家在此平台的信任值（0~100）。
    - **ai_trust**: AI 在此平台的信任值（0~100）。
    - **spread_rate**: 傳播率，百分比（整數 0~100）。
    """

    # 主鍵
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 遊戲場次 ID（外鍵）
    session_id = Column(
        String(64),
        ForeignKey("game_setups.session_id"),
        nullable=False,
        comment="對應遊戲場次 ID"
    )

    # 回合數
    round_number = Column(
        Integer,
        nullable=False,
        comment="當前回合數"
    )

    # 平台名稱
    platform_name = Column(
        String(32),
        nullable=False,
        comment="平台名稱（如 Facebook、Instagram）"
    )

    # 玩家信任值
    player_trust = Column(
        Integer,
        nullable=False,
        comment="玩家在此平台的信任值（0~100）"
    )

    # AI 信任值
    ai_trust = Column(
        Integer,
        nullable=False,
        comment="AI 在此平台的信任值（0~100）"
    )

    # 傳播率
    spread_rate = Column(
        Integer,
        nullable=False,
        comment="訊息傳播率，百分比（整數 0~100）"
    )

    def __repr__(self):
        return (
            f"<PlatformState session={self.session_id}, "
            f"round={self.round_number}, platform={self.platform_name}, "
            f"player_trust={self.player_trust}, ai_trust={self.ai_trust}, "
            f"spread_rate={self.spread_rate}>"
        )
