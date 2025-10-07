"""
Suppression model for email suppressions.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Suppression(BaseModel):
    """
    Email suppression model.
    """
    email: str = Field(..., description="Email address")
    domain: Optional[str] = Field(None, description="Domain name")
    type: Optional[str] = Field(None, description="Suppression type (bounce, unsubscribe, whitelist)")
    reason: Optional[str] = Field(None, description="Suppression reason")
    source: Optional[str] = Field(None, description="Suppression source")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
