"""SSH client-side wait utilities and connection info structures.

This module contains portable, provider-agnostic SSH helpers used by the CLI
and adapters. Import `SSHConnectionInfo`, `ISSHWaiter`, or
`ExponentialBackoffSSHWaiter` from here for direct use, or from
`flow.adapters.transport.ssh` for the stable facade.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from flow.adapters.transport.ssh.ssh_stack import SshStack
from flow.domain.ssh import SSHKeyNotFoundError
from flow.sdk.models import Task
from flow.sdk.ssh_utils import SSHNotReadyError, wait_for_task_ssh_info

logger = logging.getLogger(__name__)


@dataclass
class SSHConnectionInfo:
    host: str
    port: int
    user: str
    key_path: Path
    task_id: str
    # Optional ProxyJump destination (e.g., "ubuntu@bastion:22") when the
    # instance is only reachable via a bastion. Strategies like rsync should
    # honor this by adding "-J <proxy>" to their ssh commands.
    proxyjump: str | None = None

    @property
    def destination(self) -> str:
        return f"{self.user}@{self.host}"


class ISSHWaiter(Protocol):
    def wait_for_ssh(
        self,
        task: Task,
        timeout: int | None = None,
        probe_interval: float = 10.0,
        progress_callback: Callable[[str], None] | None = None,
        node: int | None = None,
    ) -> SSHConnectionInfo: ...


class ExponentialBackoffSSHWaiter:
    """Waits for SSH reachability using fast, adaptive probes.

    Behavior tweaks for developer workflows:
    - Much shorter initial probe interval (1s) so readiness is detected quickly
      once the instance is reachable.
    - Lower maximum backoff to avoid long idle gaps while the service comes up.
    - Tunable via environment variables for power users/providers:
        * FLOW_SSH_PROBE_INTERVAL (float, seconds; default 1.0)
        * FLOW_SSH_MAX_BACKOFF (int, seconds; default 8)
        * FLOW_SSH_BACKOFF_MULTIPLIER (float; default 1.5)
    """

    def __init__(self, provider: object | None = None):
        import os as _os

        self.provider = provider
        # Allow runtime tuning without code changes
        try:
            self.max_backoff = int(_os.getenv("FLOW_SSH_MAX_BACKOFF", "8"))
        except Exception:  # noqa: BLE001
            self.max_backoff = 8
        try:
            self.backoff_multiplier = float(_os.getenv("FLOW_SSH_BACKOFF_MULTIPLIER", "1.5"))
        except Exception:  # noqa: BLE001
            self.backoff_multiplier = 1.5

    def wait_for_ssh(
        self,
        task: Task,
        timeout: int | None = None,
        probe_interval: float = 1.0,
        progress_callback: Callable[[str], None] | None = None,
        node: int | None = None,
    ) -> SSHConnectionInfo:
        import os as _os

        # Delegate to shared API to wait for ssh info first
        try:
            task = wait_for_task_ssh_info(
                task=task, provider=self.provider, timeout=timeout or 1200, show_progress=False
            )
        except SSHNotReadyError as e:
            raise TimeoutError(str(e)) from e

        connection = SSHConnectionInfo(
            host=task.host(node),
            port=int(getattr(task, "ssh_port", 22)),
            user=getattr(task, "ssh_user", "ubuntu"),
            key_path=self._get_ssh_key_path(task),
            task_id=task.task_id,
            proxyjump=None,
        )

        # Best-effort: compute ProxyJump when instance has only a private IP.
        # Prefer provider hints when available (provider_metadata["ssh_proxyjump"]).
        try:
            # Pull a fresh task view that may include provider_metadata from the resolver path
            fresh = None
            if getattr(self.provider, "get_task", None):
                fresh = self.provider.get_task(task.task_id)
            task_meta = getattr(fresh or task, "provider_metadata", {}) or {}
            pj = task_meta.get("ssh_proxyjump")
            if pj:
                connection.proxyjump = str(pj)
            else:
                # Heuristic: if a private IP exists and differs from resolved host, use ProxyJump
                priv = None
                try:
                    if getattr(self.provider, "get_task_instances", None):
                        inst = self.provider.get_task_instances(task.task_id)
                        sel = inst[0] if inst else None
                        priv = getattr(sel, "private_ip", None)
                except Exception:  # noqa: BLE001
                    priv = None
                if priv:
                    from ipaddress import ip_address as _ip

                    try:
                        is_private = not _ip(str(priv)).is_global
                    except Exception:  # noqa: BLE001
                        is_private = False
                    if is_private and str(priv) != str(connection.host):
                        # Jump via the current host:port to reach the private IP directly
                        connection.proxyjump = (
                            f"{connection.user}@{connection.host}:{int(connection.port or 22)}"
                        )
                        connection.host = str(priv)
                        connection.port = 22
        except Exception:  # noqa: BLE001
            # Non-fatal; proceed without ProxyJump if unavailable
            pass

        # Quick readiness loop
        import time as _t

        start = _t.time()
        # Respect env override even if caller didn't pass a custom interval
        try:
            if "FLOW_SSH_PROBE_INTERVAL" in _os.environ:
                probe_interval = float(_os.environ["FLOW_SSH_PROBE_INTERVAL"])  # type: ignore[assignment]
        except Exception:  # noqa: BLE001
            pass
        interval = max(0.5, float(probe_interval or 1.0))
        while True:
            elapsed = _t.time() - start
            if timeout and elapsed >= timeout:
                raise TimeoutError(f"SSH connection timeout after {int(elapsed)}s")

            if progress_callback:
                mins, secs = divmod(int(elapsed), 60)
                progress_callback(f"Waiting for SSH ({mins}m {secs}s elapsed)")

            prefix_args = None
            try:
                if connection.proxyjump:
                    prefix_args = ["-J", str(connection.proxyjump)]
            except Exception:  # noqa: BLE001
                prefix_args = None
            if SshStack.is_ssh_ready(
                user=connection.user,
                host=connection.host,
                port=connection.port,
                key_path=connection.key_path,
                prefix_args=prefix_args,
            ):
                return connection

            _t.sleep(min(interval, self.max_backoff))
            interval = min(self.max_backoff, interval * float(self.backoff_multiplier or 1.5))

    def _get_ssh_key_path(self, task: Task) -> Path:
        # Provider-backed resolution if available
        if getattr(self.provider, "get_task_ssh_connection_info", None):
            result = self.provider.get_task_ssh_connection_info(task.task_id)
            if isinstance(result, SSHKeyNotFoundError):
                raise RuntimeError(f"Failed to resolve SSH key: {result.message}")
            return result

        # Fallbacks
        default = Path.home() / ".ssh" / "id_rsa"
        if default.exists():
            return default
        raise RuntimeError("No SSH key available; set provider or ensure default key exists")
