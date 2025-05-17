# API middleware package

from .cors import setup_cors
from .error_handler import setup_exception_handlers

__all__ = ["setup_cors", "setup_exception_handlers"]
