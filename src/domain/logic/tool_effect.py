# src/domain/logic/tool_effect.py

from src.domain.models.game import GameState, Tool

# 設定各工具的基本效果（可以之後擴充為 dict + callable）
TOOL_EFFECTS = {
    "Podcast": 5,
    "AI": 2,
    "AgeRadar": 0,
    "NewsLink": 0
}

def apply_tool_effect(game: GameState, tool_name: str) -> GameState:
    # 若已使用過該工具，則不重複計算效果
    if any(tool.name == tool_name for tool in game.tools_used):
        return game

    # 計算效果
    delta = TOOL_EFFECTS.get(tool_name, 0)
    game.trust_score += delta
    game.tools_used.append(Tool(name=tool_name))
    return game
