"""
API classes for the Kirim.Email SMTP SDK.
"""

from .credentials import CredentialsApi
from .domains import DomainsApi
from .logs import LogsApi
from .messages import MessagesApi
from .suppressions import SuppressionsApi

__all__ = [
    "MessagesApi",
    "DomainsApi",
    "CredentialsApi",
    "LogsApi",
    "SuppressionsApi",
]
