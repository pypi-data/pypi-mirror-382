"""
Tests for the CredentialsApi class.
"""

import pytest
from unittest.mock import AsyncMock

from kirimemail_smtp.api.credentials import CredentialsApi


class TestCredentialsApi:
    """Test cases for CredentialsApi."""
    
    def test_credentials_api_init(self):
        """Test CredentialsApi initialization."""
        mock_client = AsyncMock()
        api = CredentialsApi(mock_client)
        
        assert api.client is mock_client
    
    @pytest.mark.asyncio
    async def test_list_credentials(self, mock_smtp_client):
        """Test listing credentials."""
        mock_response = {
            "success": True,
            "data": [
                {"username": "user1", "domain": "example.com", "is_active": True},
                {"username": "user2", "domain": "example.com", "is_active": False}
            ],
            "pagination": {
                "current_page": 1,
                "per_page": 10,
                "total": 2,
                "last_page": 1
            }
        }
        
        mock_smtp_client.get.return_value = mock_response
        
        api = CredentialsApi(mock_smtp_client)
        result = await api.list_credentials(domain="example.com", page=1, limit=10)
        
        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["pagination"]["total"] == 2
        mock_smtp_client.get.assert_called_once_with("/api/domains/example.com/credentials", params={"page": 1, "limit": 10})
    
    @pytest.mark.asyncio
    async def test_get_credential(self, mock_smtp_client):
        """Test getting a credential."""
        credential_username = "test@example.com"
        mock_response = {
            "success": True,
            "data": {
                "username": credential_username,
                "domain": "example.com",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
        
        mock_smtp_client.get.return_value = mock_response
        
        api = CredentialsApi(mock_smtp_client)
        result = await api.get_credential(domain="example.com", credential=credential_username)
        
        assert result["success"] is True
        assert result["data"]["username"] == credential_username
        assert result["data"]["domain"] == "example.com"
        mock_smtp_client.get.assert_called_once_with("/api/domains/example.com/credentials/test@example.com")
    
    @pytest.mark.asyncio
    async def test_create_credential(self, mock_smtp_client):
        """Test creating a credential."""
        mock_response = {
            "success": True,
            "message": "Credential created successfully",
            "data": {
                "username": "newuser@example.com",
                "domain": "example.com",
                "is_active": True
            }
        }
        
        mock_smtp_client.post.return_value = mock_response
        
        api = CredentialsApi(mock_smtp_client)
        result = await api.create_credential(domain="example.com", username="newuser@example.com")
        
        assert result["success"] is True
        assert result["data"]["username"] == "newuser@example.com"
        mock_smtp_client.post.assert_called_once_with("/api/domains/example.com/credentials", data={"username": "newuser@example.com"})
    
    @pytest.mark.asyncio
    async def test_reset_password(self, mock_smtp_client):
        """Test resetting credential password."""
        mock_response = {
            "success": True,
            "message": "Password reset successfully",
            "data": {
                "username": "test@example.com",
                "domain": "example.com",
                "is_active": True
            }
        }
        
        mock_smtp_client.put.return_value = mock_response
        
        api = CredentialsApi(mock_smtp_client)
        result = await api.reset_password(domain="example.com", credential="test@example.com")
        
        assert result["success"] is True
        mock_smtp_client.put.assert_called_once_with("/api/domains/example.com/credentials/test@example.com/reset-password")
    
    @pytest.mark.asyncio
    async def test_delete_credential(self, mock_smtp_client):
        """Test deleting a credential."""
        mock_response = {
            "success": True,
            "message": "Credential deleted successfully"
        }
        
        mock_smtp_client.delete.return_value = mock_response
        
        api = CredentialsApi(mock_smtp_client)
        result = await api.delete_credential(domain="example.com", credential="test@example.com")
        
        assert result["success"] is True
        mock_smtp_client.delete.assert_called_once_with("/api/domains/example.com/credentials/test@example.com")