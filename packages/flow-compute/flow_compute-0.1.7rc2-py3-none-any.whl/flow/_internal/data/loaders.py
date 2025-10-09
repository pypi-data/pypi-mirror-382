"""Compatibility shim for legacy loaders module.

Use `flow.core.data.loaders` instead.
"""

from __future__ import annotations

from flow.core.data.loaders import AWSCredentialResolver, S3Loader

__all__ = [
    "AWSCredentialResolver",
    "S3Loader",
]
