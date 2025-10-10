# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .contact import Contact
from .._models import BaseModel

__all__ = ["Message", "Attachment", "Conversation", "ConversationPhoneNumber"]


class Attachment(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the object."""

    type: Optional[str] = None
    """The type of attachment."""

    url: Optional[str] = None
    """The URL of the attachment."""


class ConversationPhoneNumber(BaseModel):
    id: str
    """Unique identifier for the phone number"""

    number: str
    """The canonical format of the phone number."""

    type: Literal["local", "toll_free", "short_code", "demo"]
    """Whether the phone number is local, toll-free, or short code"""


class Conversation(BaseModel):
    id: str
    """Unique identifier for the object."""

    contact: Contact
    """A contact who has consented to receive messages"""

    phone_number: Optional[ConversationPhoneNumber] = None
    """This is the phone number tied to the Surge account."""


class Message(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the object."""

    attachments: Optional[List[Attachment]] = None

    body: Optional[str] = None
    """The message body."""

    conversation: Optional[Conversation] = None
    """A conversation with a Contact"""
