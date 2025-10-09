"""Lightweight event bus for SSH key-related changes.

Allows decoupled components (CLI, provider init, caches) to react to
key list mutations without tight coupling or direct cross-layer calls.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any


class KeyEventBus:
    _subscribers: defaultdict[str, list[Callable[[Any], None]]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event: str, callback: Callable[[Any], None]) -> None:
        if callback not in cls._subscribers[event]:
            cls._subscribers[event].append(callback)

    @classmethod
    def unsubscribe(cls, event: str, callback: Callable[[Any], None]) -> None:
        try:
            cls._subscribers[event].remove(callback)
        except ValueError:
            pass

    @classmethod
    def emit(cls, event: str, payload: Any | None = None) -> None:
        for cb in list(cls._subscribers.get(event, [])):
            try:
                cb(payload)
            except Exception:  # noqa: BLE001
                # Event handlers must be best-effort and never raise
                continue


SSH_KEYS_CHANGED = "ssh_keys_changed"
