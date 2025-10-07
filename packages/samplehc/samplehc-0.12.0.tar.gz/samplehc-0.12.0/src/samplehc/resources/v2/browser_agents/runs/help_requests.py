# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Query, Headers, NotGiven, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.v2.browser_agents.runs import help_request_resolve_params
from .....types.v2.browser_agents.runs.help_request_resolve_response import HelpRequestResolveResponse

__all__ = ["HelpRequestsResource", "AsyncHelpRequestsResource"]


class HelpRequestsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HelpRequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return HelpRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HelpRequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return HelpRequestsResourceWithStreamingResponse(self)

    def resolve(
        self,
        help_request_id: str,
        *,
        slug: str,
        browser_agent_run_id: str,
        resolution: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> HelpRequestResolveResponse:
        """
        Update the resolution and resolvedAt for a help request on a browser agent run.

        Args:
          resolution: Resolution details for the help request

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        if not browser_agent_run_id:
            raise ValueError(
                f"Expected a non-empty value for `browser_agent_run_id` but received {browser_agent_run_id!r}"
            )
        if not help_request_id:
            raise ValueError(f"Expected a non-empty value for `help_request_id` but received {help_request_id!r}")
        return self._patch(
            f"/api/v2/browser-agents/{slug}/runs/{browser_agent_run_id}/help-requests/{help_request_id}/resolution",
            body=maybe_transform({"resolution": resolution}, help_request_resolve_params.HelpRequestResolveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HelpRequestResolveResponse,
        )


class AsyncHelpRequestsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHelpRequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncHelpRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHelpRequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncHelpRequestsResourceWithStreamingResponse(self)

    async def resolve(
        self,
        help_request_id: str,
        *,
        slug: str,
        browser_agent_run_id: str,
        resolution: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> HelpRequestResolveResponse:
        """
        Update the resolution and resolvedAt for a help request on a browser agent run.

        Args:
          resolution: Resolution details for the help request

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        if not browser_agent_run_id:
            raise ValueError(
                f"Expected a non-empty value for `browser_agent_run_id` but received {browser_agent_run_id!r}"
            )
        if not help_request_id:
            raise ValueError(f"Expected a non-empty value for `help_request_id` but received {help_request_id!r}")
        return await self._patch(
            f"/api/v2/browser-agents/{slug}/runs/{browser_agent_run_id}/help-requests/{help_request_id}/resolution",
            body=await async_maybe_transform(
                {"resolution": resolution}, help_request_resolve_params.HelpRequestResolveParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HelpRequestResolveResponse,
        )


class HelpRequestsResourceWithRawResponse:
    def __init__(self, help_requests: HelpRequestsResource) -> None:
        self._help_requests = help_requests

        self.resolve = to_raw_response_wrapper(
            help_requests.resolve,
        )


class AsyncHelpRequestsResourceWithRawResponse:
    def __init__(self, help_requests: AsyncHelpRequestsResource) -> None:
        self._help_requests = help_requests

        self.resolve = async_to_raw_response_wrapper(
            help_requests.resolve,
        )


class HelpRequestsResourceWithStreamingResponse:
    def __init__(self, help_requests: HelpRequestsResource) -> None:
        self._help_requests = help_requests

        self.resolve = to_streamed_response_wrapper(
            help_requests.resolve,
        )


class AsyncHelpRequestsResourceWithStreamingResponse:
    def __init__(self, help_requests: AsyncHelpRequestsResource) -> None:
        self._help_requests = help_requests

        self.resolve = async_to_streamed_response_wrapper(
            help_requests.resolve,
        )
