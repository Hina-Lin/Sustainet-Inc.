# src/infrastructure/database/game_repo.py

from src.domain.models.game import GameState, Tool

# 假的 in-memory 遊戲資料庫
_fake_game_db = {
    "abc123": GameState(
        session_id="abc123",
        trust_score_player=50,
        trust_score_agent=50,
        tools_used=[]
    )
}

class GameRepository:
    @staticmethod
    def get(game_id: str) -> GameState:
        if game_id in _fake_game_db:
            return _fake_game_db[game_id]
        else:
            # 如果找不到就初始化一個新的
            game = GameState(
                session_id=game_id,
                trust_score_player=50,
                trust_score_agent=50,
                tools_used=[]
            )
            _fake_game_db[game_id] = game
            return game

    @staticmethod
    def save(game: GameState) -> None:
        _fake_game_db[game.id] = game
