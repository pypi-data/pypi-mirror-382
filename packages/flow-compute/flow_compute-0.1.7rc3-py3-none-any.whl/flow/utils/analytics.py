"""Thin forwarding layer for analytics.

IO/network access must not live in utils/**. The concrete implementation for
Amplitude is in ``flow.adapters.metrics.analytics``. This module provides a
stable import location (``flow.utils.analytics``) and forwards calls to the
adapter implementation without importing any networking libraries here.

All functions are best-effort and safe to import in any environment.
"""

from __future__ import annotations

import contextlib
from typing import Any


def telemetry_enabled() -> bool:
    """Proxy to the adapters implementation, always safe to import."""
    try:
        from flow.adapters.metrics import analytics as _impl

        return bool(_impl.telemetry_enabled())
    except Exception:  # noqa: BLE001
        return False


def start() -> None:
    """Proxy to start the adapters analytics worker (best-effort)."""
    with contextlib.suppress(Exception):
        from flow.adapters.metrics import analytics as _impl

        _impl.start()


def track(
    event_type: str, properties: dict[str, Any] | None = None, *, time_ms: int | None = None
) -> None:
    """Proxy to enqueue an analytics event (best-effort; never raises)."""
    try:
        from flow.adapters.metrics import analytics as _impl

        _impl.track(event_type, properties, time_ms=time_ms)
    except Exception:  # noqa: BLE001
        pass


# Compatibility re-exports for tests and existing code that reference
# internals from flow.utils.analytics. These are bound dynamically to the
# adapters implementation to keep IO outside utils/**.
try:  # pragma: no cover - exercised indirectly by tests that import these names
    from flow.adapters.metrics import analytics as _impl

    _AmplitudeWorker = _impl._AmplitudeWorker  # type: ignore[attr-defined]
    AnalyticsEvent = _impl.AnalyticsEvent  # type: ignore[attr-defined]
    _worker = _impl._worker  # type: ignore[attr-defined]
    DEFAULT_INGEST_URL = _impl.DEFAULT_INGEST_URL  # type: ignore[attr-defined]
except (
    Exception  # noqa: BLE001
):  # Fallback no-op stubs when adapters implementation is unavailable

    class AnalyticsEvent:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """No-op placeholder when analytics adapter is unavailable."""

    class _AmplitudeWorker:  # type: ignore[no-redef]
        def enabled(self) -> bool:
            """Return False in placeholder implementation."""
            return False

    _worker = None
