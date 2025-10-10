# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

import httpx

from ..types import account_create_params, account_update_params, account_retrieve_status_params
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
from ..types.account import Account
from ..types.account_status import AccountStatus

__all__ = ["AccountsResource", "AsyncAccountsResource"]


class AccountsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return AccountsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        brand_name: Optional[str] | Omit = omit,
        organization: account_create_params.Organization | Omit = omit,
        time_zone: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """
        Creates a new Account within the calling Platform.

        Args:
          name: The name of the account that will be visible for your internal organizational
              purposes. This will also be the default public-facing brand name unless you also
              set a `brand_name`, but otherwise the account name will never be displayed
              anywhere outside of Surge HQ, and may include your ID for the account or
              anything else that may help you.

          brand_name: The name by which the people this account communicates with know it. If not
              provided, this will match the name field.

          organization: Parameters describing the legal entity on whose behalf the account will be
              operated.

          time_zone: This is the time zone in which the account is headquartered. This time zone may
              be used for compliance with TCPA restrictions on when messages may be sent.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/accounts",
            body=maybe_transform(
                {
                    "name": name,
                    "brand_name": brand_name,
                    "organization": organization,
                    "time_zone": time_zone,
                },
                account_create_params.AccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    def update(
        self,
        id: str,
        *,
        brand_name: str | Omit = omit,
        name: str | Omit = omit,
        organization: account_update_params.Organization | Omit = omit,
        time_zone: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """
        Updates an Account

        Args:
          id: The ID for the account to update.

          brand_name: The name by which the people this account communicates with know it. If not
              provided, this will match the name field.

          name: The name of the account that will be visible for your internal organizational
              purposes. This will also be the default public-facing brand name unless you also
              set a `brand_name`, but otherwise the account name will never be displayed
              anywhere outside of Surge HQ, and may include your ID for the account or
              anything else that may help you.

          organization: Parameters describing the legal entity on whose behalf the account will be
              operated.

          time_zone: The time zone for the account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/accounts/{id}",
            body=maybe_transform(
                {
                    "brand_name": brand_name,
                    "name": name,
                    "organization": organization,
                    "time_zone": time_zone,
                },
                account_update_params.AccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    def retrieve_status(
        self,
        account_id: str,
        *,
        capabilities: List[Literal["local_messaging"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountStatus:
        """
        Check an account's status and capabilities

        Args:
          account_id: ID of the account to check

          capabilities: capabilities about which to check the status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/accounts/{account_id}/status",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"capabilities": capabilities}, account_retrieve_status_params.AccountRetrieveStatusParams
                ),
            ),
            cast_to=AccountStatus,
        )


class AsyncAccountsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return AsyncAccountsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        brand_name: Optional[str] | Omit = omit,
        organization: account_create_params.Organization | Omit = omit,
        time_zone: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """
        Creates a new Account within the calling Platform.

        Args:
          name: The name of the account that will be visible for your internal organizational
              purposes. This will also be the default public-facing brand name unless you also
              set a `brand_name`, but otherwise the account name will never be displayed
              anywhere outside of Surge HQ, and may include your ID for the account or
              anything else that may help you.

          brand_name: The name by which the people this account communicates with know it. If not
              provided, this will match the name field.

          organization: Parameters describing the legal entity on whose behalf the account will be
              operated.

          time_zone: This is the time zone in which the account is headquartered. This time zone may
              be used for compliance with TCPA restrictions on when messages may be sent.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/accounts",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "brand_name": brand_name,
                    "organization": organization,
                    "time_zone": time_zone,
                },
                account_create_params.AccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    async def update(
        self,
        id: str,
        *,
        brand_name: str | Omit = omit,
        name: str | Omit = omit,
        organization: account_update_params.Organization | Omit = omit,
        time_zone: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """
        Updates an Account

        Args:
          id: The ID for the account to update.

          brand_name: The name by which the people this account communicates with know it. If not
              provided, this will match the name field.

          name: The name of the account that will be visible for your internal organizational
              purposes. This will also be the default public-facing brand name unless you also
              set a `brand_name`, but otherwise the account name will never be displayed
              anywhere outside of Surge HQ, and may include your ID for the account or
              anything else that may help you.

          organization: Parameters describing the legal entity on whose behalf the account will be
              operated.

          time_zone: The time zone for the account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/accounts/{id}",
            body=await async_maybe_transform(
                {
                    "brand_name": brand_name,
                    "name": name,
                    "organization": organization,
                    "time_zone": time_zone,
                },
                account_update_params.AccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    async def retrieve_status(
        self,
        account_id: str,
        *,
        capabilities: List[Literal["local_messaging"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountStatus:
        """
        Check an account's status and capabilities

        Args:
          account_id: ID of the account to check

          capabilities: capabilities about which to check the status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/accounts/{account_id}/status",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"capabilities": capabilities}, account_retrieve_status_params.AccountRetrieveStatusParams
                ),
            ),
            cast_to=AccountStatus,
        )


class AccountsResourceWithRawResponse:
    def __init__(self, accounts: AccountsResource) -> None:
        self._accounts = accounts

        self.create = to_raw_response_wrapper(
            accounts.create,
        )
        self.update = to_raw_response_wrapper(
            accounts.update,
        )
        self.retrieve_status = to_raw_response_wrapper(
            accounts.retrieve_status,
        )


class AsyncAccountsResourceWithRawResponse:
    def __init__(self, accounts: AsyncAccountsResource) -> None:
        self._accounts = accounts

        self.create = async_to_raw_response_wrapper(
            accounts.create,
        )
        self.update = async_to_raw_response_wrapper(
            accounts.update,
        )
        self.retrieve_status = async_to_raw_response_wrapper(
            accounts.retrieve_status,
        )


class AccountsResourceWithStreamingResponse:
    def __init__(self, accounts: AccountsResource) -> None:
        self._accounts = accounts

        self.create = to_streamed_response_wrapper(
            accounts.create,
        )
        self.update = to_streamed_response_wrapper(
            accounts.update,
        )
        self.retrieve_status = to_streamed_response_wrapper(
            accounts.retrieve_status,
        )


class AsyncAccountsResourceWithStreamingResponse:
    def __init__(self, accounts: AsyncAccountsResource) -> None:
        self._accounts = accounts

        self.create = async_to_streamed_response_wrapper(
            accounts.create,
        )
        self.update = async_to_streamed_response_wrapper(
            accounts.update,
        )
        self.retrieve_status = async_to_streamed_response_wrapper(
            accounts.retrieve_status,
        )
