"""
PlatformState repository for database operations.
Provides synchronous CRUD operations for PlatformState entities.
"""

from typing import List, Optional

from sqlalchemy.orm import Session
from src.infrastructure.database.utils import with_session

from src.infrastructure.database.base_repo import BaseRepository
from src.infrastructure.database.models.platform_state import PlatformState
from src.utils.exceptions import ResourceNotFoundError


class PlatformStateRepository(BaseRepository[PlatformState]):
    """
    PlatformState 資料庫 Repository 類，提供對 PlatformState 實體的基本操作。
    
    用法示例:
    ```python
    repo = PlatformStateRepository()

    # 查詢
    state = repo.get_by_id(1)
    all_states = repo.get_all()
    states_for_session = repo.get_by_session_and_round("game123", 1)

    # 創建
    new_state = repo.create_platform_state(
        session_id="game123",
        round_number=1,
        platform_name="Facebook",
        player_trust=50,
        ai_trust=50,
        spread_rate=60
    )
    ```
    """

    # 對應的資料庫模型
    model = PlatformState

    @with_session
    def get_by_session_and_round(
        self,
        session_id: str,
        round_number: int,
        db: Optional[Session] = None
    ) -> List[PlatformState]:
        """
        根據 session_id 與 round_number 查詢所有平台狀態。

        Args:
            session_id: 遊戲識別碼
            round_number: 回合數
            db: 可選的資料庫 Session

        Returns:
            指定回合所有平台的狀態列表

        Raises:
            ResourceNotFoundError: 如果找不到任何符合條件的紀錄
        """
        results = self.get_by(
            db=db,
            session_id=session_id,
            round_number=round_number
        )
        if not results:
            raise ResourceNotFoundError(
                message=f"No platform states found for session_id={session_id} and round_number={round_number}",
                resource_type="platform_state",
                resource_id=f"{session_id}-{round_number}"
            )
        return results

    @with_session
    def create_platform_state(
        self,
        session_id: str,
        round_number: int,
        platform_name: str,
        player_trust: int,
        ai_trust: int,
        spread_rate: int,
        db: Optional[Session] = None
    ) -> PlatformState:
        """
        創建新的平台狀態紀錄。

        Args:
            session_id: 所屬遊戲 ID
            round_number: 所屬回合數
            platform_name: 平台名稱
            player_trust: 玩家信任度（0~100）
            ai_trust: AI 信任度（0~100）
            spread_rate: 傳播率（整數百分比）
            db: 可選的資料庫 Session

        Returns:
            新創建的 PlatformState 實體
        """
        return self.create(
            {
                "session_id": session_id,
                "round_number": round_number,
                "platform_name": platform_name,
                "player_trust": player_trust,
                "ai_trust": ai_trust,
                "spread_rate": spread_rate,
            },
            db=db
        )
