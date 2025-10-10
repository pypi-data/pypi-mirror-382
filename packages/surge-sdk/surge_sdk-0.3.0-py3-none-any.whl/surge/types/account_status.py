# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["AccountStatus", "Capabilities", "CapabilitiesError"]


class CapabilitiesError(BaseModel):
    field: str
    """
    A dot-delimited string representing the field that has an error, as in
    `organization.contact.phone_number`.
    """

    message: str
    """A human-readable string explaining the error."""

    type: str
    """A slug for the error type"""


class Capabilities(BaseModel):
    errors: List[CapabilitiesError]
    """
    A list of errors that will need corrected before capability is available to
    account.
    """

    fields_needed: List[str]
    """A list of missing fields that are required for the capability.

    Nested field names are dot-delimited, as in `organization.address.region`.
    """

    status: Literal["error", "incomplete", "ready"]
    """
    Whether the account is ready for the capability, has errors that need corrected,
    or is incomplete and requires missing data. If account has both missing and
    invalid fields, `error` will be preferred over `incomplete`.
    """


class AccountStatus(BaseModel):
    capabilities: Dict[str, Capabilities]
    """
    An object where the fields are the capabilities passed in the `capabilities`
    query param, as in `local_messaging`.
    """
