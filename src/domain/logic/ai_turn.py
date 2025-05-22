import random
from src.domain.models.game import Article
from src.application.dto.game_dto import ArticleMeta, FakeNewsAgentResponse
from datetime import datetime

class AiTurnLogic:
    def select_platform(self, platforms):
        return random.choice(platforms)
    
    def prepare_fake_news_variables(self, platform, news_1, news_2):
        return {
            "news_1": news_1.content,
            "news_1_veracity": news_1.veracity,
            "news_2": news_2.content,
            "news_2_veracity": news_2.veracity,
            "target_platform": platform.name,
            "target_audience": platform.audience,
            "used_tool_descriptions": "無可用工具"
        }
    
    def create_ai_article(self, result_data: FakeNewsAgentResponse, platform, source) -> ArticleMeta:
        return ArticleMeta(
            title=result_data.title,
            content=result_data.content,
            polished_content=None,
            image_url=result_data.image_url,
            source=source,
            author="ai",
            published_date=datetime.now().isoformat(),
            target_platform=platform.name,
            requirement=None,
            veracity=result_data.veracity
        )
