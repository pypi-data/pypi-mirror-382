"""Compatibility interfaces module.

Provides legacy import path for tests and downstream users:
    from flow.protocols.provider import ConfigField, IProviderInit

These are re-exported from the consolidated core interfaces module.
"""

from __future__ import annotations

from flow.adapters.providers.base import ConfigField
from flow.protocols.provider_init import ProviderInitProtocol as IProviderInit

__all__ = [
    "ConfigField",
    "IProviderInit",
]
