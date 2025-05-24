"""
回應轉換器 - 負責將 Domain 結果轉換為 DTO
"""
from typing import List, Dict, Any, Optional
from src.application.dto.game_dto import (
    ArticleMeta, PlatformStatus, AiTurnResponse, PlayerTurnResponse
)
from src.domain.logic.game_state_manager import GameTurnResult
from src.domain.logic.tool_availability_logic import ToolAvailabilityLogic


class ResponseConverter:
    """回應轉換器 - Application Layer"""
    
    def __init__(self, setup_repo, tool_availability_logic: ToolAvailabilityLogic):
        self.setup_repo = setup_repo
        self.tool_availability_logic = tool_availability_logic
    
    def to_turn_response(
        self, 
        game_turn_result: GameTurnResult, 
        tool_list: Optional[List[Dict[str, Any]]] = None,
        game_end_result: Optional[Dict[str, Any]] = None,
        dashboard_info: Optional[Dict[str, Any]] = None
    ):
        """轉換為回合回應 DTO"""
        turn_result = game_turn_result.turn_result
        gm_result = game_turn_result.gm_evaluation
        
        # 獲取平台設置信息
        platforms_info = self.setup_repo.get_by_session_id(turn_result.session_id).platforms
        
        # 清理文章數據（移除敏感信息）
        article_safe = self._create_safe_article(turn_result.article, turn_result.actor)
        
        # 轉換平台狀態
        platform_status_objs = self._convert_platform_status(gm_result.platform_status)
        
        # 根據回合數獲取可用工具列表（如果沒有提供的話）
        if tool_list is None:
            tool_list = self.tool_availability_logic.get_available_tools_for_round(
                round_number=turn_result.round_number,
                actor="player"  # 預設為玩家工具，因為主要是給前端顯示用
            )
        
        # 構建回應字典
        response_dict = {
            "session_id": turn_result.session_id,
            "round_number": turn_result.round_number,
            "actor": turn_result.actor,
            "article": article_safe,
            "trust_change": gm_result.trust_change,
            "reach_count": gm_result.reach_count,
            "spread_change": gm_result.spread_change,
            "platform_setup": platforms_info,
            "platform_status": platform_status_objs,
            "tool_used": turn_result.tools_used,
            "tool_list": tool_list,
            "effectiveness": gm_result.effectiveness,
            "simulated_comments": gm_result.simulated_comments
        }
        
        # 添加遊戲結束信息（如果有的話）
        if game_end_result:
            response_dict["game_end_info"] = game_end_result
        
        # 添加即時遊戲狀態（如果有的話）
        if dashboard_info:
            response_dict["dashboard_info"] = dashboard_info
        
        # 根據行動者類型返回對應的回應
        if turn_result.actor == "ai":
            return AiTurnResponse(**response_dict)
        else:
            return PlayerTurnResponse(**response_dict)
    
    def _create_safe_article(self, article: ArticleMeta, actor: str) -> ArticleMeta:
        """創建安全的文章副本（移除敏感信息）"""
        article_dict = article.model_dump()
        
        # 移除真實性信息
        article_dict["veracity"] = None
        
        # AI 回合不顯示目標平台
        if actor == "ai":
            article_dict["target_platform"] = None
        
        return ArticleMeta.model_validate(article_dict)
    
    def _convert_platform_status(self, platform_status_list) -> List[Dict[str, Any]]:
        """轉換平台狀態列表"""
        return [
            PlatformStatus(
                platform_name=ps.platform_name,
                player_trust=ps.player_trust,
                ai_trust=ps.ai_trust,
                spread_rate=ps.spread_rate
            ).model_dump() for ps in platform_status_list
        ]
