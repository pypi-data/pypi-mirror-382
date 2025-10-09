from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from flow.adapters.transport.rsync import (
    ITransferStrategy,
    RsyncTransferStrategy,
    TransferError,
    TransferResult,
)
from flow.adapters.transport.ssh import (
    ExponentialBackoffSSHWaiter,
    ISSHWaiter,
    SSHConnectionInfo,
)
from flow.core.ignore import build_exclude_patterns
from flow.errors import FlowError
from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class CodeTransferError(FlowError):
    pass


@dataclass
class CodeTransferConfig:
    source_dir: Path | None = None
    target_dir: str = "~"
    ssh_timeout: int = 1200
    transfer_timeout: int = 600
    retry_on_failure: bool = True
    use_compression: bool = True
    # When True, build a file list from Git changes for rsync; when False,
    # perform a full tree scan. None defers to legacy env override
    # (FLOW_GIT_INCREMENTAL) for temporary compatibility.
    git_incremental: bool | None = None
    # Allow using sudo -n to prepare absolute targets (mkdir/chown) if unwritable.
    # None defers to runtime settings/env; False disables; True enables.
    prepare_absolute: bool | None = None

    def __post_init__(self):
        if self.source_dir is None:
            self.source_dir = Path.cwd()


class IProgressReporter:
    @contextmanager
    def ssh_wait_progress(self, message: str):
        yield

    @contextmanager
    def transfer_progress(self, message: str):
        yield

    def update_status(self, message: str) -> None:
        pass


class RichProgressReporter(IProgressReporter):
    """Progress reporter using Rich.

    Kept light to avoid heavy imports during library use; only instantiates
    console and progress when used.
    """

    def __init__(self, console: object = None):
        if console is None:
            from rich.console import Console as _Console  # lazy import

            self.console = _Console()
        else:
            self.console = console
        self._current_progress = None

    def _start_progress(self, message: str):
        from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

        progress = AnimatedEllipsisProgress(
            self.console, f"[dim]{message}[/dim]", transient=True, start_immediately=True
        )
        self._current_progress = progress
        progress.__enter__()
        return progress

    def _stop_progress(self):
        prog = self._current_progress
        self._current_progress = None
        if prog is not None:
            try:
                prog.__exit__(None, None, None)
            except Exception:  # noqa: BLE001
                pass

    @contextmanager
    def ssh_wait_progress(self, message: str):
        progress = self._start_progress(message)
        try:
            yield progress
        finally:
            self._stop_progress()

    @contextmanager
    def transfer_progress(self, message: str):
        progress = self._start_progress(message)
        try:
            yield progress
        finally:
            self._stop_progress()

    def update_status(self, message: str) -> None:
        if self._current_progress and hasattr(self._current_progress, "update_message"):
            self._current_progress.update_message(message)
        else:
            self.console.print(f"[dim]{message}[/dim]")


