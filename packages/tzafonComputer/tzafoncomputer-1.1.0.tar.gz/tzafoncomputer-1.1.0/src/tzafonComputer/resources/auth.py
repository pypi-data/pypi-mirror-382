# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import auth_handle_callback_params
from .._types import Body, Query, Headers, NoneType, NotGiven, not_given
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
from ..types.auth_logout_response import AuthLogoutResponse
from ..types.auth_handle_callback_response import AuthHandleCallbackResponse
from ..types.auth_retrieve_current_user_response import AuthRetrieveCurrentUserResponse

__all__ = ["AuthResource", "AsyncAuthResource"]


class AuthResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AuthResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/atulgavandetzafon/computer-python#accessing-raw-response-data-eg-headers
        """
        return AuthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AuthResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/atulgavandetzafon/computer-python#with_streaming_response
        """
        return AuthResourceWithStreamingResponse(self)

    def handle_callback(
        self,
        *,
        code: str,
        state: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthHandleCallbackResponse:
        """
        Handle OAuth callback from WorkOS AuthKit and exchange code for user profile

        Args:
          code: Authorization code (valid for 10 minutes)

          state: State parameter for CSRF protection

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/auth/callback",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "code": code,
                        "state": state,
                    },
                    auth_handle_callback_params.AuthHandleCallbackParams,
                ),
            ),
            cast_to=AuthHandleCallbackResponse,
        )

    def initiate_login(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Redirect to WorkOS AuthKit for authentication"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/auth/login",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def logout(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthLogoutResponse:
        """Revoke user session and clear cookies"""
        return self._post(
            "/auth/logout",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthLogoutResponse,
        )

    def retrieve_current_user(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthRetrieveCurrentUserResponse:
        """Get authenticated user information from session"""
        return self._get(
            "/auth/me",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthRetrieveCurrentUserResponse,
        )


class AsyncAuthResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAuthResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/atulgavandetzafon/computer-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAuthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAuthResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/atulgavandetzafon/computer-python#with_streaming_response
        """
        return AsyncAuthResourceWithStreamingResponse(self)

    async def handle_callback(
        self,
        *,
        code: str,
        state: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthHandleCallbackResponse:
        """
        Handle OAuth callback from WorkOS AuthKit and exchange code for user profile

        Args:
          code: Authorization code (valid for 10 minutes)

          state: State parameter for CSRF protection

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/auth/callback",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "code": code,
                        "state": state,
                    },
                    auth_handle_callback_params.AuthHandleCallbackParams,
                ),
            ),
            cast_to=AuthHandleCallbackResponse,
        )

    async def initiate_login(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Redirect to WorkOS AuthKit for authentication"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/auth/login",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def logout(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthLogoutResponse:
        """Revoke user session and clear cookies"""
        return await self._post(
            "/auth/logout",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthLogoutResponse,
        )

    async def retrieve_current_user(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthRetrieveCurrentUserResponse:
        """Get authenticated user information from session"""
        return await self._get(
            "/auth/me",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthRetrieveCurrentUserResponse,
        )


class AuthResourceWithRawResponse:
    def __init__(self, auth: AuthResource) -> None:
        self._auth = auth

        self.handle_callback = to_raw_response_wrapper(
            auth.handle_callback,
        )
        self.initiate_login = to_raw_response_wrapper(
            auth.initiate_login,
        )
        self.logout = to_raw_response_wrapper(
            auth.logout,
        )
        self.retrieve_current_user = to_raw_response_wrapper(
            auth.retrieve_current_user,
        )


class AsyncAuthResourceWithRawResponse:
    def __init__(self, auth: AsyncAuthResource) -> None:
        self._auth = auth

        self.handle_callback = async_to_raw_response_wrapper(
            auth.handle_callback,
        )
        self.initiate_login = async_to_raw_response_wrapper(
            auth.initiate_login,
        )
        self.logout = async_to_raw_response_wrapper(
            auth.logout,
        )
        self.retrieve_current_user = async_to_raw_response_wrapper(
            auth.retrieve_current_user,
        )


class AuthResourceWithStreamingResponse:
    def __init__(self, auth: AuthResource) -> None:
        self._auth = auth

        self.handle_callback = to_streamed_response_wrapper(
            auth.handle_callback,
        )
        self.initiate_login = to_streamed_response_wrapper(
            auth.initiate_login,
        )
        self.logout = to_streamed_response_wrapper(
            auth.logout,
        )
        self.retrieve_current_user = to_streamed_response_wrapper(
            auth.retrieve_current_user,
        )


class AsyncAuthResourceWithStreamingResponse:
    def __init__(self, auth: AsyncAuthResource) -> None:
        self._auth = auth

        self.handle_callback = async_to_streamed_response_wrapper(
            auth.handle_callback,
        )
        self.initiate_login = async_to_streamed_response_wrapper(
            auth.initiate_login,
        )
        self.logout = async_to_streamed_response_wrapper(
            auth.logout,
        )
        self.retrieve_current_user = async_to_streamed_response_wrapper(
            auth.retrieve_current_user,
        )
