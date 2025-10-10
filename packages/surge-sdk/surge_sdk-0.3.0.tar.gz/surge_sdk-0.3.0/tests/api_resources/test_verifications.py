# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from surge import Surge, AsyncSurge
from surge.types import Verification, VerificationCheck
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVerifications:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Surge) -> None:
        verification = client.verifications.create(
            phone_number="+18015551234",
        )
        assert_matches_type(Verification, verification, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Surge) -> None:
        response = client.verifications.with_raw_response.create(
            phone_number="+18015551234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        verification = response.parse()
        assert_matches_type(Verification, verification, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Surge) -> None:
        with client.verifications.with_streaming_response.create(
            phone_number="+18015551234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            verification = response.parse()
            assert_matches_type(Verification, verification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_check(self, client: Surge) -> None:
        verification = client.verifications.check(
            id="vfn_01jayh15c2f2xamftg0xpyq1nj",
            code="123456",
        )
        assert_matches_type(VerificationCheck, verification, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_check(self, client: Surge) -> None:
        response = client.verifications.with_raw_response.check(
            id="vfn_01jayh15c2f2xamftg0xpyq1nj",
            code="123456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        verification = response.parse()
        assert_matches_type(VerificationCheck, verification, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_check(self, client: Surge) -> None:
        with client.verifications.with_streaming_response.check(
            id="vfn_01jayh15c2f2xamftg0xpyq1nj",
            code="123456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            verification = response.parse()
            assert_matches_type(VerificationCheck, verification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_check(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.verifications.with_raw_response.check(
                id="",
                code="123456",
            )


class TestAsyncVerifications:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSurge) -> None:
        verification = await async_client.verifications.create(
            phone_number="+18015551234",
        )
        assert_matches_type(Verification, verification, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSurge) -> None:
        response = await async_client.verifications.with_raw_response.create(
            phone_number="+18015551234",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        verification = await response.parse()
        assert_matches_type(Verification, verification, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSurge) -> None:
        async with async_client.verifications.with_streaming_response.create(
            phone_number="+18015551234",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            verification = await response.parse()
            assert_matches_type(Verification, verification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_check(self, async_client: AsyncSurge) -> None:
        verification = await async_client.verifications.check(
            id="vfn_01jayh15c2f2xamftg0xpyq1nj",
            code="123456",
        )
        assert_matches_type(VerificationCheck, verification, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_check(self, async_client: AsyncSurge) -> None:
        response = await async_client.verifications.with_raw_response.check(
            id="vfn_01jayh15c2f2xamftg0xpyq1nj",
            code="123456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        verification = await response.parse()
        assert_matches_type(VerificationCheck, verification, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_check(self, async_client: AsyncSurge) -> None:
        async with async_client.verifications.with_streaming_response.check(
            id="vfn_01jayh15c2f2xamftg0xpyq1nj",
            code="123456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            verification = await response.parse()
            assert_matches_type(VerificationCheck, verification, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_check(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.verifications.with_raw_response.check(
                id="",
                code="123456",
            )
