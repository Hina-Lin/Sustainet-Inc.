"""
Game 相關的 API 路由。
提供遊戲初始化與回合管理的 HTTP 端點。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from src.application.services.game_service import GameService
from src.application.dto.game_dto import ( 
    NewsPolishRequest, NewsPolishResponse,
    GameStartRequest, GameStartResponse,
    AiTurnRequest, AiTurnResponse,
    PlayerTurnRequest, PlayerTurnResponse,
    StartNextRoundRequest, StartNextRoundResponse,
    GameDashboardRequest, GameDashboardResponse
    )
from src.utils.exceptions import ResourceNotFoundError, BusinessLogicError
from src.api.routes.base import get_game_service

# 建立路由器
router = APIRouter(prefix="/games", tags=["games"])


@router.post("/start", response_model=GameStartResponse, status_code=status.HTTP_201_CREATED)
def start_game(service: GameService = Depends(get_game_service)):
    """
    ## 開始新遊戲
    建立一場新的遊戲並初始化三個平台與受眾，預設 AI 先攻。

    ### Response
    * session_id: 遊戲識別碼（string，自動產生）
    * round_number: 回合數（int，預設 1）
    * actor: 行動者（"ai"）
    * article: AI 發布的假新聞（結構見 ArticleMeta）
    * platform_setup: 平台與受眾組合
    * platform_status: 三平台狀態（每平台信任值、傳播率等）
    * tool_list: 可用工具清單
    * tool_used: 實際使用的工具（通常 AI 首回合無）
    * effectiveness, simulated_comments: GM 模擬結果

    ~~~注意~~~~
    不需傳入任何 body，直接送 POST 請求即可。
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
        
@router.post("/ai-turn", response_model=AiTurnResponse)
def ai_turn(
    request: AiTurnRequest,
    service: GameService = Depends(get_game_service)
):
    """
    ## AI 回合請求
    由 AI 在指定 session_id 與回合數下，發布一則新聞，由 GameMaster 評分。

    ### Request Body
    * session_id: 遊戲識別碼（string，必填）
    * round_number: 回合數（int，必填）

    ### Response : 回傳內容同 /games/start，actor 皆為 "ai" 
    * session_id: 遊戲識別碼（string，自動產生）
    * round_number: 回合數（int，預設 1）
    * actor: 行動者（"ai"）
    * article: AI 發布的假新聞（結構見 ArticleMeta）
    * platform_setup: 平台與受眾組合
    * platform_status: 三平台狀態（每平台信任值、傳播率等）
    * tool_list: 可用工具清單
    * tool_used: 實際使用的工具（通常 AI 首回合無）
    * effectiveness, simulated_comments: GM 模擬結果

    ### 常見錯誤
    * 請確保 session_id 與 round_number 有對應的遊戲狀態，否則會回 404。
    """
    try:
        return service.ai_turn(request)
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
            detail=f"AI 回合過程發生錯誤: {str(e)}"
        )

