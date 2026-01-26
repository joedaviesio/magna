"""
errors.py

Custom exceptions and error handling for Bowen backend.
Provides meaningful error codes and messages for clients.
"""

from enum import Enum
from typing import Optional, Dict, Any
from fastapi import HTTPException
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Standardized error codes for the API."""
    # Validation errors (400)
    EMPTY_MESSAGE = "EMPTY_MESSAGE"
    INVALID_SESSION_ID = "INVALID_SESSION_ID"
    INVALID_QUERY = "INVALID_QUERY"
    INVALID_LIMIT = "INVALID_LIMIT"

    # Service errors (503)
    EMBEDDINGS_NOT_LOADED = "EMBEDDINGS_NOT_LOADED"
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    ANTHROPIC_UNAVAILABLE = "ANTHROPIC_UNAVAILABLE"
    SEARCH_FAILED = "SEARCH_FAILED"
    GENERATION_FAILED = "GENERATION_FAILED"

    # Internal errors (500)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    code: str
    detail: Optional[str] = None
    retry_after: Optional[int] = None  # Seconds to wait before retry


class BowenError(HTTPException):
    """Base exception for Bowen API errors."""

    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        detail: Optional[str] = None,
        retry_after: Optional[int] = None
    ):
        self.error_code = error_code
        self.message = message
        self.error_detail = detail
        self.retry_after = retry_after

        # Build the detail dict for HTTPException
        error_body = {
            "error": message,
            "code": error_code.value,
        }
        if detail:
            error_body["detail"] = detail
        if retry_after:
            error_body["retry_after"] = retry_after

        super().__init__(status_code=status_code, detail=error_body)


class ValidationError(BowenError):
    """Raised for validation errors (400)."""

    def __init__(self, error_code: ErrorCode, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=400,
            error_code=error_code,
            message=message,
            detail=detail
        )


class ServiceUnavailableError(BowenError):
    """Raised when a required service is unavailable (503)."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        detail: Optional[str] = None,
        retry_after: int = 30
    ):
        super().__init__(
            status_code=503,
            error_code=error_code,
            message=message,
            detail=detail,
            retry_after=retry_after
        )


class InternalError(BowenError):
    """Raised for internal server errors (500)."""

    def __init__(self, error_code: ErrorCode, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=500,
            error_code=error_code,
            message=message,
            detail=detail
        )


# Convenience functions for common errors
def raise_empty_message():
    raise ValidationError(
        ErrorCode.EMPTY_MESSAGE,
        "Message cannot be empty",
        "Please provide a non-empty message in the 'message' field"
    )


def raise_invalid_query():
    raise ValidationError(
        ErrorCode.INVALID_QUERY,
        "Query parameter is required",
        "Please provide a search query using the 'q' parameter"
    )


def raise_embeddings_not_loaded():
    raise ServiceUnavailableError(
        ErrorCode.EMBEDDINGS_NOT_LOADED,
        "Search service unavailable",
        "The embeddings have not been loaded. Please wait for initialization to complete.",
        retry_after=60
    )


def raise_model_not_loaded():
    raise ServiceUnavailableError(
        ErrorCode.MODEL_NOT_LOADED,
        "Search service unavailable",
        "The embedding model has not been loaded. Please wait for initialization to complete.",
        retry_after=60
    )


def raise_anthropic_unavailable():
    raise ServiceUnavailableError(
        ErrorCode.ANTHROPIC_UNAVAILABLE,
        "AI service unavailable",
        "The Claude API is not configured or is currently unavailable.",
        retry_after=30
    )


def raise_generation_failed(error_msg: str):
    raise InternalError(
        ErrorCode.GENERATION_FAILED,
        "Failed to generate response",
        f"The AI model encountered an error: {error_msg}"
    )
