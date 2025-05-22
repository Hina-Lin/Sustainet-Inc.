from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from pydantic import BaseModel
from src.application.dto.game_dto import (
    PlatformStatus, 
    NewsPolishRequest, NewsPolishResponse,
    GameStartRequest, GameStartResponse,
    AiTurnRequest, AiTurnResponse,
    PlayerTurnRequest, PlayerTurnResponse,
    StartNextRoundRequest, StartNextRoundResponse,
    ArticleMeta, ToolUsed,
    FakeNewsAgentResponse, GameMasterAgentResponse
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
from src.utils.text_utils import strip_code_block_and_space

# Tool related imports
from src.infrastructure.database.tool_repo import ToolRepository
from src.infrastructure.database.tool_usage_repo import ToolUsageRepository
from src.domain.logic.tool_effect_logic import ToolEffectLogic
from src.domain.models.tool import DomainTool
from src.application.dto.game_dto import ToolUsed as PlayerToolUsedDTO # Alias to avoid confusion with domain model
        
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
        logger.info(f"Executing turn for actor: {actor}", extra={"session_id": session_id, "round_number": round_number, "tool_used_request": [t.tool_name for t in tool_used] if tool_used else []})

        if not self.agent_factory:
            raise BusinessLogicError("系統未設定 Agent Factory")

        game = self._rebuild_game_state(session_id, round_number)
        article_to_evaluate: ArticleMeta
        target_platform_for_action: Optional[str]

        if actor == "ai":
            ai_article_meta = self._execute_ai_turn_logic(game, session_id)
            article_to_evaluate = ai_article_meta
            target_platform_for_action = ai_article_meta.target_platform
        elif actor == "player" and article:
            article_to_evaluate = article
            target_platform_for_action = article.target_platform
        else:
            # This case should ideally not be reached if request validation is done at API layer
            raise BusinessLogicError(f"無法為行動者 '{actor}' 確定要評估的文章或平台。")

        if not target_platform_for_action: 
            available_platforms = [p.name for p in game.platforms]
            target_platform_for_action = available_platforms[0] if available_platforms else "Facebook" # Default
            logger.warning(f"target_platform_for_action for actor '{actor}' was None, defaulting to {target_platform_for_action}")
            if article_to_evaluate: # Ensure article_to_evaluate is not None before setting attribute
                article_to_evaluate.target_platform = target_platform_for_action
            else:
                # This is a more severe issue - no article to evaluate means we can't proceed for GM
                raise BusinessLogicError(f"行動者 '{actor}' 沒有可評估的文章內容。")

        # Get original GM evaluation
        original_gm_result: GameMasterAgentResponse = self._get_gm_evaluation(
            game, article_to_evaluate, target_platform_for_action, round_number
        )
        logger.debug(f"Original GM evaluation for actor '{actor}'", extra={"session_id": session_id, "round": round_number, "gm_result": original_gm_result.model_dump()})
        
        final_gm_result = original_gm_result
        tool_application_details_for_db = [] # For storing AppliedToolEffectDetail from logic

        # Apply tool effects if player and tools are used
        if actor == "player" and tool_used:
            logger.info(f"Player '{session_id}' attempting to use tools: {[t.tool_name for t in tool_used]}", extra={"round": round_number})
            domain_tools_to_apply: List[DomainTool] = []
            for tool_dto in tool_used:
                logger.debug(f"Fetching tool: '{tool_dto.tool_name}' for player '{session_id}'", extra={"round": round_number})
                domain_tool = self.tool_repo.get_tool_by_name(tool_dto.tool_name)
                if domain_tool and (domain_tool.applicable_to == "player" or domain_tool.applicable_to == "both"):
                    logger.info(f"Tool '{tool_dto.tool_name}' found and applicable for player '{session_id}'.", extra={"tool_details": domain_tool.model_dump(), "round": round_number})
                    domain_tools_to_apply.append(domain_tool)
                else:
                    logger.warning(f"Player '{session_id}' attempted to use invalid, non-existent, or not applicable tool: '{tool_dto.tool_name}'", extra={"round": round_number, "tool_found": domain_tool.model_dump() if domain_tool else None})
            
            if domain_tools_to_apply:
                logger.debug(f"Applying effects for tools: {[t.tool_name for t in domain_tools_to_apply]} for player '{session_id}'", extra={"round": round_number})
                final_gm_result, tool_application_details_for_db = self.tool_effect_logic.apply_effects(
                    original_gm_result,
                    domain_tools_to_apply
                )
                logger.info(f"GM evaluation after applying tools for player '{session_id}'", extra={"round": round_number, "final_gm_result": final_gm_result.model_dump() if final_gm_result else None})
                logger.debug(f"Tool application details for DB for player '{session_id}'", extra={"round": round_number, "details": [d.model_dump() for d in tool_application_details_for_db]})
            else:
                logger.info(f"No applicable tools found to apply for player '{session_id}' from request: {[t.tool_name for t in tool_used]}", extra={"round": round_number})
        
        # Record action (this should happen before saving tool usage if action_id is FK)
        action_record = self.action_repo.create_action_record(
            session_id=session_id,
            round_number=round_number,
            actor=actor,
            platform=target_platform_for_action,
            content=article_to_evaluate.content
        )

        # Update database states using the final GM result (after tool effects)
        self._update_database_states(session_id, round_number, action_record, final_gm_result, actor)

        # Record tool usage in the database if any tools were effectively applied
        if tool_application_details_for_db:
            for usage_detail in tool_application_details_for_db:
                if usage_detail.is_effective: # Only record if tool was deemed effective by logic
                    logger.info(f"Recording usage for effective tool: '{usage_detail.tool_name}' for action_id: {action_record.id}", extra={"session_id": session_id, "round": round_number, "usage_detail": usage_detail.model_dump()})
                    self.tool_usage_repo.create_tool_usage_record(
                        action_id=action_record.id, 
                        usage_detail=usage_detail
                    )
                else:
                    logger.debug(f"Skipping DB record for non-effective tool application: '{usage_detail.tool_name}' for action_id: {action_record.id}", extra={"session_id": session_id, "round": round_number, "usage_detail": usage_detail.model_dump()})
        
        # TODO: Consider a Unit of Work pattern to commit all DB changes at the end of the service method.
        # For now, assuming individual repos handle their commits or a session is managed externally.

        # Convert to response DTO
        # The tool_used field in the response DTO should reflect what the player *attempted* to use (original list from request)
        # The tool_list is the list of all available tools for UI purposes.
        return self._convert_to_response(
            actor=actor, 
            session_id=session_id, 
            round_number=round_number, 
            article=article_to_evaluate, 
            gm_result=final_gm_result, # Pass the gm_result *after* tool effects
            tool_used=tool_used or [], 
            tool_list=tool_list or []
        )
    
    def _rebuild_game_state(self, session_id: str, round_number: int):
        setup_data = self.setup_repo.get_by_session_id(session_id)
        platform_states = self.state_repo.get_by_session_and_round(session_id, round_number)
        return self.game_state_logic.rebuild_game_from_db(session_id, round_number, setup_data, platform_states)
    
    def _execute_ai_turn_logic(self, game, session_id: str):
        # Select platform
        selected_platform = self.ai_turn_logic.select_platform(game.platforms)
        
        # Get news sources
        news_1 = self.news_repo.get_random_active_news()
        news_2 = self.news_repo.get_random_active_news()
        
        # Prepare variables for AI agent
        variables = self.ai_turn_logic.prepare_fake_news_variables(platform=selected_platform, news_1=news_1, news_2=news_2)
        
        # Call AI agent with response model
        agent_output: FakeNewsAgentResponse = self.agent_factory.run_agent_by_name(
            session_id=session_id,
            agent_name="fake_news_agent",
            variables=variables,
            input_text="input_text",
            response_model=FakeNewsAgentResponse
        )
        
        # Create ArticleMeta using agent_output and other system-set values
        article = self.ai_turn_logic.create_ai_article(
            result_data=agent_output, 
            platform=selected_platform, 
            source=news_1.source
        )
            
        return article
    
    def _get_gm_evaluation(self, game, article, target_platform, round_number) -> GameMasterAgentResponse:
        target_platform_obj = game.get_platform(target_platform)
        variables = self.gm_logic.prepare_evaluation_variables(
            article, target_platform_obj, game.platforms, round_number
        )
        
        gm_response: GameMasterAgentResponse = self.agent_factory.run_agent_by_name(
            session_id=game.session_id.value,
            agent_name="game_master_agent",
            variables=variables,
            input_text="input_text", 
            response_model=GameMasterAgentResponse
        )
        
        return gm_response # Directly return the Pydantic model instance
    
    def _parse_agent_result(self, result, agent_name: str):
        if isinstance(result, dict): 
            return result
        elif isinstance(result, BaseModel): # If agent_factory returned a Pydantic model
            # If downstream code expects a Pydantic model, return as is.
            # If it expects a dict, use result.model_dump().
            # Given our changes, _get_gm_evaluation now returns the model directly.
            return result # or result.model_dump() if dict is strictly needed by other callers
        elif isinstance(result, str):
            cleaned = strip_code_block_and_space(result)
            try:
                return json.loads(cleaned)
            except Exception:
                raise BusinessLogicError(f"{agent_name} 回傳格式錯誤，無法解析 JSON")
        else:
            raise BusinessLogicError(f"{agent_name} 回傳了不支援的格式")
    
    def _update_database_states(self, session_id, round_number, action, gm_result: GameMasterAgentResponse, actor):
        # gm_result is now GameMasterAgentResponse, access its fields directly
        self.action_repo.update_effectiveness(
            action_id=action.id,
            trust_change=gm_result.trust_change,
            spread_change=gm_result.spread_change,
            reach_count=gm_result.reach_count,
            effectiveness=gm_result.effectiveness,
            simulated_comments=gm_result.simulated_comments
        )

        # Update platform states
        for state in gm_result.platform_status: # Iterate over Pydantic models in the list
            self.state_repo.update_platform_state(
                session_id=session_id,
                round_number=round_number,
                platform_name=state.platform_name,
                player_trust=state.player_trust,
                ai_trust=state.ai_trust,
                spread_rate=state.spread
            )

        # Mark round as completed for player turns
        if actor == "player":
            self.round_repo.update_game_round(
                session_id=session_id,
                round_number=round_number,
                is_completed=True
            )
    
    def _convert_to_response(self, actor, session_id, round_number, article, gm_result: GameMasterAgentResponse, tool_used, tool_list):
        platforms_info = self.setup_repo.get_by_session_id(session_id).platforms
        
        # Clean article data
        article_dict = article.model_dump()
        article_dict["veracity"] = None
        if actor == "ai":
            article_dict["target_platform"] = None
        article_safe = ArticleMeta.model_validate(article_dict)
        
        # gm_result.platform_status is already a list of GameMasterAgentPlatformStatus models.
        # We need to convert them to dicts if PlatformStatus DTO is different or for the response structure.
        # Assuming PlatformStatus DTO is what's expected in the final response.
        platform_status_objs = [
            PlatformStatus(
                platform_name=ps.platform_name,
                player_trust=ps.player_trust,
                ai_trust=ps.ai_trust,
                spread_rate=ps.spread
                # session_id and round_number might be missing if not part of GameMasterAgentPlatformStatus
                # and if PlatformStatus requires them. Let's assume they are optional or set elsewhere.
            ).model_dump() for ps in gm_result.platform_status
        ]

        response_dict = dict(
            session_id=session_id,
            round_number=round_number,
            actor=actor,
            article=article_safe,
            trust_change=gm_result.trust_change,
            reach_count=gm_result.reach_count,
            spread_change=gm_result.spread_change,
            platform_setup=platforms_info,
            platform_status=platform_status_objs, # List of dicts
            tool_used=tool_used,
            tool_list=tool_list,
            effectiveness=gm_result.effectiveness,
            simulated_comments=gm_result.simulated_comments
        )

        if actor == "ai":
            return AiTurnResponse(**response_dict)
        else:
            return PlayerTurnResponse(**response_dict)
    def game_master(
        self,   
        session_id: str,
        round_number: int,
        article: ArticleMeta,
        platform: str,
        trust_multiplier: float = 1.0,
        spread_multiplier: float = 1.0,
    ) -> dict:
        # Rebuild game state and evaluate using domain logic
        game = self._rebuild_game_state(session_id, round_number)
        return self._get_gm_evaluation(game, article, platform, round_number)

    @staticmethod
    def platform_status_from_dict(ps: dict) -> PlatformStatus:
        return PlatformStatus(
            platform_name=ps["platform_name"],
            player_trust=ps["player_trust"],
            ai_trust=ps["ai_trust"],
            spread_rate=ps["spread"]
        )
                
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