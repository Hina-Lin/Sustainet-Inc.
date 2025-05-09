# src/application/dto/use_tool_dto.py

from pydantic import BaseModel

class UseToolRequest(BaseModel):
    game_id: str
    tool_name: str

class UseToolResponse(BaseModel):
    trust_score: int
    message: str
