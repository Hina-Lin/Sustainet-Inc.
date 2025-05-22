from typing import List
from src.domain.models.game import Game, Platform, SessionId, TrustScore, SpreadRate

class GameStateLogic:
    def rebuild_game_from_db(self, session_id: str, round_number: int, setup_data, platform_states) -> Game:
        platforms_info = setup_data.platforms
        audience_map = {p["name"]: p["audience"] for p in platforms_info}
        
        platforms = [
            Platform(
                name=state.platform_name,
                audience=audience_map.get(state.platform_name, ""),
                player_trust=TrustScore(state.player_trust),
                ai_trust=TrustScore(state.ai_trust),
                spread_rate=SpreadRate(state.spread_rate)
            )
            for state in platform_states
        ]
        
        return Game(
            session_id=SessionId(session_id),
            current_round=round_number,
            platforms=platforms
        )
    
    def convert_platforms_to_db_format(self, platforms: List[Platform]) -> List[dict]:
        return [
            {"name": p.name, "audience": p.audience} 
            for p in platforms
        ]
    
    def convert_platforms_to_dto_format(self, platforms: List[Platform]) -> List[dict]:
        return [
            {
                "platform_name": p.name,
                "player_trust": p.player_trust.value,
                "ai_trust": p.ai_trust.value,
                "spread_rate": p.spread_rate.value
            }
            for p in platforms
        ]
