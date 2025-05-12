"""
Application exception classes.
This module defines the base error classes used throughout the application.
"""
from typing import Any, Dict, Optional, List


class AppError(Exception):
    """Base application error class"""
    def __init__(
        self, 
        message: str, 
        error_code: str = "APP_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.error_code} - {self.details}"
        return f"{self.message} - {self.error_code}"


class ValidationError(AppError):
    """Validation error for domain objects and input data"""
    def __init__(
        self, 
        message: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None
    ):
        if errors:
            details = details or {}
            details["errors"] = errors
        super().__init__(message, error_code, details)


class ResourceNotFoundError(AppError):
    """Resource not found error"""
    def __init__(
        self, 
        message: str = "Resource not found",
        error_code: str = "RESOURCE_NOT_FOUND",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(message, error_code, details)


class AuthorizationError(AppError):
    """Authorization error"""
    def __init__(
        self, 
        message: str = "Authorization error",
        error_code: str = "AUTHORIZATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ConfigurationError(AppError):
    """Configuration error"""
    def __init__(
        self, 
        message: str = "Configuration error",
        error_code: str = "CONFIGURATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ExternalServiceError(AppError):
    """External service error (API calls, etc.)"""
    def __init__(
        self, 
        message: str = "External service error",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        service_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        _details = details or {}
        if service_name:
            _details["service_name"] = service_name
        
        super().__init__(message, error_code, _details)


class DatabaseError(AppError):
    """Database error"""
    def __init__(
        self, 
        message: str = "Database error",
        error_code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class BusinessLogicError(AppError):
    """Business logic error"""
    def __init__(
        self, 
        message: str = "Business logic error",
        error_code: str = "BUSINESS_LOGIC_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


__all__ = [
    "AppError",
    "ValidationError",
    "ResourceNotFoundError",
    "AuthorizationError",
    "ConfigurationError",
    "ExternalServiceError",
    "DatabaseError", 
    "BusinessLogicError"
]
