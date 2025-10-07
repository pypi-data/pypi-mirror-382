"""
Pytest configuration and fixtures.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from kirimemail_smtp import SmtpClient


@pytest.fixture
def mock_smtp_client():
    """Create a mock SMTP client for testing."""
    client = MagicMock(spec=SmtpClient)
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.post_multipart = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    client.stream = AsyncMock()
    client.close = AsyncMock()
    return client


@pytest.fixture
def sample_email_message():
    """Sample email message for testing."""
    return {
        "from": "sender@example.com",
        "from_name": "Company Name",
        "to": "recipient@example.com",
        "subject": "Test Email",
        "text": "This is a test email.",
        "html": "<p>This is a test email.</p>",
    }


@pytest.fixture
def sample_template_message():
    """Sample template message for testing."""
    return {
        "template_guid": "template-uuid-123",
        "from": "sender@example.com",
        "from_name": "Company Name",
        "to": "recipient@example.com",
        "variables": {
            "name": "John Doe",
            "product": "Premium Plan",
        },
    }


@pytest.fixture
def sample_file():
    """Sample file for testing."""
    return {
        "field": "attachment",
        "filename": "test.txt",
        "content": b"This is test file content.",
        "content_type": "text/plain",
    }


@pytest.fixture
def mock_api_response():
    """Sample API response for testing."""
    return {
        "success": True,
        "message": "Operation completed successfully",
        "data": {
            "id": "test-id-123",
            "status": "sent",
        },
    }