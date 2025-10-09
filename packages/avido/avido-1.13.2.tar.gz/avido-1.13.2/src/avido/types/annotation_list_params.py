# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AnnotationListParams"]


class AnnotationListParams(TypedDict, total=False):
    end: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """End date (ISO8601) for filtering annotations."""

    limit: int
    """Number of items per page"""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Field to order by"""

    order_dir: Annotated[Literal["asc", "desc"], PropertyInfo(alias="orderDir")]
    """Order direction"""

    skip: int
    """Number of items to skip"""

    start: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Start date (ISO8601) for filtering annotations."""

    title: str
    """Filter by annotation title"""
