"""
回合執行邏輯 - 負責處理 AI 和玩家的行動執行
"""
from typing import Dict, Any, Optional, List
from src.application.dto.game_dto import ArticleMeta, ToolUsed, FakeNewsAgentResponse
from src.domain.models.game import Game
from src.utils.logger import logger


class TurnExecutionResult:
    """回合執行結果的統一數據結構"""
    def __init__(
        self,
        actor: str,
        session_id: str,
        round_number: int,
        article: ArticleMeta,
        target_platform: str,
        tools_used: List[ToolUsed],
        agent_response: Optional[FakeNewsAgentResponse] = None
    ):
        self.actor = actor
        self.session_id = session_id
        self.round_number = round_number
        self.article = article
        self.target_platform = target_platform
        self.tools_used = tools_used
        self.agent_response = agent_response


class TurnExecutionLogic:
    """回合執行邏輯 - Domain Layer"""
    
    def __init__(self, ai_turn_logic, tool_repo, agent_factory, news_repo):
        self.ai_turn_logic = ai_turn_logic
        self.tool_repo = tool_repo
        self.agent_factory = agent_factory
        self.news_repo = news_repo
    
    def execute_actor_turn(
        self, 
        game: Game, 
        actor: str, 
        session_id: str, 
        round_number: int,
        article: Optional[ArticleMeta] = None,
        player_tools: Optional[List[ToolUsed]] = None
    ) -> TurnExecutionResult:
        """
        執行行動者的回合
        """
        logger.info(f"Executing {actor} turn", extra={
            "session_id": session_id, 
            "round_number": round_number
        })
        
        if actor == "ai":
            return self._execute_ai_action(game, session_id, round_number)
        elif actor == "player":
            return self._execute_player_action(
                game, session_id, round_number, article, player_tools or []
            )
        else:
            raise ValueError(f"Unknown actor: {actor}")
    
    def _execute_ai_action(
        self, 
        game: Game, 
        session_id: str, 
        round_number: int
    ) -> TurnExecutionResult:
        """執行 AI 行動"""
        # 選擇平台
        selected_platform = self.ai_turn_logic.select_platform(game.platforms)
        
        # 獲取新聞來源
        news_1 = self.news_repo.get_random_active_news()
        news_2 = self.news_repo.get_random_active_news()
        
        # 準備變數
        variables = self.ai_turn_logic.prepare_fake_news_variables(
            platform=selected_platform, 
            news_1=news_1, 
            news_2=news_2
        )
        
        # 添加可用工具
        available_tools = self.tool_repo.list_tools_for_actor(actor="ai")
        variables["available_tools"] = [
            {
                "tool_name": tool.tool_name,
                "description": tool.description,
                "applicable_to": tool.applicable_to
            }
            for tool in available_tools
        ]
        
        # 調用 AI Agent
        agent_output: FakeNewsAgentResponse = self.agent_factory.run_agent_by_name(
            session_id=session_id,
            agent_name="fake_news_agent",
            variables=variables,
            input_text="input_text",
            response_model=FakeNewsAgentResponse
        )
        
        # 創建文章
        article = self.ai_turn_logic.create_ai_article(
            result_data=agent_output,
            platform=selected_platform,
            source=news_1.source
        )
        
        # 解析 AI 使用的工具
        tools_used = agent_output.tool_used or []
        
        logger.info(f"AI used tools: {[t.tool_name for t in tools_used]}", extra={
            "session_id": session_id, 
            "round_number": round_number
        })
        
        return TurnExecutionResult(
            actor="ai",
            session_id=session_id,
            round_number=round_number,
            article=article,
            target_platform=selected_platform.name,
            tools_used=tools_used,
            agent_response=agent_output
        )
    
    def _execute_player_action(
        self,
        game: Game,
        session_id: str,
        round_number: int,
        article: ArticleMeta,
        player_tools: List[ToolUsed]
    ) -> TurnExecutionResult:
        """執行玩家行動"""
        if not article:
            raise ValueError("Player article is required")
        
        # 確保目標平台存在
        target_platform = article.target_platform
        if not target_platform:
            available_platforms = [p.name for p in game.platforms]
            target_platform = available_platforms[0] if available_platforms else "Facebook"
            article.target_platform = target_platform
            
            logger.warning(f"Player article missing target_platform, defaulting to {target_platform}")
        
        logger.info(f"Player used tools: {[t.tool_name for t in player_tools]}", extra={
            "session_id": session_id, 
            "round_number": round_number
        })
        
        return TurnExecutionResult(
            actor="player",
            session_id=session_id,
            round_number=round_number,
            article=article,
            target_platform=target_platform,
            tools_used=player_tools
        )
