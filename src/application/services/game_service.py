"""
Game 相關的服務層邏輯。
處理遊戲的初始化、回合管理等操作。
"""

from typing import List, Optional, Dict, Any
import random
import uuid
import json

from src.application.dto.game_dto import GameStartResponse, PlatformStatus, NewsPolishRequest, NewsPolishResponse
from src.infrastructure.database.game_setup_repo import GameSetupRepository
from src.infrastructure.database.platform_state_repo import PlatformStateRepository
from src.infrastructure.database.news_repo import NewsRepository
from src.infrastructure.database.action_record_repo import ActionRecordRepository
from src.infrastructure.database.game_round_repo import GameRoundRepository
from src.domain.logic.agent_factory import AgentFactory
from src.utils.exceptions import BusinessLogicError, ResourceNotFoundError
from src.utils.logger import logger

# 先用 stub 代替 FakeNewsAgent
#from src.infrastructure.agents.fake_news_agent import FakeNewsAgent

# 這裡是 stub 的 FakeNewsAgent
class FakeNewsAgent:
    def generate_fake_news(self, news):
        return f"[FAKE] {news.title}"
        # 這裡省略了 Agent 的其他屬性
        
class GameService:
    """
    Game 服務類，封裝與遊戲相關的業務邏輯。
    """

    def __init__(
        self,
        setup_repo: GameSetupRepository,
        state_repo: PlatformStateRepository,
        news_repo: NewsRepository,
        action_repo: ActionRecordRepository,
        round_repo: GameRoundRepository,
        agent: FakeNewsAgent,
        agent_factory: Optional[AgentFactory] = None
    ):
        """
        初始化服務。

        Args:
            setup_repo: GameSetup 的 Repository
            state_repo: PlatformState 的 Repository
            news_repo: News 的 Repository
            action_repo: ActionRecord 的 Repository
            round_repo: GameRound 的 Repository
            agent: 假新聞生成 Agent
            agent_factory: Agent 工廠，用於潤稿功能
        """
        self.setup_repo = setup_repo
        self.state_repo = state_repo
        self.news_repo = news_repo
        self.action_repo = action_repo
        self.round_repo = round_repo
        self.agent = agent
        self.agent_factory = agent_factory

    def start_game(self) -> GameStartResponse:
        """
        遊戲初始化服務：建立初始設定、平台狀態、AI 行動與第一回合記錄。

        Returns:
            GameStartResponse: 遊戲初始化的響應 DTO
        """
        # 1. 隨機產生 platform 與 audience 組合
        platform_names = ["Facebook", "Instagram", "Twitter"]
        audiences = ["學生", "年輕族群", "中年族群"]
        random.shuffle(audiences)

        platforms = [{"name": name, "audience": audience} for name, audience in zip(platform_names, audiences)]

        # 產生唯一 session_id
        session_id = f"game_{uuid.uuid4().hex}"

        # 2. 建立 GameSetup
        self.setup_repo.create_game_setup(session_id=session_id, platforms=platforms)

        # 3. 建立 PlatformState（信任值預設 50）
        self.state_repo.create_initial_states(session_id=session_id, platforms=platforms)

        # 4. 隨機選一則新聞
        news = self.news_repo.get_random_news()

        # 5. 呼叫 FakeNewsAgent，產出訊息（假訊息或轉述）
        ai_platform = platforms[0]["name"]
        fake_content = self.agent.generate_fake_news(news)

        # 6. 建立 AI 的 ActionRecord
        action = self.action_repo.create_action_record(
            session_id=session_id,
            round_number=1,
            actor="ai",
            platform=ai_platform,
            content=fake_content
        )

        # 7. GM 評分結果（stub）
        trust_delta = +8
        spread_delta = +12
        self.action_repo.update_effectiveness(
            action_id=action.id,
            trust_change=trust_delta,
            spread_change=spread_delta,
            effectiveness="Medium",
            reach_count=800
        )

        # 8. 更新 PlatformState
        self.state_repo.update_platform_state(
            session_id=session_id,
            round_number=1,
            platform_name=ai_platform,
            trust_change_ai=trust_delta,
            spread_change=spread_delta
        )

        # 9. 建立第一回合
        self.round_repo.create_first_round(
            session_id=session_id,
            round_number=1,
            news_id=news.news_id
        )

        # 10. 回傳 DTO
        platform_states = self.state_repo.get_states_by_session(session_id)
        dto_platforms: List[PlatformStatus] = [
            PlatformStatus(
                platform=s.platform_name,
                player_trust=s.player_trust,
                ai_trust=s.ai_trust,
                spread=s.spread_rate
            ) for s in platform_states
        ]

        return GameStartResponse(
            session_id=session_id,
            platforms=dto_platforms,
            first_news=news.title,
            ai_platform=ai_platform,
            trust_change=trust_delta,
            spread_change=spread_delta
        )
        
    def polish_news(self, request: NewsPolishRequest) -> NewsPolishResponse:
        """
        使用 AI 系統當物潤稿新聞內容。
        
        Args:
            request: 潤稿請求物件
            
        Returns:
            潤稿後的新聞內容及建議
            
        Raises:
            BusinessLogicError: 處理過程中出錯
            ResourceNotFoundError: 找不到所需資源
        """
        if not self.agent_factory:
            raise BusinessLogicError("系統未設定 Agent Factory")
        
        # 準備 agent 變量
        variables = {
            "content": request.content,
            "requirements": request.requirements,
        }
        
        # 加入可選參數
        if request.sources:
            variables["sources"] = "\n".join(request.sources)
        if request.platform:
            variables["platform"] = request.platform
        if request.platform_user:
            variables["platform_user"] = request.platform_user
        if request.current_situation:
            variables["current_situation"] = request.current_situation
        if request.additional_context:
            # 將其他上下文屬性加入變量
            for k, v in request.additional_context.items():
                variables[k] = v
        logger.info(f"request.requirements: {request.requirements}")
        if request.requirements is None:
            request.requirements = "將文章潤色使其更吸引人、更有說服力"
        else:
            request.requirements = request.requirements
        # 調用 AI 代理
        try:
            result = self.agent_factory.run_agent_by_name(
                session_id=request.session_id,
                agent_name="news_polish_agent", 
                variables=variables,
                input_text=request.requirements
            )
            
            # 當用 structured_output 時，有可能是字典或JSON字符串
            result_data = None
            
            # 先判断是否為字典
            if isinstance(result, dict):
                result_data = result
            # 如果是字符串，嘗試解析為JSON
            elif isinstance(result, str):
                try:
                    result_data = json.loads(result)
                except json.JSONDecodeError:
                    # 如果不是有效的JSON，則直接用作潤稿內容
                    return NewsPolishResponse(
                        original_content=request.content,
                        polished_content=result
                    )
            
            # 如果得到了字典數據，則使用字典數據建立回應
            # TODO: 移除多餘邏輯
            if result_data and isinstance(result_data, dict):
                try:
                    return NewsPolishResponse(
                        original_content=request.content,
                        polished_content=result_data.get("polished_content", ""),
                        suggestions=result_data.get("suggestions"),
                        reasoning=result_data.get("reasoning")
                    )
                except Exception as e:
                    raise BusinessLogicError(f"無法組裝回應物件: {str(e)}")
            else:
                # 如果不是字典或解析失敗，則直接返回
                return NewsPolishResponse(
                    original_content=request.content,
                    polished_content=str(result)
                )
                
        except ResourceNotFoundError as e:
            # 找不到指定的 agent
            raise ResourceNotFoundError(
                message="找不到潤稿專用 Agent",
                resource_type="agent",
                resource_id="news_polish_agent"
            )
        except Exception as e:
            # 其他錯誤
            raise BusinessLogicError(f"潤稿過程發生錯誤: {str(e)}")
