"""Key Identity Graph: local mapping between platform key IDs and private paths.

Centralizes persistence and lookup of SSH key identity data so multiple layers
(CLI, providers, wizards) can share a single source of truth.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_META_PATH = Path.home() / ".flow" / "keys" / "metadata.json"


def _load_all() -> dict[str, Any]:
    if _META_PATH.exists():
        content = _META_PATH.read_text().strip()
        if not content:
            return {}
        return json.loads(content)
    return {}


def _save_all(data: dict[str, Any]) -> None:
    try:
        _META_PATH.parent.mkdir(parents=True, exist_ok=True)
        _META_PATH.write_text(json.dumps(data, indent=2))
        try:
            _META_PATH.chmod(0o600)
        except Exception:  # noqa: BLE001
            pass
    except Exception:  # noqa: BLE001
        # Best-effort persistence
        pass


def store_key_metadata(
    *,
    key_id: str,
    key_name: str,
    private_key_path: Path,
    project_id: str | None = None,
    auto_generated: bool = False,
) -> None:
    """Persist mapping from platform key ID to local private key path.

    Keeps the existing metadata schema for backward compatibility.
    """
    if not key_id or not str(private_key_path):
        return
    metadata = _load_all()
    entry = {
        "key_id": key_id,
        "key_name": key_name,
        "private_key_path": str(private_key_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project": project_id,
        "auto_generated": bool(auto_generated),
    }
    metadata[key_id] = entry
    _save_all(metadata)


def get_local_key_private_path(key_id: str) -> Path | None:
    """Return the local private key path for a given platform key ID, if known."""
    data = _load_all()
    info = data.get(key_id)
    if not info:
        return None
    p = Path(info.get("private_key_path", ""))
    return p if p.is_file() else None


def find_key_metadata(*, key_ref: str) -> dict[str, Any] | None:
    """Find key ID by name or private key path."""

    data = _load_all()
    key_ref_path = Path(key_ref)
    for info in data.values():
        if info.get("key_name") == key_ref:
            return info

        metadata_key_path = Path(info.get("private_key_path", ""))
        if metadata_key_path.resolve() == key_ref_path.resolve():
            return info

    return None


def get_last_auto_generated_key(project_id: str) -> str | None:
    """Check for previously auto-generated keys.

    Searches metadata.json for auto-generated keys belonging to the current
    project. Returns the most recently created key if multiple exist.

    Returns:
        Optional[str]: SSH key ID of most recent auto-generated key, or None.
    """
    data = _load_all()
    # Filter keys by project and auto-generated flag
    project_keys = [
        (k, v)
        for k, v in data.items()
        if v.get("project") == project_id and v.get("auto_generated")
    ]
    if project_keys:
        # Sort by timestamp descending, return newest
        project_keys.sort(key=lambda x: x[1]["created_at"], reverse=True)
        return project_keys[0][0]

    return None


def friendly_path_name(path: Path) -> str:
    """Return a friendly name for a path."""
    path_str = str(path)
    if path_str.startswith("~/"):
        path_str = path_str.replace("~/", "home_")
    if "/" in path_str:
        path_str = Path(path_str).stem
    return path_str
