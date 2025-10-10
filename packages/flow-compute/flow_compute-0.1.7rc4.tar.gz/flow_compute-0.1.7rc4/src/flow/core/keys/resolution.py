"""Provider-agnostic helpers for resolving SSH key references to local paths.

These utilities centralize common resolution strategies so callers (CLI, SDK,
providers) can share consistent behavior without tight coupling.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flow.core.keys.identity import get_local_key_private_path


def resolve_env_key_path(var_names: list[str] | tuple[str, ...]) -> Path | None:
    """Resolve an SSH private key path from environment variables.

    Returns the first existing file among the provided env vars.
    If a .pub is provided, returns the private counterpart if it exists.
    """
    for name in var_names:
        val = os.environ.get(name)
        if not val:
            continue
        try:
            p = Path(val).expanduser()
            if p.suffix == ".pub":
                priv = p.with_suffix("")
                if priv.exists() and priv.is_file():
                    return priv
            if p.exists() and p.is_file():
                return p
        except Exception:  # noqa: BLE001
            continue
    return None


def resolve_platform_id_to_private_path(
    platform_key_id: str, manager: Any | None = None
) -> Path | None:
    """Resolve a platform SSH key ID to a local private key path.

    Strategy:
    1) Key Identity Graph (persistent id→path mapping)
    2) Provider manager fallback (e.g., public key or fingerprint match)
    """
    if not platform_key_id:
        return None
    # 1) Identity graph
    p = get_local_key_private_path(platform_key_id)
    if p is not None:
        return p

    # 2) Provider fallback
    if manager is not None and hasattr(manager, "find_matching_local_key"):
        p = manager.find_matching_local_key(platform_key_id)
        if p is not None:
            return Path(p)

    return None


def resolve_key_reference(key_ref: str, manager: Any | None = None) -> Path | None:
    """Resolve a generic SSH key reference (platform ID or path) to local private path.

    - If `key_ref` is a platform ID (sshkey_*), use resolve_platform_id_to_private_path.
    - If `key_ref` looks like a path, return the file (or private half if .pub) if it exists.
    - Otherwise return None.
    """
    if isinstance(key_ref, str) and key_ref.startswith("sshkey_"):
        return resolve_platform_id_to_private_path(key_ref, manager)

    # Path-like
    try:
        p = Path(str(key_ref)).expanduser()
        if p.exists() and p.is_file():
            return p if p.suffix != ".pub" else p.with_suffix("")
    except Exception:  # noqa: BLE001
        pass
    return None
