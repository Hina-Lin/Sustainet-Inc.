"""
新聞服務層，處理新聞相關的業務邏輯。
提供新聞的創建、查詢、更新、刪除等服務。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from src.application.dto.news_dto import (
    NewsCreate,
    NewsUpdate,
    NewsResponse,
    NewsListResponse,
    RandomNewsRequest,
    NewsBatchCreate,
    NewsBatchResponse
)
from src.infrastructure.database.news_repo import NewsRepository
from src.utils.exceptions import ResourceNotFoundError, ValidationError


class NewsService:
    """
    新聞服務類，封裝與新聞相關的業務邏輯。
    
    用法示例:
    ```python
    # 透過依賴注入獲取服務
    @router.get("/news")
    def list_news(service: NewsService = Depends(get_news_service)):
        return service.list_news()
    ```
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        初始化服務。
        
        Args:
            db: 數據庫會話
        """
        self.db = db
        self.repo = NewsRepository()
    
    def get_news(self, news_id: int) -> NewsResponse:
        """
        獲取指定 ID 的新聞。
        
        Args:
            news_id: 新聞 ID
            
        Returns:
            新聞詳情
            
        Raises:
            ResourceNotFoundError: 若查無此新聞
        """
        news = self.repo.get_by_id(news_id, db=self.db)
        
        # 將資料庫模型轉為 DTO
        return self._convert_to_response(news)
    
    def list_news(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> NewsListResponse:
        """
        獲取新聞列表。
        
        Args:
            skip: 跳過筆數
            limit: 取得筆數
            active_only: 是否只取啟用中的新聞
            
        Returns:
            新聞列表
        """
        # 根據是否只取啟用中新聞決定查詢條件
        if active_only:
            result = self.repo.get_by(is_active=True, db=self.db)
        else:
            result = self.repo.get_all(db=self.db)
        
        # 處理分頁
        total = len(result)
        items = result[skip:skip + limit]
        
        # 轉換為回應格式
        return NewsListResponse(
            items=[self._convert_to_response(item) for item in items],
            total=total
        )
    
    def create_news(self, request: NewsCreate) -> NewsResponse:
        """
        創建新聞。
        
        Args:
            request: 新聞建立請求
            
        Returns:
            新建立的新聞
        """
        # 參數驗證
        self._validate_news_params(request.veracity, request.category)
        
        # 建立新聞
        news = self.repo.create_news(
            title=request.title,
            content=request.content,
            veracity=request.veracity,
            category=request.category,
            source=request.source,
            is_active=request.is_active,
            db=self.db
        )
        
        # 轉換為回應格式
        return self._convert_to_response(news)
    
    def update_news(self, news_id: int, request: NewsUpdate) -> NewsResponse:
        """
        更新新聞。
        
        Args:
            news_id: 新聞 ID
            request: 新聞更新請求
            
        Returns:
            更新後的新聞
            
        Raises:
            ResourceNotFoundError: 若查無此新聞
        """
        # 參數驗證
        if request.veracity:
            self._validate_news_veracity(request.veracity)
        
        if request.category:
            self._validate_news_category(request.category)
        
        # 建立更新資料字典
        update_data = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        # 若沒有需要更新的資料，則直接返回當前新聞
        if not update_data:
            return self.get_news(news_id)
        
        # 更新新聞
        updated_news = self.repo.update(news_id, update_data, db=self.db)
        
        # 轉換為回應格式
        return self._convert_to_response(updated_news)
    
    def delete_news(self, news_id: int) -> None:
        """
        刪除新聞。
        
        Args:
            news_id: 新聞 ID
            
        Raises:
            ResourceNotFoundError: 若查無此新聞
        """
        self.repo.delete(news_id, db=self.db)
        
    def batch_create_news(self, request: NewsBatchCreate) -> NewsBatchResponse:
        """
        批量創建新聞。
        
        Args:
            request: 批量新聞建立請求
            
        Returns:
            批量建立的新聞回應
            
        Raises:
            ValidationError: 若參數不符合規範
        """
        created_items = []
        
        for item in request.items:
            # 參數驗證
            self._validate_news_params(item.veracity, item.category)
            
            # 建立新聞
            news = self.repo.create_news(
                title=item.title,
                content=item.content,
                veracity=item.veracity,
                category=item.category,
                source=item.source,
                is_active=item.is_active,
                db=self.db
            )
            
            # 轉換為回應格式並添加到列表
            created_items.append(self._convert_to_response(news))
        
        # 返回批量建立結果
        return NewsBatchResponse(
            items=created_items,
            count=len(created_items)
        )
    
    def get_random_news(self, request: RandomNewsRequest) -> NewsResponse:
        """
        隨機取得一則新聞。
        
        Args:
            request: 隨機新聞請求
            
        Returns:
            隨機新聞
            
        Raises:
            ResourceNotFoundError: 若查無符合條件的新聞
        """
        # 參數驗證
        if request.veracity:
            self._validate_news_veracity(request.veracity)
        
        if request.category:
            self._validate_news_category(request.category)
        
        # 若有指定條件，則用條件查詢
        if request.veracity or request.category or not request.active_only:
            # 構建查詢條件
            conditions = {}
            if request.active_only:
                conditions["is_active"] = True
            
            if request.veracity:
                conditions["veracity"] = request.veracity
            
            if request.category:
                conditions["category"] = request.category
            
            # 取得符合條件的所有新聞
            news_list = self.repo.get_by(**conditions, db=self.db)
            
            if not news_list:
                raise ResourceNotFoundError(
                    message="No news match the criteria.",
                    resource_type="news",
                    resource_id="random"
                )
            
            # 隨機取一則
            import random
            news = random.choice(news_list)
        else:
            # 若無特定條件且只要啟用中的新聞，則使用專用方法
            news = self.repo.get_random_active_news(db=self.db)
        
        # 轉換為回應格式
        return self._convert_to_response(news)
    
    def _convert_to_response(self, news: Any) -> NewsResponse:
        """
        將資料庫模型轉換為回應 DTO。
        
        Args:
            news: 資料庫中的新聞模型
            
        Returns:
            新聞回應 DTO
        """
        return NewsResponse(
            news_id=news.news_id,
            title=news.title,
            content=news.content,
            veracity=news.veracity,
            category=news.category,
            source=news.source,
            is_active=news.is_active,
            created_at=news.created_at.isoformat(),
            updated_at=news.updated_at.isoformat()
        )
    
    def _validate_news_params(self, veracity: str, category: str) -> None:
        """
        驗證新聞參數。
        
        Args:
            veracity: 真實性標籤
            category: 分類
            
        Raises:
            ValidationError: 若參數不符合規範
        """
        self._validate_news_veracity(veracity)
        self._validate_news_category(category)
    
    def _validate_news_veracity(self, veracity: str) -> None:
        """
        驗證新聞真實性標籤。
        
        Args:
            veracity: 真實性標籤
            
        Raises:
            ValidationError: 若標籤不符合規範
        """
        valid_veracity = ["true", "false", "partial"]
        if veracity not in valid_veracity:
            raise ValidationError(
                message=f"Invalid veracity value. Must be one of: {', '.join(valid_veracity)}",
                error_code="INVALID_VERACITY"
            )
    
    def _validate_news_category(self, category: str) -> None:
        """
        驗證新聞分類。
        
        Args:
            category: 分類
            
        Raises:
            ValidationError: 若分類不符合規範
        """
        valid_categories = [
            "energy", "environment", "social_justice", 
            "economy", "policy", "technology", "event", 
            "trend", "regulation", "award"
        ]
        if category not in valid_categories:
            raise ValidationError(
                message=f"Invalid category value. Must be one of: {', '.join(valid_categories)}",
                error_code="INVALID_CATEGORY"
            )

