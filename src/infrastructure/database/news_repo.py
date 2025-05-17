"""
News repository for database operations.
Provides synchronous CRUD operations for News entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.infrastructure.database.base_repo import BaseRepository
from src.infrastructure.database.models.news import News
from src.infrastructure.database.utils import with_session
from src.utils.exceptions import ResourceNotFoundError


class NewsRepository(BaseRepository[News]):
    """
    News 資料庫 Repository 類，提供對新聞資料的基本操作。

    用法示例:
    ```python
    repo = NewsRepository()

    # 取得單筆新聞
    news = repo.get_by_id(1)

    # 隨機取一筆啟用中的新聞
    news = repo.get_random_active_news()

    # 創建新新聞資料
    new_news = repo.create_news(
        title="太陽能發電污染重？",
        content="部分研究指出...",
        veracity="partial",
        category="energy",
        source="綠色論壇"
    )
    ```
    """

    model = News

    @with_session
    def get_random_active_news(
        self,
        db: Optional[Session] = None
    ) -> News:
        """
        隨機取得一筆啟用中的新聞。

        Args:
            db: 可選資料庫 Session

        Returns:
            News 實體

        Raises:
            ResourceNotFoundError: 若查無任何啟用中的新聞
        """
        from sqlalchemy.sql import func
        stmt = db.query(News).filter(News.is_active.is_(True)).order_by(func.random()).limit(1)
        result = stmt.first()
        if not result:
            raise ResourceNotFoundError(
                message="No active news available.",
                resource_type="news",
                resource_id="active"
            )
        return result

    @with_session
    def create_news(
        self,
        title: str,
        content: str,
        veracity: str,
        category: str,
        source: str,
        is_active: bool = True,
        db: Optional[Session] = None
    ) -> News:
        """
        創建一筆新的新聞資料。

        Args:
            title: 新聞標題
            content: 內容文字
            veracity: 真實性標籤（true / false / partial）
            category: 類別（如 energy / environment）
            source: 新聞來源
            is_active: 是否啟用（預設 True）
            db: 資料庫 Session

        Returns:
            新創建的 News 實體
        """
        return self.create(
            {
                "title": title,
                "content": content,
                "veracity": veracity,
                "category": category,
                "source": source,
                "is_active": is_active,
            },
            db=db
        )

    @with_session
    def get_random_news(
        self,
        db: Optional[Session] = None
    ) -> News:
        """
        隨機取得一則新聞。

        Args:
            db: 資料庫 Session

        Returns:
            隨機選取的 News 實體
        """
        from sqlalchemy.sql import func
        stmt = db.query(News).order_by(func.random()).limit(1)
        result = stmt.first()
        if not result:
            raise ResourceNotFoundError(
                message="No news available.",
                resource_type="news",
                resource_id="random"
            )
        return result
