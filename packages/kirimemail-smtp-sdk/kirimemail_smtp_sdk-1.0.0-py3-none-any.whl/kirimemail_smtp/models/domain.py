"""
Domain model for domain management.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Domain(BaseModel):
    """
    Domain model for domain management.
    """
    domain: str = Field(..., description="Domain name")
    dkim_public_key: Optional[str] = Field(None, description="DKIM public key")
    dkim_selector: Optional[str] = Field(None, description="DKIM selector")
    dkim_key_length: Optional[int] = Field(None, description="DKIM key length")
    is_verified: Optional[bool] = Field(None, description="Whether the domain is verified")
    tracking_settings: Optional[dict[str, Any]] = Field(None, description="Tracking settings")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
