"""Base class for CLI index caches backed by TTLIndex.

Provides shared functionality for:
  - Context scoping across provider/project via prefetch context
  - Standard cache directory handling (~/.flow)
  - TTL-backed JSON persistence

Subclasses remain responsible for payload shape and public API.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flow.utils.cache.ttl_index import TTLIndex


class BaseIndexCache:
    """Shared helpers for index caches.

    Subclasses should call `super().__init__("<file>.json", cache_dir)`.
    """

    CACHE_TTL_SECONDS = 300  # 5 minutes

    def __init__(self, cache_filename: str, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or Path.home() / ".flow"
        self.cache_file = self.cache_dir / cache_filename

    def _current_context(self) -> str | None:
        """Return a context string to scope cache entries.

        Best-effort: derive from current config when available; otherwise None.
        """
        try:
            import flow.sdk.factory as sdk_factory

            flow = sdk_factory.create_client(auto_init=False)
            provider = flow.provider  # ensure initialized lazily
            base_url = getattr(getattr(provider, "http", None), "base_url", "unknown")
            project = None
            try:
                project = (flow.config.provider_config or {}).get("project")
            except Exception:  # noqa: BLE001
                project = None
            return f"{base_url}|{project or '-'}"
        except Exception:  # noqa: BLE001
            return None

    def _ttl(self) -> TTLIndex:
        return TTLIndex(self.cache_file, self.CACHE_TTL_SECONDS)

    def _load_cache(self) -> dict[str, Any] | None:
        """Load cache data if valid and matches current context when set."""
        data = self._ttl().load()
        if not data:
            return None
        try:
            saved_ctx = data.get("context")
            curr_ctx = self._current_context()
            if saved_ctx is not None and curr_ctx is not None and saved_ctx != curr_ctx:
                return None
        except Exception:  # noqa: BLE001
            pass
        return data

    def clear(self) -> None:
        """Clear the index cache file."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except Exception:  # noqa: BLE001
            pass
