from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func # Import func for SQL functions
from src.infrastructure.database.models.tools import Tool as DbTool
from src.domain.models.tool import DomainTool, ToolEffect
from src.infrastructure.database.utils import with_session

class ToolRepository:
    def __init__(self):
        pass

    def _to_domain(self, db_tool: DbTool) -> DomainTool:
        """將資料庫模型 DbTool 轉換為領域模型 DomainTool。"""
        effects = ToolEffect(
            trust_multiplier=db_tool.trust_effect if db_tool.trust_effect is not None else 1.0,
            spread_multiplier=db_tool.spread_effect if db_tool.spread_effect is not None else 1.0
        )
        return DomainTool(
            tool_name=db_tool.tool_name,
            description=db_tool.description,
            # Assuming db_tool.applicable_to is already one of "player", "ai", "both"
            applicable_to=db_tool.applicable_to, # type: ignore
            effects=effects,
            available_from_round=getattr(db_tool, 'available_from_round', 1)  # 預設第1回合
        )

    @with_session
    def get_tool_by_name(self, name: str, db: Session = None) -> Optional[DomainTool]:
        """根據工具名稱獲取工具定義（不區分大小寫）。"""
        # Convert both the stored name and the input name to lowercase for comparison
        db_tool = db.query(DbTool).filter(func.lower(DbTool.tool_name) == func.lower(name)).first()
        if db_tool:
            return self._to_domain(db_tool)
        return None

    @with_session
    def list_tools_for_actor(self, actor: str = "player", db: Session = None) -> List[DomainTool]:
        """獲取指定行動者（預設為 player）可用的所有工具。"""
        # TODO: Filter by is_active if such a field is added to DbTool
        db_tools = db.query(DbTool).filter(
            (DbTool.applicable_to == actor) | (DbTool.applicable_to == "both")
        ).all()
        return [self._to_domain(tool) for tool in db_tools]

    @with_session
    def list_all_tools(self, db: Session = None) -> List[DomainTool]:
        """獲取資料庫中定義的所有工具。"""
        db_tools = db.query(DbTool).all()
        return [self._to_domain(tool) for tool in db_tools] 