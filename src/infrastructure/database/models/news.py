from sqlalchemy import Column, Integer, String, Text
from src.infrastructure.database.models.base import Base

class News(Base):
    __tablename__ = "news"

    news_id = Column(Integer, primary_key=True, autoincrement=True)  # 加入 autoincrement=True
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    source = Column(String(128), nullable=False)

    def __repr__(self):
        return f"<News id={self.news_id}, title={self.title}>"
