from sqlalchemy import Column, String, Text, Integer, DateTime, text
from .base import Base, TimeStampMixin

class Tool(Base, TimeStampMixin):
    """
    工具表：定義可用工具及其基本效果
    """
    tool_name = Column(String(64), primary_key=True, comment="工具名稱（主鍵）")
    description = Column(Text, nullable=False, comment="工具描述")
    
    # 基本效果值
    trust_effect = Column(Integer, nullable=True, server_default=text("0"), comment="對信任值的基本效果")
    spread_effect = Column(Integer, nullable=True, server_default=text("0"), comment="對傳播率的基本效果")
    
    # 工具適用對象 (player, ai, both)
    applicable_to = Column(String(32), nullable=False, server_default=text("'both'"), comment="適用對象（player/ai/both）")

    def __repr__(self):
        return f"<Tool name={self.tool_name}>"