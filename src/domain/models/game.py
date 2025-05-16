"""
Game 模型定義。
包含遊戲狀態、工具、平台狀態等資料結構。
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timezone

@dataclass
class Tool:
    """
    工具的資料結構。
    - **name**: 工具名稱（如「事實查核」、「情緒渲染」）
    - **user**: 使用者（"player" 或 "AI"）
    """
    name: str  # 工具名稱
    user: str  # 使用者

@dataclass
class PlatformStatus:
    """
    平台狀態的資料結構。
    - **name**: 平台名稱（如 Facebook）
    - **audience**: 受眾群體（如 年輕族群）
    - **player_trust**: 玩家在此平台的信任度
    - **agent_trust**: AI 在此平台的信任度
    - **spread_rate**: 傳播率（0~100）
    """
    name: str  # 平台名稱
    audience: str  # 受眾群體
    player_trust: int  # 玩家信任度
    agent_trust: int  # AI 信任度
    spread_rate: int  # 傳播率

@dataclass
class AILastAction:
    """
    AI 上一回合的行動資料結構。
    - **content**: AI 發布的假訊息文字
    - **platform**: 發布的平台
    - **trust_change**: 該次行動導致的信任變化（由 GM 評分）
    - **spread_change**: 該次行動導致的傳播率變化（由 GM 評分）
    """
    content: str  # 假訊息文字
    platform: str  # 發布的平台
    trust_change: int  # 信任變化
    spread_change: int  # 傳播率變化

@dataclass
class GameState:
    """
    遊戲狀態的資料結構。
    - **session_id**: 遊戲的唯一 ID（對應資料庫 GameSetup 的主鍵）
    - **trust_score_player**: 玩家總信任分數（全平台總和或平均）
    - **trust_score_agent**: AI 總信任分數
    - **round_number**: 當前回合數，預設從第 1 回合開始
    - **status**: 遊戲狀態，可為 "ongoing"（進行中）、"completed"（已結束）、"aborted"（中止）
    - **created_at**: 建立時間（UTC）
    - **platforms**: 所有平台的目前狀態
    - **tools_used**: 遊戲中所有使用過的工具紀錄
    - **last_ai_action**: 上一回合 AI 發布的訊息與效果評估
    """
    session_id: str  # 遊戲的唯一 ID
    trust_score_player: int  # 玩家總信任分數
    trust_score_agent: int  # AI 總信任分數
    round_number: int = 1  # 當前回合數
    status: str = "ongoing"  # 遊戲狀態
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))  # 建立時間

    platforms: List[PlatformStatus] = field(default_factory=list)  # 平台狀態列表
    tools_used: List[Tool] = field(default_factory=list)  # 使用過的工具列表
    last_ai_action: Optional[AILastAction] = None  # 上一回合的 AI 行動
