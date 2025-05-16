"""
Game 相關的 DTO (Data Transfer Objects)。
用於遊戲初始化與回合管理的資料結構定義。
"""

from typing import List
from pydantic import BaseModel, Field


class PlatformStatus(BaseModel):
    """
    回傳每個平台當前狀態（初始化時由 DB 取得 PlatformState 轉換而來）
    """
    platform: str = Field(..., description="平台名稱，例如 Facebook、Twitter")
    player_trust: int = Field(..., description="玩家在此平台的信任值（0-100）")
    ai_trust: int = Field(..., description="AI 在此平台的信任值（0-100）")
    spread: int = Field(..., description="此平台的訊息傳播率（例如 65 表示 65%）")

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "Facebook",
                "player_trust": 50,
                "ai_trust": 45,
                "spread": 65
            }
        }


class GameStartResponse(BaseModel):
    """
    遊戲初始化後回傳給前端的資料格式
    """
    session_id: str = Field(..., description="遊戲識別碼，例如 game_12345")
    platforms: List[PlatformStatus] = Field(..., description="每個平台的狀態資訊")
    first_news: str = Field(..., description="第一則 AI 發出的假訊息標題（非全文）")
    ai_platform: str = Field(..., description="AI 在哪個平台發佈該訊息")
    trust_change: int = Field(..., description="該訊息造成的信任值變化（例如 +8）")
    spread_change: int = Field(..., description="該訊息造成的傳播率變化（例如 +12）")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "game_12345",
                "platforms": [
                    {
                        "platform": "Facebook",
                        "player_trust": 50,
                        "ai_trust": 45,
                        "spread": 65
                    },
                    {
                        "platform": "Instagram",
                        "player_trust": 55,
                        "ai_trust": 50,
                        "spread": 70
                    },
                    {
                        "platform": "Twitter",
                        "player_trust": 60,
                        "ai_trust": 55,
                        "spread": 75
                    }
                ],
                "first_news": "AI 發佈的假訊息標題",
                "ai_platform": "Facebook",
                "trust_change": 8,
                "spread_change": 12
            }
        }
