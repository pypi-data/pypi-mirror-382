"""Compatibility shim for legacy resolver module.

Use `flow.core.data.resolver` instead.
"""

from __future__ import annotations

from flow.core.data.resolver import DataError

__all__ = [
    "DataError",
]
