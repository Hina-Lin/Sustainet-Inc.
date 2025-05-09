"""
數據庫連接管理模組。
提供異步的資料庫連接會話管理功能。
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import settings

# 創建異步引擎
async_engine = create_async_engine(
    settings.database_url_async,
    echo=settings.is_development,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 創建異步會話工廠
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=async_engine
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    提供資料庫異步會話的依賴函數。
    在 FastAPI 路由中使用 Depends(get_db) 獲取數據庫會話。
    
    Returns:
        資料庫異步會話對象的異步生成器
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# 應用程序啟動和關閉時的事件處理函數
async def on_startup():
    """應用程序啟動時執行的函數"""
    # 這裡可以添加初始化代碼，例如創建表格等
    pass

async def on_shutdown():
    """應用程序關閉時執行的函數，確保資源適當釋放"""
    # 釋放連接池資源
    await async_engine.dispose()
