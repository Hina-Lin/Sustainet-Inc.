"""
遊戲狀態管理邏輯 - 負責遊戲狀態的重建、持久化等操作
"""
from typing import Dict, Any, List
from src.application.dto.game_dto import GameMasterAgentResponse
from src.domain.logic.turn_execution import TurnExecutionResult
from src.domain.models.tool import AppliedToolEffectDetail, DomainTool
from src.utils.logger import logger


class GameTurnResult:
    """完整的回合結果，包含 GM 評估和工具效果"""
    def __init__(
        self,
        turn_result: TurnExecutionResult,
        gm_evaluation: GameMasterAgentResponse,
        tool_effects: List[AppliedToolEffectDetail]
    ):
        self.turn_result = turn_result
        self.gm_evaluation = gm_evaluation
        self.tool_effects = tool_effects


class GameStateManager:
    """遊戲狀態管理器 - Domain Layer"""
    
    def __init__(
        self, 
        setup_repo, 
        state_repo, 
        action_repo, 
        tool_usage_repo,
        game_state_logic,
        gm_logic,
        tool_effect_logic,
        agent_factory
    ):
        self.setup_repo = setup_repo
        self.state_repo = state_repo
        self.action_repo = action_repo
        self.tool_usage_repo = tool_usage_repo
        self.game_state_logic = game_state_logic
        self.gm_logic = gm_logic
        self.tool_effect_logic = tool_effect_logic
        self.agent_factory = agent_factory
    
    def rebuild_game_state(self, session_id: str, round_number: int):
        """重建遊戲狀態"""
        setup_data = self.setup_repo.get_by_session_id(session_id)
        platform_states = self.state_repo.get_by_session_and_round(session_id, round_number)
        return self.game_state_logic.rebuild_game_from_db(session_id, round_number, setup_data, platform_states)
    
    def evaluate_and_apply_effects(
        self, 
        turn_result: TurnExecutionResult,
        game,
        tool_repo
    ) -> GameTurnResult:
        """評估回合效果並應用工具"""
        
        # 1. 獲取原始 GM 評估
        original_gm_result = self._get_gm_evaluation(
            game, 
            turn_result.article, 
            turn_result.target_platform, 
            turn_result.round_number
        )
        
        logger.debug(f"Original GM evaluation for {turn_result.actor}", extra={
            "session_id": turn_result.session_id, 
            "round": turn_result.round_number, 
            "gm_result": original_gm_result.model_dump()
        })
        
        # 2. 應用工具效果
        final_gm_result = original_gm_result
        tool_effects = []
        
        if turn_result.tools_used:
            domain_tools = self._get_applicable_tools(
                turn_result.tools_used, 
                turn_result.actor, 
                tool_repo,
                turn_result.session_id,
                turn_result.round_number
            )
            
            if domain_tools:
                final_gm_result, tool_effects = self.tool_effect_logic.apply_effects(
                    original_gm_result, domain_tools
                )
                logger.info(f"Applied {len(domain_tools)} tools for {turn_result.actor}", extra={
                    "session_id": turn_result.session_id,
                    "round": turn_result.round_number,
                    "tools": [t.tool_name for t in domain_tools]
                })
        
        return GameTurnResult(turn_result, final_gm_result, tool_effects)
    
    def persist_turn_result(self, game_turn_result: GameTurnResult) -> int:
        """持久化回合結果，返回 action_id"""
        turn_result = game_turn_result.turn_result
        gm_result = game_turn_result.gm_evaluation
        
        # 1. 記錄行動
        action_record = self.action_repo.create_action_record(
            session_id=turn_result.session_id,
            round_number=turn_result.round_number,
            actor=turn_result.actor,
            platform=turn_result.target_platform,
            content=turn_result.article.content
        )
        
        # 2. 更新行動效果
        self.action_repo.update_effectiveness(
            action_id=action_record.id,
            trust_change=gm_result.trust_change,
            spread_change=gm_result.spread_change,
            reach_count=gm_result.reach_count,
            effectiveness=gm_result.effectiveness,
            simulated_comments=gm_result.simulated_comments
        )
        
        # 3. 更新平台狀態
        for state in gm_result.platform_status:
            self.state_repo.update_platform_state(
                session_id=turn_result.session_id,
                round_number=turn_result.round_number,
                platform_name=state.platform_name,
                player_trust=state.player_trust,
                ai_trust=state.ai_trust,
                spread_rate=state.spread_rate
            )
        
        # 4. 記錄工具使用
        for tool_effect in game_turn_result.tool_effects:
            if tool_effect.is_effective:
                self.tool_usage_repo.create_tool_usage_record(
                    action_id=action_record.id,
                    usage_detail=tool_effect
                )
                logger.debug(f"Recorded tool usage: {tool_effect.tool_name}", extra={
                    "session_id": turn_result.session_id,
                    "action_id": action_record.id
                })
        
        # 5. 標記玩家回合完成
        if turn_result.actor == "player":
            # 這個邏輯應該由上層的 round_repo 處理，但為了保持一致性暫時放在這裡
            pass
        
        logger.info(f"Persisted {turn_result.actor} turn result", extra={
            "session_id": turn_result.session_id,
            "round": turn_result.round_number,
            "action_id": action_record.id
        })
        
        return action_record.id
    
    def _get_gm_evaluation(self, game, article, target_platform, round_number) -> GameMasterAgentResponse:
        """獲取 GM 評估"""
        target_platform_obj = game.get_platform(target_platform)
        variables = self.gm_logic.prepare_evaluation_variables(
            article, target_platform_obj, game.platforms, round_number
        )
        
        gm_response: GameMasterAgentResponse = self.agent_factory.run_agent_by_name(
            session_id=game.session_id.value,
            agent_name="game_master_agent",
            variables=variables,
            input_text="input_text",
            response_model=GameMasterAgentResponse
        )
        
        return gm_response
    
    def _get_applicable_tools(
        self, 
        tools_used: List, 
        actor: str, 
        tool_repo,
        session_id: str,
        round_number: int
    ) -> List[DomainTool]:
        """獲取適用的工具列表"""
        domain_tools = []
        
        for tool_dto in tools_used:
            domain_tool = tool_repo.get_tool_by_name(tool_dto.tool_name)
            
            if domain_tool and (domain_tool.applicable_to == actor or domain_tool.applicable_to == "both"):
                domain_tools.append(domain_tool)
                logger.debug(f"Tool '{tool_dto.tool_name}' applicable for {actor}", extra={
                    "session_id": session_id,
                    "round": round_number
                })
            else:
                logger.warning(f"{actor.capitalize()} attempted to use invalid tool: '{tool_dto.tool_name}'", extra={
                    "session_id": session_id,
                    "round": round_number
                })
        
        return domain_tools
