# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from .element_type import ElementType
from .return_format import ReturnFormat
from .chunking_strategy import ChunkingStrategy
from .parsing_job_status import ParsingJobStatus

__all__ = ["ParsingJob", "Result", "ResultChunk", "ResultChunkElement"]


class ResultChunkElement(BaseModel):
    type: ElementType
    """The type of the extracted element"""

    confidence: float
    """The confidence score of the extraction"""

    bbox: List[object]
    """The bounding box coordinates [x1, y1, x2, y2]"""

    page: int
    """The page number where the element was found"""

    content: str
    """The full content of the extracted element"""

    summary: Optional[str] = None
    """A brief summary of the element's content"""


class ResultChunk(BaseModel):
    content: str
    """The full content of the chunk"""

    content_to_embed: str
    """The content of the chunk to embed"""

    elements: List[ResultChunkElement]
    """List of elements contained in this chunk"""


class Result(BaseModel):
    chunking_strategy: ChunkingStrategy
    """The strategy used for chunking the document"""

    return_format: ReturnFormat
    """The format of the returned content"""

    element_types: List[ElementType]
    """The types of elements extracted"""

    chunks: List[ResultChunk]
    """List of extracted chunks from the document"""

    page_sizes: Optional[List[List[object]]] = None
    """List of (width, height) tuples for each page"""


class ParsingJob(BaseModel):
    id: str
    """The ID of the job"""

    file_id: str
    """The ID of the file to parse"""

    filename: Optional[str] = None
    """The name of the file"""

    status: ParsingJobStatus
    """The status of the job"""

    error: Optional[object] = None
    """The error of the job"""

    result: Optional[Result] = None
    """Result of document parsing operation."""

    started_at: Optional[datetime] = None
    """The started time of the job"""

    finished_at: Optional[datetime] = None
    """The finished time of the job"""

    created_at: Optional[datetime] = None
    """The creation time of the job"""

    updated_at: Optional[datetime] = None
    """The updated time of the job"""

    object: Optional[Literal["parsing_job"]] = None
    """The type of the object"""
