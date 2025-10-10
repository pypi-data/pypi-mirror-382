"""Upload code command for transferring local code to running tasks.

This command provides manual code upload functionality using SCP/rsync,
useful for updating code on long-running instances without restarting.
"""

from pathlib import Path

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.json_output import error_json, print_json
from flow.cli.utils.ssh_connection import maybe_wait_handshake, resolve_endpoint
from flow.cli.utils.step_progress import StepTimeline, UploadProgressReporter
from flow.cli.utils.task_selector_mixin import TaskOperationCommand
from flow.cli.utils.timeline_context import timeline_context
from flow.errors import FlowError


class UploadCodeCommand(BaseCommand, TaskOperationCommand):
    """Upload code to a running task.

    Transfers local code to a running GPU instance using efficient
    rsync-based transfer with progress reporting.
    """

    @property
    def name(self) -> str:
        return "upload-code"

    @property
    def help(self) -> str:
        return "Upload local code to running tasks - incremental sync via rsync"

    @property
    def manages_own_progress(self) -> bool:
        """Upload-code manages its own progress display for smooth transitions."""
        return True

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Show running tasks (SSH may still be provisioning)."""
        from flow.cli.utils.task_selector_mixin import TaskFilter

        return TaskFilter.running_only

    def get_selection_title(self) -> str:
        from flow.cli.ui.presentation.nomenclature import get_entity_labels

        labels = get_entity_labels()
        return f"Select {labels.article} {labels.singular} to upload code to"

    def get_no_tasks_message(self) -> str:
        from flow.cli.ui.presentation.nomenclature import get_entity_labels

        labels = get_entity_labels()
        return f"No running {labels.empty_plural} found. Start {labels.article} {labels.singular} first with 'flow submit'"

    def execute_on_task(self, task, client, **kwargs) -> None:
        """Execute code upload on the selected task."""
        source_dir = kwargs.get("source")
        timeout = kwargs.get("timeout", 600)
        dest = kwargs.get("dest")
        json_mode = bool(kwargs.get("output_json", False))
        git_incremental = bool(kwargs.get("incremental", False))
        node = kwargs.get("node", 0)
        all_nodes = bool(kwargs.get("all_nodes", False))

        # Validate node parameter for multi-instance tasks
        from flow.cli.utils.task_utils import validate_node_index

        # Only validate specific node if not uploading to all nodes
        if not all_nodes:
            validate_node_index(task, node)

        # Validate source directory
        if source_dir:
            source_path = Path(source_dir).resolve()
            if not source_path.exists():
                raise FlowError(f"Source directory does not exist: {source_path}")
            if not source_path.is_dir():
                raise FlowError(f"Source must be a directory: {source_path}")
        else:
            source_path = Path.cwd()

        # If no explicit source and task has a code_root, use it for default upload
        try:
            if kwargs.get("source") is None and getattr(
                getattr(task, "config", None), "code_root", None
            ):
                source_path = Path(task.config.code_root).resolve()
                console.print(f"[dim]Using task code_root: {source_path}[/dim]")
        except Exception:  # noqa: BLE001
            pass

        # Resolve destination directory (dynamic):
        #  - Prefer nested under working_dir (e.g., /workspace/<project>) when writable
        #  - Fall back to ~/<project>
        #  - Allow explicit --dest to override both
        if dest:
            target_dir = dest
        else:
            # Determine working_dir from task config
            try:
                working_dir = (
                    getattr(getattr(task, "config", None), "working_dir", "/workspace")
                    or "/workspace"
                )
            except Exception:  # noqa: BLE001
                working_dir = "/workspace"

            # 1) If a sync marker already exists in working_dir, update there (flat)
            try:
                import shlex as _shlex

                remote_ops = client.get_remote_operations()
                wdq = _shlex.quote(working_dir)
                check = f"test -f {wdq}/.flow-sync.json && echo MARK || echo NOMARK"
                out = remote_ops.execute_command(task.task_id, f'bash -lc "{check}"')
                if isinstance(out, str) and "MARK" in out:
                    target_dir = working_dir
                else:
                    raise RuntimeError("no marker")
            except Exception:  # noqa: BLE001
                # 2) Otherwise, choose default by mode: if working_dir is default /workspace, nest under it
                try:
                    from flow.core.code_upload.targets import (
                        plan_for_upload_code as _plan_for_upload_code,
                    )

                    # Nest only when working_dir is the default
                    nested = working_dir.rstrip("/") == "/workspace"
                    plan = _plan_for_upload_code(
                        source_dir=source_path, working_dir=working_dir, nested=nested
                    )
                    candidate = plan.remote_target
                except Exception:  # noqa: BLE001
                    candidate = (
                        f"{working_dir.rstrip('/')}/{source_path.name}"
                        if working_dir.rstrip("/") == "/workspace"
                        else working_dir
                    )

                # Writable check via provider remote operations; fallback to ~/{project}
                try:
                    cand = _shlex.quote(candidate)
                    probe = (
                        f"mkdir -p {cand} >/dev/null 2>&1 || true; "
                        f"test -w {cand} && echo OK || echo DENY"
                    )
                    out = remote_ops.execute_command(task.task_id, f'bash -lc "{probe}"')
                    if isinstance(out, str) and "OK" in out:
                        target_dir = candidate
                    else:
                        raise RuntimeError("not writable")
                except Exception:  # noqa: BLE001
                    from flow.application.config.runtime import settings as _settings

                    try:
                        project_name = (
                            source_path.name if source_path and source_path.name else "project"
                        )
                    except Exception:  # noqa: BLE001
                        project_name = "project"
                    default_dest_tpl = (_settings.upload or {}).get("default_dest", "~/{project}")
                    try:
                        target_dir = str(default_dest_tpl).replace("{project}", project_name)
                    except Exception:  # noqa: BLE001
                        target_dir = f"~/{project_name}"

        task_ref = getattr(task, "name", None) or getattr(task, "task_id", "")

        # Annotate task reference with node index for multinode tasks
        def format_task_ref_with_node(task_ref: str, node: int) -> str:
            """Format task reference with node info when relevant."""
            is_multi_instance = hasattr(task, "num_instances") and (task.num_instances or 1) > 1
            if is_multi_instance:
                return f"{task_ref}:node-{node}"
            else:
                return task_ref

        # Compute target nodes
        total_nodes = int(getattr(task, "num_instances", 1) or 1)
        if all_nodes and total_nodes > 1:
            node_indices = list(range(total_nodes))
            if not json_mode and node not in (None, 0):
                console.print("[dim]Ignoring --node when --all-nodes is set[/dim]")
        else:
            node_indices = [int(node or 0)]

        if not json_mode:
            if len(node_indices) == 1:
                task_ref_with_node = format_task_ref_with_node(task_ref, node_indices[0])
                console.print(f"[dim]Preparing upload to {task_ref_with_node}[/dim]\n")
            else:
                console.print(
                    f"[dim]Preparing upload to {task_ref} (all {total_nodes} nodes)[/dim]\n"
                )

        # Unified transfer timeline with Ctrl+C hint
        timeline = StepTimeline(console, title="flow upload-code", title_animation="auto")
        timeline.start()
        timeline.reserve_total(len(node_indices))

        # Check SSH connection before uploading (like SSHCommand does)
        try:
            # Refresh task to get latest state
            task = client.get_task(task.task_id)

            # For multi-node uploads, only check SSH handshake for one node
            with timeline_context(timeline):
                task = resolve_endpoint(client, task)
                maybe_wait_handshake(client, task, timeline)
        except Exception as e:
            timeline.fail_step(str(e))
            if json_mode:
                print_json(error_json(str(e)))
            else:
                raise

        # Provide a gentle moving bar by default (mirrors flow dev)
        results_agg = []
        for n in node_indices:
            step_label = "Uploading code" if len(node_indices) == 1 else f"Uploading to node {n}"
            upload_idx = timeline.add_step(step_label, show_bar=True)
            timeline.start_step(upload_idx)
            result = None
            try:
                # Use provider's upload with timeline-based reporter and no provider console prints
                reporter = UploadProgressReporter(timeline, upload_idx)
                # Hint about safe interruption
                try:
                    from rich.text import Text

                    from flow.cli.utils.theme_manager import theme_manager

                    accent = theme_manager.get_color("accent")
                    hint = Text()
                    hint.append("  Press ")
                    hint.append("Ctrl+C", style=accent)
                    hint.append(" to cancel upload. Instance remains running; re-run ")
                    hint.append("flow upload-code", style=accent)
                    hint.append(" later.")
                    timeline.set_active_hint_text(hint)
                except Exception:  # noqa: BLE001
                    pass

                result = client.upload_code_to_task(
                    task_id=task.task_id,
                    source_dir=source_path,
                    timeout=timeout,
                    console=None,
                    progress_reporter=reporter,
                    target_dir=target_dir,
                    git_incremental=git_incremental,
                    prepare_absolute=kwargs.get("prepare_absolute", False) or None,
                    node=n,
                )
                try:
                    actual_dir = getattr(result, "final_target", None) or target_dir
                    if not json_mode:
                        task_ref_with_node = format_task_ref_with_node(task_ref, n)
                        console.print(f"[dim]→ {task_ref_with_node}:{actual_dir}[/dim]")
                except Exception:  # noqa: BLE001
                    pass
                timeline.complete_step()
            except KeyboardInterrupt:
                timeline.fail_step("Upload interrupted by user")
                if json_mode:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json("Upload interrupted by user"))
                else:
                    console.print(
                        "\n[dim]Upload interrupted by user. Instance remains running. Re-run: flow upload-code[/dim]"
                    )
                break
            except Exception as e:
                timeline.fail_step(str(e))
                # Check for dependency errors - providers should raise DependencyNotFoundError
                # but we handle string matching for backward compatibility
                if "rsync not found" in str(e):
                    if json_mode:
                        from flow.cli.utils.json_output import error_json, print_json

                        print_json(
                            error_json(
                                "rsync is required for code upload",
                                hint="Install rsync (brew/apt/yum)",
                            )
                        )
                    else:
                        console.print("[error]Error:[/error] rsync is required for code upload\n")
                        console.print("Install rsync:")
                        console.print("  • macOS: [accent]brew install rsync[/accent]")
                        console.print(
                            "  • Ubuntu/Debian: [accent]sudo apt-get install rsync[/accent]"
                        )
                        console.print("  • RHEL/CentOS: [accent]sudo yum install rsync[/accent]")
                else:
                    if json_mode:
                        from flow.cli.utils.json_output import error_json, print_json

                        print_json(error_json(str(e)))
                    else:
                        raise
                break

            # Per-node summary
            if result is not None:
                try:
                    bt = getattr(result, "bytes_transferred", 0) or 0
                    ft = getattr(result, "files_transferred", 0) or 0
                    rate = getattr(result, "transfer_rate", None)
                    final_target = getattr(result, "final_target", None) or target_dir

                    if json_mode:
                        results_agg.append(
                            {
                                "node": n,
                                "dest": final_target,
                                "files_transferred": ft,
                                "bytes_transferred": bt,
                                "transfer_rate": rate,
                            }
                        )
                    else:
                        if ft == 0 and bt == 0:
                            task_ref_with_node = format_task_ref_with_node(task_ref, n)
                            console.print(
                                f"[dim]No changes to sync → {task_ref_with_node}:{final_target}[/dim]"
                            )
                        else:
                            size_mb = bt / (1024 * 1024)
                            task_ref_with_node = format_task_ref_with_node(task_ref, n)
                            msg = (
                                f"[success]✓[/success] Upload complete: {ft} files, {size_mb:.1f} MB"
                                f" → {task_ref_with_node}:{final_target}"
                            )
                            if isinstance(rate, str) and rate:
                                msg += f" @ {rate}"
                            console.print(msg)
                except Exception:  # noqa: BLE001
                    pass

        timeline.finish()

        # Aggregate JSON output when applicable
        if json_mode and results_agg:
            from flow.cli.utils.json_output import print_json

            if len(results_agg) == 1:
                # Single node - maintain backward compatibility
                result_data = results_agg[0]
                print_json(
                    {
                        "status": "ok",
                        "task_id": getattr(task, "task_id", None),
                        "task_name": getattr(task, "name", None),
                        "node": result_data["node"],
                        "source": str(source_path),
                        "dest": result_data["dest"],
                        "files_transferred": result_data["files_transferred"],
                        "bytes_transferred": result_data["bytes_transferred"],
                        "transfer_rate": result_data["transfer_rate"],
                    }
                )
            else:
                # Multiple nodes - new format
                print_json(
                    {
                        "status": "ok",
                        "task_id": getattr(task, "task_id", None),
                        "task_name": getattr(task, "name", None),
                        "nodes": results_agg,
                        "source": str(source_path),
                    }
                )
        elif not json_mode and results_agg:
            # Next steps
            is_multi_instance = hasattr(task, "num_instances") and (task.num_instances or 1) > 1
            base_task_ref = task.name or task.task_id

            if is_multi_instance:
                ssh_cmd = f"flow ssh {base_task_ref} --node 0"
                logs_cmd = f"flow logs {base_task_ref} --node 0 -f"
            else:
                ssh_cmd = f"flow ssh {base_task_ref}"
                logs_cmd = f"flow logs {base_task_ref} -f"

            self.show_next_actions(
                [
                    f"SSH into instance: [accent]{ssh_cmd}[/accent]",
                    f"View logs: [accent]{logs_cmd}[/accent]",
                    "Run your updated code in the SSH session",
                ]
            )

    def get_command(self) -> click.Command:
        # Import completion function
        # from flow.cli.utils.mode import demo_aware_command
        from flow.cli.ui.runtime.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--source",
            "-s",
            type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
            help="Source directory to upload (default: current directory)",
        )
        @click.option(
            "--timeout",
            "-t",
            type=int,
            default=600,
            help="Upload timeout in seconds (default: 600)",
        )
        @click.option(
            "--dest",
            type=str,
            default=None,
            help=(
                "Destination directory on the instance. Default is /workspace/<project> when writable, otherwise ~/{project}."
            ),
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed upload patterns and troubleshooting",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--incremental/--full-scan",
            default=False,
            help=(
                "Use Git to detect changed/untracked files and only upload those (default: full scan). "
                "Requires a Git repository."
            ),
        )
        @click.option(
            "--prepare-absolute",
            is_flag=True,
            default=False,
            help=(
                "Use sudo -n to prepare absolute destinations (mkdir/chown) when unwritable. "
                "Defaults to config/env when omitted."
            ),
        )
        @click.option(
            "--node", type=int, default=0, help="Node index for multi-instance tasks (default: 0)"
        )
        @click.option(
            "--all-nodes",
            "-A",
            is_flag=True,
            default=False,
            help="Upload to all nodes of a multi-instance task",
        )
        # @demo_aware_command()
        def upload_code(
            task_identifier: str | None,
            source: Path | None,
            timeout: int,
            verbose: bool,
            dest: str | None,
            output_json: bool,
            incremental: bool,
            prepare_absolute: bool = False,
            node: int = 0,
            all_nodes: bool = False,
        ):
            """Upload code to a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \\b
            Examples:
                flow upload-code                 # Interactive task selector
                flow upload-code my-training     # Upload to specific task
                flow upload-code -s ../lib       # Upload different directory
                flow upload-code -t 1200         # Longer timeout (20 min)
                flow upload-code --node 1        # Upload to node 1 of multi-instance task
                flow upload-code -A              # Upload to all nodes of multi-instance task

            Default destination is /workspace/<project> when writable; otherwise ~/<project>.
            Use --dest to override.

            Use 'flow upload-code --verbose' for advanced patterns and .flowignore guide.
            """
            if verbose and not output_json:
                from flow.cli.utils.icons import flow_icon as _flow_icon

                console.print(f"\n[bold]{_flow_icon()} Code Upload Guide:[/bold]\n")
                console.print("Basic usage:")
                console.print("  flow upload-code                  # Upload current directory")
                console.print("  flow upload-code my-task          # Upload to specific task")
                console.print("  flow upload-code -s ~/project     # Upload different source")
                console.print(
                    "  flow upload-code --node 1         # Upload to node 1 (multi-instance)"
                )
                console.print(
                    "  flow upload-code -A               # Upload to all nodes (multi-instance)\n"
                )

                console.print("Upload behavior:")
                console.print(
                    "  • Destination: /workspace/<project> when writable; else ~/<project>"
                )
                console.print("    - Override with: --dest <path> (absolute or ~)")
                console.print("  • Method: rsync with compression")
                console.print("  • Incremental: Only changed files uploaded")
                console.print("  • Progress: Real-time transfer status")
                console.print("  • Multi-node: Use --node <index> for specific nodes (0-based)\n")

                console.print(".flowignore patterns:")
                console.print("  # Common patterns to exclude:")
                console.print("  .git/")
                console.print("  __pycache__/")
                console.print("  *.pyc")
                console.print("  .env")
                console.print("  venv/")
                console.print("  node_modules/")
                console.print("  *.log")
                console.print("  .DS_Store\n")

                console.print("Large project optimization:")
                console.print("  # Create minimal .flowignore")
                console.print("  echo 'data/' >> .flowignore       # Exclude large datasets")
                console.print("  echo 'models/' >> .flowignore     # Exclude model weights")
                console.print("  echo '.git/' >> .flowignore       # Exclude git history\n")

                console.print("Common workflows:")
                console.print("  # Hot reload during development")
                console.print("  flow upload-code && flow ssh task -- python train.py")
                console.print("  ")
                console.print("  # Upload and monitor")
                console.print("  flow upload-code && flow logs task -f")
                console.print("  ")
                console.print("  # Sync specific module")
                console.print("  flow upload-code -s ./src/models")
                console.print("  ")
                console.print("  # Multi-node distributed training")
                console.print("  flow upload-code -A               # Upload to all nodes at once")
                console.print("  flow upload-code --node 0 && flow upload-code --node 1\n")

                console.print("Troubleshooting:")
                console.print("  • Timeout errors → Increase with -t 1800 (30 min)")
                console.print("  • rsync not found → Install: brew/apt/yum install rsync")
                console.print("  • Permission denied → Check task is running: flow status")
                console.print("  • Upload too slow → Add more patterns to .flowignore\n")

                console.print("Next steps after upload:")
                console.print("  • Connect: flow ssh [task.name]<task-name>[/task.name]")
                console.print("  • Run code: python your_script.py")
                console.print("  • Monitor: flow logs [task.name]<task-name>[/task.name] -f\n")
                return

            self._execute(
                task_identifier,
                source=source,
                timeout=timeout,
                dest=dest,
                output_json=output_json,
                incremental=incremental,
                prepare_absolute=prepare_absolute,
                node=node,
                all_nodes=all_nodes,
            )

        return upload_code

    def _execute(
        self,
        task_identifier: str | None,
        source: Path | None,
        timeout: int,
        dest: str | None,
        *,
        output_json: bool = False,
        incremental: bool = False,
        prepare_absolute: bool = False,
        node: int = 0,
        all_nodes: bool = False,
    ) -> None:
        """Execute the upload-code command."""
        self.execute_with_selection(
            task_identifier,
            source=source,
            timeout=timeout,
            dest=dest,
            output_json=output_json,
            incremental=incremental,
            prepare_absolute=prepare_absolute,
            node=node,
            all_nodes=all_nodes,
        )


# Export command instance
command = UploadCodeCommand()
