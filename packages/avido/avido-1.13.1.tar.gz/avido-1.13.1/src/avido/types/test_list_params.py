# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TestListParams"]


class TestListParams(TypedDict, total=False):
    limit: int
    """Number of items per page"""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Field to order by"""

    order_dir: Annotated[Literal["asc", "desc"], PropertyInfo(alias="orderDir")]
    """Order direction"""

    skip: int
    """Number of items to skip"""

    status: str
    """Filter by evaluation status"""

    task_id: Annotated[str, PropertyInfo(alias="taskId")]
    """Filter by task ID"""

    trace_id: Annotated[str, PropertyInfo(alias="traceId")]
    """Filter by trace ID"""

    type: str
    """Filter by evaluation type"""
