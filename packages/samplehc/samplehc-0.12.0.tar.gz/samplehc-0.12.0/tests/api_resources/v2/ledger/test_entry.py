# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.ledger import EntryPostResponse, EntryReverseResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEntry:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_post(self, client: SampleHealthcare) -> None:
        entry = client.v2.ledger.entry.post(
            amount_usd_cents=0,
            entry_category="charge",
            line_item_id="lineItemId",
            order_id="orderId",
        )
        assert_matches_type(EntryPostResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_post_with_all_params(self, client: SampleHealthcare) -> None:
        entry = client.v2.ledger.entry.post(
            amount_usd_cents=0,
            entry_category="charge",
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
            entry_type="insurance-payment",
            metadata={"foo": "bar"},
            payment_source="paymentSource",
            posted_at="postedAt",
            idempotency_key="idempotency-key",
        )
        assert_matches_type(EntryPostResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_post(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.entry.with_raw_response.post(
            amount_usd_cents=0,
            entry_category="charge",
            line_item_id="lineItemId",
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = response.parse()
        assert_matches_type(EntryPostResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_post(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.entry.with_streaming_response.post(
            amount_usd_cents=0,
            entry_category="charge",
            line_item_id="lineItemId",
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = response.parse()
            assert_matches_type(EntryPostResponse, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reverse(self, client: SampleHealthcare) -> None:
        entry = client.v2.ledger.entry.reverse(
            id="id",
        )
        assert_matches_type(EntryReverseResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reverse_with_all_params(self, client: SampleHealthcare) -> None:
        entry = client.v2.ledger.entry.reverse(
            id="id",
            metadata={"foo": "bar"},
            posted_at="postedAt",
        )
        assert_matches_type(EntryReverseResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reverse(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.entry.with_raw_response.reverse(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = response.parse()
        assert_matches_type(EntryReverseResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reverse(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.entry.with_streaming_response.reverse(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = response.parse()
            assert_matches_type(EntryReverseResponse, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_reverse(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.v2.ledger.entry.with_raw_response.reverse(
                id="",
            )


class TestAsyncEntry:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_post(self, async_client: AsyncSampleHealthcare) -> None:
        entry = await async_client.v2.ledger.entry.post(
            amount_usd_cents=0,
            entry_category="charge",
            line_item_id="lineItemId",
            order_id="orderId",
        )
        assert_matches_type(EntryPostResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_post_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        entry = await async_client.v2.ledger.entry.post(
            amount_usd_cents=0,
            entry_category="charge",
            line_item_id="lineItemId",
            order_id="orderId",
            description="description",
            entry_type="insurance-payment",
            metadata={"foo": "bar"},
            payment_source="paymentSource",
            posted_at="postedAt",
            idempotency_key="idempotency-key",
        )
        assert_matches_type(EntryPostResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_post(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.entry.with_raw_response.post(
            amount_usd_cents=0,
            entry_category="charge",
            line_item_id="lineItemId",
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = await response.parse()
        assert_matches_type(EntryPostResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_post(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.entry.with_streaming_response.post(
            amount_usd_cents=0,
            entry_category="charge",
            line_item_id="lineItemId",
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = await response.parse()
            assert_matches_type(EntryPostResponse, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reverse(self, async_client: AsyncSampleHealthcare) -> None:
        entry = await async_client.v2.ledger.entry.reverse(
            id="id",
        )
        assert_matches_type(EntryReverseResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reverse_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        entry = await async_client.v2.ledger.entry.reverse(
            id="id",
            metadata={"foo": "bar"},
            posted_at="postedAt",
        )
        assert_matches_type(EntryReverseResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reverse(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.entry.with_raw_response.reverse(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = await response.parse()
        assert_matches_type(EntryReverseResponse, entry, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reverse(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.entry.with_streaming_response.reverse(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = await response.parse()
            assert_matches_type(EntryReverseResponse, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_reverse(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.v2.ledger.entry.with_raw_response.reverse(
                id="",
            )
