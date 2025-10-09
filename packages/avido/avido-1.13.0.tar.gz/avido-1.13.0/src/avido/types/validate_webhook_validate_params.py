# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["ValidateWebhookValidateParams"]


class ValidateWebhookValidateParams(TypedDict, total=False):
    body: Required[Dict[str, object]]
    """The actual payload being sent by the external webhook."""

    signature: Required[str]
    """HMAC signature for the request body."""

    timestamp: Required[float]
    """Timestamp (in milliseconds) for the request."""
