"""SSH key resolution and generation service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.resources.ssh import SSHKeyManager
    from flow.sdk.models import TaskConfig
logger = logging.getLogger(__name__)


class SSHKeyService:
    def __init__(self, ssh_key_manager: SSHKeyManager, mithril_config=None) -> None:
        self._mgr = ssh_key_manager
        self._mithril_config = mithril_config

    def resolve_keys_for_task(self, config: TaskConfig) -> list[str]:
        """Full SSH key resolution logic for task submission.

        This implements the complete resolution priority:
        1. Task config SSH keys
        2. Provider config SSH keys
        3. Environment variable (MITHRIL_SSH_KEY)
        4. Existing project keys with local private keys
        5. Auto-generation of new key

        Args:
            config: Task configuration

        Returns:
            List of SSH key IDs to use for the task
        """

        # Resolution priority: task config > provider config > auto-generation
        requested_keys = config.ssh_keys
        if not requested_keys and self._mithril_config:
            requested_keys = getattr(self._mithril_config, "ssh_keys", None)

        logger.debug(f"resolve_keys_for_task: ensuring platform keys: {requested_keys}")
        resolved_keys = self._mgr.ensure_platform_keys(requested_keys) if requested_keys else []
        logger.debug(f"resolve_keys_for_task: appending required keys: {resolved_keys}")
        resolved_keys = self._mgr.append_required_keys(resolved_keys)
        logger.debug(f"resolve_keys_for_task: appending mithril env key: {resolved_keys}")
        resolved_keys = self._mgr.append_mithril_env_key(resolved_keys)
        logger.debug(f"resolve_keys_for_task: ensuring one local key: {resolved_keys}")
        resolved_keys = self._mgr.ensure_one_local_key(resolved_keys)

        return resolved_keys

    def _backfill_config(self, key_id: str) -> None:
        """Try to save generated key to config for future runs."""
        try:
            from flow.application.config.manager import ConfigManager

            cm = ConfigManager()
            payload = {
                "provider": "mithril",
                "mithril": {
                    "ssh_keys": [key_id],
                },
            }
            cm.save(payload)
        except Exception:  # noqa: BLE001
            # Never block launch on backfill issues
            pass
