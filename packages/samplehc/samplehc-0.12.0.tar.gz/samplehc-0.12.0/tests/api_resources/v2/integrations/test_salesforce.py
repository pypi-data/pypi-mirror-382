# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSalesforce:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_crud_action(self, client: SampleHealthcare) -> None:
        salesforce = client.v2.integrations.salesforce.run_crud_action(
            slug="slug",
            crud_action_type="create",
            resource_type="resourceType",
        )
        assert_matches_type(object, salesforce, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_crud_action_with_all_params(self, client: SampleHealthcare) -> None:
        salesforce = client.v2.integrations.salesforce.run_crud_action(
            slug="slug",
            crud_action_type="create",
            resource_type="resourceType",
            resource_body={"foo": "bar"},
            resource_id="resourceId",
        )
        assert_matches_type(object, salesforce, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_run_crud_action(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.salesforce.with_raw_response.run_crud_action(
            slug="slug",
            crud_action_type="create",
            resource_type="resourceType",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        salesforce = response.parse()
        assert_matches_type(object, salesforce, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_run_crud_action(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.salesforce.with_streaming_response.run_crud_action(
            slug="slug",
            crud_action_type="create",
            resource_type="resourceType",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            salesforce = response.parse()
            assert_matches_type(object, salesforce, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_run_crud_action(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.salesforce.with_raw_response.run_crud_action(
                slug="",
                crud_action_type="create",
                resource_type="resourceType",
            )


class TestAsyncSalesforce:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_crud_action(self, async_client: AsyncSampleHealthcare) -> None:
        salesforce = await async_client.v2.integrations.salesforce.run_crud_action(
            slug="slug",
            crud_action_type="create",
            resource_type="resourceType",
        )
        assert_matches_type(object, salesforce, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_crud_action_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        salesforce = await async_client.v2.integrations.salesforce.run_crud_action(
            slug="slug",
            crud_action_type="create",
            resource_type="resourceType",
            resource_body={"foo": "bar"},
            resource_id="resourceId",
        )
        assert_matches_type(object, salesforce, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_run_crud_action(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.salesforce.with_raw_response.run_crud_action(
            slug="slug",
            crud_action_type="create",
            resource_type="resourceType",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        salesforce = await response.parse()
        assert_matches_type(object, salesforce, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_run_crud_action(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.salesforce.with_streaming_response.run_crud_action(
            slug="slug",
            crud_action_type="create",
            resource_type="resourceType",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            salesforce = await response.parse()
            assert_matches_type(object, salesforce, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_run_crud_action(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.salesforce.with_raw_response.run_crud_action(
                slug="",
                crud_action_type="create",
                resource_type="resourceType",
            )
