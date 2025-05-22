import random
import uuid
from typing import List
from src.domain.models.game import Game, Platform, SessionId, TrustScore, SpreadRate

class GameInitializationLogic:
    PLATFORM_NAMES = ["Facebook", "Instagram", "Thread"]
    AUDIENCE_TYPES = ["年輕族群", "中年族群", "老年族群"]
    
    def create_new_game(self) -> Game:
        session_id = SessionId(f"game_{uuid.uuid4().hex}")
        platforms = self._create_initial_platforms()
        
        return Game(
            session_id=session_id,
            current_round=1,
            platforms=platforms
        )
    
    def _create_initial_platforms(self) -> List[Platform]:
        audiences = self.AUDIENCE_TYPES.copy()
        random.shuffle(audiences)
        
        return [
            Platform(
                name=name,
                audience=audience,
                player_trust=TrustScore(50),
                ai_trust=TrustScore(50),
                spread_rate=SpreadRate(50)
            )
            for name, audience in zip(self.PLATFORM_NAMES, audiences)
        ]
