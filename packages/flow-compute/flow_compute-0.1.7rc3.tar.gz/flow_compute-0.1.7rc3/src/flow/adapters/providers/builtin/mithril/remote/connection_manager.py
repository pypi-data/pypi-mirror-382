from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from flow.adapters.providers.builtin.mithril.core.constants import (
    EXPECTED_PROVISION_MINUTES,
    SSH_QUICK_RETRY_ATTEMPTS,
    SSH_QUICK_RETRY_MAX_SECONDS,
    SSH_READY_WAIT_SECONDS,
)
from flow.adapters.providers.builtin.mithril.remote.errors import (
    SshConnectionError,
    make_error,
)
from flow.adapters.transport.ssh.ssh_stack import SshStack
from flow.domain.ssh import SSHKeyNotFoundError
from flow.sdk.ssh_utils import SSHNotReadyError, wait_for_task_ssh_info

logger = logging.getLogger(__name__)


@dataclass
class ConnectionDetails:
    """Holds resolved and validated SSH connection details."""

    user: str
    host: str
    port: int
    key_path: Path
    cache_key: tuple | None = None
    task: object | None = None
    proxyjump: str | None = None


class SshConnectionManager:
    """Centralizes SSH setup, validation, retries, and caching."""

    def __init__(self, provider):
        self.provider = provider
        self._ssh_last_success: dict[tuple, float] = {}

    # Cache helpers --------------------------------------------------------
    def _build_cache_key(self, task_id: str, task, node: int | None) -> tuple | None:
        try:
            try:
                project_id = self.provider.project_id
            except Exception:  # noqa: BLE001
                project_id = "default"
            return (
                project_id,
                task_id,
                int(node or -1),
                task.ssh_host,
                int(getattr(task, "ssh_port", 22)),
            )
        except Exception:  # noqa: BLE001
            return None

    # Public wrapper used by callers to avoid using a private method
    def build_cache_key(self, task_id: str, task, node: int | None) -> tuple | None:
        return self._build_cache_key(task_id, task, node)

    def check_recent_success(self, cache_key: tuple | None, ttl_seconds: float = 60.0) -> bool:
        if cache_key is None:
            return False
        try:
            ts = self._ssh_last_success.get(cache_key)
            return ts is not None and (time.time() - ts) < ttl_seconds
        except Exception:  # noqa: BLE001
            return False

    def mark_success(self, cache_key: tuple | None) -> None:
        if cache_key is None:
            return
        try:
            self._ssh_last_success[cache_key] = time.time()
        except Exception:  # noqa: BLE001
            pass

    def bust_cache(self, cache_key: tuple | None) -> None:
        if cache_key is None:
            return
        try:
            self._ssh_last_success.pop(cache_key, None)
        except Exception:  # noqa: BLE001
            pass

    # Core establishment ---------------------------------------------------
    def establish_connection(
        self,
        task_id: str,
        request_id: str,
        timeout_seconds: int,
        node: int | None = None,
        quick_ready: bool = False,
    ) -> ConnectionDetails:
        """Resolve SSH details and ensure the remote host is ready."""
        # Resolve endpoint first (host/port)
        task = self._resolve_endpoint(task_id, node, request_id)

        # Compute an effective timeout that respects caller intent
        # If quick_ready: cap the wait to a small window, NEVER exceed caller timeout
        base_timeout = timeout_seconds if timeout_seconds is not None else SSH_READY_WAIT_SECONDS
        quick_cap = SSH_QUICK_RETRY_MAX_SECONDS * 2
        effective_timeout = min(base_timeout, quick_cap) if quick_ready else base_timeout

        # Build cache key and fast-path if we recently connected successfully
        cache_key = self._build_cache_key(task_id, task, node)

        # Ensure SSH key path (cheap/local)
        key_path = self._resolve_ssh_key(task_id, request_id)

        if self.check_recent_success(cache_key):
            return ConnectionDetails(
                user=getattr(task, "ssh_user", "ubuntu"),
                host=task.ssh_host,
                port=int(getattr(task, "ssh_port", 22)),
                key_path=Path(key_path),
                cache_key=cache_key,
                task=task,
                proxyjump=(getattr(task, "provider_metadata", {}) or {}).get("ssh_proxyjump"),
            )

        # Ensure SSH info exists (and refresh if needed)
        # Skip this if we already have ssh_host from node-specific resolution
        # because wait_for_task_ssh_info doesn't respect the node parameter
        if not task.ssh_host:
            try:
                task = wait_for_task_ssh_info(
                    task=task,
                    provider=self.provider,
                    timeout=effective_timeout,
                    show_progress=False,
                )
            except SSHNotReadyError as e:
                raise make_error(
                    f"No SSH access for task {task_id}: {e!s}",
                    request_id,
                    suggestions=e.suggestions,
                    cls=SshConnectionError,
                ) from e

        # Wait for SSH service readiness using shared transport waiter
        try:
            from flow.adapters.transport.ssh import ExponentialBackoffSSHWaiter

            waiter = ExponentialBackoffSSHWaiter(self.provider)
            # Attach resolved ssh_port
            task.ssh_port = int(getattr(task, "ssh_port", 22))
            waiter.wait_for_ssh(task=task, timeout=effective_timeout, progress_callback=None)
        except Exception:  # noqa: BLE001
            # Fallback to local readiness probe on failure to import or waiter error
            self._ensure_ssh_ready(task, key_path, request_id)

        # Mark recent success for subsequent quick operations
        self.mark_success(cache_key)

        return ConnectionDetails(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=int(getattr(task, "ssh_port", 22)),
            key_path=Path(key_path),
            cache_key=cache_key,
            task=task,
            proxyjump=(getattr(task, "provider_metadata", {}) or {}).get("ssh_proxyjump"),
        )

    # Internal helpers -----------------------------------------------------
    def _resolve_endpoint(self, task_id: str, node: int | None, request_id: str):
        task = self.provider.get_task(task_id)

        # If node is specified and task has ssh_hosts, use task.host(node) directly
        if node is not None and hasattr(task, "host") and callable(task.host):
            try:
                node_host = task.host(node)
                if node_host:
                    task.ssh_host = node_host
                    # Keep existing ssh_port or default to 22
                    if not getattr(task, "ssh_port", None):
                        task.ssh_port = 22
                    # Skip the full resolver since we already have the host
                    return task
            except Exception:  # noqa: BLE001
                # Fall back to resolver if task.host() fails
                pass

        # Fresh resolve endpoint; handle multi-node selection
        try:
            host, port = self.provider.resolve_ssh_endpoint(task_id, node=node)
            task.ssh_host = host
            try:
                task.ssh_port = int(port or 22)
            except Exception:  # noqa: BLE001
                task.ssh_port = 22
        except Exception as e:  # noqa: BLE001
            if not task.ssh_host:
                raise make_error(str(e), request_id)

        # Node-specific resolution is already handled above via task.host(node)
        # No need for additional instance lookup here

        # Compute bastion ProxyJump if instance has only a private IP and the selected
        # endpoint looks public (common in Mithril where the project exposes a bastion).
        try:
            from ipaddress import ip_address as _ip

            def _is_private(ip: str) -> bool:
                try:
                    return not _ip(str(ip)).is_global
                except Exception:  # noqa: BLE001
                    return False

            # Select instance doc to read private_ip
            # Only proceed if we can get actual Instance objects (not just instance IDs)
            selected = None
            if hasattr(task, "get_instances") and callable(task.get_instances):
                try:
                    instances = task.get_instances()
                    if instances:
                        index = int(node or 0)
                        selected = instances[index] if 0 <= index < len(instances) else instances[0]
                except Exception:  # noqa: BLE001
                    pass
            priv = getattr(selected, "private_ip", None) if selected else None
            if priv and _is_private(priv) and str(task.ssh_host) != str(priv):
                # Stash proxyjump for downstream consumers and repoint to private ip
                pj = f"{getattr(task, 'ssh_user', 'ubuntu')}@{task.ssh_host}:{int(getattr(task, 'ssh_port', 22) or 22)}"
                meta = getattr(task, "provider_metadata", {}) or {}
                meta["ssh_proxyjump"] = pj
                task.provider_metadata = meta  # type: ignore[assignment]
                task.ssh_host = str(priv)
                task.ssh_port = 22
        except Exception:  # noqa: BLE001
            pass

        return task

    def _resolve_ssh_key(self, task_id: str, request_id: str) -> Path:
        ssh_key_path = self.provider.get_task_ssh_connection_info(task_id)
        if isinstance(ssh_key_path, SSHKeyNotFoundError):
            raise make_error(
                f"SSH key resolution failed: {ssh_key_path.message}",
                request_id,
                cls=SshConnectionError,
            )
        return Path(ssh_key_path)

    def _ensure_ssh_ready(self, task, key_path: Path, request_id: str) -> None:
        if SshStack.is_ssh_ready(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=getattr(task, "ssh_port", 22),
            key_path=Path(key_path),
        ):
            return

        start_time = time.time()
        for attempt in range(SSH_QUICK_RETRY_ATTEMPTS):
            elapsed = time.time() - start_time
            if elapsed > SSH_QUICK_RETRY_MAX_SECONDS:
                break

            time.sleep(2 * (attempt + 1))
            if SshStack.is_ssh_ready(
                user=getattr(task, "ssh_user", "ubuntu"),
                host=task.ssh_host,
                port=getattr(task, "ssh_port", 22),
                key_path=Path(key_path),
            ):
                return

        # Before surfacing a generic readiness error, run one last probe to capture
        # a specific authentication failure (e.g., Permission denied (publickey)).
        try:
            probe_cmd = SshStack.build_ssh_command(
                user=getattr(task, "ssh_user", "ubuntu"),
                host=task.ssh_host,
                port=getattr(task, "ssh_port", 22),
                key_path=Path(key_path),
                use_mux=False,
                prefix_args=[
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=4",
                    "-o",
                    "ConnectionAttempts=1",
                ],
                remote_command="echo SSH_OK",
            )
            result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=6)
            if result.returncode != 0:
                stderr = (result.stderr or "").lower()
                if "permission denied" in stderr or "publickey" in stderr:
                    from flow.adapters.providers.builtin.mithril.remote.errors import (
                        SshConnectionError,
                        make_error,
                    )

                    # Clear cached key path and retry resolve once
                    try:
                        from flow.core.utils.ssh_key_cache import SSHKeyCache as _KC

                        _KC().clear()
                    except Exception:  # noqa: BLE001
                        pass

                    new_key_path = self.provider.get_task_ssh_connection_info(task.task_id)
                    if (
                        isinstance(new_key_path, Path)
                        and str(new_key_path) != str(key_path)
                        and SshStack.is_ssh_ready(
                            user=getattr(task, "ssh_user", "ubuntu"),
                            host=task.ssh_host,
                            port=getattr(task, "ssh_port", 22),
                            key_path=Path(key_path),
                        )
                    ):
                        return

                    suggestions = [
                        "Verify the task was launched with your SSH key",
                        "Run: flow ssh-key list (ensure your key is on the project)",
                        "Override temporarily: MITHRIL_SSH_KEY=/path/to/private/key flow <cmd>",
                    ]
                    raise make_error(
                        (
                            "SSH authentication failed (Permission denied).\n"
                            f"Key used: {Path(key_path).expanduser()!s}"
                        ),
                        request_id,
                        suggestions=suggestions,
                        cls=SshConnectionError,
                    )
        except Exception:  # noqa: BLE001
            # Best-effort diagnostics; fall back to generic flow below
            pass

        # Build nuanced error messaging based on instance status/age
        try:
            instance_age_seconds = float(getattr(task, "instance_age_seconds", 0) or 0)
        except Exception:  # noqa: BLE001
            instance_age_seconds = 0.0
        capped_seconds = max(0.0, min(instance_age_seconds, 7 * 24 * 3600))
        instance_age_minutes = int(capped_seconds // 60)

        instance_status = getattr(task, "instance_status", None)

        if instance_status == "STATUS_STARTING":
            raise make_error(
                "Instance is starting up. SSH will be available once startup completes. "
                "Please try again in a moment or check 'flow status' for current state.",
                request_id,
                cls=SshConnectionError,
            )
        elif instance_age_minutes < EXPECTED_PROVISION_MINUTES:
            raise make_error(
                f"Instance is still starting up ({instance_age_minutes} minutes elapsed). "
                f"SSH startup can take up to {EXPECTED_PROVISION_MINUTES} minutes. "
                f"Please try again in a moment.",
                request_id,
                cls=SshConnectionError,
            )
        else:
            raise make_error(
                f"SSH service on {getattr(task, 'ssh_host', 'host')} is not responding. "
                f"The instance may still be starting up (can take up to {EXPECTED_PROVISION_MINUTES} minutes). "
                f"Please try again in a moment.",
                request_id,
                cls=SshConnectionError,
            )
