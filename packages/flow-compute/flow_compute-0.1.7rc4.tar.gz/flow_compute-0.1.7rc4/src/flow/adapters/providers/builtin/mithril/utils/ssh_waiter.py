"""Compatibility wrapper for SSH waiter.

Delegates to the shared adapters transport implementation.
"""

from __future__ import annotations

from flow.adapters.transport.ssh import ExponentialBackoffSSHWaiter

__all__ = ["ExponentialBackoffSSHWaiter"]
