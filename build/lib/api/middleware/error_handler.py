"""
統一的 API 錯誤處理中間件

此模組提供了 FastAPI 應用程序的統一錯誤處理機制，
將各種異常轉換為標準格式的 HTTP 響應。
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from typing import Any, Dict, Optional, Union, Type
import traceback

from src.utils.exceptions import (
    AppError,
    ValidationError, 
    ResourceNotFoundError, 
    AuthorizationError,
    ConfigurationError,
    ExternalServiceError,
    DatabaseError,
    BusinessLogicError
)
from src.utils.logger import logger
from src.config import settings


# === 公共類別與函數 ===

class APIError(AppError):
    """API 錯誤基類，包含 HTTP 狀態碼"""
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        error_code: str = "API_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        super().__init__(message, error_code, details)


class BadRequestError(APIError):
    """400 錯誤 - 錯誤的請求"""
    def __init__(self, message: str = "Bad request", error_code: str = "BAD_REQUEST", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, error_code=error_code, details=details)


class AuthenticationError(APIError):
    """401 錯誤 - 未經授權"""
    def __init__(self, message: str = "Unauthorized", error_code: str = "UNAUTHORIZED", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, error_code=error_code, details=details)


class ForbiddenError(APIError):
    """403 錯誤 - 禁止訪問"""
    def __init__(self, message: str = "Forbidden", error_code: str = "FORBIDDEN", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, error_code=error_code, details=details)


class NotFoundError(APIError):
    """404 錯誤 - 資源不存在"""
    def __init__(self, message: str = "Not found", error_code: str = "NOT_FOUND", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, error_code=error_code, details=details)


class ConflictError(APIError):
    """409 錯誤 - 資源衝突"""
    def __init__(self, message: str = "Conflict", error_code: str = "CONFLICT", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, error_code=error_code, details=details)


class APIValidationError(APIError):
    """422 錯誤 - API 驗證錯誤"""
    def __init__(self, message: str = "Validation error", error_code: str = "VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, error_code=error_code, details=details)


class ServerError(APIError):
    """500 錯誤 - 伺服器內部錯誤"""
    def __init__(self, message: str = "Internal server error", error_code: str = "INTERNAL_SERVER_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, error_code=error_code, details=details)


def setup_exception_handlers(app):
    """
    設定 FastAPI 應用程序的異常處理器
    
    此函數應在 FastAPI 應用程序初始化時調用，用於註冊各種異常處理器。
    它會處理 API 錯誤、應用程序錯誤、HTTP 異常、請求驗證錯誤等各種異常情況。
    
    參數:
        app: FastAPI 應用程序實例
    """
    # API 專用錯誤
    app.add_exception_handler(APIError, api_exception_handler)
    
    # 通用應用程序錯誤
    app.add_exception_handler(AppError, app_exception_handler)
    
    # FastAPI/Starlette 標準錯誤
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 通用異常處理
    app.add_exception_handler(Exception, generic_exception_handler)


# === 私有函數 ===

# 將通用應用程序錯誤映射到 API 錯誤
_ERROR_MAPPING = {
    ValidationError: APIValidationError,
    ResourceNotFoundError: NotFoundError,
    AuthorizationError: ForbiddenError,
    ConfigurationError: BadRequestError,
    ExternalServiceError: ServerError,
    DatabaseError: ServerError,
    BusinessLogicError: BadRequestError
}

# 異常處理映射表
_DEFAULT_EXCEPTION_MAPPING = {
    Exception: ServerError,
    ValueError: BadRequestError,
    KeyError: BadRequestError,
    TypeError: BadRequestError,
}


def _format_error_response(error: APIError) -> Dict[str, Any]:
    """格式化錯誤響應"""
    response = {
        "success": False,
        "error": {
            "code": error.error_code,
            "message": error.message,
        }
    }
    
    if error.details:
        response["error"]["details"] = error.details
        
    return response


async def api_exception_handler(request: Request, exc: APIError) -> JSONResponse:
    """處理 API 錯誤"""
    logger.error(f"API 錯誤: {exc.message}", extra={
        "status_code": exc.status_code,
        "error_code": exc.error_code,
        "path": request.url.path,
        "details": exc.details
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=_format_error_response(exc)
    )


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    """處理通用應用程序錯誤，將其映射到適當的 API 錯誤"""
    # 從映射表中獲取對應的 API 錯誤類型
    api_error_class = _ERROR_MAPPING.get(type(exc), ServerError)
    
    # 創建 API 錯誤
    api_error = api_error_class(
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )
    
    logger.error(f"應用程序錯誤: {exc.message}", extra={
        "error_code": exc.error_code,
        "path": request.url.path,
        "details": exc.details
    })
    
    return JSONResponse(
        status_code=api_error.status_code,
        content=_format_error_response(api_error)
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """處理 HTTP 異常"""
    error = APIError(
        message=str(exc.detail),
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}"
    )
    
    logger.error(f"HTTP 錯誤: {error.message}", extra={
        "status_code": error.status_code,
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=_format_error_response(error)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """處理 FastAPI 請求驗證異常"""
    details = {"errors": []}
    
    for error in exc.errors():
        details["errors"].append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    error = APIValidationError(
        message="Request validation error",
        error_code="REQUEST_VALIDATION_ERROR",
        details=details
    )
    
    logger.error(f"驗證錯誤: {error.message}", extra={
        "path": request.url.path,
        "details": details
    })
    
    return JSONResponse(
        status_code=error.status_code,
        content=_format_error_response(error)
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """處理所有未處理的異常"""
    # 檢查異常是否映射到特定錯誤類型
    error_class = _DEFAULT_EXCEPTION_MAPPING.get(type(exc), ServerError)
    
    # 創建對應的錯誤實例
    if error_class == ServerError:
        error = error_class(
            message=f"An unexpected error occurred: {str(exc)}",
            details={"traceback": traceback.format_exc() if settings.is_development else None}
        )
    else:
        error = error_class(message=str(exc))
    
    logger.error(f"未處理的異常: {exc}", extra={
        "exception_type": type(exc).__name__,
        "path": request.url.path
    }, exc_info=True)
    
    return JSONResponse(
        status_code=error.status_code,
        content=_format_error_response(error)
    )


# 導出所有 API 錯誤類型，以便在路由中使用
__all__ = [
    'APIError',
    'BadRequestError',
    'AuthenticationError',
    'ForbiddenError',
    'NotFoundError',
    'ConflictError',
    'APIValidationError',
    'ServerError',
    'setup_exception_handlers',
]
