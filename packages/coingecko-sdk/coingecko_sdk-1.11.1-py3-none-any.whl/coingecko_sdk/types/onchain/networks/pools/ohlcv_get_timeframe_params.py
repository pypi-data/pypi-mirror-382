# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["OhlcvGetTimeframeParams"]


class OhlcvGetTimeframeParams(TypedDict, total=False):
    network: Required[str]

    pool_address: Required[str]

    token: str
    """
    return OHLCV for token use this to invert the chart Available values: 'base',
    'quote' or token address Default value: 'base'
    """

    aggregate: str
    """
    time period to aggregate each OHLCV Available values (day): `1` Available values
    (hour): `1` , `4` , `12` Available values (minute): `1` , `5` , `15` Available
    values (second): `1`, `15`, `30` Default value: 1
    """

    before_timestamp: int
    """return OHLCV data before this timestamp (integer seconds since epoch)"""

    currency: Literal["usd", "token"]
    """return OHLCV in USD or quote token Default value: usd"""

    include_empty_intervals: bool
    """include empty intervals with no trade data, default: false"""

    limit: int
    """number of OHLCV results to return, maximum 1000 Default value: 100"""
