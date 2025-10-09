"""Setup helpers for status command pre-execution concerns."""

from __future__ import annotations

import os


def apply_project_env(project: str | None) -> None:
    """If provided, set project env vars before creating Flow().

    The provider context resolves the project from ``MITHRIL_PROJECT_ID``.
    Set that primary variable, and also set legacy ``MITHRIL_PROJECT`` for
    downstream helpers that still read it.
    """
    if not project:
        return
    try:
        # Primary env used by provider context
        os.environ["MITHRIL_PROJECT_ID"] = project
        # Legacy alias used by some CLI helpers
        os.environ["MITHRIL_PROJECT"] = project
    except Exception:  # noqa: BLE001
        pass


def apply_force_refresh() -> None:
    """Clear HTTP caches when --force-refresh is set.

    Clears the cache directory directly since this is called before any
    HTTP clients are created, so the pool is empty.
    """
    try:
        # Clear cache directory directly (more reliable than pool iteration)
        import shutil
        from pathlib import Path

        cache_dir = Path.home() / ".flow" / "http_cache"
        if cache_dir.exists():
            # Remove all cache files but keep .gitignore
            for item in cache_dir.iterdir():
                if item.name != ".gitignore":
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
    except Exception:  # noqa: BLE001
        # Best-effort; don't fail if cache clearing fails
        pass
