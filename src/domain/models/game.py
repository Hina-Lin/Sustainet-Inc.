# src/domain/models/game.py

from dataclasses import dataclass
from typing import List

@dataclass
class Tool:
    name: str

@dataclass
class GameState:
    id: str
    trust_score: int
    tools_used: List[Tool]
