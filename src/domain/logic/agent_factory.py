import pkgutil
import importlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from agno.agent import Agent as AgnoAgent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.models.anthropic import Claude

from src.utils.variables_render import VariablesRenderer
from src.utils.exceptions import ResourceNotFoundError, BusinessLogicError
from src.utils.logger import logger
from src.config.settings import settings
from src.infrastructure.database.agent_repo import AgentRepository
from src.infrastructure.database.models.agent import Agent
from src.infrastructure.database.session import get_storage

import agno.tools as tools_pkg

# 工具類註冊表
TOOL_CLASSES: Dict[str, type] = {}

# 添加額外的工具目錄
extra_tools_dir = Path.cwd() / "src" / "domain" / "logic" / "tools"
if extra_tools_dir.is_dir():
    logger.info(f"添加額外工具目錄: {extra_tools_dir}")
    tools_pkg.__path__.append(str(extra_tools_dir))
else:
    logger.warning(f"額外工具目錄不存在: {extra_tools_dir}")
    
# 根據環境載入工具
if settings.app_env == "development":
    logger.info("開發環境：僅載入預設工具")
    # 載入預設工具
    try:
        from agno.tools.calculator import CalculatorTools
        TOOL_CLASSES["CalculatorTools"] = CalculatorTools
        logger.debug("添加默認 CalculatorTools")
    except ImportError:
        logger.warning("無法載入默認 CalculatorTools")

    try:
        from src.domain.logic.tools.placeholder import Placeholder
        TOOL_CLASSES["Placeholder"] = Placeholder
        logger.debug("添加默認 Placeholder")
    except ImportError:
        logger.warning("無法載入默認 Placeholder")
else:
    # 生產環境載入所有工具
    for _, mod_name, _ in pkgutil.iter_modules([str(extra_tools_dir)]):
        try:
            module = importlib.import_module(f"src.domain.logic.tools.{mod_name}")
            logger.debug(f"成功載入工具模組: {mod_name}")
            
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and hasattr(obj, "execute"):
                    TOOL_CLASSES[attr] = obj
                    logger.debug(f"註冊工具類: {attr}")
        except ImportError as e:
            logger.warning(f"跳過無法載入的工具模組 '{mod_name}': {e}")
            continue

logger.info(f"系統中可用的工具類列表: {', '.join(TOOL_CLASSES.keys())}")

