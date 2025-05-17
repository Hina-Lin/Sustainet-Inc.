from .games import router as games_router
from .agents import router as agents_router
from .news import router as news_router

__all__ = ["games_router", "agents_router", "news_router"]

