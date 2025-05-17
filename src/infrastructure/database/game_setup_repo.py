"""
GameSetup repository for database operations.
Provides synchronous CRUD operations for GameSetup entities.
"""

from typing import Optional
from sqlalchemy.orm import Session

from src.infrastructure.database.base_repo import BaseRepository
from src.infrastructure.database.models.game_setup import GameSetup
from src.infrastructure.database.utils import with_session
from src.utils.exceptions import ResourceNotFoundError


class GameSetupRepository(BaseRepository[GameSetup]):
    """
    GameSetup 資料庫 Repository 類，提供對 GameSetup 實體的基本操作。

    用法示例:
    ```python
    repo = GameSetupRepository()
    
    # 查詢
    setup = repo.get_by_session_id("game123")
    
    # 創建
    setup = repo.create_game_setup(
        session_id="game123",
        platforms=[
            {"name": "Facebook", "audience": "年輕族群"},
            {"name": "Instagram", "audience": "學生"}
        ]
    )
    ```
    """

    model = GameSetup

    @with_session
    def get_by_session_id(
        self,
        session_id: str,
        db: Optional[Session] = None
    ) -> GameSetup:
        """
        根據 session_id 查詢遊戲設置。

        Args:
            session_id: 遊戲識別碼
            db: 可選的資料庫 Session

        Returns:
            GameSetup 實體

        Raises:
            ResourceNotFoundError: 若未找到指定 session_id 對應的設定
        """
        result = self.get_by(db=db, session_id=session_id)
        if not result:
            raise ResourceNotFoundError(
                message=f"GameSetup with session_id '{session_id}' not found",
                resource_type="game_setup",
                resource_id=session_id
            )
        return result[0]

    @with_session
    def create_game_setup(
        self,
        session_id: str,
        platforms: list,
        player_initial_trust: int = 50,
        ai_initial_trust: int = 50,
        db: Optional[Session] = None
    ) -> GameSetup:
        """
        創建一筆新的遊戲設置資料。

        Args:
            session_id: 遊戲識別碼（唯一）
            platforms: 平台與受眾設定（JSON list）
            player_initial_trust: 玩家初始信任度
            ai_initial_trust: AI 初始信任度
            db: 可選的資料庫 Session

        Returns:
            新創建的 GameSetup 實體
        """
        return self.create(
            {
                "session_id": session_id,
                "platforms": platforms,
                "player_initial_trust": player_initial_trust,
                "ai_initial_trust": ai_initial_trust,
            },
            db=db
        )
