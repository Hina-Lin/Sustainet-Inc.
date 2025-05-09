"""
資料庫模型基礎元件。
提供所有模型共用的基礎類別與混入類。
"""
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr

class TimeStampMixin:
    """
    時間戳混入類。
    為模型添加 created_at 和 updated_at 欄位，並自動管理欄位值。
    """
    # 自動設定為當前時間，不能為空
    created_at = Column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    # 自動設定為當前時間，每次更新時自動更新，不能為空
    updated_at = Column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class CustomBase:
    """
    自定義基礎類別。
    提供所有模型共用的功能與屬性。
    """
    @declared_attr
    def __tablename__(cls) -> str:
        """
        自動生成表名。
        將類名轉換為小寫並加上 's' 後綴。
        例如 User -> users, BlogPost -> blog_posts
        """
        # 將駝峰命名轉換為下劃線命名
        import re
        name = re.sub('(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return f"{name}s"

# 創建基礎類別
Base = declarative_base(cls=CustomBase)
