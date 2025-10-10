"""SSH connection utilities for CLI commands.

This module provides shared SSH connection establishment and validation utilities
that can be used across multiple CLI commands like ssh, upload-code, port-forward, etc.

The utilities handle:
- SSH handshake checking with timeline progress
- Interactive SSH key prompting and resolution
- Connection validation and error handling
"""

from __future__ import annotations

import logging
import os
import subprocess
import time as _t
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

import click

from flow.adapters.providers.builtin.mithril.domain.models import PlatformSSHKey
from flow.adapters.providers.builtin.mithril.remote.errors import SshAuthenticationError
from flow.cli.commands.base import console
from flow.cli.utils.ssh_helpers import SshStack as _S
from flow.cli.utils.step_progress import SSHWaitProgressAdapter, StepTimeline
from flow.cli.utils.timeline_context import (
    ensure_timeline,
    finish_current_timeline,
)
from flow.core.keys.identity import store_key_metadata
from flow.core.keys.resolution import resolve_env_key_path
from flow.core.utils.ssh_key import match_local_key_to_platform
from flow.core.utils.ssh_key_cache import SSHKeyCache
from flow.domain.ssh import SSHKeyNotFoundError
from flow.errors import FlowError
from flow.sdk.ssh import SshStack as _CoreS

if TYPE_CHECKING:
    from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class PermissionCheckResult(Enum):
    """Result of SSH key permission check and resolution attempt."""

    NOT_PERMISSION_ERROR = "not_permission_error"  # Not a permission error
    PERMISSION_FIXED = "permission_fixed"  # Was permission error, successfully fixed
    PERMISSION_FIX_FAILED = "permission_fix_failed"  # Was permission error, fix failed
    USER_CANCELLED = "user_cancelled"  # Was permission error, user declined fix


def is_file_permission_error(error: SshAuthenticationError) -> bool:
    """Check if SSH error is related to file permissions vs generic auth failure."""
    error_text = str(error).lower()
    stderr = getattr(error, "stderr", "").lower() if hasattr(error, "stderr") else ""

    # Check for specific file permission error patterns
    permission_patterns = [
        "bad permissions",
        "permissions are too open",
        "permissions too open",
        "insecure permissions",
        "unprotected private key file",
    ]

    full_text = f"{error_text} {stderr}"

    return any(pattern in full_text for pattern in permission_patterns)


def check_and_resolve_if_key_permission_error(
    error: SshAuthenticationError,
    ssh_key_path: Path,
    timeline: StepTimeline | None = None,
) -> PermissionCheckResult:
    """Check if SSH error is a key permission issue and attempt to resolve it.

    Args:
        error: The SSH authentication error to check
        ssh_key_path: Path to the SSH key that failed
        timeline: Optional timeline instance for progress reporting

    Returns:
        PermissionCheckResult indicating what happened
    """
    logger.debug(f"Checking SSH key permission error: {error}")

    # First, check if this is actually a permission error
    if not is_file_permission_error(error):
        logger.debug("Not a permission error")
        return PermissionCheckResult.NOT_PERMISSION_ERROR

    logger.debug(f"Detected permission error for key: {ssh_key_path}")

    # Show the auto-fix option
    console.print("\n[yellow]SSH Key Permission Error[/yellow]")
    console.print(f"  Incorrect permissions on key file: {ssh_key_path}")
    try:
        current_perms = oct(ssh_key_path.stat().st_mode)[-3:]
        console.print(f"  Current permissions: {current_perms}")
    except OSError:
        pass  # File might not exist or be readable
    console.print(f"\nTo resolve: [accent]chmod 600 {ssh_key_path}[/accent]")

    # Pause timeline during interactive prompt to avoid display conflicts
    if timeline:
        finish_current_timeline()

    # Ask user if they want to fix it
    try:
        if click.confirm("Apply fix?", default=True):
            console.print(f"[dim]Running: chmod 600 {ssh_key_path}[/dim]")
            try:
                os.chmod(ssh_key_path, 0o600)
                console.print("[green]✓ Fixed key permissions[/green]")
                ensure_timeline()
                return PermissionCheckResult.PERMISSION_FIXED
            except OSError as e:
                console.print(f"[red]✗ Failed to fix permissions: {e}[/red]")
                return PermissionCheckResult.PERMISSION_FIX_FAILED
        else:
            console.print("[dim]Permission fix skipped[/dim]")
            return PermissionCheckResult.USER_CANCELLED

    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Operation cancelled[/dim]")
        return PermissionCheckResult.USER_CANCELLED


