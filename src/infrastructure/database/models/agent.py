
"""
Agent 全配置表 - 存儲 Agent 基本訊息與其配置參數
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, Float, text
from .base import Base, TimeStampMixin

class Agent(Base, TimeStampMixin):
    """
    Agent 表，結合基本資訊與配置參數於同一張表
    """
    # 主鍵
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 基本訊息
    agent_name = Column(String(128), unique=True, nullable=False, index=True)
    provider = Column(String(64), nullable=False, default='openai')
    model_name = Column(String(64), nullable=False, default='gpt-4.1')

    # 內容設定
    description = Column(Text)
    instruction = Column(Text)

    # 工具設定
    tools = Column(
        JSON,
        nullable=False,
        server_default=text("'{\"tools\": [{\"name\": \"\", \"params\": {}}]}'::jsonb")
    )

    # Agent 行為參數
    num_history_responses = Column(Integer, default=10)
    add_history_to_messages = Column(Boolean, default=True)
    show_tool_calls = Column(Boolean, default=True)
    markdown = Column(Boolean, default=True)
    debug = Column(Boolean, default=False)
    add_datetime_to_instructions = Column(Boolean, default=False)

    # 模型參數
    temperature = Column(Float, nullable=True)

    # 時間戳已由 TimeStampMixin 提供

    def __repr__(self):
        return (
            f"<Agent id={self.id}, name={self.agent_name}, "
            f"provider={self.provider}, model={self.model_name}>"
        )
