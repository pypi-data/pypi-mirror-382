# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import phone_number_purchase_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.phone_number import PhoneNumber

__all__ = ["PhoneNumbersResource", "AsyncPhoneNumbersResource"]


class PhoneNumbersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PhoneNumbersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return PhoneNumbersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PhoneNumbersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return PhoneNumbersResourceWithStreamingResponse(self)

    def purchase(
        self,
        account_id: str,
        *,
        area_code: str | Omit = omit,
        latitude: float | Omit = omit,
        longitude: float | Omit = omit,
        type: Literal["local", "toll_free"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PhoneNumber:
        """Purchase a new phone number for the account.

        You can specify search criteria or
        let the system select a random number.

        Args:
          account_id: The account for which the phone number should be created.

          area_code: The desired area code for this phone number. If provided without type, the type
              will be inferred.

          latitude: Latitude to search for nearby phone numbers. Must be used with longitude. If
              provided without type, type will be inferred as 'local'.

          longitude: Longitude to search for nearby phone numbers. Must be used with latitude. If
              provided without type, type will be inferred as 'local'.

          type: Whether the phone number is local or toll-free. Can be omitted if area_code or
              latitude/longitude are provided.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/accounts/{account_id}/phone_numbers",
            body=maybe_transform(
                {
                    "area_code": area_code,
                    "latitude": latitude,
                    "longitude": longitude,
                    "type": type,
                },
                phone_number_purchase_params.PhoneNumberPurchaseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PhoneNumber,
        )


class AsyncPhoneNumbersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPhoneNumbersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPhoneNumbersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPhoneNumbersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return AsyncPhoneNumbersResourceWithStreamingResponse(self)

    async def purchase(
        self,
        account_id: str,
        *,
        area_code: str | Omit = omit,
        latitude: float | Omit = omit,
        longitude: float | Omit = omit,
        type: Literal["local", "toll_free"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PhoneNumber:
        """Purchase a new phone number for the account.

        You can specify search criteria or
        let the system select a random number.

        Args:
          account_id: The account for which the phone number should be created.

          area_code: The desired area code for this phone number. If provided without type, the type
              will be inferred.

          latitude: Latitude to search for nearby phone numbers. Must be used with longitude. If
              provided without type, type will be inferred as 'local'.

          longitude: Longitude to search for nearby phone numbers. Must be used with latitude. If
              provided without type, type will be inferred as 'local'.

          type: Whether the phone number is local or toll-free. Can be omitted if area_code or
              latitude/longitude are provided.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/accounts/{account_id}/phone_numbers",
            body=await async_maybe_transform(
                {
                    "area_code": area_code,
                    "latitude": latitude,
                    "longitude": longitude,
                    "type": type,
                },
                phone_number_purchase_params.PhoneNumberPurchaseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PhoneNumber,
        )


class PhoneNumbersResourceWithRawResponse:
    def __init__(self, phone_numbers: PhoneNumbersResource) -> None:
        self._phone_numbers = phone_numbers

        self.purchase = to_raw_response_wrapper(
            phone_numbers.purchase,
        )


class AsyncPhoneNumbersResourceWithRawResponse:
    def __init__(self, phone_numbers: AsyncPhoneNumbersResource) -> None:
        self._phone_numbers = phone_numbers

        self.purchase = async_to_raw_response_wrapper(
            phone_numbers.purchase,
        )


class PhoneNumbersResourceWithStreamingResponse:
    def __init__(self, phone_numbers: PhoneNumbersResource) -> None:
        self._phone_numbers = phone_numbers

        self.purchase = to_streamed_response_wrapper(
            phone_numbers.purchase,
        )


class AsyncPhoneNumbersResourceWithStreamingResponse:
    def __init__(self, phone_numbers: AsyncPhoneNumbersResource) -> None:
        self._phone_numbers = phone_numbers

        self.purchase = async_to_streamed_response_wrapper(
            phone_numbers.purchase,
        )
