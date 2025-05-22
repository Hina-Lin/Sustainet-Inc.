from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class SessionId:
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.startswith('game_'):
            raise ValueError("Invalid session ID format")

@dataclass
class TrustScore:
    value: int
    
    def __post_init__(self):
        if not 0 <= self.value <= 100:
            raise ValueError(f"Trust score must be between 0 and 100, got {self.value}")
    
    def apply_change(self, change: int) -> 'TrustScore':
        new_value = max(0, min(100, self.value + change))
        return TrustScore(new_value)

@dataclass
class SpreadRate:
    value: int
    
    def __post_init__(self):
        if not 0 <= self.value <= 100:
            raise ValueError(f"Spread rate must be between 0 and 100, got {self.value}")
    
    def apply_change(self, change: int) -> 'SpreadRate':
        new_value = max(0, min(100, self.value + change))
        return SpreadRate(new_value)

@dataclass
class Platform:
    name: str
    audience: str
    player_trust: TrustScore
    ai_trust: TrustScore
    spread_rate: SpreadRate
    
    def apply_trust_change(self, actor: str, change: int) -> None:
        if actor == "player":
            self.player_trust = self.player_trust.apply_change(change)
        elif actor == "ai":
            self.ai_trust = self.ai_trust.apply_change(change)
    
    def apply_spread_change(self, change: int) -> None:
        self.spread_rate = self.spread_rate.apply_change(change)

@dataclass
class Article:
    title: str
    content: str
    author: str
    target_platform: str
    published_date: str
    polished_content: Optional[str] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    requirement: Optional[str] = None
    veracity: Optional[str] = None

@dataclass
class ToolUsed:
    tool_name: str
    description: Optional[str] = None

@dataclass
class PlayerAction:
    article: Article
    tools_used: List[ToolUsed]

@dataclass
class ActionResult:
    trust_change: int
    reach_count: int
    spread_change: int
    effectiveness: str
    simulated_comments: List[str]

@dataclass
class Game:
    session_id: SessionId
    current_round: int
    platforms: List[Platform]
    status: str = "active"
    
    def get_platform(self, name: str) -> Optional[Platform]:
        return next((p for p in self.platforms if p.name == name), None)
    
    def increment_round(self) -> int:
        self.current_round += 1
        return self.current_round
    
    def apply_action_result(self, platform_name: str, actor: str, result: ActionResult) -> None:
        platform = self.get_platform(platform_name)
        if platform:
            platform.apply_trust_change(actor, result.trust_change)
            platform.apply_spread_change(result.spread_change)
