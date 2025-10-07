# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.coins import market_chart_get_params, market_chart_get_range_params
from ..._base_client import make_request_options
from ...types.coins.market_chart_get_response import MarketChartGetResponse
from ...types.coins.market_chart_get_range_response import MarketChartGetRangeResponse

__all__ = ["MarketChartResource", "AsyncMarketChartResource"]


class MarketChartResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MarketChartResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/coingecko/coingecko-python#accessing-raw-response-data-eg-headers
        """
        return MarketChartResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MarketChartResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/coingecko/coingecko-python#with_streaming_response
        """
        return MarketChartResourceWithStreamingResponse(self)

    def get(
        self,
        id: str,
        *,
        days: str,
        vs_currency: str,
        interval: Literal["5m", "hourly", "daily"] | Omit = omit,
        precision: Literal[
            "full",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MarketChartGetResponse:
        """
        This endpoint allows you to **get the historical chart data of a coin including
        time in UNIX, price, market cap and 24hr volume based on particular coin ID**

        Args:
          days: data up to number of days ago You may use any integer or `max` for number of
              days

          vs_currency: target currency of market data \\**refers to
              [`/simple/supported_vs_currencies`](/reference/simple-supported-currencies).

          interval: data interval, leave empty for auto granularity

          precision: decimal place for currency price value

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/coins/{id}/market_chart",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "days": days,
                        "vs_currency": vs_currency,
                        "interval": interval,
                        "precision": precision,
                    },
                    market_chart_get_params.MarketChartGetParams,
                ),
            ),
            cast_to=MarketChartGetResponse,
        )

    def get_range(
        self,
        id: str,
        *,
        from_: str,
        to: str,
        vs_currency: str,
        interval: Literal["5m", "hourly", "daily"] | Omit = omit,
        precision: Literal[
            "full",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MarketChartGetRangeResponse:
        """
        This endpoint allows you to **get the historical chart data of a coin within
        certain time range in UNIX along with price, market cap and 24hr volume based on
        particular coin ID**

        Args:
          from_: starting date in ISO date string (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`) or UNIX
              timestamp. **use ISO date string for best compatibility**

          to: ending date in ISO date string (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`) or UNIX
              timestamp. **use ISO date string for best compatibility**

          vs_currency: target currency of market data \\**refers to
              [`/simple/supported_vs_currencies`](/reference/simple-supported-currencies).

          interval: data interval, leave empty for auto granularity

          precision: decimal place for currency price value

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/coins/{id}/market_chart/range",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "from_": from_,
                        "to": to,
                        "vs_currency": vs_currency,
                        "interval": interval,
                        "precision": precision,
                    },
                    market_chart_get_range_params.MarketChartGetRangeParams,
                ),
            ),
            cast_to=MarketChartGetRangeResponse,
        )


class AsyncMarketChartResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMarketChartResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/coingecko/coingecko-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMarketChartResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMarketChartResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/coingecko/coingecko-python#with_streaming_response
        """
        return AsyncMarketChartResourceWithStreamingResponse(self)

    async def get(
        self,
        id: str,
        *,
        days: str,
        vs_currency: str,
        interval: Literal["5m", "hourly", "daily"] | Omit = omit,
        precision: Literal[
            "full",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MarketChartGetResponse:
        """
        This endpoint allows you to **get the historical chart data of a coin including
        time in UNIX, price, market cap and 24hr volume based on particular coin ID**

        Args:
          days: data up to number of days ago You may use any integer or `max` for number of
              days

          vs_currency: target currency of market data \\**refers to
              [`/simple/supported_vs_currencies`](/reference/simple-supported-currencies).

          interval: data interval, leave empty for auto granularity

          precision: decimal place for currency price value

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/coins/{id}/market_chart",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "days": days,
                        "vs_currency": vs_currency,
                        "interval": interval,
                        "precision": precision,
                    },
                    market_chart_get_params.MarketChartGetParams,
                ),
            ),
            cast_to=MarketChartGetResponse,
        )

    async def get_range(
        self,
        id: str,
        *,
        from_: str,
        to: str,
        vs_currency: str,
        interval: Literal["5m", "hourly", "daily"] | Omit = omit,
        precision: Literal[
            "full",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MarketChartGetRangeResponse:
        """
        This endpoint allows you to **get the historical chart data of a coin within
        certain time range in UNIX along with price, market cap and 24hr volume based on
        particular coin ID**

        Args:
          from_: starting date in ISO date string (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`) or UNIX
              timestamp. **use ISO date string for best compatibility**

          to: ending date in ISO date string (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`) or UNIX
              timestamp. **use ISO date string for best compatibility**

          vs_currency: target currency of market data \\**refers to
              [`/simple/supported_vs_currencies`](/reference/simple-supported-currencies).

          interval: data interval, leave empty for auto granularity

          precision: decimal place for currency price value

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/coins/{id}/market_chart/range",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "from_": from_,
                        "to": to,
                        "vs_currency": vs_currency,
                        "interval": interval,
                        "precision": precision,
                    },
                    market_chart_get_range_params.MarketChartGetRangeParams,
                ),
            ),
            cast_to=MarketChartGetRangeResponse,
        )


class MarketChartResourceWithRawResponse:
    def __init__(self, market_chart: MarketChartResource) -> None:
        self._market_chart = market_chart

        self.get = to_raw_response_wrapper(
            market_chart.get,
        )
        self.get_range = to_raw_response_wrapper(
            market_chart.get_range,
        )


class AsyncMarketChartResourceWithRawResponse:
    def __init__(self, market_chart: AsyncMarketChartResource) -> None:
        self._market_chart = market_chart

        self.get = async_to_raw_response_wrapper(
            market_chart.get,
        )
        self.get_range = async_to_raw_response_wrapper(
            market_chart.get_range,
        )


class MarketChartResourceWithStreamingResponse:
    def __init__(self, market_chart: MarketChartResource) -> None:
        self._market_chart = market_chart

        self.get = to_streamed_response_wrapper(
            market_chart.get,
        )
        self.get_range = to_streamed_response_wrapper(
            market_chart.get_range,
        )


class AsyncMarketChartResourceWithStreamingResponse:
    def __init__(self, market_chart: AsyncMarketChartResource) -> None:
        self._market_chart = market_chart

        self.get = async_to_streamed_response_wrapper(
            market_chart.get,
        )
        self.get_range = async_to_streamed_response_wrapper(
            market_chart.get_range,
        )
