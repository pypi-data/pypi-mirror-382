"""SSH facet - handles SSH operations, remote execution, and tunneling."""

from __future__ import annotations

import logging
import os
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from flow.adapters.providers.builtin.mithril.adapters.remote import MithrilRemoteOperations
from flow.adapters.providers.builtin.mithril.domain.models import PlatformSSHKey
from flow.adapters.providers.builtin.mithril.transport.jupyter_tunnel_manager import (
    MithrilJupyterTunnelManager,
)
from flow.adapters.transport.ssh import SSHTunnelManager
from flow.errors import FlowError

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext
    from flow.adapters.providers.builtin.mithril.provider.provider import MithrilProvider
    from flow.domain.ssh import SSHKeyNotFoundError
    from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class SSHFacet:
    """Handles SSH operations and remote execution."""

    def __init__(self, ctx: MithrilContext, provider: MithrilProvider) -> None:
        """Initialize SSH facet and wire remote operations.

        Args:
            ctx: Mithril context with all dependencies
        """
        self.ctx = ctx
        self.provider = provider

        # Back-inject remote ops & ssh readiness into services that need them
        # This avoids circular dependencies
        self.ctx.log_service._remote = self.get_remote_operations()
        self.ctx.volume_attach.make_remote_ops = self.get_remote_operations  # type: ignore[attr-defined]
        self.ctx.volume_attach.is_instance_ssh_ready = self._is_instance_ssh_ready  # type: ignore[attr-defined]

    def get_remote_operations(self):
        """Get remote operations handler.

        Returns:
            MithrilRemoteOperations instance
        """
        # Pass self as provider-like object
        return MithrilRemoteOperations(self.provider)  # type: ignore[arg-type]

    def get_ssh_tunnel_manager(self):
        """Get SSH tunnel manager class.

        Returns:
            SSHTunnelManager class
        """
        return SSHTunnelManager

    def get_jupyter_tunnel_manager(self):
        """Get Jupyter-specific tunnel manager for Mithril.

        Returns:
            MithrilJupyterTunnelManager instance with foundrypf support
        """
        return MithrilJupyterTunnelManager()

    def get_task_ssh_connection_info(self, task_id: str) -> Path | SSHKeyNotFoundError:
        """Get SSH connection info for a task.

        Args:
            task_id: Task ID

        Returns:
            Tuple of (ssh_key_path, error_message)
            If successful, returns (Path, "")
            If failed, returns (None, error_message)
        """
        return self.ctx.ssh_access.get_task_ssh_connection_info(
            task_id=task_id,
            provider=self.provider,
        )

    def resolve_ssh_endpoint(self, task_id: str, node: int | None = None) -> tuple[str, int]:
        """Resolve SSH endpoint for a task.

        Args:
            task_id: Task ID
            node: Optional node index for multi-node tasks

        Returns:
            Tuple of (host, port)
        """
        # Try to get SSH endpoint resolver
        try:
            from flow.adapters.providers.builtin.mithril.domain.ssh_endpoint_resolver import (
                SshEndpointResolver,
            )

            resolver = SshEndpointResolver(
                self.ctx.api, self.ctx.get_project_id, self.ctx.instances
            )

            try:
                from flow.application.config.runtime import settings as _settings  # local import

                debug = bool((_settings.ssh or {}).get("debug", False))
            except Exception:  # noqa: BLE001
                debug = os.environ.get("FLOW_SSH_DEBUG") == "1"

            # Try cached resolution first
            if hasattr(resolver, "resolve_with_cache"):
                host, port = resolver.resolve_with_cache(
                    task_id, node=node, tcp_probe=True, debug=debug
                )
            else:
                host, port = resolver.resolve(task_id, node=node, tcp_probe=True, debug=debug)

            return host, port

        except ImportError:
            # Fallback to basic resolution
            bid = self._get_bid(task_id)
            instances = bid.get("instances", [])

            if not instances:
                raise ValueError(f"No instances found for task {task_id}")

            # Get the requested node or first instance
            idx = node if node is not None else 0
            if idx >= len(instances):
                idx = 0

            instance = instances[idx]

            # Try to get SSH destination
            ssh_dest = instance.get("ssh_destination")
            if ssh_dest:
                from flow.adapters.providers.builtin.mithril.domain.ssh_access import (
                    parse_ssh_destination,
                )

                host, port = parse_ssh_destination(ssh_dest)
                if host:
                    return host, port

            # Fallback to public IP
            host = instance.get("public_ip")
            if not host:
                raise ValueError(f"No SSH endpoint found for task {task_id}")

            return host, 22

    def get_transport(self):
        """Get transport helper for SSH operations.

        Returns:
            Transport object with wait_for_ssh and upload_code methods
        """

        class _Transport:
            def __init__(self, ssh_facet):
                self.ssh = ssh_facet

            def wait_for_ssh(self, task: Task, timeout: int | None = None):
                """Wait for SSH to become available."""
                from flow.adapters.transport.ssh import ExponentialBackoffSSHWaiter

                waiter = ExponentialBackoffSSHWaiter(self.ssh)  # type: ignore[arg-type]
                return waiter.wait_for_ssh(task, timeout=timeout)

            def upload_code(self, task: Task, source_dir: Path, target_dir: str = "~"):
                """Upload code to task."""
                from flow.adapters.transport.code_transfer import (
                    CodeTransferConfig,
                    CodeTransferManager,
                )

                manager = CodeTransferManager(provider=self.ssh)  # type: ignore[arg-type]
                cfg = CodeTransferConfig(source_dir=source_dir, target_dir=target_dir)
                return manager.transfer_code_to_task(task, cfg)

        return _Transport(self)

    def _is_instance_ssh_ready(self, task: Task) -> bool:
        """Check if instance is ready for SSH.

        Args:
            task: Task to check

        Returns:
            True if SSH is ready, False otherwise
        """
        # Check basic requirements
        if not task.ssh_host or not task.ssh_port:
            return False

        if task.status.value.lower() != "running":
            return False

        # Check if instance has been running for minimum time
        with suppress(Exception):
            created = datetime.fromisoformat(task.created_at.replace("Z", "+00:00"))
            age_sec = (datetime.now(timezone.utc) - created).total_seconds()
            if age_sec < 60:  # Wait at least 60 seconds
                return False

        return True

    def _get_bid(self, task_id: str) -> dict:
        """Get bid data for a task.

        Args:
            task_id: Task ID

        Returns:
            Bid data dictionary
        """
        try:
            return self.ctx.api.get_bid(task_id)
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to get bid for task {task_id}: {e}")
            return {}

    def get_task_ssh_keys(self, task_id: str) -> list[PlatformSSHKey]:
        """Get SSH keys configured for a specific task.

        This method follows the Mithril API contract by:
        1. Getting the bid data for the task from the API
        2. Extracting SSH key IDs from the launch specification
        3. Enriching with key metadata from the SSH key manager

        Args:
            task_id: Task ID to get SSH keys for

        Returns:
            List of PlatformSSHKey objects with platform key details
        """
        # Get bid data from Mithril API
        bid = self._get_bid(task_id)
        if not bid:
            raise FlowError(f"No bid found for task {task_id}")

        # Extract SSH key IDs from launch specification
        launch_spec = bid.get("launch_specification", {})
        key_ids = launch_spec.get("ssh_keys", [])

        result = []
        for key_id in key_ids:
            key = self.ctx.ssh_key_mgr.get_key(key_id)
            if not key:
                raise FlowError(f"SSH key {key_id} not found")

            result.append(
                PlatformSSHKey(
                    fid=key_id,
                    name=key.name,
                    public_key=key.public_key,
                    fingerprint=key.fingerprint,
                    created_at=key.created_at,
                    required=key.required,
                )
            )

        return result

    # Provider interface compatibility methods
    # These allow SSHFacet to be used as a provider-like object

    @property
    def api_url(self) -> str:
        """Get API URL for compatibility."""
        return self.ctx.mithril_config.api_url

    @property
    def project_id(self) -> str:
        """Get project ID for compatibility."""
        return self.ctx.get_project_id()