class AgentFactory:
    """
    Agent Factory 服務，負責創建和管理 Agent
    """
    
    def __init__(self, agent_repo: AgentRepository):
        """
        初始化 Agent Factory 服務。
        
        Args:
            agent_repo: Agent Repository 實例
        """
        self.agent_repo = agent_repo
        self.storage = get_storage()

    def run_agent_by_name(self,
                         session_id: str,
                         agent_name: str,
                         variables: Dict[str, Any],
                         input_text: Optional[str] = None,
                         response_model: Optional[type] = None,
                         **kwargs) -> Any:
        """創建、執行指定名稱的代理，並返回結果內容。

        Args:
            session_id: 會話 ID
            agent_name: 要運行的代理名稱
            variables: 傳遞給代理模板的變數
            input_text: 傳遞給 agent.run 的輸入文本
            response_model: 可選的響應模型類別
            **kwargs: 額外參數

        Returns:
            代理執行結果內容

        Raises:
            ResourceNotFoundError: 如果找不到代理配置
            BusinessLogicError: 如果代理配置無效或執行失敗
        """
        try:
            # 1. 獲取 Agent 資料
            agent = self.agent_repo.get_by_name(agent_name)
            if not agent:
                raise ResourceNotFoundError(f"找不到名稱為 {agent_name} 的 Agent")

            interal_session_id = f"{session_id}_{agent_name}"

            # 2. 處理變數替換
            if variables:
                if agent.description:
                    agent.description = VariablesRenderer.render_variables(agent.description, variables)
                if agent.instruction:
                    agent.instruction = VariablesRenderer.render_variables(agent.instruction, variables)

            # 3. 創建 Agent 實例
            agent_instance = self._create_agent_from_data(interal_session_id, agent, variables, response_model)
            if not agent_instance:
                raise BusinessLogicError("無法創建 Agent 實例")

            # 4. 執行 Agent
            result = agent_instance.run(input_text)
            
            # 5. 處理結果
            if hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
            
            return content.strip() if isinstance(content, str) else content

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"執行代理 {agent_name} (session: {session_id}) 時發生錯誤: {str(e)}")
            raise BusinessLogicError(f"執行代理失敗: {str(e)}")

    def create_agent(self, agent_id: int, session_id: str = None, variables: Dict[str, Any] = None) -> Any:
        """
        根據 ID 創建 Agent。

        Args:
            agent_id: Agent ID
            session_id: 會話 ID
            variables: 變數字典

        Returns:
            創建的 Agent 實例

        Raises:
            ResourceNotFoundError: 如果找不到 Agent
            BusinessLogicError: 如果創建失敗
        """
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise ResourceNotFoundError(f"找不到 ID 為 {agent_id} 的 Agent")
        
        return self._create_agent_from_data(session_id, agent, variables, None)

    def create_agent_by_name(self, session_id: str, agent_name: str, variables: Dict[str, Any] = None) -> Any:
        """
        根據名稱創建 Agent。

        Args:
            session_id: 會話 ID
            agent_name: Agent 名稱
            variables: 變數字典

        Returns:
            創建的 Agent 實例

        Raises:
            ResourceNotFoundError: 如果找不到 Agent
            BusinessLogicError: 如果創建失敗
        """
        agent = self.agent_repo.get_by_name(agent_name)
        if not agent:
            raise ResourceNotFoundError(f"找不到名稱為 {agent_name} 的 Agent")
        
        return self._create_agent_from_data(session_id, agent, variables, None)

    def _create_agent_from_data(self, session_id: str, agent: Agent, variables: Dict[str, Any] = None, response_model: Optional[type] = None) -> AgnoAgent:
        """從 Agent 資料創建 Agent 實例。

        Args:
            session_id: 會話 ID
            agent: Agent 實體
            variables: 變數字典
            response_model: 可選的響應模型類別

        Returns:
            創建的 Agent 實例

        Raises:
            BusinessLogicError: 如果創建失敗
        """
        try:
            # 1. 建立基本配置
            config = {
                "name": agent.agent_name,
                "description": agent.description,
                "instruction": agent.instruction,
                "tools": self._get_tools(agent.tools) if agent.tools else [],
                "num_history_responses": agent.num_history_responses,
                "markdown": agent.markdown,
                "debug": agent.debug,
                "add_history_to_messages": agent.add_history_to_messages
            }

            logger.debug(f"Agent 配置: {config}")
            
            # 2. 處理變數替換
            if variables:
                if config["description"]:
                    config["description"] = VariablesRenderer.render_variables(config["description"], variables)
                if config["instruction"]:
                    config["instruction"] = VariablesRenderer.render_variables(config["instruction"], variables)
            
            # 3. 創建模型實例
            model = self._get_agno_model_instance(
                provider=agent.provider,
                model_name=agent.model_name,
                temperature=agent.temperature
            )

            # 4. 創建 Agno Agent 實例
            agent_instance = AgnoAgent(
                session_id=session_id,
                model=model,
                response_model=response_model,
                name=config["name"],
                instructions=config["instruction"],
                description=config["description"],
                tools=config["tools"],
                num_history_responses=config["num_history_responses"],
                markdown=config["markdown"],
                # debug_mode=config["debug"]
                debug_mode=True,
                storage=self.storage,
                add_history_to_messages=config["add_history_to_messages"]
            )
                
            return agent_instance
            
        except Exception as e:
            logger.error(f"創建 Agent 失敗: {e}")
            raise BusinessLogicError(f"創建 Agent 失敗: {str(e)}")

    def _get_agno_model_instance(self, 
                              provider: str, 
                              model_name: str,
                              temperature: Optional[float] = None,
                              ) -> Any:
        """
        根據提供商和參數創建對應的模型實例。

        Args:
            provider: 提供商名稱
            model_name: 模型名稱
            temperature: 溫度參數，控制輸出的隨機性

        Returns:
            模型實例

        Note:
            如果提供商不支援，會回退到使用 OpenAI 的 gpt-4.1
        """
        provider_lower = provider.lower()
        try:
            if provider_lower == 'openai':
                return OpenAIChat(
                    id=model_name,
                    temperature=temperature
                )
            elif provider_lower == 'google':
                return Gemini(
                    id=model_name,
                    temperature=temperature
                )
            elif provider_lower == 'anthropic':
                return Claude(
                    id=model_name,
                    temperature=temperature
                )
            else:
                logger.warning(f"不支援的提供商 '{provider}'，使用預設的 claude-3-7-sonnet-latest")
                return Claude(id="claude-3-7-sonnet-latest")
        except Exception as e:
            logger.error(f"創建模型實例失敗: {str(e)}")
            raise BusinessLogicError(f"創建模型實例失敗: {str(e)}")

    def _get_tools(self, agent_data: Dict[str, Any]) -> List[Any]:
        """
        從 Agent 配置獲取工具實例列表。

        Args:
            agent_data: Agent 配置資料

        Returns:
            工具實例列表
        """
        tools_cfg = agent_data.get("tools")
        if isinstance(tools_cfg, str):
            try:
                tools_cfg = json.loads(tools_cfg)
            except json.JSONDecodeError:
                logger.warning(f"工具設定不是合法 JSON：{tools_cfg}")
                return []

        if isinstance(tools_cfg, dict) and "tools" in tools_cfg:
            tools_cfg = tools_cfg["tools"]

        if not tools_cfg:
            return []
        if not isinstance(tools_cfg, list):
            tools_cfg = [tools_cfg]

        instances = []
        for entry in tools_cfg:
            if isinstance(entry, str):
                cls = TOOL_CLASSES.get(entry)
                if cls:
                    instances.append(cls())
                else:
                    logger.warning(f"Unknown tool '{entry}'，跳過")
            elif isinstance(entry, dict):
                name = entry.get("name")
                params = entry.get("params", {})
                if not name:
                    logger.warning(f"工具配置缺少 name，條目：{entry}，跳過")
                    continue
                cls = TOOL_CLASSES.get(name)
                if cls:
                    instances.append(cls(**params))
                else:
                    logger.warning(f"Unknown tool '{name}'，跳過")
        return instances
