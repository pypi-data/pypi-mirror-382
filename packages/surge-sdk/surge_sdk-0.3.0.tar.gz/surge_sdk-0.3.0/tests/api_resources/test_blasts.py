# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from surge import Surge, AsyncSurge
from surge.types import Blast
from tests.utils import assert_matches_type
from surge._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBlasts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Surge) -> None:
        blast = client.blasts.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        )
        assert_matches_type(Blast, blast, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Surge) -> None:
        blast = client.blasts.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            attachments=[{"url": "https://example.com/image.jpg"}],
            body="Join us for our grand opening!",
            contacts=["ctc_01jxwtp1vse91twb5bj977gav9"],
            name="Grand Opening Announcement",
            segments=["seg_01jxwtwzqhfykb31dt6mvpsa9k"],
            send_at=parse_datetime("2024-02-01T15:00:00Z"),
            to=["seg_01j9dy8mdzfn3r0e8x1tbdrdrf", "ctc_01j9dy8mdzfn3r0e8x1tbdrdrf", "+18015551234", "+18015555678"],
        )
        assert_matches_type(Blast, blast, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Surge) -> None:
        response = client.blasts.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        blast = response.parse()
        assert_matches_type(Blast, blast, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Surge) -> None:
        with client.blasts.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            blast = response.parse()
            assert_matches_type(Blast, blast, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.blasts.with_raw_response.create(
                account_id="",
            )


class TestAsyncBlasts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSurge) -> None:
        blast = await async_client.blasts.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        )
        assert_matches_type(Blast, blast, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSurge) -> None:
        blast = await async_client.blasts.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            attachments=[{"url": "https://example.com/image.jpg"}],
            body="Join us for our grand opening!",
            contacts=["ctc_01jxwtp1vse91twb5bj977gav9"],
            name="Grand Opening Announcement",
            segments=["seg_01jxwtwzqhfykb31dt6mvpsa9k"],
            send_at=parse_datetime("2024-02-01T15:00:00Z"),
            to=["seg_01j9dy8mdzfn3r0e8x1tbdrdrf", "ctc_01j9dy8mdzfn3r0e8x1tbdrdrf", "+18015551234", "+18015555678"],
        )
        assert_matches_type(Blast, blast, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSurge) -> None:
        response = await async_client.blasts.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        blast = await response.parse()
        assert_matches_type(Blast, blast, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSurge) -> None:
        async with async_client.blasts.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            blast = await response.parse()
            assert_matches_type(Blast, blast, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.blasts.with_raw_response.create(
                account_id="",
            )
