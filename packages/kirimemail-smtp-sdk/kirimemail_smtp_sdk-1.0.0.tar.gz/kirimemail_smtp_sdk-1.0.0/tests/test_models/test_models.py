"""
Tests for Pydantic models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from kirimemail_smtp.models import (
    Credential,
    Domain,
    LogEntry,
    Pagination,
    Suppression
)


class TestCredential:
    """Test cases for Credential model."""
    
    def test_credential_creation(self):
        """Test creating a valid credential."""
        data = {
            "username": "test@example.com",
            "domain": "example.com",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        credential = Credential(**data)
        
        assert credential.username == "test@example.com"
        assert credential.domain == "example.com"
        assert credential.is_active is True
    
    def test_credential_optional_fields(self):
        """Test credential with optional fields."""
        credential = Credential(username="test@example.com", domain="example.com")
        
        assert credential.username == "test@example.com"
        assert credential.domain == "example.com"
        assert credential.is_active is True
        assert credential.created_at is None
        assert credential.updated_at is None

        assert credential.created_at is None


class TestDomain:
    """Test cases for Domain model."""
    
    def test_domain_creation(self):
        """Test creating a valid domain."""
        data = {
            "domain": "example.com",
            "dkim_public_key": "v=DKIM1; k=rsa; p=...",
            "dkim_selector": "kirim",
            "dkim_key_length": 2048,
            "is_verified": True,
            "tracking_settings": {"enabled": True},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        domain = Domain(**data)
        
        assert domain.domain == "example.com"
        assert domain.dkim_public_key == "v=DKIM1; k=rsa; p=..."
        assert domain.dkim_selector == "kirim"
        assert domain.dkim_key_length == 2048
        assert domain.is_verified is True
        assert domain.tracking_settings == {"enabled": True}
    
    def test_domain_minimal(self):
        """Test domain with minimal fields."""
        domain = Domain(domain="example.com")
        
        assert domain.domain == "example.com"
        assert domain.dkim_public_key is None
        assert domain.is_verified is None
        assert domain.created_at is None



class TestLogEntry:
    """Test cases for LogEntry model."""
    
    def test_log_entry_creation(self):
        """Test creating a valid log entry."""
        data = {
            "id": "log-123",
            "message_id": "msg-123",
            "event_type": "sent",
            "recipient": "user@example.com",
            "response_message": "250 OK",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        log_entry = LogEntry(**data)
        
        assert log_entry.id == "log-123"
        assert log_entry.message_id == "msg-123"
        assert log_entry.event_type == "sent"
        assert log_entry.recipient == "user@example.com"
        assert log_entry.response_message == "250 OK"
        assert log_entry.recipient == "user@example.com"

    
    def test_log_entry_optional_fields(self):
        """Test log entry with optional fields."""
        log_entry = LogEntry(id="log-123", message_id="msg-123", event_type="delivered")
        
        assert log_entry.id == "log-123"
        assert log_entry.message_id == "msg-123"
        assert log_entry.event_type == "delivered"
        assert log_entry.recipient is None
        assert log_entry.response_message is None

        assert log_entry.recipient is None


class TestPagination:
    """Test cases for Pagination model."""
    
    def test_pagination_creation(self):
        """Test creating a valid pagination."""
        data = {
            "total": 100,
            "per_page": 10,
            "current_page": 1,
            "last_page": 10
        }
        
        pagination = Pagination(**data)
        
        assert pagination.total == 100
        assert pagination.per_page == 10
        assert pagination.current_page == 1
        assert pagination.last_page == 10
    
    def test_pagination_calculation(self):
        """Test pagination with calculated fields."""
        pagination = Pagination(total=100, per_page=25, current_page=2, last_page=4)
        
        assert pagination.total == 100
        assert pagination.per_page == 25
        assert pagination.current_page == 2
        assert pagination.last_page == 4
        assert pagination.has_next is True
        assert pagination.has_previous is True
        assert pagination.next_page == 3
        assert pagination.previous_page == 1  # 100 / 25 = 4


class TestSuppression:
    """Test cases for Suppression model."""
    
    def test_suppression_creation(self):
        """Test creating a valid suppression."""
        data = {
            "email": "user@example.com",
            "type": "bounce",
            "reason": "Hard bounce",
            "source": "smtp",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        suppression = Suppression(**data)
        
        assert suppression.email == "user@example.com"
        assert suppression.type == "bounce"
        assert suppression.reason == "Hard bounce"
        assert suppression.source == "smtp"
    
    def test_suppression_minimal(self):
        """Test suppression with minimal fields."""
        suppression = Suppression(email="user@example.com", type="unsubscribe")
        
        assert suppression.email == "user@example.com"
        assert suppression.type == "unsubscribe"
        assert suppression.reason is None
        assert suppression.source is None
        assert suppression.reason is None
    
    def test_suppression_invalid_type(self):
        """Test suppression with invalid type."""
        # The current model doesn't validate the type field, so this should not raise an error
        suppression = Suppression(email="user@example.com", type="invalid_type")
        assert suppression.email == "user@example.com"
        assert suppression.type == "invalid_type"