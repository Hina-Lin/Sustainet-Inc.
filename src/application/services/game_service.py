import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.application.dto.game_dto import (
    NewsPolishRequest, NewsPolishResponse,
    GameStartRequest, GameStartResponse,
    AiTurnRequest, AiTurnResponse,
    PlayerTurnRequest, PlayerTurnResponse,
    StartNextRoundRequest, StartNextRoundResponse,
    ArticleMeta
)
from src.infrastructure.database.game_setup_repo import GameSetupRepository
from src.infrastructure.database.platform_state_repo import PlatformStateRepository
from src.infrastructure.database.news_repo import NewsRepository
from src.infrastructure.database.action_record_repo import ActionRecordRepository
from src.infrastructure.database.game_round_repo import GameRoundRepository
from src.domain.logic.agent_factory import AgentFactory
from src.domain.logic.game_initialization import GameInitializationLogic
from src.domain.logic.ai_turn import AiTurnLogic
from src.domain.logic.game_master import GameMasterLogic
from src.domain.logic.game_state import GameStateLogic
from src.domain.logic.player_action import PlayerActionLogic
from src.utils.exceptions import BusinessLogicError, ResourceNotFoundError
from src.utils.logger import logger

# Tool related imports
from src.infrastructure.database.tool_repo import ToolRepository
from src.infrastructure.database.tool_usage_repo import ToolUsageRepository
from src.domain.logic.tool_effect_logic import ToolEffectLogic
from src.application.dto.game_dto import ToolUsed as PlayerToolUsedDTO

# New imports for refactored architecture
from src.domain.logic.turn_execution import TurnExecutionLogic
from src.domain.logic.game_state_manager import GameStateManager
from src.domain.logic.response_converter import ResponseConverter
from src.domain.logic.tool_availability_logic import ToolAvailabilityLogic
        
