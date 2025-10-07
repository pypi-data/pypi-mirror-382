# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from coingecko_sdk import Coingecko, AsyncCoingecko
from coingecko_sdk.types.coins import TickerGetResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTickers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Coingecko) -> None:
        ticker = client.coins.tickers.get(
            id="bitcoin",
        )
        assert_matches_type(TickerGetResponse, ticker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Coingecko) -> None:
        ticker = client.coins.tickers.get(
            id="bitcoin",
            depth=True,
            dex_pair_format="contract_address",
            exchange_ids="binance",
            include_exchange_logo=True,
            order="trust_score_desc",
            page=0,
        )
        assert_matches_type(TickerGetResponse, ticker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Coingecko) -> None:
        response = client.coins.tickers.with_raw_response.get(
            id="bitcoin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ticker = response.parse()
        assert_matches_type(TickerGetResponse, ticker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Coingecko) -> None:
        with client.coins.tickers.with_streaming_response.get(
            id="bitcoin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ticker = response.parse()
            assert_matches_type(TickerGetResponse, ticker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Coingecko) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.coins.tickers.with_raw_response.get(
                id="",
            )


class TestAsyncTickers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncCoingecko) -> None:
        ticker = await async_client.coins.tickers.get(
            id="bitcoin",
        )
        assert_matches_type(TickerGetResponse, ticker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncCoingecko) -> None:
        ticker = await async_client.coins.tickers.get(
            id="bitcoin",
            depth=True,
            dex_pair_format="contract_address",
            exchange_ids="binance",
            include_exchange_logo=True,
            order="trust_score_desc",
            page=0,
        )
        assert_matches_type(TickerGetResponse, ticker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncCoingecko) -> None:
        response = await async_client.coins.tickers.with_raw_response.get(
            id="bitcoin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ticker = await response.parse()
        assert_matches_type(TickerGetResponse, ticker, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncCoingecko) -> None:
        async with async_client.coins.tickers.with_streaming_response.get(
            id="bitcoin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ticker = await response.parse()
            assert_matches_type(TickerGetResponse, ticker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncCoingecko) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.coins.tickers.with_raw_response.get(
                id="",
            )
