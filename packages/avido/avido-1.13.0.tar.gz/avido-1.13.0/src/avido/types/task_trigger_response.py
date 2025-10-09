# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["TaskTriggerResponse"]


class TaskTriggerResponse(BaseModel):
    success: bool
    """Whether the task was triggered successfully"""