class GameService:
    def __init__(
        self,
        setup_repo: GameSetupRepository,
        state_repo: PlatformStateRepository,
        news_repo: NewsRepository,
        action_repo: ActionRecordRepository,
        round_repo: GameRoundRepository,
        tool_repo: ToolRepository,
        tool_usage_repo: ToolUsageRepository,
        agent_factory: Optional[AgentFactory] = None,
    ):
        self.setup_repo = setup_repo
        self.state_repo = state_repo
        self.news_repo = news_repo
        self.action_repo = action_repo
        self.round_repo = round_repo
        self.agent_factory = agent_factory
        self.tool_repo = tool_repo
        self.tool_usage_repo = tool_usage_repo
        
        # Domain logic instances
        self.game_init_logic = GameInitializationLogic()
        self.ai_turn_logic = AiTurnLogic()
        self.gm_logic = GameMasterLogic()
        self.game_state_logic = GameStateLogic()
        self.player_action_logic = PlayerActionLogic()
        self.tool_effect_logic = ToolEffectLogic()
        
        # New refactored components
        self.turn_execution_logic = TurnExecutionLogic(
            self.ai_turn_logic, self.tool_repo, self.agent_factory, self.news_repo
        )
        self.game_state_manager = GameStateManager(
            setup_repo, state_repo, action_repo, tool_usage_repo,
            self.game_state_logic, self.gm_logic, self.tool_effect_logic, self.agent_factory
        )
        self.tool_availability_logic = ToolAvailabilityLogic(tool_repo)
        self.response_converter = ResponseConverter(setup_repo, self.tool_availability_logic)

    def start_game(self, request: Optional[GameStartRequest] = None) -> GameStartResponse:
        # Create new game using domain logic
        game = self.game_init_logic.create_new_game()
        
        # Save to database
        platforms_data = self.game_state_logic.convert_platforms_to_db_format(game.platforms)
        
        self.setup_repo.create_game_setup(
            session_id=game.session_id.value, 
            platforms=platforms_data, 
            player_initial_trust=50, 
            ai_initial_trust=50
        )

        self.state_repo.create_all_platforms_states(
            session_id=game.session_id.value,
            round_number=game.current_round,
            platforms=platforms_data,
            player_trust=50,
            ai_trust=50,
            spread_rate=50
        )
        
        self.round_repo.create_game_round(
            session_id=game.session_id.value,
            round_number=game.current_round,
            is_completed=False
        )
              
        # Execute AI turn
        ai_request = AiTurnRequest(session_id=game.session_id.value, round_number=game.current_round)
        ai_response = self.ai_turn(ai_request)
        return GameStartResponse(**ai_response.model_dump())

    def ai_turn(self, request: AiTurnRequest) -> AiTurnResponse:
        return self._execute_turn(
            actor="ai",
            session_id=request.session_id,
            round_number=request.round_number,
            article=None,
            tool_used=[],
            tool_list=None
        )

    def player_turn(self, request: PlayerTurnRequest) -> PlayerTurnResponse:
        return self._execute_turn(
            actor="player",
            session_id=request.session_id,
            round_number=request.round_number,
            article=request.article,
            tool_used=request.tool_used or [],
            tool_list=request.tool_list
        )

    def start_next_round(self, request: StartNextRoundRequest) -> StartNextRoundResponse:
        session_id = request.session_id
        
        last_round = self.round_repo.get_latest_round_by_session(session_id)
        if not last_round:
            raise BusinessLogicError("找不到上一回合紀錄")
        round_number = last_round.round_number + 1

        platforms = self.setup_repo.get_by_session_id(session_id).platforms
        self.state_repo.create_all_platforms_states(
            session_id=session_id,
            round_number=round_number,
            platforms=platforms
        )
        
        self.round_repo.create_game_round(
            session_id=session_id,
            round_number=round_number,
            is_completed=False
        )
        
        ai_request = AiTurnRequest(session_id=session_id, round_number=round_number)
        ai_response = self.ai_turn(ai_request)
        return StartNextRoundResponse(**ai_response.model_dump())

    def _execute_turn(
        self,
        actor: str,
        session_id: str,
        round_number: int,
        article: Optional[ArticleMeta],
        tool_used: Optional[List[PlayerToolUsedDTO]],
        tool_list: Optional[List[Dict[str, Any]]]
    ):
        """重構後的回合執行 - 只負責流程編排"""
        logger.info(f"Executing turn for actor: {actor}", extra={
            "session_id": session_id, 
            "round_number": round_number
        })

        if not self.agent_factory:
            raise BusinessLogicError("系統未設定 Agent Factory")

        # 1. 重建遊戲狀態
        game = self.game_state_manager.rebuild_game_state(session_id, round_number)
        
        # 2. 執行行動者回合
        turn_result = self.turn_execution_logic.execute_actor_turn(
            game=game,
            actor=actor,
            session_id=session_id,
            round_number=round_number,
            article=article,
            player_tools=tool_used
        )
        
        # 3. 評估效果並應用工具
        game_turn_result = self.game_state_manager.evaluate_and_apply_effects(
            turn_result, game, self.tool_repo
        )
        
        # 4. 持久化結果
        action_id = self.game_state_manager.persist_turn_result(game_turn_result)
        
        # 5. 標記玩家回合完成
        if actor == "player":
            self.round_repo.update_game_round(
                session_id=session_id,
                round_number=round_number,
                is_completed=True
            )
        
        # 6. 轉換為回應 DTO
        response = self.response_converter.to_turn_response(
            game_turn_result, tool_list
        )
        
        logger.info(f"Completed {actor} turn", extra={
            "session_id": session_id,
            "round_number": round_number,
            "action_id": action_id
        })
        
        return response
    
    def polish_news(self, request: NewsPolishRequest) -> NewsPolishResponse:
        if not self.agent_factory:
            raise BusinessLogicError("系統未設定 Agent Factory")
        
        variables = {"content": request.content, "requirements": request.requirements or "將文章潤色使其更吸引人、更有說服力"}
        
        if request.sources:
            variables["sources"] = "\n".join(request.sources)
        if request.platform:
            variables["platform"] = request.platform
        if request.platform_user:
            variables["platform_user"] = request.platform_user
        if request.current_situation:
            variables["current_situation"] = request.current_situation
        if request.additional_context:
            variables.update(request.additional_context)
        
        try:
            result = self.agent_factory.run_agent_by_name(
                session_id=request.session_id,
                agent_name="news_polish_agent", 
                variables=variables,
                input_text="input_text"
            )
            
            if isinstance(result, dict):
                return NewsPolishResponse(
                    original_content=request.content,
                    polished_content=result.get("polished_content", ""),
                    suggestions=result.get("suggestions"),
                    reasoning=result.get("reasoning")
                )
            elif isinstance(result, str):
                try:
                    result_data = json.loads(result)
                    return NewsPolishResponse(
                        original_content=request.content,
                        polished_content=result_data.get("polished_content", ""),
                        suggestions=result_data.get("suggestions"),
                        reasoning=result_data.get("reasoning")
                    )
                except json.JSONDecodeError:
                    return NewsPolishResponse(
                        original_content=request.content,
                        polished_content=result
                    )
            else:
                return NewsPolishResponse(
                    original_content=request.content,
                    polished_content=str(result)
                )
                
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message="找不到潤稿專用 Agent",
                resource_type="agent",
                resource_id="news_polish_agent"
            )
        except Exception as e:
            raise BusinessLogicError(f"潤稿過程發生錯誤: {str(e)}")