"""
Memara SDK Exceptions

Custom exception classes for the Memara Python SDK.
"""

from typing import Any, Dict, Optional


class MemaraError(Exception):
    """Base exception for all Memara SDK errors."""

    pass


class MemaraAPIError(MemaraError):
    """Exception raised when the Memara API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.status_code:
            return f"API Error {self.status_code}: {self.message}"
        return f"API Error: {self.message}"


class MemaraAuthError(MemaraAPIError):
    """Exception raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class MemaraNotFoundError(MemaraAPIError):
    """Exception raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} '{resource_id}' not found"
        super().__init__(message, status_code=404)


class MemaraValidationError(MemaraAPIError):
    """Exception raised when request validation fails."""

    def __init__(
        self, message: str, validation_errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=422)
        self.validation_errors = validation_errors or {}


class MemaraRateLimitError(MemaraAPIError):
    """Exception raised when API rate limit is exceeded."""

    def __init__(self, message: str = "API rate limit exceeded"):
        super().__init__(message, status_code=429)


class MemaraServerError(MemaraAPIError):
    """Exception raised when the server encounters an internal error."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)
