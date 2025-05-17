"""
API 基礎路由設定模組。

提供 API 路由所需的通用依賴注入與功能：
- 資料庫會話管理
- 統一的服務層依賴注入
- 基礎路由類別
"""
from typing import Callable, Type, TypeVar, Generic, Dict, Any, Optional
from functools import lru_cache

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db

# 用於定義服務類型
ServiceType = TypeVar('ServiceType')

# 用於模型類型
T = TypeVar('T')

class BaseRouter(Generic[ServiceType]):
    """
    基礎路由類別，用於抽象化常見的路由操作。
    每個模塊的路由器可以繼承此類，簡化路由配置與依賴注入。
    
    用法示例:
    ```python
    # 建立路由器
    agent_router = BaseRouter[AgentService](
        prefix="/agents",
        tags=["agents"],
        service_class=AgentService,
    )
    
    # 註冊路由
    @agent_router.router.get("", response_model=AgentListResponse)
    def list_agents(service: AgentService = Depends(agent_router.get_service)):
        return service.list_agents()
    ```
    """
    def __init__(
        self,
        prefix: str = "", 
        tags: list = None,
        service_class: Type[ServiceType] = None,
    ):
        """
        初始化路由器。
        
        Args:
            prefix: 路由前綴
            tags: 路由標籤列表
            service_class: 服務類別
        """
        if tags is None:
            tags = []
            
        self.prefix = prefix
        self.tags = tags
        self.service_class = service_class
        self.router = APIRouter(prefix=prefix, tags=tags)
    
    def get_service(self, db: Session = Depends(get_db)) -> ServiceType:
        """
        獲取服務實例的依賴函數。
        
        用法:
        ```python
        @router.get("")
        def list_items(service: MyService = Depends(get_service)):
            return service.list_items()
        ```
        
        Args:
            db: 數據庫會話
            
        Returns:
            服務實例
        """
        if self.service_class is None:
            raise NotImplementedError("Service class must be defined")
        return self.service_class(db=db)

# 全局服務依賴字典
_service_instances: Dict[Type, Any] = {}

def inject_service(service_class: Type[ServiceType]) -> Callable[[Session], ServiceType]:
    """
    服務依賴注入裝飾器。
    用於在 API 路由中注入服務實例。
    
    用法:
    ```python
    @router.get("")
    def list_agents(service = Depends(inject_service(AgentService))):
        return service.list_agents()
    ```
    
    Args:
        service_class: 服務類別
        
    Returns:
        依賴函數，返回服務實例
    """
    def get_service_instance(db: Session = Depends(get_db)) -> ServiceType:
        """依賴函數，返回服務實例"""
        return service_class(db=db)
    
    return get_service_instance

# 通用服務依賴注入函數

# 導入服務類別型別
from src.application.services.agent_service import AgentService
from src.application.services.news_service import NewsService
from src.domain.logic.agent_factory import AgentFactory
from src.infrastructure.database.agent_repo import AgentRepository

def get_agent_service(db: Session = Depends(get_db)) -> AgentService:
    """獲取 Agent 服務實例"""
    return AgentService(db=db)

def get_news_service(db: Session = Depends(get_db)) -> NewsService:
    """獲取 News 服務實例"""
    return NewsService(db=db)

def get_agent_factory(db: Session = Depends(get_db)) -> AgentFactory:
    """獲取 AgentFactory 實例"""
    return AgentFactory(AgentRepository())
# 如果需要 GameService 和 ToolService，請添加相應的導入
# 然後實現對應的依賴函數
