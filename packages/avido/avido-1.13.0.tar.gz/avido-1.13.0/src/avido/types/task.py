# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .application import Application

__all__ = ["Task", "Definition", "TaskSchedule"]


class Definition(BaseModel):
    id: str

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the eval definition was created"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the eval definition was last modified"""

    name: str

    type: Literal["NATURALNESS", "STYLE", "RECALL", "CUSTOM", "BLACKLIST", "FACT"]
    """Type of evaluation. Valid options: NATURALNESS, STYLE, RECALL, CUSTOM, FACT."""

    application: Optional[Application] = None
    """Application configuration and metadata"""

    global_config: Optional[object] = FieldInfo(alias="globalConfig", default=None)

    style_guide_id: Optional[str] = FieldInfo(alias="styleGuideId", default=None)


class TaskSchedule(BaseModel):
    criticality: Literal["LOW", "MEDIUM", "HIGH"]

    cron: str

    last_run_at: Optional[datetime] = FieldInfo(alias="lastRunAt", default=None)

    next_run_at: Optional[datetime] = FieldInfo(alias="nextRunAt", default=None)


class Task(BaseModel):
    id: str
    """The unique identifier of the task"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the task was created"""

    definitions: List[Definition]

    description: str
    """The task description"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the task was last modified"""

    title: str
    """The title of the task"""

    type: Literal["ADVERSARY", "NORMAL"]
    """The type of task.

    Normal tasks have a dynamic user prompt, while adversarial tasks have a fixed
    user prompt.
    """

    input_examples: Optional[List[str]] = FieldInfo(alias="inputExamples", default=None)
    """Example inputs for the task"""

    last_test: Optional[datetime] = FieldInfo(alias="lastTest", default=None)
    """The date and time this task was last tested"""

    pass_rate: Optional[float] = FieldInfo(alias="passRate", default=None)
    """The 30 day pass rate for the task measured in percentage"""

    task_schedule: Optional[TaskSchedule] = FieldInfo(alias="taskSchedule", default=None)

    topic_id: Optional[str] = FieldInfo(alias="topicId", default=None)
    """The ID of the topic this task belongs to"""
