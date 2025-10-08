"""Batch execution wrapper for queuing actions - protected from Stainless regeneration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from ._client import Computer as TzafonClient
    from .types.computer_execute_batch_response import ComputerExecuteBatchResponse

__all__ = ["BatchComputerWrapper"]


class BatchComputerWrapper:
    """Wrapper that queues actions and executes them in batch."""

    def __init__(self, client: TzafonClient, computer_id: str) -> None:
        self._client = client
        self.id = computer_id
        self._actions: List[Dict[str, Any]] = []

    def navigate(self, url: str) -> BatchComputerWrapper:
        """Queue navigate action."""
        self._actions.append({"type": "go_to_url", "url": url})
        return self

    def type(self, text: str) -> BatchComputerWrapper:
        """Queue type action."""
        self._actions.append({"type": "type", "text": text})
        return self

    def click(self, x: int, y: int) -> BatchComputerWrapper:
        """Queue click action."""
        self._actions.append({"type": "click", "x": x, "y": y})
        return self

    def screenshot(self) -> BatchComputerWrapper:
        """Queue screenshot action."""
        self._actions.append({"type": "screenshot"})
        return self

    def double_click(self, x: int, y: int) -> BatchComputerWrapper:
        """Queue double-click action."""
        self._actions.append({"type": "double_click", "x": x, "y": y})
        return self

    def right_click(self, x: int, y: int) -> BatchComputerWrapper:
        """Queue right-click action."""
        self._actions.append({"type": "right_click", "x": x, "y": y})
        return self

    def drag(self, from_x: int, from_y: int, to_x: int, to_y: int) -> BatchComputerWrapper:
        """Queue drag action."""
        self._actions.append({
            "type": "drag",
            "x1": from_x,
            "y1": from_y,
            "x2": to_x,
            "y2": to_y,
        })
        return self

    def hotkey(self, *keys: str) -> BatchComputerWrapper:
        """Queue hotkey action."""
        self._actions.append({"type": "keypress", "keys": list(keys)})
        return self

    def scroll(self, direction: str, amount: int = 500) -> BatchComputerWrapper:
        """Queue scroll action."""
        dy = amount if direction == "down" else -amount
        self._actions.append({"type": "scroll", "x": 0, "y": 0, "dx": 0, "dy": dy})
        return self

    def wait(self, seconds: float) -> BatchComputerWrapper:
        """Queue wait action."""
        self._actions.append({"type": "wait", "ms": int(seconds * 1000)})
        return self

    def execute(self) -> ComputerExecuteBatchResponse:
        """Execute all queued actions in batch."""
        if not self._actions:
            raise ValueError("No actions to execute. Queue actions first.")
        
        result = self._client.computers.execute_batch(
            self.id,
            body={"actions": self._actions}
        )
        self._actions = []  # Clear queue after execution
        return result

    def terminate(self) -> None:
        """Terminate the computer session."""
        self._client.computers.terminate(self.id)

    def __enter__(self) -> BatchComputerWrapper:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - auto cleanup."""
        self.terminate()

