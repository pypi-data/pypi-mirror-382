# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["Blast", "Attachment"]


class Attachment(BaseModel):
    url: Optional[str] = None
    """The URL of the attachment."""


class Blast(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the object."""

    attachments: Optional[List[Attachment]] = None

    body: Optional[str] = None
    """The message body."""

    name: Optional[str] = None
    """Optional name for the blast."""

    send_at: Optional[datetime] = None
    """When the blast will be or was sent."""
