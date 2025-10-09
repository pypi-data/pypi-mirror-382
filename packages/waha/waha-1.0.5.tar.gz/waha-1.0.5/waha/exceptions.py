"""
Custom exception classes for WAHA

Provides specific exception types for different error scenarios.
"""

from typing import Any, Dict, Optional


class WahaException(Exception):
    """Base exception for all WAHA SDK errors."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class WahaAPIError(WahaException):
    """Exception raised for API errors from the WAHA service."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, details)
        self.status_code = status_code

    def __str__(self) -> str:
        base_msg = self.message
        if self.status_code:
            base_msg = f"HTTP {self.status_code}: {base_msg}"
        if self.details:
            base_msg += f". Details: {self.details}"
        return base_msg


class WahaTimeoutError(WahaException):
    """Exception raised when a request times out."""

    pass


class WahaAuthenticationError(WahaException):
    """Exception raised for authentication failures."""

    pass


class WahaValidationError(WahaException):
    """Exception raised for data validation errors."""

    def __init__(
        self, message: str, field: Optional[str] = None, details: Optional[Any] = None
    ):
        super().__init__(message, details)
        self.field = field

    def __str__(self) -> str:
        base_msg = self.message
        if self.field:
            base_msg = f"Validation error for field '{self.field}': {base_msg}"
        if self.details:
            base_msg += f". Details: {self.details}"
        return base_msg


class WahaSessionError(WahaException):
    """Exception raised for session-related errors."""

    def __init__(
        self, message: str, session: Optional[str] = None, details: Optional[Any] = None
    ):
        super().__init__(message, details)
        self.session = session

    def __str__(self) -> str:
        base_msg = self.message
        if self.session:
            base_msg = f"Session '{self.session}': {base_msg}"
        if self.details:
            base_msg += f". Details: {self.details}"
        return base_msg


class WahaNetworkError(WahaException):
    """Exception raised for network-related errors."""

    pass


class WahaRateLimitError(WahaAPIError):
    """Exception raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after
