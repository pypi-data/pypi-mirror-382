# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["StyleGuideCreateParams"]


class StyleGuideCreateParams(TypedDict, total=False):
    application_id: Required[Annotated[str, PropertyInfo(alias="applicationId")]]
    """ID of the application this style guide belongs to"""

    content: Required[Dict[str, object]]
    """The JSON content of the style guide"""
