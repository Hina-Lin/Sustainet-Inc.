"""
Agent 相關的服務層邏輯。
處理 Agent 的建立、更新、查詢等操作。
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from src.application.dto.agent_dto import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse
)
from src.infrastructure.database.agent_repo import AgentRepository
from src.utils.exceptions import ResourceNotFoundError
from src.infrastructure.database.models.agent import Agent

class AgentService:
    """
    Agent 服務類，封裝與 Agent 相關的業務邏輯。
    
    用法示例:
    ```python
    # 透過依賴注入獲取服務
    @router.get("/agents")
    def list_agents(service: AgentService = Depends(get_agent_service)):
        return service.list_agents()
    ```
    """
    def __init__(self, db: Optional[Session] = None):
        """
        初始化服務。
        
        Args:
            db: 數據庫會話
        """
        self.db = db
        self.repo = AgentRepository()
    
    def create_agent(self, request: AgentCreateRequest) -> AgentResponse:
        """
        建立新的 Agent。
        
        Args:
            request: 建立 Agent 的請求 DTO
            
        Returns:
            新建立的 Agent 響應 DTO
        """
        agent = self.repo.create_agent(
            agent_name=request.agent_name,
            provider=request.provider,
            model_name=request.model_name,
            description=request.description,
            instruction=request.instruction,
            tools=request.tools,
            temperature=request.temperature,
            num_history_responses=request.num_history_responses,
            markdown=request.markdown,
            debug=request.debug,
            db=self.db
        )
        
        return AgentResponse(
            id=agent.id,
            agent_name=agent.agent_name,
            provider=agent.provider,
            model_name=agent.model_name,
            description=agent.description,
            tools=agent.tools,
            temperature=agent.temperature,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat()
        )
    
    def get_agent(self, agent_id: int) -> AgentResponse:
        """
        獲取 Agent。
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent 響應 DTO
            
        Raises:
            ResourceNotFoundError: 如果找不到 Agent
        """
        agent = self.repo.get_by_id(agent_id, db=self.db)
        
        return AgentResponse(
            id=agent.id,
            agent_name=agent.agent_name,
            provider=agent.provider,
            model_name=agent.model_name,
            description=agent.description,
            tools=agent.tools,
            temperature=agent.temperature,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat()
        )
    
    def get_agent_by_name(self, agent_name: str) -> Optional[AgentResponse]:
        """
        根據名稱獲取 Agent。
        
        Args:
            agent_name: Agent 名稱
            
        Returns:
            Agent 響應 DTO，如果未找到則返回 None
        """
        agent = self.repo.get_by_name(agent_name, db=self.db)
        
        if not agent:
            return None
            
        return AgentResponse(
            id=agent.id,
            agent_name=agent.agent_name,
            provider=agent.provider,
            model_name=agent.model_name,
            description=agent.description,
            tools=agent.tools,
            temperature=agent.temperature,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat()
        )
    
    def list_agents(self) -> AgentListResponse:
        """
        獲取所有 Agent 列表。
        
        Returns:
            Agent 列表響應 DTO
        """
        agents: List[Agent] = self.repo.get_all(db=self.db)
        
        agent_responses: List[AgentResponse] = []
        for agent in agents:
            # 明確的類型標註
            created_at: datetime = agent.created_at
            updated_at: datetime = agent.updated_at
            
            agent_responses.append(
                AgentResponse(
                    id=agent.id,
                    agent_name=agent.agent_name,
                    provider=agent.provider,
                    model_name=agent.model_name,
                    description=agent.description,
                    tools=agent.tools,
                    temperature=agent.temperature,
                    created_at=created_at.isoformat(),
                    updated_at=updated_at.isoformat()
                )
            )
            
        return AgentListResponse(
            agents=agent_responses,
            total=len(agent_responses)
        )
    
    def update_agent(self, agent_id: int, request: AgentUpdateRequest) -> AgentResponse:
        """
        更新 Agent。
        
        Args:
            agent_id: Agent ID
            request: 更新 Agent 的請求 DTO
            
        Returns:
            更新後的 Agent 響應 DTO
            
        Raises:
            ResourceNotFoundError: 如果找不到 Agent
        """
        # 構建更新數據
        update_data: Dict[str, Any] = {}
        for key, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[key] = value
                
        if not update_data:
            # 如果沒有需要更新的資料，直接返回現有 Agent
            return self.get_agent(agent_id)
                
        # 更新 Agent
        agent: Agent = self.repo.update(agent_id, update_data, db=self.db)
        
        # 明確的類型標註
        created_at: datetime = agent.created_at
        updated_at: datetime = agent.updated_at
        
        # 轉換為響應 DTO
        return AgentResponse(
            id=agent.id,
            agent_name=agent.agent_name,
            provider=agent.provider,
            model_name=agent.model_name,
            description=agent.description,
            tools=agent.tools,
            temperature=agent.temperature,
            created_at=created_at.isoformat(),
            updated_at=updated_at.isoformat()
        )
    
    def delete_agent(self, agent_id: int) -> None:
        self.repo.delete(agent_id, db=self.db)
