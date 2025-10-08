"""Client extensions - protected from Stainless regeneration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import Computer as TzafonClient
    from .wrapper import ComputerWrapper
    from .batch_wrapper import BatchComputerWrapper

__all__ = ["add_client_extensions", "add_batch_client_extensions"]


def add_client_extensions(client_class: type[TzafonClient]) -> None:
    """Monkey-patch the Computer client to add custom methods."""

    def create(
        self: TzafonClient, kind: str = "browser", **kwargs
    ) -> ComputerWrapper:
        """Create a computer and return a high-level wrapper.

        Args:
            kind: Type of computer ("browser", "desktop", "code")
            **kwargs: Additional arguments passed to computers.create()

        Returns:
            ComputerWrapper instance with clean API
        """
        from .wrapper import ComputerWrapper

        response = self.computers.create(kind=kind, **kwargs)
        return ComputerWrapper(self, response.id)

    # Add the method to the class
    client_class.create = create  # type: ignore


def add_batch_client_extensions(client_class: type[TzafonClient]) -> None:
    """Monkey-patch the Computer client for batch execution."""

    def create(
        self: TzafonClient, kind: str = "browser", **kwargs
    ) -> BatchComputerWrapper:
        """Create a computer and return a batch execution wrapper.

        Args:
            kind: Type of computer ("browser", "desktop", "code")
            **kwargs: Additional arguments passed to computers.create()

        Returns:
            BatchComputerWrapper instance that queues actions
        """
        from .batch_wrapper import BatchComputerWrapper

        response = self.computers.create(kind=kind, **kwargs)
        return BatchComputerWrapper(self, response.id)

    # Add the method to the class
    client_class.create = create  # type: ignore

