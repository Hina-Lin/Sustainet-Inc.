"""
新聞相關的 API 路由。
提供新聞的 CRUD 操作和隨機獲取功能。
"""
from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, HTTPException, status

from src.application.dto.news_dto import (
    NewsCreate,
    NewsUpdate,
    NewsResponse,
    NewsListResponse,
    RandomNewsRequest,
    NewsBatchCreate,
    NewsBatchResponse
)
from src.api.routes.base import get_news_service
from src.application.services.news_service import NewsService
from src.utils.exceptions import ResourceNotFoundError, ValidationError

router = APIRouter(prefix="/news", tags=["news"])

@router.post("", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
def create_news(
    request: NewsCreate,
    service: NewsService = Depends(get_news_service)
):
    """
    建立新的新聞。
    
    - **title**: 新聞標題
    - **content**: 新聞內容
    - **veracity**: 真實性標籤 (true / false / partial)
    - **category**: 新聞分類
    - **source**: 新聞來源
    - **is_active**: 是否啟用
    """
    try:
        return service.create_news(request)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/batch", response_model=NewsBatchResponse, status_code=status.HTTP_201_CREATED)
def batch_create_news(
    request: NewsBatchCreate,
    service: NewsService = Depends(get_news_service)
):
    """
    批量建立新的新聞（一次新增多筆）。
    
    - **items**: 新聞清單，每筆新聞包含下列欄位：
      - **title**: 新聞標題
      - **content**: 新聞內容
      - **veracity**: 真實性標籤 (true / false / partial)
      - **category**: 新聞分類
      - **source**: 新聞來源
      - **is_active**: 是否啟用
    """
    try:
        return service.batch_create_news(request)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=NewsListResponse)
def list_news(
    skip: int = Query(0, ge=0, description="跳過筆數"),
    limit: int = Query(100, ge=1, le=1000, description="取得筆數"),
    active_only: bool = Query(False, description="是否只取啟用中的新聞"),
    service: NewsService = Depends(get_news_service)
):
    """
    獲取新聞列表。
    
    - **skip**: 跳過筆數
    - **limit**: 取得筆數
    - **active_only**: 是否只取啟用中的新聞
    """
    return service.list_news(skip=skip, limit=limit, active_only=active_only)

@router.get("/random", response_model=NewsResponse)
def get_random_news(
    active_only: bool = Query(True, description="是否只取啟用中的新聞"),
    veracity: Optional[str] = Query(None, description="指定真實性標籤（不指定則不限）"),
    category: Optional[str] = Query(None, description="指定分類（不指定則不限）"),
    service: NewsService = Depends(get_news_service)
):
    """
    隨機取得一則新聞。
    
    - **active_only**: 是否只取啟用中的新聞
    - **veracity**: 指定真實性標籤（不指定則不限）
    - **category**: 指定分類（不指定則不限）
    """
    try:
        request = RandomNewsRequest(
            active_only=active_only,
            veracity=veracity,
            category=category
        )
        return service.get_random_news(request)
    except (ResourceNotFoundError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(e, ResourceNotFoundError) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{news_id}", response_model=NewsResponse)
def get_news(
    news_id: int = Path(..., description="新聞 ID"),
    service: NewsService = Depends(get_news_service)
):
    """
    根據 ID 獲取特定新聞。
    
    - **news_id**: 新聞 ID
    """
    try:
        return service.get_news(news_id)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{news_id}", response_model=NewsResponse)
def update_news(
    request: NewsUpdate,
    news_id: int = Path(..., description="新聞 ID"),
    service: NewsService = Depends(get_news_service)
):
    """
    更新特定新聞。
    
    - **news_id**: 新聞 ID
    """
    try:
        return service.update_news(news_id, request)
    except (ResourceNotFoundError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if isinstance(e, ResourceNotFoundError) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(
    news_id: int = Path(..., description="新聞 ID"),
    service: NewsService = Depends(get_news_service)
):
    """
    刪除特定新聞。
    
    - **news_id**: 新聞 ID
    """
    try:
        service.delete_news(news_id)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return None
