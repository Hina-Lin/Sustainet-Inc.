"""
ActionRecord 模型定義。
記錄每一回合中，AI 與玩家的實際行動內容與其擴散與信任影響。
"""

from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from .base import Base, TimeStampMixin

class ActionRecord(Base, TimeStampMixin):
    """
    行動記錄表。

    - **id**: 主鍵，自動遞增。
    - **session_id**: 遊戲識別碼，對應 GameSetup。
    - **round_number**: 回合編號。
    - **actor**: 行動者（"player" 或 "ai"）。
    - **platform**: 所使用的平台（如 "Facebook"）。
    - **content**: 發布的文字內容。
    - **reach_count**: 預估觸及人數。
    - **trust_change**: 此次行動造成的信任值變化。
    - **spread_change**: 此次行動造成的傳播率變化。
    - **effectiveness**: GM 評定效果（如 "high", "medium", "low"）。
    - **simulated_comments**: 模擬社群留言（JSON 陣列）。

    範例 simulated_comments 結構：
    ```json
    [
        "真的假的？看起來很有道理。",
        "來源在哪？",
        "我也轉發了這篇！"
    ]
    """
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主鍵，自動遞增"
    )

    session_id = Column(
        String(64),
        ForeignKey("game_setups.session_id"),
        nullable=False,
        comment="對應的遊戲 session ID"
    )

    round_number = Column(
        Integer,
        nullable=False,
        comment="所屬回合編號"
    )

    actor = Column(
        String(32),
        nullable=False,
        comment="行動者（'player' 或 'ai'）"
    )

    platform = Column(
        String(32),
        nullable=False,
        comment="發布平台名稱（如 Facebook、Twitter）"
    )

    content = Column(
        Text,
        nullable=False,
        comment="行動文字內容（可為假訊息或澄清）"
    )

    reach_count = Column(
        Integer,
        nullable=True,
        comment="GM 評估的觸及人數"
    )

    trust_change = Column(
        Integer,
        nullable=True,
        comment="此行動對信任值造成的變化"
    )

    spread_change = Column(
        Integer,
        nullable=True,
        comment="此行動對傳播率造成的變化"
    )

    effectiveness = Column(
        String(32),
        nullable=True,
        comment="GM 對此行動的評價等級（如 low/medium/high）"
    )

    simulated_comments = Column(
        JSON,
        nullable=True,
        comment="模擬社群留言（JSON 陣列）"
    )

    def __repr__(self):
        return (
            f"<ActionRecord session_id={self.session_id}, "
            f"round={self.round_number}, actor={self.actor}, platform={self.platform}>"
        )
