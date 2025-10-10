# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .verification import Verification

__all__ = ["VerificationCheck"]


class VerificationCheck(BaseModel):
    result: Optional[Literal["ok", "incorrect", "exhausted", "expired", "already_verified"]] = None
    """The result of the code check."""

    verification: Optional[Verification] = None
    """A phone number verification"""
