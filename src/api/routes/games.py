"""
Game 相關的 API 路由。
提供遊戲初始化與回合管理的 HTTP 端點。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.services.game_service import GameService, FakeNewsAgent
from src.application.dto.game_dto import GameStartResponse, NewsPolishRequest, NewsPolishResponse
from src.infrastructure.database.game_setup_repo import GameSetupRepository
from src.infrastructure.database.platform_state_repo import PlatformStateRepository
from src.infrastructure.database.news_repo import NewsRepository
from src.infrastructure.database.action_record_repo import ActionRecordRepository
from src.infrastructure.database.game_round_repo import GameRoundRepository
from src.domain.logic.agent_factory import AgentFactory
from src.utils.exceptions import ResourceNotFoundError, BusinessLogicError
from src.infrastructure.database.session import get_db
from src.api.routes.base import  get_agent_factory

# 建立路由器
router = APIRouter(prefix="/games", tags=["games"])

# 依賴注入函數
def get_game_service(db: Session = Depends(get_db)) -> GameService:
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


@router.post("/polish-news", response_model=NewsPolishResponse)
def polish_news(
    request: NewsPolishRequest,
    service: GameService = Depends(get_game_service),
    agent_factory: AgentFactory = Depends(get_agent_factory)
):
    """
    使用 AI 系統維物潤稿新聞內容。
    
    - **session_id**: 會話ID
    - **content**: 使用者的新聞內容
    - **requirements**: 使用者的潤稿要求
    - **sources**: (可選) 參考的新聞連結
    - **platform**: (可選) 即將發布的平台
    - **platform_user**: (可選) 平台用戶名稱/特徵
    - **current_situation**: (可選) 當前狀況描述
    - **additional_context**: (可選) 其他上下文資訊
    """
    try:
        # 使用服務層進行潤稿，將 agent_factory 傳入方法而非構造函數
        return service.polish_news(request, agent_factory=agent_factory)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"潤稿過程發生錯誤: {str(e)}"
        )