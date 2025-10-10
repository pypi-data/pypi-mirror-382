"""SSH access resolution helpers for Mithril provider.

Encapsulates key matching/caching and bid-driven SSH access preparation so the
provider facade can remain thin.
"""

from __future__ import annotations

import logging
from pathlib import Path

from flow.adapters.providers.builtin.mithril.domain.models import PlatformSSHKey
from flow.adapters.providers.builtin.mithril.resources.ssh import (
    SSHKeyManager,
)
from flow.core.keys.resolution import (
    resolve_env_key_path,
    resolve_platform_id_to_private_path,
)
from flow.core.utils.ssh_key_cache import SSHKeyCache
from flow.domain.ssh import SSHKeyNotFoundError

logger = logging.getLogger(__name__)

# Some sensible limit
MAX_KEYS_IN_ERROR = 20


def parse_ssh_destination(ssh_destination: str | None) -> tuple[str | None, int]:
    """Parse SSH destination string into host and port.

    Args:
        ssh_destination: SSH destination in format "host:port" or just "host"

    Returns:
        Tuple of (host, port) where port defaults to 22
    """
    if not ssh_destination:
        return None, 22

    # Handle "host:port" format
    if ":" in ssh_destination:
        parts = ssh_destination.rsplit(":", 1)
        try:
            return parts[0], int(parts[1])
        except (ValueError, IndexError):
            return ssh_destination, 22

    return ssh_destination, 22


class SshAccessService:
    """Resolves local SSH key to use for a task and prepares access errors.

    This service depends on the provider's `ssh_key_manager` for platform key
    lookup and local key matching. It does not perform any network operations on
    its own beyond accessing the provider's collaborators.
    """

    def __init__(self, ssh_key_manager: SSHKeyManager) -> None:
        self.ssh_key_manager = ssh_key_manager

    def get_task_ssh_connection_info(
        self,
        task_id: str,
        provider,
    ) -> Path | SSHKeyNotFoundError:
        """Get SSH key path for a task."""

        # Respect explicit override for power-users/automation
        env_path = resolve_env_key_path(["MITHRIL_SSH_KEY"])
        if env_path is not None:
            return env_path

        task = provider.get_task(task_id)
        platform_keys = task.get_ssh_keys()
        platform_key_ids = [key.fid for key in platform_keys] if platform_keys else None

        ssh_cache = SSHKeyCache()
        cached_path = ssh_cache.get_key_path(task_id, validate_with_platform_keys=platform_key_ids)
        if cached_path:
            logger.debug(f"Using cached SSH key path for task {task_id}: {cached_path}")
            return Path(cached_path)

        logger.debug(f"No cached SSH key found for task {task_id}, performing key discovery")

        ssh_key_path = self._find_local_key(platform_keys)

        if isinstance(ssh_key_path, Path):
            try:
                ssh_cache.save_key_path(
                    task_id, str(ssh_key_path), platform_key_ids=platform_key_ids
                )
                logger.debug(f"Cached SSH key path for task {task_id}: {ssh_key_path}")
            except Exception:
                logger.exception("Failed to save SSH key path to cache")

        return ssh_key_path

    # TODO(oliviert): Refactor SSH key resolution to eliminate redundant lookups and simplify call chain.
    #
    # Current problems:
    # - Complex 4-layer call chain: _find_local_key -> resolve_platform_id_to_private_path ->
    #   find_matching_local_key -> discover_local_ssh_keys + match_local_key_to_platform
    # - Multiple repeated lookups: metadata.json read in identity graph, SSH manager cache,
    #   and filesystem scanning all happen independently
    # - API key details fetched multiple times for same key ID
    # - Hard to trace execution flow and debug key matching failures
    def _find_local_key(self, platform_keys: list[PlatformSSHKey]) -> Path | SSHKeyNotFoundError:
        """Prepare SSH access by finding matching local keys for the bid.

        Returns (private_key_path, error_message). Error message is empty string
        on success.
        """
        # Resolve against platform keys and local names/paths deterministically
        for platform_key in platform_keys:
            private_key_path = resolve_platform_id_to_private_path(
                platform_key.fid, self.ssh_key_manager
            )
            if private_key_path:
                return private_key_path

        # No matching key found - build precise error (do not guess a local key)
        key_names = [f"'{key.name}' ({key.fid})" for key in platform_keys[:MAX_KEYS_IN_ERROR]]
        keys_desc = ", ".join(key_names)
        if len(platform_keys) > MAX_KEYS_IN_ERROR:
            keys_desc += f" and {len(platform_keys) - MAX_KEYS_IN_ERROR} more"

        return SSHKeyNotFoundError(
            f"No matching local SSH key found for required platform key(s): {keys_desc}.",
            suggestions=[
                "Ensure the corresponding private key exists locally (check ~/.flow/keys and ~/.ssh)"
                "Or export MITHRIL_SSH_KEY=/path/to/private/key and retry"
            ],
        )
