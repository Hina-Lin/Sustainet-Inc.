"""
Base repository class for database operations.
Provides common synchronous CRUD operations for all entity repositories.
"""
from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Union, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.utils.exceptions import DatabaseError, ResourceNotFoundError
from src.infrastructure.database.models.base import Base
from src.infrastructure.database.session import get_db
from src.infrastructure.database.utils import with_session

# Type variable for the entity model
T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    基礎資料庫 Repository 類，提供通用的同步 CRUD 操作。
    
    用法示例:
    ```python
    class AgentRepository(BaseRepository[Agent]):
        model = Agent
    
    agent_repo = AgentRepository()
    agents = agent_repo.get_all()
    agent = agent_repo.get_by_id(1)
    ```
    """
    # 子類需要覆寫此屬性
    model: Type[Any] = None
    
    def __init__(self):
        """初始化 repository。"""
        if self.__class__.model is None:
            raise NotImplementedError("Repository class must define 'model' attribute")
    
    @with_session
    def get_by_pk(self, pk_value: Union[Any, Tuple[Any, ...]], db: Session = None) -> T:
        """
        根據主鍵取得實體。
        
        Args:
            pk_value: 實體主鍵值 (對於複合主鍵，請傳入一個元組)
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Returns:
            實體對象
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        entity = db.get(self.model, pk_value)
        if not entity:
            raise ResourceNotFoundError(
                message=f"{self.model.__name__} with primary key {pk_value} not found",
                resource_type=self.model.__name__.lower(),
                resource_id=str(pk_value)
            )
        return entity
    
    @with_session
    def get_all(self, db: Session = None) -> List[T]:
        """
        取得所有實體列表。
        
        Args:
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Returns:
            實體列表
        """
        stmt = select(self.model)
        result = db.execute(stmt)
        return list(result.scalars().all())
    
    @with_session
    def get_by(self, db: Session = None, **kwargs) -> List[T]:
        """
        根據條件查詢實體。
        
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
        
        result = db.execute(stmt)
        return list(result.scalars().all())
    
    @with_session
    def create(self, data: Union[Dict[str, Any], T], db: Session = None) -> T:
        """
        創建新實體。
        
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
            
        db.add(entity)
        db.flush()
        db.refresh(entity)
        
        return entity
    
    @with_session
    def update_by_pk(self, pk_value: Union[Any, Tuple[Any, ...]], data: Dict[str, Any], db: Session = None) -> T:
        """
        根據主鍵更新實體。
        
        Args:
            pk_value: 實體主鍵值 (對於複合主鍵，請傳入一個元組)
            data: 要更新的數據
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Returns:
            更新後的實體
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        entity = db.get(self.model, pk_value)
        if not entity:
            raise ResourceNotFoundError(
                message=f"{self.model.__name__} with primary key {pk_value} not found",
                resource_type=self.model.__name__.lower(),
                resource_id=str(pk_value)
            )
        
        # 更新實體屬性
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        db.flush()
        db.refresh(entity)
        
        return entity
    
    @with_session
    def delete_by_pk(self, pk_value: Union[Any, Tuple[Any, ...]], db: Session = None) -> None:
        """
        根據主鍵刪除實體。
        
        Args:
            pk_value: 實體主鍵值 (對於複合主鍵，請傳入一個元組)
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Raises:
            ResourceNotFoundError: 如果找不到實體
        """
        entity = db.get(self.model, pk_value)
        if not entity:
            raise ResourceNotFoundError(
                message=f"{self.model.__name__} with primary key {pk_value} not found",
                resource_type=self.model.__name__.lower(),
                resource_id=str(pk_value)
            )
        
        db.delete(entity)
