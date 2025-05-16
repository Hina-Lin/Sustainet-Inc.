from typing import Optional
from sqlalchemy.orm import Session
from src.infrastructure.database.base_repo import BaseRepository
from src.infrastructure.database.models.game_records import GameRecord

class GameRecordRepository(BaseRepository[GameRecord]):
    """
    遊戲紀錄的 Repository，提供對 GameRecord 的基本操作。
    """
    model = GameRecord

    def create_game_record(self, session_id: str, round_number: int, actor: str, platform: str, input_text: str, result: str, db: Optional[Session] = None) -> GameRecord:
        """
        創建新的遊戲紀錄。

        Args:
            session_id: 遊戲的唯一識別碼
            round_number: 回合數
            actor: 行為者（如 FakeNewsAgent 或玩家）
            platform: 平台名稱
            input_text: 輸入文字
            result: 假訊息結果
            db: 可選的數據庫 Session

        Returns:
            新創建的 GameRecord 實體
        """
        record_data = {
            "session_id": session_id,
            "round_number": round_number,
            "actor": actor,
            "platform": platform,
            "input_text": input_text,
            "result": result
        }
        return self.create(record_data, db=db)