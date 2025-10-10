# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["Error"]


class Error(BaseModel):
    message: str
    """A human-readable error message."""

    type: str
    """A unique error code."""

    detail: Optional[Dict[str, object]] = None
    """Additional details about the error."""
