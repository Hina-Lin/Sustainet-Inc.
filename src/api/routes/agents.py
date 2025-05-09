"""
Agent 相關的 API 路由。
提供 Agent CRUD 操作的 HTTP 端點。
"""
from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.agent_dto import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse
)
from src.application.services.agent_service import (
    create_agent_service,
    get_agent_service,
    get_agent_by_name_service,
    list_agents_service,
    update_agent_service,
    delete_agent_service,
    async_create_agent_service,
    async_get_agent_service,
    async_get_agent_by_name_service,
    async_list_agents_service,
    async_update_agent_service,
    async_delete_agent_service
)
from src.infrastructure.database.session import get_db, get_async_db
from src.utils.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/agents", tags=["agents"])

# 同步 API 端點

@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    request: AgentCreateRequest,
    db: Session = Depends(get_db)
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
    return create_agent_service(request, db=db)

@router.get("", response_model=AgentListResponse)
def list_agents(
    db: Session = Depends(get_db)
):
    """
    獲取所有 Agent 列表。
    """
    return list_agents_service(db=db)

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: int = Path(..., description="Agent ID"),
    db: Session = Depends(get_db)
):
    """
    根據 ID 獲取特定 Agent。
    
    - **agent_id**: Agent ID
    """
    try:
        return get_agent_service(agent_id, db=db)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/by-name/{agent_name}", response_model=AgentResponse)
def get_agent_by_name(
    agent_name: str = Path(..., description="Agent 名稱"),
    db: Session = Depends(get_db)
):
    """
    根據名稱獲取特定 Agent。
    
    - **agent_name**: Agent 名稱
    """
    agent = get_agent_by_name_service(agent_name, db=db)
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
    db: Session = Depends(get_db)
):
    """
    更新特定 Agent。
    
    - **agent_id**: Agent ID
    """
    try:
        return update_agent_service(agent_id, request, db=db)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: int = Path(..., description="Agent ID"),
    db: Session = Depends(get_db)
):
    """
    刪除特定 Agent。
    
    - **agent_id**: Agent ID
    """
    try:
        delete_agent_service(agent_id, db=db)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return None

# 異步 API 端點

@router.post("/async", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def async_create_agent(
    request: AgentCreateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    建立新的 Agent (異步)。
    
    - **agent_name**: Agent 名稱，必須唯一
    - **provider**: 提供商名稱 (如 'openai', 'anthropic')
    - **model_name**: 使用的模型名稱
    - **description**: Agent 描述
    - **instruction**: Agent 的指令設定
    - **tools**: Agent 的工具設定
    """
    return await async_create_agent_service(request, db=db)

@router.get("/async", response_model=AgentListResponse)
async def async_list_agents(
    db: AsyncSession = Depends(get_async_db)
):
    """
    獲取所有 Agent 列表 (異步)。
    """
    return await async_list_agents_service(db=db)

@router.get("/async/{agent_id}", response_model=AgentResponse)
async def async_get_agent(
    agent_id: int = Path(..., description="Agent ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    根據 ID 獲取特定 Agent (異步)。
    
    - **agent_id**: Agent ID
    """
    try:
        return await async_get_agent_service(agent_id, db=db)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/async/by-name/{agent_name}", response_model=AgentResponse)
async def async_get_agent_by_name(
    agent_name: str = Path(..., description="Agent 名稱"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    根據名稱獲取特定 Agent (異步)。
    
    - **agent_name**: Agent 名稱
    """
    agent = await async_get_agent_by_name_service(agent_name, db=db)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with name '{agent_name}' not found"
        )
    return agent

@router.put("/async/{agent_id}", response_model=AgentResponse)
async def async_update_agent(
    request: AgentUpdateRequest,
    agent_id: int = Path(..., description="Agent ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新特定 Agent (異步)。
    
    - **agent_id**: Agent ID
    """
    try:
        return await async_update_agent_service(agent_id, request, db=db)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/async/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def async_delete_agent(
    agent_id: int = Path(..., description="Agent ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    刪除特定 Agent (異步)。
    
    - **agent_id**: Agent ID
    """
    try:
        await async_delete_agent_service(agent_id, db=db)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return None
