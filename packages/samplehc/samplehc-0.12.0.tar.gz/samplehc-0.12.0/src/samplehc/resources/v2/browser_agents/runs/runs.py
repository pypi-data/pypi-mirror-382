# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from .help_requests import (
    HelpRequestsResource,
    AsyncHelpRequestsResource,
    HelpRequestsResourceWithRawResponse,
    AsyncHelpRequestsResourceWithRawResponse,
    HelpRequestsResourceWithStreamingResponse,
    AsyncHelpRequestsResourceWithStreamingResponse,
)

__all__ = ["RunsResource", "AsyncRunsResource"]


class RunsResource(SyncAPIResource):
    @cached_property
    def help_requests(self) -> HelpRequestsResource:
        return HelpRequestsResource(self._client)

    @cached_property
    def with_raw_response(self) -> RunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return RunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return RunsResourceWithStreamingResponse(self)


class AsyncRunsResource(AsyncAPIResource):
    @cached_property
    def help_requests(self) -> AsyncHelpRequestsResource:
        return AsyncHelpRequestsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncRunsResourceWithStreamingResponse(self)


class RunsResourceWithRawResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

    @cached_property
    def help_requests(self) -> HelpRequestsResourceWithRawResponse:
        return HelpRequestsResourceWithRawResponse(self._runs.help_requests)


class AsyncRunsResourceWithRawResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

    @cached_property
    def help_requests(self) -> AsyncHelpRequestsResourceWithRawResponse:
        return AsyncHelpRequestsResourceWithRawResponse(self._runs.help_requests)


class RunsResourceWithStreamingResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

    @cached_property
    def help_requests(self) -> HelpRequestsResourceWithStreamingResponse:
        return HelpRequestsResourceWithStreamingResponse(self._runs.help_requests)


class AsyncRunsResourceWithStreamingResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

    @cached_property
    def help_requests(self) -> AsyncHelpRequestsResourceWithStreamingResponse:
        return AsyncHelpRequestsResourceWithStreamingResponse(self._runs.help_requests)
