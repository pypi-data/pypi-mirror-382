# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .eval import Eval
from .._models import BaseModel

__all__ = ["EvalRetrieveResponse"]


class EvalRetrieveResponse(BaseModel):
    eval: Eval
    """Complete evaluation information"""
