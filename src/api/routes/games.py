from fastapi import APIRouter
from src.application.services.game_service import GameService, FakeNewsAgent
from src.application.dto.game_dto import GameStartResponse
from src.infrastructure.database.game_setup_repo import GameSetupRepository
from src.infrastructure.database.platform_state_repo import PlatformStateRepository
from src.infrastructure.database.news_repo import NewsRepository
from src.infrastructure.database.action_record_repo import ActionRecordRepository
from src.infrastructure.database.game_round_repo import GameRoundRepository

router = APIRouter()


@router.post("/games/start", response_model=GameStartResponse)
def start_game():
    """
    開始新遊戲，回傳平台初始狀態與 AI 首次假訊息。
    """
    # 手動注入相依物件（正式版建議改為 FastAPI Depends 管理）
    service = GameService(
        setup_repo=GameSetupRepository(),
        state_repo=PlatformStateRepository(),
        news_repo=NewsRepository(),
        action_repo=ActionRecordRepository(),
        round_repo=GameRoundRepository(),
        agent=FakeNewsAgent()
    )
    return service.start_game()
