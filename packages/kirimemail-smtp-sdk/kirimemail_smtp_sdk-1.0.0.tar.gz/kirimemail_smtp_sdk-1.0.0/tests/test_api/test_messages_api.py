"""
Tests for the MessagesApi class.
"""

import pytest
from unittest.mock import AsyncMock

from kirimemail_smtp.api.messages import MessagesApi
from kirimemail_smtp.exceptions import ValidationException


class TestMessagesApi:
    """Test cases for MessagesApi."""
    
    def test_messages_api_init(self):
        """Test MessagesApi initialization."""
        mock_client = AsyncMock()
        api = MessagesApi(mock_client)
        
        assert api.client is mock_client
    
    @pytest.mark.asyncio
    async def test_send_message(self, mock_smtp_client, sample_email_message):
        """Test sending a message."""
        mock_smtp_client.post.return_value = {
            "success": True,
            "message": "Message sent successfully",
            "data": {"message_id": "msg-123"}
        }
        
        api = MessagesApi(mock_smtp_client)
        result = await api.send_message("example.com", sample_email_message)
        
        assert result["success"] is True
        assert result["data"]["message_id"] == "msg-123"
        mock_smtp_client.post.assert_called_once_with("/api/domains/example.com/message", data=sample_email_message)
    
    @pytest.mark.asyncio
    async def test_send_template_message(self, mock_smtp_client, sample_template_message):
        """Test sending a template message."""
        mock_smtp_client.post.return_value = {
            "success": True,
            "message": "Template message sent successfully",
            "data": {"message_id": "msg-template-123"}
        }
        
        api = MessagesApi(mock_smtp_client)
        result = await api.send_template_message("example.com", sample_template_message)
        
        assert result["success"] is True
        assert result["data"]["message_id"] == "msg-template-123"
        mock_smtp_client.post.assert_called_once_with("/api/domains/example.com/message/template", data=sample_template_message)
    
    @pytest.mark.asyncio
    async def test_send_message_with_attachment(self, mock_smtp_client, sample_email_message, sample_file):
        """Test sending a message with attachment."""
        mock_smtp_client.post_multipart.return_value = {
            "success": True,
            "message": "Message with attachment sent successfully",
            "data": {"message_id": "msg-attachment-123"}
        }
        
        api = MessagesApi(mock_smtp_client)
        result = await api.send_message_with_attachments("example.com", sample_email_message, [sample_file])
        
        assert result["success"] is True
        assert result["data"]["message_id"] == "msg-attachment-123"
        mock_smtp_client.post_multipart.assert_called_once_with("/api/domains/example.com/message", data=sample_email_message, files=[sample_file])
    
    @pytest.mark.asyncio
    async def test_send_message_validation_error(self, mock_smtp_client):
        """Test sending a message with validation error."""
        from kirimemail_smtp.exceptions import ApiException
        
        invalid_message = {"to": "invalid-email"}  # Missing required fields
        
        api = MessagesApi(mock_smtp_client)
        
        with pytest.raises(ApiException) as exc_info:
            await api.send_message("example.com", invalid_message)
        
        assert "Missing required field: from" in str(exc_info.value)
    
