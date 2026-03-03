"""
STTS Pagination Utilities
─────────────────────────
Standardized pagination for list endpoints.
"""

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def skip(self) -> int:
        """Calculate the number of documents to skip."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    """Standardized paginated response wrapper."""

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: list, total: int, page: int, page_size: int) -> "PaginatedResponse":
        """Factory method to build paginated response."""
        total_pages = max(1, (total + page_size - 1) // page_size)
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
