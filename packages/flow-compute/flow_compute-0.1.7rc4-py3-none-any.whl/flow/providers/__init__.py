"""Removed legacy package alias.

The public import path `flow.providers` has been removed in favor of the
explicit adapter hierarchy `flow.adapters.providers.*`.

Importing this package now raises ModuleNotFoundError to prevent accidental
use of the legacy namespace and to satisfy the deprecation contract.
"""

from __future__ import annotations

raise ModuleNotFoundError(
    "flow.providers has been removed; import from flow.adapters.providers.* instead"
)
