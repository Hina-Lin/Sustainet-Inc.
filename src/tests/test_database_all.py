from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.models import Tool, GameRecord, GameSetup, News
from src.infrastructure.database.models.base import Base

# 連線設定
DATABASE_URL = "postgresql://postgres.bmosasqfvflagnjffulc:FUzeloGpe1WdFF7T@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_create_all_tables():
    db = SessionLocal()
    try:
        # 產生唯一用的識別碼
        session_id = f"test_session_{uuid4().hex[:8]}"
        tool_name = f"TestTool_{uuid4().hex[:6]}"

        # Tool
        tool = Tool(tool_name=tool_name, role="player", effect="Increase Trust")
        db.add(tool)

        # GameRecord
        record = GameRecord(
            session_id=session_id,
            round_number=1,
            actor="player",
            platform="line",
            input_text="test input",
            used_tool=tool_name,
            result="test result"
        )
        db.add(record)

        # GameSetup
        setup = GameSetup(
            session_id=session_id,
            platform="line",
            audience_group="young adults",
            platform_user_state="active"
        )
        db.add(setup)

        # News
        news = News(
            title="Test News",
            content="Lorem ipsum...",
            source="Test Source"
        )
        db.add(news)

        db.commit()
        db.refresh(news)

        # 驗證是否寫入成功
        assert db.query(Tool).filter_by(tool_name=tool_name).first() is not None
        assert db.query(GameRecord).filter_by(session_id=session_id).first() is not None
        assert db.query(GameSetup).filter_by(session_id=session_id).first() is not None
        assert db.query(News).filter_by(news_id=news.news_id).first() is not None

        print(f"✅ 測試成功：session_id = {session_id}, tool_name = {tool_name}, news_id = {news.news_id}")
    finally:
        db.close()

if __name__ == "__main__":
    test_create_all_tables()
