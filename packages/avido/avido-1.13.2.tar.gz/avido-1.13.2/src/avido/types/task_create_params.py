# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TaskCreateParams"]


class TaskCreateParams(TypedDict, total=False):
    application_id: Required[Annotated[str, PropertyInfo(alias="applicationId")]]
    """ID of the application this task belongs to"""

    description: Required[str]
    """A short description of the task"""

    title: Required[str]
    """The title of the task"""

    type: Required[Literal["ADVERSARY", "NORMAL"]]
    """The type of task"""

    topic_id: Annotated[Optional[str], PropertyInfo(alias="topicId")]
    """ID of the topic this task belongs to"""
