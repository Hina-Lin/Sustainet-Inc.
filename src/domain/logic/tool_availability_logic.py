"""
工具可用性邏輯 - 根據遊戲回合判斷可用工具
完全基於資料庫 available_from_round 欄位進行判斷，支援快取
"""
from typing import List, Dict, Any, Optional, Tuple
from src.infrastructure.database.tool_repo import ToolRepository
from src.domain.models.game import Game
from src.utils.logger import logger
import time


class ToolAvailabilityLogic:
    """
    決定基於遊戲進度（回合數）哪些工具應該對玩家可用。
    完全基於資料庫 available_from_round 欄位進行判斷。
    支援快取機制來減少資料庫查詢。
    """
    
    def __init__(self, tool_repo: ToolRepository, cache_ttl: int = 300):
        """
        Args:
            tool_repo: 工具資料存取物件
            cache_ttl: 快取存活時間（秒），預設 5 分鐘
        """
        self.tool_repo = tool_repo
        self.cache_ttl = cache_ttl
        self._tool_cache: Dict[str, Tuple[List, float]] = {}  # {actor: (tools, timestamp)}
        
    def _get_tools_with_cache(self, actor: str) -> List:
        """
        使用快取獲取工具列表，如果快取過期則重新從資料庫讀取
        
        Args:
            actor: 角色類型
            
        Returns:
            工具列表
        """
        current_time = time.time()
        
        # 檢查快取是否存在且未過期
        if actor in self._tool_cache:
            cached_tools, cache_time = self._tool_cache[actor]
            if current_time - cache_time < self.cache_ttl:
                logger.debug(f"使用快取中的 {actor} 工具資料")
                return cached_tools
        
        # 快取不存在或已過期，從資料庫重新讀取
        logger.debug(f"從資料庫讀取 {actor} 工具資料")
        tools = self.tool_repo.list_tools_for_actor(actor)
        
        # 更新快取
        self._tool_cache[actor] = (tools, current_time)
        
        return tools
        
    def clear_cache(self, actor: Optional[str] = None):
        """
        清除快取
        
        Args:
            actor: 指定清除特定角色的快取，如果為 None 則清除所有快取
        """
        if actor:
            self._tool_cache.pop(actor, None)
            logger.debug(f"已清除 {actor} 的工具快取")
        else:
            self._tool_cache.clear()
            logger.debug("已清除所有工具快取")
    
    def get_available_tools_for_round(
        self, 
        round_number: int, 
        actor: str, 
        game_state: Optional[Game] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        根據回合數和角色返回可用工具列表。
        
        Args:
            round_number: 當前遊戲回合數
            actor: "player" 或 "ai"
            game_state: 可選的遊戲狀態（目前未使用，保留擴展性）
            use_cache: 是否使用快取，預設為 True
            
        Returns:
            適合前端使用的工具字典列表
        """
        logger.debug(f"獲取 {actor} 在第 {round_number} 回合的可用工具")
        
        # 1. 獲取該角色的所有工具（使用快取）
        if use_cache:
            all_tools = self._get_tools_with_cache(actor)
        else:
            all_tools = self.tool_repo.list_tools_for_actor(actor)
        
        # 2. 根據回合數過濾工具：round_number >= available_from_round
        available_tools = [
            tool for tool in all_tools 
            if round_number >= tool.available_from_round
        ]
        
        # 3. 轉換為前端需要的格式
        tool_list = []
        for tool in available_tools:
            tool_dict = {
                "tool_name": tool.tool_name,
                "description": tool.description,
                "trust_effect": tool.effects.trust_multiplier,
                "spread_effect": tool.effects.spread_multiplier,
                "applicable_to": tool.applicable_to,
                "available_from_round": tool.available_from_round  # 新增：回傳解鎖回合資訊
            }
            tool_list.append(tool_dict)
        
        logger.debug(f"第 {round_number} 回合 {actor} 可用工具: {[t['tool_name'] for t in tool_list]}")
        return tool_list
    
    def get_all_available_tools_info(self, actor: str = "player", use_cache: bool = True) -> Dict[str, Any]:
        """
        獲取所有工具的解鎖資訊，用於前端顯示或調試。
        完全基於資料庫數據生成。
        
        Args:
            actor: 角色類型
            use_cache: 是否使用快取
            
        Returns:
            包含工具解鎖資訊的字典
        """
        if use_cache:
            all_tools = self._get_tools_with_cache(actor)
        else:
            all_tools = self.tool_repo.list_tools_for_actor(actor)
        
        # 按可用回合數分組
        tools_by_round = {}
        for tool in all_tools:
            round_key = f"round_{tool.available_from_round}_plus"
            if round_key not in tools_by_round:
                tools_by_round[round_key] = []
            tools_by_round[round_key].append({
                "tool_name": tool.tool_name,
                "description": tool.description,
                "available_from_round": tool.available_from_round
            })
        
        # 生成摘要統計
        total_tools = len(all_tools)
        round_stats = {}
        for tool in all_tools:
            round_key = tool.available_from_round
            if round_key not in round_stats:
                round_stats[round_key] = 0
            round_stats[round_key] += 1
        
        result = {
            "total_tools": total_tools,
            "tools_by_round": tools_by_round,
            "round_statistics": round_stats,  # 例如：{1: 4, 3: 2, 5: 2} 表示第1回合4個工具，第3回合2個工具等
            "actor": actor,
            "cache_info": {
                "cached": actor in self._tool_cache if use_cache else False,
                "cache_age_seconds": time.time() - self._tool_cache[actor][1] if actor in self._tool_cache else 0
            }
        }
        
        logger.debug(f"工具解鎖統計 - 總數: {total_tools}, 分佈: {round_stats}")
        return result
