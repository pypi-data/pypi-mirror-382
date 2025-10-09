# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .vector_store_file import VectorStoreFile

__all__ = ["FileListResponse", "Pagination"]


class Pagination(BaseModel):
    has_more: bool
    """
    Contextual direction-aware flag: True if more items exist in the requested
    pagination direction. For 'after': more items after this page. For 'before':
    more items before this page.
    """

    first_cursor: Optional[str] = None
    """Cursor of the first item in this page.

    Use for backward pagination. None if page is empty.
    """

    last_cursor: Optional[str] = None
    """Cursor of the last item in this page.

    Use for forward pagination. None if page is empty.
    """

    total: Optional[int] = None
    """Total number of items available across all pages.

    Only included when include_total=true was requested. Expensive operation - use
    sparingly.
    """


class FileListResponse(BaseModel):
    pagination: Pagination
    """Response model for cursor-based pagination."""

    object: Optional[Literal["list"]] = None
    """The object type of the response"""

    data: List[VectorStoreFile]
    """The list of vector store files"""
