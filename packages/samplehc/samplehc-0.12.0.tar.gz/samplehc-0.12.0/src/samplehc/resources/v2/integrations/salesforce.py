# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ....types.v2.integrations import salesforce_run_crud_action_params

__all__ = ["SalesforceResource", "AsyncSalesforceResource"]


class SalesforceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SalesforceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return SalesforceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SalesforceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return SalesforceResourceWithStreamingResponse(self)

    def run_crud_action(
        self,
        slug: str,
        *,
        crud_action_type: Literal["create", "update", "upsert", "delete", "retrieve"],
        resource_type: str,
        resource_body: Dict[str, object] | Omit = omit,
        resource_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Resolve connection by slug and run a CRUD action on a Salesforce sObject.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._post(
            f"/api/v2/integrations/salesforce/{slug}/crud-action",
            body=maybe_transform(
                {
                    "crud_action_type": crud_action_type,
                    "resource_type": resource_type,
                    "resource_body": resource_body,
                    "resource_id": resource_id,
                },
                salesforce_run_crud_action_params.SalesforceRunCrudActionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncSalesforceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSalesforceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSalesforceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSalesforceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncSalesforceResourceWithStreamingResponse(self)

    async def run_crud_action(
        self,
        slug: str,
        *,
        crud_action_type: Literal["create", "update", "upsert", "delete", "retrieve"],
        resource_type: str,
        resource_body: Dict[str, object] | Omit = omit,
        resource_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Resolve connection by slug and run a CRUD action on a Salesforce sObject.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._post(
            f"/api/v2/integrations/salesforce/{slug}/crud-action",
            body=await async_maybe_transform(
                {
                    "crud_action_type": crud_action_type,
                    "resource_type": resource_type,
                    "resource_body": resource_body,
                    "resource_id": resource_id,
                },
                salesforce_run_crud_action_params.SalesforceRunCrudActionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class SalesforceResourceWithRawResponse:
    def __init__(self, salesforce: SalesforceResource) -> None:
        self._salesforce = salesforce

        self.run_crud_action = to_raw_response_wrapper(
            salesforce.run_crud_action,
        )


class AsyncSalesforceResourceWithRawResponse:
    def __init__(self, salesforce: AsyncSalesforceResource) -> None:
        self._salesforce = salesforce

        self.run_crud_action = async_to_raw_response_wrapper(
            salesforce.run_crud_action,
        )


class SalesforceResourceWithStreamingResponse:
    def __init__(self, salesforce: SalesforceResource) -> None:
        self._salesforce = salesforce

        self.run_crud_action = to_streamed_response_wrapper(
            salesforce.run_crud_action,
        )


class AsyncSalesforceResourceWithStreamingResponse:
    def __init__(self, salesforce: AsyncSalesforceResource) -> None:
        self._salesforce = salesforce

        self.run_crud_action = async_to_streamed_response_wrapper(
            salesforce.run_crud_action,
        )
