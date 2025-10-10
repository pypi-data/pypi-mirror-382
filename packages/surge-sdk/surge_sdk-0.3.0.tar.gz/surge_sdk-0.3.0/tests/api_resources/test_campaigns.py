# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from surge import Surge, AsyncSurge
from surge.types import Campaign
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCampaigns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Surge) -> None:
        campaign = client.campaigns.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
            description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
            message_samples=[
                "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
            ],
            privacy_policy_url="https://fastauto.shop/sms-privacy",
            use_cases=["account_notification", "customer_care", "marketing"],
            volume="high",
        )
        assert_matches_type(Campaign, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Surge) -> None:
        campaign = client.campaigns.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
            description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
            message_samples=[
                "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
            ],
            privacy_policy_url="https://fastauto.shop/sms-privacy",
            use_cases=["account_notification", "customer_care", "marketing"],
            volume="high",
            includes=["links", "phone_numbers"],
            link_sample="https://l.fastauto.shop/s034ij",
            terms_and_conditions_url="https://fastauto.shop/terms-and-conditions",
        )
        assert_matches_type(Campaign, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Surge) -> None:
        response = client.campaigns.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
            description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
            message_samples=[
                "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
            ],
            privacy_policy_url="https://fastauto.shop/sms-privacy",
            use_cases=["account_notification", "customer_care", "marketing"],
            volume="high",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = response.parse()
        assert_matches_type(Campaign, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Surge) -> None:
        with client.campaigns.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
            description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
            message_samples=[
                "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
            ],
            privacy_policy_url="https://fastauto.shop/sms-privacy",
            use_cases=["account_notification", "customer_care", "marketing"],
            volume="high",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = response.parse()
            assert_matches_type(Campaign, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.campaigns.with_raw_response.create(
                account_id="",
                consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
                description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
                message_samples=[
                    "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                    "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                    "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
                ],
                privacy_policy_url="https://fastauto.shop/sms-privacy",
                use_cases=["account_notification", "customer_care", "marketing"],
                volume="high",
            )


class TestAsyncCampaigns:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSurge) -> None:
        campaign = await async_client.campaigns.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
            description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
            message_samples=[
                "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
            ],
            privacy_policy_url="https://fastauto.shop/sms-privacy",
            use_cases=["account_notification", "customer_care", "marketing"],
            volume="high",
        )
        assert_matches_type(Campaign, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSurge) -> None:
        campaign = await async_client.campaigns.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
            description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
            message_samples=[
                "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
            ],
            privacy_policy_url="https://fastauto.shop/sms-privacy",
            use_cases=["account_notification", "customer_care", "marketing"],
            volume="high",
            includes=["links", "phone_numbers"],
            link_sample="https://l.fastauto.shop/s034ij",
            terms_and_conditions_url="https://fastauto.shop/terms-and-conditions",
        )
        assert_matches_type(Campaign, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSurge) -> None:
        response = await async_client.campaigns.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
            description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
            message_samples=[
                "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
            ],
            privacy_policy_url="https://fastauto.shop/sms-privacy",
            use_cases=["account_notification", "customer_care", "marketing"],
            volume="high",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = await response.parse()
        assert_matches_type(Campaign, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSurge) -> None:
        async with async_client.campaigns.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
            description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
            message_samples=[
                "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
            ],
            privacy_policy_url="https://fastauto.shop/sms-privacy",
            use_cases=["account_notification", "customer_care", "marketing"],
            volume="high",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = await response.parse()
            assert_matches_type(Campaign, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.campaigns.with_raw_response.create(
                account_id="",
                consent_flow="When customers bring in their car for service, they will fill out this web form for intake: https://fastauto.shop/bp108c In it they can choose to opt in to text message notifications. If they choose to opt in, we will send them notifications to let them know if our mechanics find issues and once the car is ready to go, as well as links to invoices and to leave us feedback.",
                description="This phone number will send auto maintenance notifications to end users that have opted in. It will also be used for responding to customer inquiries and sending some marketing offers.",
                message_samples=[
                    "You are now opted in to receive repair notifications from DT Precision Auto. Frequency varies. Msg&data rates apply. Reply STOP to opt out.",
                    "You're lucky that hundred shot of NOS didn't blow the welds on the intake!",
                    "Your car is ready to go. See your invoice here: https://l.fastauto.shop/s034ij",
                ],
                privacy_policy_url="https://fastauto.shop/sms-privacy",
                use_cases=["account_notification", "customer_care", "marketing"],
                volume="high",
            )
