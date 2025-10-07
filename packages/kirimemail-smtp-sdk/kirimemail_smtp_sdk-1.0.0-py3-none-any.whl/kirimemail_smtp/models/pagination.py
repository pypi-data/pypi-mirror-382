"""
Pagination model for API responses.
"""

from typing import Optional

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """
    Pagination metadata for API responses.
    """
    total: int = Field(..., description="Total number of items")
    per_page: int = Field(..., description="Number of items per page")
    current_page: int = Field(..., description="Current page number")
    last_page: int = Field(..., description="Last page number")

    class Config:
        """Pydantic configuration."""
        populate_by_name = True

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.current_page < self.last_page

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.current_page > 1

    @property
    def next_page(self) -> Optional[int]:
        """Get the next page number."""
        return self.current_page + 1 if self.has_next else None

    @property
    def previous_page(self) -> Optional[int]:
        """Get the previous page number."""
        return self.current_page - 1 if self.has_previous else None
