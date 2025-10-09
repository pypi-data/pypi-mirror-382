# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    computer_create_params,
    computer_navigate_params,
    computer_execute_batch_params,
    computer_execute_action_params,
)
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
from ..types.action_result import ActionResult
from ..types.computer_response import ComputerResponse
from ..types.computer_list_response import ComputerListResponse
from ..types.computer_keep_alive_response import ComputerKeepAliveResponse
from ..types.computer_execute_batch_response import ComputerExecuteBatchResponse

__all__ = ["ComputersResource", "AsyncComputersResource"]


class ComputersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ComputersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/atulgavandetzafon/computer-python#accessing-raw-response-data-eg-headers
        """
        return ComputersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ComputersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/atulgavandetzafon/computer-python#with_streaming_response
        """
        return ComputersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        context_id: str | Omit = omit,
        display: computer_create_params.Display | Omit = omit,
        kind: str | Omit = omit,
        stealth: object | Omit = omit,
        timeout_seconds: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerResponse:
        """
        Create a new browser or desktop automation session

        Args:
          display: TODO: implement

          kind: "browser"|"desktop"|"code" etc

          stealth: TODO: implement

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/computers",
            body=maybe_transform(
                {
                    "context_id": context_id,
                    "display": display,
                    "kind": kind,
                    "stealth": stealth,
                    "timeout_seconds": timeout_seconds,
                },
                computer_create_params.ComputerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerResponse:
        """
        Get the current status of a computer instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/computers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerListResponse:
        """List all active computers for the user's organization"""
        return self._get(
            "/computers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerListResponse,
        )

    def execute_action(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Execute a single action (screenshot, click, type, navigate, )

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/execute",
            body=maybe_transform(body, computer_execute_action_params.ComputerExecuteActionParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def execute_batch(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerExecuteBatchResponse:
        """
        Execute a batch of actions in sequence, stopping on first error

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/batch",
            body=maybe_transform(body, computer_execute_batch_params.ComputerExecuteBatchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerExecuteBatchResponse,
        )

    def keep_alive(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerKeepAliveResponse:
        """
        Extend the timeout for a computer session

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/keepalive",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerKeepAliveResponse,
        )

    def navigate(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Navigate the browser to a specified URL

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/navigate",
            body=maybe_transform(body, computer_navigate_params.ComputerNavigateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def stream_events(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Stream real-time events using Server-Sent Events (SSE)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/computers/{id}/events",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def terminate(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Terminate and clean up a computer instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/computers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncComputersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncComputersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/atulgavandetzafon/computer-python#accessing-raw-response-data-eg-headers
        """
        return AsyncComputersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncComputersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/atulgavandetzafon/computer-python#with_streaming_response
        """
        return AsyncComputersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        context_id: str | Omit = omit,
        display: computer_create_params.Display | Omit = omit,
        kind: str | Omit = omit,
        stealth: object | Omit = omit,
        timeout_seconds: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerResponse:
        """
        Create a new browser or desktop automation session

        Args:
          display: TODO: implement

          kind: "browser"|"desktop"|"code" etc

          stealth: TODO: implement

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/computers",
            body=await async_maybe_transform(
                {
                    "context_id": context_id,
                    "display": display,
                    "kind": kind,
                    "stealth": stealth,
                    "timeout_seconds": timeout_seconds,
                },
                computer_create_params.ComputerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerResponse:
        """
        Get the current status of a computer instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/computers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerListResponse:
        """List all active computers for the user's organization"""
        return await self._get(
            "/computers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerListResponse,
        )

    async def execute_action(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Execute a single action (screenshot, click, type, navigate, )

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/execute",
            body=await async_maybe_transform(body, computer_execute_action_params.ComputerExecuteActionParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def execute_batch(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerExecuteBatchResponse:
        """
        Execute a batch of actions in sequence, stopping on first error

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/batch",
            body=await async_maybe_transform(body, computer_execute_batch_params.ComputerExecuteBatchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerExecuteBatchResponse,
        )

    async def keep_alive(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerKeepAliveResponse:
        """
        Extend the timeout for a computer session

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/keepalive",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerKeepAliveResponse,
        )

    async def navigate(
        self,
        id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Navigate the browser to a specified URL

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/navigate",
            body=await async_maybe_transform(body, computer_navigate_params.ComputerNavigateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def stream_events(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Stream real-time events using Server-Sent Events (SSE)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/computers/{id}/events",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def terminate(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Terminate and clean up a computer instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/computers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ComputersResourceWithRawResponse:
    def __init__(self, computers: ComputersResource) -> None:
        self._computers = computers

        self.create = to_raw_response_wrapper(
            computers.create,
        )
        self.retrieve = to_raw_response_wrapper(
            computers.retrieve,
        )
        self.list = to_raw_response_wrapper(
            computers.list,
        )
        self.execute_action = to_raw_response_wrapper(
            computers.execute_action,
        )
        self.execute_batch = to_raw_response_wrapper(
            computers.execute_batch,
        )
        self.keep_alive = to_raw_response_wrapper(
            computers.keep_alive,
        )
        self.navigate = to_raw_response_wrapper(
            computers.navigate,
        )
        self.stream_events = to_raw_response_wrapper(
            computers.stream_events,
        )
        self.terminate = to_raw_response_wrapper(
            computers.terminate,
        )


class AsyncComputersResourceWithRawResponse:
    def __init__(self, computers: AsyncComputersResource) -> None:
        self._computers = computers

        self.create = async_to_raw_response_wrapper(
            computers.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            computers.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            computers.list,
        )
        self.execute_action = async_to_raw_response_wrapper(
            computers.execute_action,
        )
        self.execute_batch = async_to_raw_response_wrapper(
            computers.execute_batch,
        )
        self.keep_alive = async_to_raw_response_wrapper(
            computers.keep_alive,
        )
        self.navigate = async_to_raw_response_wrapper(
            computers.navigate,
        )
        self.stream_events = async_to_raw_response_wrapper(
            computers.stream_events,
        )
        self.terminate = async_to_raw_response_wrapper(
            computers.terminate,
        )


class ComputersResourceWithStreamingResponse:
    def __init__(self, computers: ComputersResource) -> None:
        self._computers = computers

        self.create = to_streamed_response_wrapper(
            computers.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            computers.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            computers.list,
        )
        self.execute_action = to_streamed_response_wrapper(
            computers.execute_action,
        )
        self.execute_batch = to_streamed_response_wrapper(
            computers.execute_batch,
        )
        self.keep_alive = to_streamed_response_wrapper(
            computers.keep_alive,
        )
        self.navigate = to_streamed_response_wrapper(
            computers.navigate,
        )
        self.stream_events = to_streamed_response_wrapper(
            computers.stream_events,
        )
        self.terminate = to_streamed_response_wrapper(
            computers.terminate,
        )


class AsyncComputersResourceWithStreamingResponse:
    def __init__(self, computers: AsyncComputersResource) -> None:
        self._computers = computers

        self.create = async_to_streamed_response_wrapper(
            computers.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            computers.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            computers.list,
        )
        self.execute_action = async_to_streamed_response_wrapper(
            computers.execute_action,
        )
        self.execute_batch = async_to_streamed_response_wrapper(
            computers.execute_batch,
        )
        self.keep_alive = async_to_streamed_response_wrapper(
            computers.keep_alive,
        )
        self.navigate = async_to_streamed_response_wrapper(
            computers.navigate,
        )
        self.stream_events = async_to_streamed_response_wrapper(
            computers.stream_events,
        )
        self.terminate = async_to_streamed_response_wrapper(
            computers.terminate,
        )