def check_ssh_permission_error(
    ssh_key_path: Path, task: Task, prefix_args: list[str] | None
) -> bool:
    """Run SSH command to check if it's failing due to permission errors.

    Args:
        ssh_key_path: Path to SSH key file
        task: Task object with SSH connection info
        prefix_args: SSH prefix arguments (e.g., ProxyJump)

    Returns:
        True if SSH is failing due to permission errors, False otherwise
    """
    # Build the same SSH command that is_ssh_ready uses
    probe_prefix: list[str] = []
    if prefix_args:
        probe_prefix.extend(list(prefix_args))
    probe_prefix.extend(
        [
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=4",
            "-o",
            "ConnectionAttempts=1",
        ]
    )
    test_cmd = _S.build_ssh_command(
        user=getattr(task, "ssh_user", "ubuntu"),
        host=task.ssh_host,
        port=get_ssh_port(task),
        key_path=ssh_key_path,
        use_mux=False,
        prefix_args=probe_prefix,
        remote_command="echo SSH_OK",
    )
    try:
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=4)
        logger.debug(f"SSH permission check: exit={result.returncode}, stderr={result.stderr}")

        # Check for permission error patterns in stderr
        if result.stderr:
            stderr_lower = result.stderr.lower()
            permission_patterns = [
                "bad permissions",
                "permissions are too open",
                "permissions too open",
                "insecure permissions",
                "unprotected private key file",
            ]

            for pattern in permission_patterns:
                if pattern in stderr_lower:
                    logger.debug(f"Permission error pattern found: {pattern}")
                    return True

    except subprocess.TimeoutExpired:
        logger.debug("SSH permission check timed out")

    return False


