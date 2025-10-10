# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["BlastCreateParams", "Attachment"]


class BlastCreateParams(TypedDict, total=False):
    attachments: Iterable[Attachment]

    body: str
    """The message body."""

    contacts: SequenceNotStr[str]
    """Deprecated. Use `to` instead."""

    name: str
    """Optional name for the blast."""

    segments: SequenceNotStr[str]
    """Deprecated. Use `to` instead."""

    send_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """When to send the blast. If not provided, sends immediately."""

    to: SequenceNotStr[str]
    """List of recipients to whom the blast should be sent.

    This can be a combination of contact IDs, segment IDs, and phone numbers.
    """


class Attachment(TypedDict, total=False):
    url: Required[str]
    """The URL of the attachment."""
