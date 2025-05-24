"""
Configuration package for the application.
"""
from .settings import settings
from .game_config import game_config

# 導出全局設定實例
__all__ = ["settings", "game_config"]
