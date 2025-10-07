# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .xcures import (
    XcuresResource,
    AsyncXcuresResource,
    XcuresResourceWithRawResponse,
    AsyncXcuresResourceWithRawResponse,
    XcuresResourceWithStreamingResponse,
    AsyncXcuresResourceWithStreamingResponse,
)
from .careviso import (
    CarevisoResource,
    AsyncCarevisoResource,
    CarevisoResourceWithRawResponse,
    AsyncCarevisoResourceWithRawResponse,
    CarevisoResourceWithStreamingResponse,
    AsyncCarevisoResourceWithStreamingResponse,
)
from .bank.bank import (
    BankResource,
    AsyncBankResource,
    BankResourceWithRawResponse,
    AsyncBankResourceWithRawResponse,
    BankResourceWithStreamingResponse,
    AsyncBankResourceWithStreamingResponse,
)
from .kno2.kno2 import (
    Kno2Resource,
    AsyncKno2Resource,
    Kno2ResourceWithRawResponse,
    AsyncKno2ResourceWithRawResponse,
    Kno2ResourceWithStreamingResponse,
    AsyncKno2ResourceWithStreamingResponse,
)
from .snowflake import (
    SnowflakeResource,
    AsyncSnowflakeResource,
    SnowflakeResourceWithRawResponse,
    AsyncSnowflakeResourceWithRawResponse,
    SnowflakeResourceWithStreamingResponse,
    AsyncSnowflakeResourceWithStreamingResponse,
)
from ...._compat import cached_property
from .salesforce import (
    SalesforceResource,
    AsyncSalesforceResource,
    SalesforceResourceWithRawResponse,
    AsyncSalesforceResourceWithRawResponse,
    SalesforceResourceWithStreamingResponse,
    AsyncSalesforceResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from .glidian.glidian import (
    GlidianResource,
    AsyncGlidianResource,
    GlidianResourceWithRawResponse,
    AsyncGlidianResourceWithRawResponse,
    GlidianResourceWithStreamingResponse,
    AsyncGlidianResourceWithStreamingResponse,
)

__all__ = ["IntegrationsResource", "AsyncIntegrationsResource"]


class IntegrationsResource(SyncAPIResource):
    @cached_property
    def snowflake(self) -> SnowflakeResource:
        return SnowflakeResource(self._client)

    @cached_property
    def bank(self) -> BankResource:
        return BankResource(self._client)

    @cached_property
    def careviso(self) -> CarevisoResource:
        return CarevisoResource(self._client)

    @cached_property
    def kno2(self) -> Kno2Resource:
        return Kno2Resource(self._client)

    @cached_property
    def glidian(self) -> GlidianResource:
        return GlidianResource(self._client)

    @cached_property
    def xcures(self) -> XcuresResource:
        return XcuresResource(self._client)

    @cached_property
    def salesforce(self) -> SalesforceResource:
        return SalesforceResource(self._client)

    @cached_property
    def with_raw_response(self) -> IntegrationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return IntegrationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IntegrationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return IntegrationsResourceWithStreamingResponse(self)


class AsyncIntegrationsResource(AsyncAPIResource):
    @cached_property
    def snowflake(self) -> AsyncSnowflakeResource:
        return AsyncSnowflakeResource(self._client)

    @cached_property
    def bank(self) -> AsyncBankResource:
        return AsyncBankResource(self._client)

    @cached_property
    def careviso(self) -> AsyncCarevisoResource:
        return AsyncCarevisoResource(self._client)

    @cached_property
    def kno2(self) -> AsyncKno2Resource:
        return AsyncKno2Resource(self._client)

    @cached_property
    def glidian(self) -> AsyncGlidianResource:
        return AsyncGlidianResource(self._client)

    @cached_property
    def xcures(self) -> AsyncXcuresResource:
        return AsyncXcuresResource(self._client)

    @cached_property
    def salesforce(self) -> AsyncSalesforceResource:
        return AsyncSalesforceResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncIntegrationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIntegrationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIntegrationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncIntegrationsResourceWithStreamingResponse(self)


class IntegrationsResourceWithRawResponse:
    def __init__(self, integrations: IntegrationsResource) -> None:
        self._integrations = integrations

    @cached_property
    def snowflake(self) -> SnowflakeResourceWithRawResponse:
        return SnowflakeResourceWithRawResponse(self._integrations.snowflake)

    @cached_property
    def bank(self) -> BankResourceWithRawResponse:
        return BankResourceWithRawResponse(self._integrations.bank)

    @cached_property
    def careviso(self) -> CarevisoResourceWithRawResponse:
        return CarevisoResourceWithRawResponse(self._integrations.careviso)

    @cached_property
    def kno2(self) -> Kno2ResourceWithRawResponse:
        return Kno2ResourceWithRawResponse(self._integrations.kno2)

    @cached_property
    def glidian(self) -> GlidianResourceWithRawResponse:
        return GlidianResourceWithRawResponse(self._integrations.glidian)

    @cached_property
    def xcures(self) -> XcuresResourceWithRawResponse:
        return XcuresResourceWithRawResponse(self._integrations.xcures)

    @cached_property
    def salesforce(self) -> SalesforceResourceWithRawResponse:
        return SalesforceResourceWithRawResponse(self._integrations.salesforce)


class AsyncIntegrationsResourceWithRawResponse:
    def __init__(self, integrations: AsyncIntegrationsResource) -> None:
        self._integrations = integrations

    @cached_property
    def snowflake(self) -> AsyncSnowflakeResourceWithRawResponse:
        return AsyncSnowflakeResourceWithRawResponse(self._integrations.snowflake)

    @cached_property
    def bank(self) -> AsyncBankResourceWithRawResponse:
        return AsyncBankResourceWithRawResponse(self._integrations.bank)

    @cached_property
    def careviso(self) -> AsyncCarevisoResourceWithRawResponse:
        return AsyncCarevisoResourceWithRawResponse(self._integrations.careviso)

    @cached_property
    def kno2(self) -> AsyncKno2ResourceWithRawResponse:
        return AsyncKno2ResourceWithRawResponse(self._integrations.kno2)

    @cached_property
    def glidian(self) -> AsyncGlidianResourceWithRawResponse:
        return AsyncGlidianResourceWithRawResponse(self._integrations.glidian)

    @cached_property
    def xcures(self) -> AsyncXcuresResourceWithRawResponse:
        return AsyncXcuresResourceWithRawResponse(self._integrations.xcures)

    @cached_property
    def salesforce(self) -> AsyncSalesforceResourceWithRawResponse:
        return AsyncSalesforceResourceWithRawResponse(self._integrations.salesforce)


class IntegrationsResourceWithStreamingResponse:
    def __init__(self, integrations: IntegrationsResource) -> None:
        self._integrations = integrations

    @cached_property
    def snowflake(self) -> SnowflakeResourceWithStreamingResponse:
        return SnowflakeResourceWithStreamingResponse(self._integrations.snowflake)

    @cached_property
    def bank(self) -> BankResourceWithStreamingResponse:
        return BankResourceWithStreamingResponse(self._integrations.bank)

    @cached_property
    def careviso(self) -> CarevisoResourceWithStreamingResponse:
        return CarevisoResourceWithStreamingResponse(self._integrations.careviso)

    @cached_property
    def kno2(self) -> Kno2ResourceWithStreamingResponse:
        return Kno2ResourceWithStreamingResponse(self._integrations.kno2)

    @cached_property
    def glidian(self) -> GlidianResourceWithStreamingResponse:
        return GlidianResourceWithStreamingResponse(self._integrations.glidian)

    @cached_property
    def xcures(self) -> XcuresResourceWithStreamingResponse:
        return XcuresResourceWithStreamingResponse(self._integrations.xcures)

    @cached_property
    def salesforce(self) -> SalesforceResourceWithStreamingResponse:
        return SalesforceResourceWithStreamingResponse(self._integrations.salesforce)


class AsyncIntegrationsResourceWithStreamingResponse:
    def __init__(self, integrations: AsyncIntegrationsResource) -> None:
        self._integrations = integrations

    @cached_property
    def snowflake(self) -> AsyncSnowflakeResourceWithStreamingResponse:
        return AsyncSnowflakeResourceWithStreamingResponse(self._integrations.snowflake)

    @cached_property
    def bank(self) -> AsyncBankResourceWithStreamingResponse:
        return AsyncBankResourceWithStreamingResponse(self._integrations.bank)

    @cached_property
    def careviso(self) -> AsyncCarevisoResourceWithStreamingResponse:
        return AsyncCarevisoResourceWithStreamingResponse(self._integrations.careviso)

    @cached_property
    def kno2(self) -> AsyncKno2ResourceWithStreamingResponse:
        return AsyncKno2ResourceWithStreamingResponse(self._integrations.kno2)

    @cached_property
    def glidian(self) -> AsyncGlidianResourceWithStreamingResponse:
        return AsyncGlidianResourceWithStreamingResponse(self._integrations.glidian)

    @cached_property
    def xcures(self) -> AsyncXcuresResourceWithStreamingResponse:
        return AsyncXcuresResourceWithStreamingResponse(self._integrations.xcures)

    @cached_property
    def salesforce(self) -> AsyncSalesforceResourceWithStreamingResponse:
        return AsyncSalesforceResourceWithStreamingResponse(self._integrations.salesforce)
