"""Provider-first instance type resolution helper.

Tries to resolve user-friendly instance specs (e.g., "a100", "4xa100") using
the active provider when possible, falling back to domain canonicalization.

This is intentionally lightweight and safe: it never raises on fallback paths
and returns the input when no better resolution is available.
"""

from __future__ import annotations

from typing import Any


def resolve_instance_type(provider: Any, spec: str) -> str:
    """Resolve an instance type via provider, with safe fallback.

    Behavior:
      - If provider exposes `resolve_instance_type`, use it.
      - If `spec` already looks like a provider ID (e.g., "it_..."), return as-is.
      - Fall back to canonicalizing via domain parser; if that fails, return input.
    """
    s = (spec or "").strip()
    if not s:
        return s

    # Provider-native resolution
    try:
        if hasattr(provider, "resolve_instance_type") and callable(provider.resolve_instance_type):
            return provider.resolve_instance_type(s)
    except Exception:  # noqa: BLE001
        pass

    # Pass through apparent provider IDs
    if s.startswith("it_"):
        return s

    # Best-effort canonicalization (provider-agnostic)
    try:
        from flow.domain.parsers.instance_parser import canonicalize_instance_type as _canon

        return _canon(s)
    except Exception:  # noqa: BLE001
        return s


__all__ = ["resolve_instance_type"]
