"""
Logs API for email log retrieval and streaming.
"""

from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any, Optional

from ..client.smtp_client import SmtpClient


class LogsApi:
    """
    API class for email log retrieval and streaming.
    """

    def __init__(self, client: SmtpClient) -> None:
        """
        Initialize the Logs API.

        Args:
            client: SMTP client instance
        """
        self.client = client

    async def get_logs(
        self,
        domain: str,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get email logs for a domain.

        Args:
            domain: Domain name
            limit: Number of logs per page
            page: Page number
            start: Start date filter
            end: End date filter
            sender: Sender email filter
            recipient: Recipient email filter

        Returns:
            Log entries with pagination
        """
        params = {}
        if limit is not None:
            params["limit"] = str(limit)
        if page is not None:
            params["page"] = str(page)
        if start is not None:
            params["start"] = start.isoformat()
        if end is not None:
            params["end"] = end.isoformat()
        if sender is not None:
            params["sender"] = sender
        if recipient is not None:
            params["recipient"] = recipient

        return await self.client.get(f"/api/domains/{domain}/log", params=params)

    async def get_message_logs(
        self,
        domain: str,
        message_guid: str,
    ) -> dict[str, Any]:
        """
        Get logs for a specific message.

        Args:
            domain: Domain name
            message_guid: Message GUID

        Returns:
            Message log entries
        """
        return await self.client.get(f"/api/domains/{domain}/log/{message_guid}")

    async def stream_logs(
        self,
        domain: str,
        limit: Optional[int] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream email logs for a domain.

        Args:
            domain: Domain name
            limit: Number of logs per page
            start: Start date filter
            end: End date filter
            sender: Sender email filter
            recipient: Recipient email filter

        Yields:
            Log entries
        """
        params = {}
        if limit is not None:
            params["limit"] = str(limit)
        if start is not None:
            params["start"] = start.isoformat()
        if end is not None:
            params["end"] = end.isoformat()
        if sender is not None:
            params["sender"] = sender
        if recipient is not None:
            params["recipient"] = recipient

        async for log_entry in self.client.stream(f"/api/domains/{domain}/log", params=params):
            yield log_entry

    async def get_logs_by_date_range(
        self,
        domain: str,
        start_date: datetime,
        end_date: datetime,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get logs within a date range.

        Args:
            domain: Domain name
            start_date: Start date
            end_date: End date
            limit: Number of logs per page
            page: Page number
            sender: Sender email filter
            recipient: Recipient email filter

        Returns:
            Log entries with pagination
        """
        return await self.get_logs(
            domain=domain,
            limit=limit,
            page=page,
            start=start_date,
            end=end_date,
            sender=sender,
            recipient=recipient,
        )


