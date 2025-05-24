import random
import uuid
from typing import List
from src.domain.models.game import Game, Platform, SessionId, TrustScore, SpreadRate
from src.config.game_config import game_config

class GameInitializationLogic:
    
    def __init__(self):
        self.config = game_config
    
    def create_new_game(self) -> Game:
        session_id = SessionId(f"game_{uuid.uuid4().hex}")
        platforms = self._create_initial_platforms()
        
        return Game(
            session_id=session_id,
            current_round=1,
            platforms=platforms
        )
    
    def _create_initial_platforms(self) -> List[Platform]:
        audiences = self.config.audience_types.copy()
        random.shuffle(audiences)
        
        return [
            Platform(
                name=name,
                audience=audience,
                player_trust=TrustScore(self.config.initial_player_trust),
                ai_trust=TrustScore(self.config.initial_ai_trust),
                spread_rate=SpreadRate(self.config.initial_spread_rate)
            )
            for name, audience in zip(self.config.platform_names, audiences)
        ]
