# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .entry import (
    EntryResource,
    AsyncEntryResource,
    EntryResourceWithRawResponse,
    AsyncEntryResourceWithRawResponse,
    EntryResourceWithStreamingResponse,
    AsyncEntryResourceWithStreamingResponse,
)
from .account import (
    AccountResource,
    AsyncAccountResource,
    AccountResourceWithRawResponse,
    AsyncAccountResourceWithRawResponse,
    AccountResourceWithStreamingResponse,
    AsyncAccountResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["LedgerResource", "AsyncLedgerResource"]


class LedgerResource(SyncAPIResource):
    @cached_property
    def entry(self) -> EntryResource:
        return EntryResource(self._client)

    @cached_property
    def account(self) -> AccountResource:
        return AccountResource(self._client)

    @cached_property
    def with_raw_response(self) -> LedgerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return LedgerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LedgerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return LedgerResourceWithStreamingResponse(self)


class AsyncLedgerResource(AsyncAPIResource):
    @cached_property
    def entry(self) -> AsyncEntryResource:
        return AsyncEntryResource(self._client)

    @cached_property
    def account(self) -> AsyncAccountResource:
        return AsyncAccountResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncLedgerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLedgerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLedgerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncLedgerResourceWithStreamingResponse(self)


class LedgerResourceWithRawResponse:
    def __init__(self, ledger: LedgerResource) -> None:
        self._ledger = ledger

    @cached_property
    def entry(self) -> EntryResourceWithRawResponse:
        return EntryResourceWithRawResponse(self._ledger.entry)

    @cached_property
    def account(self) -> AccountResourceWithRawResponse:
        return AccountResourceWithRawResponse(self._ledger.account)


class AsyncLedgerResourceWithRawResponse:
    def __init__(self, ledger: AsyncLedgerResource) -> None:
        self._ledger = ledger

    @cached_property
    def entry(self) -> AsyncEntryResourceWithRawResponse:
        return AsyncEntryResourceWithRawResponse(self._ledger.entry)

    @cached_property
    def account(self) -> AsyncAccountResourceWithRawResponse:
        return AsyncAccountResourceWithRawResponse(self._ledger.account)


class LedgerResourceWithStreamingResponse:
    def __init__(self, ledger: LedgerResource) -> None:
        self._ledger = ledger

    @cached_property
    def entry(self) -> EntryResourceWithStreamingResponse:
        return EntryResourceWithStreamingResponse(self._ledger.entry)

    @cached_property
    def account(self) -> AccountResourceWithStreamingResponse:
        return AccountResourceWithStreamingResponse(self._ledger.account)


class AsyncLedgerResourceWithStreamingResponse:
    def __init__(self, ledger: AsyncLedgerResource) -> None:
        self._ledger = ledger

    @cached_property
    def entry(self) -> AsyncEntryResourceWithStreamingResponse:
        return AsyncEntryResourceWithStreamingResponse(self._ledger.entry)

    @cached_property
    def account(self) -> AsyncAccountResourceWithStreamingResponse:
        return AsyncAccountResourceWithStreamingResponse(self._ledger.account)
