"""SSH command for connecting to running GPU instances.

Provides secure shell access to running tasks for debugging and development.
Keep examples in CLI help to avoid drift.
"""

import concurrent.futures
import logging
import os
import shlex
import subprocess
import threading
from contextlib import suppress
from pathlib import Path

import click

import flow.sdk.factory as sdk_factory
from flow.adapters.providers.builtin.mithril.remote.errors import SshAuthenticationError
from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.formatters import TaskFormatter
from flow.cli.ui.presentation.nomenclature import get_entity_labels
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.json_output import print_json
from flow.cli.utils.ssh_connection import (
    PermissionCheckResult,
    check_and_resolve_if_key_permission_error,
    get_ssh_port,
    maybe_wait_handshake,
    resolve_endpoint,
)
from flow.cli.utils.ssh_helpers import build_ssh_argv, ssh_command_string
from flow.cli.utils.task_resolver import (
    resolve_task_identifier as _resolve_identifier,
)
from flow.cli.utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from flow.cli.utils.timeline_context import (
    finish_current_timeline,
)
from flow.domain.ssh import SSHKeyNotFoundError
from flow.errors import FlowError
from flow.plugins import registry as plugin_registry
from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class SSHCommand(BaseCommand, TaskOperationCommand):
    """SSH command implementation.

    Handles both interactive sessions and remote command execution.
    Requires task to be in running state with SSH keys configured.
    """

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()
        # Store current task context for error handling
        self._current_task_id = None
        self._current_node = None
        self._current_command = None

    @property
    def name(self) -> str:
        return "ssh"

    def handle_error(self, error: Exception | str, exit_code: int = 1) -> None:
        """Override error handling to show next steps for SSH permission errors."""
        if isinstance(error, SshAuthenticationError):
            # Call parent error handler first to show the original error
            try:
                super().handle_error(error, exit_code)
            except click.exceptions.Exit:
                # Parent handler would exit, but we want to prompt first
                pass

            # Try to resolve key permission issues
            key_path = Path(str(error.key_path)) if error.key_path else None
            permission_result = None

            if key_path:
                permission_result = check_and_resolve_if_key_permission_error(error, key_path)

            # Only show next actions if permission fix was NOT successful
            if permission_result in [
                PermissionCheckResult.NOT_PERMISSION_ERROR,
                PermissionCheckResult.PERMISSION_FIX_FAILED,
                PermissionCheckResult.USER_CANCELLED,
            ]:
                # Show general SSH troubleshooting suggestions
                next_steps = []

                # Add permission fix suggestion if it was a permission error that wasn't fixed
                if (
                    permission_result
                    in [
                        PermissionCheckResult.PERMISSION_FIX_FAILED,
                        PermissionCheckResult.USER_CANCELLED,
                    ]
                    and key_path
                ):
                    next_steps.append(
                        f"[accent]chmod 600 {key_path}[/accent] [muted]— Fix key permissions manually[/muted]"
                    )

                # Add general troubleshooting steps
                next_steps.extend(
                    [
                        "[accent]flow ssh-keys get -v[/accent] [muted]— Check your registered SSH keys[/muted]",
                        "[accent]MITHRIL_SSH_KEY=/path/to/key flow ssh[/accent] [muted]— Override SSH key[/muted]",
                    ]
                )

                self.show_next_actions(next_steps, title="Fix SSH Authentication", max_items=4)

            # If permission was successfully fixed, automatically retry the SSH connection
            if (
                permission_result == PermissionCheckResult.PERMISSION_FIXED
                and self._current_task_id
            ):
                try:
                    console.print("[dim]Retrying SSH connection...[/dim]")

                    # We need to get the client and task again to retry
                    client = sdk_factory.create_client(auto_init=True)
                    task = client.get_task(self._current_task_id)

                    # Retry the SSH connection
                    if self._current_command:
                        # For remote commands
                        task.shell(
                            command=self._current_command,
                            node=self._current_node or 0,
                            record=False,
                        )
                    else:
                        # For interactive sessions
                        task.shell(command=None, node=self._current_node or 0, record=False)

                    return  # Success - don't exit with error code

                except FlowError as retry_error:
                    console.print(f"[red]✗ Retry failed: {retry_error}[/red]")
        else:
            # For non-SSH authentication errors, just call parent handler
            super().handle_error(error, exit_code)

        # Exit cleanly
        raise SystemExit(exit_code)

    @property
    def manages_own_progress(self) -> bool:
        """SSH manages its own progress display."""
        return True

    @property
    def help(self) -> str:
        """Short help text for command listing (full help is in command docstring)."""
        return "SSH to running GPU instances - Interactive shell or remote command execution"

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Show running tasks; SSH may still be provisioning.

        We purposely allow tasks without an SSH endpoint yet so users can
        select a running task and the command will wait for SSH readiness.
        """
        return TaskFilter.running_only

    def get_selection_title(self) -> str:
        labels = get_entity_labels()
        return f"Select {labels.article} running {labels.singular} to SSH into"

    def get_no_tasks_message(self) -> str:
        labels = get_entity_labels()
        return f"No running {labels.empty_plural} available for SSH"

    # Command execution
    def execute_on_task(self, task: Task, client, **kwargs) -> None:
        """Execute SSH connection on the selected task with a unified timeline."""
        command = kwargs.get("command")
        node = kwargs.get("node")
        record = kwargs.get("record", False)

        # Store task context for error handling
        self._current_task_id = task.task_id
        self._current_node = node
        self._current_command = command

        # Validate node parameter for multi-instance tasks (shared helper)
        from flow.cli.utils.task_utils import (
            validate_node_index,  # local import to avoid CLI cold-start cost
        )

        total_nodes = task.num_instances

        multinode_command = command and total_nodes > 1 and node is None
        if multinode_command:
            node_indices = list(range(total_nodes))
            self._execute_multi_nodes(task, client, command, node_indices, record)
            return

        # Single-node path
        target_node = int(node or 0)
        validate_node_index(task, target_node)

        # Cache-first direct exec for the common case: interactive, not recording, node 0
        try:
            if self._try_direct_exec_from_cache(
                task, client, node=target_node, command=command, record=record
            ):
                return
        except Exception:  # noqa: BLE001
            pass

        self._execute_single_node(task, client, command, target_node, record)

    def _prepare_ssh_task(self, task: Task, client, timeline):
        """Common SSH preparation logic shared between single and multi-node execution."""
        try:
            self._ensure_provider_support(client)
            self._ensure_default_ssh_key(client)
            task = self._maybe_wait_for_ssh(task, client, timeline)
            return self._refresh_task(client, task)
        except Exception as e:
            self._handle_connect_error(e, client, task, timeline)
            raise

    def _execute_single_node(
        self, task: Task, client, command: str | None, node: int, record: bool
    ) -> None:
        """Execute SSH on a single node using SDK."""
        # Unified timeline
        from flow.cli.utils.step_progress import StepTimeline  # local import by design
        from flow.cli.utils.timeline_context import timeline_context

        timeline = StepTimeline(console, title="flow ssh", title_animation="auto")

        with timeline_context(timeline):
            timeline.start()
            finished = False
            try:
                task = self._prepare_ssh_task(task, client, timeline)

                task = resolve_endpoint(client, task, node)
                if not self._is_fast_mode():
                    maybe_wait_handshake(client, task, timeline)

                # Finish before handing control to the user's terminal/output
                if command:
                    idx = timeline.add_step("Executing remote command", show_bar=False)
                    timeline.start_step(idx)
                    timeline.complete_step()
                    timeline.finish()
                    finished = True
                else:
                    timeline.finish()
                    finished = True

            except Exception:
                finish_current_timeline()
                finished = True
                raise
            finally:
                if not finished:
                    timeline.finish()

        # Execute shell OUTSIDE timeline context to prevent display conflicts
        task.shell(command=command, node=node, record=record)
        self._maybe_print_next_actions(task, ran_command=bool(command))

    def _execute_multi_nodes(
        self,
        task: Task,
        client,
        command: str,
        node_indices: list[int],
        record: bool,
    ) -> None:
        """Execute SSH command on all nodes in parallel."""
        from flow.cli.utils.step_progress import StepTimeline  # local import by design

        total_nodes = len(node_indices)

        console.print(f"[dim]Executing command on {task.name} (all {total_nodes} nodes)[/dim]\n")

        # Unified timeline for all nodes
        timeline = StepTimeline(console, title="flow ssh", title_animation="auto")
        timeline.start()
        timeline.reserve_total(total_nodes)

        # Setup common requirements once
        try:
            task = self._prepare_ssh_task(task, client, timeline)
        except Exception:
            timeline.finish()
            raise

        # Pre-create all steps for parallel execution
        step_indices = {}
        for n in node_indices:
            step_label = f"Executing on node {n}"
            cmd_idx = timeline.add_step(step_label, show_bar=False)
            step_indices[n] = cmd_idx

        # Shared state for synchronization
        interrupted = threading.Event()

        def execute_on_node(node_idx: int) -> dict:
            """Execute command on a single node and return the result."""
            step_idx = step_indices[node_idx]

            try:
                # Start this step
                timeline.start_step(step_idx)

                # Check for early interruption
                if interrupted.is_set():
                    timeline.fail_step("Interrupted by user")
                    return {"node": node_idx, "status": "interrupted"}

                # Resolve endpoint for this specific node
                node_task = self._resolve_endpoint(client, task, node_idx)

                # Execute the command and capture output for clean display
                output = client.shell(
                    node_task.task_id,
                    command=command,
                    node=node_idx,
                    progress_context=None,
                    record=record,
                    capture_output=True,
                )

                # Mark success and return output
                timeline.complete_step()
                return {
                    "node": node_idx,
                    "status": "success",
                    "output": output or "",
                }

            except KeyboardInterrupt:
                interrupted.set()
                timeline.fail_step("Interrupted by user")
                return {"node": node_idx, "status": "interrupted"}
            except Exception as e:  # noqa: BLE001
                timeline.fail_step(str(e))
                return {"node": node_idx, "status": "error", "error": str(e)}

        # Execute all nodes and collect results
        results = {}
        try:
            # Limit concurrent connections to avoid overwhelming the system
            max_workers = min(total_nodes, int(os.getenv("FLOW_SSH_MAX_PARALLEL", "10")))

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                futures = {executor.submit(execute_on_node, n): n for n in node_indices}

                try:
                    # Collect results as futures complete
                    for future in concurrent.futures.as_completed(futures.keys()):
                        try:
                            result = future.result()
                            results[result["node"]] = result
                        except Exception as e:  # noqa: BLE001
                            # Handle any unexpected exceptions
                            node_idx = futures[future]
                            results[node_idx] = {
                                "node": node_idx,
                                "status": "error",
                                "error": str(e),
                            }
                except KeyboardInterrupt:
                    interrupted.set()
                    console.print("\n[dim]Interrupting parallel execution...[/dim]")
                    # Cancel remaining futures
                    for future in futures:
                        future.cancel()
                    # Wait a bit for graceful shutdown
                    concurrent.futures.wait(futures.keys(), timeout=2.0)
                    # Collect any results that completed before cancellation
                    for future in futures:
                        if future.done() and not future.cancelled():
                            try:
                                result = future.result()
                                results[result["node"]] = result
                            except Exception:  # noqa: BLE001
                                pass
        except KeyboardInterrupt:
            interrupted.set()
            console.print("\n[dim]Command execution interrupted[/dim]")

        timeline.finish()

        # Display captured outputs sequentially by node index to avoid interleaving
        for node_idx in sorted(node_indices):
            if node_idx in results:
                result = results[node_idx]
                if result.get("status") == "success":
                    console.print(f"[dim]→ node {node_idx}:[/dim]")
                    output = result.get("output", "")
                    if output:
                        console.print(output, end="")
                    else:
                        console.print("[dim]No output captured[/dim]")
                elif result.get("status") == "error":
                    console.print(
                        f"[dim]→ node {node_idx}:[/dim] [red]Error: {result.get('error', 'Unknown error')}[/red]"
                    )
                elif result.get("status") == "interrupted":
                    console.print(f"[dim]→ node {node_idx}:[/dim] [yellow]Interrupted[/yellow]")

        # Print summary
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        error_count = sum(1 for r in results.values() if r.get("status") == "error")
        interrupted_count = sum(1 for r in results.values() if r.get("status") == "interrupted")

        # Always display a summary
        summary_parts = [f"{success_count} successful"]
        if error_count > 0:
            summary_parts.append(f"{error_count} failed")
        if interrupted_count > 0:
            summary_parts.append(f"{interrupted_count} interrupted")

        summary_text = ", ".join(summary_parts)
        console.print(f"\n[dim]Command completed: {summary_text} ({total_nodes} total nodes)[/dim]")

    # ----- Cohesive helpers (extracted for testability) -----
    def _ensure_provider_support(self, client) -> None:
        """Ensure the current provider supports remote operations, else guide the user.

        Uses a lightweight capability probe and raises a ClickException if unsupported.
        """
        try:
            _ = client.get_remote_operations()
        except (AttributeError, NotImplementedError):
            from flow.cli.utils.provider_support import print_provider_not_supported

            print_provider_not_supported(
                "remote operations",
                tips=[
                    "Try again after switching provider: [accent]flow setup --provider mithril[/accent]",
                    "Open a shell via the provider UI if available",
                ],
            )
            raise click.ClickException("Provider does not support remote operations")

    def _ensure_default_ssh_key(self, client) -> None:
        """Best-effort default SSH key creation; logs at debug on failure.

        Avoids silent hangs where instances never expose SSH due to missing keys.
        """
        log = logging.getLogger(__name__)
        try:
            from flow.cli.utils.ssh_launch_keys import (
                ensure_default_project_ssh_key as _ensure,
            )

            _ensure(client)
        except Exception as e:  # noqa: BLE001
            # Best-effort: log only at debug
            try:
                log.debug("ensure_default_ssh_key failed: %s", e)
            except Exception:  # noqa: BLE001
                pass

    def _maybe_wait_for_ssh(self, task: Task, client, timeline):
        """Wait for SSH details only when needed, with accurate messaging.

        - If the task is already RUNNING but lacks an endpoint, show a short
          "Resolving SSH endpoint" step instead of a long "Provisioning" step.
        - Fall back to the longer provisioning message only when the task
          truly looks like it's still starting.
        """
        if self._is_fast_mode() or getattr(task, "ssh_host", None):
            return task

        from flow.cli.utils.step_progress import (  # local import
            SSHWaitProgressAdapter,
            build_provisioning_hint,
            build_wait_hints,
        )
        from flow.sdk.ssh_utils import DEFAULT_PROVISION_MINUTES, SSHNotReadyError

        try:
            from flow.sdk.models import TaskStatus as _TaskStatus  # local import
        except Exception:  # noqa: BLE001
            _TaskStatus = None  # type: ignore[assignment]

        # Determine copy and timeout based on current state/age
        try:
            baseline = int(getattr(task, "instance_age_seconds", 0) or 0)
        except (TypeError, ValueError):
            baseline = 0

        is_running = False
        try:
            if _TaskStatus is not None:
                is_running = getattr(task, "status", None) == getattr(_TaskStatus, "RUNNING", None)
            else:
                is_running = str(getattr(task, "status", "")).lower() == "running"
        except Exception:  # noqa: BLE001
            is_running = False

        # Shorter resolve window for running tasks; otherwise use provisioning budget
        if is_running or baseline >= 60:
            step_label = "Resolving SSH endpoint"
            estimated_seconds = int(os.getenv("FLOW_SSH_RESOLVE_TIMEOUT", "180"))
            hint = build_wait_hints("SSH", "flow ssh")
        else:
            step_label = f"Provisioning instance (up to {DEFAULT_PROVISION_MINUTES}m)"
            estimated_seconds = DEFAULT_PROVISION_MINUTES * 60
            hint = build_provisioning_hint("instance", "flow ssh")

        step_idx = timeline.add_step(
            step_label,
            show_bar=True,
            estimated_seconds=estimated_seconds,
            baseline_elapsed_seconds=baseline,
        )
        adapter = SSHWaitProgressAdapter(
            timeline,
            step_idx,
            estimated_seconds,
            baseline_elapsed_seconds=baseline,
        )
        try:
            with adapter:
                timeline.set_active_hint_text(hint)
                return client.wait_for_ssh(
                    task_id=task.task_id,
                    timeout=estimated_seconds,
                    show_progress=False,
                    progress_adapter=adapter,
                )
        except SSHNotReadyError as e:
            timeline.fail_step(str(e))
            raise SystemExit(1)

    def _refresh_task(self, client, task: Task) -> Task:
        """Fetch a fresh view of the task if possible."""
        with suppress(FlowError):
            return client.get_task(task.task_id)
        return task

    def _handle_connect_error(self, e: Exception, client, task: Task, timeline) -> None:
        """Render a helpful failure and a manual connection hint when possible."""
        provider_name = (
            getattr(getattr(client, "config", None), "provider", None)
            or os.environ.get("FLOW_PROVIDER")
            or "mithril"
        )
        connection_cmd = None
        with suppress(Exception):  # best-effort formatting from provider
            ProviderClass = plugin_registry.get_provider(provider_name)
            if ProviderClass and hasattr(ProviderClass, "format_connection_hint"):
                connection_cmd = ProviderClass.format_connection_hint(task)
        if connection_cmd:
            from flow.cli.utils.theme_manager import theme_manager as _tm_warn

            warn = _tm_warn.get_color("warning")
            console.print(
                f"\n[{warn}]Connection failed. You can try connecting manually with:[/{warn}]"
            )
            console.print(f"  {connection_cmd}\n")
        req_id = getattr(e, "request_id", None)
        if req_id:
            timeline.fail_step(f"{e!s}\nRequest ID: {req_id}")
        else:
            timeline.fail_step(str(e))

    def _maybe_print_next_actions(self, task: Task, ran_command: bool) -> None:
        if ran_command:
            return
        task_ref = task.name or task.task_id
        self.show_next_actions(
            [
                f"View logs: [accent]flow logs {task_ref} --follow[/accent]",
                f"Check status: [accent]flow status {task_ref}[/accent]",
                f"Run nvidia-smi: [accent]flow ssh {task_ref} -- nvidia-smi[/accent]",
                "Enter container: [accent]docker exec -it main bash -l || docker exec -it main sh -l[/accent]",
            ]
        )

    def _is_fast_mode(self) -> bool:
        """Centralized FAST mode detection supporting config and env strings."""
        try:
            from flow.application.config.runtime import settings  # local import by design

            v = (settings.ssh or {}).get("fast")
            if isinstance(v, bool):
                return v
        except Exception:  # noqa: BLE001
            pass
        env = os.getenv("FLOW_SSH_FAST", "").strip().lower()
        return env in {"1", "true", "yes", "on"}

    def _try_direct_exec_from_cache(
        self, task: Task, client, *, node: int, command: str | None, record: bool
    ) -> bool:
        """Try a zero-API, cache-first SSH exec for fastest UX.

        Returns True if we started ssh (process may be replaced), else False.
        """
        if command is not None or record or int(node or 0) != 0:
            return False

        # Endpoint from last status cache or task fields
        from flow.cli.utils.task_index_cache import TaskIndexCache as _TIC

        def get_host_and_port():
            """Get host and port from cache first, then task attributes."""
            cached = _TIC().get_cached_task(getattr(task, "task_id", ""))

            ssh_port = get_ssh_port(task, cached)

            # Try cache first
            if cached:
                # Try ssh_hosts list for multi-node tasks
                hosts = cached.get("ssh_hosts")
                if hosts and isinstance(hosts, list) and 0 <= node < len(hosts):
                    return hosts[node], ssh_port

                # Fallback to single ssh_host
                if cached.get("ssh_host"):
                    return cached.get("ssh_host"), ssh_port

            # Fallback to task attributes
            task_host = getattr(task, "ssh_host", None)
            if task_host:
                return task_host, ssh_port

            return None, ssh_port

        host, port = get_host_and_port()
        if not host:
            return False

        # Key from cache only; if missing, defer to normal provider resolution
        try:
            from flow.core.utils.ssh_key_cache import SSHKeyCache as _KC

            key_path = _KC().get_key_path(getattr(task, "task_id", ""))
        except Exception:  # noqa: BLE001
            key_path = None
        if not key_path:
            return False
        from flow.cli.utils.ssh_helpers import build_ssh_argv

        ssh_argv = build_ssh_argv(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=str(host),
            port=int(port or 22),
            key_path=str(key_path),
            extra_ssh_args=None,
            remote_command=None,
        )

        try:
            from flow.cli.utils.ssh_helpers import SshStack as _S

            if not _S.is_ssh_ready(
                user=getattr(task, "ssh_user", "ubuntu"),
                host=str(host),
                port=int(port or 22),
                key_path=Path(key_path),
            ):
                # SSH not ready, fall back to normal flow
                return False

        except Exception as e:  # noqa: BLE001
            # If readiness check fails, fall back to normal flow
            logger.debug(f"SSH readiness check failed: {e}")
            return False

        try:
            os.execvp(ssh_argv[0], ssh_argv)
        except Exception:  # noqa: BLE001
            logger.debug("oht _try_direct_exec_from_cache exception")
            subprocess.run(ssh_argv, check=False)
        return True

    def get_command(self) -> click.Command:
        # Import completion function
        # from flow.cli.utils.mode import demo_aware_command
        from flow.cli.ui.runtime.shell_completion import complete_task_ids

        # Generate dynamic help text based on nomenclature mode
        labels = get_entity_labels()
        identifier_name = (
            "INSTANCE_IDENTIFIER" if labels.singular == "instance" else "TASK_IDENTIFIER"
        )
        entity_label = labels.singular.capitalize()

        @click.command(name=self.name)
        @click.argument(
            "task_identifier",
            required=False,
            shell_complete=complete_task_ids,
            metavar=f"[{identifier_name}]",
        )
        # Trailing command only; no -c/--command flag
        @click.option(
            "--node",
            type=int,
            default=None,
            help="Node index for multi-instance tasks (remote commands default to all nodes; interactive default is 0)",
        )
        @click.option(
            "--container",
            is_flag=True,
            hidden=True,  # hide in help to avoid false positive '-c' test
            help=(
                "Open inside the task container (docker exec) or run the given command in the container"
            ),
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed help and examples")
        @click.option(
            "--json", "output_json", is_flag=True, help="Output connection parameters as JSON"
        )
        @click.option(
            "--record",
            is_flag=True,
            hidden=True,
            help="Record session to host logs (viewable with flow logs --source host)",
        )
        @click.option(
            "--fast",
            is_flag=True,
            help="Skip readiness wait; prefer cached endpoint and connect immediately",
        )
        # @demo_aware_command()
        @click.argument("remote_cmd", nargs=-1)
        @cli_error_guard(self)
        def ssh(
            task_identifier: str | None,
            node: int | None,
            verbose: bool,
            record: bool,
            remote_cmd: tuple[str, ...],
            output_json: bool,
            container: bool,
            fast: bool,
        ):
            if fast:
                try:
                    os.environ["FLOW_SSH_FAST"] = "1"
                except Exception:  # noqa: BLE001
                    pass

            if verbose:
                console.print("\n[bold]Advanced SSH Usage:[/bold]\n")
                console.print("Multi-instance tasks (0-based node index):")
                console.print("  flow ssh distributed-job --node 0    # Connect to first node")
                console.print("  flow ssh distributed-job --node 1    # Connect to second node")
                console.print("Remote commands:")
                console.print(
                    "  flow ssh task -- nvidia-smi          # Run on all nodes (multi-node)"
                )
                console.print("  flow ssh task --node 0 -- nvidia-smi # Run on a specific node\n")

                console.print("File transfer:")
                console.print("  scp file.py $(flow ssh task -- echo $USER@$HOSTNAME):~/")
                console.print(
                    "  rsync -av ./data/ $(flow ssh task -- echo $USER@$HOSTNAME):/data/\n"
                )

                console.print("Container mode:")
                console.print("  (Use the container flag to exec inside the main container)")
                console.print("  Examples: enter shell, or run nvidia-smi inside the container\n")

                console.print("Port forwarding:")
                console.print(
                    "  ssh -L 8888:localhost:8888 $(flow ssh task -- echo $USER@$HOSTNAME)"
                )
                console.print(
                    "  ssh -L 6006:localhost:6006 $(flow ssh task -- echo $USER@$HOSTNAME)  # TensorBoard\n"
                )

                console.print("Monitoring:")
                console.print("  flow ssh task -- watch -n1 nvidia-smi    # GPU usage")
                console.print("  flow ssh task -- htop                     # System resources")
                console.print("  flow ssh task -- tail -f output.log       # Stream logs")
                console.print(
                    "  flow ssh task --node 0 -- free -h         # Memory on a specific node\n"
                )

                console.print("Troubleshooting:")
                console.print("  • No SSH info? Wait 2-5 minutes for instance provisioning")
                console.print(
                    "  • Permission denied? Check flow ssh list or override temporarily: MITHRIL_SSH_KEY=/path/to/private/key flow ssh <task>"
                )
                console.print("  • Task terminated? Check: flow status <name>\n")
                return

            # If a trailing command was provided after '--', use it
            # Normalize selection identifiers early (works after `flow status`)
            if task_identifier:
                task_identifier = self._normalize_task_identifier(task_identifier)
            command = " ".join(remote_cmd) if remote_cmd else None

            # Debug logging for command parsing
            logger.debug(
                "SSH command parsing: task_identifier=%r, remote_cmd=%r, parsed_command=%r, node=%r",
                task_identifier,
                remote_cmd,
                command,
                node,
            )

            # JSON mode requires a concrete task identifier to avoid interactive selector output
            if output_json:
                if not task_identifier:
                    raise click.UsageError("--json requires a task identifier (id or name)")
                if container:
                    raise click.UsageError("--json cannot be combined with --container")

                client = sdk_factory.create_client(auto_init=True)
                # Resolve ':dev', indices, names, or IDs consistently with normal ssh flow
                task, _err = _resolve_identifier(client, task_identifier)
                if task is None:
                    # _err contains a human-readable message
                    raise click.UsageError(_err or "Task not found")
                # Try to resolve endpoint, fallback to task fields
                try:
                    host, port = client.resolve_ssh_endpoint(task.task_id, node=int(node or 0))
                except Exception:  # noqa: BLE001
                    host = getattr(task, "ssh_host", None)
                    port = get_ssh_port(task)
                user = getattr(task, "ssh_user", "ubuntu")
                key_path = client.get_task_ssh_connection_info(task.task_id)
                if isinstance(key_path, SSHKeyNotFoundError):
                    key_path = None
                ssh_argv = build_ssh_argv(
                    user=user,
                    host=host,
                    port=port,
                    key_path=str(key_path) if key_path else None,
                    extra_ssh_args=None,
                    remote_command=None,
                )
                cmd = ssh_command_string(ssh_argv)
                print_json(
                    {
                        "user": user,
                        "host": host,
                        "port": port,
                        "key_path": str(key_path) if key_path else None,
                        "ssh_command": cmd,
                        "task_id": task.task_id,
                        "task_name": getattr(task, "name", None),
                        "node": int(node or 0),
                    }
                )
                return

            # Transform command for container mode before execution
            if container:
                command = self._wrap_container_cmd(command, interactive=not bool(command))

            self._execute(task_identifier, command, node, record, fast=fast)

        # Set dynamic help text based on nomenclature
        # Note: Using triple-quoted string with literal \b markers for Click's formatter
        help_text = f"""SSH to running GPU instances - Interactive shell or remote command execution

