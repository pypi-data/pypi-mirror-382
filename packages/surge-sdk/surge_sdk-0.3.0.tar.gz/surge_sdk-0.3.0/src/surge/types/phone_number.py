# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["PhoneNumber"]


class PhoneNumber(BaseModel):
    id: str
    """Unique identifier for the phone number"""

    number: str
    """The phone number in E.164 format"""

    type: Literal["local", "toll_free"]
    """Whether the phone number is local, toll-free, or short code"""
