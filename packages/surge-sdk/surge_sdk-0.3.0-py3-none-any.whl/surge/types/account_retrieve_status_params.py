# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["AccountRetrieveStatusParams"]


class AccountRetrieveStatusParams(TypedDict, total=False):
    capabilities: List[Literal["local_messaging"]]
    """capabilities about which to check the status"""
