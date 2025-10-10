# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import campaign_create_params
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
from .._base_client import make_request_options
from ..types.campaign import Campaign

__all__ = ["CampaignsResource", "AsyncCampaignsResource"]


class CampaignsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CampaignsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return CampaignsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CampaignsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return CampaignsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        consent_flow: str,
        description: str,
        message_samples: SequenceNotStr[str],
        privacy_policy_url: str,
        use_cases: List[
            Literal[
                "account_notification",
                "customer_care",
                "delivery_notification",
                "fraud_alert",
                "higher_education",
                "marketing",
                "polling_voting",
                "public_service_announcement",
                "security_alert",
                "two_factor_authentication",
            ]
        ],
        volume: Literal["high", "low"],
        includes: List[Literal["links", "phone_numbers", "age_gated", "direct_lending"]] | Omit = omit,
        link_sample: str | Omit = omit,
        terms_and_conditions_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Campaign:
        """
        Creates a campaign to register account to send text messages.

        Args:
          account_id: The account for which the campaign should be created.

          consent_flow: A string explaining the method through which end users will opt in to receive
              messages from the brand. Typically this should include URLs for opt-in forms or
              screenshots that might be helpful in explaining the flow to someone unfamiliar
              with the organization's purpose.

          description: An explanation of the organization's purpose and how it will be using text
              messaging to accomplish that purpose.

          message_samples: An array of 2-5 strings with examples of the messages that will be sent from
              this campaign. Typically the first sample should be a compliance message like
              `You are now opted in to messages from {brand name}. Frequency varies. Msg&data rates apply. Reply STOP to opt out.`
              These samples don't necessarily need to be the only templates that will be used
              for the campaign, but they should reflect the purpose of the messages that will
              be sent. Any variable content can be reflected by wrapping it in square brackets
              like `[customer name]`.

          privacy_policy_url: The URL of the privacy policy for the brand in question. This may be a shared
              privacy policy if it's the policy that is displayed to end users when they opt
              in to messaging.

          use_cases: A list containing 1-5 types of messages that will be sent with this campaign.

              The following use cases are typically available to all brands:

              - `account_notification` - For sending reminders, alerts, and general
                account-related notifications like booking confirmations or appointment
                reminders.
              - `customer_care` - For account support, troubleshooting, and general customer
                service communication.
              - `delivery_notification` - For notifying customers about the status of product
                or service deliveries.
              - `fraud_alert` - For warning customers about suspicious or potentially
                fraudulent activity.
              - `higher_education` - For messaging related to colleges, universities, and
                school districts outside of K–12.
              - `marketing` - For promotional or advertising messages intended to market
                products or services.
              - `polling_voting` - For conducting surveys, polls, or voting-related messaging.
              - `public_service_announcement` - For raising awareness about social issues or
                important public information.
              - `security_alert` - For alerts related to potential security breaches or
                compromised systems requiring user action.
              - `two_factor_authentication` - For sending one-time passwords or verification
                codes for login or password reset.

              For access to special use cases not shown here, reach out to support@surge.app.

          volume:
              This will be one of the following:

              - `low` - The campaign will be allowed to send up to 2000 SMS segments to
                T-Mobile customers each day. In this case your platform will be charged for
                the setup fee for a low volume number upon receipt of the API request.
              - `high` - The campaign will be allowed to send up to 200k SMS segments to
                T-Mobile customers each day, depending on the trust score assigned by The
                Campaign Registry. Your platform will be charged for the setup fee for a high
                volume number upon receipt of the API request, and phone numbers will be
                charged as high volume numbers going forward.

          includes: A list of properties that this campaign should include. These properties can be
              any of the following values:

              - `links` - whether the campaign might send links in messages
              - `phone_numbers` - whether the campaign might send phone numbers in messages
              - `age_gated` - whether the campaign contains age gated content (controlled
                substances or adult content)
              - `direct_lending` - whether the campaign contains content related to direct
                lending or other loan arrangements

          link_sample: A sample link that might be sent by this campaign. If links from other domains
              are sent through this campaign, they are much more likely to be filtered by the
              carriers. If link shortening is enabled for the account, the link shortener URL
              will be used instead of what is provided. Reach out to support if you would like
              to disable automatic link shortening.

          terms_and_conditions_url: The URL of the terms and conditions presented to end users when they opt in to
              messaging. These terms and conditions may be shared among all of a platform's
              customers if they're the terms that are presented to end users when they opt in
              to messaging.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/accounts/{account_id}/campaigns",
            body=maybe_transform(
                {
                    "consent_flow": consent_flow,
                    "description": description,
                    "message_samples": message_samples,
                    "privacy_policy_url": privacy_policy_url,
                    "use_cases": use_cases,
                    "volume": volume,
                    "includes": includes,
                    "link_sample": link_sample,
                    "terms_and_conditions_url": terms_and_conditions_url,
                },
                campaign_create_params.CampaignCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Campaign,
        )


class AsyncCampaignsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCampaignsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/surgeapi/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCampaignsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCampaignsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/surgeapi/python-sdk#with_streaming_response
        """
        return AsyncCampaignsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        consent_flow: str,
        description: str,
        message_samples: SequenceNotStr[str],
        privacy_policy_url: str,
        use_cases: List[
            Literal[
                "account_notification",
                "customer_care",
                "delivery_notification",
                "fraud_alert",
                "higher_education",
                "marketing",
                "polling_voting",
                "public_service_announcement",
                "security_alert",
                "two_factor_authentication",
            ]
        ],
        volume: Literal["high", "low"],
        includes: List[Literal["links", "phone_numbers", "age_gated", "direct_lending"]] | Omit = omit,
        link_sample: str | Omit = omit,
        terms_and_conditions_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Campaign:
        """
        Creates a campaign to register account to send text messages.

        Args:
          account_id: The account for which the campaign should be created.

          consent_flow: A string explaining the method through which end users will opt in to receive
              messages from the brand. Typically this should include URLs for opt-in forms or
              screenshots that might be helpful in explaining the flow to someone unfamiliar
              with the organization's purpose.

          description: An explanation of the organization's purpose and how it will be using text
              messaging to accomplish that purpose.

          message_samples: An array of 2-5 strings with examples of the messages that will be sent from
              this campaign. Typically the first sample should be a compliance message like
              `You are now opted in to messages from {brand name}. Frequency varies. Msg&data rates apply. Reply STOP to opt out.`
              These samples don't necessarily need to be the only templates that will be used
              for the campaign, but they should reflect the purpose of the messages that will
              be sent. Any variable content can be reflected by wrapping it in square brackets
              like `[customer name]`.

          privacy_policy_url: The URL of the privacy policy for the brand in question. This may be a shared
              privacy policy if it's the policy that is displayed to end users when they opt
              in to messaging.

          use_cases: A list containing 1-5 types of messages that will be sent with this campaign.

              The following use cases are typically available to all brands:

              - `account_notification` - For sending reminders, alerts, and general
                account-related notifications like booking confirmations or appointment
                reminders.
              - `customer_care` - For account support, troubleshooting, and general customer
                service communication.
              - `delivery_notification` - For notifying customers about the status of product
                or service deliveries.
              - `fraud_alert` - For warning customers about suspicious or potentially
                fraudulent activity.
              - `higher_education` - For messaging related to colleges, universities, and
                school districts outside of K–12.
              - `marketing` - For promotional or advertising messages intended to market
                products or services.
              - `polling_voting` - For conducting surveys, polls, or voting-related messaging.
              - `public_service_announcement` - For raising awareness about social issues or
                important public information.
              - `security_alert` - For alerts related to potential security breaches or
                compromised systems requiring user action.
              - `two_factor_authentication` - For sending one-time passwords or verification
                codes for login or password reset.

              For access to special use cases not shown here, reach out to support@surge.app.

          volume:
              This will be one of the following:

              - `low` - The campaign will be allowed to send up to 2000 SMS segments to
                T-Mobile customers each day. In this case your platform will be charged for
                the setup fee for a low volume number upon receipt of the API request.
              - `high` - The campaign will be allowed to send up to 200k SMS segments to
                T-Mobile customers each day, depending on the trust score assigned by The
                Campaign Registry. Your platform will be charged for the setup fee for a high
                volume number upon receipt of the API request, and phone numbers will be
                charged as high volume numbers going forward.

          includes: A list of properties that this campaign should include. These properties can be
              any of the following values:

              - `links` - whether the campaign might send links in messages
              - `phone_numbers` - whether the campaign might send phone numbers in messages
              - `age_gated` - whether the campaign contains age gated content (controlled
                substances or adult content)
              - `direct_lending` - whether the campaign contains content related to direct
                lending or other loan arrangements

          link_sample: A sample link that might be sent by this campaign. If links from other domains
              are sent through this campaign, they are much more likely to be filtered by the
              carriers. If link shortening is enabled for the account, the link shortener URL
              will be used instead of what is provided. Reach out to support if you would like
              to disable automatic link shortening.

          terms_and_conditions_url: The URL of the terms and conditions presented to end users when they opt in to
              messaging. These terms and conditions may be shared among all of a platform's
              customers if they're the terms that are presented to end users when they opt in
              to messaging.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/accounts/{account_id}/campaigns",
            body=await async_maybe_transform(
                {
                    "consent_flow": consent_flow,
                    "description": description,
                    "message_samples": message_samples,
                    "privacy_policy_url": privacy_policy_url,
                    "use_cases": use_cases,
                    "volume": volume,
                    "includes": includes,
                    "link_sample": link_sample,
                    "terms_and_conditions_url": terms_and_conditions_url,
                },
                campaign_create_params.CampaignCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Campaign,
        )


class CampaignsResourceWithRawResponse:
    def __init__(self, campaigns: CampaignsResource) -> None:
        self._campaigns = campaigns

        self.create = to_raw_response_wrapper(
            campaigns.create,
        )


class AsyncCampaignsResourceWithRawResponse:
    def __init__(self, campaigns: AsyncCampaignsResource) -> None:
        self._campaigns = campaigns

        self.create = async_to_raw_response_wrapper(
            campaigns.create,
        )


class CampaignsResourceWithStreamingResponse:
    def __init__(self, campaigns: CampaignsResource) -> None:
        self._campaigns = campaigns

        self.create = to_streamed_response_wrapper(
            campaigns.create,
        )


class AsyncCampaignsResourceWithStreamingResponse:
    def __init__(self, campaigns: AsyncCampaignsResource) -> None:
        self._campaigns = campaigns

        self.create = async_to_streamed_response_wrapper(
            campaigns.create,
        )
