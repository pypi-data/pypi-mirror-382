# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    first_name: Required[str]
    """The user's first name."""

    last_name: str
    """The user's last name."""

    metadata: Dict[str, str]
    """Set of key-value pairs that will be stored with the object."""

    photo_url: str
    """URL of a photo to be used as the user's avatar."""