{identifier_name}: {entity_label} ID or name (optional - interactive selector if omitted)

\b
Quick connect:
    flow ssh                         # Interactive selector
    flow ssh my-training             # Connect by name
    flow ssh abc-123                 # Connect by ID

\b
Remote commands:
    flow ssh <{labels.singular}> -- nvidia-smi      # Run command on all nodes (multi-node)
    flow ssh <{labels.singular}> -- htop            # Monitor system resources
    flow ssh <{labels.singular}> --node 0 -- nvidia-smi  # Run on a specific node (0-based)

\b
Tip: Use verbose help for container mode and advanced examples (flow ssh --verbose)."""

        ssh.help = help_text
        ssh.__doc__ = help_text

        return ssh

    def _execute(
        self,
        task_identifier: str | None,
        command: str | None,
        node: int | None = None,
        record: bool = False,
        *,
        fast: bool = False,
    ) -> None:
        """Execute SSH connection or command."""
        # For non-interactive commands, use standard flow
        if command:
            self.execute_with_selection(
                task_identifier,
                command=command,
                node=node,
                record=record,
                fast=fast,
            )
            return

        # Delegate to selection without pre-animations; the timeline inside execute_on_task owns the UX
        self.execute_with_selection(
            task_identifier,
            command=command,
            node=node,
            record=record,
            fast=fast,
        )

    # ----- CLI-facing utilities -----
    def _normalize_task_identifier(self, raw: str) -> str:
        """Normalize selection grammar to a single task id or raise UsageError."""
        from flow.cli.utils.selection_helpers import parse_selection_to_task_ids

        ids, err = parse_selection_to_task_ids(raw)
        if err:
            raise click.UsageError(err)
        if ids is not None:
            if len(ids) != 1:
                raise click.UsageError("Selection must resolve to exactly one task for ssh")
            return ids[0]
        return raw

    # Deprecated -c/--command flag removed; trailing command is the supported path

    def _wrap_container_cmd(self, user_cmd: str | None, interactive: bool) -> str | None:
        """Wrap a user command to run inside the main container, or pick an interactive shell.

        Always run via POSIX shell inside the container; prefer bash if present.
        """
        if user_cmd:
            return f"docker exec main sh -lc {shlex.quote(user_cmd)}"
        return "docker exec -it main bash -l || docker exec -it main sh -l" if interactive else None


# Export command instance
command = SSHCommand()
