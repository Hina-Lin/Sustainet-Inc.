"""
Base repository class for database operations.
Provides common asynchronous CRUD operations for all entity repositories.
"""
from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.utils.exceptions import DatabaseError, ResourceNotFoundError
from src.infrastructure.database.models.base import Base
from src.infrastructure.database.session import get_db
from src.infrastructure.database.utils import with_session

# Type variable for the entity model
T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    基礎資料庫 Repository 類，提供通用的非同步 CRUD 操作。
    
    用法示例:
    ```python
    class AgentRepository(BaseRepository[Agent]):
        model = Agent
    
    agent_repo = AgentRepository()
    agents = await agent_repo.get_all()
    agent = await agent_repo.get_by_id(1)
    ```
    """
    # 子類需要覆寫此屬性
    model: Type[Any] = None
    
    def __init__(self):
        """初始化 repository。"""
        if self.__class__.model is None:
            raise NotImplementedError("Repository class must define 'model' attribute")
    
    @with_session
    async def get_by_id(self, id: int, db: AsyncSession = None) -> T:
        """
        根據 ID 取得實體。
        
        Args:
            id: 實體 ID
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Returns:
            實體對象
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        entity = await db.get(self.model, id)
        if not entity:
            raise ResourceNotFoundError(
                message=f"{self.model.__name__} with id {id} not found",
                resource_type=self.model.__name__.lower(),
                resource_id=str(id)
            )
        return entity
    
    @with_session
    async def get_all(self, db: AsyncSession = None) -> List[T]:
        """
        取得所有實體列表。
        
        Args:
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Returns:
            實體列表
        """
        stmt = select(self.model)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @with_session
    async def get_by(self, db: AsyncSession = None, **kwargs) -> List[T]:
        """
        根據條件查詢實體。
        
        Args:
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            **kwargs: 查詢條件
            
        Returns:
            符合條件的實體列表
        """
        stmt = select(self.model)
        
        # 添加所有查詢條件
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @with_session
    async def create(self, data: Union[Dict[str, Any], T], db: AsyncSession = None) -> T:
        """
        創建新實體。
        
        Args:
            data: 實體數據或實體對象
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Returns:
            新創建的實體
        """
        # 根據輸入類型處理
        if isinstance(data, dict):
            entity = self.model(**data)
        else:
            entity = data
            
        db.add(entity)
        await db.flush()
        await db.refresh(entity)
        
        return entity
    
    @with_session
    async def update(self, id: int, data: Dict[str, Any], db: AsyncSession = None) -> T:
        """
        更新實體。
        
        Args:
            id: 實體 ID
            data: 要更新的數據
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Returns:
            更新後的實體
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        entity = await db.get(self.model, id)
        if not entity:
            raise ResourceNotFoundError(
                message=f"{self.model.__name__} with id {id} not found",
                resource_type=self.model.__name__.lower(),
                resource_id=str(id)
            )
        
        # 更新實體屬性
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        await db.flush()
        await db.refresh(entity)
        
        return entity
    
    @with_session
    async def delete(self, id: int, db: AsyncSession = None) -> None:
        """
        刪除實體。
        
        Args:
            id: 實體 ID
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        entity = await db.get(self.model, id)
        if not entity:
            raise ResourceNotFoundError(
                message=f"{self.model.__name__} with id {id} not found",
                resource_type=self.model.__name__.lower(),
                resource_id=str(id)
            )
        
        await db.delete(entity)
