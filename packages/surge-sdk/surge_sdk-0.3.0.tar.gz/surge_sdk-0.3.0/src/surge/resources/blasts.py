# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime

import httpx

from ..types import blast_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..types.blast import Blast
from .._base_client import make_request_options

__all__ = ["BlastsResource", "AsyncBlastsResource"]


class BlastsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BlastsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return BlastsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BlastsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return BlastsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        attachments: Iterable[blast_create_params.Attachment] | Omit = omit,
        body: str | Omit = omit,
        contacts: SequenceNotStr[str] | Omit = omit,
        name: str | Omit = omit,
        segments: SequenceNotStr[str] | Omit = omit,
        send_at: Union[str, datetime] | Omit = omit,
        to: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Blast:
        """
        Sends a Blast.

        Args:
          account_id: The account for which the blast should be sent.

          body: The message body.

          contacts: Deprecated. Use `to` instead.

          name: Optional name for the blast.

          segments: Deprecated. Use `to` instead.

          send_at: When to send the blast. If not provided, sends immediately.

          to: List of recipients to whom the blast should be sent. This can be a combination
              of contact IDs, segment IDs, and phone numbers.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/accounts/{account_id}/blasts",
            body=maybe_transform(
                {
                    "attachments": attachments,
                    "body": body,
                    "contacts": contacts,
                    "name": name,
                    "segments": segments,
                    "send_at": send_at,
                    "to": to,
                },
                blast_create_params.BlastCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Blast,
        )


class AsyncBlastsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBlastsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncBlastsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBlastsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return AsyncBlastsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        attachments: Iterable[blast_create_params.Attachment] | Omit = omit,
        body: str | Omit = omit,
        contacts: SequenceNotStr[str] | Omit = omit,
        name: str | Omit = omit,
        segments: SequenceNotStr[str] | Omit = omit,
        send_at: Union[str, datetime] | Omit = omit,
        to: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Blast:
        """
        Sends a Blast.

        Args:
          account_id: The account for which the blast should be sent.

          body: The message body.

          contacts: Deprecated. Use `to` instead.

          name: Optional name for the blast.

          segments: Deprecated. Use `to` instead.

          send_at: When to send the blast. If not provided, sends immediately.

          to: List of recipients to whom the blast should be sent. This can be a combination
              of contact IDs, segment IDs, and phone numbers.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/accounts/{account_id}/blasts",
            body=await async_maybe_transform(
                {
                    "attachments": attachments,
                    "body": body,
                    "contacts": contacts,
                    "name": name,
                    "segments": segments,
                    "send_at": send_at,
                    "to": to,
                },
                blast_create_params.BlastCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Blast,
        )


class BlastsResourceWithRawResponse:
    def __init__(self, blasts: BlastsResource) -> None:
        self._blasts = blasts

        self.create = to_raw_response_wrapper(
            blasts.create,
        )


class AsyncBlastsResourceWithRawResponse:
    def __init__(self, blasts: AsyncBlastsResource) -> None:
        self._blasts = blasts

        self.create = async_to_raw_response_wrapper(
            blasts.create,
        )


class BlastsResourceWithStreamingResponse:
    def __init__(self, blasts: BlastsResource) -> None:
        self._blasts = blasts

        self.create = to_streamed_response_wrapper(
            blasts.create,
        )


class AsyncBlastsResourceWithStreamingResponse:
    def __init__(self, blasts: AsyncBlastsResource) -> None:
        self._blasts = blasts

        self.create = async_to_streamed_response_wrapper(
            blasts.create,
        )