@router.post("/player-turn", response_model=PlayerTurnResponse)
def player_turn(
    request: PlayerTurnRequest,
    service: GameService = Depends(get_game_service)
):
    """
    ## 玩家回合請求
    玩家於指定 session_id 與 round_number，提交一則新聞（查核、澄清、附和等皆可），可選擇同時使用工具。
    系統會依據玩家提交內容與使用工具，由 GameMaster 判斷效果與分數。

    ### Request Body
    * session_id: 遊戲識別碼（string，必填）
    * round_number: 回合數（int，必填）
    * article: 玩家發布的新聞內容（object，必填，結構如下）
        - title: 文章標題（string，必填）
        - content: 原始內容（string，必填）
        - author: 發文者名稱（string，必填，通常為玩家名稱）
        - published_date: 發布時間（string，必填，ISO 格式，如 "2025-05-21T14:45:00"）
        - target_platform: 文章發佈的平台（string，必填）
        - polished_content: 潤稿後內容（string，選填，若有使用工具可填入）
        - image_url: 配圖連結（string，選填，預設為 null）
        - source: 新聞來源（string，選填，預設為 null）
        - requirement: 風格或語氣需求（string，選填）
        - veracity: 真實性標註（string，選填，由後端填入，前端可省略）
    * tool_used: 玩家實際使用的工具（list，選填，預設為空）
    * tool_list: 可用工具清單（list，選填，由後端傳，前端可省略）

    ### Response
    回傳本回合所有判定結果（同 ai-turn），actor 皆為 "player"。
    * session_id: 遊戲識別碼（string）
    * round_number: 回合數（int）
    * actor: 行動者（"player"）
    * article: 本回合玩家發布的新聞內容（object，結構如 ArticleMeta）
    * platform_setup: 平台與受眾組合
    * platform_status: 三平台狀態（每平台信任值、傳播率等）
    * tool_list: 可用工具清單
    * tool_used: 本回合實際使用的工具
    * effectiveness: GM 模擬評分（"low"/"medium"/"high"）
    * simulated_comments: GM 模擬社群留言

    ~~~注意~~~
    欄位如未使用可設為 null 或留空，後端會自動處理。
    """
    try:
        return service.player_turn(request)
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
            detail=f"玩家回合過程發生錯誤: {str(e)}"
        )

@router.post("/next-round", response_model=StartNextRoundResponse)
def start_next_round(
    request: StartNextRoundRequest,
    service: GameService = Depends(get_game_service)
):
    """
    ## 進入下一回合
    進行新一輪遊戲，由 AI 先攻。系統自動判斷目前最大回合數，自動 +1，產生新回合，並由 AI 發布假新聞。

    ### Request Body
    * session_id: 遊戲識別碼（string，必填）

    ### Response : 回傳本回合所有資料，結構同 ai-turn，actor 為 "ai"。
    * session_id: 遊戲識別碼（string）
    * round_number: 回合數（int，自動加 1）
    * actor: 行動者（"ai"）
    * article: AI 發布的假新聞內容（object，見 ArticleMeta 結構）
    * platform_setup: 平台與受眾組合
    * platform_status: 三平台狀態（每平台信任值、傳播率等）
    * tool_list: 可用工具清單
    * tool_used: 本回合實際使用的工具
    * effectiveness: GM 模擬評分
    * simulated_comments: GM 模擬社群留言

    ~~~注意~~~
    前端僅需傳入 session_id，後端自動判斷回合序號。
    """

    try:
        return service.start_next_round(request)
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
                detail=f"切換回合過程發生錯誤: {str(e)}"
            )

@router.get("/dashboard/{session_id}", response_model=GameDashboardResponse)
def get_game_dashboard(
    session_id: str,
    service: GameService = Depends(get_game_service)
):
    """
    ## 遊戲面板（Dashboard）
    取得指定遊戲的完整歷史記錄和當前狀態，包含所有回合的詳細資訊。

    ### Path Parameters
    * session_id: 遊戲識別碼（string，由 URL 传入）

    ### Response
    * session_id: 遊戲識別碼
    * game_summary: 遊戲摘要訊息（回合數、開始時間、是否結束等）
    * round_records: 所有回合的詳細記錄（AI和玩家行動、平台狀態等）
    * current_status: 當前遊戲狀態統計（總信任值、領先者等）
    * game_end_info: 遊戲結束資訊（如果遊戲已結束）

    ### 使用場景
    適合用於前端建立遊戲面板，展示：
    - 遊戲進度與結束狀態
    - 每回合的AI和玩家行動記錄
    - 平台信任值變化趨勢
    - 社群模擬留言
    - 工具使用情況

    ~~~注意~~~
    此 API 會返回大量數據，建議前端做好緩存和分頁處理。
    """
    try:
        request = GameDashboardRequest(session_id=session_id)
        return service.get_game_dashboard(request)
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
            detail=f"取得遊戲面板時發生錯誤: {str(e)}"
        )