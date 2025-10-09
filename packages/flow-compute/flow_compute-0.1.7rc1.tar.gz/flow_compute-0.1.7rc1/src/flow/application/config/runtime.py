"""Runtime settings facade for Flow SDK.

Provides a single import point to read configuration across the codebase with
clear precedence (environment > ~/.flow/config.yaml > defaults).

Usage:
    from flow.application.config.runtime import settings
    if settings.logging.get("json"):
        ...

This module intentionally keeps a light dependency surface and lazy-loads
configuration to avoid expensive imports on hot paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import Config as _Config
from .loader import ConfigLoader as _ConfigLoader


@dataclass
class RuntimeSettings:
    """Aggregated settings resolved from env + YAML."""

    provider: str
    api_key: str | None
    mithril: dict[str, Any] = field(default_factory=dict)
    health: dict[str, Any] = field(default_factory=dict)
    logging: dict[str, Any] = field(default_factory=dict)
    http: dict[str, Any] = field(default_factory=dict)
    colab: dict[str, Any] = field(default_factory=dict)
    ssh: dict[str, Any] = field(default_factory=dict)
    upload: dict[str, Any] = field(default_factory=dict)
    ui: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls) -> RuntimeSettings:
        """Load settings from current environment and config file."""
        cfg = _Config.from_env(require_auth=False)
        loader = _ConfigLoader()
        return cls(
            provider=cfg.provider,
            api_key=cfg.auth_token,
            mithril=dict(cfg.provider_config or {}),
            health=dict(cfg.health_config or {}),
            logging=loader.get_logging_config(),
            http=loader.get_http_config(),
            colab=loader.get_colab_config(),
            ssh=loader.get_ssh_config(),
            upload=loader.get_upload_config(),
            ui=loader.get_ui_config(),
        )

    def refresh(self) -> None:
        """Refresh values from env + YAML (in-place)."""
        updated = self.load()
        self.provider = updated.provider
        self.api_key = updated.api_key
        self.mithril = updated.mithril
        self.health = updated.health
        self.logging = updated.logging
        self.http = updated.http
        self.colab = updated.colab
        self.ssh = updated.ssh
        self.upload = updated.upload
        self.ui = updated.ui


# Lazy global with a simple accessor to allow future injection/testing if needed
_SETTINGS: RuntimeSettings | None = None


def get_settings() -> RuntimeSettings:
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = RuntimeSettings.load()
    return _SETTINGS


# Convenient alias for most callers
settings = get_settings()
