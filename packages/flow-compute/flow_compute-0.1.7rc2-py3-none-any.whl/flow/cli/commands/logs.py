"""Logs command for viewing task output.

Provides both historical log retrieval and real-time streaming.
Supports stdout/stderr selection and tail functionality.

Examples:
    View recent logs:
        $ flow logs task-abc123

    Stream logs in real-time:
        $ flow logs task-abc123 -f

    Show last 50 lines of stderr:
        $ flow logs task-abc123 --stderr -n 50
"""

import re
import time
from datetime import datetime

import click

import flow.sdk.factory as sdk_factory
from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.formatters import TaskFormatter
from flow.cli.ui.presentation.next_steps import render_next_steps_panel
from flow.cli.ui.presentation.nomenclature import get_entity_labels
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.step_progress import SSHWaitProgressAdapter, StepTimeline
from flow.cli.utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from flow.cli.utils.theme_manager import theme_manager
from flow.errors import FlowError

# Back-compat: expose Flow for tests that patch flow.cli.commands.logs.Flow
from flow.sdk.client import Flow  # noqa: F401
from flow.sdk.models import Task, TaskStatus


class LogsCommand(BaseCommand, TaskOperationCommand):
    """Logs command implementation.

    Handles both batch retrieval and streaming modes with automatic
    reconnection for long-running tasks.
    """

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    def _parse_since(self, since_str: str) -> datetime | None:
        """Parse since string to datetime (delegates to utils.time_spec)."""
        from flow.cli.utils.time_spec import parse_timespec

        return parse_timespec(since_str)

    def _format_log_line(self, line: str, node_idx: int, no_prefix: bool, full_prefix: bool) -> str:
        """Format a log line with node prefix."""
        if no_prefix:
            return line

        if full_prefix:
            prefix = f"[node-{node_idx}] "
        else:
            prefix = f"[{node_idx}] "

        return prefix + line

    def _filter_logs(self, logs: str, grep: str | None, since: datetime | None) -> list[str]:
        """Filter logs based on grep pattern and an optional since timestamp.

        Since filtering is best‑effort: if a line begins with a recognizable
        timestamp (ISO8601 or common "YYYY-MM-DD HH:MM:SS" forms), it will be
        parsed and compared. Lines without a timestamp are included.
        """
        lines = logs.splitlines(keepends=True)

        if grep:
            try:
                pattern = re.compile(grep)
                lines = [line for line in lines if pattern.search(line)]
            except re.error:
                # If grep is invalid, fall back to no grep filtering
                pass

        if since is not None:

            def parse_line_dt(s: str) -> datetime | None:
                s_strip = s.lstrip()
                # ISO8601 e.g., 2024-08-10T12:34:56Z or with offset/millis
                m = re.match(
                    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:\d{2}))",
                    s_strip,
                )
                if m:
                    txt = m.group(1)
                    try:
                        # fromisoformat doesn't support Z; normalize
                        txt = txt.replace("Z", "+00:00")
                        return datetime.fromisoformat(txt)
                    except Exception:  # noqa: BLE001
                        return None
                # Bracketed or space-separated e.g., [2024-08-10 12:34:56] or 2024-08-10 12:34:56
                m = re.match(r"^\[?(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})(?:\.\d+)?\]?", s_strip)
                if m:
                    txt = m.group(1)
                    try:
                        return datetime.fromisoformat(txt)
                    except Exception:  # noqa: BLE001
                        return None
                return None

            filtered: list[str] = []
            for line in lines:
                dt = parse_line_dt(line)
                if dt is not None:
                    try:
                        # Treat naive as UTC
                        if dt.tzinfo is None:
                            from datetime import timezone as _tz

                            dt = dt.replace(tzinfo=_tz.utc)
                        # Keep if at or after since
                        if dt >= since:
                            filtered.append(line)
                    except Exception:  # noqa: BLE001
                        filtered.append(line)
                else:
                    # No timestamp → keep
                    filtered.append(line)
            lines = filtered

        return lines

    def _get_node_display_name(self, task: Task, node_index: int, full_prefix: bool = False) -> str:
        """Get display name for a node in a multi-instance task.

        Args:
            task: Task object
            node_index: Index of the node
            full_prefix: If True, use full hostname/IP; if False, use "node-N" format

        Returns:
            Display name for the node (e.g., "node-0", "node-0 (10.0.0.1)", or "10.0.0.1")
        """
        instances = task.get_instances()

        if instances and node_index < len(instances):
            instance = instances[node_index]

            # Extract hostname/IP from instance
            # Note: task.get_instances() may return different types depending on context:
            # - dict: Raw API response with fields like ssh_host, instance_id
            # - str: Just an instance ID (from task.instances which is list[str])
            # - Instance object: Properly typed object with ssh_host attribute
            if isinstance(instance, dict):
                host = instance.get("ssh_host") or instance.get("instance_id")
            elif isinstance(instance, str):
                # Instance is just an ID string, can't get hostname from it
                host = None
            elif hasattr(instance, "ssh_host"):
                host = instance.ssh_host or getattr(instance, "instance_id", None)
            else:
                host = None

            if host:
                # If full_prefix requested, return the full host
                if full_prefix:
                    return host

                # For IP addresses, show as "node-N (IP)" for node 0, otherwise just "node-N"
                if self._is_ip_address(host):
                    if node_index == 0:
                        return f"node-0 ({host})"
                    return f"node-{node_index}"

                # For hostnames, use the hostname if full_prefix, otherwise node-N
                return host if full_prefix else f"node-{node_index}"

        return f"node-{node_index}"

    def _is_ip_address(self, s: str) -> bool:
        """Check if string is an IPv4 address."""
        if not isinstance(s, str):
            return False
        parts = s.split(".")
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

    @property
    def name(self) -> str:
        return "logs"

    @property
    def help(self) -> str:
        """Short help text for command listing (full help is in command docstring)."""
        labels = get_entity_labels()
        return f"View {labels.singular} output logs - stdout, stderr, real-time streaming"

    # Fetch list under spinner; stop before emitting logs to avoid interleaving
    @property
    def prefer_fetch_before_selection(self) -> bool:  # type: ignore[override]
        return True

    @property
    def _fetch_spinner_label(self) -> str:  # type: ignore[override]
        try:
            return f"Fetching {get_entity_labels().empty_plural} for log viewing"
        except Exception:  # noqa: BLE001
            return "Fetching tasks for log viewing"

    def progress_label_for_identifier(self, task_identifier: str) -> str:  # type: ignore[override]
        # Use index cache for a friendlier label when possible
        try:
            from flow.cli.utils.task_index_cache import TaskIndexCache as _Cache

            cache = _Cache()
            tid = task_identifier
            if task_identifier.startswith(":"):
                resolved, _ = cache.resolve_index(task_identifier)
                if resolved:
                    tid = resolved
            cached = cache.get_cached_task(tid)
            if cached:
                name = cached.get("name", tid)
                short = (tid[:12] + "…") if len(tid) > 12 else tid
                return f"Fetching logs from {name} ({short})"
        except Exception:  # noqa: BLE001
            pass
        return f"Fetching logs from {task_identifier}"

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Prefer running tasks but allow all."""
        return TaskFilter.with_logs

    def get_selection_title(self) -> str:
        labels = get_entity_labels()
        return f"Select {labels.article} {labels.singular} to view logs"

    def get_no_tasks_message(self) -> str:
        labels = get_entity_labels()
        return f"No running or completed {labels.empty_plural} found"

    # Command execution
    def execute_on_task(self, task: Task, client, **kwargs) -> None:
        """Execute log viewing on the selected task."""
        follow = kwargs.get("follow", False)
        tail = kwargs.get("tail", 100)
        stderr = kwargs.get("stderr", False)
        source = kwargs.get("source", "container")
        stream_opt = kwargs.get("stream")
        node = kwargs.get("node")
        since = kwargs.get("since")
        grep = kwargs.get("grep")
        no_prefix = kwargs.get("no_prefix", False)
        full_prefix = kwargs.get("full_prefix", False)
        output_json = kwargs.get("output_json", False)

        # Get entity labels for dynamic messaging
        labels = get_entity_labels()

        # Validate node parameter for multi-instance tasks via shared helper
        from flow.cli.utils.task_utils import validate_node_index

        is_multi_instance = task.num_instances > 1
        if node is not None:
            validate_node_index(task, node)

        # Determine selected stream honoring --stream over --stderr for forward compatibility
        selected_stream = "stderr" if stderr else (stream_opt if stream_opt else "stdout")

        # JSON output mode
        if output_json:
            from flow.cli.utils.json_output import error_json, iso_z, print_json, task_to_json

            # Disallow follow (also guarded earlier); return a structured error
            if follow:
                print_json(
                    error_json(
                        "--json is not supported with --follow",
                        hint=f"Use: flow logs <{labels.singular}> --json (without --follow) or stream without --json",
                    )
                )
                return

            # Normalize labels for output
            src_label = str(source or "auto").lower()
            stream_label = str(selected_stream or ("stderr" if stderr else "stdout")).lower()
            if src_label in ("both", "all") or stream_label == "combined":
                stream_label = "combined"

            # Fetch snapshot and emit as lines
            try:
                logs_text = client.logs(
                    task.task_id,
                    follow=False,
                    tail=tail,
                    stderr=(selected_stream == "stderr"),
                    source=source,
                    stream=selected_stream,
                )  # type: ignore[arg-type]
                if not isinstance(logs_text, str):
                    try:
                        logs_text = "".join(list(logs_text))
                    except Exception:  # noqa: BLE001
                        logs_text = str(logs_text)
            except Exception as e:  # noqa: BLE001
                print_json(error_json(f"Failed to fetch logs: {e}"))
                return

            since_dt = self._parse_since(since) if since else None
            filtered_lines = self._filter_logs(logs_text, grep, since_dt)
            # Keep consistent lines without trailing newlines
            lines = [ln.rstrip("\n") for ln in filtered_lines]

            print_json(
                {
                    "task": task_to_json(task),
                    "source": src_label,
                    "stream": stream_label,
                    "node": node,
                    "tail": tail,
                    "since": iso_z(since_dt) if since_dt else None,
                    "grep": grep or None,
                    "lines": lines,
                }
            )
            return

        task_display = getattr(
            self.task_formatter, "format_task_display", lambda t: (t.name or t.task_id)
        )(task)

        # Build unified timeline for non-JSON output
        timeline: StepTimeline | None = None
        if not output_json:
            timeline = StepTimeline(console, title="flow logs", title_animation="auto")
            timeline.start()

        if follow:
            # Ensure SSH/log readiness if needed (running tasks without ssh_host)
            if timeline and not task.ssh_host:
                from flow.sdk.ssh_utils import DEFAULT_PROVISION_MINUTES, SSHNotReadyError

                # Seed baseline from instance age to make resume realistic
                baseline = int(task.instance_age_seconds or 0)
                step_idx = timeline.add_step(
                    f"Provisioning instance (up to {DEFAULT_PROVISION_MINUTES}m)",
                    show_bar=True,
                    estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
                    baseline_elapsed_seconds=baseline,
                )
                adapter = SSHWaitProgressAdapter(
                    timeline,
                    step_idx,
                    DEFAULT_PROVISION_MINUTES * 60,
                    baseline_elapsed_seconds=baseline,
                )
                try:
                    with adapter:
                        # Unified provisioning hint (same as flow dev/ssh)
                        try:
                            from flow.cli.utils.step_progress import (
                                build_provisioning_hint as _bph,
                            )

                            timeline.set_active_hint_text(_bph("instance", "flow logs"))
                        except Exception:  # noqa: BLE001
                            pass
                        task = client.wait_for_ssh(
                            task_id=task.task_id,
                            timeout=DEFAULT_PROVISION_MINUTES * 60,
                            show_progress=False,
                            progress_adapter=adapter,
                        )
                except SSHNotReadyError as e:
                    timeline.fail_step(str(e))
                    timeline.finish()
                    return

            # Attach step
            if timeline:
                attach_idx = timeline.add_step(
                    f"Tailing last {tail} lines, then following", show_bar=False
                )
                timeline.start_step(attach_idx)
            # Enhanced log streaming with status indicator
            from rich.panel import Panel

            # Create header with task info
            from flow.cli.ui.formatters import GPUFormatter

            gpu_display = (
                GPUFormatter.format_ultra_compact(task.instance_type, task.num_instances)
                if task.instance_type
                else "N/A"
            )
            # Status string with robust fallback for mocks
            # Use get_display_status for consistency (e.g., "starting" vs "pending")
            display_status = self.task_formatter.get_display_status(task)
            status_display = self.task_formatter.format_status_with_color(display_status)

            # Explicitly show source/stream selection for clarity
            _src_label = str(source or "auto").lower()
            _stream_label = str(selected_stream or ("stderr" if stderr else "stdout")).lower()
            if _src_label in ("both", "all") or _stream_label == "combined":
                _stream_label = "combined"

            # Build descriptive source label with file paths
            source_description = {
                "auto": "Auto (container → startup fallback)",
                "container": "docker logs <container>",
                "startup": "/var/log/foundry/startup_script.log",
                "cloud-init": "/var/log/cloud-init-output.log",
                "host": "/var/log/foundry/ (SSH & startup logs)",
                "both": "docker logs <container> (stdout + stderr)",
                "all": "docker logs <container> (stdout + stderr)",
            }.get(_src_label, _src_label)

            # Show SSH endpoint if available
            ssh_info = (
                f"{task.ssh_host}:{task.ssh_port or 22}" if task.ssh_host else "connecting..."
            )

            # For auto mode, don't show stream in header since we might show files
            if _src_label == "auto":
                source_line = f"[bold]Source:[/bold] {source_description}"
            else:
                source_line = f"[bold]Source:[/bold] {source_description} ({_stream_label})"

            header = Panel(
                f"[bold]Task:[/bold] {task.name or task.task_id}\n"
                f"[bold]Status:[/bold] {status_display}\n"
                f"[bold]Instance:[/bold] {gpu_display}\n"
                f"[bold]SSH:[/bold] {ssh_info}\n"
                f"{source_line}",
                title="[bold accent]Log Stream[/bold accent]",
                border_style=theme_manager.get_color("accent"),
                padding=(0, 1),
                height=6,
            )

            console.print(header)
            console.print(
                f"[dim]Following logs... (Ctrl+C to stop){'  Filter: ' + grep if grep else ''}[/dim]\n"
            )
            if timeline:
                timeline.complete_step()

            try:
                # Use provider directly for node support
                provider = client._ensure_provider()
                facets = client._get_facets_for_provider(provider)
                if facets and getattr(facets, "logs", None):
                    stream = facets.logs.stream_task_logs(
                        task.task_id,
                        log_type=selected_stream if source == "container" else source or "auto",
                        follow=True,
                        tail=tail,
                        node=node,
                    )
                else:
                    # Fallback without node support
                    stream = client.logs(
                        task.task_id,
                        follow=True,
                        stderr=(selected_stream == "stderr"),
                        source=source,
                        stream=selected_stream,
                    )  # type: ignore[arg-type]
                # Support both iterators and plain strings from mocks
                if isinstance(stream, str):
                    for line in self._filter_logs(
                        stream, grep, self._parse_since(since) if since else None
                    ):
                        if is_multi_instance and not no_prefix:
                            node_idx = 0  # Placeholder - would come from provider
                            line = self._format_log_line(line, node_idx, no_prefix, full_prefix)
                        console.print(line, end="", markup=False, highlight=False)
                else:
                    for line in stream:  # type: ignore[assignment]
                        if is_multi_instance and not no_prefix:
                            node_idx = 0  # Placeholder - would come from provider
                            line = self._format_log_line(line, node_idx, no_prefix, full_prefix)
                        if grep and not re.search(grep, line):
                            continue
                        console.print(line, end="", markup=False, highlight=False)
            except KeyboardInterrupt:
                console.print("\n[dim]Stopped following logs[/dim]")
            finally:
                if timeline:
                    timeline.finish()
        else:
            # Retry loop for instances that may be starting
            # Default short wait; extend when it's likely the instance needs to start
            retry_delay = 2
            src_lower = (source or "").lower().strip()
            is_host_like = src_lower in {"host", "startup", "cloud-init"}
            pending_like = task.status == TaskStatus.PENDING
            max_retries = 30 if (is_host_like or pending_like) else 6
            logs = None
            waiting_hint_set = False

            # Fetch step with clear source indication including file paths
            fetch_idx = None
            if timeline:
                # For auto mode, don't show stream or all possibilities
                # The actual source will be shown when we display them
                if str(source).lower() == "auto":
                    fetch_idx = timeline.add_step(
                        f"Fetching last {tail} lines",
                        show_bar=False,
                    )
                else:
                    src_label = {
                        "container": "docker logs",
                        "startup": "/var/log/foundry/startup_script.log",
                        "cloud-init": "/var/log/cloud-init-output.log",
                        "host": "/var/log/foundry/",
                        "both": "docker logs (combined)",
                        "all": "docker logs (combined)",
                    }.get(str(source).lower(), source)
                    # Only show stream for container sources
                    src_lower = str(source).lower()
                    if src_lower in ("container", "both", "all"):
                        fetch_idx = timeline.add_step(
                            f"Fetching last {tail} lines from {src_label} ({selected_stream})",
                            show_bar=False,
                        )
                    else:
                        fetch_idx = timeline.add_step(
                            f"Fetching last {tail} lines from {src_label}",
                            show_bar=False,
                        )
                timeline.start_step(fetch_idx)

            for _attempt in range(max_retries):
                try:
                    # TODO: Multi-instance support requires provider implementation
                    # For now, fetch logs normally
                    logs = None
                    primary_ok = False
                    try:
                        # Try provider logs API first with source/stream preserved
                        # Note: client.logs doesn't support node parameter yet, so we need to use the provider directly
                        provider = client._ensure_provider()
                        facets = client._get_facets_for_provider(provider)
                        if facets and getattr(facets, "logs", None):
                            logs = facets.logs.get_task_logs(
                                task.task_id,
                                tail=tail,
                                log_type=(
                                    selected_stream if source == "container" else source or "auto"
                                ),
                                node=node,
                            )
                        else:
                            # Fallback without node support
                            logs = client.logs(
                                task.task_id,
                                follow=False,
                                tail=tail,
                                stderr=stderr,
                                source=source,
                                stream=selected_stream,
                            )
                        primary_ok = True
                    except Exception:  # noqa: BLE001
                        primary_ok = False
                        # Surface a quick hint about what's happening
                        if timeline and not waiting_hint_set:
                            try:
                                from rich.text import Text as _Text

                                from flow.cli.utils.theme_manager import theme_manager as _tm

                                tip = _Text()
                                tip.append("Connecting via SSH to fetch logs from instance… ")
                                tip.append("Tip:", style=_tm.get_color("muted"))
                                tip.append(" use ")
                                tip.append(
                                    f"flow logs {task.name or task.task_id} -f",
                                    style=_tm.get_color("accent"),
                                )
                                tip.append(" to follow in real time.")
                                timeline.set_active_hint_text(tip)
                            except Exception:  # noqa: BLE001
                                pass

                    # Normalize and/or fallback
                    if isinstance(logs, bytes):
                        logs = logs.decode("utf-8", errors="ignore")
                    if not isinstance(logs, str):
                        try:
                            task_obj = client.get_task(task.task_id)
                            # Some providers/tests expose logs() on the task
                            if hasattr(task_obj, "logs") and callable(task_obj.logs):
                                logs = task_obj.logs(
                                    follow=False,
                                    tail=tail,
                                    stderr=stderr,
                                    source=source,
                                    stream=selected_stream,
                                    node=node,
                                )
                                if isinstance(logs, bytes):
                                    logs = logs.decode("utf-8", errors="ignore")
                                if not isinstance(logs, str):
                                    logs = str(logs)
                            else:
                                # Last resort: coerce to string
                                logs = str(logs) if logs is not None else ""
                        except Exception:
                            # If both attempts fail, re-raise the primary error if that path was tried
                            if primary_ok:
                                raise
                            # else, surface a simple message and break
                            logs = ""

                    # Check if we got a provider-side guidance message instead of actual logs
                    # Note: This is a temporary check until providers consistently raise InstanceNotReadyError
                    lower = logs.lower() if isinstance(logs, str) else str(logs).lower()

                    # If the provider explicitly reports that the container hasn't started yet for
                    # an explicit container request, surface that guidance instead of generic SSH text.
                    src_lower = (source or "").lower().strip()
                    is_container_src = src_lower in {"container", "both", "all"}
                    if is_container_src and "container not started" in lower:
                        # Break and display provider guidance
                        break

                    # Treat common SSH-not-ready/provider endpoint errors as a transient start-up state
                    # so we can wait a bit and show helpful guidance instead of failing immediately.
                    endpoint_not_ready = any(
                        phrase in lower
                        for phrase in (
                            "no public endpoint available",
                            "ssh setup failed",
                            "no ssh access",
                            "not accessible via ssh",
                            "no ssh endpoint",
                        )
                    )

                    if logs and (
                        "waiting for instance" in lower
                        or "instance is still starting" in lower
                        or "ssh is not ready" in lower
                        or "task pending" in lower
                        or ("not available yet" in lower and not is_container_src)
                        or endpoint_not_ready
                    ):
                        # Quietly wait; show a light hint once
                        if timeline and not waiting_hint_set:
                            try:
                                from rich.text import Text as _Text

                                from flow.cli.utils.theme_manager import theme_manager as _tm

                                tip = _Text()
                                tip.append("Instance is starting; waiting for logs. ")
                                tip.append("Tip:", style=_tm.get_color("muted"))
                                tip.append(" run ")
                                tip.append(
                                    f"flow logs {task.name or task.task_id} -f",
                                    style=_tm.get_color("accent"),
                                )
                                tip.append(" to follow when ready.")
                                timeline.set_active_hint_text(tip)
                            except Exception:  # noqa: BLE001
                                pass
                            waiting_hint_set = True
                        time.sleep(retry_delay)
                        continue

                    # Got real logs or empty logs - break out
                    break

                except FlowError as e:
                    # Handle common errors with quiet backoff
                    error_msg = str(e)
                    if "not ready" in error_msg.lower() or "starting up" in error_msg.lower():
                        if timeline and not waiting_hint_set:
                            try:
                                from rich.text import Text as _Text

                                from flow.cli.utils.theme_manager import theme_manager as _tm

                                tip = _Text()
                                tip.append("Instance is starting; waiting for logs. ")
                                tip.append("Tip:", style=_tm.get_color("muted"))
                                tip.append(" run ")
                                tip.append(
                                    f"flow logs {task.name or task.task_id} -f",
                                    style=_tm.get_color("accent"),
                                )
                                tip.append(" to follow when ready.")
                                timeline.set_active_hint_text(tip)
                            except Exception:  # noqa: BLE001
                                pass
                            waiting_hint_set = True
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise
            else:
                # Max retries exceeded - show helpful message
                if timeline:
                    timeline.fail_step("Instance is taking longer than expected")
                    timeline.finish()
                from flow.cli.utils.theme_manager import theme_manager as _tm

                task_ref = task.name or task.task_id
                src_lower = (source or "").lower().strip()

                # Tailor the guidance for explicit container requests
                if src_lower in {"container", "both", "all"}:
                    console.print(
                        f"[{_tm.get_color('warning')}]Container logs are not accessible yet[/{_tm.get_color('warning')}]\n"
                    )
                    console.print(
                        "Common reasons:\n"
                        "  • SSH is not ready yet (container logs require SSH).\n"
                        "  • The container may have already started and exited; logs are retained and will be available once SSH is ready."
                    )
                    console.print(
                        "\nNext steps:\n"
                        f"  • View startup activity now: [accent]flow logs {task_ref} --source startup -n {tail}[/accent]\n"
                        f"  • Follow and auto-switch when ready: [accent]flow logs {task_ref} -f[/accent]\n"
                        f"  • Wait for SSH then retry: [accent]flow ssh {task_ref}[/accent] (auto-waits)"
                    )
                else:
                    console.print(
                        f"[{_tm.get_color('warning')}]Instance is taking longer than expected to start[/{_tm.get_color('warning')}]\n"
                    )
                    console.print(
                        "The instance needs a few minutes to be ready for SSH connections."
                    )
                    console.print(
                        f"\nTry: [accent]flow ssh {task_ref}[/accent] (automatically waits for readiness)"
                    )
                return

            # Detect what source was actually used based on log content and source param
            logs_lower = logs.lower() if logs else ""
            actual_source = None

            if logs and "container not started" in logs_lower:
                actual_source = "/var/log/foundry/startup_script.log (container not ready yet)"
            elif logs and (logs.startswith("[Startup]") or logs.startswith("[SSH-")):
                actual_source = "/var/log/foundry/ (host system logs)"
            elif source == "startup":
                actual_source = "/var/log/foundry/startup_script.log"
            elif source == "cloud-init":
                actual_source = "/var/log/cloud-init-output.log"
            elif source in ("host", "both", "all"):
                actual_source = {
                    "host": "/var/log/foundry/ (SSH & startup logs)",
                    "both": "docker logs <container> (combined)",
                    "all": "docker logs <container> (combined)",
                }.get(source, source)
            elif source == "auto" and logs and "[Startup]" not in logs:
                actual_source = f"docker logs <container> ({selected_stream})"

            # Check if logs contain only placeholder messages (treat as empty)
            logs_stripped = logs.strip() if logs else ""
            is_placeholder = any(
                placeholder in logs_stripped
                for placeholder in [
                    "Container not started. Showing startup logs snapshot...",
                    "--- End of startup snapshot.",
                    "Startup logs are empty (instance may still be starting).",
                    "Cloud-init logs are empty (instance may still be starting).",
                    "Waiting for startup logs...",
                    "Waiting for cloud-init logs...",
                ]
            )

            # Display logs (outside of progress context)
            if logs and logs.strip() and not is_placeholder:
                # Show source indicator before logs (skip for placeholders, we'll show better message)
                if actual_source and not output_json:
                    console.print(f"[dim]Showing {actual_source}[/dim]")

                # Apply filtering
                lines = self._filter_logs(logs, grep, self._parse_since(since) if since else None)

                # Handle multi-instance node display and prefixing
                if is_multi_instance and not no_prefix:
                    display_node = node if node is not None else 0
                    node_name = self._get_node_display_name(task, display_node, full_prefix)

                    # Show which node we're viewing if not explicitly specified
                    if node is None:
                        console.print(
                            f"[dim]Showing logs from {node_name} (use --node to select a different node)[/dim]"
                        )

                    # Add node prefix to lines if node was explicitly specified
                    if node is not None:
                        prefix = f"[{node_name}] "
                        lines = [
                            prefix + line if not line.startswith("[") else line for line in lines
                        ]

                # Join and print
                output = "".join(lines)
                if output.strip():
                    console.print(output, markup=False, highlight=False, end="")
                else:
                    console.print("[dim]No logs match the specified filters[/dim]")
            else:
                # Provide specific message based on source
                if is_placeholder:
                    # Show the placeholder message if it's informative
                    if logs_stripped and "Container not started" in logs_stripped:
                        console.print(
                            "[dim]Container not ready, showing logs from /var/log/foundry/startup_script.log...[/dim]\n"
                        )
                        console.print("[dim](empty file)[/dim]\n")
                    else:
                        console.print(f"[dim]Showing {actual_source or 'logs'}[/dim]\n")
                        console.print("[dim](empty file)[/dim]\n")
                elif actual_source:
                    console.print(f"[dim]{actual_source} is empty[/dim]\n")
                else:
                    console.print(f"[dim]No logs available for {task_display}[/dim]\n")

            # Show available log sources panel at the end for non-follow mode
            if not output_json:
                task_ref = task.name or task.task_id
                log_sources = [
                    f"Container logs (auto-selected): [accent]flow logs {task_ref}[/accent]",
                    f"Startup script: [accent]flow logs {task_ref} --source startup[/accent]",
                    f"Cloud-init output: [accent]flow logs {task_ref} --source cloud-init[/accent]",
                    f"Host system logs: [accent]flow logs {task_ref} --source host[/accent]",
                    f"Follow logs live: [accent]flow logs {task_ref} -f[/accent]",
                ]
                render_next_steps_panel(
                    console,
                    log_sources,
                    title="Available log sources",
                    max_items=5,
                )

            if timeline:
                if fetch_idx is not None:
                    timeline.complete_step()
                timeline.finish()

        # Show next actions based on task status
        task_ref = task.name or task.task_id
        if task.status == TaskStatus.RUNNING:
            self.show_next_actions(
                [
                    f"SSH into instance: [accent]flow ssh {task_ref}[/accent]",
                    f"Check task status: [accent]flow status {task_ref}[/accent]",
                    f"Cancel task: [accent]flow cancel {task_ref}[/accent]",
                ]
            )
        elif task.status == TaskStatus.COMPLETED:
            self.show_next_actions(
                [
                    "Submit a new task: [accent]flow submit <config.yaml>[/accent]",
                    "View all tasks: [accent]flow status[/accent]",
                ]
            )
        elif task.status == TaskStatus.FAILED:
            self.show_next_actions(
                [
                    f"View error details: [accent]flow logs {task_ref} --stderr[/accent]",
                    f"Check task details: [accent]flow status {task_ref}[/accent]",
                    "Retry with different parameters: [accent]flow submit <config.yaml>[/accent]",
                ]
            )
        elif task.status == TaskStatus.PENDING:
            self.show_next_actions(
                [
                    f"Check task status: [accent]flow status {task_ref}[/accent]",
                    f"Cancel if needed: [accent]flow cancel {task_ref}[/accent]",
                    "View resource availability: [accent]flow status --all[/accent]",
                ]
            )

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
        article = labels.article

        @click.command(name=self.name)
        @click.argument(
            "task_identifier",
            required=False,
            shell_complete=complete_task_ids,
            metavar=f"[{identifier_name}]",
        )
        @click.option("--follow", "-f", is_flag=True, help="Follow log output")
        @click.option("--tail", "-n", type=int, default=100, help="Number of lines to show")
        @click.option("--stderr", is_flag=True, help="Show stderr instead of stdout")
        @click.option(
            "--source",
            type=click.Choice(
                ["auto", "container", "startup", "cloud-init", "host", "both", "all"],
                case_sensitive=False,
            ),
            default="auto",
            help=(
                "Log source: 'container' for task logs, 'startup' for startup script, "
                "'cloud-init' for raw cloud-init output, 'host' for system logs, "
                "'both/all' for combined container logs, or 'auto' to pick sensibly"
            ),
        )
        @click.option(
            "--stream",
            type=click.Choice(["stdout", "stderr", "combined"], case_sensitive=False),
            default=None,
            help="Which stream to show (overrides --stderr)",
        )
        @click.option("--node", type=int, help="Specific node (0-indexed) for multi-instance tasks")
        @click.option(
            "--since", help="Show logs since timestamp (e.g., '5m', '1h', '2024-01-15T10:00:00')"
        )
        @click.option("--grep", help="Filter lines matching pattern")
        @click.option(
            "--no-prefix", is_flag=True, help="Remove node prefix for single-node or piping"
        )
        @click.option(
            "--full-prefix",
            is_flag=True,
            help="Use full node prefix (e.g., [node-0] instead of [0])",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--verbose", "-v", is_flag=True, help="Show detailed examples and usage patterns"
        )
        # @demo_aware_command()
        @cli_error_guard(self)
        def logs(
            task_identifier: str | None,
            follow: bool,
            tail: int,
            stderr: bool,
            source: str,
            stream: str | None,
            node: int | None,
            since: str | None,
            grep: str | None,
            no_prefix: bool,
            full_prefix: bool,
            output_json: bool,
            verbose: bool,
        ):
            # Ensure local client variable is defined before any conditional assignment
            client = None

            if verbose:
                console.print("\n[bold]Advanced Log Viewing:[/bold]\n")
                console.print("Real-time streaming:")
                console.print(f"  flow logs {labels.singular} -f                # Follow stdout")
                console.print(f"  flow logs {labels.singular} -f --stderr        # Follow stderr")
                console.print(
                    f"  flow logs {labels.singular} -f --grep ERROR   # Stream only errors\n"
                )

                console.print("Time-based filtering:")
                console.print(f"  flow logs {labels.singular} --since 5m        # Last 5 minutes")
                console.print(f"  flow logs {labels.singular} --since 1h        # Last hour")
                console.print(
                    f"  flow logs {labels.singular} --since 2024-01-15T10:00:00  # Since timestamp\n"
                )

                console.print(f"Multi-node {labels.empty_plural}:")
                console.print("  flow logs distributed --node 0    # Head node logs")
                console.print("  flow logs distributed --node 1    # Worker node logs")
                console.print(
                    f"  flow logs {labels.singular} --no-prefix        # Remove [0] prefix for piping\n"
                )

                console.print("Advanced filtering:")
                console.print(
                    f"  flow logs {labels.singular} --grep 'loss.*0\\.[0-9]+'     # Regex patterns"
                )
                console.print(
                    f"  flow logs {labels.singular} -n 1000 | grep -v DEBUG      # Unix pipelines"
                )
                console.print(
                    f"  flow logs {labels.singular} --json > logs.json            # Export for analysis\n"
                )

                console.print("Common patterns:")
                console.print(
                    f"  • Training progress: flow logs {labels.singular} -f --grep 'epoch\\|loss'"
                )
                console.print(
                    f"  • Error debugging: flow logs {labels.singular} --stderr --grep ERROR"
                )
                console.print(
                    f"  • Save full logs: flow logs {labels.singular} -n 999999 > {labels.singular}.log"
                )
                console.print(
                    f"  • Monitor GPU: flow ssh {labels.singular} -- tail -f /var/log/gpud.log\n"
                )
                return

            # JSON mode requires a concrete task identifier to avoid interactive/UI output
            if output_json and not task_identifier:
                from flow.cli.utils.json_output import error_json, print_json

                print_json(
                    error_json(
                        f"--json requires {article} {labels.singular} identifier (id or name)",
                        hint=f"Usage: flow logs <{labels.singular}> --json",
                    )
                )
                return

            # Selection grammar: attempt if looks like indices (works after 'flow status')
            if task_identifier:
                from flow.cli.utils.selection_helpers import parse_selection_to_task_ids

                ids, err = parse_selection_to_task_ids(task_identifier)
                if err:
                    from flow.cli.utils.theme_manager import theme_manager as _tm

                    console.print(
                        f"[{_tm.get_color('error')}]{{err}}[/{_tm.get_color('error')}]".replace(
                            "{err}", str(err)
                        )
                    )
                    return
                if ids is not None:
                    if len(ids) != 1:
                        console.print(
                            f"[{_tm.get_color('error')}]Selection must resolve to exactly one task for logs[/{_tm.get_color('error')}]"
                        )
                        return
                    task_identifier = ids[0]

            # When a direct identifier is provided, avoid the selector mixin path to allow tests
            # to patch Flow and resolver without requiring full auth config.
            if task_identifier:
                # Immediate user feedback before client init/resolution to avoid perceived hang
                if not output_json:
                    try:
                        from flow.cli.utils.task_index_cache import TaskIndexCache as _Cache

                        cache = _Cache()
                        tid = task_identifier
                        if isinstance(tid, str) and tid.startswith(":"):
                            resolved, _ = cache.resolve_index(tid)
                            if resolved:
                                tid = resolved
                        cached = cache.get_cached_task(tid) or {}
                        name = cached.get("name") or task_identifier

                        # Only show task ID in parens if it's different from the name
                        task_display = name
                        if str(tid) != str(name) and not str(name).startswith(str(tid)[:8]):
                            short = (
                                (str(tid)[:12] + "…")
                                if isinstance(tid, str) and len(tid) > 12
                                else str(tid)
                            )
                            task_display = f"{name} ({short})"

                        # Build source description with file paths
                        src_desc = {
                            "auto": "logs",  # Will show actual source later when we know it
                            "container": "docker logs <container>",
                            "startup": "/var/log/foundry/startup_script.log",
                            "cloud-init": "/var/log/cloud-init-output.log",
                            "host": "/var/log/foundry/ (SSH & startup)",
                            "both": "docker logs <container> (combined)",
                            "all": "docker logs <container> (combined)",
                        }.get(source, source)

                        stream_desc = stream or ("stderr" if stderr else "stdout")

                        # For auto mode, don't show stream - we might be fetching files, not streams
                        if source == "auto":
                            console.print(f"[dim]Fetching logs for {task_display}[/dim]")
                        elif source in ("container", "both", "all"):
                            # Only show stream for container sources where stdout/stderr applies
                            console.print(
                                f"[dim]Fetching {src_desc} ({stream_desc}) for {task_display}[/dim]"
                            )
                        else:
                            # File-based sources (startup, cloud-init, host) - no stream label
                            console.print(f"[dim]Fetching {src_desc} for {task_display}[/dim]")
                        host = cached.get("ssh_host")
                        port = cached.get("ssh_port") or 22
                        if host:
                            console.print(f"[dim]Connecting via SSH to {host}:{port}[/dim]")
                        else:
                            console.print("[dim]Looking up instance SSH endpoint…[/dim]")
                    except Exception:  # noqa: BLE001
                        pass
                # For snapshot mode, hint what we are about to fetch right away
                if not follow and not output_json:
                    try:
                        console.print(f"[dim]Fetching last {tail} lines…[/dim]")
                    except Exception:  # noqa: BLE001
                        pass
                # Disallow --json with --follow for now; a future event stream will support it
                if output_json and follow:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(
                        error_json(
                            "--json is not supported with --follow",
                            hint=f"Use: flow logs <{labels.singular}> --json (without --follow) or stream without --json",
                        )
                    )
                    return
                # In tests, prefer Flow symbol so patches take effect
                if client is None:
                    client = sdk_factory.create_client(auto_init=True)
                # Import resolver from canonical path to ensure tests can patch it reliably
                from flow.cli.utils.task_resolver import (
                    resolve_task_identifier as _resolve_task_identifier,
                )

                task, error = _resolve_task_identifier(client, task_identifier)
                if error:
                    console.print(
                        f"[{_tm.get_color('error')}]{{error}}[/{_tm.get_color('error')}]".replace(
                            "{error}", str(error)
                        )
                    )
                    return
                self.execute_on_task(
                    task,
                    client,
                    follow=follow,
                    tail=tail,
                    stderr=stderr,
                    source=source,
                    stream=stream,
                    node=node,
                    since=since,
                    grep=grep,
                    no_prefix=no_prefix,
                    full_prefix=full_prefix,
                    output_json=output_json,
                )
            else:
                if client is None:
                    client = sdk_factory.create_client(auto_init=True)
                self.execute_with_selection(
                    task_identifier,
                    flow_factory=lambda: client,
                    follow=follow,
                    tail=tail,
                    stderr=stderr,
                    source=source,
                    stream=stream,
                    node=node,
                    since=since,
                    grep=grep,
                    no_prefix=no_prefix,
                    full_prefix=full_prefix,
                    output_json=output_json,
                )

        # Set dynamic help text based on nomenclature
        help_text = f"""Get logs from a running {labels.singular}.

{identifier_name}: {entity_label} ID or name (optional - interactive selector if omitted)

\b
Examples:
    flow logs                    # Interactive selector
    flow logs my-training        # View recent logs
    flow logs {labels.singular}-abc123 -f     # Stream logs in real-time
    flow logs {labels.singular} --stderr -n 50  # Last 50 stderr lines

Use 'flow logs --verbose' for advanced filtering and multi-node examples."""

        logs.help = help_text
        logs.__doc__ = help_text

        return logs

    def _execute(
        self,
        task_identifier: str | None,
        follow: bool,
        tail: int,
        stderr: bool,
        node: int | None,
        since: str | None,
        grep: str | None,
        no_prefix: bool,
        full_prefix: bool,
        output_json: bool,
        flow_client=None,
    ) -> None:
        """Execute log retrieval or streaming."""
        self.execute_with_selection(
            task_identifier,
            flow_factory=lambda: (flow_client or sdk_factory.create_client(auto_init=True)),
            follow=follow,
            tail=tail,
            stderr=stderr,
            node=node,
            since=since,
            grep=grep,
            no_prefix=no_prefix,
            full_prefix=full_prefix,
            output_json=output_json,
        )


# Export command instance
command = LogsCommand()
