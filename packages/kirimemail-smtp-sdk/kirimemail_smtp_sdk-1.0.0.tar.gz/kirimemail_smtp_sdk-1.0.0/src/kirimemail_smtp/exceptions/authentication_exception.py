"""
Exception raised for authentication errors (401, 403).
"""

from typing import Any, Optional

from .api_exception import ApiException


class AuthenticationException(ApiException):
    """
    Exception raised for authentication errors.

    Typically raised when the API returns 401 (Unauthorized) or 403 (Forbidden).
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: Optional[int] = None,
        errors: Optional[dict[str, Any]] = None,
        response: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code or 401, errors, response)
        self.name = "AuthenticationException"
