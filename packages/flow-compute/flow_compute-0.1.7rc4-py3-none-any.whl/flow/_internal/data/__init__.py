"""Backwards-compatible data module.

Provides legacy import paths for data loaders and error types that moved to
`flow.core.data.*`.
"""

from __future__ import annotations

from flow.core.data.loaders import AWSCredentialResolver, S3Loader

# Re-export for convenience if imported as `flow._internal.data` directly
from flow.core.data.resolver import DataError

__all__ = [
    "AWSCredentialResolver",
    "DataError",
    "S3Loader",
]