def maybe_wait_handshake(client, task: Task, timeline) -> None:
    """Wait for SSH handshake; fail fast if it never becomes ready.

    Previously, we would continue even when the handshake never succeeded,
    which could lead to an indefinite hang in the interactive ssh process
    (e.g., TCP open on a bastion/load-balancer that never completes SSH).
    Now we surface a clear, bounded failure with suggestions.

    Args:
        client: Flow client instance
        task: Task to check SSH connection for
        timeline: Timeline instance for progress reporting

    Raises:
        SystemExit: If SSH handshake fails within timeout
    """
    if not getattr(task, "ssh_host", None):
        logger.debug("No SSH host found on task, skipping handshake")
        return

    logger.debug(f"Starting SSH handshake for task {task.task_id}")
    logger.debug(f"SSH host: {task.ssh_host}, port: {get_ssh_port(task)}")

    user_provided_key = False
    platform_keys = None
    ssh_key_path = client.get_task_ssh_connection_info(task.task_id)
    logger.debug(f"Initial SSH key resolution result: {type(ssh_key_path)} - {ssh_key_path}")

    env_path = resolve_env_key_path(["MITHRIL_SSH_KEY"])
    if env_path is not None:
        user_provided_key = True
        logger.debug("MITHRIL_SSH_KEY override detected, will store association on success")

    if isinstance(ssh_key_path, SSHKeyNotFoundError):
        logger.debug("SSH key not found, prompting user for key path")
        # Get platform keys from the task object
        platform_keys = task.get_ssh_keys()
        logger.debug(
            f"Platform keys available: {[k.name + ' (' + k.fid + ')' for k in platform_keys]}"
        )

        # Pause timeline during interactive prompt to avoid display conflicts
        finish_current_timeline()
        ssh_key_path = prompt_for_ssh_key(platform_keys)
        user_provided_key = True
        logger.debug(f"User provided SSH key path: {ssh_key_path}")

    else:
        logger.debug(f"Using resolved SSH key path: {ssh_key_path}")

    try:
        # Verify key file exists and is readable
        if ssh_key_path:
            key_path = Path(ssh_key_path)
            if not key_path.exists():
                logger.error(f"SSH key file does not exist: {key_path}")
                timeline.fail_step(f"SSH key file not found: {key_path}")
                raise SystemExit(1)
            logger.debug(f"SSH key file exists and is readable: {key_path}")
            logger.debug(f"SSH key file permissions: {oct(key_path.stat().st_mode)[-3:]}")

        handshake_seconds = int(os.getenv("FLOW_SSH_HANDSHAKE_SEC", "1200"))

        timeline = ensure_timeline()
        step_idx = timeline.add_step(
            "Establishing SSH session",
            show_bar=True,
            estimated_seconds=handshake_seconds,
            show_estimate=False,
        )
        adapter = SSHWaitProgressAdapter(timeline, step_idx, handshake_seconds)
        with adapter:
            start_wait = _t.time()
            # Include ProxyJump for readiness checks when provider supplies it
            pj = (getattr(task, "provider_metadata", {}) or {}).get("ssh_proxyjump")
            pfx = ["-J", str(pj)] if pj else None

            attempt = 0
            while True:
                attempt += 1
                elapsed = _t.time() - start_wait
                logger.debug(f"SSH handshake attempt {attempt}, elapsed: {elapsed:.1f}s")

                try:
                    # If we have a key, do a full BatchMode probe; otherwise check SSH banner only
                    if ssh_key_path and _S.is_ssh_ready(
                        user=getattr(task, "ssh_user", "ubuntu"),
                        host=task.ssh_host,
                        port=get_ssh_port(task),
                        key_path=ssh_key_path,
                        prefix_args=pfx,
                    ):
                        # SSH connection successful! Store the key association permanently
                        if user_provided_key:
                            if not platform_keys:
                                platform_keys = task.get_ssh_keys()
                            logger.debug("Storing SSH key association for future use")
                            store_ssh_key_association(ssh_key_path, platform_keys, task.task_id)
                        break
                    if (
                        not ssh_key_path
                        and _S.tcp_port_open(task.ssh_host, get_ssh_port(task))
                        and _CoreS.has_ssh_banner(task.ssh_host, get_ssh_port(task))
                    ):
                        break
                except SshAuthenticationError as e:
                    logger.debug(f"SSH authentication error: {e}")
                    # Check if this is a permission error and attempt to fix it
                    result = check_and_resolve_if_key_permission_error(
                        e, Path(ssh_key_path), timeline=timeline
                    )
                    if result == PermissionCheckResult.PERMISSION_FIXED:
                        logger.debug("Retrying SSH connection after fixing permissions")
                        continue  # Retry immediately without sleeping
                    else:
                        # Authentication error that couldn't be fixed
                        timeline.fail_step(f"SSH authentication failed: {e}")
                        finish_current_timeline()

                        # Use FlowError for consistent error display
                        raise FlowError(
                            f"SSH Authentication Failed\n\n"
                            f"The SSH key '{ssh_key_path}' was rejected by the server.\n"
                            f"This usually means the key doesn't match any authorized keys on the remote instance.",
                            suggestions=[
                                "Try again and enter a different key when prompted.",
                                f"Use key override: 'export MITHRIL_SSH_KEY=/path/to/key flow ssh {task.task_id}'.",
                                f"Check 'flow status {task.task_id}' for task details.",
                                "Verify you have the correct SSH private key for this task.",
                            ],
                        )

                if _t.time() - start_wait > handshake_seconds:
                    # Surface a clear failure rather than proceeding to a hang
                    logger.debug(f"SSH handshake timeout after {handshake_seconds} seconds")
                    timeline.fail_step(
                        "SSH did not become ready in time. Check 'flow status' and 'flow logs --source host'."
                    )
                    raise SystemExit(1)

                adapter.update_eta()
                logger.debug("Sleeping 2 seconds before next attempt...")
                _t.sleep(2)
    finally:
        timeline.finish()


