"""Pydantic models for request/response validation."""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from .types import LocationType, SearchType

__all__ = [
    "SearchRequest",
    "SearchResult",
    "ImageResult",
    "SearchResponse",
    "ErrorResponse",
]


class SearchRequest(BaseModel):
    """Request model for search API."""

    queries: list[str] = Field(..., min_length=1, max_length=100, description="Search queries")
    type: SearchType = Field(default=SearchType.SEARCH, description="Search type")
    num: int = Field(default=10, ge=1, le=100, description="Number of results per query")
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    gl: str = Field(default="us", description="Country code (e.g., 'us', 'cn')")
    hl: str = Field(default="en", description="Interface language (e.g., 'en', 'zh-CN')")
    lr: str = Field(default="en", description="Content language restriction (e.g., 'en', 'zh-CN')")
    location: LocationType | None = Field(
        default=None,
        description="Location for local search (e.g., LocationType.US, LocationType.GB)",
    )

    @field_validator("queries")
    @classmethod
    def validate_queries(cls, v: list[str]) -> list[str]:
        """Validate search queries."""
        if not v:
            raise ValueError("At least one query is required")
        for query in v:
            if not query or len(query) > 2048:
                raise ValueError("Query must be between 1 and 2048 characters")
        return v


class SearchResult(BaseModel):
    """Single search result item."""

    title: str = Field(..., description="Result title")
    link: str = Field(..., description="Result URL")
    snippet: str = Field(..., description="Result description snippet")
    position: int = Field(..., description="Result position in SERP")


class ImageResult(BaseModel):
    """Image search result item."""

    title: str = Field(..., description="Image title")
    link: str = Field(..., description="Image source URL")
    thumbnail: str = Field(..., description="Thumbnail URL")
    source: str = Field(..., description="Source website")
    source_link: str = Field(..., description="Source page URL")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    position: int = Field(..., description="Result position")


class SearchResponse(BaseModel):
    """Response model for search API."""

    success: bool = Field(..., description="Whether request was successful")
    query: str = Field(..., description="Original search query")
    total_results: str = Field(..., description="Total result count estimate")
    search_time: str = Field(..., description="Search time in seconds")
    results: list[SearchResult] | list[ImageResult] = Field(
        default_factory=list, description="Search results"
    )
    credits_used: int = Field(..., description="Credits consumed by this request")


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_code: str | None = Field(default=None, description="Error code")
    details: dict[str, Any] | None = Field(default=None, description="Additional error details")
