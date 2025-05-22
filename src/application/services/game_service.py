"""
Game 相關的服務層邏輯。
處理遊戲的初始化、回合管理等操作。
"""

from typing import List, Optional, Dict, Any
import random
import uuid
import json
from datetime import datetime
import re

from src.application.dto.game_dto import (
    PlatformStatus, 
    NewsPolishRequest, NewsPolishResponse,
    GameStartRequest, GameStartResponse,
    AiTurnRequest, AiTurnResponse,
    PlayerTurnRequest, PlayerTurnResponse,
    StartNextRoundRequest, StartNextRoundResponse,
    ArticleMeta, ToolUsed
    )
from src.infrastructure.database.game_setup_repo import GameSetupRepository
from src.infrastructure.database.platform_state_repo import PlatformStateRepository
from src.infrastructure.database.news_repo import NewsRepository
from src.infrastructure.database.action_record_repo import ActionRecordRepository
from src.infrastructure.database.game_round_repo import GameRoundRepository
from src.domain.logic.agent_factory import AgentFactory
from src.utils.exceptions import BusinessLogicError, ResourceNotFoundError
from src.utils.logger import logger

# 移除 markdown code block 的輔助函數
def strip_code_block_and_space(text: str) -> str:
    # 砍 code block
    cleaned = re.sub(r"^```[a-zA-Z]*\n", "", text)
    cleaned = re.sub(r"\n?```$", "", cleaned)
    # 砍全型、半型、no-break 空白
    cleaned = cleaned.strip().replace('\u3000', '').replace('\xa0', '')
    return cleaned
        
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
        agent_factory: Optional[AgentFactory] = None,
        tools_repo: Optional[Any] = None
    ):
        """
        初始化服務。

        Args:
            setup_repo: GameSetup 的 Repository
            state_repo: PlatformState 的 Repository
            news_repo: News 的 Repository
            action_repo: ActionRecord 的 Repository
            round_repo: GameRound 的 Repository
            agent_factory: Agent 工廠，用於潤稿功能
        """
        self.setup_repo = setup_repo
        self.state_repo = state_repo
        self.news_repo = news_repo
        self.action_repo = action_repo
        self.round_repo = round_repo
        self.agent_factory = agent_factory
        self.tools_repo = tools_repo

    # ========================== 開始遊戲 ==========================

    def start_game(self, request: Optional[GameStartRequest] = None) -> GameStartResponse:
        """
        開始遊戲，初始化遊戲狀態。
        1. 產生唯一的 session_id
        2. 隨機產生三個平台與受眾的組合
        3. 建立 GameSetup 紀錄
        4. 建立第一回合的 PlatformState 紀錄
        5. 建立第一回合的 GameRound 紀錄
        6. 呼叫 AI 進行第一回合的操作    
    
        Returns:
            GameStartResponse: 回傳本次遊戲初始化與第一回合 AI 行動的所有資訊，欄位如下：
    
            - session_id: 遊戲識別碼
            - round_number: 回合數（預設為 1）
            - article: ArticleMeta，AI 發布的假新聞內容
            - actor: 本回合行動者（"ai"）
            - trust_change: 本回合造成的信任值變化
            - reach_count: 本回合的觸及人數
            - spread_change: 本回合造成的傳播率變化
            - platform_setup: 平台與受眾的組合（初始化時的 platforms）
            - platform_status: 所有平台目前的狀態（信任值、傳播率等）
            - tool_list: 所有可用工具的名稱、描述及啟用狀況
            - tool_used: 本回合實際使用的工具（如有）

        """
        # 產生唯一 session_id
        session_id = f"game_{uuid.uuid4().hex}"
        round_number = 1 # 第一回合
        
        # 隨機產生 platform 與 audience 組合
        platform_names = ["Facebook", "Instagram", "Thread"]
        audiences = ["年輕族群", "中年族群", "老年族群"]
        random.shuffle(audiences)
        platforms = [{"name": name, "audience": audience} for name, audience in zip(platform_names, audiences)]
        
        # 建立 GameSetup 紀錄
        self.setup_repo.create_game_setup(
            session_id=session_id, 
            platforms=platforms, 
            player_initial_trust=50, 
            ai_initial_trust=50
            )

        # 建立第一回合 PlatformState（玩家信任值, AI 信任值, 傳播率皆預設 50）
        self.state_repo.create_all_platforms_states(
            session_id=session_id,
            round_number=round_number,
            platforms=platforms,  # 這是一個 list of dict，例如 [{"name": "Facebook"}, ...]
            player_trust=50,
            ai_trust=50,
            spread_rate=50
        )
        
        # 建立第一回合 GameRound 紀錄
        self.round_repo.create_game_round(
            session_id=session_id,
            round_number=round_number,
            is_completed=False
        )
              
        # 進入 AI 先攻回合
        ai_request = AiTurnRequest(session_id=session_id, round_number=round_number)
        ai_response = self.ai_turn(ai_request)
        return GameStartResponse(**ai_response.model_dump())

    # ========================== AI 回合 ==========================
    
    def ai_turn(self, request: AiTurnRequest) -> AiTurnResponse:
        return self._generic_turn(
            actor="ai",
            session_id=request.session_id,
            round_number=request.round_number,
            article=None,
            tool_used=[],
            tool_list=None
        )
    
    # ========================== 玩家回合 ==========================

    def player_turn(self, request: PlayerTurnRequest) -> PlayerTurnResponse:
        return self._generic_turn(
            actor="player",
            session_id=request.session_id,
            round_number=request.round_number,
            article=request.article,
            tool_used=request.tool_used or [],
            tool_list=request.tool_list
        )

    # ========================== 下一回合 ==========================

    def start_next_round(self, request: StartNextRoundRequest) -> StartNextRoundResponse:
        """
        進入下一回合，內部自動 +1，建立新狀態並啟動 AI 行動。
        """
        session_id = request.session_id
        
        # 查詢目前最大回合數，並自動 +1
        last_round = self.round_repo.get_latest_round_by_session(session_id)
        if not last_round:
            raise BusinessLogicError("找不到上一回合紀錄")
        round_number = last_round.round_number + 1

        # 建立新回合的 PlatformState
        platforms = self.setup_repo.get_by_session_id(session_id).platforms
        self.state_repo.create_all_platforms_states(
            session_id=session_id,
            round_number=round_number,
            platforms=platforms
        )
        
        # 建立 GameRound
        self.round_repo.create_game_round(
            session_id=session_id,
            round_number=round_number,
            is_completed=False
        )
        # 直接呼叫 AI 先攻
        ai_request = AiTurnRequest(session_id=session_id, round_number=round_number)
        ai_response = self.ai_turn(ai_request)
        return StartNextRoundResponse(**ai_response.model_dump())

    # ========================== 回合主邏輯（共用） ==========================

    def _generic_turn(
        self,
        actor: str,
        session_id: str,
        round_number: int,
        article: Optional[ArticleMeta],
        tool_used: Optional[List[ToolUsed]],
        tool_list: Optional[List[Dict[str, Any]]]
    ):
        """
        回合主流程（AI/玩家共用）。AI回合自動產生貼文；玩家回合用戶提供貼文與工具。
        """
        if not self.agent_factory:
            raise BusinessLogicError("系統未設定 Agent Factory")

        # 取得三平台設定
        platforms_info = self.setup_repo.get_by_session_id(session_id).platforms

        # ======== AI 回合邏輯 ========
        if actor == "ai":
            ai_platform_info = random.choice(platforms_info)
            target_platform = ai_platform_info["name"]
            target_audience = ai_platform_info["audience"]
            # 取兩則新聞
            news_1 = self.news_repo.get_random_active_news()
            news_2 = self.news_repo.get_random_active_news()
            # 工具（這邊可擴充取得 AI 可用工具）
            all_tools = []
            tool_used = []
            used_tool_descriptions = "無可用工具"
            # TODO: 這邊要從 tools_repo 取得所有可用工具
            """
            if hasattr(self, 'tools_repo') and self.tools_repo is not None:
                all_tools = self.tools_repo.get_all_tools()
                tool_used = [tool for tool in all_tools if tool.get("applicable_to") in ["ai", "both"]]
                used_tool_descriptions = ", ".join([t.get("description") for t in tool_used if t.get("description")])
            """

            # 準備 prompt 變數
            variables = {
                "news_1": news_1.content,
                "news_1_veracity": news_1.veracity,
                "news_2": news_2.content,
                "news_2_veracity": news_2.veracity,
                "target_platform": target_platform,
                "target_audience": target_audience,
                "used_tool_descriptions": used_tool_descriptions
            }

            # 呼叫 FakeNewsAgent 生成假新聞
            try:
                result = self.agent_factory.run_agent_by_name(
                session_id=session_id,
                agent_name="fake_news_agent",
                variables=variables,
                input_text="input_text"
                )

                # 統一解析 output
                if isinstance(result, dict):
                    result_data = result
                elif isinstance(result, str):
                    cleaned = strip_code_block_and_space(result)
                    logger.debug("[FakeNewsAgent] 淨化後內容：%r", cleaned)

                    try:
                        result_data = json.loads(cleaned)
                    except Exception:
                        raise BusinessLogicError("FakeNewsAgent 回傳格式錯誤，無法解析 JSON")
                else:
                    raise BusinessLogicError("FakeNewsAgent 回傳了不支援的格式")

                # 組成 ArticleMeta
                article = ArticleMeta(
                    title=result_data.get("title"),
                    content=result_data.get("content"),
                    polished_content=None,
                    image_url=result_data.get("image_url"),
                    source=news_1.source, # 只給一個
                    author="ai",
                    published_date=datetime.now().isoformat(),
                    target_platform=target_platform,  
                    requirement=None,
                    veracity=result_data.get("veracity")  
                )
            except ResourceNotFoundError:
                raise ResourceNotFoundError(
                    message="找不到 FakeNewsAgent",
                    resource_type="agent",
                    resource_id="FakeNewsAgent"
                )
            except Exception as e:
                raise BusinessLogicError(f"生成假新聞過程發生錯誤: {str(e)}")
      
        # ======== 玩家回合邏輯 ========
        else:
            all_tools = tool_list or []
            # 玩家自己決定 target_platform
            target_platform = article.target_platform

        # 建立 ActionRecord
        action = self.action_repo.create_action_record(
            session_id=session_id,
            round_number=round_number,
            actor=actor,
            platform=target_platform,
            content=article.content
        )

        # AI: 更新 GameRound news_id
        if actor == "ai":
            self.round_repo.update_game_round(
                session_id=session_id,
                round_number=round_number,
                news_id=getattr(news_1, "news_id", None),
            )

        # 工具倍率計算（預設 1.0，這裡可擴充）
        trust_multiplier = 1.0
        spread_multiplier = 1.0

        # GM 評分
        gm_result = self.game_master(
            session_id=session_id,
            round_number=round_number,
            article=article,
            platform=target_platform,
            trust_multiplier=trust_multiplier,
            spread_multiplier=spread_multiplier
        )
        trust_change = gm_result["trust_change"]
        spread_change = gm_result["spread_change"]
        reach_count = gm_result["reach_count"]
        platform_status = gm_result["platform_status"]
        effectiveness = gm_result.get("effectiveness")
        simulated_comments = gm_result.get("simulated_comments")

        # 更新 ActionRecord
        self.action_repo.update_effectiveness(
            action_id=action.id,
            trust_change=trust_change,
            spread_change=spread_change,
            reach_count=reach_count,
            effectiveness=effectiveness,
            simulated_comments=simulated_comments
        )

        # 更新 PlatformState
        for state in platform_status:
            self.state_repo.update_platform_state(
                session_id=session_id,
                round_number=round_number,
                platform_name=state["platform_name"],
                player_trust=state["player_trust"],
                ai_trust=state["ai_trust"],
                spread_rate=state["spread"]
            )

        # 玩家回合才設 is_completed
        if actor == "player":
            self.round_repo.update_game_round(
                session_id=session_id,
                round_number=round_number,
                news_id=None,
                is_completed=True
            )

        # Output 結構整理（去掉 article veracity, AI 不顯示 target_platform）
        article_dict = article.model_dump()
        article_dict["veracity"] = None
        if actor == "ai":
            article_dict["target_platform"] = None
        article_safe = ArticleMeta.model_validate(article_dict)
        platform_status_objs = [self.platform_status_from_dict(ps).model_dump() for ps in platform_status]

        # Response 組裝
        response_dict = dict(
            session_id=session_id,
            round_number=round_number,
            actor=actor,
            article=article_safe,
            trust_change=trust_change,
            reach_count=reach_count,
            spread_change=spread_change,
            platform_setup=platforms_info,
            platform_status=platform_status_objs,
            tool_used=tool_used or [],
            tool_list=all_tools,
            effectiveness=effectiveness,
            simulated_comments=simulated_comments
        )
        logger.debug("platform_status 原始內容: %r", platform_status)
        logger.debug("platform_status 組裝成物件後: %r", platform_status_objs)
        logger.debug("response_dict 最終平台數: %d", len(response_dict["platform_status"]))

        # 輸出對應型別
        if actor == "ai":
            return AiTurnResponse(**response_dict)
        else:
            return PlayerTurnResponse(**response_dict)
   
    # ========================== GM 評分 ==========================
    def game_master(
        self,   
        session_id: str,
        round_number: int,
        article: ArticleMeta,
        platform: str,
        trust_multiplier: float = 1.0,
        spread_multiplier: float = 1.0,
    ) -> dict:
        """
        GameMaster：僅負責計算/回傳評分，不做任何 DB 寫入。
    
        Args:
            session_id: 遊戲場次 ID
            round_number: 回合數
            article: ArticleMeta（本回合發文的所有欄位）
            platform: 本回合發文的平台名稱
            trust_multiplier: 工具倍率，影響信任值變化
            spread_multiplier: 工具倍率，影響傳播率變化
    
        Returns:
            dict: 包含本回合評分結果，格式如下：
                {
                    "trust_change": int,         # 本回合造成的信任值變化
                    "spread_change": int,        # 本回合造成的傳播率變化
                    "reach_count": int,          # 本回合的觸及人數
                    "platform_status": [         # 各平台最新狀態
                        {
                            "platform_name": str,
                            "player_trust": int,
                            "ai_trust": int,
                            "spread": int
                        },
                        ...
                    ]
                }
    
        流程說明：
            1. 取得三平台與受眾組合
            2. 取得三平台當前狀態
            3. 組成平台摘要字串，傳給 GM agent
            4. 呼叫 GameMaster agent 進行評分
            5. 解析回傳結果，回傳評分與平台狀態
        """  
        
        if not self.agent_factory:
            raise BusinessLogicError("系統未設定 Agent Factory")
    
        # === 從 GameSetup 撈出三個平台與對應受眾 ===
        game_setup = self.setup_repo.get_by_session_id(session_id)
        platforms_info = game_setup.platforms  # JSON 欄位：list of {"name": ..., "audience": ...}
        audience_map = {p["name"]: p["audience"] for p in platforms_info}

        # === 撈出三個平台當前狀態 ===
        platform_states = self.state_repo.get_by_session_and_round(
            session_id=session_id,
            round_number=round_number
        )

        # === 組成平台摘要字串給 agent 參考（含受眾）===
        platform_state_summary = "\n".join([
            f"{s.platform_name}（受眾：{audience_map.get(s.platform_name)}） | 玩家信任: {s.player_trust} | AI信任: {s.ai_trust} | 傳播率: {s.spread_rate}%"
            for s in platform_states
        ])

        if article.polished_content:
            article.content = article.polished_content

        # === 準備傳給 GM agent 的變數 ===
        variables = {
            "title": article.title,
            "content": article.content,
            "image_url": article.image_url,
            "source": article.source,
            "veracity": article.veracity,
            "target_platform": platform,
            "author": article.author,
            "trust_multiplier": trust_multiplier,
            "spread_multiplier": spread_multiplier,
            "platform_state_summary": platform_state_summary,
            "round_number": round_number
        }

        # === 呼叫 GameMaster Agent 評分 ===
        try:
            result = self.agent_factory.run_agent_by_name(
                session_id=session_id,
                agent_name="game_master_agent",
                variables=variables,
                input_text="input_text"
            )

            # 嘗試解析回傳 JSON 結果
            if isinstance(result, dict):
                result_data = result
            elif isinstance(result, str):
                cleaned = strip_code_block_and_space(result)
                logger.debug("[GameMasterAgent] 淨化後內容：%r", cleaned)
                try:
                    result_data = json.loads(cleaned)
                except Exception as e:
                    raise BusinessLogicError(f"GameMasterAgent 回傳格式錯誤，無法解析 JSON: {repr(cleaned)} | {str(e)}")
            else:
                # 強制賦值，避免後面用到 cleaned 變數未定義
                cleaned = None
                raise BusinessLogicError("GameMasterAgent 回傳了不支援的格式")

    
            # 基本資料與可選欄位
            return {
                "trust_change": result_data.get("trust_change", 0),
                "spread_change": result_data.get("spread_change", 0),
                "reach_count": result_data.get("reach_count", 0),
                "platform_status": result_data.get("platform_status", []),
                "effectiveness": result_data.get("effectiveness"),
                "simulated_comments": result_data.get("simulated_comments")
            }
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message="找不到 GameMasterAgent",
                resource_type="agent",
                resource_id="GameMasterAgent"
            )

        except Exception as e:
            raise BusinessLogicError(f"GameMaster 評分過程發生錯誤: {str(e)}")

    @staticmethod
    def platform_status_from_dict(ps: dict) -> PlatformStatus:
        return PlatformStatus(
            platform_name=ps["platform_name"],
            player_trust=ps["player_trust"],
            ai_trust=ps["ai_trust"],
            spread_rate=ps["spread"]
        )
                
    # ========== 新聞潤稿 ==========

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
                input_text="input_text"
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