def prompt_for_ssh_key(platform_keys: list[PlatformSSHKey]) -> Path | None:
    """Prompt user for SSH key path with validation.

    Args:
        platform_keys: List of platform SSH keys from the task

    Returns:
        Path to the selected SSH private key, or None if user cancels

    Raises:
        SystemExit: If user cancels or provides invalid input
    """
    click.echo("\nNo local SSH key found matching any of:")

    if platform_keys:
        for key in platform_keys:
            click.echo(f"  • {key.name} ({key.fid})")

    click.echo("\nCommon key locations: ~/.ssh, ~/Downloads")

    while True:
        try:
            path_str = click.prompt(
                "Enter path to SSH key (or 'q' to abort)",
                type=str,
                default="",
                show_default=False,
            )

            # Allow user to quit
            if path_str.lower() in ("q", "quit", "exit"):
                raise SystemExit(1)

            # Skip empty inputs
            if not path_str.strip():
                click.echo("Error: Path cannot be empty")
                continue

            # Validate the path
            path = Path(path_str.strip()).expanduser().resolve()
            if not path.exists():
                click.echo(f"Error: File does not exist: {path}")
                continue
            if not path.is_file():
                click.echo(f"Error: Path is not a file: {path}")
                continue
            if path.suffix == ".pub":
                click.echo(f"Error: This appears to be a public key, not a private key: {path}")
                continue

            return path

        except (click.Abort, KeyboardInterrupt):
            click.echo("\nOperation cancelled.")
            raise SystemExit(1)


def store_ssh_key_association(
    ssh_key_path: Path, platform_keys: list[PlatformSSHKey], task_id: str
) -> None:
    """Store SSH key association for future use."""
    # Find which specific platform key matches this local key
    matched_platform_id = match_local_key_to_platform(
        ssh_key_path, platform_keys, match_by_name=True
    )

    if matched_platform_id:
        # Find the matching platform key object
        matched_key = next(
            (key for key in platform_keys if key.fid == matched_platform_id),
            None,
        )

        if matched_key:
            # Store only the matching key association
            store_key_metadata(
                key_id=matched_platform_id,
                key_name=matched_key.name,
                private_key_path=ssh_key_path,
                project_id=None,  # Could get project_id from provider if needed
                auto_generated=False,
            )
            logger.debug(f"Stored key association: {matched_platform_id} -> {ssh_key_path}")

            # Also cache for immediate reuse
            ssh_cache = SSHKeyCache()
            ssh_cache.save_key_path(
                task_id,
                str(ssh_key_path),
                platform_key_ids=[matched_platform_id],
            )
        else:
            logger.debug(
                f"Could not find platform key object for matched ID: {matched_platform_id}"
            )
    else:
        logger.debug(f"Could not match local key {ssh_key_path} to any platform key")


def get_ssh_port(task, cached: dict | None = None, default: int = 22) -> int:
    """Get SSH port from cache first, then task attributes, with safe conversion.

    Args:
        task: Task object to extract port from
        cached: Optional cached task data
        default: Default port if none found (defaults to 22)

    Returns:
        SSH port as integer
    """

    def safe_int(value, fallback: int = default) -> int:
        """Safely convert value to int, returning fallback on failure."""
        try:
            return int(value) if value is not None else fallback
        except (ValueError, TypeError):
            return fallback

    # Try cache first
    if cached and cached.get("ssh_port") is not None:
        return safe_int(cached.get("ssh_port"), default)

    # Fallback to task attributes
    return safe_int(getattr(task, "ssh_port", None), default)


def resolve_endpoint(client, task, node: int | None = None):
    """Resolve the freshest SSH endpoint for the given task/node, best-effort.

    Args:
        client: Flow client instance
        task: Task to resolve SSH endpoint for
        node: Node index for multi-instance tasks

    Returns:
        Updated task with SSH endpoint information
    """
    # Short-circuit to avoid network calls when endpoint is already present
    if getattr(task, "ssh_host", None) and getattr(task, "ssh_port", None):
        return task
    try:
        host, port = client.resolve_ssh_endpoint(task.task_id, node=node)
        task.ssh_host = host
        task.ssh_port = get_ssh_port(task, {"ssh_port": port})
    except (FlowError, ValueError, AttributeError):
        pass
    return task
