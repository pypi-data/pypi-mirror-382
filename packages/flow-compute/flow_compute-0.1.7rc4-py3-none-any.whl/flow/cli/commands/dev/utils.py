"""Utilities for dev command behavior.

Keep helpers minimal and focused to avoid coupling and scope creep.
"""

from __future__ import annotations


def sanitize_env_name(name: str | None) -> str:
    """Normalize a container environment name for path usage.

    Rules:
    - Preserve the sentinel "default" (case-insensitive)
    - Trim whitespace and leading/trailing slashes
    - If empty after normalization, return a generic non-default name ("env")

    This prevents double slashes in paths like "/envs//project" while
    retaining container semantics (i.e., not mapping to the special
    VM-only "default" behavior).
    """

    raw = (name or "").strip()
    if raw.lower() == "default":
        return "default"
    # Remove leading/trailing slashes, keep inner content intact
    cleaned = raw.strip("/").strip()
    if not cleaned:
        return "env"
    return cleaned
