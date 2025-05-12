from sqlalchemy import Column, String, Text
from .base import Base, TimeStampMixin

class Tool(Base, TimeStampMixin):
    """
    工具表：以 tool_name 作為主鍵
    """
    tool_name = Column(String(64), primary_key=True)
    role = Column(String(32), nullable=False)
    effect = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Tool name={self.tool_name}, role={self.role}>"
