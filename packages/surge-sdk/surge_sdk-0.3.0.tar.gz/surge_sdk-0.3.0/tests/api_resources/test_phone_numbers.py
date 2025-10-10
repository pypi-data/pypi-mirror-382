# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from surge import Surge, AsyncSurge
from surge.types import PhoneNumber
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPhoneNumbers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_purchase(self, client: Surge) -> None:
        phone_number = client.phone_numbers.purchase(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_purchase_with_all_params(self, client: Surge) -> None:
        phone_number = client.phone_numbers.purchase(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            area_code="801",
            latitude=40.7128,
            longitude=-74.006,
            type="local",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_purchase(self, client: Surge) -> None:
        response = client.phone_numbers.with_raw_response.purchase(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = response.parse()
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_purchase(self, client: Surge) -> None:
        with client.phone_numbers.with_streaming_response.purchase(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = response.parse()
            assert_matches_type(PhoneNumber, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_purchase(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.phone_numbers.with_raw_response.purchase(
                account_id="",
            )


class TestAsyncPhoneNumbers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_purchase(self, async_client: AsyncSurge) -> None:
        phone_number = await async_client.phone_numbers.purchase(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_purchase_with_all_params(self, async_client: AsyncSurge) -> None:
        phone_number = await async_client.phone_numbers.purchase(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            area_code="801",
            latitude=40.7128,
            longitude=-74.006,
            type="local",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_purchase(self, async_client: AsyncSurge) -> None:
        response = await async_client.phone_numbers.with_raw_response.purchase(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = await response.parse()
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_purchase(self, async_client: AsyncSurge) -> None:
        async with async_client.phone_numbers.with_streaming_response.purchase(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = await response.parse()
            assert_matches_type(PhoneNumber, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_purchase(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.phone_numbers.with_raw_response.purchase(
                account_id="",
            )
