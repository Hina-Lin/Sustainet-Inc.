"""
Game 相關的服務層邏輯。
處理遊戲的初始化、回合管理等操作。
"""

from typing import List
import random
import uuid

from src.application.dto.game_dto import GameStartResponse, PlatformStatus
from src.infrastructure.database.game_setup_repo import GameSetupRepository
from src.infrastructure.database.platform_state_repo import PlatformStateRepository
from src.infrastructure.database.news_repo import NewsRepository
from src.infrastructure.database.action_record_repo import ActionRecordRepository
from src.infrastructure.database.game_round_repo import GameRoundRepository

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
        agent: FakeNewsAgent
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
        """
        self.setup_repo = setup_repo
        self.state_repo = state_repo
        self.news_repo = news_repo
        self.action_repo = action_repo
        self.round_repo = round_repo
        self.agent = agent

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
