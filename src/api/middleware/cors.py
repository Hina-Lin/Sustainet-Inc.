"""
CORS（跨來源資源共享）中間件。
設定 API 允許的跨來源請求規則。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

def setup_cors(app: FastAPI) -> None:
    """
    設定 CORS 中間件。
    
    Args:
        app: FastAPI 應用實例
    """
    # 在開發環境中允許所有來源
    # 在生產環境中應該限制來源
    origins = ["*"] if settings.is_development else [
        # 在此添加允許的生產環境域名
        "https://sustainet-inc.example.com",
        # 可以添加更多允許的域名
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
