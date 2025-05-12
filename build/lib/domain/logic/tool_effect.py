# src/domain/logic/tool_effect.py

from src.domain.models.game import GameState, Tool

# 設定各工具的基本效果（可以之後擴充為 dict + callable）
TOOL_EFFECTS = {
    "Podcast": 5,
    "AI": 2,
    "AgeRadar": 0,
    "NewsLink": 0
}

def apply_tool_effect(game: GameState, tool_name: str, user: str) -> GameState:
    # 檢查是否已使用過
    if any(tool.name == tool_name and tool.user == user for tool in game.tools_used):
        return game

    delta = TOOL_EFFECTS.get(tool_name, 0)

    # 根據使用者更新不同的 trust_score
    if user == "player":
        game.trust_score_player += delta
    elif user == "agent":
        game.trust_score_agent += delta

    # 記錄工具使用
    game.tools_used.append(Tool(name=tool_name, user=user))
    return game

