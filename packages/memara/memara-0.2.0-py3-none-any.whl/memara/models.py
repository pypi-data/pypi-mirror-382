"""
Memara SDK Data Models

Pydantic models for Memara API requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Memory(BaseModel):
    """A memory object from the Memara API."""

    id: str = Field(..., description="Unique identifier for the memory")
    content: str = Field(..., description="The content of the memory")
    tags: List[str] = Field(
        default_factory=list, description="Tags associated with the memory"
    )
    source: str = Field(default="sdk", description="The source of the memory")
    importance: int = Field(
        default=5, ge=1, le=10, description="Importance level (1-10)"
    )
    space_id: Optional[str] = Field(
        None, description="ID of the space this memory belongs to"
    )
    created_at: datetime = Field(..., description="When the memory was created")
    updated_at: Optional[datetime] = Field(None, description="When the memory was last updated")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CreateMemoryRequest(BaseModel):
    """Request model for creating a new memory."""

    content: str = Field(..., description="The content of the memory")
    tags: List[str] = Field(
        default_factory=list, description="Tags associated with the memory"
    )
    source: str = Field(default="sdk", description="The source of the memory")
    importance: int = Field(
        default=5, ge=1, le=10, description="Importance level (1-10)"
    )
    space_id: Optional[str] = Field(
        None, description="ID of the space to create the memory in"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class SearchResult(BaseModel):
    """A search result containing memories and metadata."""

    memories: List[Memory] = Field(..., description="List of matching memories")
    total: int = Field(..., description="Total number of matching memories")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of results per page")
    query: str = Field(..., description="The search query used")


class Space(BaseModel):
    """A memory space object from the Memara API."""

    id: str = Field(..., description="Unique identifier for the space")
    name: str = Field(..., description="Name of the space")
    icon: str = Field(default="📁", description="Icon for the space")
    color: str = Field(default="#6366F1", description="Color code for the space")
    template_type: str = Field(
        default="custom", description="Template type used for the space"
    )
    privacy_level: str = Field(
        default="personal", description="Privacy level of the space"
    )
    memory_count: int = Field(default=0, description="Number of memories in this space")
    created_at: datetime = Field(..., description="When the space was created")
    updated_at: datetime = Field(..., description="When the space was last updated")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CreateSpaceRequest(BaseModel):
    """Request model for creating a new space."""

    name: str = Field(..., description="Name of the space")
    icon: str = Field(default="📁", description="Icon for the space")
    color: str = Field(default="#6366F1", description="Color code for the space")
    template_type: str = Field(
        default="custom", description="Template type for the space"
    )
    privacy_level: str = Field(
        default="personal", description="Privacy level of the space"
    )


class PaginatedResponse(BaseModel):
    """Base model for paginated API responses."""

    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class MemoryListResponse(PaginatedResponse):
    """Paginated response for memory listings."""

    items: List[Memory] = Field(..., description="List of memories")


class SpaceListResponse(BaseModel):
    """Response model for space listings."""

    spaces: List[Space] = Field(..., description="List of spaces")
