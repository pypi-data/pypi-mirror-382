# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.browser_agents.runs import HelpRequestResolveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHelpRequests:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_resolve(self, client: SampleHealthcare) -> None:
        help_request = client.v2.browser_agents.runs.help_requests.resolve(
            help_request_id="helpRequestId",
            slug="slug",
            browser_agent_run_id="browserAgentRunId",
            resolution="resolution",
        )
        assert_matches_type(HelpRequestResolveResponse, help_request, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_resolve(self, client: SampleHealthcare) -> None:
        response = client.v2.browser_agents.runs.help_requests.with_raw_response.resolve(
            help_request_id="helpRequestId",
            slug="slug",
            browser_agent_run_id="browserAgentRunId",
            resolution="resolution",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        help_request = response.parse()
        assert_matches_type(HelpRequestResolveResponse, help_request, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_resolve(self, client: SampleHealthcare) -> None:
        with client.v2.browser_agents.runs.help_requests.with_streaming_response.resolve(
            help_request_id="helpRequestId",
            slug="slug",
            browser_agent_run_id="browserAgentRunId",
            resolution="resolution",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            help_request = response.parse()
            assert_matches_type(HelpRequestResolveResponse, help_request, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_resolve(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.browser_agents.runs.help_requests.with_raw_response.resolve(
                help_request_id="helpRequestId",
                slug="",
                browser_agent_run_id="browserAgentRunId",
                resolution="resolution",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_agent_run_id` but received ''"):
            client.v2.browser_agents.runs.help_requests.with_raw_response.resolve(
                help_request_id="helpRequestId",
                slug="slug",
                browser_agent_run_id="",
                resolution="resolution",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `help_request_id` but received ''"):
            client.v2.browser_agents.runs.help_requests.with_raw_response.resolve(
                help_request_id="",
                slug="slug",
                browser_agent_run_id="browserAgentRunId",
                resolution="resolution",
            )


class TestAsyncHelpRequests:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_resolve(self, async_client: AsyncSampleHealthcare) -> None:
        help_request = await async_client.v2.browser_agents.runs.help_requests.resolve(
            help_request_id="helpRequestId",
            slug="slug",
            browser_agent_run_id="browserAgentRunId",
            resolution="resolution",
        )
        assert_matches_type(HelpRequestResolveResponse, help_request, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_resolve(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.browser_agents.runs.help_requests.with_raw_response.resolve(
            help_request_id="helpRequestId",
            slug="slug",
            browser_agent_run_id="browserAgentRunId",
            resolution="resolution",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        help_request = await response.parse()
        assert_matches_type(HelpRequestResolveResponse, help_request, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_resolve(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.browser_agents.runs.help_requests.with_streaming_response.resolve(
            help_request_id="helpRequestId",
            slug="slug",
            browser_agent_run_id="browserAgentRunId",
            resolution="resolution",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            help_request = await response.parse()
            assert_matches_type(HelpRequestResolveResponse, help_request, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_resolve(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.browser_agents.runs.help_requests.with_raw_response.resolve(
                help_request_id="helpRequestId",
                slug="",
                browser_agent_run_id="browserAgentRunId",
                resolution="resolution",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_agent_run_id` but received ''"):
            await async_client.v2.browser_agents.runs.help_requests.with_raw_response.resolve(
                help_request_id="helpRequestId",
                slug="slug",
                browser_agent_run_id="",
                resolution="resolution",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `help_request_id` but received ''"):
            await async_client.v2.browser_agents.runs.help_requests.with_raw_response.resolve(
                help_request_id="",
                slug="slug",
                browser_agent_run_id="browserAgentRunId",
                resolution="resolution",
            )
