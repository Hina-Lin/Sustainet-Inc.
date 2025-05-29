from src.domain.models.game import Article
from src.application.dto.game_dto import ArticleMeta, FakeNewsAgentResponse
from datetime import datetime
from typing import List, Optional, Dict, Any

class AiTurnLogic:
    def select_platform(self, platforms):
        # AI不再隨機選擇平台，而是由Agent根據平台狀況自己決定
        # 這個方法現在返回None，讓Agent在generate_content時自己選擇
        return None
    
    def prepare_fake_news_variables(
        self, 
        all_platforms: List = None,
        news_1 = None, 
        news_2 = None, 
        player_responses: Optional[List[Dict[str, Any]]] = None,
        ai_previous_feedback: Optional[Dict[str, Any]] = None,
        current_round: int = 1,
        available_tools: Optional[List[Dict[str, Any]]] = None
    ):
        # 格式化平台狀態信息供Agent選擇
        platform_options = []
        if all_platforms:
            for platform in all_platforms:
                platform_options.append({
                    "name": platform.name,
                    "audience": platform.audience,
                    "player_trust": platform.player_trust.value,
                    "ai_trust": platform.ai_trust.value,
                    "spread_rate": platform.spread_rate.value
                })
        
        variables = {
            "news_1": news_1.content if news_1 else "",
            "news_1_veracity": news_1.veracity if news_1 else "",
            "news_2": news_2.content if news_2 else "",
            "news_2_veracity": news_2.veracity if news_2 else "",
            "all_platforms": platform_options,  # 改為 all_platforms 匹配模板
            "current_round": current_round,
            "player_responses": player_responses or [],
            "ai_previous_feedback": ai_previous_feedback or {},  # 新增：AI上一回合的群眾反應
            "available_tools": available_tools or []
        }

        return variables
    
    def create_ai_article(self, result_data: FakeNewsAgentResponse) -> ArticleMeta:
        return ArticleMeta(
            title=result_data.title,
            content=result_data.content,
            polished_content=None,
            image_url=result_data.image_url,
            source=result_data.source,  # 使用Agent生成的source
            author="ai",
            published_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            target_platform=getattr(result_data, 'target_platform', None),  # Agent現在會返回選擇的平台
            requirement=None,
            veracity=result_data.veracity
        )
    
    def get_platform_by_name(self, platforms, platform_name: str):
        for platform in platforms:
            if platform.name == platform_name:
                return platform
        return platforms[0] if platforms else None  # 如果找不到，返回第一個平台
