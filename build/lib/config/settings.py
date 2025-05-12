"""
Configuration module for the application.
Provides a unified Settings class that loads all environment variables.
"""
import os
import logging
from dataclasses import dataclass, field
from typing import Dict, Any
from dotenv import load_dotenv

# 加載 .env 檔案
load_dotenv()

# === 公共類別與函數 ===

@dataclass
class Settings:
    """
    統一的應用程式設定類，從環境變數加載所有配置。
    
    用法示例:
    ```python
    from src.config import settings
    
    # 使用應用設定
    port = settings.app_port
    env = settings.app_env
    
    # 檢查環境
    if settings.is_development:
        # 開發環境特定代碼
        pass
    
    # 使用 API 密鑰
    openai_key = settings.openai_api_key
    google_key = settings.google_api_key
    
    # 使用資料庫設定
    db_url_sync = settings.database_url_sync
    db_url_async = settings.database_url_async
    ```
    """
    # 應用設定
    app_env: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    app_port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    app_log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "debug"))
    app_log_to_file: bool = field(default_factory=lambda: os.getenv("LOG_TO_FILE", "false").lower() == "true")
    app_log_file_path: str = field(default_factory=lambda: os.getenv("LOG_FILE_PATH", "logs/app.log"))
    
    # API 密鑰
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    
    # 資料庫設定
    database_url_sync: str = field(default_factory=lambda: os.getenv("DATABASE_URL_SYNC", ""))
    database_url_async: str = field(default_factory=lambda: os.getenv("DATABASE_URL_ASYNC", ""))
    
    @property
    def is_development(self) -> bool:
        """檢查是否為開發環境"""
        return self.app_env.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """檢查是否為生產環境"""
        return self.app_env.lower() == "production"
    
    @property
    def log_level(self) -> int:
        """取得日誌級別"""
        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        return levels.get(self.app_log_level.lower(), logging.INFO)
    
    def to_dict(self) -> Dict[str, Any]:
        """將設定轉換為字典"""
        return {
            "app": {
                "env": self.app_env,
                "port": self.app_port,
                "log_level": self.app_log_level,
                "log_to_file": self.app_log_to_file,
                "log_file_path": self.app_log_file_path,
                "is_development": self.is_development,
                "is_production": self.is_production,
            },
            "api_keys": {
                "openai": bool(self.openai_api_key),
                "anthropic": bool(self.anthropic_api_key),
                "google": bool(self.google_api_key),
            },
            "database": {
                "url_sync": bool(self.database_url_sync),  # 只顯示是否設定，不顯示實際 URL
                "url_async": bool(self.database_url_async),  # 只顯示是否設定，不顯示實際 URL
            }
        }

# 全局設定實例
settings = Settings()
