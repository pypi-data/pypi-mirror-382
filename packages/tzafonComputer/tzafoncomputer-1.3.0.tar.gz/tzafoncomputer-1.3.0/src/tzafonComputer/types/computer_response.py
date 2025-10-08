# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["ComputerResponse"]


class ComputerResponse(BaseModel):
    id: Optional[str] = None

    created_at: Optional[str] = None

    endpoints: Optional[Dict[str, str]] = None

    status: Optional[str] = None

    type: Optional[str] = None
