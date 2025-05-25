from typing import Optional, List
from sqlalchemy.orm import Session

from src.infrastructure.database.base_repo import BaseRepository
from src.infrastructure.database.models.article_polish_record import ArticlePolishRecord
from src.infrastructure.database.utils import with_session
from src.utils.exceptions import ResourceNotFoundError


class ArticlePolishRecordRepository(BaseRepository[ArticlePolishRecord]):
    """
    ArticlePolishRecord 資料庫 Repository 類，對應潤飾前後文章的資料表。
    支援基本 CRUD 操作，預期主要用途為新增與查詢。

    用法示例:
    ```python
    repo = ArticlePolishRecordRepository()
    # 建立新潤飾記錄
    record = repo.create_record(
        session_id="game123",
        round_number=2,
        original_content="原始內容",
        polished_content="潤飾後內容"
    )
    # 查詢某場次某回合的潤飾記錄
    records = repo.get_by_session_and_round("game123", 2)
    ```
    """
    model = ArticlePolishRecord

    @with_session
    def create_polish_record(
        self,
        session_id: str,
        round_number: int,
        original_content: str,
        polished_content: str,
        db: Optional[Session] = None
    ) -> ArticlePolishRecord:
        """
        新增一筆潤飾記錄。
        """
        return self.create(
            {
                "session_id": session_id,
                "round_number": round_number,
                "original_content": original_content,
                "polished_content": polished_content,
            },
            db=db
        )

    @with_session
    def get_by_session_and_round(
        self,
        session_id: str,
        round_number: int,
        db: Optional[Session] = None
    ) -> List[ArticlePolishRecord]:
        """
        查詢指定 session_id 與 round_number 的所有潤飾記錄。
        找不到時回傳空列表。
        """
        return (
            db.query(self.model)
            .filter_by(session_id=session_id, round_number=round_number)
            .order_by(self.model.created_at.asc())
            .all()
        )

    @with_session
    def get_or_raise(
        self,
        session_id: str,
        round_number: int,
        db: Optional[Session] = None
    ) -> List[ArticlePolishRecord]:
        """
        查詢指定 session_id 與 round_number 的所有潤飾記錄。
        若查無資料則丟 ResourceNotFoundError。
        """
        result = self.get_by(
            db=db,
            session_id=session_id,
            round_number=round_number
        )
        if not result:
            raise ResourceNotFoundError(
                message=f"No ArticlePolishRecords found for session_id='{session_id}' round={round_number}",
                resource_type="article_polish_record",
                resource_id=f"{session_id}-{round_number}"
            )
        return result

    @with_session
    def update_polished_content(
        self,
        record_id: int,
        polished_content: str,
        db: Optional[Session] = None
    ) -> ArticlePolishRecord:
        """
        更新指定記錄的潤飾後內容。
        """
        record = db.query(ArticlePolishRecord).filter_by(id=record_id).first()
        if not record:
            raise ResourceNotFoundError(
                message=f"ArticlePolishRecord with id={record_id} not found",
                resource_type="article_polish_record",
                resource_id=record_id
            )
        record.polished_content = polished_content
        db.commit()
        db.refresh(record)
        return record

    @with_session
    def delete_record(
        self,
        record_id: int,
        db: Optional[Session] = None
    ):
        """
        刪除指定 id 的潤飾記錄。
        """
        record = db.query(ArticlePolishRecord).filter_by(id=record_id).first()
        if not record:
            raise ResourceNotFoundError(
                message=f"ArticlePolishRecord with id={record_id} not found",
                resource_type="article_polish_record",
                resource_id=record_id
            )
        db.delete(record)
        db.commit()
