"""SDK setup utilities (provider registry helpers).

Surgical shim to expose provider discovery to CLI without creating
static CLI→core dependencies. Uses lazy imports under the hood.
"""

from __future__ import annotations

import importlib
from typing import Any


def _import_attr(module: str, name: str, default: Any = None) -> Any:
    try:
        mod = importlib.import_module(module)
        return getattr(mod, name)
    except Exception:  # noqa: BLE001
        return default


def register_providers() -> None:
    """Register providers into the core registry, if available."""
    reg = _import_attr("flow.core.setup_registry", "register_providers", default=None)
    try:
        if reg:
            reg()
    except Exception:  # noqa: BLE001
        # Best-effort only
        pass


def list_providers() -> list[str]:
    """Return list of available provider names (best effort)."""
    register_providers()
    SetupRegistry = _import_attr("flow.core.setup_registry", "SetupRegistry", default=None)
    if not SetupRegistry:
        raise RuntimeError("SetupRegistry not found")
    return list(SetupRegistry.list_adapters())


def get_adapter(name: str) -> Any | None:
    """Return the provider adapter for a given name (or None)."""
    register_providers()
    SetupRegistry = _import_attr("flow.core.setup_registry", "SetupRegistry", default=None)
    if not SetupRegistry:
        raise RuntimeError("SetupRegistry not found")
    return SetupRegistry.get_adapter(name)
