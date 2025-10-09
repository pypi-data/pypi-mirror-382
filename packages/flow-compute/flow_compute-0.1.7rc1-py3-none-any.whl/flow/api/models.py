"""Deprecated models compatibility shim.

Provides backward-compatible imports from `flow.api.models` to `flow.sdk.models`.
"""

from __future__ import annotations

import warnings as _warnings

from flow.sdk.models import *  # noqa: F403 - re-export for compatibility

_warnings.warn(
    "flow.api.models is deprecated; import from flow.sdk.models",
    DeprecationWarning,
    stacklevel=2,
)
