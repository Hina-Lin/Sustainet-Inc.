"""
Game 相關的 DTO (Data Transfer Objects)。
用於遊戲初始化與回合管理的資料結構定義。
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ========== 通用資料物件 ==========

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
                "session_id": "game_001",
                "round_number": 1,
                "platform_name": "Facebook",
                "player_trust": 53,
                "ai_trust": 67,
                "spread_rate": 62
            }
            }

# ========== Dashboard ==========

class GameDashboardRequest(BaseModel):
    """
    遊戲面板請求 DTO
    """
    session_id: str = Field(..., description="遊戲識別碼")

class CurrentRoundInfo(BaseModel):
    """
    當前回合資訊
    """
    round_number: int = Field(..., description="當前回合數")
    ai_news: Optional[Dict[str, Any]] = Field(None, description="AI發布的假訊息")
    player_response: Optional[Dict[str, Any]] = Field(None, description="玩家回應")
    social_reactions: List[str] = Field(default=[], description="社群反應留言")
    ai_impact: Optional[Dict[str, Any]] = Field(None, description="AI影響評估")
    clarification_effect: Optional[Dict[str, Any]] = Field(None, description="澄清效果")
    
    class Config:
        json_schema_extra = {
            "example": {
                "round_number": 3,
                "ai_news": {
                    "title": "據說新再生能源其實會導致更多空汙，研究顯示…",
                    "content": "在新的研究中發現...",
                    "platform": "Instagram",
                    "category": "能源環保"
                },
                "player_response": {
                    "content": "實際上，太陽能與風力造成的污染極低，資料來自能源署。",
                    "tools_used": ["引用權威"]
                },
                "social_reactions": [
                    "假的啦，再生能源明明比石化好 (質疑)",
                    "我也有看到這個，真的假的 (疑惑)",
                    "怎麼沒有主流媒體報？ (質疑)"
                ],
                "ai_impact": {
                    "reach_count": 390,
                    "spread_change": "+15%",
                    "trust_change": "-10 點 (從 50 降至 40)",
                    "effectiveness": "高傳播，因情緒性語句 + 無來源"
                },
                "clarification_effect": {
                    "tool_bonus": "信任度 +5",
                    "final_effectiveness": "中度有效",
                    "reach_count": 120,
                    "trust_change": "+16 點 (從 40 升至 56)"
                }
            }
        }

class PlatformDashboardStatus(BaseModel):
    """
    面板用平台狀態顯示
    """
    platform_name: str = Field(..., description="平台名稱")
    player_trust: int = Field(..., description="玩家信任度")
    ai_trust: int = Field(..., description="AI信任度")
    spread_rate: int = Field(..., description="傳播率")
    trust_trend: str = Field(..., description="信任度趋势", example="↗")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform_name": "Instagram",
                "player_trust": 56,
                "ai_trust": 40,
                "spread_rate": 75,
                "trust_trend": "↗"
            }
        }

class GameDashboardResponse(BaseModel):
    """
    遊戲面板回應 DTO - 顯示當前遊戲狀態的即時面板
    """
    session_id: str = Field(..., description="遊戲識別碼")
    current_round: CurrentRoundInfo = Field(..., description="當前回合資訊")
    platform_status: List[PlatformDashboardStatus] = Field(..., description="平台狀態")
    game_progress: Dict[str, Any] = Field(..., description="遊戲進度")
    game_end_info: Optional[Dict[str, Any]] = Field(None, description="遊戲結束資訊（如果已結束）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "game_123",
                "current_round": {
                    "round_number": 3,
                    "ai_news": {
                        "title": "據說新再生能源其實會導致更多空汙",
                        "platform": "Instagram",
                        "category": "能源環保"
                    },
                    "social_reactions": [
                        "假的啦，再生能源明明比石化好 (質疑)"
                    ],
                    "ai_impact": {
                        "reach_count": 390,
                        "trust_change": "-10 點"
                    }
                },
                "platform_status": [
                    {
                        "platform_name": "Instagram",
                        "player_trust": 56,
                        "ai_trust": 40,
                        "spread_rate": 75,
                        "trust_trend": "↗"
                    }
                ],
                "game_progress": {
                    "current_round": 3,
                    "max_rounds": 10,
                    "is_ended": False
                },
                "game_end_info": None
            }
        }

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
    veracity: Optional[str] = Field(None, description="AI 生成文章的真實性，由 AI 或 GM 判定")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "極端氣候威脅全球能源",
                "content": "全球近年發生多起極端氣候事件，專家警告能源政策必須加快轉型...",
                "polished_content": None,
                "image_url": "https://img.server/image1.jpg",
                "source": "聯合報",
                "author": "ai",
                "published_date": "2025-05-21T14:45:00",
                "target_platform": "Instagram",
                "requirement": "強調危機感、簡明易懂",
                "veracity": "partial"
            }
        }

class ToolUsed(BaseModel):
    """
    玩家/AI 本回合實際使用的工具
    """
    tool_name: str = Field(..., description="工具名稱")

    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "事實查核"
            }
        }

# ========== Agent Specific Responses ==========

class FakeNewsAgentResponse(BaseModel):
    title: str = Field(..., description="Agent生成的新聞標題")
    content: str = Field(..., description="Agent生成的新聞內容")
    image_url: Optional[str] = Field(None, description="Agent生成的圖片URL（可選）")
    source: str = Field(..., description="Agent創造的新聞來源")
    veracity: str = Field(..., description="Agent判定的新聞真實性 (false, partial, true)")
    tool_used: Optional[List[ToolUsed]] = Field(None, description="Agent實際使用的工具")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "驚爆！太陽能板夜間竟能發電？最新突破能源界將改寫歷史！",
                "content": "科學家團隊深夜宣布，透過革命性的奈米塗層技術，成功讓太陽能板在無光環境下收集月光甚至星光轉換為可用電力...",
                "image_url": "https://example.com/fake_solar_night.jpg",
                "source": "全球科技前沿報",
                "veracity": "false"
            }
        }

class GameMasterAgentPlatformStatus(BaseModel):
    platform_name: str = Field(..., description="平台名稱")
    player_trust: int = Field(..., description="該平台玩家信任度")
    ai_trust: int = Field(..., description="該平台AI信任度")
    spread_rate: int = Field(..., description="該平台傳播率")

    class Config:
        json_schema_extra = {
            "example": {
                "platform_name": "Facebook",
                "player_trust": 52,
                "ai_trust": 45,
                "spread_rate": 70
            }
        }

class GameMasterAgentResponse(BaseModel):
    trust_change: int = Field(..., description="本回合目標平台信任值變化")
    spread_change: int = Field(..., description="本回合目標平台傳播率變化")
    reach_count: int = Field(..., description="本回合目標平台觸及人數")
    platform_status: List[GameMasterAgentPlatformStatus] = Field(..., description="各平台最新狀態")
    effectiveness: str = Field(..., description="行動有效性 (low, medium, high)")
    simulated_comments: List[str] = Field(..., description="模擬的社群評論")

    class Config:
        json_schema_extra = {
            "example": {
                "trust_change": -10,
                "spread_change": 15,
                "reach_count": 390,
                "platform_status": [
                    {"platform_name": "Facebook", "player_trust": 40, "ai_trust": 60, "spread_rate": 75},
                    {"platform_name": "Instagram", "player_trust": 50, "ai_trust": 50, "spread_rate": 50}
                ],
                "effectiveness": "high",
                "simulated_comments": [
                    "這太誇張了吧！", "消息來源可靠嗎？", "已轉發，大家注意！"
                ]
            }
        }

# ========== 共用回應 DTO（基底） ==========

class BaseRoundResponse(BaseModel):
    """
    回合共用回應物件（AI/玩家/遊戲開始/回合切換都繼承此類）
    """
    session_id: str = Field(..., description="遊戲識別碼")
    round_number: int = Field(..., description="回合數")
    actor: str = Field(..., description="行動者（ai 或 player）")
    article: ArticleMeta = Field(..., description="本回合發布的新聞內容")
    trust_change: int = Field(..., description="本回合造成的信任值變化")
    reach_count: int = Field(..., description="本回合的觸及人數")
    spread_change: int = Field(..., description="本回合造成的傳播率變化")
    platform_setup: List[Dict[str, Any]] = Field(..., description="平台與受眾組合（初始化時）")
    platform_status: List[PlatformStatus] = Field(..., description="三平台目前狀態")
    tool_used: Optional[List[ToolUsed]] = Field(None, description="實際使用的工具")
    tool_list: Optional[List[Dict[str, Any]]] = Field(None, description="全部可用工具")
    effectiveness: Optional[str] = Field(None, description="本回合貼文有效度（low/medium/high）")
    simulated_comments: Optional[List[str]] = Field(None, description="模擬群眾留言")
    game_end_info: Optional[Dict[str, Any]] = Field(None, description="遊戲結束資訊（如果遊戲結束）")
    # 新增：即時遊戲狀態
    dashboard_info: Optional[Dict[str, Any]] = Field(None, description="當前遊戲狀態面板資訊")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "game_002",
                "round_number": 2,
                "actor": "player",
                "article": {
                    "title": "大雨致水災 民生受影響",
                    "content": "昨夜連續暴雨導致多區域淹水，專家呼籲儘速檢討排水政策...",
                    "author": "player1",
                    "published_date": "2025-05-22T08:00:00"
                },
                "trust_change": 8,
                "reach_count": 12345,
                "spread_change": 5,
                "platform_setup": [
                    {"name": "Facebook", "audience": "年輕族群"},
                    {"name": "Instagram", "audience": "中年族群"},
                    {"name": "Thread", "audience": "老年族群"}
                ],
                "platform_status": [
                    {
                        "platform_name": "Facebook",
                        "player_trust": 68,
                        "ai_trust": 51,
                        "spread_rate": 42
                    }
                ],
                "tool_used": [
                    {
                        "tool_name": "圖片查證"
                    }
                ],
                "tool_list": [
                    {
                        "tool_name": "圖片查證",
                        "description": "協助判斷圖片真偽",
                        "applicable_to": "both"
                    }
                ],
                "effectiveness": "medium",
                "simulated_comments": [
                    "這新聞看起來很可疑！",
                    "真的發生這麼嚴重嗎？",
                    "請政府說明！"
                ]
            }
        }

# ========== 遊戲開始 ==========

class GameStartRequest(BaseModel):
    """
    開始遊戲請求 DTO
    """
    # 通常不需額外欄位

class GameStartResponse(BaseRoundResponse):
    """
    遊戲開始回應 DTO，內容同 BaseRoundResponse
    """
    pass

# ========== AI 回合 ==========

class AiTurnRequest(BaseModel):
    """
    AI 回合請求 DTO
    """
    session_id: str = Field(..., description="遊戲識別碼")
    round_number: int = Field(..., description="回合數")

class AiTurnResponse(BaseRoundResponse):
    """
    AI 回合回應 DTO
    """
    pass

# ========== 玩家回合 ==========

class PlayerTurnRequest(BaseModel):
    """
    玩家回合請求 DTO
    """
    session_id: str = Field(..., description="遊戲識別碼")
    round_number: int = Field(..., description="回合數")
    article: ArticleMeta = Field(..., description="玩家發布的新聞")
    tool_used: Optional[List[ToolUsed]] = Field(None, description="玩家實際使用的工具")
    tool_list: Optional[List[Dict[str, Any]]] = Field(None, description="全部可用工具（前端可留空）")

class PlayerTurnResponse(BaseRoundResponse):
    """
    玩家回合回應 DTO
    """
    pass

# ========== 下一回合 ==========

class StartNextRoundRequest(BaseModel):
    """
    下一回合請求 DTO
    """
    session_id: str = Field(..., description="遊戲識別碼")

class StartNextRoundResponse(BaseRoundResponse):
    """
    下一回合回應 DTO
    """
    pass

# ========== News 潤稿 ==========
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
