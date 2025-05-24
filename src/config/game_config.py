"""
遊戲相關配置設定
將硬編碼的遊戲參數集中管理
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any
from dotenv import load_dotenv

# 加載 .env 檔案
load_dotenv()

@dataclass
class GameConfig:
    """
    遊戲核心配置類，統一管理遊戲參數
    
    用法示例:
    ```python
    from src.config.game_config import game_config
    
    # 檢查遊戲是否結束
    if game_config.should_game_end(round_number, platform_states):
        # 遊戲結束邏輯
        pass
    
    # 使用遊戲參數
    max_rounds = game_config.max_rounds
    win_trust_threshold = game_config.win_trust_threshold
    ```
    """
    
    # ===== 遊戲基本設定 =====
    max_rounds: int = field(default_factory=lambda: int(os.getenv("GAME_MAX_ROUNDS", "2")))
    win_trust_threshold: int = field(default_factory=lambda: int(os.getenv("GAME_WIN_TRUST_THRESHOLD", "100")))
    win_platform_count: int = field(default_factory=lambda: int(os.getenv("GAME_WIN_PLATFORM_COUNT", "3")))
    
    # ===== 初始值設定 =====
    initial_player_trust: int = field(default_factory=lambda: int(os.getenv("GAME_INITIAL_PLAYER_TRUST", "50")))
    initial_ai_trust: int = field(default_factory=lambda: int(os.getenv("GAME_INITIAL_AI_TRUST", "50")))
    initial_spread_rate: int = field(default_factory=lambda: int(os.getenv("GAME_INITIAL_SPREAD_RATE", "50")))
    
    # ===== 平台設定 =====
    platform_names: List[str] = field(default_factory=lambda: 
        os.getenv("GAME_PLATFORM_NAMES", "Facebook,Instagram,Thread").split(",")
    )
    audience_types: List[str] = field(default_factory=lambda: 
        os.getenv("GAME_AUDIENCE_TYPES", "年輕族群,中年族群,老年族群").split(",")
    )
    
    # ===== 信任值範圍設定 =====
    min_trust_value: int = field(default_factory=lambda: int(os.getenv("GAME_MIN_TRUST", "0")))
    max_trust_value: int = field(default_factory=lambda: int(os.getenv("GAME_MAX_TRUST", "100")))
    
    # ===== 傳播率範圍設定 =====
    min_spread_rate: int = field(default_factory=lambda: int(os.getenv("GAME_MIN_SPREAD", "0")))
    max_spread_rate: int = field(default_factory=lambda: int(os.getenv("GAME_MAX_SPREAD", "100")))
    
    def should_game_end(self, round_number: int, platform_states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        判斷遊戲是否應該結束
        
        Args:
            round_number: 當前回合數
            platform_states: 平台狀態列表，每個元素包含 platform_name, player_trust, ai_trust
            
        Returns:
            Dict包含: 
            - is_ended: bool - 遊戲是否結束
            - reason: str - 結束原因
            - winner: str - 獲勝者 ("player", "ai", "draw")
            - details: Dict - 詳細資訊
        """
        # 檢查回合數限制
        if round_number >= self.max_rounds:
            return self._calculate_final_winner(platform_states, "max_rounds_reached")
        
        # 檢查玩家是否達成勝利條件
        player_win_platforms = self._count_winning_platforms(platform_states, "player")
        if player_win_platforms >= self.win_platform_count:
            return {
                "is_ended": True,
                "reason": "player_dominance",
                "winner": "player",
                "details": {
                    "winning_platforms": player_win_platforms,
                    "threshold": self.win_platform_count,
                    "round_number": round_number
                }
            }
        
        # 檢查AI是否達成勝利條件
        ai_win_platforms = self._count_winning_platforms(platform_states, "ai")
        if ai_win_platforms >= self.win_platform_count:
            return {
                "is_ended": True,
                "reason": "ai_dominance", 
                "winner": "ai",
                "details": {
                    "winning_platforms": ai_win_platforms,
                    "threshold": self.win_platform_count,
                    "round_number": round_number
                }
            }
        
        # 遊戲繼續
        return {
            "is_ended": False,
            "reason": None,
            "winner": None,
            "details": {
                "round_number": round_number,
                "player_winning_platforms": player_win_platforms,
                "ai_winning_platforms": ai_win_platforms
            }
        }
    
    def _count_winning_platforms(self, platform_states: List[Dict[str, Any]], actor: str) -> int:
        """計算指定角色達到勝利門檻的平台數量"""
        count = 0
        trust_key = f"{actor}_trust"
        
        for platform in platform_states:
            if platform.get(trust_key, 0) >= self.win_trust_threshold:
                count += 1
                
        return count
    
    def _calculate_final_winner(self, platform_states: List[Dict[str, Any]], reason: str) -> Dict[str, Any]:
        """當達到最大回合數時，計算最終獲勝者"""
        player_total_trust = sum(platform.get("player_trust", 0) for platform in platform_states)
        ai_total_trust = sum(platform.get("ai_trust", 0) for platform in platform_states)
        
        if player_total_trust > ai_total_trust:
            winner = "player"
        elif ai_total_trust > player_total_trust:
            winner = "ai"  
        else:
            winner = "draw"
        
        return {
            "is_ended": True,
            "reason": reason,
            "winner": winner,
            "details": {
                "player_total_trust": player_total_trust,
                "ai_total_trust": ai_total_trust,
                "platform_details": platform_states,
                "max_rounds": self.max_rounds
            }
        }
    
    def validate_trust_value(self, value: int) -> int:
        """驗證並限制信任值在有效範圍內"""
        return max(self.min_trust_value, min(self.max_trust_value, value))
    
    def validate_spread_rate(self, value: int) -> int:
        """驗證並限制傳播率在有效範圍內"""  
        return max(self.min_spread_rate, min(self.max_spread_rate, value))
    
    def to_dict(self) -> Dict[str, Any]:
        """將遊戲配置轉換為字典"""
        return {
            "game_rules": {
                "max_rounds": self.max_rounds,
                "win_trust_threshold": self.win_trust_threshold,
                "win_platform_count": self.win_platform_count
            },
            "initial_values": {
                "player_trust": self.initial_player_trust,
                "ai_trust": self.initial_ai_trust,
                "spread_rate": self.initial_spread_rate
            },
            "platforms": {
                "names": self.platform_names,
                "audiences": self.audience_types
            },
            "value_ranges": {
                "trust": {"min": self.min_trust_value, "max": self.max_trust_value},
                "spread": {"min": self.min_spread_rate, "max": self.max_spread_rate}
            }
        }

# 全局遊戲配置實例
game_config = GameConfig()
