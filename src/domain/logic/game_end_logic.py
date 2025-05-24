"""
遊戲結束邏輯 - 負責判斷遊戲是否結束及處理結束狀態
"""
from typing import Dict, Any, List
from src.config.game_config import game_config
from src.utils.logger import logger


class GameEndLogic:
    """遊戲結束判斷邏輯 - Domain Layer"""
    
    def __init__(self):
        self.config = game_config
    
    def check_game_end_condition(
        self,
        session_id: str,
        round_number: int,
        platform_states: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        檢查遊戲是否應該結束
        
        Args:
            session_id: 遊戲會話ID
            round_number: 當前回合數
            platform_states: 平台狀態列表
            
        Returns:
            遊戲結束狀態資訊
        """
        logger.info(f"Checking game end condition", extra={
            "session_id": session_id,
            "round_number": round_number,
            "platform_count": len(platform_states)
        })
        
        # 使用配置檢查遊戲結束條件
        end_result = self.config.should_game_end(round_number, platform_states)
        
        if end_result["is_ended"]:
            logger.info(f"Game ended", extra={
                "session_id": session_id,
                "reason": end_result["reason"],
                "winner": end_result["winner"],
                "details": end_result["details"]
            })
        else:
            logger.debug(f"Game continues", extra={
                "session_id": session_id,
                "progress": end_result["details"]
            })
        
        return end_result
    
    def format_game_end_summary(self, end_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化遊戲結束摘要資訊
        
        Args:
            end_result: check_game_end_condition 的回傳結果
            
        Returns:
            格式化的遊戲結束摘要
        """
        if not end_result["is_ended"]:
            return {"summary": "遊戲進行中", "is_ended": False}
        
        reason_messages = {
            "max_rounds_reached": f"已達最大回合數 ({self.config.max_rounds} 回合)",
            "player_dominance": f"玩家在 {self.config.win_platform_count} 個平台達到 {self.config.win_trust_threshold} 信任值",
            "ai_dominance": f"AI 在 {self.config.win_platform_count} 個平台達到 {self.config.win_trust_threshold} 信任值"
        }
        
        winner_messages = {
            "player": "🎉 玩家勝利！",
            "ai": "🤖 AI 勝利！",
            "draw": "🤝 平局！"
        }
        
        reason = end_result["reason"]
        winner = end_result["winner"]
        details = end_result["details"]
        
        summary = {
            "is_ended": True,
            "winner": winner,
            "winner_message": winner_messages.get(winner, "遊戲結束"),
            "reason": reason,
            "reason_message": reason_messages.get(reason, "遊戲結束"),
            "game_statistics": self._calculate_game_statistics(details),
        }
        
        return summary
    
    def _calculate_game_statistics(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """計算遊戲統計資訊"""
        stats = {
            "total_rounds": details.get("round_number", 0),
            "max_possible_rounds": self.config.max_rounds
        }
        
        # 如果有平台詳細資訊，計算統計
        if "platform_details" in details:
            platforms = details["platform_details"]
            stats.update({
                "final_player_total_trust": sum(p.get("player_trust", 0) for p in platforms),
                "final_ai_total_trust": sum(p.get("ai_trust", 0) for p in platforms),
                "platform_breakdown": [
                    {
                        "platform": p.get("platform_name", "Unknown"),
                        "player_trust": p.get("player_trust", 0),
                        "ai_trust": p.get("ai_trust", 0),
                        "spread_rate": p.get("spread_rate", 0)
                    }
                    for p in platforms
                ]
            })
        
        # 計算勝利平台數
        if "winning_platforms" in details:
            stats["winning_platforms"] = details["winning_platforms"]
            stats["winning_threshold"] = details.get("threshold", self.config.win_platform_count)
        
        return stats
