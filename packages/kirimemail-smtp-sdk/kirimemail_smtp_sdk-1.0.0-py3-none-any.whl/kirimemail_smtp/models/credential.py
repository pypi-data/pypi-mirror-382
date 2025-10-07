"""
Credential model for SMTP credentials.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Credential(BaseModel):
    """
    SMTP credential model.
    """
    username: str = Field(..., description="Username for the SMTP credential")
    domain: str = Field(..., description="Domain name")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    is_active: Optional[bool] = Field(True, description="Whether the credential is active")

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
