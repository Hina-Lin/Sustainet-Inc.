from src.domain.models.game import PlayerAction, Article, ToolUsed
from typing import List

class PlayerActionLogic:
    def create_player_action(self, request_data) -> PlayerAction:
        article = Article(
            title=request_data.article.title,
            content=request_data.article.content,
            author=request_data.article.author,
            target_platform=request_data.article.target_platform,
            published_date=request_data.article.published_date,
            polished_content=request_data.article.polished_content,
            image_url=request_data.article.image_url,
            source=request_data.article.source,
            requirement=request_data.article.requirement,
            veracity=request_data.article.veracity
        )
        
        tools_used = [
            ToolUsed(tool_name=tool.tool_name, description=tool.description)
            for tool in (request_data.tool_used or [])
        ]
        
        return PlayerAction(
            article=article,
            tools_used=tools_used
        )
