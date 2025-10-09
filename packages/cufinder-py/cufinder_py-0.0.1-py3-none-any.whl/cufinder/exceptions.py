"""Custom exceptions for the Cufinder SDK."""

from typing import Any, Dict, Optional


class CufinderError(Exception):
    """Base exception for all Cufinder SDK errors."""

    def __init__(
        self,
        message: str,
        error_type: str = "CUFINDER_ERROR",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.error_type}] {self.message} (Status: {self.status_code})"
        return f"[{self.error_type}] {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }


class AuthenticationError(CufinderError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)


class ValidationError(CufinderError):
    """Raised when request validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "VALIDATION_ERROR", 400, details)


class RateLimitError(CufinderError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, "RATE_LIMIT_ERROR", 429, details)
        self.retry_after = retry_after


class CreditLimitError(CufinderError):
    """Raised when credit limit is exceeded."""

    def __init__(self, message: str = "Credit limit exceeded"):
        super().__init__(message, "CREDIT_LIMIT_ERROR", 402)


class NetworkError(CufinderError):
    """Raised when network-related errors occur."""

    def __init__(self, message: str = "Network error", status_code: int = 0):
        super().__init__(message, "NETWORK_ERROR", status_code)
