"""Icon utilities for Flow CLI.

Provides a single source of truth for the Flow brand icon and helpers to
prefix help strings consistently across the CLI.
"""

from __future__ import annotations

import os


def flow_icon() -> str:
    """Return the Flow icon character with graceful fallbacks.

    Priority:
    1) FLOW_ICON env override
    2) Unicode star ❊ (U+274A)
    3) ASCII fallback '*'
    """
    try:
        override = (os.environ.get("FLOW_ICON") or "").strip()
        if override:
            return override
    except Exception:  # noqa: BLE001
        pass

    # Preferred brand mark
    try:
        return "❊"
    except Exception:  # noqa: BLE001
        # Fallback to explicit unicode escape if needed
        try:
            return "\u274a"
        except Exception:  # noqa: BLE001
            return "*"


def prefix_with_flow_icon(text: str | None, muted: bool = False) -> str:
    """Prefix provided text with the Flow icon, if not already present.

    Args:
        text: Text to prefix with icon
        muted: If True, apply muted styling to the entire text
    """
    icon = flow_icon()
    base = text or ""
    stripped = base.lstrip()
    if stripped.startswith(icon) or stripped.startswith("\u274a"):
        result = base
    else:
        result = f"{icon} {base}".rstrip()

    if muted:
        # Apply Rich markup for muted styling
        return f"[muted]{result}[/muted]"
    return result
