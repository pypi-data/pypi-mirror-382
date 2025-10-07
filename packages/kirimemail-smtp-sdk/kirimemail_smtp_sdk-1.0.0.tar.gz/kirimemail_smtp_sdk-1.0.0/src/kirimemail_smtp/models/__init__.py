"""
Data models for the Kirim.Email SMTP API.
"""

from .credential import Credential
from .domain import Domain
from .log_entry import LogEntry
from .pagination import Pagination
from .suppression import Suppression

__all__ = [
    "Credential",
    "Domain",
    "LogEntry",
    "Pagination",
    "Suppression",
]
