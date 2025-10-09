# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["FileCreateParams", "Experimental"]


class FileCreateParams(TypedDict, total=False):
    metadata: object
    """Optional metadata for the file"""

    experimental: Experimental
    """Strategy for adding the file"""

    file_id: Required[str]
    """ID of the file to add"""


class Experimental(TypedDict, total=False):
    parsing_strategy: Literal["fast", "high_quality"]
    """Strategy for adding the file"""

    contextualization: bool
    """Whether to contextualize the file"""
