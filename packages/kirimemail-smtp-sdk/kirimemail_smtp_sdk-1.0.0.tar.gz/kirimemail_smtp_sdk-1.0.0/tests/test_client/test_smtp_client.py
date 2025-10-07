"""
Tests for the SmtpClient class.
"""

import pytest
from unittest.mock import AsyncMock, patch

from kirimemail_smtp import SmtpClient
from kirimemail_smtp.exceptions import (
    ApiException,
    AuthenticationException,
    ValidationException,
    NotFoundException,
    ServerException,
)


class TestSmtpClient:
    """Test cases for SmtpClient."""
    
    def test_client_initialization(self):
        """Test SmtpClient initialization."""
        client = SmtpClient("test-user", "test-token")
        
        assert client.username == "test-user"
        assert client.token == "test-token"
        assert client.base_url == "https://smtp-app.kirim.email"
        assert client.has_auth() is True
    
    def test_client_initialization_without_auth(self):
        """Test SmtpClient initialization without auth."""
        client = SmtpClient()
        
        assert client.username is None
        assert client.token is None
        assert client.has_auth() is False
    
    def test_client_custom_base_url(self):
        """Test SmtpClient with custom base URL."""
        custom_url = "https://api.example.com"
        client = SmtpClient(base_url=custom_url)
        
        assert client.get_base_url() == custom_url
    
    def test_set_auth(self):
        """Test setting authentication credentials."""
        client = SmtpClient()
        client.set_auth("new-user", "new-token")
        
        assert client.username == "new-user"
        assert client.token == "new-token"
        assert client.has_auth() is True
    
    def test_set_base_url(self):
        """Test setting base URL."""
        client = SmtpClient()
        new_url = "https://new-api.example.com"
        client.set_base_url(new_url)
        
        assert client.get_base_url() == new_url
    
    def test_get_auth_headers(self):
        """Test authentication headers generation."""
        client = SmtpClient("test-user", "test-token")
        headers = client._get_auth_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")
        assert headers["User-Agent"] == "kirimemail-smtp-sdk/1.0.0"
        assert headers["Accept"] == "application/json"
    
    def test_get_auth_headers_without_auth(self):
        """Test authentication headers without credentials."""
        client = SmtpClient()
        headers = client._get_auth_headers()
        
        assert "Authorization" not in headers
        assert headers["User-Agent"] == "kirimemail-smtp-sdk/1.0.0"
        assert headers["Accept"] == "application/json"
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test SmtpClient as async context manager."""
        client = SmtpClient("test-user", "test-token")
        
        async with client as c:
            assert c is client
            assert c.has_auth() is True
        
        # Client should be closed after context
        # Note: We can't easily test if client is closed without mocking
    
    @pytest.mark.asyncio
    async def test_close_method(self):
        """Test close method."""
        client = SmtpClient("test-user", "test-token")
        
        # Should not raise an exception
        await client.close()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request')
    async def test_make_request_success(self, mock_request):
        """Test successful request making."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json = AsyncMock(return_value={"success": True, "data": "test"})
        mock_request.return_value = mock_response
        
        client = SmtpClient("test-user", "test-token")
        result = await client._make_request("GET", "/test")
        
        assert result == {"success": True, "data": "test"}
        mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request')
    async def test_make_request_authentication_error(self, mock_request):
        """Test authentication error handling."""
        # Mock auth error response
        mock_response = AsyncMock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_response.json = AsyncMock(return_value={"message": "Unauthorized"})
        mock_request.return_value = mock_response
        
        client = SmtpClient("test-user", "test-token")
        
        with pytest.raises(AuthenticationException) as exc_info:
            await client._make_request("GET", "/test")
        
        assert "Unauthorized" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request')
    async def test_make_request_validation_error(self, mock_request):
        """Test validation error handling."""
        # Mock validation error response
        mock_response = AsyncMock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.json = AsyncMock(return_value={
            "message": "Validation failed",
            "errors": {"field": ["error message"]}
        })
        mock_request.return_value = mock_response
        
        client = SmtpClient("test-user", "test-token")
        
        with pytest.raises(ValidationException) as exc_info:
            await client._make_request("GET", "/test")
        
        assert "Validation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request')
    async def test_make_request_not_found_error(self, mock_request):
        """Test not found error handling."""
        # Mock not found response
        mock_response = AsyncMock()
        mock_response.is_success = False
        mock_response.status_code = 404
        mock_response.json = AsyncMock(return_value={"message": "Not found"})
        mock_request.return_value = mock_response
        
        client = SmtpClient("test-user", "test-token")
        
        with pytest.raises(NotFoundException) as exc_info:
            await client._make_request("GET", "/test")
        
        assert "Not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request')
    async def test_make_request_server_error(self, mock_request):
        """Test server error handling."""
        # Mock server error response
        mock_response = AsyncMock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_response.json = AsyncMock(return_value={"message": "Server error"})
        mock_request.return_value = mock_response
        
        client = SmtpClient("test-user", "test-token")
        
        with pytest.raises(ServerException) as exc_info:
            await client._make_request("GET", "/test")
        
        assert "Server error" in str(exc_info.value)