# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .test import Test
from .._models import BaseModel

__all__ = ["Run"]


class Run(BaseModel):
    id: str
    """Unique identifier of the run"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the run was created"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the run was last modified"""

    status: Literal["PENDING", "IN_PROGRESS", "PASSED", "COMPLETED", "FAILED"]
    """Status of the evaluation/test.

    Valid options: PENDING, IN_PROGRESS, PASSED, COMPLETED, FAILED.
    """

    tests: List[Test]

    result: Optional[Literal["PASSED", "FAILED"]] = None
    """Result of the run (if completed)"""
