"""
日誌處理模組 - 提供統一的日誌記錄功能。
"""
import logging
import sys
import os
import json
from typing import Any, Dict, Optional
from src.config import settings

# 設定 ANSI 顏色代碼
COLORS = {
    'DEBUG': '\033[94m',  # 藍色
    'INFO': '\033[92m',   # 綠色
    'WARNING': '\033[93m', # 黃色
    'ERROR': '\033[91m',  # 紅色
    'CRITICAL': '\033[95m', # 紫色
    'RESET': '\033[0m'    # 重置顏色
}

# 自定義格式處理程序，添加顏色
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
            record.msg = f"{COLORS[levelname]}{record.msg}{COLORS['RESET']}"
        return super().format(record)

# 創建基本的日誌配置
class Logger:
    def __init__(
        self, 
        name: str = "Sustainet-Inc"
    ):
        self.logger = logging.getLogger(name)
        
        # 設定日誌級別 (從設定中獲取)
        self.logger.setLevel(settings.log_level)
        
        # 避免重複添加 handler
        if not self.logger.handlers:
            # 控制台處理程序
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(settings.log_level)
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
            
            # 如果啟用了文件日誌
            if settings.app_log_to_file:
                # 確保日誌目錄存在
                log_file_path = settings.app_log_file_path
                os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
                
                # 文件處理程序
                file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
                file_handler.setLevel(settings.log_level)
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
    
    def _format_log(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """格式化日誌訊息，可選添加額外資訊"""
        if extra:
            return f"{message} | {json.dumps(extra, ensure_ascii=False)}"
        return message
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """記錄 INFO 級別的日誌"""
        self.logger.info(self._format_log(message, extra))

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=False) -> None:
        """記錄 ERROR 級別的日誌, 可選包含異常訊息"""
        self.logger.error(self._format_log(message, extra), exc_info=exc_info)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """記錄 WARNING 級別的日誌"""
        self.logger.warning(self._format_log(message, extra))
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """記錄 DEBUG 級別的日誌"""
        self.logger.debug(self._format_log(message, extra))
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """記錄 CRITICAL 級別的日誌"""
        self.logger.critical(self._format_log(message, extra))
    
    def exception(self, message: str, exc_info=True, extra: Optional[Dict[str, Any]] = None) -> None:
        """記錄異常訊息"""
        self.logger.exception(self._format_log(message, extra), exc_info=exc_info)

# 創建全局 logger 實例
logger = Logger()
