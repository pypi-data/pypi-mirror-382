# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .embedding import Embedding
from .shared.usage import Usage
from .encoding_format import EncodingFormat
from .multi_encoding_embedding import MultiEncodingEmbedding

__all__ = ["EmbeddingCreateResponse"]


class EmbeddingCreateResponse(BaseModel):
    usage: Usage
    """The usage of the model"""

    model: str
    """The model used"""

    data: Union[List[Embedding], List[MultiEncodingEmbedding]]
    """The created embeddings."""

    object: Optional[Literal["list"]] = None
    """The object type of the response"""

    normalized: bool
    """Whether the embeddings are normalized."""

    encoding_format: Union[EncodingFormat, List[EncodingFormat]]
    """The encoding formats of the embeddings."""

    dimensions: Optional[int] = None
    """The number of dimensions used for the embeddings."""
