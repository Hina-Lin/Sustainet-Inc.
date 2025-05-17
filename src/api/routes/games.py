"""
Game 相關的 API 路由。
提供遊戲初始化與回合管理的 HTTP 端點。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.application.services.game_service import GameService
from src.application.dto.game_dto import GameStartResponse, NewsPolishRequest, NewsPolishResponse
from src.utils.exceptions import ResourceNotFoundError, BusinessLogicError
from src.api.routes.base import get_game_service

# 建立路由器
router = APIRouter(prefix="/games", tags=["games"])


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
    service: GameService = Depends(get_game_service)
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
        # 使用服務層進行潤稿
        return service.polish_news(request)
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