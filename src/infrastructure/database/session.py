"""
Database connection management module.
Provides synchronous database session management.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config import settings
from agno.storage.postgres import PostgresStorage

# Create synchronous engine
engine = create_engine(
    settings.database_url_sync,  
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create synchronous session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

def get_db() -> Generator[Session, None, None]:
    """
    Provide a synchronous database session dependency.
    Use in FastAPI routes with Depends(get_db).

    Yields:
        SQLAlchemy Session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

agent_storage = PostgresStorage(
            db_url=settings.database_url_sync,
            table_name="agent_session_history",
            schema="public",
            auto_upgrade_schema=True
        )

def get_storage():
    """
    提供資料庫存儲的依賴注入函數，
    用於 FastAPI 中的 Depends 參數。
    """
    return agent_storage