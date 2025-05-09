"""
Agent repository for database operations.
Provides synchronous CRUD operations for Agent entities.
"""
from typing import Optional, Dict, Any, List, Union

from sqlalchemy.orm import Session
from src.infrastructure.database.utils import with_session

from src.infrastructure.database.base_repo import BaseRepository
from src.infrastructure.database.models.agent import Agent
from src.utils.exceptions import ResourceNotFoundError

class AgentRepository(BaseRepository[Agent]):
    """
    Agent 資料庫 Repository 類，提供對 Agent 實體的基本 CRUD 操作。
    
    用法示例:
    ```python
    # 建立實例
    agent_repo = AgentRepository()
    
    # 同步操作
    all_agents = agent_repo.get_all()
    agent = agent_repo.get_by_id(1)
    agent = agent_repo.get_by_name("FakeNewsAgent")
    
    # 同步創建 Agent
    new_agent = agent_repo.create_agent(
        agent_name="FactCheckerAgent",
        provider="openai",
        model_name="gpt-4.1"
    )
    ```
    """
    # 設定對應的模型
    model = Agent
    
    # 以下方法通過 @with_session 裝飾器實現自動 session 管理
    
    @with_session
    def get_by_name(self, agent_name: str, db: Optional[Session] = None) -> Optional[Agent]:
        """
        根據 Agent 名稱獲取 Agent 實體。
        
        Args:
            agent_name: Agent 名稱
            db: 可選的數據庫 Session，如果未提供則自動創建
            
        Returns:
            Agent 實體，如果未找到則返回 None
        """
        results = self.get_by(db=db, agent_name=agent_name)
        return results[0] if results else None
    
    @with_session
    def create_agent(self, 
                     agent_name: str, provider: Optional[str] = "openai", 
                     model_name: Optional[str] = "gpt-4.1", 
                     description: Optional[str] = None, 
                     instruction: Optional[str] = None, 
                     tools: Optional[Dict] = None, 
                     temperature: Optional[float] = None, 
                     num_history_responses: Optional[int] = 10,
                     markdown: Optional[bool] = True, 
                     debug: Optional[bool] = False,
                     
                     db: Optional[Session] = None, **kwargs) -> Agent:
        """
        創建新的 Agent 實體。
        
        Args:
            agent_name: Agent 名稱
            provider: 提供商名稱，預設為 "openai"
            model_name: 模型名稱，預設為 "gpt-4.1"
            description: 描述
            instruction: 指令
            tools: 工具配置
            temperature: 模型溫度參數
            num_history_responses: 歷史回應數量
            markdown: 是否啟用 markdown
            debug: 是否啟用調試模式
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
        
        if temperature is not None:
            agent_data["temperature"] = temperature
            
        if num_history_responses is not None:
            agent_data["num_history_responses"] = num_history_responses
            
        if markdown is not None:
            agent_data["markdown"] = markdown
            
        if debug is not None:
            agent_data["debug"] = debug
            
        # 添加其他參數
        for key, value in kwargs.items():
            if hasattr(Agent, key):
                agent_data[key] = value
        
        # 調用父類的 create 方法
        return self.create(agent_data, db=db)
