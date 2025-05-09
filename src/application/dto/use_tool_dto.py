# src/application/dto/use_tool_dto.py

from pydantic import BaseModel

class UseToolRequest(BaseModel):
    game_id: str
    tool_name: str
    user: str  # "player" 或 "agent"


class UseToolResponse(BaseModel):
    trust_score: int
    message: str
