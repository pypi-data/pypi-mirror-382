# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["ActionResult"]


class ActionResult(BaseModel):
    error_message: Optional[str] = None

    result: Optional[Dict[str, object]] = None

    status: Optional[str] = None

    timestamp: Optional[str] = None
