"""
回合執行邏輯 - 負責處理 AI 和玩家的行動執行
"""
from typing import Dict, Any, Optional, List
from src.application.dto.game_dto import ArticleMeta, ToolUsed, FakeNewsAgentResponse, SimulateCommentsRequest
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
        agent_response: Optional[FakeNewsAgentResponse] = None,
        simulated_comments: Optional[List[str]] = None  
    ):
        self.actor = actor
        self.session_id = session_id
        self.round_number = round_number
        self.article = article
        self.target_platform = target_platform
        self.tools_used = tools_used
        self.agent_response = agent_response
        self.simulated_comments = simulated_comments


class TurnExecutionLogic:
    """回合執行邏輯 - Domain Layer"""
    
    def __init__(self, ai_turn_logic, tool_repo, agent_factory, news_repo, simulate_comments_logic, action_repo):
        self.ai_turn_logic = ai_turn_logic
        self.tool_repo = tool_repo
        self.agent_factory = agent_factory
        self.news_repo = news_repo
        self.simulate_comments_logic = simulate_comments_logic
        self.action_repo = action_repo  # 新增：用於獲取玩家歷史回應
    
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
        
        # 獲取玩家歷史回應
        player_responses = self._get_player_responses(session_id, round_number)
        
        # 獲取並格式化 AI 可用工具
        all_ai_tools_from_repo = self.tool_repo.list_tools_for_actor(actor="ai")
        
        # 根據當前回合數過濾工具
        unlocked_ai_tools = [
            tool for tool in all_ai_tools_from_repo
            if round_number >= getattr(tool, 'available_from_round', 1) # 假設若無此屬性則預設第一回合可用
        ]
        
        formatted_available_tools = [
            {
                "tool_name": tool.tool_name,
                "description": tool.description
                # 如果 AI Agent 的 prompt 需要 applicable_to，也可以在這裡加上
                # "applicable_to": tool.applicable_to 
            }
            for tool in unlocked_ai_tools # 使用過濾後的工具列表
        ]

        # 準備變數（現在包含玩家歷史和格式化後的可用工具）
        variables = self.ai_turn_logic.prepare_fake_news_variables(
            platform=selected_platform, 
            news_1=news_1, 
            news_2=news_2,
            player_responses=player_responses,
            current_round=round_number,
            available_tools=formatted_available_tools # 傳遞格式化後的工具列表
        )
        
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
        
        # 產生模擬留言
        sim_req = SimulateCommentsRequest(
            session_id=session_id,
            article=article,
            actor="ai",
            round_number=round_number,
            platform=selected_platform.name,
            audience=selected_platform.audience
        )
        sim_resp = self.simulate_comments_logic.generate_comments(sim_req)
        simulated_comments = sim_resp.comments if sim_resp else []
        
        return TurnExecutionResult(
            actor="ai",
            session_id=session_id,
            round_number=round_number,
            article=article,
            target_platform=selected_platform.name,
            tools_used=tools_used,
            agent_response=agent_output,
            simulated_comments=simulated_comments
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
        audience = None
        if not target_platform:
            available_platforms = [p.name for p in game.platforms]
            target_platform = available_platforms[0] if available_platforms else "Facebook"
            article.target_platform = target_platform
            
            logger.warning(f"Player article missing target_platform, defaulting to {target_platform}")
        
        for p in game.platforms:
            if p.name == target_platform:
                audience = getattr(p, 'audience', None)
                break
            
        logger.info(f"Player used tools: {[t.tool_name for t in player_tools]}", extra={
            "session_id": session_id, 
            "round_number": round_number
        })
        
        # 產生模擬留言
        sim_req = SimulateCommentsRequest(
            session_id=session_id,
            article=article,
            actor="player",
            round_number=round_number,
            platform=target_platform,
            audience=audience
        )
        sim_resp = self.simulate_comments_logic.generate_comments(sim_req)
        simulated_comments = sim_resp.comments if sim_resp else []
        
        return TurnExecutionResult(
            actor="player",
            session_id=session_id,
            round_number=round_number,
            article=article,
            target_platform=target_platform,
            tools_used=player_tools,
            simulated_comments=simulated_comments
        )
    
    def _get_player_responses(self, session_id: str, current_round: int) -> List[Dict[str, Any]]:
        """
        獲取玩家的歷史回應記錄
        
        Args:
            session_id: 遊戲會話ID
            current_round: 當前回合數
            
        Returns:
            玩家回應記錄列表
        """
        try:
            # 獲取當前回合之前的所有玩家行動
            player_actions = self.action_repo.get_player_actions_before_round(
                session_id=session_id,
                before_round=current_round
            )
            
            if not player_actions:
                logger.info(f"No player responses found for session {session_id} before round {current_round}")
                return []
            
            # 轉換為字典格式
            responses = []
            for action in player_actions:
                response_dict = {
                    'round_number': action.round_number,
                    'platform': action.platform,
                    'title': action.title,
                    'content': action.content,
                    'effectiveness': action.effectiveness,
                    'trust_change': action.trust_change,
                    'spread_change': action.spread_change,
                    'reach_count': action.reach_count,
                    'simulated_comments': action.simulated_comments if action.simulated_comments else []
                }
                responses.append(response_dict)
            
            logger.info(f"Retrieved {len(responses)} player responses for AI analysis", extra={
                "session_id": session_id,
                "current_round": current_round,
                "player_responses_count": len(responses)
            })
            
            return responses
            
        except Exception as e:
            logger.error(f"Failed to retrieve player responses: {str(e)}", extra={
                "session_id": session_id,
                "current_round": current_round
            })
            return []
