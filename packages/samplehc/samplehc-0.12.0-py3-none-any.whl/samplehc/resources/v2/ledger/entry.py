# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, strip_not_given, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.ledger import entry_post_params, entry_reverse_params
from ....types.v2.ledger.entry_post_response import EntryPostResponse
from ....types.v2.ledger.entry_reverse_response import EntryReverseResponse

__all__ = ["EntryResource", "AsyncEntryResource"]


class EntryResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EntryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return EntryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EntryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return EntryResourceWithStreamingResponse(self)

    def post(
        self,
        *,
        amount_usd_cents: float,
        entry_category: Literal["charge", "payment", "adjustment"],
        line_item_id: str,
        order_id: str,
        description: str | Omit = omit,
        entry_type: Union[
            Literal[
                "insurance-payment",
                "institution-payment",
                "patient-payment",
                "write-off",
                "institution-discount",
                "contracted-payer-adjustment",
                "patient-pay-adjustment",
                "charge",
                "payment",
                "adjustment",
            ],
            object,
        ]
        | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        payment_source: str | Omit = omit,
        posted_at: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EntryPostResponse:
        """
        Create diagnostics ledger entry

        Args:
          amount_usd_cents: The amount of the ledger entry in cents. Positive for charges, negative for
              payments.

          line_item_id: The line item ID associated with the ledger entry.

          order_id: The order ID associated with the ledger entry.

          description: The description of the ledger entry.

          entry_type: The type of ledger entry.

          metadata: Any optional metadata to associate with the ledger entry.

          payment_source: The source of the payment, e.g. payer ID, patient ID, etc.

          posted_at: The date and time the ledger entry was posted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"idempotency-key": idempotency_key}), **(extra_headers or {})}
        return self._post(
            "/api/v2/ledger/entry",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "entry_category": entry_category,
                    "line_item_id": line_item_id,
                    "order_id": order_id,
                    "description": description,
                    "entry_type": entry_type,
                    "metadata": metadata,
                    "payment_source": payment_source,
                    "posted_at": posted_at,
                },
                entry_post_params.EntryPostParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntryPostResponse,
        )

    def reverse(
        self,
        id: str,
        *,
        metadata: Dict[str, object] | Omit = omit,
        posted_at: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EntryReverseResponse:
        """
        Reverse diagnostics ledger entry

        Args:
          metadata: Any optional metadata to associate with the reversal entry.

          posted_at: The date and time the reversal entry was posted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/api/v2/ledger/entry/{id}/reverse",
            body=maybe_transform(
                {
                    "metadata": metadata,
                    "posted_at": posted_at,
                },
                entry_reverse_params.EntryReverseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntryReverseResponse,
        )


class AsyncEntryResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEntryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEntryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEntryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncEntryResourceWithStreamingResponse(self)

    async def post(
        self,
        *,
        amount_usd_cents: float,
        entry_category: Literal["charge", "payment", "adjustment"],
        line_item_id: str,
        order_id: str,
        description: str | Omit = omit,
        entry_type: Union[
            Literal[
                "insurance-payment",
                "institution-payment",
                "patient-payment",
                "write-off",
                "institution-discount",
                "contracted-payer-adjustment",
                "patient-pay-adjustment",
                "charge",
                "payment",
                "adjustment",
            ],
            object,
        ]
        | Omit = omit,
        metadata: Dict[str, object] | Omit = omit,
        payment_source: str | Omit = omit,
        posted_at: str | Omit = omit,
        idempotency_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EntryPostResponse:
        """
        Create diagnostics ledger entry

        Args:
          amount_usd_cents: The amount of the ledger entry in cents. Positive for charges, negative for
              payments.

          line_item_id: The line item ID associated with the ledger entry.

          order_id: The order ID associated with the ledger entry.

          description: The description of the ledger entry.

          entry_type: The type of ledger entry.

          metadata: Any optional metadata to associate with the ledger entry.

          payment_source: The source of the payment, e.g. payer ID, patient ID, etc.

          posted_at: The date and time the ledger entry was posted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"idempotency-key": idempotency_key}), **(extra_headers or {})}
        return await self._post(
            "/api/v2/ledger/entry",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "entry_category": entry_category,
                    "line_item_id": line_item_id,
                    "order_id": order_id,
                    "description": description,
                    "entry_type": entry_type,
                    "metadata": metadata,
                    "payment_source": payment_source,
                    "posted_at": posted_at,
                },
                entry_post_params.EntryPostParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntryPostResponse,
        )

    async def reverse(
        self,
        id: str,
        *,
        metadata: Dict[str, object] | Omit = omit,
        posted_at: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EntryReverseResponse:
        """
        Reverse diagnostics ledger entry

        Args:
          metadata: Any optional metadata to associate with the reversal entry.

          posted_at: The date and time the reversal entry was posted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/api/v2/ledger/entry/{id}/reverse",
            body=await async_maybe_transform(
                {
                    "metadata": metadata,
                    "posted_at": posted_at,
                },
                entry_reverse_params.EntryReverseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntryReverseResponse,
        )


class EntryResourceWithRawResponse:
    def __init__(self, entry: EntryResource) -> None:
        self._entry = entry

        self.post = to_raw_response_wrapper(
            entry.post,
        )
        self.reverse = to_raw_response_wrapper(
            entry.reverse,
        )


class AsyncEntryResourceWithRawResponse:
    def __init__(self, entry: AsyncEntryResource) -> None:
        self._entry = entry

        self.post = async_to_raw_response_wrapper(
            entry.post,
        )
        self.reverse = async_to_raw_response_wrapper(
            entry.reverse,
        )


class EntryResourceWithStreamingResponse:
    def __init__(self, entry: EntryResource) -> None:
        self._entry = entry

        self.post = to_streamed_response_wrapper(
            entry.post,
        )
        self.reverse = to_streamed_response_wrapper(
            entry.reverse,
        )


class AsyncEntryResourceWithStreamingResponse:
    def __init__(self, entry: AsyncEntryResource) -> None:
        self._entry = entry

        self.post = async_to_streamed_response_wrapper(
            entry.post,
        )
        self.reverse = async_to_streamed_response_wrapper(
            entry.reverse,
        )
