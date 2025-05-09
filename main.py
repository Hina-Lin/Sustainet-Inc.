# src/main.py

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.routes import tools, agents
from src.api.middleware.error_handler import setup_exception_handlers
from src.config import settings
from src.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動事件
    logger.info("API 服務啟動中", extra={
        "environment": settings.app_env,
        "port": settings.app_port
    })
    yield
    # 關閉事件
    logger.info("API 服務關閉中")

# 創建 FastAPI 應用
app = FastAPI(
    title="Sustainet-Inc API",
    description="Sustainet Inc. 的 API 服務",
    version="0.1.0",
    lifespan=lifespan
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定全局異常處理
setup_exception_handlers(app)

# 加載 API 路由
app.include_router(tools.router, prefix="/api")
app.include_router(agents.router, prefix="/api")

# 簡單的健康檢查端點
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "environment": settings.app_env,
        "version": app.version
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=True)