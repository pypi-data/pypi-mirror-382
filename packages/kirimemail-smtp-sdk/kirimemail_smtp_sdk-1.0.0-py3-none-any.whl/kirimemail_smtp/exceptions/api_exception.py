"""
Base exception class for all API-related errors.
"""

from typing import Any, Optional


class ApiException(Exception):
    """
    Base exception class for all API-related errors.

    Attributes:
        message: Error message
        status_code: HTTP status code (optional)
        errors: Dictionary of field-specific errors (optional)
        response: Full response data (optional)
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        errors: Optional[dict[str, Any]] = None,
        response: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}
        self.response = response or {}
        self.name = "ApiException"

    def has_errors(self) -> bool:
        """Check if the exception has validation errors."""
        return bool(self.errors)

    def get_error_messages(self) -> list[str]:
        """Get all validation errors as a flat list."""
        if not self.errors:
            return []

        error_messages: list[str] = []
        for field_errors in self.errors.values():
            if isinstance(field_errors, list):
                error_messages.extend(str(error) for error in field_errors)
            else:
                error_messages.append(str(field_errors))

        return error_messages

    def get_error_for_field(self, field: str) -> list[str]:
        """Get error messages for a specific field."""
        field_errors = self.errors.get(field)
        if not field_errors:
            return []

        if isinstance(field_errors, list):
            return [str(error) for error in field_errors]
        return [str(field_errors)]

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary representation."""
        return {
            "name": self.name,
            "message": self.message,
            "status_code": self.status_code,
            "errors": self.errors,
            "response": self.response,
        }

    def __str__(self) -> str:
        if self.status_code:
            return f"{self.name} ({self.status_code}): {self.message}"
        return f"{self.name}: {self.message}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code!r}, "
            f"errors={self.errors!r}"
            f")"
        )
