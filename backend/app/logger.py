"""
logger.py

Structured logging for Bowen backend with failure tracking.
Provides consistent logging format and tracks analytics failures.
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


class LogEvent(Enum):
    """Standardized log event types."""
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    CHAT_REQUEST = "chat_request"
    CHAT_RESPONSE = "chat_response"
    SEARCH = "search"
    ANALYTICS_SUCCESS = "analytics_success"
    ANALYTICS_FAILURE = "analytics_failure"
    SUPABASE_ERROR = "supabase_error"
    CLAUDE_ERROR = "claude_error"
    EMBEDDING_ERROR = "embedding_error"


class BowenLogger:
    """Structured logger for Bowen application."""

    def __init__(self, name: str = "bowen"):
        self.logger = logging.getLogger(name)
        self._failure_counts: Dict[str, int] = {}

    def _format_extra(self, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format extra data for log message."""
        if not extra:
            return ""
        items = [f"{k}={v}" for k, v in extra.items() if v is not None]
        return " | " + " | ".join(items) if items else ""

    def info(self, event: LogEvent, message: str, **extra):
        """Log an info message."""
        self.logger.info(f"[{event.value}] {message}{self._format_extra(extra)}")

    def warning(self, event: LogEvent, message: str, **extra):
        """Log a warning message."""
        self.logger.warning(f"[{event.value}] {message}{self._format_extra(extra)}")

    def error(self, event: LogEvent, message: str, error: Optional[Exception] = None, **extra):
        """Log an error message and track failure count."""
        error_msg = str(error) if error else None
        if error_msg:
            extra['error'] = error_msg

        self.logger.error(f"[{event.value}] {message}{self._format_extra(extra)}")

        # Track failure counts
        key = event.value
        self._failure_counts[key] = self._failure_counts.get(key, 0) + 1

    def track_analytics_failure(self, operation: str, error: Exception, session_id: Optional[str] = None):
        """Track an analytics logging failure."""
        self.error(
            LogEvent.ANALYTICS_FAILURE,
            f"Failed to log {operation}",
            error=error,
            operation=operation,
            session_id=session_id[:8] if session_id else None  # Only log first 8 chars for privacy
        )

    def track_analytics_success(self, operation: str, session_id: Optional[str] = None):
        """Track successful analytics operation."""
        self.info(
            LogEvent.ANALYTICS_SUCCESS,
            f"Successfully logged {operation}",
            operation=operation,
            session_id=session_id[:8] if session_id else None
        )

    def log_chat_request(self, session_id: str, query_length: int, detected_act: Optional[str] = None):
        """Log an incoming chat request."""
        self.info(
            LogEvent.CHAT_REQUEST,
            "Chat request received",
            session_id=session_id[:8],
            query_length=query_length,
            detected_act=detected_act
        )

    def log_chat_response(
        self,
        session_id: str,
        response_time_ms: int,
        sources_count: int,
        success: bool = True
    ):
        """Log a chat response."""
        event = LogEvent.CHAT_RESPONSE
        if success:
            self.info(
                event,
                "Chat response sent",
                session_id=session_id[:8],
                response_time_ms=response_time_ms,
                sources_count=sources_count
            )
        else:
            self.warning(
                event,
                "Chat response failed",
                session_id=session_id[:8],
                response_time_ms=response_time_ms
            )

    def get_failure_counts(self) -> Dict[str, int]:
        """Get current failure counts by event type."""
        return self._failure_counts.copy()

    def get_failure_summary(self) -> str:
        """Get a summary of all failures."""
        if not self._failure_counts:
            return "No failures recorded"

        summary_parts = [f"{k}: {v}" for k, v in self._failure_counts.items()]
        return "Failure counts: " + ", ".join(summary_parts)


# Global logger instance
logger = BowenLogger()
