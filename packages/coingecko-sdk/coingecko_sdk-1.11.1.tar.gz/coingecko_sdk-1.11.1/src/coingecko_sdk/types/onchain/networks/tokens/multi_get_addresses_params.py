# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["MultiGetAddressesParams"]


class MultiGetAddressesParams(TypedDict, total=False):
    network: Required[str]

    include: Literal["top_pools"]
    """attributes to include"""

    include_composition: bool
    """include pool composition, default: false"""
