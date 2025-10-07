"""
Exception raised when a resource is not found (404).
"""

from typing import Any, Optional

from .api_exception import ApiException


class NotFoundException(ApiException):
    """
    Exception raised when a requested resource is not found.

    Typically raised when the API returns 404 (Not Found).
    """

    def __init__(
        self,
        message: str = "Resource not found",
        status_code: Optional[int] = None,
        errors: Optional[dict[str, Any]] = None,
        response: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code or 404, errors, response)
        self.name = "NotFoundException"
