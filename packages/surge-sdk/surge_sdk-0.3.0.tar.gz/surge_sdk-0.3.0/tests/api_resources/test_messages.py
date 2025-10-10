# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from surge import Surge, AsyncSurge
from surge.types import Message
from tests.utils import assert_matches_type
from surge._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_overload_1(self, client: Surge) -> None:
        message = client.messages.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            conversation={"contact": {"phone_number": "+18015551234"}},
        )
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: Surge) -> None:
        message = client.messages.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            conversation={
                "contact": {
                    "phone_number": "+18015551234",
                    "email": "dom@toretto.family",
                    "first_name": "Dominic",
                    "last_name": "Toretto",
                    "metadata": {"car": "1970 Dodge Charger R/T"},
                },
                "phone_number": "+18015556789",
            },
            attachments=[{"url": "https://toretto.family/coronas.gif"}],
            body="body",
            send_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_overload_1(self, client: Surge) -> None:
        response = client.messages.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            conversation={"contact": {"phone_number": "+18015551234"}},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_1(self, client: Surge) -> None:
        with client.messages.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            conversation={"contact": {"phone_number": "+18015551234"}},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_overload_1(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.messages.with_raw_response.create(
                account_id="",
                conversation={"contact": {"phone_number": "+18015551234"}},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_overload_2(self, client: Surge) -> None:
        message = client.messages.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            to="+18015551234",
        )
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: Surge) -> None:
        message = client.messages.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            to="+18015551234",
            attachments=[{"url": "https://toretto.family/coronas.gif"}],
            body="body",
            from_="+18015552345",
            send_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_overload_2(self, client: Surge) -> None:
        response = client.messages.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            to="+18015551234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_2(self, client: Surge) -> None:
        with client.messages.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            to="+18015551234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_overload_2(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.messages.with_raw_response.create(
                account_id="",
                to="+18015551234",
            )


class TestAsyncMessages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncSurge) -> None:
        message = await async_client.messages.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            conversation={"contact": {"phone_number": "+18015551234"}},
        )
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncSurge) -> None:
        message = await async_client.messages.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            conversation={
                "contact": {
                    "phone_number": "+18015551234",
                    "email": "dom@toretto.family",
                    "first_name": "Dominic",
                    "last_name": "Toretto",
                    "metadata": {"car": "1970 Dodge Charger R/T"},
                },
                "phone_number": "+18015556789",
            },
            attachments=[{"url": "https://toretto.family/coronas.gif"}],
            body="body",
            send_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncSurge) -> None:
        response = await async_client.messages.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            conversation={"contact": {"phone_number": "+18015551234"}},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncSurge) -> None:
        async with async_client.messages.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            conversation={"contact": {"phone_number": "+18015551234"}},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_overload_1(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.messages.with_raw_response.create(
                account_id="",
                conversation={"contact": {"phone_number": "+18015551234"}},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncSurge) -> None:
        message = await async_client.messages.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            to="+18015551234",
        )
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncSurge) -> None:
        message = await async_client.messages.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            to="+18015551234",
            attachments=[{"url": "https://toretto.family/coronas.gif"}],
            body="body",
            from_="+18015552345",
            send_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncSurge) -> None:
        response = await async_client.messages.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            to="+18015551234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(Message, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncSurge) -> None:
        async with async_client.messages.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            to="+18015551234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_overload_2(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.messages.with_raw_response.create(
                account_id="",
                to="+18015551234",
            )
