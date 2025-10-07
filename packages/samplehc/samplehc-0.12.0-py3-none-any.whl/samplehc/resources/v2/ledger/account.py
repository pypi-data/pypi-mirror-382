# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.ledger import account_writeoff_params
from ....types.v2.ledger.account_writeoff_response import AccountWriteoffResponse

__all__ = ["AccountResource", "AsyncAccountResource"]


class AccountResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AccountResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AccountResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AccountResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AccountResourceWithStreamingResponse(self)

    def get_balance(
        self,
        line_item_id: str,
        *,
        order_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Get balance for a ledger account

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        if not line_item_id:
            raise ValueError(f"Expected a non-empty value for `line_item_id` but received {line_item_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/api/v2/ledger/account/{order_id}/line-item/{line_item_id}/balance",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def writeoff(
        self,
        line_item_id: str,
        *,
        order_id: str,
        description: str,
        metadata: Dict[str, object] | Omit = omit,
        posted_at: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountWriteoffResponse:
        """Writes off the remaining balance in an account on the ledger.

        Throws an error if
        the account contains a non-positive balance.

        Args:
          description: The description of the write-off.

          metadata: Any optional metadata to associate with the write-off.

          posted_at: The date and time to post the write-off.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        if not line_item_id:
            raise ValueError(f"Expected a non-empty value for `line_item_id` but received {line_item_id!r}")
        return self._post(
            f"/api/v2/ledger/account/{order_id}/line-item/{line_item_id}/writeoff",
            body=maybe_transform(
                {
                    "description": description,
                    "metadata": metadata,
                    "posted_at": posted_at,
                },
                account_writeoff_params.AccountWriteoffParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountWriteoffResponse,
        )


class AsyncAccountResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAccountResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAccountResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAccountResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncAccountResourceWithStreamingResponse(self)

    async def get_balance(
        self,
        line_item_id: str,
        *,
        order_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Get balance for a ledger account

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        if not line_item_id:
            raise ValueError(f"Expected a non-empty value for `line_item_id` but received {line_item_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/api/v2/ledger/account/{order_id}/line-item/{line_item_id}/balance",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def writeoff(
        self,
        line_item_id: str,
        *,
        order_id: str,
        description: str,
        metadata: Dict[str, object] | Omit = omit,
        posted_at: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountWriteoffResponse:
        """Writes off the remaining balance in an account on the ledger.

        Throws an error if
        the account contains a non-positive balance.

        Args:
          description: The description of the write-off.

          metadata: Any optional metadata to associate with the write-off.

          posted_at: The date and time to post the write-off.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        if not line_item_id:
            raise ValueError(f"Expected a non-empty value for `line_item_id` but received {line_item_id!r}")
        return await self._post(
            f"/api/v2/ledger/account/{order_id}/line-item/{line_item_id}/writeoff",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "metadata": metadata,
                    "posted_at": posted_at,
                },
                account_writeoff_params.AccountWriteoffParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AccountWriteoffResponse,
        )


class AccountResourceWithRawResponse:
    def __init__(self, account: AccountResource) -> None:
        self._account = account

        self.get_balance = to_raw_response_wrapper(
            account.get_balance,
        )
        self.writeoff = to_raw_response_wrapper(
            account.writeoff,
        )


class AsyncAccountResourceWithRawResponse:
    def __init__(self, account: AsyncAccountResource) -> None:
        self._account = account

        self.get_balance = async_to_raw_response_wrapper(
            account.get_balance,
        )
        self.writeoff = async_to_raw_response_wrapper(
            account.writeoff,
        )


class AccountResourceWithStreamingResponse:
    def __init__(self, account: AccountResource) -> None:
        self._account = account

        self.get_balance = to_streamed_response_wrapper(
            account.get_balance,
        )
        self.writeoff = to_streamed_response_wrapper(
            account.writeoff,
        )


class AsyncAccountResourceWithStreamingResponse:
    def __init__(self, account: AsyncAccountResource) -> None:
        self._account = account

        self.get_balance = async_to_streamed_response_wrapper(
            account.get_balance,
        )
        self.writeoff = async_to_streamed_response_wrapper(
            account.writeoff,
        )
