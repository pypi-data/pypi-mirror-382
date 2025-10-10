"""Handles code synchronization (rsync) for the dev command."""

import logging
import os
import posixpath as _pp
from pathlib import Path

from flow.cli.commands.base import console
from flow.cli.commands.dev.utils import sanitize_env_name
from flow.cli.utils.step_progress import StepTimeline, UploadProgressReporter
from flow.sdk.client import Flow
from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class DevUploadManager:
    """Handles synchronization of local code to the dev VM."""

    def __init__(
        self,
        flow_client: Flow,
        vm_task: Task,
        timeline: StepTimeline,
        *,
        upload_mode: str = "nested",
        upload_path: str | None = None,
    ):
        self.flow_client = flow_client
        self.vm_task = vm_task
        self.timeline = timeline
        self.provider = flow_client.provider
        self.upload_mode = upload_mode
        self.upload_path = upload_path

    def upload(self, upload_path: str, env_name: str) -> tuple[str, str | None]:
        """Validates the path and uploads code.

        Returns:
            (vm_target_dir, container_workdir_or_none)
        """
        upload_path_resolved = Path(upload_path).resolve()
        if not upload_path_resolved.exists():
            console.print(f"[error]Error: Upload path does not exist: {upload_path}[/error]")
            raise SystemExit(1)

        if not upload_path_resolved.is_dir():
            console.print(f"[error]Error: Upload path must be a directory: {upload_path}[/error]")
            raise SystemExit(1)

        try:
            if env_name == "default":
                vm_dir = self._upload_to_default(upload_path_resolved)
                return (vm_dir, None)
            else:
                return self._upload_to_env(upload_path_resolved, env_name)
        except Exception as e:  # noqa: BLE001
            self._handle_upload_error(e)
            return ("~", None)

    def _compute_remote_dirs(self, local_root: Path) -> tuple[str, str]:
        """Return (remote_parent_dir, remote_upload_dir) based on unified planner.

        - nested: remote_upload_dir := <parent>/<dir_name>
        - flat:   remote_upload_dir := <parent>

        Default parent is '~' for dev default environment.
        """
        try:
            from flow.core.code_upload.targets import plan_for_dev as _plan_for_dev

            plan = _plan_for_dev(
                source_dir=local_root,
                env_name="default",
                upload_mode=self.upload_mode,
                parent_override=self.upload_path or "~",
            )
            return plan.remote_parent, plan.remote_target
        except Exception:  # noqa: BLE001
            # Fallback to legacy behavior if planner unavailable
            source_dir_name = os.path.basename(os.path.abspath(str(local_root))) or "dir"
            remote_parent_dir = self.upload_path or "~"
            if self.upload_mode == "nested":
                remote_upload_dir = _pp.join(remote_parent_dir, source_dir_name)
            else:
                remote_upload_dir = remote_parent_dir
            return remote_parent_dir, remote_upload_dir

    def _upload_to_default(self, source_dir: Path) -> str:
        step_idx_upload = self.timeline.add_step("Establishing SSH connection", show_bar=False)
        self.timeline.start_step(step_idx_upload)
        try:
            from rich.text import Text

            self.timeline.set_active_hint_text(
                Text("Waiting for instance to be ready for code upload...")
            )
        except Exception:  # noqa: BLE001
            pass

        # Determine remote target based on upload mode
        remote_parent_dir, remote_upload_dir = self._compute_remote_dirs(source_dir)

        # Best-effort: ensure parent dir exists remotely to keep rsync happy in nested mode
        try:
            remote_ops = self.flow_client.get_remote_operations()
            parent_to_create = (
                remote_parent_dir if self.upload_mode == "flat" else _pp.dirname(remote_upload_dir)
            )
            if not parent_to_create:
                parent_to_create = "~"
            remote_ops.execute_command(
                self.vm_task.task_id, f"mkdir -p {parent_to_create} && mkdir -p {remote_upload_dir}"
            )
        except Exception:  # noqa: BLE001
            # Continue; rsync will generally create directories as needed
            pass

        def _flip_to_upload():
            try:
                self.timeline.complete_step()
                new_idx = self.timeline.add_step(
                    "Uploading code",
                    show_bar=True,
                )
                self.timeline.start_step(new_idx)
                nonlocal upload_reporter
                upload_reporter = UploadProgressReporter(self.timeline, new_idx)
            except Exception:  # noqa: BLE001
                pass

        upload_reporter = UploadProgressReporter(
            self.timeline, step_idx_upload, on_start=_flip_to_upload
        )
        # Use transport-layer manager to support progress and provider-agnostic upload
        from flow.sdk.transfer import CodeTransferConfig as _Cfg
        from flow.sdk.transfer import CodeTransferManager as _Mgr

        # Target is computed based on mode; use '~' expansion semantics
        target_dir = remote_upload_dir
        cfg = _Cfg(
            source_dir=source_dir,
            target_dir=target_dir,
            ssh_timeout=1200,
            transfer_timeout=600,
        )
        result = _Mgr(
            provider=self.provider, progress_reporter=upload_reporter
        ).transfer_code_to_task(self.vm_task, cfg)
        try:
            if (
                getattr(result, "files_transferred", 0) == 0
                and getattr(result, "bytes_transferred", 0) == 0
            ):
                try:
                    self.timeline.complete_step(note="No changes")
                except Exception:  # noqa: BLE001
                    pass
            else:
                # Provide a concise hint for where the code lives on the VM
                try:
                    actual_dir = getattr(result, "final_target", target_dir) or target_dir
                    upload_reporter.set_completion_note(f"→ {actual_dir}")
                except Exception:  # noqa: BLE001
                    pass
        except Exception:  # noqa: BLE001
            pass
        # Reflect actual target in case of fallback
        try:
            actual_dir = getattr(result, "final_target", target_dir) or target_dir
        except Exception:  # noqa: BLE001
            actual_dir = target_dir
        # One-time UX notice: after first nested upload
        try:
            self._maybe_show_nested_notice_once(actual_dir)
        except Exception:  # noqa: BLE001
            pass
        return actual_dir

    def _maybe_show_nested_notice_once(self, actual_dir: str) -> None:
        if self.upload_mode != "nested":
            return
        try:
            home = Path.home()
            notices_dir = home / ".flow"
            notices_dir.mkdir(parents=True, exist_ok=True)
            marker = notices_dir / ".notice_dev_nested_upload"
            if marker.exists():
                return
            # Best-effort write then show message
            try:
                marker.write_text("1")
            except Exception:  # noqa: BLE001
                pass
            try:
                console.print(
                    f"[dim]Uploaded to {actual_dir}; use --flat to expand into parent.[/dim]"
                )
            except Exception:  # noqa: BLE001
                pass
        except Exception:  # noqa: BLE001
            pass

    def _upload_to_env(self, source_dir: Path, env_name: str) -> tuple[str, str | None]:
        from flow.cli.utils.step_progress import build_sync_check_hint

        # Create environment directory
        remote_ops = self.flow_client.get_remote_operations()
        env = sanitize_env_name(env_name)
        # Use unified planner for consistent target derivation
        try:
            from flow.core.code_upload.targets import plan_for_dev as _plan_for_dev

            plan = _plan_for_dev(
                source_dir=source_dir,
                env_name=env,
                upload_mode=self.upload_mode,
            )
            env_target_dir = plan.remote_parent
            project_env_dir = plan.remote_target
        except Exception:  # noqa: BLE001
            env_target_dir = _pp.join("/envs", env)
            project_name = source_dir.name
            project_env_dir = _pp.join(env_target_dir, project_name)

        setup_cmd = f"mkdir -p {env_target_dir}"
        remote_ops.execute_command(self.vm_task.task_id, setup_cmd)

        # Upload directly into the environment under a project-named subdirectory
        step_idx_upload = self.timeline.add_step("Checking for changes", show_bar=False)
        self.timeline.start_step(step_idx_upload)
        try:
            self.timeline.set_active_hint_text(build_sync_check_hint())
        except Exception:  # noqa: BLE001
            pass

        def _flip_to_upload2():
            try:
                self.timeline.complete_step()
                new_idx = self.timeline.add_step(
                    "Uploading code",
                    show_bar=True,
                )
                self.timeline.start_step(new_idx)
                nonlocal upload_reporter
                upload_reporter = UploadProgressReporter(self.timeline, new_idx)
            except Exception:  # noqa: BLE001
                pass

        upload_reporter = UploadProgressReporter(
            self.timeline, step_idx_upload, on_start=_flip_to_upload2
        )
        from flow.sdk.transfer import CodeTransferConfig as _Cfg
        from flow.sdk.transfer import CodeTransferManager as _Mgr

        cfg = _Cfg(
            source_dir=source_dir,
            target_dir=project_env_dir,
            ssh_timeout=1500,
            transfer_timeout=1200,
        )
        result = _Mgr(
            provider=self.provider, progress_reporter=upload_reporter
        ).transfer_code_to_task(self.vm_task, cfg)
        try:
            if (
                getattr(result, "files_transferred", 0) == 0
                and getattr(result, "bytes_transferred", 0) == 0
            ):
                try:
                    self.timeline.complete_step(note="No changes")
                except Exception:  # noqa: BLE001
                    pass
            else:
                # Add concise destination hint; in containers it appears under /workspace
                try:
                    actual_dir = getattr(result, "final_target", project_env_dir) or project_env_dir
                    # Normalize for display to avoid double slashes
                    actual_dir = _pp.normpath(actual_dir)
                    if actual_dir == project_env_dir:
                        upload_reporter.set_completion_note(
                            f"→ {project_env_dir} (container: /workspace/{project_name})"
                        )
                    else:
                        upload_reporter.set_completion_note(f"→ {actual_dir}")
                except Exception:  # noqa: BLE001
                    pass
        except Exception:  # noqa: BLE001
            pass
        # Reflect actual target for caller; provide container path only when under env dir
        try:
            actual_vm_dir = getattr(result, "final_target", project_env_dir) or project_env_dir
        except Exception:  # noqa: BLE001
            actual_vm_dir = project_env_dir
        # Normalize for reliable prefix checks
        actual_vm_dir = _pp.normpath(actual_vm_dir)
        env_target_dir_norm = _pp.normpath(env_target_dir)
        container_dir = (
            (
                plan.container_workdir
                if "plan" in locals() and plan.container_workdir
                else f"/workspace/{source_dir.name}"
            )
            if actual_vm_dir.startswith(env_target_dir_norm)
            else None
        )
        return (actual_vm_dir, container_dir)

    def _handle_upload_error(self, e: Exception) -> None:
        msg = str(e)
        console.print(f"[error]Error uploading code: {msg}[/error]")
        low = msg.lower()

        # Heuristic guidance based on common rsync/SSH errors
        if "permission denied" in low or "publickey" in low:
            console.print("\n[warning]SSH authentication failed[/warning]")
            console.print(
                "  • Ensure your SSH key is registered: [accent]flow ssh-key list[/accent]"
            )
            console.print(
                "  • Upload a key if missing: [accent]flow ssh-key upload ~/.ssh/id_ed25519.pub[/accent]"
            )
            console.print("  • Or set MITHRIL_SSH_KEYS env to your private key path")
            return

        # Only treat as rsync missing when the error explicitly states it
        if (
            "rsync: command not found" in low
            or "rsync not found" in low
            or ("command not found" in low and "rsync" in low)
        ):
            console.print("\n[warning]rsync missing[/warning]")
            console.print(
                "  • Local: macOS [accent]brew install rsync[/accent]; Ubuntu [accent]sudo apt-get install rsync[/accent]"
            )
            console.print(
                "  • Remote VM: attach with [accent]flow dev[/accent] and run [accent]sudo apt-get update && sudo apt-get install -y rsync[/accent]"
            )
            return

        if (
            "connection closed by" in low
            or "banner exchange" in low
            or "timed out" in low
            or "connection refused" in low
        ):
            console.print("\n[warning]SSH connection unstable[/warning]")
            console.print(
                "  • Instance may still be initializing. Wait 60–90s and retry: [accent]flow dev[/accent]"
            )
            console.print(
                "  • If it persists, cancel and recreate the dev VM: [accent]flow cancel :dev && flow dev --force-new[/accent]"
            )
            return

        if "no space left on device" in low:
            console.print("\n[warning]Remote disk is full[/warning]")
            console.print(
                "  • Clean up large files on the VM or reduce what you upload via [.flowignore]"
            )
            console.print(
                "  • Check disk usage: [accent]flow dev[/accent] then [accent]df -h[/accent]"
            )
            return

        if (
            "connection timed out" in low
            or "connection refused" in low
            or "network is unreachable" in low
        ):
            console.print("\n[warning]Network issue during upload[/warning]")
            console.print("  • Verify the VM is reachable: [accent]flow dev[/accent]")
            console.print("  • Retry shortly; transient network hiccups can occur")
            return

        if "file name too long" in low or "argument list too long" in low:
            console.print("\n[warning]Too many files or paths too long[/warning]")
            console.print("  • Add more patterns to [.flowignore] to limit uploads")
            console.print("  • Consider excluding build artifacts, venvs, node_modules")
            return

        # Generic guidance
        console.print(
            "\n[dim]Tips:[/dim] Use [.flowignore] to exclude large directories; run [accent]flow upload-code[/accent] for manual sync."
        )
