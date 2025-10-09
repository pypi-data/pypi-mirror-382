# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import test_list_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncOffsetPagination, AsyncOffsetPagination
from ..types.test import Test
from .._base_client import AsyncPaginator, make_request_options
from ..types.test_retrieve_response import TestRetrieveResponse

__all__ = ["TestsResource", "AsyncTestsResource"]


class TestsResource(SyncAPIResource):
    __test__ = False

    @cached_property
    def with_raw_response(self) -> TestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return TestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return TestsResourceWithStreamingResponse(self)

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
    ) -> TestRetrieveResponse:
        """
        Retrieves detailed information about a specific test.

        Args:
          id: The unique identifier of the test

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v0/tests/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestRetrieveResponse,
        )

    def list(
        self,
        *,
        limit: int | Omit = omit,
        order_by: str | Omit = omit,
        order_dir: Literal["asc", "desc"] | Omit = omit,
        skip: int | Omit = omit,
        status: str | Omit = omit,
        task_id: str | Omit = omit,
        trace_id: str | Omit = omit,
        type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncOffsetPagination[Test]:
        """
        Retrieves a paginated list of tests with optional filtering.

        Args:
          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          skip: Number of items to skip

          status: Filter by evaluation status

          task_id: Filter by task ID

          trace_id: Filter by trace ID

          type: Filter by evaluation type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/tests",
            page=SyncOffsetPagination[Test],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "skip": skip,
                        "status": status,
                        "task_id": task_id,
                        "trace_id": trace_id,
                        "type": type,
                    },
                    test_list_params.TestListParams,
                ),
            ),
            model=Test,
        )


class AsyncTestsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return AsyncTestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return AsyncTestsResourceWithStreamingResponse(self)

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
    ) -> TestRetrieveResponse:
        """
        Retrieves detailed information about a specific test.

        Args:
          id: The unique identifier of the test

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v0/tests/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestRetrieveResponse,
        )

    def list(
        self,
        *,
        limit: int | Omit = omit,
        order_by: str | Omit = omit,
        order_dir: Literal["asc", "desc"] | Omit = omit,
        skip: int | Omit = omit,
        status: str | Omit = omit,
        task_id: str | Omit = omit,
        trace_id: str | Omit = omit,
        type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Test, AsyncOffsetPagination[Test]]:
        """
        Retrieves a paginated list of tests with optional filtering.

        Args:
          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          skip: Number of items to skip

          status: Filter by evaluation status

          task_id: Filter by task ID

          trace_id: Filter by trace ID

          type: Filter by evaluation type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/tests",
            page=AsyncOffsetPagination[Test],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "skip": skip,
                        "status": status,
                        "task_id": task_id,
                        "trace_id": trace_id,
                        "type": type,
                    },
                    test_list_params.TestListParams,
                ),
            ),
            model=Test,
        )


class TestsResourceWithRawResponse:
    __test__ = False

    def __init__(self, tests: TestsResource) -> None:
        self._tests = tests

        self.retrieve = to_raw_response_wrapper(
            tests.retrieve,
        )
        self.list = to_raw_response_wrapper(
            tests.list,
        )


class AsyncTestsResourceWithRawResponse:
    def __init__(self, tests: AsyncTestsResource) -> None:
        self._tests = tests

        self.retrieve = async_to_raw_response_wrapper(
            tests.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            tests.list,
        )


class TestsResourceWithStreamingResponse:
    __test__ = False

    def __init__(self, tests: TestsResource) -> None:
        self._tests = tests

        self.retrieve = to_streamed_response_wrapper(
            tests.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            tests.list,
        )


class AsyncTestsResourceWithStreamingResponse:
    def __init__(self, tests: AsyncTestsResource) -> None:
        self._tests = tests

        self.retrieve = async_to_streamed_response_wrapper(
            tests.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            tests.list,
        )
