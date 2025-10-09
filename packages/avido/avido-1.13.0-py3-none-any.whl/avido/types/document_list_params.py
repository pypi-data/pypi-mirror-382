# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DocumentListParams"]


class DocumentListParams(TypedDict, total=False):
    assignee: str
    """Filter by assignee user ID"""

    limit: int
    """Number of items per page"""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Field to order by"""

    order_dir: Annotated[Literal["asc", "desc"], PropertyInfo(alias="orderDir")]
    """Order direction"""

    scrape_job_id: Annotated[str, PropertyInfo(alias="scrapeJobId")]
    """Filter by scrape job ID"""

    skip: int
    """Number of items to skip"""

    status: Literal["DRAFT", "REVIEW", "APPROVED", "ARCHIVED"]
    """Filter by document status"""
