# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .style_guide import StyleGuide

__all__ = ["StyleGuideResponse"]


class StyleGuideResponse(BaseModel):
    style_guide: StyleGuide = FieldInfo(alias="styleGuide")
    """A style guide for a specific application"""
