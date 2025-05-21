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
    session_id: Optional[str] = Field(None, description="遊戲識別碼")
    round_number: Optional[int] = Field(None, description="回合數")
    platform_name: Optional[str] = Field(None, description="平台名稱，例如 Facebook, Instagram, Thread")
    player_trust: Optional[int] = Field(None, description="玩家在此平台的信任值（0-100）")
    ai_trust: Optional[int] = Field(None, description="AI 在此平台的信任值（0-100）")
    spread_rate: Optional[int] = Field(None, description="此平台的訊息傳播率（例如 65 表示 65%）")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "game_12345",
                "round_number": 1,
                "platform_name": "Facebook",
                "player_trust": 50,
                "ai_trust": 45,
                "spread_rate": 65
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

class FakeNewsAgentRequest(BaseModel):
    """
    假新聞生成請求 DTO
    """
    session_id: str = Field(..., description="遊戲 ID")  
    round_number: int = Field(..., description="回合數")

class ArticleMeta(BaseModel):
    """
    文章的基本資訊欄位
    """
    title: str = Field(..., description="文章標題")  
    content: str = Field(..., description="原始內容") 
    polished_content: Optional[str] = Field(None, description="潤稿後的內容（僅玩家使用工具時提供）")
    image_url: Optional[str] = Field(None, description="配圖連結") 
    source: Optional[str] = Field(None, description="新聞來源")
    author: str = Field(..., description="發文者名稱，ai 或 玩家名稱")
    published_date: str = Field(..., description="發布時間，例如 2024-05-18T15:30:00")
    target_platform: Optional[str] = Field(None, description="文章發佈的平台（AI 回合不顯示）")
    requirement: Optional[str] = Field(None, description="語氣或風格需求（如有）")
    veracity: Optional[str] = Field(None, description="AI 生成文章的真實性，由 AI 自己判斷")
        
class ArticleSubmissionResponse(BaseModel):
    """
    發布新聞後的回應
    """
    session_id: str = Field(..., description="遊戲識別碼")
    round_number: int = Field(..., description="回合數")
    actor: str = Field(..., description="ai / player")
    article: ArticleMeta = Field(..., description="實際發文的內容")
    trust_change: int = Field(..., description="這回合造成的信任值變化")
    reach_count: int = Field(..., description="這回合的觸及人數")
    spread_change: int = Field(..., description="這回合造成的傳播率變化")
    platform_setup: List[dict] = Field(..., description="平台+受眾組合")
    platform_status: List[PlatformStatus] = Field(..., description="所有平台目前的狀態")
    effectiveness: Optional[str] = Field(None, description="GM 評定效果（low / medium / high）")
    simulated_comments: Optional[List[str]] = Field(None, description="模擬社群留言，JSON 陣列")
    tool_used: Optional[List[Dict[str, Any]]] = Field(None, description="實際使用的工具")
    tool_list: List[Dict[str, Any]] = Field(..., description="所有工具的名稱、描述及啟用狀況")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "game_123456",
                "round_number": 2,
                "actor": "ai",
                "article": {
                    "title": "震驚！地球即將進入極端氣候新紀元",
                    "content": "新研究指出...",
                    "polished_content": None,
                    "image_url": "https://example.com/image.jpg",
                    "source": "虛構新聞社",
                    "author": "ai",
                    "published_date": "2025-05-18T15:00:00",
                    "target_platform": "Facebook",
                    "requirement": None,
                    "veracity": None
                },
                "trust_change": 8,
                "reach_count": 1200,
                "spread_change": 12,
                "platform_setup": [
                    {"name": "Facebook", "audience": "年輕族群"},
                    {"name": "Instagram", "audience": "中年族群"},
                    {"name": "Thread", "audience": "老年族群"}
                ],
                "platform_status": [
                    {
                        "session_id": "game_123456",
                        "round_number": 2,
                        "platform_name": "Facebook",
                        "player_trust": 50,
                        "ai_trust": 45,
                        "spread_rate": 65
                    },
                    {
                        "session_id": "game_123456",
                        "round_number": 2,
                        "platform_name": "Instagram",
                        "player_trust": 55,
                        "ai_trust": 50,
                        "spread_rate": 70
                    },
                    {
                        "session_id": "game_123456",
                        "round_number": 2,
                        "platform_name": "Twitter",
                        "player_trust": 60,
                        "ai_trust": 55,
                        "spread_rate": 75
                    }
                ],
                "effectiveness": "high",
                "simulated_comments": [
                    "這新聞太誇張了吧！",
                    "真的假的？",
                    "我覺得有點唬爛"
                ],
                "tool_used": [
                    {"tool_name": "情緒強化器", "effect": "increase_trust"}
                ],
                "tool_list": [
                    {"tool_name": "情緒強化器", "description": "提升情緒感染力"},
                    {"tool_name": "語氣轉換器", "description": "模仿年輕族群語氣"}
                ]
            }
        }
