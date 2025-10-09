"""Deprecated compatibility package.

The legacy `flow.api` package has been replaced by the unified SDK surface
under `flow.sdk.*`. Importing this package emits a DeprecationWarning to aid
migration while keeping older code running for a deprecation window.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "flow.api is deprecated; use flow.sdk.* instead",
    DeprecationWarning,
    stacklevel=2,
)

# Optionally expose a few convenient aliases for older code paths
try:  # pragma: no cover - thin shim
    from flow.sdk import client, models  # type: ignore
except Exception:  # pragma: no cover - best effort  # noqa: BLE001
    pass

__all__ = [
    "client",
    "models",
]
