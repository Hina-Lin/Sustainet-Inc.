"""
Base repository class for database operations.
Provides common CRUD operations for all entity repositories.
Supports both synchronous and asynchronous operations.
"""
from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Union

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.utils.exceptions import DatabaseError, ResourceNotFoundError
from src.infrastructure.database.models.base import Base
from src.infrastructure.database.session import db_session

# Type variable for the entity model
T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    基礎資料庫 Repository 類，提供通用的 CRUD 操作。
    支援同步和異步操作，使用統一的 session 管理。
    
    用法示例:
    ```python
    # 同步操作
    class AgentRepository(BaseRepository[Agent]):
        model = Agent
    
    agent_repo = AgentRepository()
    agents = agent_repo.get_all()
    agent = agent_repo.get_by_id(1)
    
    # 異步操作
    agents = await agent_repo.async_get_all()
    agent = await agent_repo.async_get_by_id(1)
    ```
    """
    # 子類需要覆寫此屬性
    model: Type[Any] = None
    
    def __init__(self):
        """初始化 repository。"""
        if self.__class__.model is None:
            raise NotImplementedError("Repository class must define 'model' attribute")
    
    def get_by_id(self, id: int, db: Session = None) -> T:
        """
        根據 ID 取得實體（同步）。
        
        Args:
            id: 實體 ID
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Returns:
            實體對象
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        if db is not None:
            # 使用傳入的 session
            entity = db.get(self.model, id)
            if not entity:
                raise ResourceNotFoundError(
                    message=f"{self.model.__name__} with id {id} not found",
                    resource_type=self.model.__name__.lower(),
                    resource_id=str(id)
                )
            return entity
        else:
            # 使用上下文管理器自動管理 session
            with db_session.session() as session:
                entity = session.get(self.model, id)
                if not entity:
                    raise ResourceNotFoundError(
                        message=f"{self.model.__name__} with id {id} not found",
                        resource_type=self.model.__name__.lower(),
                        resource_id=str(id)
                    )
                return entity
    
    async def async_get_by_id(self, id: int, db: AsyncSession = None) -> T:
        """
        根據 ID 取得實體（異步）。
        
        Args:
            id: 實體 ID
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Returns:
            實體對象
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        if db is not None:
            # 使用傳入的 session
            entity = await db.get(self.model, id)
            if not entity:
                raise ResourceNotFoundError(
                    message=f"{self.model.__name__} with id {id} not found",
                    resource_type=self.model.__name__.lower(),
                    resource_id=str(id)
                )
            return entity
        else:
            # 使用異步 session
            async with db_session.get_async_session() as session:
                entity = await session.get(self.model, id)
                if not entity:
                    raise ResourceNotFoundError(
                        message=f"{self.model.__name__} with id {id} not found",
                        resource_type=self.model.__name__.lower(),
                        resource_id=str(id)
                    )
                return entity
    
    def get_all(self, db: Session = None) -> List[T]:
        """
        取得所有實體列表（同步）。
        
        Args:
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Returns:
            實體列表
        """
        if db is not None:
            # 使用傳入的 session
            stmt = select(self.model)
            return list(db.execute(stmt).scalars().all())
        else:
            # 使用上下文管理器自動管理 session
            with db_session.session() as session:
                stmt = select(self.model)
                return list(session.execute(stmt).scalars().all())
    
    async def async_get_all(self, db: AsyncSession = None) -> List[T]:
        """
        取得所有實體列表（異步）。
        
        Args:
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Returns:
            實體列表
        """
        if db is not None:
            # 使用傳入的 session
            stmt = select(self.model)
            result = await db.execute(stmt)
            return list(result.scalars().all())
        else:
            # 使用異步 session
            async with db_session.get_async_session() as session:
                stmt = select(self.model)
                result = await session.execute(stmt)
                return list(result.scalars().all())
    
    def get_by(self, db: Session = None, **kwargs) -> List[T]:
        """
        根據條件查詢實體（同步）。
        
        Args:
            db: 可選的數據庫 Session，如果未提供則自動創建
            **kwargs: 查詢條件
            
        Returns:
            符合條件的實體列表
        """
        stmt = select(self.model)
        
        # 添加所有查詢條件
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
        
        if db is not None:
            # 使用傳入的 session
            return list(db.execute(stmt).scalars().all())
        else:
            # 使用上下文管理器自動管理 session
            with db_session.session() as session:
                return list(session.execute(stmt).scalars().all())
    
    async def async_get_by(self, db: AsyncSession = None, **kwargs) -> List[T]:
        """
        根據條件查詢實體（異步）。
        
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
        
        if db is not None:
            # 使用傳入的 session
            result = await db.execute(stmt)
            return list(result.scalars().all())
        else:
            # 使用異步 session
            async with db_session.get_async_session() as session:
                result = await session.execute(stmt)
                return list(result.scalars().all())
    
    def create(self, data: Union[Dict[str, Any], T], db: Session = None) -> T:
        """
        創建新實體（同步）。
        
        Args:
            data: 實體數據或實體對象
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Returns:
            新創建的實體
        """
        # 根據輸入類型處理
        if isinstance(data, dict):
            entity = self.model(**data)
        else:
            entity = data
            
        if db is not None:
            # 使用傳入的 session
            db.add(entity)
            db.flush()
            db.refresh(entity)
            return entity
        else:
            # 使用上下文管理器自動管理 session
            with db_session.session() as session:
                session.add(entity)
                session.flush()
                session.refresh(entity)
                return entity
    
    async def async_create(self, data: Union[Dict[str, Any], T], db: AsyncSession = None) -> T:
        """
        創建新實體（異步）。
        
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
            
        if db is not None:
            # 使用傳入的 session
            db.add(entity)
            await db.flush()
            await db.refresh(entity)
            return entity
        else:
            # 使用異步 session
            async with db_session.get_async_session() as session:
                session.add(entity)
                await session.flush()
                await session.refresh(entity)
                return entity
    
    def update(self, id: int, data: Dict[str, Any], db: Session = None) -> T:
        """
        更新實體（同步）。
        
        Args:
            id: 實體 ID
            data: 要更新的數據
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Returns:
            更新後的實體
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        if db is not None:
            # 使用傳入的 session
            entity = db.get(self.model, id)
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
            
            db.flush()
            db.refresh(entity)
            return entity
        else:
            # 使用上下文管理器自動管理 session
            with db_session.session() as session:
                entity = session.get(self.model, id)
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
                
                session.flush()
                session.refresh(entity)
                return entity
    
    async def async_update(self, id: int, data: Dict[str, Any], db: AsyncSession = None) -> T:
        """
        更新實體（異步）。
        
        Args:
            id: 實體 ID
            data: 要更新的數據
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Returns:
            更新後的實體
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        if db is not None:
            # 使用傳入的 session
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
        else:
            # 使用異步 session
            async with db_session.get_async_session() as session:
                entity = await session.get(self.model, id)
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
                
                await session.flush()
                await session.refresh(entity)
                return entity
    
    def delete(self, id: int, db: Session = None) -> None:
        """
        刪除實體（同步）。
        
        Args:
            id: 實體 ID
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        if db is not None:
            # 使用傳入的 session
            entity = db.get(self.model, id)
            if not entity:
                raise ResourceNotFoundError(
                    message=f"{self.model.__name__} with id {id} not found",
                    resource_type=self.model.__name__.lower(),
                    resource_id=str(id)
                )
            
            db.delete(entity)
        else:
            # 使用上下文管理器自動管理 session
            with db_session.session() as session:
                entity = session.get(self.model, id)
                if not entity:
                    raise ResourceNotFoundError(
                        message=f"{self.model.__name__} with id {id} not found",
                        resource_type=self.model.__name__.lower(),
                        resource_id=str(id)
                    )
                
                session.delete(entity)
    
    async def async_delete(self, id: int, db: AsyncSession = None) -> None:
        """
        刪除實體（異步）。
        
        Args:
            id: 實體 ID
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        if db is not None:
            # 使用傳入的 session
            entity = await db.get(self.model, id)
            if not entity:
                raise ResourceNotFoundError(
                    message=f"{self.model.__name__} with id {id} not found",
                    resource_type=self.model.__name__.lower(),
                    resource_id=str(id)
                )
            
            await db.delete(entity)
        else:
            # 使用異步 session
            async with db_session.get_async_session() as session:
                entity = await session.get(self.model, id)
                if not entity:
                    raise ResourceNotFoundError(
                        message=f"{self.model.__name__} with id {id} not found",
                        resource_type=self.model.__name__.lower(),
                        resource_id=str(id)
                    )
                
                await session.delete(entity)
