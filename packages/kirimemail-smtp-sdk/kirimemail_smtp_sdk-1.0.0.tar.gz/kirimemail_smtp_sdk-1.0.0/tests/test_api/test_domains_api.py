"""
Tests for the DomainsApi class.
"""

import pytest
from unittest.mock import AsyncMock

from kirimemail_smtp.api.domains import DomainsApi


class TestDomainsApi:
    """Test cases for DomainsApi."""
    
    def test_domains_api_init(self):
        """Test DomainsApi initialization."""
        mock_client = AsyncMock()
        api = DomainsApi(mock_client)
        
        assert api.client is mock_client
    
    @pytest.mark.asyncio
    async def test_list_domains(self, mock_smtp_client):
        """Test listing domains."""
        mock_response = {
            "success": True,
            "data": [
                {"id": "dom-1", "domain": "example.com", "status": "verified"},
                {"id": "dom-2", "domain": "test.com", "status": "pending"}
            ],
            "pagination": {
                "page": 1,
                "limit": 10,
                "total": 2,
                "total_pages": 1
            }
        }
        
        mock_smtp_client.get.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.list_domains(page=1, limit=10)
        
        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["pagination"]["total"] == 2
        mock_smtp_client.get.assert_called_once_with("/api/domains", params={"limit": 10, "page": 1})
    
    @pytest.mark.asyncio
    async def test_get_domain(self, mock_smtp_client):
        """Test getting a domain."""
        domain_name = "example.com"
        mock_response = {
            "success": True,
            "data": {
                "id": "dom-123",
                "domain": domain_name,
                "status": "verified",
                "dns_records": [
                    {"type": "TXT", "name": "kirim._domainkey", "value": "v=DKIM1; k=rsa; p=..."}
                ]
            }
        }
        
        mock_smtp_client.get.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.get_domain(domain_name)
        
        assert result["success"] is True
        assert result["data"]["domain"] == domain_name
        mock_smtp_client.get.assert_called_once_with(f"/api/domains/{domain_name}")
    
    @pytest.mark.asyncio
    async def test_create_domain(self, mock_smtp_client):
        """Test creating a domain."""
        domain_name = "newdomain.com"
        mock_response = {
            "success": True,
            "message": "Domain created successfully",
            "data": {
                "id": "dom-new-123",
                "domain": "newdomain.com",
                "status": "pending"
            }
        }
        
        mock_smtp_client.post.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.create_domain(domain_name)
        
        assert result["success"] is True
        assert result["data"]["domain"] == "newdomain.com"
        mock_smtp_client.post.assert_called_once_with("/api/domains", data={"domain": "newdomain.com", "dkim_key_length": 2048})
    
    @pytest.mark.asyncio
    async def test_update_domain(self, mock_smtp_client):
        """Test updating a domain."""
        domain_name = "example.com"
        update_data = {"return_path_subdomain": "bounce"}
        mock_response = {
            "success": True,
            "message": "Domain updated successfully",
            "data": {
                "id": "dom-123",
                "domain": "example.com",
                "return_path_subdomain": "bounce"
            }
        }
        
        mock_smtp_client.put.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.update_domain(domain_name, update_data)
        
        assert result["success"] is True
        assert result["data"]["return_path_subdomain"] == "bounce"
        mock_smtp_client.put.assert_called_once_with(f"/api/domains/{domain_name}", data={"return_path_subdomain": "bounce"})
    
    @pytest.mark.asyncio
    async def test_delete_domain(self, mock_smtp_client):
        """Test deleting a domain."""
        domain_name = "example.com"
        mock_response = {
            "success": True,
            "message": "Domain deleted successfully"
        }
        
        mock_smtp_client.delete.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.delete_domain(domain_name)
        
        assert result["success"] is True
        mock_smtp_client.delete.assert_called_once_with(f"/api/domains/{domain_name}")
    
    @pytest.mark.asyncio
    async def test_setup_auth_domain(self, mock_smtp_client):
        """Test setting up auth domain."""
        domain_name = "example.com"
        config = {"some_config": "value"}
        mock_response = {
            "success": True,
            "message": "Auth domain setup completed",
            "data": {
                "domain": domain_name,
                "auth_setup": True
            }
        }
        
        mock_smtp_client.post.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.setup_auth_domain(domain_name, config)
        
        assert result["success"] is True
        mock_smtp_client.post.assert_called_once_with(f"/api/domains/{domain_name}/setup-auth-domain", data=config)
    
    @pytest.mark.asyncio
    async def test_verify_mandatory_records(self, mock_smtp_client):
        """Test verifying mandatory domain."""
        domain_name = "example.com"
        mock_response = {
            "success": True,
            "message": "Mandatory verification completed",
            "data": {
                "domain": domain_name,
                "verified": True
            }
        }
        
        mock_smtp_client.post.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.verify_mandatory_records(domain_name)
        
        assert result["success"] is True
        mock_smtp_client.post.assert_called_once_with(f"/api/domains/{domain_name}/verify-mandatory")
    
    @pytest.mark.asyncio
    async def test_verify_auth_domain_records(self, mock_smtp_client):
        """Test verifying auth domain."""
        domain_name = "example.com"
        mock_response = {
            "success": True,
            "message": "Auth domain verification completed",
            "data": {
                "domain": domain_name,
                "auth_verified": True
            }
        }
        
        mock_smtp_client.post.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.verify_auth_domain_records(domain_name)
        
        assert result["success"] is True
        mock_smtp_client.post.assert_called_once_with(f"/api/domains/{domain_name}/verify-auth-domain")
    
    @pytest.mark.asyncio
    async def test_setup_tracklink(self, mock_smtp_client):
        """Test setting up tracklink."""
        domain_name = "example.com"
        tracking_domain = "track.example.com"
        mock_response = {
            "success": True,
            "message": "Tracklink setup completed",
            "data": {
                "domain": domain_name,
                "tracklink_setup": True
            }
        }
        
        mock_smtp_client.post.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.setup_tracklink(domain_name, tracking_domain)
        
        assert result["success"] is True
        mock_smtp_client.post.assert_called_once_with(f"/api/domains/{domain_name}/setup-tracklink", data={"tracking_domain": tracking_domain})
    
    @pytest.mark.asyncio
    async def test_verify_tracklink(self, mock_smtp_client):
        """Test verifying tracklink."""
        domain_name = "example.com"
        mock_response = {
            "success": True,
            "message": "Tracklink verification completed",
            "data": {
                "domain": domain_name,
                "tracklink_verified": True
            }
        }
        
        mock_smtp_client.post.return_value = mock_response
        
        api = DomainsApi(mock_smtp_client)
        result = await api.verify_tracklink(domain_name)
        
        assert result["success"] is True
        mock_smtp_client.post.assert_called_once_with(f"/api/domains/{domain_name}/verify-tracklink")
    
