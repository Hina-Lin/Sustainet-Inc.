"""
遊戲結束邏輯測試
"""
import pytest
from src.domain.logic.game_end_logic import GameEndLogic
from src.config.game_config import GameConfig


class TestGameEndLogic:
    """測試遊戲結束邏輯"""
    
    def setup_method(self):
        """設置測試環境"""
        # 使用測試專用配置
        test_config = GameConfig()
        test_config.max_rounds = 10
        test_config.win_trust_threshold = 100
        test_config.win_platform_count = 3
        
        self.game_end_logic = GameEndLogic()
        self.game_end_logic.config = test_config  # 注入測試配置
    
    def test_game_continues_normal_situation(self):
        """測試正常情況下遊戲繼續"""
        platform_states = [
            {"platform_name": "Facebook", "player_trust": 60, "ai_trust": 40, "spread_rate": 50},
            {"platform_name": "Instagram", "player_trust": 55, "ai_trust": 45, "spread_rate": 60},
            {"platform_name": "Thread", "player_trust": 50, "ai_trust": 50, "spread_rate": 50}
        ]
        
        result = self.game_end_logic.check_game_end_condition(
            session_id="test_game",
            round_number=5,
            platform_states=platform_states
        )
        
        assert result["is_ended"] is False
        assert result["winner"] is None
        assert result["reason"] is None
    
    def test_game_ends_max_rounds_reached(self):
        """測試達到最大回合數時遊戲結束"""
        platform_states = [
            {"platform_name": "Facebook", "player_trust": 60, "ai_trust": 40, "spread_rate": 50},
            {"platform_name": "Instagram", "player_trust": 55, "ai_trust": 45, "spread_rate": 60},
            {"platform_name": "Thread", "player_trust": 50, "ai_trust": 50, "spread_rate": 50}
        ]
        
        result = self.game_end_logic.check_game_end_condition(
            session_id="test_game",
            round_number=10,  # 達到最大回合數
            platform_states=platform_states
        )
        
        assert result["is_ended"] is True
        assert result["reason"] == "max_rounds_reached"
        assert result["winner"] == "player"  # 玩家總信任值較高
    
    def test_player_wins_by_dominance(self):
        """測試玩家通過平台主導獲勝"""
        platform_states = [
            {"platform_name": "Facebook", "player_trust": 100, "ai_trust": 30, "spread_rate": 50},
            {"platform_name": "Instagram", "player_trust": 100, "ai_trust": 35, "spread_rate": 60},
            {"platform_name": "Thread", "player_trust": 100, "ai_trust": 40, "spread_rate": 50}
        ]
        
        result = self.game_end_logic.check_game_end_condition(
            session_id="test_game",
            round_number=5,
            platform_states=platform_states
        )
        
        assert result["is_ended"] is True
        assert result["reason"] == "player_dominance"
        assert result["winner"] == "player"
        assert result["details"]["winning_platforms"] == 3
    
    def test_ai_wins_by_dominance(self):
        """測試AI通過平台主導獲勝"""
        platform_states = [
            {"platform_name": "Facebook", "player_trust": 30, "ai_trust": 100, "spread_rate": 50},
            {"platform_name": "Instagram", "player_trust": 35, "ai_trust": 100, "spread_rate": 60},
            {"platform_name": "Thread", "player_trust": 40, "ai_trust": 100, "spread_rate": 50}
        ]
        
        result = self.game_end_logic.check_game_end_condition(
            session_id="test_game",
            round_number=5,
            platform_states=platform_states
        )
        
        assert result["is_ended"] is True
        assert result["reason"] == "ai_dominance"
        assert result["winner"] == "ai"
        assert result["details"]["winning_platforms"] == 3
    
    def test_draw_at_max_rounds(self):
        """測試最大回合數時平局"""
        platform_states = [
            {"platform_name": "Facebook", "player_trust": 50, "ai_trust": 50, "spread_rate": 50},
            {"platform_name": "Instagram", "player_trust": 50, "ai_trust": 50, "spread_rate": 60},
            {"platform_name": "Thread", "player_trust": 50, "ai_trust": 50, "spread_rate": 50}
        ]
        
        result = self.game_end_logic.check_game_end_condition(
            session_id="test_game",
            round_number=10,  # 達到最大回合數
            platform_states=platform_states
        )
        
        assert result["is_ended"] is True
        assert result["reason"] == "max_rounds_reached"
        assert result["winner"] == "draw"  # 總信任值相等
    
    def test_format_game_end_summary(self):
        """測試遊戲結束摘要格式化"""
        end_result = {
            "is_ended": True,
            "reason": "player_dominance",
            "winner": "player",
            "details": {
                "winning_platforms": 3,
                "threshold": 3,
                "round_number": 7
            }
        }
        
        summary = self.game_end_logic.format_game_end_summary(end_result)
        
        assert summary["is_ended"] is True
        assert summary["winner"] == "player"
        assert summary["winner_message"] == "🎉 玩家勝利！"
        assert "玩家在 3 個平台達到 100 信任值" in summary["reason_message"]
        assert summary["game_statistics"]["total_rounds"] == 7


if __name__ == "__main__":
    # 簡單運行測試
    test = TestGameEndLogic()
    test.setup_method()
    
    print("測試遊戲繼續...")
    test.test_game_continues_normal_situation()
    print("✅ 通過")
    
    print("測試達到最大回合數...")
    test.test_game_ends_max_rounds_reached()
    print("✅ 通過")
    
    print("測試玩家主導獲勝...")
    test.test_player_wins_by_dominance()
    print("✅ 通過")
    
    print("測試AI主導獲勝...")
    test.test_ai_wins_by_dominance()
    print("✅ 通過")
    
    print("測試平局...")
    test.test_draw_at_max_rounds()
    print("✅ 通過")
    
    print("測試摘要格式化...")
    test.test_format_game_end_summary()
    print("✅ 通過")
    
    print("\n🎉 所有測試通過！")
