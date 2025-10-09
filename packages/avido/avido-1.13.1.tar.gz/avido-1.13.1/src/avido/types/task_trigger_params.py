# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TaskTriggerParams"]


class TaskTriggerParams(TypedDict, total=False):
    task_id: Required[Annotated[str, PropertyInfo(alias="taskId")]]
    """ID of the task to run"""
