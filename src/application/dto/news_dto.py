"""
新聞相關的 DTO（資料傳輸物件）定義。
用於前後端交互傳輸的資料結構定義。
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class NewsBase(BaseModel):
    """新聞基礎資料定義。"""
    title: str = Field(..., description="新聞標題", example="太陽能板製造過程污染嚴重？", min_length=2, max_length=256)
    content: str = Field(..., description="新聞內容", example="根據某研究報告指出，太陽能板製造過程中...", min_length=10)
    veracity: str = Field(..., description="真實性標籤（true / false / partial）", example="partial")
    category: str = Field(..., description="新聞分類", example="energy")
    source: str = Field(..., description="新聞來源", example="某新聞網", max_length=1280)
    is_active: bool = Field(True, description="是否啟用")


class NewsCreate(NewsBase):
    """新增新聞的請求資料結構。"""
    pass


class NewsUpdate(BaseModel):
    """更新新聞的請求資料結構。"""
    title: Optional[str] = Field(None, description="新聞標題", example="太陽能板製造過程污染嚴重？", min_length=2, max_length=256)
    content: Optional[str] = Field(None, description="新聞內容", example="根據某研究報告指出，太陽能板製造過程中...", min_length=10)
    veracity: Optional[str] = Field(None, description="真實性標籤（true / false / partial）", example="partial")
    category: Optional[str] = Field(None, description="新聞分類", example="energy")
    source: Optional[str] = Field(None, description="新聞來源", example="某新聞網", max_length=1280)
    is_active: Optional[bool] = Field(None, description="是否啟用")


class NewsResponse(NewsBase):
    """新聞回覆的資料結構。"""
    news_id: int = Field(..., description="新聞 ID")
    created_at: str = Field(..., description="建立時間")
    updated_at: str = Field(..., description="更新時間")


class NewsListResponse(BaseModel):
    """新聞列表回覆的資料結構。"""
    items: List[NewsResponse] = Field(..., description="新聞列表")
    total: int = Field(..., description="總筆數")


class RandomNewsRequest(BaseModel):
    """隨機取得新聞的請求資料結構。"""
    active_only: bool = Field(True, description="是否只取啟用中的新聞")
    veracity: Optional[str] = Field(None, description="指定真實性標籤（不指定則不限）")
    category: Optional[str] = Field(None, description="指定分類（不指定則不限）")


class NewsBatchCreate(BaseModel):
    """批量新增新聞的請求資料結構。"""
    items: List[NewsCreate] = Field(..., description="新聞清單，至少1筆，最多100筆")
    
    @validator('items')
    def validate_items_length(cls, v):
        if len(v) < 1:
            raise ValueError('At least one news item is required')
        if len(v) > 100:
            raise ValueError('Maximum 100 news items allowed')
        return v


class NewsBatchResponse(BaseModel):
    """批量新增新聞的回應資料結構。"""
    items: List[NewsResponse] = Field(..., description="成功建立的新聞清單")
    count: int = Field(..., description="成功建立的新聞數量")
