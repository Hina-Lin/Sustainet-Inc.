from sqlalchemy.orm import Session
from typing import List
from src.infrastructure.database.models.toolusage import ToolUsage as DbToolUsage
from src.domain.models.tool import AppliedToolEffectDetail # Using the domain model for details
from src.infrastructure.database.utils import with_session # Import the decorator

class ToolUsageRepository:
    # __init__ no longer takes db_session
    def __init__(self):
        pass

    @with_session # Apply decorator
    def create_tool_usage_record(
        self, 
        action_id: int, 
        usage_detail: AppliedToolEffectDetail,
        db: Session = None # Add db param
    ) -> DbToolUsage:
        """創建一條工具使用記錄。"""
        db_record = DbToolUsage(
            action_id=action_id,
            tool_name=usage_detail.tool_name,
            trust_effect=usage_detail.applied_trust_effect_value,
            spread_effect=usage_detail.applied_spread_effect_value,
            is_effective=usage_detail.is_effective
        )
        db.add(db_record)
        # A flush might be needed here if the caller needs the id of db_record immediately
        # and before the session managed by @with_session commits.
        # db.flush() 
        # db.refresh(db_record) # To get generated values like id
        return db_record
    
    @with_session
    def get_by_action_id(self, action_id: int, db: Session = None) -> List[DbToolUsage]:
        """取得指定行動的所有工具使用記錄。"""
        return db.query(DbToolUsage).filter_by(action_id=action_id).all() 