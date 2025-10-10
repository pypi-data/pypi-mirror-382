# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Verification"]


class Verification(BaseModel):
    id: str
    """Unique identifier for the object."""

    attempt_count: int
    """The number of times the code has been attempted."""

    phone_number: str
    """The phone number being verified. In E.164 format."""

    status: Literal["pending", "verified", "exhausted", "expired"]
    """The current status of the verification."""
