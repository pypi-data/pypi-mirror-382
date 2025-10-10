# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["UserCreateTokenParams"]


class UserCreateTokenParams(TypedDict, total=False):
    duration_seconds: int
    """For how many seconds the token should be accepted. Defaults to 15 minutes."""
