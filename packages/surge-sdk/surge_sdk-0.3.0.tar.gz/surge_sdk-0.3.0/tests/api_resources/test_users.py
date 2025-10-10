# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from surge import Surge, AsyncSurge
from surge.types import User, UserTokenResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Surge) -> None:
        user = client.users.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            first_name="Brian",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Surge) -> None:
        user = client.users.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            first_name="Brian",
            last_name="O'Conner",
            metadata={
                "email": "boconner@toretti.family",
                "user_id": "string",
            },
            photo_url="https://toretti.family/people/brian.jpg",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Surge) -> None:
        response = client.users.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            first_name="Brian",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Surge) -> None:
        with client.users.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            first_name="Brian",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(User, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.users.with_raw_response.create(
                account_id="",
                first_name="Brian",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Surge) -> None:
        user = client.users.retrieve(
            "usr_01j9dwavghe1ttppewekjjkfrx",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Surge) -> None:
        response = client.users.with_raw_response.retrieve(
            "usr_01j9dwavghe1ttppewekjjkfrx",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Surge) -> None:
        with client.users.with_streaming_response.retrieve(
            "usr_01j9dwavghe1ttppewekjjkfrx",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(User, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.users.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Surge) -> None:
        user = client.users.update(
            id="usr_01j9dwavghe1ttppewekjjkfrx",
            first_name="Brian",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Surge) -> None:
        user = client.users.update(
            id="usr_01j9dwavghe1ttppewekjjkfrx",
            first_name="Brian",
            last_name="O'Conner",
            metadata={
                "email": "boconner@toretti.family",
                "user_id": "string",
            },
            photo_url="https://toretti.family/people/brian.jpg",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Surge) -> None:
        response = client.users.with_raw_response.update(
            id="usr_01j9dwavghe1ttppewekjjkfrx",
            first_name="Brian",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Surge) -> None:
        with client.users.with_streaming_response.update(
            id="usr_01j9dwavghe1ttppewekjjkfrx",
            first_name="Brian",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(User, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.users.with_raw_response.update(
                id="",
                first_name="Brian",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_token(self, client: Surge) -> None:
        user = client.users.create_token(
            user_id="usr_01jymgdfrpec2asc5m0z3a6fr9",
        )
        assert_matches_type(UserTokenResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_token_with_all_params(self, client: Surge) -> None:
        user = client.users.create_token(
            user_id="usr_01jymgdfrpec2asc5m0z3a6fr9",
            duration_seconds=900,
        )
        assert_matches_type(UserTokenResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_token(self, client: Surge) -> None:
        response = client.users.with_raw_response.create_token(
            user_id="usr_01jymgdfrpec2asc5m0z3a6fr9",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserTokenResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_token(self, client: Surge) -> None:
        with client.users.with_streaming_response.create_token(
            user_id="usr_01jymgdfrpec2asc5m0z3a6fr9",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserTokenResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_token(self, client: Surge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.users.with_raw_response.create_token(
                user_id="",
            )


class TestAsyncUsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSurge) -> None:
        user = await async_client.users.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            first_name="Brian",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSurge) -> None:
        user = await async_client.users.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            first_name="Brian",
            last_name="O'Conner",
            metadata={
                "email": "boconner@toretti.family",
                "user_id": "string",
            },
            photo_url="https://toretti.family/people/brian.jpg",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSurge) -> None:
        response = await async_client.users.with_raw_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            first_name="Brian",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSurge) -> None:
        async with async_client.users.with_streaming_response.create(
            account_id="acct_01j9a43avnfqzbjfch6pygv1td",
            first_name="Brian",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(User, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.users.with_raw_response.create(
                account_id="",
                first_name="Brian",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSurge) -> None:
        user = await async_client.users.retrieve(
            "usr_01j9dwavghe1ttppewekjjkfrx",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSurge) -> None:
        response = await async_client.users.with_raw_response.retrieve(
            "usr_01j9dwavghe1ttppewekjjkfrx",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSurge) -> None:
        async with async_client.users.with_streaming_response.retrieve(
            "usr_01j9dwavghe1ttppewekjjkfrx",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(User, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.users.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncSurge) -> None:
        user = await async_client.users.update(
            id="usr_01j9dwavghe1ttppewekjjkfrx",
            first_name="Brian",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncSurge) -> None:
        user = await async_client.users.update(
            id="usr_01j9dwavghe1ttppewekjjkfrx",
            first_name="Brian",
            last_name="O'Conner",
            metadata={
                "email": "boconner@toretti.family",
                "user_id": "string",
            },
            photo_url="https://toretti.family/people/brian.jpg",
        )
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncSurge) -> None:
        response = await async_client.users.with_raw_response.update(
            id="usr_01j9dwavghe1ttppewekjjkfrx",
            first_name="Brian",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(User, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncSurge) -> None:
        async with async_client.users.with_streaming_response.update(
            id="usr_01j9dwavghe1ttppewekjjkfrx",
            first_name="Brian",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(User, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.users.with_raw_response.update(
                id="",
                first_name="Brian",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_token(self, async_client: AsyncSurge) -> None:
        user = await async_client.users.create_token(
            user_id="usr_01jymgdfrpec2asc5m0z3a6fr9",
        )
        assert_matches_type(UserTokenResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_token_with_all_params(self, async_client: AsyncSurge) -> None:
        user = await async_client.users.create_token(
            user_id="usr_01jymgdfrpec2asc5m0z3a6fr9",
            duration_seconds=900,
        )
        assert_matches_type(UserTokenResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_token(self, async_client: AsyncSurge) -> None:
        response = await async_client.users.with_raw_response.create_token(
            user_id="usr_01jymgdfrpec2asc5m0z3a6fr9",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserTokenResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_token(self, async_client: AsyncSurge) -> None:
        async with async_client.users.with_streaming_response.create_token(
            user_id="usr_01jymgdfrpec2asc5m0z3a6fr9",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserTokenResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_token(self, async_client: AsyncSurge) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.users.with_raw_response.create_token(
                user_id="",
            )
