# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["AuthHandleCallbackParams"]


class AuthHandleCallbackParams(TypedDict, total=False):
    code: Required[str]
    """Authorization code (valid for 10 minutes)"""

    state: Required[str]
    """State parameter for CSRF protection"""
