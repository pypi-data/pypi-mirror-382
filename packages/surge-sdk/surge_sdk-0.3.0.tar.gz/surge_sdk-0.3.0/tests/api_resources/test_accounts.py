# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from surge import Surge, AsyncSurge
from surge.types import (
    Account,
    AccountStatus,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAccounts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Surge) -> None:
        account = client.accounts.create(
            name="Account #2840 - DT Precision Auto",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Surge) -> None:
        account = client.accounts.create(
            name="Account #2840 - DT Precision Auto",
            brand_name="DT Precision Auto",
            organization={
                "address": {
                    "country": "US",
                    "line1": "2640 Huron St",
                    "line2": None,
                    "locality": "Los Angeles",
                    "name": "DT Precision Auto",
                    "postal_code": "90065",
                    "region": "CA",
                },
                "contact": {
                    "email": "dom@dtprecisionauto.com",
                    "first_name": "Dominic",
                    "last_name": "Toretto",
                    "phone_number": "+13235556439",
                    "title": "other",
                    "title_other": "Owner",
                },
                "country": "US",
                "email": "dom@dtprecisionauto.com",
                "identifier": "123456789",
                "identifier_type": "ein",
                "industry": "automotive",
                "mobile_number": "+13235556439",
                "regions_of_operation": ["usa_and_canada"],
                "registered_name": "DT Precision Auto LLC",
                "stock_exchange": None,
                "stock_symbol": None,
                "type": "llc",
                "website": "https://dtprecisionauto.com",
            },
            time_zone="America/Los_Angeles",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Surge) -> None:
        response = client.accounts.with_raw_response.create(
            name="Account #2840 - DT Precision Auto",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Surge) -> None:
        with client.accounts.with_streaming_response.create(
            name="Account #2840 - DT Precision Auto",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(Account, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Surge) -> None:
        account = client.accounts.update(
            id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Surge) -> None:
        account = client.accounts.update(
            id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
            brand_name="DT Precision Auto",
            name="D·T Precision Auto Shop",
            organization={
                "address": {
                    "country": "US",
                    "line1": "2640 Huron St",
                    "line2": None,
                    "locality": "Los Angeles",
                    "name": "DT Precision Auto",
                    "postal_code": "90065",
                    "region": "CA",
                },
                "contact": {
                    "email": "dom@dtprecisionauto.com",
                    "first_name": "Dominic",
                    "last_name": "Toretto",
                    "phone_number": "+13235556439",
                    "title": "other",
                    "title_other": "Owner",
                },
                "country": "US",
                "email": "dom@dtprecisionauto.com",
                "identifier": "123456789",
                "identifier_type": "ein",
                "industry": "automotive",
                "mobile_number": "+13235556439",
                "regions_of_operation": ["usa_and_canada"],
                "registered_name": "DT Precision Auto LLC",
                "stock_exchange": None,
                "stock_symbol": None,
                "type": "llc",
                "website": "https://dtprecisionauto.com",
            },
            time_zone="America/Los_Angeles",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Surge) -> None:
        response = client.accounts.with_raw_response.update(
            id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Surge) -> None:
        with client.accounts.with_streaming_response.update(
            id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(Account, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.accounts.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_status(self, client: Surge) -> None:
        account = client.accounts.retrieve_status(
            account_id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        )
        assert_matches_type(AccountStatus, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_status_with_all_params(self, client: Surge) -> None:
        account = client.accounts.retrieve_status(
            account_id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
            capabilities=["local_messaging"],
        )
        assert_matches_type(AccountStatus, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_status(self, client: Surge) -> None:
        response = client.accounts.with_raw_response.retrieve_status(
            account_id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountStatus, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_status(self, client: Surge) -> None:
        with client.accounts.with_streaming_response.retrieve_status(
            account_id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountStatus, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_status(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.with_raw_response.retrieve_status(
                account_id="",
            )


class TestAsyncAccounts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSurge) -> None:
        account = await async_client.accounts.create(
            name="Account #2840 - DT Precision Auto",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSurge) -> None:
        account = await async_client.accounts.create(
            name="Account #2840 - DT Precision Auto",
            brand_name="DT Precision Auto",
            organization={
                "address": {
                    "country": "US",
                    "line1": "2640 Huron St",
                    "line2": None,
                    "locality": "Los Angeles",
                    "name": "DT Precision Auto",
                    "postal_code": "90065",
                    "region": "CA",
                },
                "contact": {
                    "email": "dom@dtprecisionauto.com",
                    "first_name": "Dominic",
                    "last_name": "Toretto",
                    "phone_number": "+13235556439",
                    "title": "other",
                    "title_other": "Owner",
                },
                "country": "US",
                "email": "dom@dtprecisionauto.com",
                "identifier": "123456789",
                "identifier_type": "ein",
                "industry": "automotive",
                "mobile_number": "+13235556439",
                "regions_of_operation": ["usa_and_canada"],
                "registered_name": "DT Precision Auto LLC",
                "stock_exchange": None,
                "stock_symbol": None,
                "type": "llc",
                "website": "https://dtprecisionauto.com",
            },
            time_zone="America/Los_Angeles",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSurge) -> None:
        response = await async_client.accounts.with_raw_response.create(
            name="Account #2840 - DT Precision Auto",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSurge) -> None:
        async with async_client.accounts.with_streaming_response.create(
            name="Account #2840 - DT Precision Auto",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(Account, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncSurge) -> None:
        account = await async_client.accounts.update(
            id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncSurge) -> None:
        account = await async_client.accounts.update(
            id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
            brand_name="DT Precision Auto",
            name="D·T Precision Auto Shop",
            organization={
                "address": {
                    "country": "US",
                    "line1": "2640 Huron St",
                    "line2": None,
                    "locality": "Los Angeles",
                    "name": "DT Precision Auto",
                    "postal_code": "90065",
                    "region": "CA",
                },
                "contact": {
                    "email": "dom@dtprecisionauto.com",
                    "first_name": "Dominic",
                    "last_name": "Toretto",
                    "phone_number": "+13235556439",
                    "title": "other",
                    "title_other": "Owner",
                },
                "country": "US",
                "email": "dom@dtprecisionauto.com",
                "identifier": "123456789",
                "identifier_type": "ein",
                "industry": "automotive",
                "mobile_number": "+13235556439",
                "regions_of_operation": ["usa_and_canada"],
                "registered_name": "DT Precision Auto LLC",
                "stock_exchange": None,
                "stock_symbol": None,
                "type": "llc",
                "website": "https://dtprecisionauto.com",
            },
            time_zone="America/Los_Angeles",
        )
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncSurge) -> None:
        response = await async_client.accounts.with_raw_response.update(
            id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(Account, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncSurge) -> None:
        async with async_client.accounts.with_streaming_response.update(
            id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(Account, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.accounts.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_status(self, async_client: AsyncSurge) -> None:
        account = await async_client.accounts.retrieve_status(
            account_id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        )
        assert_matches_type(AccountStatus, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_status_with_all_params(self, async_client: AsyncSurge) -> None:
        account = await async_client.accounts.retrieve_status(
            account_id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
            capabilities=["local_messaging"],
        )
        assert_matches_type(AccountStatus, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_status(self, async_client: AsyncSurge) -> None:
        response = await async_client.accounts.with_raw_response.retrieve_status(
            account_id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountStatus, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_status(self, async_client: AsyncSurge) -> None:
        async with async_client.accounts.with_streaming_response.retrieve_status(
            account_id="acct_01jpqjvfg9enpt7pyxd60pcmxj",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountStatus, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_status(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.with_raw_response.retrieve_status(
                account_id="",
            )
