"""
Logging configuration for the OCR Service.
Provides structured logging with request tracing.
"""

import logging
import sys
from typing import Optional
import uuid
from contextvars import ContextVar

from app.core.config import settings

# Context variable for request ID tracking
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIDFilter(logging.Filter):
    """Add request ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get() or "no-request"
        return True


def setup_logging() -> None:
    """Configure application logging."""
    
    # Create formatter
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(request_id)s | "
        "%(name)s:%(lineno)d | %(message)s"
    )
    formatter = logging.Formatter(log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIDFilter())
    
    # Clear existing handlers and add new one
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    logger = logging.getLogger(name)
    return logger


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())[:8]


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set the request ID for the current context."""
    if request_id is None:
        request_id = generate_request_id()
    request_id_var.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """Get the current request ID."""
    return request_id_var.get()
