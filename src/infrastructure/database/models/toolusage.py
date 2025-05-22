from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, text, Float
from .base import Base, TimeStampMixin

class ToolUsage(Base, TimeStampMixin):
    __tablename__ = "tool_usages"
    """
    工具使用記錄表：記錄每次行動中使用的工具及其效果
    """
    id = Column(Integer, primary_key=True, autoincrement=True, comment="工具使用記錄主鍵")
    action_id = Column(Integer, ForeignKey('action_records.id'), nullable=False, comment="關聯的行動記錄 ID")
    tool_name = Column(String(64), ForeignKey('tools.tool_name'), nullable=False, comment="使用的工具名稱")
    
    # 效果數值 - 儲存工具造成的實際變化量，可以是小數，所以用Float
    trust_effect = Column(Float, nullable=True, comment="對信任值的實際效果（淨變化量）")
    spread_effect = Column(Float, nullable=True, comment="對傳播率的實際效果（淨變化量）")
    
    # 工具使用成功否
    is_effective = Column(Boolean, nullable=False, server_default=text("true"), comment="工具是否有效")

    def __repr__(self):
        return f"<ToolUsage id={self.id}, tool={self.tool_name}, action={self.action_id}>"