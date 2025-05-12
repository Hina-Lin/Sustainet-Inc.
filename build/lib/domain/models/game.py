# src/domain/models/game.py

from dataclasses import dataclass
from typing import List

@dataclass
class Tool:
    name: str
    user: str


@dataclass
class GameState:
    id: str
    trust_score_player: int
    trust_score_agent: int
    tools_used: List[Tool]
