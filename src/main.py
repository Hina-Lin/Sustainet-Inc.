# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import tools, demo
from src.api.middleware.error_handler import setup_exception_handlers
from src.config import config
from src.utils.logger import logger

# 創建 FastAPI 應用
app = FastAPI(
    title="Sustainet-Inc API",
    description="Sustainet Inc. 的 API 服務",
    version="0.1.0"
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
app.include_router(demo.router, prefix="/api")

# 啟動事件
@app.on_event("startup")
async def startup_event():
    logger.info("API 服務啟動中", extra={
        "environment": config.app.env,
        "port": config.app.port
    })

# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API 服務關閉中")

# 簡單的健康檢查端點
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "environment": config.app.env,
        "version": app.version
    }
