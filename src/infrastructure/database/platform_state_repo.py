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
    def get_states_by_session(
        self,
        session_id: str,
        db: Optional[Session] = None
    ) -> List[PlatformState]:
        """
        根據 session_id 取得所有平台狀態。

        Args:
            session_id: 遊戲識別碼
            db: 可選的資料庫 Session

        Returns:
            該 session_id 下所有平台的狀態列表
        """
        return db.query(PlatformState).filter_by(session_id=session_id).all()
    
    @with_session
    def get_state_by_session_round_and_platform_name(
        self,
        session_id: str,
        round_number: int,
        platform_name: str,
        db: Optional[Session] = None
    ) -> Optional[PlatformState]:  
        return db.query(PlatformState).filter_by(
            session_id=session_id,
            round_number=round_number,
            platform_name=platform_name
        ).first()

    @with_session
    def create_platform_state(
        self,
        session_id: str,
        round_number: int,
        platform_name: str,
        player_trust: Optional[int]=None,
        ai_trust: Optional[int]=None,
        spread_rate: Optional[int]=None,
        db: Optional[Session] = None 
    ) -> PlatformState:
        """
        創建一個新的平台狀態紀錄。
        如果不是第一回合，會自動從上一回合抓信任度和傳播率，否則預設 50。
        """
        if round_number > 1:
            prev_state = self.get_state_by_session_round_and_platform_name(
                session_id=session_id,
                round_number=round_number - 1,
                platform_name=platform_name,
                db=db
            )
        else:
            prev_state = None

        platform_player_trust = player_trust if player_trust is not None else (prev_state.player_trust if prev_state else 50)
        platform_ai_trust = ai_trust if ai_trust is not None else (prev_state.ai_trust if prev_state else 50)
        platform_spread_rate = spread_rate if spread_rate is not None else (prev_state.spread_rate if prev_state else 50)

        return self.create(
            {
                "session_id": session_id,
                "round_number": round_number,
                "platform_name": platform_name,
                "player_trust": platform_player_trust,
                "ai_trust": platform_ai_trust,
                "spread_rate": platform_spread_rate,
            },
            db=db
        )
        
    @with_session
    def create_all_platforms_states(
        self,
        session_id: str,
        round_number: int,
        platforms: List[dict],
        player_trust: int=None,
        ai_trust: int=None,
        spread_rate: int=None,
        db: Optional[Session] = None
    ):
        """
        一次創建所有平台的狀態紀錄。
        """
        previous_states_dict = {}
        if round_number > 1:
            try:
                previous_states = self.get_by_session_and_round(
                    session_id=session_id,
                    round_number=round_number - 1,
                    db=db
                )
                previous_states_dict = {
                    state.platform_name: state for state in previous_states
                }
            except ResourceNotFoundError:
                # 如果不是第一回合卻查不到上一回合，才 raise
                raise

        for platform in platforms:
            if "name" not in platform:
                raise ValueError("Each platform must have a 'name' key.")

            previous_state = previous_states_dict.get(platform["name"])
            platform_player_trust = player_trust if player_trust is not None else (previous_state.player_trust if previous_state else 50)
            platform_ai_trust = ai_trust if ai_trust is not None else (previous_state.ai_trust if previous_state else 50)
            platform_spread_rate = spread_rate if spread_rate is not None else (previous_state.spread_rate if previous_state else 50)

            self.create(
                {
                    "session_id": session_id,
                    "round_number": round_number,
                    "platform_name": platform["name"],
                    "player_trust": platform_player_trust,
                    "ai_trust": platform_ai_trust,
                    "spread_rate": platform_spread_rate,
                },
                db=db
            )

    @with_session
    def update_platform_state(
        self,
        session_id: str,
        round_number: int,
        platform_name: str,
        player_trust: int,
        ai_trust: int,
        spread_rate: int,
        db: Optional[Session] = None
    ):
        """
        更新指定平台的 AI 信任值與傳播率。

        Args:
            session_id: 遊戲識別碼
            round_number: 回合數
            platform_name: 平台名稱
            trust_change_ai: AI 信任值的變化量
            spread_change: 傳播率的變化量
            db: 可選的資料庫 Session

        Raises:
            ResourceNotFoundError: 如果找不到指定的 PlatformState
        """
        platform = db.query(PlatformState).filter_by(
            session_id=session_id,
            round_number=round_number,
            platform_name=platform_name
        ).first()

        if not platform:
            raise ResourceNotFoundError(
                message=f"PlatformState not found for session={session_id}, round={round_number}, platform={platform_name}",
                resource_type="platform_state",
                resource_id=f"{session_id}-{round_number}-{platform_name}"
            )

        # 這裡才是正確做法
        platform.player_trust = player_trust
        platform.ai_trust = ai_trust
        platform.spread_rate = spread_rate
        db.commit()

    
    @with_session    
    def update_all_platforms_states(
        self,
        session_id: str,
        round_number: int,
        platform_status_list: List[dict],
        db: Optional[Session] = None
    ):
        """
        批次更新所有平台狀態。
        platform_status_list: [
            {"platform_name": ..., "ai_trust": ..., "spread": ...},
            ...
        ]
        """
        for state in platform_status_list:
            self.update_platform_state(
                session_id=session_id,
                round_number=round_number,
                platform_name=state["platform_name"],
                ai_trust=state["ai_trust"],
                spread_rate=state["spread"],
                db=db
            )

