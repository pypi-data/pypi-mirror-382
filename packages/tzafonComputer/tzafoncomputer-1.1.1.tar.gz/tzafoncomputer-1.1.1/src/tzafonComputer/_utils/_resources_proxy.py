from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `tzafonComputer.resources` module.

    This is used so that we can lazily import `tzafonComputer.resources` only when
    needed *and* so that users can just import `tzafonComputer` and reference `tzafonComputer.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("tzafonComputer.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
