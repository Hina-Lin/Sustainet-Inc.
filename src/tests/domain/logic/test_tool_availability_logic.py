"""
工具可用性邏輯的單元測試
"""
import pytest
from unittest.mock import Mock
from src.domain.logic.tool_availability_logic import ToolAvailabilityLogic
from src.domain.models.tool import DomainTool, ToolEffect


class TestToolAvailabilityLogic:
    """測試工具可用性邏輯"""
    
    def setup_method(self):
        """設置測試環境"""
        self.mock_tool_repo = Mock()
        self.tool_availability_logic = ToolAvailabilityLogic(self.mock_tool_repo)
        
        # 設置模擬工具數據
        self.mock_tools = [
            DomainTool(
                tool_name="情緒刺激",
                description="提高訊息的情緒張力和傳播力",
                applicable_to="both",
                effects=ToolEffect(trust_multiplier=1.0, spread_multiplier=1.2),
                available_from_round=1
            ),
            DomainTool(
                tool_name="AI文案優化",
                description="使用AI優化文章的說服力和清晰度",
                applicable_to="both",
                effects=ToolEffect(trust_multiplier=1.1, spread_multiplier=1.1),
                available_from_round=1
            ),
            DomainTool(
                tool_name="社群媒體分析",
                description="分析社群媒體趨勢和用戶行為",
                applicable_to="player",
                effects=ToolEffect(trust_multiplier=1.15, spread_multiplier=1.1),
                available_from_round=3
            ),
            DomainTool(
                tool_name="影片製作",  
                description="製作高質量的宣傳影片",
                applicable_to="both",
                effects=ToolEffect(trust_multiplier=1.2, spread_multiplier=1.3),
                available_from_round=3
            ),
            DomainTool(
                tool_name="專家訪談",
                description="邀請領域專家進行訪談",
                applicable_to="player",
                effects=ToolEffect(trust_multiplier=1.25, spread_multiplier=1.0),
                available_from_round=5
            )
        ]
        
        self.mock_tool_repo.list_tools_for_actor.return_value = self.mock_tools
    
    def test_tool_availability_logic_creation(self):
        """測試 ToolAvailabilityLogic 對象創建"""
        assert self.tool_availability_logic is not None
        assert hasattr(self.tool_availability_logic, 'tool_repo')
        assert hasattr(self.tool_availability_logic, 'cache_ttl')
        assert hasattr(self.tool_availability_logic, '_tool_cache')
    
    def test_round_filtering_by_available_from_round(self):
        """測試根據 available_from_round 過濾工具"""
        # 第 1 回合：應該只有 available_from_round=1 的工具
        result_round_1 = self.tool_availability_logic.get_available_tools_for_round(1, "player")
        tool_names_1 = [tool["tool_name"] for tool in result_round_1]
        expected_round_1 = ["情緒刺激", "AI文案優化"]
        assert set(tool_names_1) == set(expected_round_1)
        
        # 第 3 回合：應該包含 available_from_round <= 3 的工具
        result_round_3 = self.tool_availability_logic.get_available_tools_for_round(3, "player")
        tool_names_3 = [tool["tool_name"] for tool in result_round_3]
        expected_round_3 = ["情緒刺激", "AI文案優化", "社群媒體分析"]  # 影片製作 applicable_to="both"
        assert "情緒刺激" in tool_names_3
        assert "AI文案優化" in tool_names_3
        assert "社群媒體分析" in tool_names_3
        
        # 第 5 回合：應該包含所有工具
        result_round_5 = self.tool_availability_logic.get_available_tools_for_round(5, "player")
        tool_names_5 = [tool["tool_name"] for tool in result_round_5]
        expected_round_5 = ["情緒刺激", "AI文案優化", "社群媒體分析", "專家訪談"]
        assert set(tool_names_5) == set(expected_round_5)
    
    def test_actor_filtering(self):
        """測試角色過濾功能"""
        # 設置 AI 專用工具
        ai_tools = [
            DomainTool(
                tool_name="AI專用工具",
                description="僅AI可用的工具",
                applicable_to="ai",
                effects=ToolEffect(trust_multiplier=1.0, spread_multiplier=1.0),
                available_from_round=1
            )
        ] + self.mock_tools
        
        self.mock_tool_repo.list_tools_for_actor.return_value = ai_tools
        
        # 測試 player 不會獲得 AI 專用工具
        player_tools = self.tool_availability_logic.get_available_tools_for_round(10, "player")
        player_tool_names = [tool["tool_name"] for tool in player_tools]
        assert "AI專用工具" not in player_tool_names
    
    def test_tool_format_conversion(self):
        """測試工具格式轉換"""
        result = self.tool_availability_logic.get_available_tools_for_round(1, "player", use_cache=False)
        
        # 驗證返回格式
        assert isinstance(result, list)
        assert len(result) > 0
        
        tool = result[0]
        required_fields = ["tool_name", "description", "trust_effect", "spread_effect", "applicable_to", "available_from_round"]
        for field in required_fields:
            assert field in tool
        
        # 驗證數據類型
        assert isinstance(tool["tool_name"], str)
        assert isinstance(tool["description"], str)
        assert isinstance(tool["trust_effect"], (int, float))
        assert isinstance(tool["spread_effect"], (int, float))
        assert isinstance(tool["applicable_to"], str)
        assert isinstance(tool["available_from_round"], int)
    
    def test_cache_functionality(self):
        """測試快取功能"""
        # 第一次調用（應該調用 repository）
        result1 = self.tool_availability_logic.get_available_tools_for_round(1, "player", use_cache=True)
        
        # 第二次調用（應該使用快取）
        result2 = self.tool_availability_logic.get_available_tools_for_round(1, "player", use_cache=True)
        
        # 驗證結果一致
        assert result1 == result2
        
        # 驗證 repository 只被調用一次（第二次使用快取）
        assert self.mock_tool_repo.list_tools_for_actor.call_count == 1
        
        # 測試清除快取
        self.tool_availability_logic.clear_cache("player")
        result3 = self.tool_availability_logic.get_available_tools_for_round(1, "player", use_cache=True)
        
        # 驗證清除快取後會重新調用 repository
        assert self.mock_tool_repo.list_tools_for_actor.call_count == 2
    
    def test_get_all_available_tools_info(self):
        """測試獲取所有工具資訊功能"""
        info = self.tool_availability_logic.get_all_available_tools_info("player", use_cache=False)
        
        # 驗證返回結構
        required_keys = ["total_tools", "tools_by_round", "round_statistics", "actor", "cache_info"]
        for key in required_keys:
            assert key in info
        
        # 驗證統計資訊
        assert isinstance(info["total_tools"], int)
        assert info["total_tools"] > 0
        assert isinstance(info["tools_by_round"], dict)
        assert isinstance(info["round_statistics"], dict)
        assert info["actor"] == "player"
        assert isinstance(info["cache_info"], dict)
    
    def test_empty_tools_handling(self):
        """測試空工具列表處理"""
        self.mock_tool_repo.list_tools_for_actor.return_value = []
        
        result = self.tool_availability_logic.get_available_tools_for_round(1, "player", use_cache=False)
        assert result == []
    
    def test_disable_cache(self):
        """測試停用快取功能"""
        # 停用快取的調用
        result1 = self.tool_availability_logic.get_available_tools_for_round(1, "player", use_cache=False)
        result2 = self.tool_availability_logic.get_available_tools_for_round(1, "player", use_cache=False)
        
        # 驗證每次都調用 repository
        assert self.mock_tool_repo.list_tools_for_actor.call_count == 2
        assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__])
