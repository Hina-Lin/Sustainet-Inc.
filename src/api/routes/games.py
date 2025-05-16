"""
Game 相關的 API 路由。
提供遊戲初始化與回合管理的 HTTP 端點。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from src.application.services.game_service import GameService, FakeNewsAgent
from src.application.dto.game_dto import GameStartResponse
from src.infrastructure.database.game_setup_repo import GameSetupRepository
from src.infrastructure.database.platform_state_repo import PlatformStateRepository
from src.infrastructure.database.news_repo import NewsRepository
from src.infrastructure.database.action_record_repo import ActionRecordRepository
from src.infrastructure.database.game_round_repo import GameRoundRepository
from src.utils.exceptions import ResourceNotFoundError

# 設置路由前綴與標籤
router = APIRouter(prefix="/games", tags=["games"])


# 依賴注入
def get_game_service() -> GameService:
    """
    獲取 GameService 實例。
    """
    return GameService(
        setup_repo=GameSetupRepository(),
        state_repo=PlatformStateRepository(),
        news_repo=NewsRepository(),
        action_repo=ActionRecordRepository(),
        round_repo=GameRoundRepository(),
        agent=FakeNewsAgent()
    )


@router.post("/start", response_model=GameStartResponse, status_code=status.HTTP_201_CREATED)
def start_game(service: GameService = Depends(get_game_service)):
    """
    開始新遊戲，回傳平台初始狀態與 AI 首次假訊息。
    """
    try:
        return service.start_game()
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"遊戲初始化時發生錯誤: {str(e)}"
        )
