"""
Agent 相關的 DTO (Data Transfer Objects)。
用於 API 請求與響應的資料結構定義。
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class AgentCreateRequest(BaseModel):
    """建立 Agent 的請求 DTO。"""
    agent_name: str = Field(..., description="Agent 名稱，必須唯一")
    provider: str = Field(default="openai", description="提供商名稱 (如 'openai', 'anthropic')")
    model_name: str = Field(default="gpt-4.1", description="使用的模型名稱")
    description: Optional[str] = Field(default="", description="Agent 描述")
    instruction: Optional[str] = Field(default="", description="Agent 的指令設定")
    tools: Optional[Dict[str, List[Dict[str, Any]]]] = Field(
        default={"tools": [{"name": "", "params": {}}]},
        description="Agent 的工具設定"
    )
    temperature: Optional[float] = Field(default=0.7, description="溫度參數 (0-1)")
    num_history_responses: Optional[int] = Field(default=-1, description="歷史回應數量")
    markdown: Optional[bool] = Field(default=True, description="是否支援 Markdown")
    debug: Optional[bool] = Field(default=False, description="是否啟用調試模式")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "TestAgent",
                "provider": "openai",
                "model_name": "gpt-4.1",
                "instruction": "這是指令設定",
                "tools": {
                    "tools": [
                        {
                            "name": "",
                            "params": {}
                        }
                    ]
                },
                "markdown": True,
                "debug": False
            }
        }

class AgentUpdateRequest(BaseModel):
    """更新 Agent 的請求 DTO。"""
    agent_name: str = Field(..., description="Agent 名稱，必須唯一")
    provider: str = Field(default="openai", description="提供商名稱 (如 'openai', 'anthropic')")
    model_name: str = Field(default="gpt-4.1", description="使用的模型名稱")
    description: Optional[str] = Field(default="", description="Agent 描述")
    instruction: Optional[str] = Field(default="", description="Agent 的指令設定")
    tools: Optional[Dict[str, List[Dict[str, Any]]]] = Field(
        default={"tools": [{"name": "", "params": {}}]},
        description="Agent 的工具設定"
    )
    temperature: Optional[float] = Field(default=0.7, description="溫度參數 (0-1)")
    num_history_responses: Optional[int] = Field(default=-1, description="歷史回應數量")
    markdown: Optional[bool] = Field(default=True, description="是否支援 Markdown")
    debug: Optional[bool] = Field(default=False, description="是否啟用調試模式")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "model_name": "gpt-4.1",
                "instruction": "這是指令設定",
                "tools": {
                    "tools": [
                        {
                            "name": "",
                            "params": {}
                        }
                    ]
                },
                "markdown": True,
                "debug": False
            }
        }

class AgentResponse(BaseModel):
    """Agent 響應 DTO。"""
    id: int
    agent_name: str
    provider: str
    model_name: str
    description: Optional[str] = None
    tools: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    created_at: str
    updated_at: str

class AgentListResponse(BaseModel):
    """Agent 列表響應 DTO。"""
    agents: List[AgentResponse]
    total: int
