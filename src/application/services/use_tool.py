# src/application/services/use_tool.py

from src.application.dto.use_tool_dto import UseToolRequest, UseToolResponse
from src.domain.logic.tool_effect import apply_tool_effect
from src.infrastructure.database.game_repo import GameRepository

def use_tool_service(request: UseToolRequest) -> UseToolResponse:
    game = GameRepository.get(request.game_id)
    updated_game = apply_tool_effect(game, request.tool_name, request.user)
    GameRepository.save(updated_game)
    
    return UseToolResponse(
        trust_score=updated_game.trust_score,
        message=f"Used {request.tool_name}."
    )
