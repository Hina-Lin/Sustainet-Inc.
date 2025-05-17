"""
News 模型定義。
儲存遊戲中可使用的新聞或議題資料。
"""

from sqlalchemy import Column, Integer, String, Text, Boolean
from .base import Base, TimeStampMixin

class News(Base, TimeStampMixin):
    """
    新聞／議題表。

    - **news_id**: 主鍵，自動遞增。
    - **title**: 新聞標題。
    - **content**: 新聞內文。
    - **veracity**: 真實性（可選值："true", "false", "partial"）。
    - **category**: 議題分類（如 "energy", "environment", "social_justice"）。
    - **source**: 新聞來源（如 "某新聞網", "環保團體聲明"）。
    - **is_active**: 是否為有效新聞（預設 True，用於過濾已下架內容）。

    範例資料：
    ```json
    {
        "title": "太陽能板產生毒氣？",
        "veracity": "partial",
        "category": "energy",
        "source": "網友轉傳",
        "is_active": true
    }
    """
    __tablename__ = "news"

    news_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主鍵，自動遞增"
    )

    title = Column(
        String(256),
        nullable=False,
        comment="新聞標題"
    )

    content = Column(
        Text,
        nullable=False,
        comment="新聞內容"
    )

    veracity = Column(
        String(32),
        nullable=False,
        comment="新聞真實性標籤（'true', 'false', 'partial'）"
    )

    category = Column(
        String(64),
        nullable=False,
        comment="新聞分類（如 energy, environment）"
    )

    source = Column(
        String(1280),
        nullable=False,
        comment="新聞來源"
    )

    is_active = Column(
        Boolean,
        default=True,
        comment="是否為啟用中新聞（預設 True）"
    )

    def __repr__(self):
        return f"<News id={self.news_id}, title={self.title}, veracity={self.veracity}>"
