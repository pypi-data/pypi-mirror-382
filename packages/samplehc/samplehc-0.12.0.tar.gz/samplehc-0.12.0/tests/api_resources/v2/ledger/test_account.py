# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.ledger import AccountWriteoffResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAccount:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_balance(self, client: SampleHealthcare) -> None:
        account = client.v2.ledger.account.get_balance(
            line_item_id="lineItemId",
            order_id="orderId",
        )
        assert account is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_balance(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.account.with_raw_response.get_balance(
            line_item_id="lineItemId",
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert account is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_balance(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.account.with_streaming_response.get_balance(
            line_item_id="lineItemId",
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert account is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_balance(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `order_id` but received ''"):
            client.v2.ledger.account.with_raw_response.get_balance(
                line_item_id="lineItemId",
                order_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `line_item_id` but received ''"):
            client.v2.ledger.account.with_raw_response.get_balance(
                line_item_id="",
                order_id="orderId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_writeoff(self, client: SampleHealthcare) -> None:
        account = client.v2.ledger.account.writeoff(
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
        )
        assert_matches_type(AccountWriteoffResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_writeoff_with_all_params(self, client: SampleHealthcare) -> None:
        account = client.v2.ledger.account.writeoff(
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
            metadata={"foo": "bar"},
            posted_at="postedAt",
        )
        assert_matches_type(AccountWriteoffResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_writeoff(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.account.with_raw_response.writeoff(
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(AccountWriteoffResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_writeoff(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.account.with_streaming_response.writeoff(
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(AccountWriteoffResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_writeoff(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `order_id` but received ''"):
            client.v2.ledger.account.with_raw_response.writeoff(
                line_item_id="lineItemId",
                order_id="",
                description="description",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `line_item_id` but received ''"):
            client.v2.ledger.account.with_raw_response.writeoff(
                line_item_id="",
                order_id="orderId",
                description="description",
            )


class TestAsyncAccount:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_balance(self, async_client: AsyncSampleHealthcare) -> None:
        account = await async_client.v2.ledger.account.get_balance(
            line_item_id="lineItemId",
            order_id="orderId",
        )
        assert account is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_balance(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.account.with_raw_response.get_balance(
            line_item_id="lineItemId",
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert account is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_balance(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.account.with_streaming_response.get_balance(
            line_item_id="lineItemId",
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert account is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_balance(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `order_id` but received ''"):
            await async_client.v2.ledger.account.with_raw_response.get_balance(
                line_item_id="lineItemId",
                order_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `line_item_id` but received ''"):
            await async_client.v2.ledger.account.with_raw_response.get_balance(
                line_item_id="",
                order_id="orderId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        account = await async_client.v2.ledger.account.writeoff(
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
        )
        assert_matches_type(AccountWriteoffResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_writeoff_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        account = await async_client.v2.ledger.account.writeoff(
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
            metadata={"foo": "bar"},
            posted_at="postedAt",
        )
        assert_matches_type(AccountWriteoffResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.account.with_raw_response.writeoff(
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(AccountWriteoffResponse, account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.account.with_streaming_response.writeoff(
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(AccountWriteoffResponse, account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `order_id` but received ''"):
            await async_client.v2.ledger.account.with_raw_response.writeoff(
                line_item_id="lineItemId",
                order_id="",
                description="description",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `line_item_id` but received ''"):
            await async_client.v2.ledger.account.with_raw_response.writeoff(
                line_item_id="",
                order_id="orderId",
                description="description",
            )
