# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["ContactCreateParams"]


class ContactCreateParams(TypedDict, total=False):
    phone_number: Required[str]
    """The contact's phone number in E.164 format."""

    email: str
    """The contact's email address."""

    first_name: str
    """The contact's first name."""

    last_name: str
    """The contact's last name."""

    metadata: Dict[str, str]
    """Set of key-value pairs that will be stored with the object."""
