"""
ActionRecord repository for database operations.
Provides synchronous CRUD operations for ActionRecord entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.infrastructure.database.base_repo import BaseRepository
from src.infrastructure.database.models.action_record import ActionRecord
from src.infrastructure.database.utils import with_session
from src.utils.exceptions import ResourceNotFoundError


class ActionRecordRepository(BaseRepository[ActionRecord]):
    """
    ActionRecord 資料庫 Repository 類，提供對 ActionRecord 的基本操作。

    用法示例:
    ```python
    repo = ActionRecordRepository()

    # 創建新紀錄
    action = repo.create_action_record(
        session_id="game123",
        round_number=1,
        actor="ai",
        platform="Facebook",
        content="這是假新聞內容...",
        reach_count=300,
        trust_change=-5,
        spread_change=10,
        effectiveness="high",
        simulated_comments=["真的假的", "好有感"]
    )

    # 查詢回合內所有行動
    actions = repo.get_actions_by_session_and_round("game123", 1)
    ```
    """

    model = ActionRecord

    @with_session
    def get_actions_by_session_and_round(
        self,
        session_id: str,
        round_number: int,
        db: Optional[Session] = None
    ) -> List[ActionRecord]:
        """
        查詢指定遊戲與回合中所有行動記錄。
        在找不到時返回空列表而非拋出例外。

        Args:
            session_id: 遊戲識別碼
            round_number: 回合編號
            db: 資料庫 Session（自動注入）

        Returns:
            該回合內所有行動記錄（可能為空列表）
        """
        return (
            db.query(self.model)
            .filter_by(session_id=session_id, round_number=round_number)
            .order_by(self.model.created_at.asc())
            .all()
        )

    @with_session
    def get_by_session_and_round(
        self,
        session_id: str,
        round_number: int,
        db: Optional[Session] = None
    ) -> List[ActionRecord]:
        """
        查詢指定遊戲與回合中所有行動記錄。

        Args:
            session_id: 遊戲識別碼
            round_number: 回合編號
            db: 資料庫 Session（自動注入）

        Returns:
            該回合內所有行動記錄

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
                message=f"No ActionRecords found for session_id='{session_id}' round={round_number}",
                resource_type="action_record",
                resource_id=f"{session_id}-{round_number}"
            )
        return result

    @with_session
    def create_action_record(
        self,
        session_id: str,
        round_number: int,
        actor: str,
        platform: str,
        content: str,
        reach_count: Optional[int] = None,
        trust_change: Optional[int] = None,
        spread_change: Optional[int] = None,
        effectiveness: Optional[str] = None,
        simulated_comments: Optional[list] = None,
        db: Optional[Session] = None
    ) -> ActionRecord:
        """
        創建一筆新的行動記錄。

        Args:
            session_id: 遊戲識別碼
            round_number: 回合數
            actor: 行動者（"player" 或 "ai"）
            platform: 發布平台名稱
            content: 行動內容
            reach_count: 預估觸及人數
            trust_change: 信任度變化
            spread_change: 傳播率變化
            effectiveness: GM 效果評分
            simulated_comments: 模擬留言（list of str）
            db: 資料庫 Session

        Returns:
            新創建的 ActionRecord 實體
        """
        return self.create(
            {
                "session_id": session_id,
                "round_number": round_number,
                "actor": actor,
                "platform": platform,
                "content": content,
                "reach_count": reach_count,
                "trust_change": trust_change,
                "spread_change": spread_change,
                "effectiveness": effectiveness,
                "simulated_comments": simulated_comments,
            },
            db=db
        )

    @with_session
    def update_effectiveness(
        self,
        action_id: int,
        trust_change: Optional[int] = None,  # 設為可選
        spread_change: Optional[int] = None,  # 設為可選
        effectiveness: Optional[str] = None,  # 設為可選
        reach_count: Optional[int] = None,  # 設為可選
        simulated_comments: Optional[list] = None,  # 設為可選
        db: Optional[Session] = None
    ):
        """
        更新行動記錄的效果評估。

        Args:
            action_id: 行動記錄的 ID
            trust_change: 信任值變化
            spread_change: 傳播率變化
            effectiveness: 效果評估（如 "Low", "Medium", "High"）
            reach_count: 預估觸及人數
            db: 資料庫 Session
        """
        action = db.query(ActionRecord).filter_by(id=action_id).first()
        if not action:
            raise ResourceNotFoundError(
                message=f"ActionRecord with id={action_id} not found",
                resource_type="action_record",
                resource_id=action_id
            )

        # 更新欄位（只有在提供值時才更新）
        if trust_change is not None:
            action.trust_change = trust_change
        if spread_change is not None:
            action.spread_change = spread_change
        if effectiveness is not None:
            action.effectiveness = effectiveness
        if reach_count is not None:
            action.reach_count = reach_count
        if simulated_comments is not None:
            action.simulated_comments = simulated_comments

        db.commit()
