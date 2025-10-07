# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from coingecko_sdk import Coingecko, AsyncCoingecko
from coingecko_sdk.types.nfts import MarketChartGetResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMarketChart:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Coingecko) -> None:
        market_chart = client.nfts.market_chart.get(
            id="pudgy-penguins",
            days="days",
        )
        assert_matches_type(MarketChartGetResponse, market_chart, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Coingecko) -> None:
        response = client.nfts.market_chart.with_raw_response.get(
            id="pudgy-penguins",
            days="days",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        market_chart = response.parse()
        assert_matches_type(MarketChartGetResponse, market_chart, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Coingecko) -> None:
        with client.nfts.market_chart.with_streaming_response.get(
            id="pudgy-penguins",
            days="days",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            market_chart = response.parse()
            assert_matches_type(MarketChartGetResponse, market_chart, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Coingecko) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.nfts.market_chart.with_raw_response.get(
                id="",
                days="days",
            )


class TestAsyncMarketChart:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncCoingecko) -> None:
        market_chart = await async_client.nfts.market_chart.get(
            id="pudgy-penguins",
            days="days",
        )
        assert_matches_type(MarketChartGetResponse, market_chart, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncCoingecko) -> None:
        response = await async_client.nfts.market_chart.with_raw_response.get(
            id="pudgy-penguins",
            days="days",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        market_chart = await response.parse()
        assert_matches_type(MarketChartGetResponse, market_chart, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncCoingecko) -> None:
        async with async_client.nfts.market_chart.with_streaming_response.get(
            id="pudgy-penguins",
            days="days",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            market_chart = await response.parse()
            assert_matches_type(MarketChartGetResponse, market_chart, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncCoingecko) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.nfts.market_chart.with_raw_response.get(
                id="",
                days="days",
            )
