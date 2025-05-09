"""
Agent 相關的服務層邏輯。
處理 Agent 的建立、更新、查詢等操作。
"""
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.agent_dto import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse
)
from src.infrastructure.database.agent_repo import AgentRepository
from src.utils.exceptions import ResourceNotFoundError

# 建立全局 repository 實例
agent_repo = AgentRepository()

# 同步服務函數
def create_agent_service(request: AgentCreateRequest, db: Session = None) -> AgentResponse:
    """
    建立新的 Agent 服務。
    
    Args:
        request: 建立 Agent 的請求 DTO
        db: 可選的數據庫 Session
        
    Returns:
        新建立的 Agent 響應 DTO
    """
    # 從 repository 建立 Agent
    agent = agent_repo.create_agent(
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
        db=db
    )
    
    # 轉換為響應 DTO
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

def get_agent_service(agent_id: int, db: Session = None) -> AgentResponse:
    """
    獲取 Agent 服務。
    
    Args:
        agent_id: Agent ID
        db: 可選的數據庫 Session
        
    Returns:
        Agent 響應 DTO
        
    Raises:
        ResourceNotFoundError: 如果找不到 Agent
    """
    agent = agent_repo.get_by_id(agent_id, db=db)
    
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

def get_agent_by_name_service(agent_name: str, db: Session = None) -> Optional[AgentResponse]:
    """
    根據名稱獲取 Agent 服務。
    
    Args:
        agent_name: Agent 名稱
        db: 可選的數據庫 Session
        
    Returns:
        Agent 響應 DTO，如果未找到則返回 None
    """
    agent = agent_repo.get_by_name(agent_name, db=db)
    
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

def list_agents_service(db: Session = None) -> AgentListResponse:
    """
    獲取所有 Agent 列表服務。
    
    Args:
        db: 可選的數據庫 Session
        
    Returns:
        Agent 列表響應 DTO
    """
    agents = agent_repo.get_all(db=db)
    
    agent_responses = []
    for agent in agents:
        agent_responses.append(
            AgentResponse(
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
        )
        
    return AgentListResponse(
        agents=agent_responses,
        total=len(agent_responses)
    )

def update_agent_service(agent_id: int, request: AgentUpdateRequest, db: Session = None) -> AgentResponse:
    """
    更新 Agent 服務。
    
    Args:
        agent_id: Agent ID
        request: 更新 Agent 的請求 DTO
        db: 可選的數據庫 Session
        
    Returns:
        更新後的 Agent 響應 DTO
        
    Raises:
        ResourceNotFoundError: 如果找不到 Agent
    """
    # 構建更新數據
    update_data = {}
    for key, value in request.dict(exclude_unset=True).items():
        if value is not None:
            update_data[key] = value
            
    if not update_data:
        # 如果沒有需要更新的資料，直接返回現有 Agent
        return get_agent_service(agent_id, db=db)
            
    # 更新 Agent
    agent = agent_repo.update(agent_id, update_data, db=db)
    
    # 轉換為響應 DTO
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

def delete_agent_service(agent_id: int, db: Session = None) -> None:
    """
    刪除 Agent 服務。
    
    Args:
        agent_id: Agent ID
        db: 可選的數據庫 Session
        
    Raises:
        ResourceNotFoundError: 如果找不到 Agent
    """
    agent_repo.delete(agent_id, db=db)

# 異步服務函數

async def async_create_agent_service(request: AgentCreateRequest, db: AsyncSession = None) -> AgentResponse:
    """
    建立新的 Agent 服務（異步）。
    
    Args:
        request: 建立 Agent 的請求 DTO
        db: 可選的異步數據庫 Session
        
    Returns:
        新建立的 Agent 響應 DTO
    """
    # 從 repository 建立 Agent
    agent = await agent_repo.async_create_agent(
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
        db=db
    )
    
    # 轉換為響應 DTO
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

async def async_get_agent_service(agent_id: int, db: AsyncSession = None) -> AgentResponse:
    """
    獲取 Agent 服務（異步）。
    
    Args:
        agent_id: Agent ID
        db: 可選的異步數據庫 Session
        
    Returns:
        Agent 響應 DTO
        
    Raises:
        ResourceNotFoundError: 如果找不到 Agent
    """
    agent = await agent_repo.async_get_by_id(agent_id, db=db)
    
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

async def async_get_agent_by_name_service(agent_name: str, db: AsyncSession = None) -> Optional[AgentResponse]:
    """
    根據名稱獲取 Agent 服務（異步）。
    
    Args:
        agent_name: Agent 名稱
        db: 可選的異步數據庫 Session
        
    Returns:
        Agent 響應 DTO，如果未找到則返回 None
    """
    agent = await agent_repo.async_get_by_name(agent_name, db=db)
    
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

async def async_list_agents_service(db: AsyncSession = None) -> AgentListResponse:
    """
    獲取所有 Agent 列表服務（異步）。
    
    Args:
        db: 可選的異步數據庫 Session
        
    Returns:
        Agent 列表響應 DTO
    """
    agents = await agent_repo.async_get_all(db=db)
    
    agent_responses = []
    for agent in agents:
        agent_responses.append(
            AgentResponse(
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
        )
        
    return AgentListResponse(
        agents=agent_responses,
        total=len(agent_responses)
    )

async def async_update_agent_service(agent_id: int, request: AgentUpdateRequest, db: AsyncSession = None) -> AgentResponse:
    """
    更新 Agent 服務（異步）。
    
    Args:
        agent_id: Agent ID
        request: 更新 Agent 的請求 DTO
        db: 可選的異步數據庫 Session
        
    Returns:
        更新後的 Agent 響應 DTO
        
    Raises:
        ResourceNotFoundError: 如果找不到 Agent
    """
    # 構建更新數據
    update_data = {}
    for key, value in request.dict(exclude_unset=True).items():
        if value is not None:
            update_data[key] = value
            
    if not update_data:
        # 如果沒有需要更新的資料，直接返回現有 Agent
        return await async_get_agent_service(agent_id, db=db)
            
    # 更新 Agent
    agent = await agent_repo.async_update(agent_id, update_data, db=db)
    
    # 轉換為響應 DTO
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

async def async_delete_agent_service(agent_id: int, db: AsyncSession = None) -> None:
    """
    刪除 Agent 服務（異步）。
    
    Args:
        agent_id: Agent ID
        db: 可選的異步數據庫 Session
        
    Raises:
        ResourceNotFoundError: 如果找不到 Agent
    """
    await agent_repo.async_delete(agent_id, db=db)
