"""
Messages API for sending emails and templates.
"""

from typing import Any, Optional

from ..client.smtp_client import SmtpClient
from ..exceptions import ApiException


class MessagesApi:
    """
    API class for sending emails and templates.
    """

    def __init__(self, client: SmtpClient) -> None:
        """
        Initialize the Messages API.

        Args:
            client: SMTP client instance
        """
        self.client = client

    async def send_message(
        self,
        domain: str,
        message: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send a simple email.

        Args:
            domain: Domain name
            message: Email message data

        Returns:
            Send response

        Raises:
            ApiException: For API errors
        """
        self._validate_email_message(message)

        return await self.client.post(
            f"/api/domains/{domain}/message",
            data=message,
        )

    async def send_message_with_attachments(
        self,
        domain: str,
        message: dict[str, Any],
        files: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Send an email with attachments.

        Args:
            domain: Domain name
            message: Email message data
            files: List of files to attach

        Returns:
            Send response

        Raises:
            ApiException: For API errors
        """
        self._validate_email_message(message)
        self._validate_files(files)

        return await self.client.post_multipart(
            f"/api/domains/{domain}/message",
            data=message,
            files=files,
        )

    async def send_template_message(
        self,
        domain: str,
        template: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send a template email.

        Args:
            domain: Domain name
            template: Template message data

        Returns:
            Send response

        Raises:
            ApiException: For API errors
        """
        self._validate_template_message(template)

        return await self.client.post(
            f"/api/domains/{domain}/message/template",
            data=template,
        )

    async def send_template_message_with_attachments(
        self,
        domain: str,
        template: dict[str, Any],
        files: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Send a template email with attachments.

        Args:
            domain: Domain name
            template: Template message data
            files: List of files to attach

        Returns:
            Send response

        Raises:
            ApiException: For API errors
        """
        self._validate_template_message(template)
        self._validate_files(files)

        return await self.client.post_multipart(
            f"/api/domains/{domain}/message/template",
            data=template,
            files=files,
        )

    async def send_bulk_message(
        self,
        domain: str,
        message: dict[str, Any],
        files: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Send bulk email to multiple recipients.

        Args:
            domain: Domain name
            message: Email message data with 'to' as array
            files: Optional list of files to attach

        Returns:
            Send response

        Raises:
            ApiException: For API errors
        """
        self._validate_bulk_message(message)

        if files:
            self._validate_files(files)
            return await self.client.post_multipart(
                f"/api/domains/{domain}/message",
                data=message,
                files=files,
            )
        else:
            return await self.client.post(
                f"/api/domains/{domain}/message",
                data=message,
            )

    async def send_message_with_attachment_options(
        self,
        domain: str,
        message: dict[str, Any],
        files: list[dict[str, Any]],
        attachment_options: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send email with attachment processing options.

        Args:
            domain: Domain name
            message: Email message data
            files: List of files to attach
            attachment_options: Attachment processing options

        Returns:
            Send response

        Raises:
            ApiException: For API errors
        """
        self._validate_email_message(message)
        self._validate_files(files)

        # Add attachment options to message
        message["attachment_options"] = attachment_options

        return await self.client.post_multipart(
            f"/api/domains/{domain}/message",
            data=message,
            files=files,
        )

    def _validate_email_message(self, message: dict[str, Any]) -> None:
        """
        Validate email message data.

        Args:
            message: Email message data

        Raises:
            ApiException: For validation errors
        """
        required_fields = ["from", "to", "subject"]
        for field in required_fields:
            if field not in message:
                raise ApiException(f"Missing required field: {field}")

        # Validate email format for 'from' field
        if not self._is_valid_email(message["from"]):
            raise ApiException(f"Invalid email format for 'from' field: {message['from']}")

        # Validate 'to' field
        to_field = message["to"]
        if isinstance(to_field, str):
            if not self._is_valid_email(to_field):
                raise ApiException(f"Invalid email format for 'to' field: {to_field}")
        elif isinstance(to_field, list):
            for email in to_field:
                if not self._is_valid_email(email):
                    raise ApiException(f"Invalid email format in 'to' field: {email}")
        else:
            raise ApiException("'to' field must be a string or list of strings")

        # Validate that either text or html content is provided
        if not message.get("text") and not message.get("html"):
            raise ApiException("Either 'text' or 'html' content must be provided")

    def _validate_template_message(self, template: dict[str, Any]) -> None:
        """
        Validate template message data.

        Args:
            template: Template message data

        Raises:
            ApiException: For validation errors
        """
        required_fields = ["template_guid", "to"]
        for field in required_fields:
            if field not in template:
                raise ApiException(f"Missing required field: {field}")

        # Validate 'to' field
        to_field = template["to"]
        if isinstance(to_field, str):
            if not self._is_valid_email(to_field):
                raise ApiException(f"Invalid email format for 'to' field: {to_field}")
        elif isinstance(to_field, list):
            for email in to_field:
                if not self._is_valid_email(email):
                    raise ApiException(f"Invalid email format in 'to' field: {email}")
        else:
            raise ApiException("'to' field must be a string or list of strings")

        # Validate 'from' field if provided
        if "from" in template and not self._is_valid_email(template["from"]):
            raise ApiException(f"Invalid email format for 'from' field: {template['from']}")

    def _validate_bulk_message(self, message: dict[str, Any]) -> None:
        """
        Validate bulk message data.

        Args:
            message: Bulk message data

        Raises:
            ApiException: For validation errors
        """
        self._validate_email_message(message)

        # For bulk messages, 'to' must be an array
        if not isinstance(message["to"], list):
            raise ApiException("Bulk email requires 'to' field to be an array of email addresses")

        if len(message["to"]) > 1000:
            raise ApiException("Maximum 1000 recipients allowed per bulk request")

        if len(message["to"]) == 0:
            raise ApiException("At least one recipient is required for bulk email")

    def _validate_files(self, files: list[dict[str, Any]]) -> None:
        """
        Validate file upload data.

        Args:
            files: List of file data

        Raises:
            ApiException: For validation errors
        """
        if not files:
            return

        for file_info in files:
            required_fields = ["field", "filename", "content"]
            for field in required_fields:
                if field not in file_info:
                    raise ApiException(f"Missing required field in file upload: {field}")

            # Validate content type if provided
            if "content_type" in file_info:
                content_type = file_info["content_type"]
                if not isinstance(content_type, str) or "/" not in content_type:
                    raise ApiException(f"Invalid content_type: {content_type}")

    def _is_valid_email(self, email: str) -> bool:
        """
        Basic email validation.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
