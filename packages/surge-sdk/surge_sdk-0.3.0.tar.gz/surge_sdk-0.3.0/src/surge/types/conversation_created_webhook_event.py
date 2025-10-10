# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from .contact import Contact
from .._models import BaseModel
from .phone_number import PhoneNumber

__all__ = ["ConversationCreatedWebhookEvent", "Data"]


class Data(BaseModel):
    id: str
    """The unique identifier for the conversation"""

    contact: Contact
    """A contact who has consented to receive messages"""

    phone_number: PhoneNumber
    """A phone number that can be used to send and receive messages and calls"""


class ConversationCreatedWebhookEvent(BaseModel):
    account_id: str
    """The ID of the account in which this event occurred"""

    data: Data
    """The data associated with the event"""

    timestamp: datetime
    """The timestamp when this event occurred, in ISO8601 format"""

    type: Literal["conversation.created"]
    """The type of the event. Always `conversation.created` for this event."""
