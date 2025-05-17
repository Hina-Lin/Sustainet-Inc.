"""
Game 相關的 DTO (Data Transfer Objects)。
用於遊戲初始化與回合管理的資料結構定義。
"""

from typing import List, Dict, Any, Optional
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


class NewsPolishRequest(BaseModel):
    """
    新聞潤稿請求 DTO
    """
    session_id: str = Field(..., description="會話ID")
    content: str = Field(..., description="使用者的新聞內容", max_length=4096)
    requirements: Optional[str] = Field(None, description="使用者的潤稿要求", max_length=4096)
    sources: Optional[List[str]] = Field(None, description="參考的新聞連結")
    platform: Optional[str] = Field(None, description="即將發布的平台")
    platform_user: Optional[str] = Field(None, description="平台用戶名稱/特徵")
    current_situation: Optional[str] = Field(None, description="當前狀況描述")
    additional_context: Optional[Dict[str, Any]] = Field(None, description="其他上下文資訊")

class NewsPolishResponse(BaseModel):
    """
    新聞潤稿響應 DTO
    """
    original_content: str = Field(..., description="原始新聞內容")
    polished_content: str = Field(..., description="潤稿後的新聞內容")
    suggestions: Optional[List[str]] = Field(None, description="其他改進建議")
    reasoning: Optional[str] = Field(None, description="潤稿思路說明")

    class Config:
        json_schema_extra = {
            "example": {
                "original_content": "台南今天舉辦淨灘活動，共有200人參與，清出300公斤垃圾。",
                "polished_content": "【台南環保行動】藍天碧海守護者集結！今日台南黃金海岸淨灘活動吸引超過200名志工熱情參與，他們在短短三小時內清理出驚人的300公斤海洋垃圾，展現公民守護海洋生態的決心...",
                "suggestions": [
                    "可新增參與者感想或組織者聲明",
                    "建議加入未來淨灘活動資訊"
                ],
                "reasoning": "修改重點包括：加入吸引人的標題、使用更生動的描述語言、強調環保意識、突出成就感與使命感。"
            }
        }
