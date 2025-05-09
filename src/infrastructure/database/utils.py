"""
資料庫工具函數。
提供資料庫操作的輔助功能。
"""
import functools
from typing import TypeVar, Callable, Any, Awaitable, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import get_db

T = TypeVar('T')

def with_session(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    裝飾器：自動處理 session 的創建和關閉。
    
    當函數的 db 參數為 None 時，自動創建一個新的 session。
    函數執行完畢後自動關閉 session（如果是由裝飾器創建的）。
    
    用法：
    ```python
    @with_session
    async def get_entity(id: int, db: AsyncSession = None) -> Entity:
        entity = await db.get(Entity, id)
        return entity
    ```
    
    Args:
        func: 要裝飾的異步函數，必須有一個名為 db 的參數，類型為 AsyncSession，且可為 None
    
    Returns:
        裝飾後的函數
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        # 檢查是否已提供 db
        db = kwargs.get('db')
        own_session = False
        
        # 如果沒有提供 db，創建一個新的
        if db is None:
            db_context = get_db()
            db = await anext(db_context.__aiter__())
            kwargs['db'] = db
            own_session = True
        
        try:
            # 調用原函數
            result = await func(*args, **kwargs)
            
            # 如果我們創建了自己的 session，則提交
            if own_session:
                await db.commit()
                
            return result
        except Exception as e:
            # 如果我們創建了自己的 session，則回滾
            if own_session:
                await db.rollback()
            raise e
        finally:
            # 如果我們創建了自己的 session，則關閉
            if own_session:
                await db.close()
    
    return wrapper

async def manage_session(db: Optional[AsyncSession] = None) -> AsyncGenerator[AsyncSession, None]:
    """
    上下文管理器函數：提供一個可在 async with 中使用的 session 管理器。
    
    用法：
    ```python
    async def some_operation():
        async with manage_session() as session:
            # 使用 session 進行操作
            entity = await session.get(Entity, 1)
        # session 已自動關閉
    ```
    
    Args:
        db: 可選的現有 session。如果提供，將直接使用該 session 且不會關閉它
        
    Returns:
        AsyncSession 實例
    """
    if db is not None:
        # 如果已提供 session，直接返回且不在結束時關閉
        yield db
        return
        
    # 創建新的 session
    db_context = get_db()
    session = await anext(db_context.__aiter__())
    
    try:
        # 提供 session 給調用者
        yield session
        # 提交變更
        await session.commit()
    except Exception:
        # 發生異常時回滾
        await session.rollback()
        raise
    finally:
        # 總是關閉自己創建的 session
        await session.close()
