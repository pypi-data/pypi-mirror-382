# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from surge import Surge, AsyncSurge
from surge.types import Contact
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestContacts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Surge) -> None:
        contact = client.contacts.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            phone_number="+18015551234",
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Surge) -> None:
        contact = client.contacts.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            phone_number="+18015551234",
            email="dom@toretto.family",
            first_name="Dominic",
            last_name="Toretto",
            metadata={"car": "1970 Dodge Charger R/T"},
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Surge) -> None:
        response = client.contacts.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            phone_number="+18015551234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contact = response.parse()
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Surge) -> None:
        with client.contacts.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            phone_number="+18015551234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contact = response.parse()
            assert_matches_type(Contact, contact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.contacts.with_raw_response.create(
                account_id="",
                phone_number="+18015551234",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Surge) -> None:
        contact = client.contacts.retrieve(
            "ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Surge) -> None:
        response = client.contacts.with_raw_response.retrieve(
            "ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contact = response.parse()
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Surge) -> None:
        with client.contacts.with_streaming_response.retrieve(
            "ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contact = response.parse()
            assert_matches_type(Contact, contact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.contacts.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Surge) -> None:
        contact = client.contacts.update(
            id="ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
            phone_number="+18015551234",
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Surge) -> None:
        contact = client.contacts.update(
            id="ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
            phone_number="+18015551234",
            email="dom@toretto.family",
            first_name="Dominic",
            last_name="Toretto",
            metadata={"car": "1970 Dodge Charger R/T"},
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Surge) -> None:
        response = client.contacts.with_raw_response.update(
            id="ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
            phone_number="+18015551234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contact = response.parse()
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Surge) -> None:
        with client.contacts.with_streaming_response.update(
            id="ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
            phone_number="+18015551234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contact = response.parse()
            assert_matches_type(Contact, contact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.contacts.with_raw_response.update(
                id="",
                phone_number="+18015551234",
            )


class TestAsyncContacts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSurge) -> None:
        contact = await async_client.contacts.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            phone_number="+18015551234",
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSurge) -> None:
        contact = await async_client.contacts.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            phone_number="+18015551234",
            email="dom@toretto.family",
            first_name="Dominic",
            last_name="Toretto",
            metadata={"car": "1970 Dodge Charger R/T"},
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSurge) -> None:
        response = await async_client.contacts.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            phone_number="+18015551234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contact = await response.parse()
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSurge) -> None:
        async with async_client.contacts.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            phone_number="+18015551234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contact = await response.parse()
            assert_matches_type(Contact, contact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.contacts.with_raw_response.create(
                account_id="",
                phone_number="+18015551234",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSurge) -> None:
        contact = await async_client.contacts.retrieve(
            "ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSurge) -> None:
        response = await async_client.contacts.with_raw_response.retrieve(
            "ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contact = await response.parse()
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSurge) -> None:
        async with async_client.contacts.with_streaming_response.retrieve(
            "ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contact = await response.parse()
            assert_matches_type(Contact, contact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.contacts.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncSurge) -> None:
        contact = await async_client.contacts.update(
            id="ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
            phone_number="+18015551234",
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncSurge) -> None:
        contact = await async_client.contacts.update(
            id="ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
            phone_number="+18015551234",
            email="dom@toretto.family",
            first_name="Dominic",
            last_name="Toretto",
            metadata={"car": "1970 Dodge Charger R/T"},
        )
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncSurge) -> None:
        response = await async_client.contacts.with_raw_response.update(
            id="ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
            phone_number="+18015551234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contact = await response.parse()
        assert_matches_type(Contact, contact, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncSurge) -> None:
        async with async_client.contacts.with_streaming_response.update(
            id="ctc_01j9dy8mdzfn3r0e8x1tbdrdrf",
            phone_number="+18015551234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contact = await response.parse()
            assert_matches_type(Contact, contact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.contacts.with_raw_response.update(
                id="",
                phone_number="+18015551234",
            )
