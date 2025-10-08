# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from tzafonComputer import Computer, AsyncComputer
from tzafonComputer.types import (
    AuthLogoutResponse,
    AuthHandleCallbackResponse,
    AuthRetrieveCurrentUserResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuth:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_handle_callback(self, client: Computer) -> None:
        auth = client.auth.handle_callback(
            code="code",
            state="state",
        )
        assert_matches_type(AuthHandleCallbackResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_handle_callback(self, client: Computer) -> None:
        response = client.auth.with_raw_response.handle_callback(
            code="code",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(AuthHandleCallbackResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_handle_callback(self, client: Computer) -> None:
        with client.auth.with_streaming_response.handle_callback(
            code="code",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(AuthHandleCallbackResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_method_initiate_login(self, client: Computer) -> None:
        auth = client.auth.initiate_login()
        assert auth is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_raw_response_initiate_login(self, client: Computer) -> None:
        response = client.auth.with_raw_response.initiate_login()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert auth is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_streaming_response_initiate_login(self, client: Computer) -> None:
        with client.auth.with_streaming_response.initiate_login() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_logout(self, client: Computer) -> None:
        auth = client.auth.logout()
        assert_matches_type(AuthLogoutResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_logout(self, client: Computer) -> None:
        response = client.auth.with_raw_response.logout()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(AuthLogoutResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_logout(self, client: Computer) -> None:
        with client.auth.with_streaming_response.logout() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(AuthLogoutResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_current_user(self, client: Computer) -> None:
        auth = client.auth.retrieve_current_user()
        assert_matches_type(AuthRetrieveCurrentUserResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_current_user(self, client: Computer) -> None:
        response = client.auth.with_raw_response.retrieve_current_user()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(AuthRetrieveCurrentUserResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_current_user(self, client: Computer) -> None:
        with client.auth.with_streaming_response.retrieve_current_user() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(AuthRetrieveCurrentUserResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAuth:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_handle_callback(self, async_client: AsyncComputer) -> None:
        auth = await async_client.auth.handle_callback(
            code="code",
            state="state",
        )
        assert_matches_type(AuthHandleCallbackResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_handle_callback(self, async_client: AsyncComputer) -> None:
        response = await async_client.auth.with_raw_response.handle_callback(
            code="code",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(AuthHandleCallbackResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_handle_callback(self, async_client: AsyncComputer) -> None:
        async with async_client.auth.with_streaming_response.handle_callback(
            code="code",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(AuthHandleCallbackResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_method_initiate_login(self, async_client: AsyncComputer) -> None:
        auth = await async_client.auth.initiate_login()
        assert auth is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_raw_response_initiate_login(self, async_client: AsyncComputer) -> None:
        response = await async_client.auth.with_raw_response.initiate_login()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert auth is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_streaming_response_initiate_login(self, async_client: AsyncComputer) -> None:
        async with async_client.auth.with_streaming_response.initiate_login() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_logout(self, async_client: AsyncComputer) -> None:
        auth = await async_client.auth.logout()
        assert_matches_type(AuthLogoutResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_logout(self, async_client: AsyncComputer) -> None:
        response = await async_client.auth.with_raw_response.logout()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(AuthLogoutResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_logout(self, async_client: AsyncComputer) -> None:
        async with async_client.auth.with_streaming_response.logout() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(AuthLogoutResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_current_user(self, async_client: AsyncComputer) -> None:
        auth = await async_client.auth.retrieve_current_user()
        assert_matches_type(AuthRetrieveCurrentUserResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_current_user(self, async_client: AsyncComputer) -> None:
        response = await async_client.auth.with_raw_response.retrieve_current_user()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(AuthRetrieveCurrentUserResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_current_user(self, async_client: AsyncComputer) -> None:
        async with async_client.auth.with_streaming_response.retrieve_current_user() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(AuthRetrieveCurrentUserResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True
