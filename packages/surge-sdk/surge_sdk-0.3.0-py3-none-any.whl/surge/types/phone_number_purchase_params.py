# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["PhoneNumberPurchaseParams"]


class PhoneNumberPurchaseParams(TypedDict, total=False):
    area_code: str
    """The desired area code for this phone number.

    If provided without type, the type will be inferred.
    """

    latitude: float
    """Latitude to search for nearby phone numbers.

    Must be used with longitude. If provided without type, type will be inferred as
    'local'.
    """

    longitude: float
    """Longitude to search for nearby phone numbers.

    Must be used with latitude. If provided without type, type will be inferred as
    'local'.
    """

    type: Literal["local", "toll_free"]
    """Whether the phone number is local or toll-free.

    Can be omitted if area_code or latitude/longitude are provided.
    """
