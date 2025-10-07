"""
Exception classes for the Kirim.Email SMTP SDK.
"""

from .api_exception import ApiException
from .authentication_exception import AuthenticationException
from .not_found_exception import NotFoundException
from .server_exception import ServerException
from .validation_exception import ValidationException

__all__ = [
    "ApiException",
    "AuthenticationException",
    "ValidationException",
    "NotFoundException",
    "ServerException",
]
