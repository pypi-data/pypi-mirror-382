# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .contact import Contact
from .._models import BaseModel
from .phone_number import PhoneNumber

__all__ = ["MessageDeliveredWebhookEvent", "Data", "DataConversation", "DataAttachment"]


class DataConversation(BaseModel):
    id: str
    """The unique identifier for the conversation"""

    contact: Contact
    """A contact who has consented to receive messages"""

    phone_number: PhoneNumber
    """A phone number that can be used to send and receive messages and calls"""


class DataAttachment(BaseModel):
    id: str
    """The unique identifier for the attachment"""

    type: Literal["file", "image", "link", "video"]
    """The type of attachment"""

    url: str
    """The URL where the attachment can be downloaded"""


class Data(BaseModel):
    id: str
    """The unique identifier for the message"""

    body: str
    """The content of the message"""

    conversation: DataConversation
    """The conversation this message belongs to"""

    delivered_at: datetime
    """When the message was delivered"""

    attachments: Optional[List[DataAttachment]] = None
    """Attachments included with the message"""


class MessageDeliveredWebhookEvent(BaseModel):
    account_id: str
    """The ID of the account in which this event occurred"""

    data: Data
    """The data associated with the event"""

    timestamp: datetime
    """The timestamp when this event occurred, in ISO8601 format"""

    type: Literal["message.delivered"]
    """The type of the event. Always `message.delivered` for this event."""
