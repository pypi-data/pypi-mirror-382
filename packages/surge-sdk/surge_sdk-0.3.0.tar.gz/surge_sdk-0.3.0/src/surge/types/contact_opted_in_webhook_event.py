# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ContactOptedInWebhookEvent", "Data"]


class Data(BaseModel):
    id: str
    """The unique identifier for the contact"""


class ContactOptedInWebhookEvent(BaseModel):
    account_id: str
    """The ID of the account in which this event occurred"""

    data: Data
    """The data associated with the event"""

    timestamp: datetime
    """The timestamp when this event occurred, in ISO8601 format"""

    type: Literal["contact.opted_in"]
    """The type of the event. Always `contact.opted_in` for this event."""
