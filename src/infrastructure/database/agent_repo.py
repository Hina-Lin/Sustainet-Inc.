"""
Agent repository for database operations.
Provides CRUD operations for Agent entities.
Supports both synchronous and asynchronous operations.
"""
from typing import Optional, Dict, Any, List, Union

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.base_repo import BaseRepository
from src.infrastructure.database.models.agent import Agent
from src.utils.exceptions import ResourceNotFoundError

class AgentRepository(BaseRepository[Agent]):
    """
    Agent 資料庫 Repository 類，提供對 Agent 實體的基本 CRUD 操作。
    支援同步和異步操作。
    
    用法示例:
    ```python
    # 建立實例
    agent_repo = AgentRepository()
    
    # 同步操作
    all_agents = agent_repo.get_all()
    agent = agent_repo.get_by_id(1)
    agent = agent_repo.get_by_name("FakeNewsAgent")
    
    # 創建新 Agent
    new_agent = agent_repo.create_agent(
        agent_name="FactCheckerAgent",
        provider="openai",
        model_name="gpt-4.1",
        description="Checks facts in news articles"
    )
    
    # 異步操作
    all_agents = await agent_repo.async_get_all()
    agent = await agent_repo.async_get_by_id(1)
    agent = await agent_repo.async_get_by_name("FakeNewsAgent")
    
    # 異步創建 Agent
    new_agent = await agent_repo.async_create_agent(
        agent_name="FactCheckerAgent",
        provider="openai",
        model_name="gpt-4.1"
    )
    ```
    """
    # 設定對應的模型
    model = Agent
    
    # 繼承父類的 CRUD 方法
    # get_by_id
    # get_all
    # get_by
    # create
    # update
    # delete
    # 以及對應的異步版本
    
    def get_by_name(self, agent_name: str, db: Session = None) -> Optional[Agent]:
        """
        根據 Agent 名稱獲取 Agent 實體（同步）。
        
        Args:
            agent_name: Agent 名稱
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Returns:
            Agent 實體，如果未找到則返回 None
        """
        results = self.get_by(db=db, agent_name=agent_name)
        return results[0] if results else None
    
    async def async_get_by_name(self, agent_name: str, db: AsyncSession = None) -> Optional[Agent]:
        """
        根據 Agent 名稱獲取 Agent 實體（異步）。
        
        Args:
            agent_name: Agent 名稱
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            
        Returns:
            Agent 實體，如果未找到則返回 None
        """
        results = await self.async_get_by(db=db, agent_name=agent_name)
        return results[0] if results else None
    
    def create_agent(self, agent_name: str, provider: str = "openai", 
                    model_name: str = "gpt-4.1", description: str = None, 
                    instruction: str = None, tools: Dict = None, 
                    db: Session = None, **kwargs) -> Agent:
        """
        創建新的 Agent 實體（同步）。
        通過調用父類的 create 方法實現，便於未來抽換實現。
        
        Args:
            agent_name: Agent 名稱
            provider: 提供商名稱，預設為 "openai"
            model_name: 模型名稱，預設為 "gpt-4.1"
            description: 描述
            instruction: 指令
            tools: 工具配置
            db: 可選的數據庫 Session，如果未提供則自動創建
            **kwargs: 其他參數
            
        Returns:
            新創建的 Agent 實體
        """
        agent_data = {
            "agent_name": agent_name,
            "provider": provider,
            "model_name": model_name
        }
        
        if description is not None:
            agent_data["description"] = description
        
        if instruction is not None:
            agent_data["instruction"] = instruction
            
        if tools is not None:
            agent_data["tools"] = tools
            
        # 添加其他參數
        for key, value in kwargs.items():
            if hasattr(Agent, key):
                agent_data[key] = value
        
        # 調用父類的 create 方法
        return self.create(agent_data, db=db)
    
    async def async_create_agent(self, agent_name: str, provider: str = "openai", 
                                model_name: str = "gpt-4.1", description: str = None, 
                                instruction: str = None, tools: Dict = None, 
                                db: AsyncSession = None, **kwargs) -> Agent:
        """
        創建新的 Agent 實體（異步）。
        通過調用父類的 async_create 方法實現，便於未來抽換實現。
        
        Args:
            agent_name: Agent 名稱
            provider: 提供商名稱，預設為 "openai"
            model_name: 模型名稱，預設為 "gpt-4.1"
            description: 描述
            instruction: 指令
            tools: 工具配置
            db: 可選的異步數據庫 Session，如果未提供則自動創建
            **kwargs: 其他參數
            
        Returns:
            新創建的 Agent 實體
        """
        agent_data = {
            "agent_name": agent_name,
            "provider": provider,
            "model_name": model_name
        }
        
        if description is not None:
            agent_data["description"] = description
        
        if instruction is not None:
            agent_data["instruction"] = instruction
            
        if tools is not None:
            agent_data["tools"] = tools
            
        # 添加其他參數
        for key, value in kwargs.items():
            if hasattr(Agent, key):
                agent_data[key] = value
        
        # 調用父類的 async_create 方法
        return await self.async_create(agent_data, db=db)
