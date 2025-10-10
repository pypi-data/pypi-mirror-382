# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import users, blasts, accounts, contacts, messages, webhooks, campaigns, phone_numbers, verifications
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import SurgeError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Surge", "AsyncSurge", "Client", "AsyncClient"]


class Surge(SyncAPIClient):
    accounts: accounts.AccountsResource
    blasts: blasts.BlastsResource
    campaigns: campaigns.CampaignsResource
    contacts: contacts.ContactsResource
    messages: messages.MessagesResource
    phone_numbers: phone_numbers.PhoneNumbersResource
    users: users.UsersResource
    verifications: verifications.VerificationsResource
    webhooks: webhooks.WebhooksResource
    with_raw_response: SurgeWithRawResponse
    with_streaming_response: SurgeWithStreamedResponse

    # client options
    api_key: str
    webhook_signing_secret: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        webhook_signing_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Surge client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `SURGE_API_KEY`
        - `webhook_signing_secret` from `SURGE_WEBHOOK_SIGNING_SECRET`
        """
        if api_key is None:
            api_key = os.environ.get("SURGE_API_KEY")
        if api_key is None:
            raise SurgeError(
                "The api_key client option must be set either by passing api_key to the client or by setting the SURGE_API_KEY environment variable"
            )
        self.api_key = api_key

        if webhook_signing_secret is None:
            webhook_signing_secret = os.environ.get("SURGE_WEBHOOK_SIGNING_SECRET")
        self.webhook_signing_secret = webhook_signing_secret

        if base_url is None:
            base_url = os.environ.get("SURGE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.surge.app"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.accounts = accounts.AccountsResource(self)
        self.blasts = blasts.BlastsResource(self)
        self.campaigns = campaigns.CampaignsResource(self)
        self.contacts = contacts.ContactsResource(self)
        self.messages = messages.MessagesResource(self)
        self.phone_numbers = phone_numbers.PhoneNumbersResource(self)
        self.users = users.UsersResource(self)
        self.verifications = verifications.VerificationsResource(self)
        self.webhooks = webhooks.WebhooksResource(self)
        self.with_raw_response = SurgeWithRawResponse(self)
        self.with_streaming_response = SurgeWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        webhook_signing_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            webhook_signing_secret=webhook_signing_secret or self.webhook_signing_secret,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncSurge(AsyncAPIClient):
    accounts: accounts.AsyncAccountsResource
    blasts: blasts.AsyncBlastsResource
    campaigns: campaigns.AsyncCampaignsResource
    contacts: contacts.AsyncContactsResource
    messages: messages.AsyncMessagesResource
    phone_numbers: phone_numbers.AsyncPhoneNumbersResource
    users: users.AsyncUsersResource
    verifications: verifications.AsyncVerificationsResource
    webhooks: webhooks.AsyncWebhooksResource
    with_raw_response: AsyncSurgeWithRawResponse
    with_streaming_response: AsyncSurgeWithStreamedResponse

    # client options
    api_key: str
    webhook_signing_secret: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        webhook_signing_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncSurge client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `SURGE_API_KEY`
        - `webhook_signing_secret` from `SURGE_WEBHOOK_SIGNING_SECRET`
        """
        if api_key is None:
            api_key = os.environ.get("SURGE_API_KEY")
        if api_key is None:
            raise SurgeError(
                "The api_key client option must be set either by passing api_key to the client or by setting the SURGE_API_KEY environment variable"
            )
        self.api_key = api_key

        if webhook_signing_secret is None:
            webhook_signing_secret = os.environ.get("SURGE_WEBHOOK_SIGNING_SECRET")
        self.webhook_signing_secret = webhook_signing_secret

        if base_url is None:
            base_url = os.environ.get("SURGE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.surge.app"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.accounts = accounts.AsyncAccountsResource(self)
        self.blasts = blasts.AsyncBlastsResource(self)
        self.campaigns = campaigns.AsyncCampaignsResource(self)
        self.contacts = contacts.AsyncContactsResource(self)
        self.messages = messages.AsyncMessagesResource(self)
        self.phone_numbers = phone_numbers.AsyncPhoneNumbersResource(self)
        self.users = users.AsyncUsersResource(self)
        self.verifications = verifications.AsyncVerificationsResource(self)
        self.webhooks = webhooks.AsyncWebhooksResource(self)
        self.with_raw_response = AsyncSurgeWithRawResponse(self)
        self.with_streaming_response = AsyncSurgeWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        webhook_signing_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            webhook_signing_secret=webhook_signing_secret or self.webhook_signing_secret,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class SurgeWithRawResponse:
    def __init__(self, client: Surge) -> None:
        self.accounts = accounts.AccountsResourceWithRawResponse(client.accounts)
        self.blasts = blasts.BlastsResourceWithRawResponse(client.blasts)
        self.campaigns = campaigns.CampaignsResourceWithRawResponse(client.campaigns)
        self.contacts = contacts.ContactsResourceWithRawResponse(client.contacts)
        self.messages = messages.MessagesResourceWithRawResponse(client.messages)
        self.phone_numbers = phone_numbers.PhoneNumbersResourceWithRawResponse(client.phone_numbers)
        self.users = users.UsersResourceWithRawResponse(client.users)
        self.verifications = verifications.VerificationsResourceWithRawResponse(client.verifications)


class AsyncSurgeWithRawResponse:
    def __init__(self, client: AsyncSurge) -> None:
        self.accounts = accounts.AsyncAccountsResourceWithRawResponse(client.accounts)
        self.blasts = blasts.AsyncBlastsResourceWithRawResponse(client.blasts)
        self.campaigns = campaigns.AsyncCampaignsResourceWithRawResponse(client.campaigns)
        self.contacts = contacts.AsyncContactsResourceWithRawResponse(client.contacts)
        self.messages = messages.AsyncMessagesResourceWithRawResponse(client.messages)
        self.phone_numbers = phone_numbers.AsyncPhoneNumbersResourceWithRawResponse(client.phone_numbers)
        self.users = users.AsyncUsersResourceWithRawResponse(client.users)
        self.verifications = verifications.AsyncVerificationsResourceWithRawResponse(client.verifications)


class SurgeWithStreamedResponse:
    def __init__(self, client: Surge) -> None:
        self.accounts = accounts.AccountsResourceWithStreamingResponse(client.accounts)
        self.blasts = blasts.BlastsResourceWithStreamingResponse(client.blasts)
        self.campaigns = campaigns.CampaignsResourceWithStreamingResponse(client.campaigns)
        self.contacts = contacts.ContactsResourceWithStreamingResponse(client.contacts)
        self.messages = messages.MessagesResourceWithStreamingResponse(client.messages)
        self.phone_numbers = phone_numbers.PhoneNumbersResourceWithStreamingResponse(client.phone_numbers)
        self.users = users.UsersResourceWithStreamingResponse(client.users)
        self.verifications = verifications.VerificationsResourceWithStreamingResponse(client.verifications)


class AsyncSurgeWithStreamedResponse:
    def __init__(self, client: AsyncSurge) -> None:
        self.accounts = accounts.AsyncAccountsResourceWithStreamingResponse(client.accounts)
        self.blasts = blasts.AsyncBlastsResourceWithStreamingResponse(client.blasts)
        self.campaigns = campaigns.AsyncCampaignsResourceWithStreamingResponse(client.campaigns)
        self.contacts = contacts.AsyncContactsResourceWithStreamingResponse(client.contacts)
        self.messages = messages.AsyncMessagesResourceWithStreamingResponse(client.messages)
        self.phone_numbers = phone_numbers.AsyncPhoneNumbersResourceWithStreamingResponse(client.phone_numbers)
        self.users = users.AsyncUsersResourceWithStreamingResponse(client.users)
        self.verifications = verifications.AsyncVerificationsResourceWithStreamingResponse(client.verifications)


Client = Surge

AsyncClient = AsyncSurge
