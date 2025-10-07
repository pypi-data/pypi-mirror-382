"""
Kirim.Email SMTP Python SDK

A modern, type-safe Python client for the Kirim.Email SMTP API.
"""

from .api.credentials import CredentialsApi
from .api.domains import DomainsApi
from .api.logs import LogsApi
from .api.messages import MessagesApi
from .api.suppressions import SuppressionsApi
from .client.smtp_client import SmtpClient
from .exceptions import (
    ApiException,
    AuthenticationException,
    NotFoundException,
    ServerException,
    ValidationException,
)

__version__ = "1.0.0"
__author__ = "Kirim.Email"
__email__ = "support@kirim.email"

__all__ = [
    "SmtpClient",
    "MessagesApi",
    "DomainsApi",
    "CredentialsApi",
    "LogsApi",
    "SuppressionsApi",
    "ApiException",
    "AuthenticationException",
    "ValidationException",
    "NotFoundException",
    "ServerException",
]
