# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DocumentListChunksParams"]


class DocumentListChunksParams(TypedDict, total=False):
    document_id: Required[Annotated[str, PropertyInfo(alias="documentId")]]
    """Filter by document ID"""

    limit: int
    """Number of items per page"""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Field to order by"""

    order_dir: Annotated[Literal["asc", "desc"], PropertyInfo(alias="orderDir")]
    """Order direction"""

    skip: int
    """Number of items to skip"""

    status: Literal["DRAFT", "REVIEW", "APPROVED", "ARCHIVED"]
    """Filter by document status"""
