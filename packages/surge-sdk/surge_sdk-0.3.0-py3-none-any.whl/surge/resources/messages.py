# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import overload

import httpx

from ..types import message_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import required_args, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.message import Message

__all__ = ["MessagesResource", "AsyncMessagesResource"]


class MessagesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return MessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return MessagesResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        account_id: str,
        *,
        conversation: message_create_params.MessageParamsWithConversationConversation,
        attachments: Iterable[message_create_params.MessageParamsWithConversationAttachment] | Omit = omit,
        body: str | Omit = omit,
        send_at: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Message:
        """
        Creates and enqueues a new message to be sent.

        Messages are always sent asynchronously. When you hit this endpoint, the message
        will be created within Surge's system and enqueued for sending, and then the id
        for the new message will be returned. When the message is actually sent, a
        `message.sent` webhook event will be triggered and sent to any webhook endpoints
        that you have subscribed to this event type. Then a `message.delivered` webhook
        event will be triggered when the carrier sends us a delivery receipt.

        By default all messages will be sent immediately. If you would like to schedule
        sending for some time up to 60 days in the future, you can do that by providing
        a value for the `send_at` field. This should be formatted as an ISO8601 datetime
        like `2028-10-14T18:06:00Z`.

        You must include either a `body` or `attachments` field (or both) in the request
        body. The `body` field should contain the text of the message you want to send,
        and the `attachments` field should be an array of objects with a `url` field
        pointing to the file you want to attach. Surge will download these files and
        send them as attachments in the message.

        You can provide either a `conversation` object or a `to` field to specify the
        intended recipient of the message, but an error will be returned if both fields
        are provided. Similarly the `from` field cannot be used together with the
        `conversation` field, and `conversation.phone_number` should be specified
        instead.

        Args:
          account_id: The account from which the message should be sent.

          conversation: Params for selecting or creating a new conversation. Either the id or the
              Contact must be given.

          body: The message body.

          send_at: An optional datetime for scheduling message up to a couple of months in the
              future.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        account_id: str,
        *,
        to: str,
        attachments: Iterable[message_create_params.SimpleMessageParamsAttachment] | Omit = omit,
        body: str | Omit = omit,
        from_: str | Omit = omit,
        send_at: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Message:
        """
        Creates and enqueues a new message to be sent.

        Messages are always sent asynchronously. When you hit this endpoint, the message
        will be created within Surge's system and enqueued for sending, and then the id
        for the new message will be returned. When the message is actually sent, a
        `message.sent` webhook event will be triggered and sent to any webhook endpoints
        that you have subscribed to this event type. Then a `message.delivered` webhook
        event will be triggered when the carrier sends us a delivery receipt.

        By default all messages will be sent immediately. If you would like to schedule
        sending for some time up to 60 days in the future, you can do that by providing
        a value for the `send_at` field. This should be formatted as an ISO8601 datetime
        like `2028-10-14T18:06:00Z`.

        You must include either a `body` or `attachments` field (or both) in the request
        body. The `body` field should contain the text of the message you want to send,
        and the `attachments` field should be an array of objects with a `url` field
        pointing to the file you want to attach. Surge will download these files and
        send them as attachments in the message.

        You can provide either a `conversation` object or a `to` field to specify the
        intended recipient of the message, but an error will be returned if both fields
        are provided. Similarly the `from` field cannot be used together with the
        `conversation` field, and `conversation.phone_number` should be specified
        instead.

        Args:
          account_id: The account from which the message should be sent.

          to: The recipient's phone number in E.164 format. Cannot be used together with
              'conversation'.

          body: The message body.

          from_: The sender's phone number in E.164 format or phone number ID. If omitted, uses
              the account's default phone number. Cannot be used together with 'conversation'.

          send_at: An optional datetime for scheduling message up to a couple of months in the
              future.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["conversation"], ["to"])
    def create(
        self,
        account_id: str,
        *,
        conversation: message_create_params.MessageParamsWithConversationConversation | Omit = omit,
        attachments: Iterable[message_create_params.MessageParamsWithConversationAttachment]
        | Iterable[message_create_params.SimpleMessageParamsAttachment]
        | Omit = omit,
        body: str | Omit = omit,
        send_at: Union[str, datetime] | Omit = omit,
        to: str | Omit = omit,
        from_: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Message:
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/accounts/{account_id}/messages",
            body=maybe_transform(
                {
                    "conversation": conversation,
                    "attachments": attachments,
                    "body": body,
                    "send_at": send_at,
                    "to": to,
                    "from_": from_,
                },
                message_create_params.MessageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Message,
        )


class AsyncMessagesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return AsyncMessagesResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        account_id: str,
        *,
        conversation: message_create_params.MessageParamsWithConversationConversation,
        attachments: Iterable[message_create_params.MessageParamsWithConversationAttachment] | Omit = omit,
        body: str | Omit = omit,
        send_at: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Message:
        """
        Creates and enqueues a new message to be sent.

        Messages are always sent asynchronously. When you hit this endpoint, the message
        will be created within Surge's system and enqueued for sending, and then the id
        for the new message will be returned. When the message is actually sent, a
        `message.sent` webhook event will be triggered and sent to any webhook endpoints
        that you have subscribed to this event type. Then a `message.delivered` webhook
        event will be triggered when the carrier sends us a delivery receipt.

        By default all messages will be sent immediately. If you would like to schedule
        sending for some time up to 60 days in the future, you can do that by providing
        a value for the `send_at` field. This should be formatted as an ISO8601 datetime
        like `2028-10-14T18:06:00Z`.

        You must include either a `body` or `attachments` field (or both) in the request
        body. The `body` field should contain the text of the message you want to send,
        and the `attachments` field should be an array of objects with a `url` field
        pointing to the file you want to attach. Surge will download these files and
        send them as attachments in the message.

        You can provide either a `conversation` object or a `to` field to specify the
        intended recipient of the message, but an error will be returned if both fields
        are provided. Similarly the `from` field cannot be used together with the
        `conversation` field, and `conversation.phone_number` should be specified
        instead.

        Args:
          account_id: The account from which the message should be sent.

          conversation: Params for selecting or creating a new conversation. Either the id or the
              Contact must be given.

          body: The message body.

          send_at: An optional datetime for scheduling message up to a couple of months in the
              future.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        account_id: str,
        *,
        to: str,
        attachments: Iterable[message_create_params.SimpleMessageParamsAttachment] | Omit = omit,
        body: str | Omit = omit,
        from_: str | Omit = omit,
        send_at: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Message:
        """
        Creates and enqueues a new message to be sent.

        Messages are always sent asynchronously. When you hit this endpoint, the message
        will be created within Surge's system and enqueued for sending, and then the id
        for the new message will be returned. When the message is actually sent, a
        `message.sent` webhook event will be triggered and sent to any webhook endpoints
        that you have subscribed to this event type. Then a `message.delivered` webhook
        event will be triggered when the carrier sends us a delivery receipt.

        By default all messages will be sent immediately. If you would like to schedule
        sending for some time up to 60 days in the future, you can do that by providing
        a value for the `send_at` field. This should be formatted as an ISO8601 datetime
        like `2028-10-14T18:06:00Z`.

        You must include either a `body` or `attachments` field (or both) in the request
        body. The `body` field should contain the text of the message you want to send,
        and the `attachments` field should be an array of objects with a `url` field
        pointing to the file you want to attach. Surge will download these files and
        send them as attachments in the message.

        You can provide either a `conversation` object or a `to` field to specify the
        intended recipient of the message, but an error will be returned if both fields
        are provided. Similarly the `from` field cannot be used together with the
        `conversation` field, and `conversation.phone_number` should be specified
        instead.

        Args:
          account_id: The account from which the message should be sent.

          to: The recipient's phone number in E.164 format. Cannot be used together with
              'conversation'.

          body: The message body.

          from_: The sender's phone number in E.164 format or phone number ID. If omitted, uses
              the account's default phone number. Cannot be used together with 'conversation'.

          send_at: An optional datetime for scheduling message up to a couple of months in the
              future.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["conversation"], ["to"])
    async def create(
        self,
        account_id: str,
        *,
        conversation: message_create_params.MessageParamsWithConversationConversation | Omit = omit,
        attachments: Iterable[message_create_params.MessageParamsWithConversationAttachment]
        | Iterable[message_create_params.SimpleMessageParamsAttachment]
        | Omit = omit,
        body: str | Omit = omit,
        send_at: Union[str, datetime] | Omit = omit,
        to: str | Omit = omit,
        from_: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Message:
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/accounts/{account_id}/messages",
            body=await async_maybe_transform(
                {
                    "conversation": conversation,
                    "attachments": attachments,
                    "body": body,
                    "send_at": send_at,
                    "to": to,
                    "from_": from_,
                },
                message_create_params.MessageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Message,
        )


class MessagesResourceWithRawResponse:
    def __init__(self, messages: MessagesResource) -> None:
        self._messages = messages

        self.create = to_raw_response_wrapper(
            messages.create,
        )


class AsyncMessagesResourceWithRawResponse:
    def __init__(self, messages: AsyncMessagesResource) -> None:
        self._messages = messages

        self.create = async_to_raw_response_wrapper(
            messages.create,
        )


class MessagesResourceWithStreamingResponse:
    def __init__(self, messages: MessagesResource) -> None:
        self._messages = messages

        self.create = to_streamed_response_wrapper(
            messages.create,
        )


class AsyncMessagesResourceWithStreamingResponse:
    def __init__(self, messages: AsyncMessagesResource) -> None:
        self._messages = messages

        self.create = async_to_streamed_response_wrapper(
            messages.create,
        )
