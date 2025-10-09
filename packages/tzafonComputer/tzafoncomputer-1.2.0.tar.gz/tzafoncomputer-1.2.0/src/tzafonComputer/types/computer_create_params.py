# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ComputerCreateParams", "Display"]


class ComputerCreateParams(TypedDict, total=False):
    context_id: str

    display: Display
    """TODO: implement"""

    kind: str
    """\"browser"|"desktop"|"code" etc"""

    stealth: object
    """TODO: implement"""

    timeout_seconds: int


class Display(TypedDict, total=False):
    height: int

    scale: float

    width: int
