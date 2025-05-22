from sqlalchemy import Column, String, Text, Float, text
from .base import Base, TimeStampMixin

class Tool(Base, TimeStampMixin):
    __tablename__ = "tools"
    """
    工具表：定義可用工具及其基本效果
    """
    tool_name = Column(String(64), primary_key=True, comment="工具名稱（主鍵）")
    description = Column(Text, nullable=False, comment="工具描述")
    
    # 基本效果值 - 現在是乘數
    trust_effect = Column(Float, nullable=True, server_default=text("1.0"), comment="對信任值的乘數效果 (例如 1.1 表示增加10%)")
    spread_effect = Column(Float, nullable=True, server_default=text("1.0"), comment="對傳播率的乘數效果 (例如 1.2 表示增加20%)")
    
    # 工具適用對象 (player, ai, both)
    applicable_to = Column(String(32), nullable=False, server_default=text("'both'"), comment="適用對象（player/ai/both）")

    def __repr__(self):
        return f"<Tool name={self.tool_name}>"