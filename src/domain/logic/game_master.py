from typing import Dict, Any, List
from src.domain.models.game import Platform
from src.application.dto.game_dto import ArticleMeta

class GameMasterLogic:
    def prepare_evaluation_variables(
        self, 
        article: ArticleMeta, 
        platform: Platform,
        all_platforms: List[Platform],
        round_number: int
    ) -> Dict[str, Any]:
        platform_summary = "\n".join([
            f"{p.name}（受眾：{p.audience}） | 玩家信任: {p.player_trust.value} | AI信任: {p.ai_trust.value} | 傳播率: {p.spread_rate.value}%"
            for p in all_platforms
        ])
        
        content = article.polished_content or article.content
        
        return {
            "title": article.title,
            "content": content,
            "image_url": article.image_url,
            "source": article.source,
            "veracity": article.veracity,
            "target_platform": platform.name,
            "author": article.author,
            "trust_multiplier": 1.0,
            "spread_multiplier": 1.0,
            "platform_state_summary": platform_summary,
            "round_number": round_number
        }
    
    def parse_gm_result(self, gm_result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "trust_change": gm_result.get("trust_change", 0),
            "reach_count": gm_result.get("reach_count", 0),
            "spread_change": gm_result.get("spread_change", 0),
            "effectiveness": gm_result.get("effectiveness", "medium"),
            "simulated_comments": gm_result.get("simulated_comments", []),
            "platform_status": gm_result.get("platform_status", [])
        }
    
    def apply_platform_updates(self, platforms: List[Platform], platform_updates: List[Dict[str, Any]]) -> None:
        for update in platform_updates:
            platform = next(
                (p for p in platforms if p.name == update["platform_name"]), 
                None
            )
            if platform:
                platform.player_trust.value = update["player_trust"]
                platform.ai_trust.value = update["ai_trust"] 
                platform.spread_rate.value = update["spread"]
