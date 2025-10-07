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
from ..._base_client import make_request_options
from ...types.exchanges import ticker_get_params
from ...types.exchanges.ticker_get_response import TickerGetResponse

__all__ = ["TickersResource", "AsyncTickersResource"]


class TickersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TickersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/coingecko/coingecko-python#accessing-raw-response-data-eg-headers
        """
        return TickersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TickersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/coingecko/coingecko-python#with_streaming_response
        """
        return TickersResourceWithStreamingResponse(self)

    def get(
        self,
        id: str,
        *,
        coin_ids: str | Omit = omit,
        depth: bool | Omit = omit,
        dex_pair_format: Literal["contract_address", "symbol"] | Omit = omit,
        include_exchange_logo: bool | Omit = omit,
        order: Literal[
            "market_cap_asc",
            "market_cap_desc",
            "trust_score_desc",
            "trust_score_asc",
            "volume_desc",
            "volume_asc",
            "base_target",
        ]
        | Omit = omit,
        page: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TickerGetResponse:
        """
        This endpoint allows you to **query exchange's tickers based on exchange's ID**

        Args:
          coin_ids: filter tickers by coin IDs, comma-separated if querying more than 1 coin
              \\**refers to [`/coins/list`](/reference/coins-list).

          depth: include 2% orderbook depth (Example: cost_to_move_up_usd &
              cost_to_move_down_usd),default: false

          dex_pair_format:
              set to `symbol` to display DEX pair base and target as symbols, default:
              `contract_address`

          include_exchange_logo: include exchange logo, default: false

          order: use this to sort the order of responses, default: trust_score_desc

          page: page through results

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/exchanges/{id}/tickers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "coin_ids": coin_ids,
                        "depth": depth,
                        "dex_pair_format": dex_pair_format,
                        "include_exchange_logo": include_exchange_logo,
                        "order": order,
                        "page": page,
                    },
                    ticker_get_params.TickerGetParams,
                ),
            ),
            cast_to=TickerGetResponse,
        )


class AsyncTickersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTickersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/coingecko/coingecko-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTickersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTickersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/coingecko/coingecko-python#with_streaming_response
        """
        return AsyncTickersResourceWithStreamingResponse(self)

    async def get(
        self,
        id: str,
        *,
        coin_ids: str | Omit = omit,
        depth: bool | Omit = omit,
        dex_pair_format: Literal["contract_address", "symbol"] | Omit = omit,
        include_exchange_logo: bool | Omit = omit,
        order: Literal[
            "market_cap_asc",
            "market_cap_desc",
            "trust_score_desc",
            "trust_score_asc",
            "volume_desc",
            "volume_asc",
            "base_target",
        ]
        | Omit = omit,
        page: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TickerGetResponse:
        """
        This endpoint allows you to **query exchange's tickers based on exchange's ID**

        Args:
          coin_ids: filter tickers by coin IDs, comma-separated if querying more than 1 coin
              \\**refers to [`/coins/list`](/reference/coins-list).

          depth: include 2% orderbook depth (Example: cost_to_move_up_usd &
              cost_to_move_down_usd),default: false

          dex_pair_format:
              set to `symbol` to display DEX pair base and target as symbols, default:
              `contract_address`

          include_exchange_logo: include exchange logo, default: false

          order: use this to sort the order of responses, default: trust_score_desc

          page: page through results

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/exchanges/{id}/tickers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "coin_ids": coin_ids,
                        "depth": depth,
                        "dex_pair_format": dex_pair_format,
                        "include_exchange_logo": include_exchange_logo,
                        "order": order,
                        "page": page,
                    },
                    ticker_get_params.TickerGetParams,
                ),
            ),
            cast_to=TickerGetResponse,
        )


class TickersResourceWithRawResponse:
    def __init__(self, tickers: TickersResource) -> None:
        self._tickers = tickers

        self.get = to_raw_response_wrapper(
            tickers.get,
        )


class AsyncTickersResourceWithRawResponse:
    def __init__(self, tickers: AsyncTickersResource) -> None:
        self._tickers = tickers

        self.get = async_to_raw_response_wrapper(
            tickers.get,
        )


class TickersResourceWithStreamingResponse:
    def __init__(self, tickers: TickersResource) -> None:
        self._tickers = tickers

        self.get = to_streamed_response_wrapper(
            tickers.get,
        )


class AsyncTickersResourceWithStreamingResponse:
    def __init__(self, tickers: AsyncTickersResource) -> None:
        self._tickers = tickers

        self.get = async_to_streamed_response_wrapper(
            tickers.get,
        )
