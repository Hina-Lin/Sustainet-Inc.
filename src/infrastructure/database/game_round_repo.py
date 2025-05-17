"""
GameRound repository for database operations.
Provides synchronous CRUD operations for GameRound entities.
"""

from typing import Optional
from sqlalchemy.orm import Session

from src.infrastructure.database.base_repo import BaseRepository
from src.infrastructure.database.models.game_round import GameRound
from src.infrastructure.database.utils import with_session
from src.utils.exceptions import ResourceNotFoundError


class GameRoundRepository(BaseRepository[GameRound]):
    """
    GameRound 資料庫 Repository 類，提供對 GameRound 實體的基本操作。

    用法示例:
    ```python
    repo = GameRoundRepository()

    # 查詢特定回合
    round = repo.get_by_session_and_round("game123", 1)

    # 創建一個新的回合
    round = repo.create_game_round(
        session_id="game123",
        round_number=1,
        news_id=12
    )
    ```
    """

    model = GameRound

    @with_session
    def get_by_session_and_round(
        self,
        session_id: str,
        round_number: int,
        db: Optional[Session] = None
    ) -> GameRound:
        """
        查詢指定遊戲與回合編號的回合資料。

        Args:
            session_id: 遊戲識別碼
            round_number: 回合編號
            db: 資料庫 Session（自動注入）

        Returns:
            對應的 GameRound 實體

        Raises:
            ResourceNotFoundError: 若查無資料
        """
        result = self.get_by(
            db=db,
            session_id=session_id,
            round_number=round_number
        )
        if not result:
            raise ResourceNotFoundError(
                message=f"GameRound not found for session_id='{session_id}' round={round_number}",
                resource_type="game_round",
                resource_id=f"{session_id}-{round_number}"
            )
        return result[0]

    @with_session
    def create_game_round(
        self,
        session_id: str,
        round_number: int,
        news_id: int,
        is_completed: bool = False,
        db: Optional[Session] = None
    ) -> GameRound:
        """
        創建一個新的遊戲回合。

        Args:
            session_id: 遊戲識別碼
            round_number: 回合編號（從 1 開始）
            news_id: 本回合所使用的新聞 ID
            is_completed: 是否為已完成狀態（預設 False）
            db: 資料庫 Session（自動注入）

        Returns:
            新創建的 GameRound 實體
        """
        return self.create(
            {
                "session_id": session_id,
                "round_number": round_number,
                "news_id": news_id,
                "is_completed": is_completed
            },
            db=db
        )

    @with_session
    def create_first_round(
        self,
        session_id: str,
        round_number: int,
        news_id: int,
        db: Optional[Session] = None
    ) -> GameRound:
        """
        建立第一回合的遊戲記錄。

        Args:
            session_id: 遊戲識別碼
            round_number: 回合數（通常為 1）
            news_id: 本回合所使用的新聞 ID
            db: 資料庫 Session

        Returns:
            新創建的 GameRound 實體
        """
        return self.create(
            {
                "session_id": session_id,
                "round_number": round_number,
                "news_id": news_id,
                "is_completed": False,
            },
            db=db
        )
