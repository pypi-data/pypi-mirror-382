# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ApplicationCreateParams"]


class ApplicationCreateParams(TypedDict, total=False):
    context: Required[str]
    """Context/instructions for the application"""

    description: Required[str]
    """Description of the application"""

    environment: Required[Literal["DEV", "PROD"]]
    """Environment of the application"""

    slug: Required[str]
    """URL-friendly slug for the application"""

    title: Required[str]
    """Title of the application"""

    type: Required[Literal["CHATBOT", "AGENT"]]
    """Type of the application"""