class CodeTransferManager:
    def __init__(
        self,
        provider: object | None = None,
        ssh_waiter: ISSHWaiter | None = None,
        transfer_strategy: ITransferStrategy | None = None,
        progress_reporter: IProgressReporter | None = None,
    ):
        self.provider = provider
        self.ssh_waiter = ssh_waiter or ExponentialBackoffSSHWaiter(provider)
        self.transfer_strategy = transfer_strategy or RsyncTransferStrategy()
        self.progress_reporter = progress_reporter

    def transfer_code_to_task(
        self,
        task: Task,
        config: CodeTransferConfig | None = None,
        node: int | None = None,
    ) -> TransferResult:
        if not config:
            config = CodeTransferConfig()

        logger.info(
            f"Starting code transfer to task {task.task_id}\n  Source: {config.source_dir}\n  Target: {task.task_id}:{config.target_dir}"
        )

        try:
            # Expose current config for downstream policy decisions
            try:
                self._current_transfer_config = config
            except Exception:  # noqa: BLE001
                pass
            connection = self._wait_for_ssh(task, config, node)
            result = self._transfer_code(connection, config)
            self._verify_transfer(connection, config)
            return result
        except Exception as e:
            raise CodeTransferError(f"Failed to transfer code to task {task.task_id}: {e!s}") from e
        finally:
            try:
                self._current_transfer_config = None
            except Exception:  # noqa: BLE001
                pass

    def _wait_for_ssh(
        self, task: Task, config: CodeTransferConfig, node: int | None = None
    ) -> SSHConnectionInfo:
        # When an ssh_host is present, a very short probe can still catch the VM mid-provision.
        # Avoid the previous overly aggressive 3s quick probe; allow a brief stabilization window instead.
        if task.ssh_host:
            try:
                return self.ssh_waiter.wait_for_ssh(
                    task, timeout=min(30, int(config.ssh_timeout or 1200)), node=node
                )
            except Exception:  # noqa: BLE001
                # Fall through to a full wait with progress
                pass

        def ssh_progress(status: str):
            if self.progress_reporter:
                self.progress_reporter.update_status(status)

        try:
            if self.progress_reporter:
                with self.progress_reporter.ssh_wait_progress("Waiting for SSH access"):
                    return self.ssh_waiter.wait_for_ssh(
                        task, timeout=config.ssh_timeout, progress_callback=ssh_progress, node=node
                    )
            return self.ssh_waiter.wait_for_ssh(
                task, timeout=config.ssh_timeout, progress_callback=ssh_progress, node=node
            )
        except Exception as e:
            raise CodeTransferError(f"Failed to establish SSH connection: {e!s}") from e

    def _stabilize_ssh(self, connection: SSHConnectionInfo, *, seconds: int = 20) -> None:
        """Best-effort: require a couple of consecutive quick successes before heavy operations.

        Uses SshStack.is_ssh_ready() against the same host/key so we reuse any control master.
        Never raises; returns after the window or two consecutive OKs.
        """
        try:
            from flow.adapters.transport.ssh.ssh_stack import SshStack as _S
        except Exception:  # noqa: BLE001
            return
        import time as _t

        deadline = _t.time() + max(5, int(seconds))
        ok = 0
        while _t.time() < deadline and ok < 2:
            try:
                prefix_args = None
                try:
                    if getattr(connection, "proxyjump", None):
                        prefix_args = ["-J", str(connection.proxyjump)]
                except Exception:  # noqa: BLE001
                    prefix_args = None
                if _S.is_ssh_ready(
                    user=connection.user,
                    host=connection.host,
                    port=connection.port,
                    key_path=connection.key_path,
                    prefix_args=prefix_args,
                ):
                    ok += 1
                else:
                    ok = 0
            except Exception:  # noqa: BLE001
                ok = 0
            _t.sleep(2)

    def _transfer_code(
        self, connection: SSHConnectionInfo, config: CodeTransferConfig
    ) -> TransferResult:
        # Decide if incremental mode is both requested and safe
        incremental_requested = getattr(config, "git_incremental", None) is True
        use_incremental = False
        if incremental_requested:
            try:
                use_incremental = self._is_incremental_safe(connection, config)
            except Exception:  # noqa: BLE001
                use_incremental = False

        # Choose an effective target directory. Home-relative destinations are expected to be writable,
        # so we skip early writability checks there and rely on preflight mkdir. For absolute paths,
        # create the directory first, then probe writability to decide on a fallback.
        target_to_use = config.target_dir
        try:
            probe_target = str(target_to_use).strip() if target_to_use is not None else None
        except Exception:  # noqa: BLE001
            probe_target = None

        # Light stabilization before preflight to reduce flap-related false negatives
        try:
            self._stabilize_ssh(connection, seconds=10)
        except Exception:  # noqa: BLE001
            pass

        # Preflight directory creation
        try:
            self._preflight_target_dir(connection, probe_target)
        except Exception:  # noqa: BLE001
            pass

        # Only probe absolute paths for writability; leave ~ and ~/... alone
        try:
            if (
                probe_target
                and probe_target.startswith("/")
                and not self._is_remote_dir_writable(connection, probe_target)
            ):
                fallback = self._compute_home_fallback(config)
                if fallback != probe_target and self.progress_reporter:
                    try:
                        self.progress_reporter.update_status(
                            f"Remote path {probe_target} not writable; using {fallback}"
                        )
                    except Exception:  # noqa: BLE001
                        pass
                target_to_use = fallback
        except Exception:  # noqa: BLE001
            # If probe fails for any reason, keep the original and let rsync attempt
            target_to_use = config.target_dir

        def transfer_progress(progress):
            if self.progress_reporter:
                if hasattr(self.progress_reporter, "update_transfer"):
                    self.progress_reporter.update_transfer(
                        progress.percentage, progress.speed, progress.eta, progress.current_file
                    )
                else:
                    if progress.current_file:
                        file_display = progress.current_file.split("/")[-1]
                        self.progress_reporter.update_status(f"Uploading: {file_display}")
                    elif progress.percentage is not None:
                        status = f"Progress: {progress.percentage:.0f}%"
                        if progress.speed:
                            status += f" @ {progress.speed}"
                        if progress.eta:
                            status += f" (ETA: {progress.eta})"
                        self.progress_reporter.update_status(status)

        # Allow transfer strategies to seed a realistic estimated duration (e.g., from a preflight)
        # by attaching a helper on the callback. This avoids tight coupling and keeps the interface stable.
        try:
            if self.progress_reporter and hasattr(self.progress_reporter, "seed_estimated_seconds"):
                transfer_progress.seed_estimated_seconds = (
                    lambda seconds: self.progress_reporter.seed_estimated_seconds(seconds)
                )
        except Exception:  # noqa: BLE001
            pass

        try:
            if self.progress_reporter:
                with self.progress_reporter.transfer_progress(f"Uploading code to {target_to_use}"):
                    # Helpful status before rsync emits the first progress line
                    try:
                        if incremental_requested and not use_incremental:
                            self.progress_reporter.update_status(
                                "Incremental requested but no matching baseline; using full scan"
                            )
                        else:
                            self.progress_reporter.update_status(
                                "Starting rsync (scanning changes)..."
                            )
                    except Exception:  # noqa: BLE001
                        pass
                    # Optional preflight: create well-known absolute targets to avoid permission fallbacks
                    try:
                        self._preflight_target_dir(connection, target_to_use)
                    except Exception:  # noqa: BLE001
                        pass
                    result = self.transfer_strategy.transfer(
                        source=config.source_dir,  # type: ignore[arg-type]
                        target=target_to_use,
                        connection=connection,
                        progress_callback=transfer_progress,
                        git_incremental=use_incremental,
                    )
                    # Quick remote verification message
                    try:
                        self.progress_reporter.update_status("Verifying upload on remote...")
                    except Exception:  # noqa: BLE001
                        pass
                    # Write remote sync marker for future safe incrementals
                    try:
                        self._write_remote_marker(connection, config, result)
                    except Exception:  # noqa: BLE001
                        pass
                    # Attach a concise summary to the completed step (best-effort)
                    try:
                        if hasattr(self.progress_reporter, "set_completion_note"):
                            rate = getattr(result, "transfer_rate", None)
                            mb = max(0, int(result.bytes_transferred / (1024 * 1024)))
                            note = f"{result.files_transferred} files, {mb} MB"
                            if isinstance(rate, str) and rate:
                                note += f" @ {rate}"
                            self.progress_reporter.set_completion_note(note)
                    except Exception:  # noqa: BLE001
                        pass
                    try:
                        # Track the final target used for downstream verification
                        self._last_final_target = (
                            getattr(result, "final_target", None) or config.target_dir
                        )
                    except Exception:  # noqa: BLE001
                        self._last_final_target = config.target_dir
                    return result
            # Optional preflight: create well-known absolute targets to avoid permission fallbacks
            try:
                self._preflight_target_dir(connection, target_to_use)
            except Exception:  # noqa: BLE001
                pass
            result = self.transfer_strategy.transfer(
                source=config.source_dir,  # type: ignore[arg-type]
                target=target_to_use,
                connection=connection,
                progress_callback=transfer_progress,
                git_incremental=use_incremental,
            )
            try:
                self._write_remote_marker(connection, config, result)
            except Exception:  # noqa: BLE001
                pass
            try:
                self._last_final_target = getattr(result, "final_target", None) or config.target_dir
            except Exception:  # noqa: BLE001
                self._last_final_target = config.target_dir
            return result
        except TransferError as e:
            # Opportunistic fallback when target directory is not writable (e.g., /workspace on host)
            msg = str(e)
            try:
                target = target_to_use or config.target_dir
            except Exception:  # noqa: BLE001
                target = None

            def _should_fallback_to_home(error_text: str, target_dir: str | None) -> bool:
                if not target_dir:
                    return False
                denied_indicators = [
                    "Permission denied",
                    "failed: Permission denied",
                    f'mkdir "{target_dir}" failed',
                    "error in file IO (code 11)",
                ]
                return any(ind in error_text for ind in denied_indicators)

            attempted_fallback = False
            if target and _should_fallback_to_home(msg, target) and target != "~":
                # Compute a safer home fallback under ~/workspace/<project>
                try:
                    src_dir = config.source_dir or Path.cwd()
                    project_name = src_dir.name or "project"
                    fallback_home_target = f"~/workspace/{project_name}"
                except Exception:  # noqa: BLE001
                    fallback_home_target = "~"
                try:
                    if self.progress_reporter:
                        self.progress_reporter.update_status(
                            f"Remote path {target} not writable; retrying with {fallback_home_target}"
                        )
                except Exception:  # noqa: BLE001
                    pass
                # Retry once to the computed home directory
                try:
                    attempted_fallback = True
                    fb_result = self.transfer_strategy.transfer(
                        source=config.source_dir,  # type: ignore[arg-type]
                        target=fallback_home_target,
                        connection=connection,
                        progress_callback=transfer_progress,
                        git_incremental=use_incremental,
                    )
                    # Ensure downstream steps know the real target used
                    try:
                        fb_result.final_target = str(fallback_home_target)
                    except Exception:  # noqa: BLE001
                        pass
                    # Best-effort: write marker to the actual target path
                    try:
                        self._write_remote_marker(connection, config, fb_result)
                    except Exception:  # noqa: BLE001
                        pass
                    try:
                        self._last_final_target = getattr(fb_result, "final_target", None) or str(
                            fallback_home_target
                        )
                    except Exception:  # noqa: BLE001
                        self._last_final_target = str(fallback_home_target)
                    return fb_result
                except TransferError:
                    # Fall through to generic handling
                    pass

            # If we attempted a home fallback and it failed, avoid retrying the unwritable original path.
            # If the error looks network/SSH-related, attempt a short stabilization before the retry.
            net_low = str(msg).lower()
            if (
                any(
                    s in net_low
                    for s in (
                        "connection closed by",
                        "banner exchange",
                        "timed out",
                        "connection refused",
                        "network is unreachable",
                    )
                )
                and config.retry_on_failure
            ):
                try:
                    if self.progress_reporter:
                        self.progress_reporter.update_status("SSH unstable; re-checking connection")
                    self._stabilize_ssh(connection, seconds=30)
                except Exception:  # noqa: BLE001
                    pass

            if config.retry_on_failure:
                try:
                    if attempted_fallback:
                        # One more attempt to the safer home target in case of transient error
                        return self.transfer_strategy.transfer(
                            source=config.source_dir,  # type: ignore[arg-type]
                            target=fallback_home_target,  # type: ignore[name-defined]
                            connection=connection,
                            git_incremental=use_incremental,
                        )
                    # Otherwise, retry original target once
                    return self.transfer_strategy.transfer(
                        source=config.source_dir,  # type: ignore[arg-type]
                        target=config.target_dir,
                        connection=connection,
                        git_incremental=use_incremental,
                    )
                except TransferError as e2:
                    raise CodeTransferError(f"Code transfer failed after retry: {e2}") from e2

            raise CodeTransferError(f"Code transfer failed: {e}") from e

    def _preflight_target_dir(self, connection: SSHConnectionInfo, target_dir: str | None) -> None:
        """Best-effort remote mkdir for common absolute targets to minimize permission issues.

        Ensures the effective target directory exists before rsync. Supports:
        - Absolute paths (may fail silently if not writable)
        - Home-relative paths ("~/...") expanded via $HOME
        - "~" is treated as $HOME and left as-is
        Uses provider.remote_exec when available, otherwise falls back to a
        direct SSH execution using the same connection parameters.
        """
        if not target_dir:
            return
        try:
            td = str(target_dir).strip()
        except Exception:  # noqa: BLE001
            return
        try:
            from flow.adapters.transport.remote_helpers import ensure_dir, ensure_writable

            allow_sudo = self._get_prepare_absolute_policy()
            ensure_dir(connection, td, sudo=allow_sudo)
            # If we used sudo to create absolute path, also try to make it writable for the SSH user
            if allow_sudo and td.startswith("/"):
                ensure_writable(connection, td, user=connection.user, sudo=True)
        except Exception:  # noqa: BLE001
            pass

    def _verify_transfer(self, connection: SSHConnectionInfo, config: CodeTransferConfig) -> None:
        # Optional: provider-specific verification via remote execution, if provider exposes it
        try:
            if getattr(self.provider, "remote_exec", None):
                # Prefer verifying the actual final target when available
                final_target = None
                try:
                    # Some strategies attach final_target to the result; when unavailable, use config
                    final_target = getattr(self, "_last_final_target", None) or config.target_dir
                except Exception:  # noqa: BLE001
                    final_target = config.target_dir
                output = self.provider.remote_exec(
                    connection.task_id, f"ls -la {final_target} | head -5"
                )
                if output and "No such file or directory" in output:
                    raise CodeTransferError(
                        f"Target directory {final_target} not found after transfer"
                    )
        except Exception:  # noqa: BLE001
            # Best-effort
            pass

    # ---------------- incremental handshake helpers ----------------
    def _get_git_head(self, source: Path | None) -> str | None:
        if not source:
            return None
        try:
            check = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=source,
                capture_output=True,
                text=True,
            )
            if check.returncode != 0 or check.stdout.strip().lower() != "true":
                return None
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=source, capture_output=True, text=True
            )
            if head.returncode == 0:
                return head.stdout.strip()
        except Exception:  # noqa: BLE001
            return None
        return None

    def _hash_patterns(self, patterns: list[str]) -> str:
        h = hashlib.sha256()
        for p in sorted(patterns):
            h.update(p.encode("utf-8", "ignore") + b"\n")
        return h.hexdigest()

    def _is_incremental_safe(
        self, connection: SSHConnectionInfo, config: CodeTransferConfig
    ) -> bool:
        source_dir = config.source_dir or Path.cwd()
        commit = self._get_git_head(source_dir)
        if not commit:
            return False
        spec = build_exclude_patterns(source_dir)
        ignore_hash = self._hash_patterns(spec.patterns)

        # Candidate marker locations: requested target and home
        candidates: list[str] = []
        try:
            if config.target_dir:
                candidates.append(f"{config.target_dir}/.flow-sync.json")
        except Exception:  # noqa: BLE001
            pass
        candidates.append("~/.flow-sync.json")

        for remote_path in candidates:
            try:
                if getattr(self.provider, "remote_exec", None):
                    out = self.provider.remote_exec(
                        connection.task_id, f"cat {remote_path} 2>/dev/null || true"
                    )
                    if not out:
                        continue
                    data = json.loads(out)
                    if (
                        isinstance(data, dict)
                        and data.get("commit") == commit
                        and data.get("ignore_hash") == ignore_hash
                    ):
                        return True
            except Exception:  # noqa: BLE001
                continue
        return False

    def _write_remote_marker(
        self, connection: SSHConnectionInfo, config: CodeTransferConfig, result: TransferResult
    ) -> None:
        source_dir = config.source_dir or Path.cwd()
        spec = build_exclude_patterns(source_dir)
        meta = {
            "version": 1,
            "commit": self._get_git_head(source_dir),
            "ignore_hash": self._hash_patterns(spec.patterns),
            "ignore_source": spec.source,
            "target_dir": getattr(result, "final_target", config.target_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        content = json.dumps(meta, separators=(",", ":"))
        remote_dir = getattr(result, "final_target", config.target_dir)
        # Build a robust path expression: convert leading '~' to $HOME for safe quoting
        try:
            if remote_dir == "~":
                target_expr = "$HOME/.flow-sync.json"
            elif isinstance(remote_dir, str) and remote_dir.startswith("~/"):
                target_expr = "$HOME/" + remote_dir[2:] + "/.flow-sync.json"
            else:
                target_expr = (remote_dir or "~").rstrip("/") + "/.flow-sync.json"
        except Exception:  # noqa: BLE001
            target_expr = "$HOME/.flow-sync.json"
        if not getattr(self.provider, "remote_exec", None):
            return
        # Write via here-doc with conservative quoting. Use bash -lc "..." so $HOME expands.
        # Escape any double quotes in the target expression for inclusion inside the double-quoted script
        target_expr_escaped = str(target_expr).replace('"', '\\"')
        # Keep here-doc content single-quoted to avoid interpolation
        escaped = content.replace("'", "'''")
        cmd = f'bash -lc "cat > "{target_expr_escaped}" <<\'EOF\'\n{escaped}\nEOF"'
        try:
            self.provider.remote_exec(connection.task_id, cmd)
        except Exception:  # noqa: BLE001
            pass

    # ---------------- remote helpers ----------------
    def _is_remote_dir_writable(self, connection: SSHConnectionInfo, target_dir: str) -> bool:
        """Best-effort probe to check whether the remote directory is writable.

        Uses provider.remote_exec when available. Returns False on any error.
        Avoids aggressive shell constructs to minimize compatibility issues.
        """
        if not getattr(self.provider, "remote_exec", None):
            try:
                from flow.adapters.transport.remote_helpers import is_writable

                return is_writable(connection, target_dir)
            except Exception:  # noqa: BLE001
                return False
        try:
            td = str(target_dir).strip()
        except Exception:  # noqa: BLE001
            return False
        if not td:
            return False
        # Only probe absolute or home-relative destinations; ignore plain '~'
        if td == "~":
            return True
        try:
            from flow.adapters.transport.remote_helpers import is_writable

            return is_writable(connection, td)
        except Exception:  # noqa: BLE001
            return False

    def _compute_home_fallback(self, config: CodeTransferConfig) -> str:
        try:
            src_dir = config.source_dir or Path.cwd()
            project_name = src_dir.name or "project"
            # Prefer a single-level directory under $HOME so rsync can create
            # the final component without requiring pre-existing parents.
            return f"~/{project_name}"
        except Exception:  # noqa: BLE001
            return "~"

    def _get_prepare_absolute_policy(self) -> bool:
        """Resolve whether to allow sudo for preparing absolute paths.

        Precedence: CodeTransferConfig.prepare_absolute > env FLOW_UPLOAD_ALLOW_SUDO > runtime settings.
        """
        # Config flag if present on current transfer
        try:
            current_cfg = getattr(self, "_current_transfer_config", None)
            if current_cfg and getattr(current_cfg, "prepare_absolute", None) is not None:
                return bool(current_cfg.prepare_absolute)
        except Exception:  # noqa: BLE001
            pass
        # Env override
        try:
            import os as _os

            env_val = _os.environ.get("FLOW_UPLOAD_ALLOW_SUDO")
            if env_val is not None:
                return str(env_val).strip().lower() in {"1", "true", "yes", "on"}
        except Exception:  # noqa: BLE001
            pass
        # Runtime setting
        try:
            from flow.application.config.runtime import settings as _settings

            return bool((_settings.upload or {}).get("allow_sudo_absolute", False))
        except Exception:  # noqa: BLE001
            return False
