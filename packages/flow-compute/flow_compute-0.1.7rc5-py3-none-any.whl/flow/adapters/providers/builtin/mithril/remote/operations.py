from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from flow.adapters.providers.builtin.mithril.core.constants import (
    EXPECTED_PROVISION_MINUTES,
    SSH_READY_WAIT_SECONDS,
)
from flow.adapters.providers.builtin.mithril.remote.connection_manager import (
    SshConnectionManager,
)
from flow.adapters.providers.builtin.mithril.remote.errors import (
    RemoteExecutionError,
    SshConnectionError,
    make_error,
)
from flow.adapters.providers.builtin.mithril.remote.recording import build_recording_command
from flow.adapters.providers.builtin.mithril.remote.utils import new_request_id
from flow.adapters.transport.ssh.ssh_stack import SshStack
from flow.domain.ssh import SSHKeyNotFoundError
from flow.protocols.remote_operations import RemoteOperationsProtocol as IRemoteOperations

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider import MithrilProvider


logger = logging.getLogger(__name__)


class MithrilRemoteOperations(IRemoteOperations):
    """Mithril remote operations via SSH (refactored)."""

    def __init__(self, provider: MithrilProvider):
        self.provider = provider
        self.connection_manager = SshConnectionManager(provider)

    # ------------------------------------------------------------------
    # Command execution
    # ------------------------------------------------------------------
    def execute_command(
        self, task_id: str, command: str, timeout: int | None = None, *, node: int | None = None
    ) -> str:
        request_id = new_request_id("ssh-exec")

        try:
            # Use a shorter readiness window for command exec to reduce latency
            conn = self.connection_manager.establish_connection(
                task_id=task_id,
                request_id=request_id,
                timeout_seconds=(timeout or SSH_READY_WAIT_SECONDS),
                node=node,
                quick_ready=True,
            )
        except SshConnectionError:
            raise
        except Exception as e:  # noqa: BLE001
            raise make_error(f"SSH setup failed: {e!s}", request_id)

        # Optional debug: print resolved SSH details for logs/exec paths
        try:
            if os.getenv("FLOW_LOGS_DEBUG") == "1" or os.getenv("FLOW_SSH_DEBUG") == "1":
                logger.debug(
                    "SSH exec details (request_id=%s): user=%s host=%s port=%s key=%s cmd=%r",
                    request_id,
                    getattr(conn, "user", "ubuntu"),
                    getattr(conn, "host", ""),
                    getattr(conn, "port", 22),
                    str(getattr(conn, "key_path", "")),
                    command,
                )
        except Exception:  # noqa: BLE001
            pass

        prefix: list[str] | None = None
        if getattr(conn, "proxyjump", None):
            prefix = ["-J", str(conn.proxyjump)]
        ssh_cmd = SshStack.build_ssh_command(
            user=conn.user,
            host=conn.host,
            port=conn.port,
            key_path=Path(conn.key_path),
            prefix_args=prefix,
            remote_command=command,
        )

        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=timeout if timeout else None,
            )
            if result.returncode != 0:
                stderr = (result.stderr or "").lower()
                if "permission denied" in stderr or "publickey" in stderr:
                    suggestions = [
                        "Verify the task was launched with your SSH key",
                        "Run: flow ssh-key list (confirm your key on the project)",
                        "Optionally override: MITHRIL_SSH_KEY=/path/to/private/key flow <cmd>",
                    ]
                    raise make_error(
                        (
                            "SSH authentication failed (Permission denied).\n"
                            f"Key used: {Path(conn.key_path).expanduser()!s}"
                        ),
                        request_id,
                        suggestions=suggestions,
                    )
                if "connection closed" in stderr or "connection reset" in stderr:
                    raise make_error(
                        "SSH connection was closed. The instance may still be starting up. "
                        "Please wait a moment and try again.",
                        request_id,
                    )
                raise make_error(f"Command failed: {result.stderr}", request_id)
            # Mark a recent success so subsequent quick ops (preflights) skip heavy waits
            try:
                self.connection_manager.mark_success(getattr(conn, "cache_key", None))
            except Exception:  # noqa: BLE001
                pass
            return result.stdout
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Command timed out after {timeout} seconds") from e
        except RemoteExecutionError:
            raise
        except Exception as e:  # noqa: BLE001
            raise make_error(f"SSH execution failed: {e!s}", request_id)

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------
    def stream_command(self, task_id: str, command: str) -> Iterator[str]:
        request_id = new_request_id("ssh-stream")

        try:
            conn = self.connection_manager.establish_connection(
                task_id=task_id,
                request_id=request_id,
                timeout_seconds=SSH_READY_WAIT_SECONDS,
            )
        except SshConnectionError:
            raise
        except Exception as e:  # noqa: BLE001
            raise make_error(f"SSH setup failed: {e!s}", request_id)

        # Optional debug: print resolved SSH details for streaming path
        try:
            if os.getenv("FLOW_LOGS_DEBUG") == "1" or os.getenv("FLOW_SSH_DEBUG") == "1":
                logger.debug(
                    "SSH stream details (request_id=%s): user=%s host=%s port=%s key=%s cmd=%r",
                    request_id,
                    getattr(conn, "user", "ubuntu"),
                    getattr(conn, "host", ""),
                    getattr(conn, "port", 22),
                    str(getattr(conn, "key_path", "")),
                    command,
                )
        except Exception:  # noqa: BLE001
            pass

        ssh_cmd = SshStack.build_ssh_command(
            user=conn.user,
            host=conn.host,
            port=conn.port,
            key_path=Path(conn.key_path),
            remote_command=command,
        )

        process = None
        try:
            process = subprocess.Popen(
                ssh_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            if process.stdout is not None:
                for line in iter(process.stdout.readline, ""):
                    yield line.rstrip("\n")

            process.wait()

            if process.returncode != 0 and process.returncode == 255:
                raise make_error("SSH connection error (exit code 255)", request_id)
        except GeneratorExit:
            if process and process.poll() is None:
                process.terminate()
        except RemoteExecutionError:
            raise
        except Exception as e:  # noqa: BLE001
            raise make_error(f"SSH streaming failed unexpectedly: {e!s}", request_id)
        finally:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

    # ------------------------------------------------------------------
    # Interactive shell
    # ------------------------------------------------------------------
    def open_shell(
        self,
        task_id: str,
        command: str | None = None,
        node: int | None = None,
        progress_context=None,
        record: bool = False,
    ) -> None:
        request_id = new_request_id("ssh-connect")

        # Resolve endpoint and SSH key without enforcing readiness yet
        # We keep the fast-path and special waiting logic for best UX.
        # Endpoint - use optimized path that respects node parameter
        task = self.provider.get_task(task_id)

        # Use task.host(node) directly if available for multi-instance tasks
        if node is not None and hasattr(task, "host") and callable(task.host):
            try:
                node_host = task.host(node)
                if node_host:
                    task.ssh_host = node_host
                    if not getattr(task, "ssh_port", None):
                        task.ssh_port = 22
            except Exception:  # noqa: BLE001
                pass  # Fall back to resolver
        # If task.ssh_host not set by node-specific path, use resolver
        if not getattr(task, "ssh_host", None):
            try:
                host, port = self.provider.resolve_ssh_endpoint(task_id, node=node)
                task.ssh_host = host
                try:
                    task.ssh_port = int(port or 22)
                except Exception:  # noqa: BLE001
                    task.ssh_port = 22
            except Exception as e:  # noqa: BLE001
                if not getattr(task, "ssh_host", None):
                    raise make_error(str(e), request_id)

        # SSH key path
        ssh_key_path = self.provider.get_task_ssh_connection_info(task_id)
        if isinstance(ssh_key_path, SSHKeyNotFoundError):
            raise make_error(f"SSH key resolution failed: {ssh_key_path.message}", request_id)

        # Build cache key for recent-success heuristics
        cache_key = self.connection_manager.build_cache_key(task_id, task, node)
        recent_success = self.connection_manager.check_recent_success(cache_key)

        # Fast TCP probe and optional immediate connect
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            _debug = bool((_settings.ssh or {}).get("debug", False))
            fast_flag = bool((_settings.ssh or {}).get("fast", False))
        except Exception:  # noqa: BLE001
            _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
            fast_flag = os.environ.get("FLOW_SSH_FAST") == "1"
        if _debug:
            try:
                logger.debug(
                    "SSH readiness probe for %s host=%s port=%s key=%s",
                    task_id,
                    task.ssh_host,
                    getattr(task, "ssh_port", 22),
                    str(ssh_key_path),
                )
            except Exception:  # noqa: BLE001
                pass

        pj = (getattr(task, "provider_metadata", {}) or {}).get("ssh_proxyjump")
        pfx = ["-J", str(pj)] if pj else None
        ssh_is_ready = SshStack.is_ssh_ready(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=getattr(task, "ssh_port", 22),
            key_path=Path(ssh_key_path),
            prefix_args=pfx,
        )

        # Optional debug: log resolved details for open_shell
        try:
            if os.getenv("FLOW_SSH_DEBUG") == "1":
                logger.debug(
                    "SSH open details (request_id=%s): user=%s host=%s port=%s key=%s ready=%s recent_success=%s command=%r",
                    request_id,
                    getattr(task, "ssh_user", "ubuntu"),
                    task.ssh_host,
                    getattr(task, "ssh_port", 22),
                    str(ssh_key_path),
                    bool(ssh_is_ready),
                    bool(recent_success),
                    command,
                )
        except Exception:  # noqa: BLE001
            pass

        try:
            # Do not take the fast-path when recording; we must wrap with 'script' to capture logs.
            # Also avoid fast-path unless SSH is actually ready to prevent confusing auth errors.
            if command is None and not record and (recent_success or ssh_is_ready or fast_flag):
                prefix: list[str] | None = None
                if pj:
                    prefix = ["-J", str(pj)]
                ssh_cmd = SshStack.build_ssh_command(
                    user=getattr(task, "ssh_user", "ubuntu"),
                    host=task.ssh_host,
                    port=getattr(task, "ssh_port", 22),
                    key_path=Path(ssh_key_path),
                    prefix_args=prefix,
                    use_mux=False,
                )
                try:
                    _debug = bool((_settings.ssh or {}).get("debug", False))
                except Exception:  # noqa: BLE001
                    _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
                if _debug:
                    logger.debug("SSH fast-path exec argv: %s", " ".join(ssh_cmd))
                fast_result = subprocess.run(ssh_cmd)
                if fast_result.returncode == 0:
                    # mark recent success for quicker follow-ups
                    try:
                        self.connection_manager.mark_success(cache_key)
                    except Exception:  # noqa: BLE001
                        pass
                    return
        except Exception:  # noqa: BLE001
            pass

        if progress_context and hasattr(progress_context, "update_message"):
            try:
                progress_context.update_message(
                    "SSH ready, connecting..." if ssh_is_ready else "Waiting for SSH to be ready..."
                )
            except Exception:  # noqa: BLE001
                pass

        # Wait for readiness if needed (short sleeps/backoff), unless we recently succeeded
        if not ssh_is_ready and not recent_success:
            start_time = time.time()
            timeout = SSH_READY_WAIT_SECONDS
            attempts = 0
            while time.time() - start_time < timeout:
                if SshStack.is_ssh_ready(
                    user=getattr(task, "ssh_user", "ubuntu"),
                    host=task.ssh_host,
                    port=getattr(task, "ssh_port", 22),
                    key_path=Path(ssh_key_path),
                ):
                    break
                wait_time = min(0.2 * (1 + attempts), 2.0)
                time.sleep(wait_time)
                attempts += 1
            else:
                # Fallback: try immediate interactive connect once
                try:
                    prefix = ["-J", str(pj)] if pj else None
                    ssh_cmd = SshStack.build_ssh_command(
                        user=getattr(task, "ssh_user", "ubuntu"),
                        host=task.ssh_host,
                        port=getattr(task, "ssh_port", 22),
                        key_path=Path(ssh_key_path),
                        use_mux=False,
                        prefix_args=prefix,
                    )
                    try:
                        from flow.application.config.runtime import (
                            settings as _settings,  # local import
                        )

                        _debug = bool((_settings.ssh or {}).get("debug", False))
                    except Exception:  # noqa: BLE001
                        _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
                    if _debug:
                        logger.debug("SSH fallback exec argv: %s", " ".join(ssh_cmd))
                    subprocess.run(ssh_cmd)
                    return
                except Exception:  # noqa: BLE001
                    pass
                raise make_error("SSH connection timed out", request_id)

        # Build base SSH command (avoid ControlMaster/MUX for initial interactive connect)
        prefix = ["-J", str(pj)] if pj else None
        ssh_cmd = SshStack.build_ssh_command(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=getattr(task, "ssh_port", 22),
            key_path=Path(ssh_key_path),
            use_mux=False,
            prefix_args=prefix,
        )

        # Apply recording wrapper if requested
        if record:
            remote_command, requires_tty = build_recording_command(command)
            if requires_tty:
                try:
                    ssh_cmd.insert(1, "-tt")
                except Exception:  # noqa: BLE001
                    ssh_cmd.append("-tt")
            ssh_cmd.append(remote_command)
        elif command:
            ssh_cmd.append(command)

        try:
            from flow.application.config.runtime import settings as _settings  # local import

            _debug = bool((_settings.ssh or {}).get("debug", False))
        except Exception:  # noqa: BLE001
            _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
        if _debug:
            try:
                logger.debug("SSH exec argv: %s", " ".join(ssh_cmd))
            except Exception:  # noqa: BLE001
                pass

        try:
            # Decide interactive vs non-interactive execution.
            # If the provided command launches an interactive login shell (e.g.,
            # "bash -lc \"cd <dir> && exec bash -l\""), we should allocate a TTY
            # and NOT capture output, otherwise the session appears to hang.
            interactive_markers = [
                "exec bash -l",
                "exec zsh -l",
                "exec sh -l",
                "exec fish -l",
            ]
            is_interactive_cmd = bool(
                command and any(marker in command for marker in interactive_markers)
            )
            # Also treat docker exec with TTY flags as interactive
            if (
                command
                and ("docker exec" in command)
                and any(flag in command for flag in [" -it", " --tty", " -t "])
            ):
                is_interactive_cmd = True

            if is_interactive_cmd:
                # Force TTY for remote command so the shell is interactive
                try:
                    ssh_cmd.insert(1, "-tt")
                except Exception:  # noqa: BLE001
                    ssh_cmd.append("-tt")
                ssh_cmd.append(command)  # run remote command but attach to user's TTY

                # Stop animation if still active before taking over terminal
                if (
                    progress_context
                    and hasattr(progress_context, "_active")
                    and progress_context._active
                ):  # type: ignore[attr-defined]
                    progress_context.__exit__(None, None, None)

                result = subprocess.run(ssh_cmd)
                if result.returncode == 0:
                    self.connection_manager.mark_success(cache_key)
                    return

                # Quick diagnostic probe to classify the failure and decide on retry
                try:
                    probe_cmd = SshStack.build_ssh_command(
                        user=getattr(task, "ssh_user", "ubuntu"),
                        host=task.ssh_host,
                        port=getattr(task, "ssh_port", 22),
                        key_path=Path(ssh_key_path),
                        use_mux=False,
                        prefix_args=(
                            [
                                "-o",
                                "BatchMode=yes",
                                "-o",
                                "ConnectTimeout=4",
                                "-o",
                                "ConnectionAttempts=1",
                            ]
                            + (["-J", str(pj)] if pj else [])
                        ),
                        remote_command="echo SSH_OK",
                    )
                    probe = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=6)
                    stderr_lower = (probe.stderr or "").lower()
                except Exception:  # noqa: BLE001
                    stderr_lower = ""

                transient_markers = (
                    "connection reset by peer",
                    "kex_exchange_identification",
                    "connection closed",
                )

                if any(m in stderr_lower for m in transient_markers) or result.returncode == 255:
                    # Retry up to 2 times with short backoff
                    for backoff in (1.5, 3.0):
                        time.sleep(backoff)
                        retry = subprocess.run(ssh_cmd)
                        if retry.returncode == 0:
                            self.connection_manager.mark_success(cache_key)
                            return
                    # Surface a clearer error after retries exhausted
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH connection was reset while the instance was initializing.\n"
                        "Please wait 1–2 minutes and try again.",
                        request_id,
                    )

                # Handle auth failures explicitly: clear caches, re-resolve key, and retry once without mux
                if ("permission denied" in stderr_lower) or ("publickey" in stderr_lower):
                    try:
                        from flow.core.utils.ssh_key_cache import SSHKeyCache as _KC

                        _KC().clear()
                    except Exception:  # noqa: BLE001
                        pass
                    try:
                        new_key_path = self.provider.get_task_ssh_connection_info(task_id)
                        if isinstance(new_key_path, Path):
                            ssh_key_path = str(new_key_path)
                        retry_cmd = SshStack.build_ssh_command(
                            user=getattr(task, "ssh_user", "ubuntu"),
                            host=task.ssh_host,
                            port=getattr(task, "ssh_port", 22),
                            key_path=Path(ssh_key_path),
                            use_mux=False,
                        )
                        retry = subprocess.run(retry_cmd)
                        if retry.returncode == 0:
                            self.connection_manager.mark_success(cache_key)
                            return
                    except Exception:  # noqa: BLE001
                        pass
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH authentication failed (Permission denied).\n"
                        "Verify your key matches the task's SSH key, or set MITHRIL_SSH_KEY to override.",
                        request_id,
                    )

                # Non-transient failure. If it's an auth failure, clear key cache,
                # re-resolve the key once, and retry. Otherwise surface a clear error.
                if "permission denied" in stderr_lower or "publickey" in stderr_lower:
                    try:
                        # Bust task-id -> key-path cache to avoid stale keys
                        from flow.core.utils.ssh_key_cache import SSHKeyCache as _KC

                        _KC().clear()
                    except Exception:  # noqa: BLE001
                        pass
                    # Re-resolve key and retry once
                    try:
                        new_key_path = self.provider.get_task_ssh_connection_info(task_id)
                        if isinstance(new_key_path, Path) and str(new_key_path) != str(
                            ssh_key_path
                        ):
                            ssh_key_path = str(new_key_path)
                            # rebuild command with the new key
                            ssh_cmd = SshStack.build_ssh_command(
                                user=getattr(task, "ssh_user", "ubuntu"),
                                host=task.ssh_host,
                                port=getattr(task, "ssh_port", 22),
                                key_path=new_key_path,
                            )
                            retry2 = subprocess.run(ssh_cmd)
                            if retry2.returncode == 0:
                                self.connection_manager.mark_success(cache_key)
                                return
                    except Exception:  # noqa: BLE001
                        pass

                    suggestions = [
                        "Verify the task was launched with your SSH key",
                        "Run: flow ssh-key list (ensure your key is on the project)",
                        "Override temporarily: MITHRIL_SSH_KEY=/path/to/private/key flow ssh <task>",
                    ]
                    raise make_error(
                        (
                            "SSH authentication failed (Permission denied).\n"
                            f"Key used: {Path(ssh_key_path).expanduser()!s}"
                        ),
                        request_id,
                        suggestions=suggestions,
                    )

                # Non-auth failure (e.g., other). Raise a generic error.
                # Handle authentication failures explicitly (re-resolve and retry once without mux)
                if ("permission denied" in stderr_lower) or ("publickey" in stderr_lower):
                    try:
                        from flow.core.utils.ssh_key_cache import SSHKeyCache as _KC

                        _KC().clear()
                    except Exception:  # noqa: BLE001
                        pass
                    try:
                        new_key_path = self.provider.get_task_ssh_connection_info(task_id)
                        if isinstance(new_key_path, Path):
                            ssh_key_path = str(new_key_path)
                        retry_cmd = SshStack.build_ssh_command(
                            user=getattr(task, "ssh_user", "ubuntu"),
                            host=task.ssh_host,
                            port=getattr(task, "ssh_port", 22),
                            key_path=Path(ssh_key_path),
                            use_mux=False,
                        )
                        retry = subprocess.run(retry_cmd)
                        if retry.returncode == 0:
                            self.connection_manager.mark_success(cache_key)
                            return
                    except Exception:  # noqa: BLE001
                        pass
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH authentication failed (Permission denied).\n"
                        "Verify your key matches the task's SSH key, or set MITHRIL_SSH_KEY to override.",
                        request_id,
                    )

                self.connection_manager.bust_cache(cache_key)
                raise make_error(
                    f"SSH connection failed (exit {result.returncode}).",
                    request_id,
                )

            # Non-interactive command: capture output
            if command:
                logger.debug("Executing SSH command: %s", " ".join(ssh_cmd))
                result = subprocess.run(ssh_cmd, capture_output=True, text=True)
                logger.debug(
                    "SSH command result: returncode=%s, stdout_len=%s, stderr_len=%s",
                    result.returncode,
                    len(result.stdout or ""),
                    len(result.stderr or ""),
                )
                logger.debug("SSH command stdout: %r", result.stdout)
                logger.debug("SSH command stderr: %r", result.stderr)

                if result.returncode == 0:
                    # Always print stdout, even if empty (e.g., empty directory listing)
                    print(result.stdout, end="")
                    self.connection_manager.mark_success(cache_key)
                    return

            # Pure interactive shell (no command specified)
            else:
                # Stop animation if still active before taking over terminal
                if (
                    progress_context
                    and hasattr(progress_context, "_active")
                    and progress_context._active
                ):  # type: ignore[attr-defined]
                    progress_context.__exit__(None, None, None)

                result = subprocess.run(ssh_cmd)
                if result.returncode == 0:
                    self.connection_manager.mark_success(cache_key)
                    return

                # If the interactive remote command failed immediately, treat like connection failure
                try:
                    probe_cmd = SshStack.build_ssh_command(
                        user=getattr(task, "ssh_user", "ubuntu"),
                        host=task.ssh_host,
                        port=getattr(task, "ssh_port", 22),
                        key_path=Path(ssh_key_path),
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
                    probe = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=6)
                    stderr_lower = (probe.stderr or "").lower()
                except Exception:  # noqa: BLE001
                    stderr_lower = ""

                transient_markers = (
                    "connection reset by peer",
                    "kex_exchange_identification",
                    "connection closed",
                )
                if any(m in stderr_lower for m in transient_markers) or result.returncode == 255:
                    for backoff in (1.5, 3.0):
                        time.sleep(backoff)
                        retry = subprocess.run(ssh_cmd)
                        if retry.returncode == 0:
                            self.connection_manager.mark_success(cache_key)
                            return
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH connection was reset while the instance was initializing.\n"
                        "Please wait 1–2 minutes and try again.",
                        request_id,
                    )

                self.connection_manager.bust_cache(cache_key)
                raise make_error(
                    f"SSH connection failed (exit {result.returncode}).",
                    request_id,
                )

            # Error handling for failed commands
            # First, show any output from the failed command
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)

            stderr = (result.stderr or "").lower()
            if result.returncode != 0:
                if "connection timed out" in stderr or "operation timed out" in stderr:
                    elapsed = getattr(task, "instance_age_seconds", 0) or 0
                    if elapsed < EXPECTED_PROVISION_MINUTES * 60:
                        raise make_error(
                            f"SSH connection timed out. Instance may still be provisioning "
                            f"(elapsed: {elapsed / 60:.1f} minutes). Mithril instances can take up to "
                            f"{EXPECTED_PROVISION_MINUTES} minutes to become fully available. Please try again later.",
                            request_id,
                        )
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH connection timed out. Possible causes:\n"
                        f"  - Instance is still provisioning (can take up to {EXPECTED_PROVISION_MINUTES} minutes)\n"
                        "  - Network connectivity issues\n"
                        "  - Security group/firewall blocking SSH (port 22)",
                        request_id,
                    )
                elif "connection refused" in stderr:
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH connection refused. The instance is reachable but SSH service "
                        "is not ready yet. Please wait a few more minutes and try again.",
                        request_id,
                    )
                elif (
                    "connection reset by peer" in stderr or "kex_exchange_identification" in stderr
                ):
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH connection was reset. The SSH service is still initializing.\n"
                        "This typically happens during the first few minutes after instance creation.\n"
                        "Please wait 1-2 minutes and try again.",
                        request_id,
                    )
                elif "permission denied" in stderr:
                    error_msg = "SSH authentication failed despite key resolution.\n\n"
                    error_msg += (
                        "This is unexpected - the SSH key was found but authentication failed.\n"
                    )
                    error_msg += "Possible causes:\n"
                    error_msg += (
                        "  1. The private key file permissions are too open (should be 600)\n"
                    )
                    error_msg += "  2. The key file is corrupted or invalid\n"
                    error_msg += (
                        "  3. The instance was created with a different key than expected\n\n"
                    )
                    error_msg += "Debug information:\n"
                    error_msg += f"  - SSH command: {' '.join(ssh_cmd[:6])}...\n"
                    error_msg += f"  - Task ID: {task_id}\n"
                    if "-i" in ssh_cmd:
                        key_idx = ssh_cmd.index("-i") + 1
                        if key_idx < len(ssh_cmd):
                            error_msg += f"  - Using SSH key: {ssh_cmd[key_idx]}\n"
                    raise make_error(error_msg, request_id)
                else:
                    raise make_error(f"SSH connection failed: {result.stderr}", request_id)
        except RemoteExecutionError:
            logger.exception("MithrilRemoteOperations.open_shell: RemoteExecutionError occurred")
            raise
        except Exception as e:
            logger.exception("MithrilRemoteOperations.open_shell: Exception occurred")
            raise make_error(f"SSH shell failed: {e!s}", request_id)
