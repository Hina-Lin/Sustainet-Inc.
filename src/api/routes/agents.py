"""
Agent 相關的 API 路由。
提供 Agent CRUD 操作的 HTTP 端點。
"""
from fastapi import APIRouter, Depends, Path, HTTPException, status

from src.application.dto.agent_dto import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse
)
from src.api.routes.base import get_agent_service
from src.utils.exceptions import ResourceNotFoundError
from src.application.services.agent_service import AgentService

router = APIRouter(prefix="/agents", 
                   tags=["agents"])

@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    request: AgentCreateRequest,
    service: AgentService = Depends(get_agent_service)
):
    """
    建立新的 Agent。
    
    - **agent_name**: Agent 名稱，必須唯一
    - **provider**: 提供商名稱 (如 'openai', 'anthropic')
    - **model_name**: 使用的模型名稱
    - **description**: Agent 描述
    - **instruction**: Agent 的指令設定
    - **tools**: Agent 的工具設定
    """
    return service.create_agent(request)

@router.get("", response_model=AgentListResponse)
def list_agents(
    service: AgentService = Depends(get_agent_service)
):
    """
    獲取所有 Agent 列表。
    """
    return service.list_agents()

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: int = Path(..., description="Agent ID"),
    service: AgentService = Depends(get_agent_service)
):
    """
    根據 ID 獲取特定 Agent。
    
    - **agent_id**: Agent ID
    """
    try:
        return service.get_agent(agent_id)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/by-name/{agent_name}", response_model=AgentResponse)
def get_agent_by_name(
    agent_name: str = Path(..., description="Agent 名稱"),
    service: AgentService = Depends(get_agent_service)
):
    """
    根據名稱獲取特定 Agent。
    
    - **agent_name**: Agent 名稱
    """
    agent = service.get_agent_by_name(agent_name)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with name '{agent_name}' not found"
        )
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    request: AgentUpdateRequest,
    agent_id: int = Path(..., description="Agent ID"),
    service: AgentService = Depends(get_agent_service)
):
    """
    更新特定 Agent。
    
    - **agent_id**: Agent ID
    """
    try:
        return service.update_agent(agent_id, request)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: int = Path(..., description="Agent ID"),
    service: AgentService = Depends(get_agent_service)
):
    """
    刪除特定 Agent。
    
    - **agent_id**: Agent ID
    """
    try:
        service.delete_agent(agent_id)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return None
