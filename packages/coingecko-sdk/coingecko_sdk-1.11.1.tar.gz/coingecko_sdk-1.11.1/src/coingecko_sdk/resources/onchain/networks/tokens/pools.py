# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.onchain.networks.tokens import pool_get_params
from .....types.onchain.networks.tokens.pool_get_response import PoolGetResponse

__all__ = ["PoolsResource", "AsyncPoolsResource"]


class PoolsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PoolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/coingecko/coingecko-python#accessing-raw-response-data-eg-headers
        """
        return PoolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PoolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/coingecko/coingecko-python#with_streaming_response
        """
        return PoolsResourceWithStreamingResponse(self)

    def get(
        self,
        token_address: str,
        *,
        network: str,
        include: str | Omit = omit,
        page: int | Omit = omit,
        sort: Literal["h24_volume_usd_liquidity_desc", "h24_tx_count_desc", "h24_volume_usd_desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PoolGetResponse:
        """
        This endpoint allows you to **query top pools based on the provided token
        contract address on a network**

        Args:
          include: attributes to include, comma-separated if more than one to include Available
              values: `base_token`, `quote_token`, `dex`

          page: page through results Default value: 1

          sort: sort the pools by field Default value: h24_volume_usd_liquidity_desc

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not network:
            raise ValueError(f"Expected a non-empty value for `network` but received {network!r}")
        if not token_address:
            raise ValueError(f"Expected a non-empty value for `token_address` but received {token_address!r}")
        return self._get(
            f"/onchain/networks/{network}/tokens/{token_address}/pools",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include": include,
                        "page": page,
                        "sort": sort,
                    },
                    pool_get_params.PoolGetParams,
                ),
            ),
            cast_to=PoolGetResponse,
        )


class AsyncPoolsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPoolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/coingecko/coingecko-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPoolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPoolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/coingecko/coingecko-python#with_streaming_response
        """
        return AsyncPoolsResourceWithStreamingResponse(self)

    async def get(
        self,
        token_address: str,
        *,
        network: str,
        include: str | Omit = omit,
        page: int | Omit = omit,
        sort: Literal["h24_volume_usd_liquidity_desc", "h24_tx_count_desc", "h24_volume_usd_desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PoolGetResponse:
        """
        This endpoint allows you to **query top pools based on the provided token
        contract address on a network**

        Args:
          include: attributes to include, comma-separated if more than one to include Available
              values: `base_token`, `quote_token`, `dex`

          page: page through results Default value: 1

          sort: sort the pools by field Default value: h24_volume_usd_liquidity_desc

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not network:
            raise ValueError(f"Expected a non-empty value for `network` but received {network!r}")
        if not token_address:
            raise ValueError(f"Expected a non-empty value for `token_address` but received {token_address!r}")
        return await self._get(
            f"/onchain/networks/{network}/tokens/{token_address}/pools",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "include": include,
                        "page": page,
                        "sort": sort,
                    },
                    pool_get_params.PoolGetParams,
                ),
            ),
            cast_to=PoolGetResponse,
        )


class PoolsResourceWithRawResponse:
    def __init__(self, pools: PoolsResource) -> None:
        self._pools = pools

        self.get = to_raw_response_wrapper(
            pools.get,
        )


class AsyncPoolsResourceWithRawResponse:
    def __init__(self, pools: AsyncPoolsResource) -> None:
        self._pools = pools

        self.get = async_to_raw_response_wrapper(
            pools.get,
        )


class PoolsResourceWithStreamingResponse:
    def __init__(self, pools: PoolsResource) -> None:
        self._pools = pools

        self.get = to_streamed_response_wrapper(
            pools.get,
        )


class AsyncPoolsResourceWithStreamingResponse:
    def __init__(self, pools: AsyncPoolsResource) -> None:
        self._pools = pools

        self.get = async_to_streamed_response_wrapper(
            pools.get,
        )
