"""Cancel command - terminate running GPU tasks.

Allows terminating running or pending tasks with optional confirmation.

Examples:
    # Cancel a specific task
    $ flow cancel my-training-job

    # Cancel last task from status (using index)
    $ flow cancel 1

    # Cancel all dev tasks without confirmation (wildcard)
    $ flow cancel --name-pattern "dev-*" --yes

Command Usage:
    flow cancel TASK_ID_OR_NAME [OPTIONS]

The command will:
- Verify the task exists and is cancellable
- Prompt for confirmation (unless --yes is used)
- Send cancellation request to the provider
- Display cancellation status

Note:
    Only tasks in 'pending' or 'running' state can be cancelled.
    Completed or failed tasks cannot be cancelled.
"""

from __future__ import annotations

import fnmatch
import os
import re

import click

import flow.sdk.factory as sdk_factory
from flow.cli.commands.base import BaseCommand, console
from flow.cli.commands.utils import maybe_show_auto_status
from flow.cli.ui.formatters import GPUFormatter, TaskFormatter
from flow.cli.ui.presentation.nomenclature import (
    get_delete_verbs,
    get_entity_labels,
    is_compute_mode,
)
from flow.cli.ui.runtime.owner_resolver import OwnerResolver
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from flow.errors import AuthenticationError

# Back-compat: expose Flow for tests that patch flow.cli.commands.cancel.Flow
from flow.sdk.client import Flow
from flow.sdk.models import Task, TaskStatus


class CancelCommand(BaseCommand, TaskOperationCommand):
    """Cancel a running task."""

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "cancel"

    @property
    def help(self) -> str:
        return """Cancel GPU tasks - pattern matching uses wildcards by default

        Example: flow cancel -n 'dev-*'"""

    # Progress/selection behavior: fetch under spinner; stop spinner before confirmation
    @property
    def prefer_fetch_before_selection(self) -> bool:  # type: ignore[override]
        return True

    @property
    def stop_spinner_before_confirmation(self) -> bool:  # type: ignore[override]
        return True

    # Spinner label for the fetch phase
    @property
    def _fetch_spinner_label(self) -> str:  # type: ignore[override]
        return f"Looking up {get_entity_labels().empty_plural} to cancel"

    def get_command(self) -> click.Command:
        # Import completion function
        # from flow.cli.utils.mode import demo_aware_command
        from flow.cli.ui.runtime.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
        @click.option("--all", is_flag=True, help="Cancel all running tasks")
        @click.option(
            "--name-pattern",
            "-n",
            help="Cancel tasks matching wildcard pattern (e.g., 'dev-*', '*-gpu-8x*', 'train-v?'). Use --regex for regex.",
        )
        @click.option("--regex", is_flag=True, help="Treat pattern as regex instead of wildcard")
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed examples and patterns")
        @click.option(
            "--interactive/--no-interactive",
            default=None,
            help="Force interactive selector on/off regardless of terminal autodetect",
        )
        # @demo_aware_command()
        @cli_error_guard(self)
        def cancel(
            task_identifier: str,  # Optional at runtime, Click passes ''/None if omitted
            yes: bool,
            all: bool,
            name_pattern: str,  # Optional at runtime
            regex: bool,
            verbose: bool,
            interactive: bool | None,
        ):
            """Cancel a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \b
            Examples:
                flow cancel                       # Interactive task selector
                flow cancel my-training           # Cancel by name
                flow cancel task-abc123           # Cancel by ID
                flow cancel -n 'dev-*' --yes      # Cancel tasks starting with 'dev-'
                flow cancel --all --yes           # Cancel all running tasks

            Pattern matching uses wildcards by default:
                flow cancel -n 'dev-*'           # Matches: dev-1, dev-test, dev-experiment
                flow cancel -n '*-gpu-8x*'       # Matches tasks mentioning 8x GPU
                flow cancel -n 'train-v?'        # Single character wildcard
            Use --regex for advanced regex patterns:
                flow cancel -n '^gpu-test-' --regex     # Start anchor
                flow cancel -n '.*-v[0-9]+' --regex     # Version pattern

            Use 'flow cancel --verbose' for advanced pattern matching examples.
            """
            if verbose:
                # Detect if we're being called via instance delete alias
                cmd = "flow instance delete" if is_compute_mode() else "flow cancel"

                console.print("\n[bold]Pattern Matching Examples[/bold]\n")

                console.print("[bold]Wildcard patterns (default):[/bold]")
                console.print(f"  {cmd} -n 'dev-*'                # Cancel all starting with dev-")
                console.print(f"  {cmd} -n '*-gpu-8x*'            # Match GPU type")
                console.print(f"  {cmd} -n 'train-v?'             # Single character wildcard\n")

                console.print("[bold]Regex patterns (with --regex flag):[/bold]")
                console.print(
                    f"  {cmd} -n '^dev-' --regex        # Matches tasks starting with 'dev-'"
                )
                console.print(
                    f"  {cmd} -n 'dev-$' --regex        # Matches tasks ending with 'dev-'"
                )
                console.print(
                    f"  {cmd} -n '.*-v[0-9]+' --regex  # Version pattern (e.g., app-v1, test-v23)"
                )
                console.print(f"  {cmd} -n '^test-.*-2024' --regex   # Complex matching")
                console.print(
                    f"  {cmd} -n 'gpu-(test|prod)' --regex # Match gpu-test OR gpu-prod\n"
                )

                console.print(
                    "[warning]Note: When using wildcards (default), quote them to prevent shell expansion:[/warning]"
                )
                console.print(f"  [success]✓ CORRECT:[/success]  {cmd} -n 'gpu-test-*'")
                console.print(
                    f"  [error]✗ WRONG:[/error]    {cmd} -n gpu-test-*   # Shell expands *\n"
                )

                console.print("[bold]Batch operations:[/bold]")
                console.print(
                    f"  {cmd} --all                       # Cancel all (with confirmation)"
                )
                console.print(f"  {cmd} --all --yes                 # Force cancel all\n")

                console.print("[bold]Common workflows:[/bold]")
                console.print(f"  • Cancel all dev tasks: {cmd} -n 'dev-*' --yes")
                console.print(f"  • Clean up test tasks: {cmd} -n '*test*' --yes")
                console.print(f"  • Cancel specific prefix: {cmd} -n 'training-v2-*' --yes")
                console.print(f"  • Cancel by suffix: {cmd} -n '*-temp' --yes\n")
                return

            # Interactive toggle via flag overrides autodetect
            if interactive is True:
                os.environ["FLOW_FORCE_INTERACTIVE"] = "true"
            elif interactive is False:
                os.environ["FLOW_NONINTERACTIVE"] = "1"

            # Selection grammar: allow batch cancel via indices (works after 'flow status')
            if task_identifier:
                from flow.cli.utils.selection_helpers import parse_selection_to_task_ids

                ids, err = parse_selection_to_task_ids(task_identifier)
                if err:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_err

                    error_color = _tm_err.get_color("error")
                    console.print(f"[{error_color}]{err}[/{error_color}]")
                    return
                if ids is not None:
                    # Prepare client first for task name resolution
                    client = sdk_factory.create_client(auto_init=True)

                    # Echo expansion with task names
                    display_names: list[str] = []
                    for tid in ids:
                        try:
                            task = client.get_task(tid)
                            name = task.name or (tid[:12] + "…" if len(tid) > 12 else tid)
                            display_names.append(name)
                        except Exception:  # noqa: BLE001
                            # Fallback to task ID if get_task fails
                            display_names.append(tid[:12] + "…" if len(tid) > 12 else tid)
                    console.print(
                        f"[dim]Selection {task_identifier} → {', '.join(display_names)}[/dim]"
                    )

                    # Use appropriate terminology based on context
                    labels = get_entity_labels()
                    verbs = get_delete_verbs()
                    entity = labels.empty_plural
                    action = verbs.base
                    abort_msg = f"{verbs.noun.capitalize()} aborted"

                    if len(ids) == 1:
                        # Single-id path: fetch full task to show detailed confirmation with owner
                        tid = ids[0]
                        try:
                            task = client.get_task(tid)
                            # Show detailed confirmation (unless --yes), which includes owner info
                            self.execute_on_task(task, client, yes=yes, use_aep=True)
                        except Exception as e:  # noqa: BLE001
                            from rich.markup import escape

                            from flow.cli.utils.theme_manager import theme_manager as _tm_fail

                            error_color = _tm_fail.get_color("error")
                            action_verb_past = verbs.base_lower
                            console.print(
                                f"[{error_color}]✗[/{error_color}] Failed to {action_verb_past} {tid[:12]}…: {escape(str(e))}"
                            )
                        return

                    # Multiple IDs: show batch confirmation
                    if not yes and not click.confirm(f"{action} {len(ids)} {entity}?"):
                        console.print(f"[dim]{abort_msg}[/dim]")
                        return
                    else:
                        # Batch UX: quick feedback and per-item progress via StepTimeline
                        plural = get_entity_labels().empty_plural

                        # Use appropriate action verb
                        action_verb = verbs.present

                        console.print(f"[dim]{action_verb} {len(ids)} {plural}…[/dim]")
                        for tid in ids:
                            try:
                                # Fast path: try to get task name from cache, fallback to task ID
                                disp_name = None
                                try:
                                    task = client.get_task(tid)
                                    disp_name = task.name or (
                                        tid[:12] + "…" if len(tid) > 12 else tid
                                    )
                                except Exception:  # noqa: BLE001
                                    # Fallback to task ID if get_task fails
                                    disp_name = tid[:12] + "…" if len(tid) > 12 else tid

                                self.execute_on_task_id(
                                    task_id=tid,
                                    client=client,
                                    display_name=disp_name,
                                )
                            except Exception as e:  # noqa: BLE001
                                from rich.markup import escape

                                from flow.cli.utils.theme_manager import (
                                    theme_manager as _tm_fail,
                                )

                                error_color = _tm_fail.get_color("error")
                                console.print(
                                    f"[{error_color}]✗[/{error_color}] Failed to cancel {tid[:12]}…: {escape(str(e))}"
                                )
                    # Show next steps once after batch
                    self.show_next_actions(
                        [
                            "View all tasks: [accent]flow status[/accent]",
                            "Submit a new task: [accent]flow submit <config.yaml>[/accent]",
                        ]
                    )
                    return

            # For non-batch flows, create client if needed
            try:
                client = sdk_factory.create_client(auto_init=True)
            except AuthenticationError:
                self.handle_auth_error()
                return

            self._execute(task_identifier, yes, all, name_pattern, regex, flow_client=client)

        return cancel

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Only show cancellable tasks."""
        return TaskFilter.cancellable

    def get_selection_title(self) -> str:
        labels = get_entity_labels()
        return f"Select {labels.article} {labels.singular} to cancel"

    def get_no_tasks_message(self) -> str:
        plural = get_entity_labels().empty_plural
        return f"No running {plural} to cancel"

    # Command execution
    def execute_on_task(self, task: Task, client, **kwargs) -> None:
        """Execute cancellation on the selected task."""
        yes = kwargs.get("yes", False)
        suppress_next_steps = kwargs.get("suppress_next_steps", False)
        use_aep = kwargs.get("use_aep", False)

        # Double-check task is still cancellable
        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            status_str = str(task.status).replace("TaskStatus.", "").lower()
            console.print(
                f"[warning]Task '{task.name or task.task_id}' is already {status_str}[/warning]"
            )
            return

        # Show confirmation with task details
        if not yes:
            self._show_cancel_confirmation(task)

            # Use appropriate terminology based on how command was invoked
            verbs = get_delete_verbs()
            action = verbs.noun
            abort_msg = f"{verbs.noun.capitalize()} aborted"

            # Simple, focused confirmation prompt
            if not click.confirm(f"\nProceed with {action}?", default=False):
                console.print(f"[dim]{abort_msg}[/dim]")
                return

        # Determine terminology based on instance mode
        verbs = get_delete_verbs()
        action_verb_present = verbs.present
        action_verb_past = verbs.past

        if use_aep:
            # Transient spinner-based UX for single cancellations
            try:
                from flow.cli.ui.presentation.animated_progress import (
                    AnimatedEllipsisProgress as _AEP,
                )

                label = f"{action_verb_present} {task.name or task.task_id}"
                with _AEP(console, label, transient=True, start_immediately=True):
                    client.cancel(task.task_id)
            except Exception:  # noqa: BLE001
                # Fallback without spinner
                client.cancel(task.task_id)
            # Reflect cancellation in local task object for immediate UX feedback
            try:
                task.status = TaskStatus.CANCELLED
            except Exception:  # noqa: BLE001
                pass
        else:
            # StepTimeline progress
            from flow.cli.utils.step_progress import StepTimeline

            timeline = StepTimeline(console, title="flow cancel", title_animation="auto")
            timeline.start()
            step_idx = timeline.add_step(
                f"{action_verb_present} {task.name or task.task_id}", show_bar=False
            )
            timeline.start_step(step_idx)
            try:
                client.cancel(task.task_id)
                # Reflect cancellation in the local task object for immediate UX/tests
                try:
                    task.status = TaskStatus.CANCELLED
                except Exception:  # noqa: BLE001
                    pass
                timeline.complete_step()
            except Exception as e:
                timeline.fail_step(str(e))
                timeline.finish()
                raise
            finally:
                try:
                    timeline.finish()
                except Exception:  # noqa: BLE001
                    pass

        # Invalidate task cache after successful cancellation
        from flow.adapters.http.client import HttpClientPool

        for http_client in HttpClientPool._clients.values():
            if hasattr(http_client, "invalidate_task_cache"):
                http_client.invalidate_task_cache()

        # Success message
        from flow.cli.utils.theme_manager import theme_manager as _tm

        success_color = _tm.get_color("success")
        console.print(
            f"\n[{success_color}]✓[/{success_color}] {action_verb_past} [bold]{task.name or task.task_id}[/bold]"
        )

        # Show next actions (suppress in batch mode)
        if not suppress_next_steps:
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow submit <config.yaml>[/accent]",
                ]
            )

        # Show a compact status snapshot after state change
        try:
            maybe_show_auto_status(
                focus=(task.name or task.task_id), reason="After cancellation", show_all=False
            )
        except Exception:  # noqa: BLE001
            pass

    def execute_on_task_id(
        self,
        task_id: str,
        client,
        *,
        display_name: str | None = None,
        show_next_steps: bool = False,
        use_aep_spinner: bool = True,
    ) -> None:
        """Cancel by task id without pre-fetching Task details.

        Optimized for batch flows: shows immediate per-item progress and avoids
        blocking `get_task()` network calls before feedback.
        """
        # Build a friendly label: prefer provided name, then short id.
        label: str
        if display_name:
            label = display_name
        else:
            label = task_id[:12] + "…" if len(task_id) > 12 else task_id

        # Determine terminology based on instance mode
        verbs = get_delete_verbs()
        action_verb_present = verbs.present
        action_verb_past = verbs.past

        if use_aep_spinner:
            try:
                from flow.cli.ui.presentation.animated_progress import (
                    AnimatedEllipsisProgress as _AEP,
                )

                with _AEP(
                    console,
                    f"{action_verb_present} {label}",
                    transient=True,
                    start_immediately=True,
                ):
                    client.cancel(task_id)
            except Exception:  # noqa: BLE001
                # Fallback to timeline if AEP not available
                use_aep_spinner = False

        if not use_aep_spinner:
            from flow.cli.utils.step_progress import StepTimeline

            timeline = StepTimeline(console, title="flow cancel", title_animation="auto")
            timeline.start()
            step_idx = timeline.add_step(f"{action_verb_present} {label}", show_bar=False)
            timeline.start_step(step_idx)
            try:
                client.cancel(task_id)
                timeline.complete_step()
            except Exception as e:
                timeline.fail_step(str(e))
                timeline.finish()
                raise
            finally:
                try:
                    timeline.finish()
                except Exception:  # noqa: BLE001
                    pass

        # Invalidate task cache after successful cancellation
        from flow.adapters.http.client import HttpClientPool

        for http_client in HttpClientPool._clients.values():
            if hasattr(http_client, "invalidate_task_cache"):
                http_client.invalidate_task_cache()

        # Success message (compact; no next-steps in batch mode)
        from flow.cli.utils.theme_manager import theme_manager as _tm

        success_color = _tm.get_color("success")
        console.print(
            f"\n[{success_color}]✓[/{success_color}] {action_verb_past} [bold]{label}[/bold]"
        )

        if show_next_steps:
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow submit <config.yaml>[/accent]",
                ]
            )

    def _show_cancel_confirmation(self, task: Task) -> None:
        """Show a confirmation panel with task details."""
        from datetime import datetime, timezone

        from rich.panel import Panel
        from rich.table import Table

        from flow.cli.ui.presentation.time_formatter import TimeFormatter

        time_fmt = TimeFormatter()

        # Create a clean table for task details
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()

        # Task name
        table.add_row("Task", task.name or "Unnamed task")

        # GPU type - show total GPUs if multiple instances
        gpu_display = GPUFormatter.format_ultra_compact(
            task.instance_type, getattr(task, "num_instances", 1)
        )
        table.add_row("GPU", gpu_display)

        # Status - use get_display_status for consistency with flow status
        try:
            from flow.cli.ui.formatters import TaskFormatter as _TF

            # Get enriched display status (e.g., "starting" vs "running")
            display_status = _TF.get_display_status(task)
            status_display = _TF.format_status_with_color(display_status)
        except Exception:  # noqa: BLE001
            # Fallback to raw status value
            status_display = str(getattr(task.status, "value", task.status))
        table.add_row("Status", status_display)

        # Duration and cost
        duration = time_fmt.calculate_duration(task)
        table.add_row("Duration", duration)

        # Calculate approximate cost if available
        if (
            hasattr(task, "price_per_hour")
            and task.price_per_hour
            and task.status == TaskStatus.RUNNING
        ) and task.started_at:
            start = task.started_at
            if hasattr(start, "tzinfo") and start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            hours_run = (now - start).total_seconds() / 3600
            cost_so_far = hours_run * task.price_per_hour

            table.add_row("Cost so far", f"${cost_so_far:.2f}")
            table.add_row("Hourly rate", f"${task.price_per_hour:.2f}/hr")

        # Show owner information, especially if it's not yours
        if task.created_by:
            resolver = OwnerResolver()
            me = resolver.get_me()
            owner_map = resolver.get_teammates_map()

            # Use the existing format_owner method for consistent owner display
            owner_display = OwnerResolver.format_owner(task.created_by, me, owner_map)

            # Display owner information
            table.add_row("Owner", owner_display)

        # Create panel with calmer themed colors
        from flow.cli.utils.theme_manager import theme_manager as _tm

        warning_color = _tm.get_color("warning")
        border_color = _tm.get_color("table.border")
        noun = get_entity_labels().header

        # Use appropriate action verb based on mode
        verbs = get_delete_verbs()
        action_verb = verbs.base

        panel = Panel(
            table,
            title=f"[bold {warning_color}]⚠  {action_verb} {noun}[/bold {warning_color}]",
            title_align="center",
            border_style=border_color,
            padding=(1, 2),
        )

        console.print()
        console.print(panel)

    def _execute(
        self,
        task_identifier: str,
        yes: bool,
        all: bool,
        name_pattern: str,
        regex: bool,
        flow_client=None,
    ) -> None:
        """Execute the cancel command."""
        if all:
            self._execute_cancel_all(yes, flow_client=flow_client)
        elif name_pattern:
            self._execute_cancel_pattern(name_pattern, yes, regex, flow_client=flow_client)
        else:
            # Prefer direct path to allow tests to patch Flow and resolver cleanly
            if task_identifier:
                try:
                    client = flow_client or sdk_factory.create_client(auto_init=True)
                    task = self.resolve_task(task_identifier, client)
                    # Direct identifier path: show AEP for single cancellation UX
                    self.execute_on_task(task, client, yes=yes, use_aep=True)
                except AuthenticationError:
                    self.handle_auth_error()
                except Exception as e:  # noqa: BLE001
                    self.handle_error(str(e))
            else:
                # Fallback to interactive selection via mixin
                self.execute_with_selection(
                    task_identifier,
                    yes=yes,
                    flow_factory=lambda: (flow_client or sdk_factory.create_client(auto_init=True)),
                )

    # Override resolve_task to import resolver from its canonical module so tests can patch it there
    def resolve_task(self, task_identifier: str | None, client: Flow, allow_multiple: bool = False):  # type: ignore[override]
        if task_identifier:
            from flow.cli.utils.task_resolver import (
                resolve_task_identifier as resolver,  # type: ignore
            )

            task, error = resolver(client, task_identifier)
            if error:
                from flow.cli.commands.base import console as _console

                _console.print(f"[error]✗ Error:[/error] {error}")
                raise SystemExit(1)
            return task
        # Fallback to base mixin behavior for interactive selection
        return super().resolve_task(task_identifier, client, allow_multiple)

    def _show_batch_cancellation_table(self, tasks: list[Task], title_msg: str) -> None:
        """Show a table of tasks to be cancelled with owner information.

        Args:
            tasks: List of tasks to show
            title_msg: Title message to display above the table
        """
        console.print(f"\n[bold]{title_msg}[/bold]\n")
        from rich.table import Table

        from flow.cli.ui.presentation.nomenclature import get_entity_labels
        from flow.cli.utils.theme_manager import theme_manager as _tm

        labels = get_entity_labels()
        table = Table(show_header=True, box=None)
        table.add_column(f"{labels.header} Name", style=_tm.get_color("accent"))
        table.add_column(f"{labels.header} ID", style="dim")
        table.add_column("Status")
        table.add_column("GPU Type")
        table.add_column("Owner")

        # Get owner info once for all tasks
        me = None
        owner_map = None
        from flow.cli.ui.runtime.owner_resolver import OwnerResolver

        resolver = OwnerResolver()
        me = resolver.get_me()
        owner_map = resolver.get_teammates_map()

        for task in tasks:
            from flow.cli.ui.formatters import GPUFormatter as _GPUF
            from flow.cli.ui.formatters import TaskFormatter as _TF

            # Use get_display_status for consistency with flow status
            display_status = _TF.get_display_status(task)
            status_display = _TF.format_status_with_color(display_status)
            gpu_display = _GPUF.format_ultra_compact(
                task.instance_type, getattr(task, "num_instances", 1)
            )

            # Format owner display
            owner_display = "-"
            if task.created_by:
                owner_display = OwnerResolver.format_owner(task.created_by, me, owner_map)

            table.add_row(
                task.name or "Unnamed",
                task.task_id[:12] + "...",
                status_display,
                gpu_display,
                owner_display,
            )

        console.print(table)
        console.print()

    def _execute_cancel_all(self, yes: bool, *, flow_client=None) -> None:
        """Handle --all flag separately as it's a special case."""
        from flow.cli.utils.step_progress import StepTimeline

        try:
            timeline = StepTimeline(console, title="flow cancel", title_animation="auto")
            timeline.start()

            # Step 1: Discover cancellable tasks
            find_idx = timeline.add_step("Finding all cancellable tasks", show_bar=False)
            timeline.start_step(find_idx)
            client = flow_client or sdk_factory.create_client(auto_init=True)

            # Get cancellable tasks using TaskFetcher for consistent behavior
            from flow.cli.utils.task_fetcher import TaskFetcher

            fetcher = TaskFetcher(client)
            all_tasks = fetcher.fetch_all_tasks(limit=1000, prioritize_active=True)
            cancellable = TaskFilter.cancellable(all_tasks)
            timeline.complete_step()

            if not cancellable:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn

                warn = _tm_warn.get_color("warning")
                timeline.finish()
                console.print(f"[{warn}]No running tasks to cancel[/{warn}]")
                return

            # Show all cancellable tasks in a table with owner information
            timeline.finish()
            self._show_batch_cancellation_table(
                cancellable, f"Found {len(cancellable)} cancellable task(s):"
            )

            # Confirm: prompt user
            if not yes:
                if not click.confirm(f"Cancel all {len(cancellable)} running task(s)?"):
                    console.print("Cancelled")
                    return
                # Recreate a fresh timeline for the cancellation phase
                timeline = StepTimeline(console, title="flow cancel", title_animation="auto")
                timeline.start()

            # Immediate feedback post-confirmation for consistency
            plural = get_entity_labels().empty_plural
            console.print(f"[dim]Canceling {len(cancellable)} {plural}…[/dim]")

            # Step 2: Cancel tasks iteratively with a progress bar
            cancelled_count = 0
            failed_count = 0
            total = len(cancellable)
            plural = get_entity_labels().empty_plural
            cancel_idx = timeline.add_step(
                f"Canceling {total} {plural}", show_bar=True, estimated_seconds=None
            )
            timeline.start_step(cancel_idx)
            for i, task in enumerate(cancellable):
                task_name = task.name or task.task_id
                try:
                    client.cancel(task.task_id)
                    cancelled_count += 1
                except Exception as e:  # noqa: BLE001
                    from rich.markup import escape

                    from flow.cli.utils.theme_manager import theme_manager as _tm_fail2

                    err = _tm_fail2.get_color("error")
                    console.print(
                        f"[{err}]✗[/{err}] Failed to cancel {task_name}: {escape(str(e))}"
                    )
                    failed_count += 1
                finally:
                    # Update bar by item count
                    pct = (i + 1) / float(total)
                    timeline.update_active(percent=pct, message=f"{i + 1}/{total} – {task_name}")

            timeline.complete_step(note=f"{cancelled_count} succeeded, {failed_count} failed")
            timeline.finish()

            # Invalidate task cache after batch cancellation
            if cancelled_count > 0:
                try:
                    from flow.adapters.http.client import HttpClientPool

                    for http_client in HttpClientPool._clients.values():
                        if hasattr(http_client, "invalidate_task_cache"):
                            http_client.invalidate_task_cache()
                except Exception:  # noqa: BLE001
                    pass

            # Summary
            console.print()
            if cancelled_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm2

                success_color = _tm2.get_color("success")
                console.print(
                    f"[{success_color}]✓[/{success_color}] Canceled {cancelled_count} {plural}"
                )
            if failed_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm_fail3

                err = _tm_fail3.get_color("error")
                console.print(f"[{err}]✗[/{err}] Failed to cancel {failed_count} task(s)")

            # Next actions
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow submit <config.yaml>[/accent]",
                ]
            )

        except click.Abort:
            # Ensure live UI is cleaned up and exit gracefully on Ctrl+C
            try:
                timeline.finish()
            except Exception:  # noqa: BLE001
                pass
            console.print("[dim]Cancelled[/dim]")
            raise click.exceptions.Exit(130)
        except KeyboardInterrupt:
            try:
                timeline.finish()
            except Exception:  # noqa: BLE001
                pass
            console.print("[dim]Cancelled[/dim]")
            raise click.exceptions.Exit(130)
        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:  # noqa: BLE001
            self.handle_error(str(e))

    def _execute_cancel_pattern(
        self, pattern: str, yes: bool, use_regex: bool, *, flow_client=None
    ) -> None:
        """Cancel tasks matching a name pattern."""
        from flow.cli.utils.step_progress import StepTimeline

        try:
            timeline = StepTimeline(console, title="flow cancel", title_animation="auto")
            timeline.start()

            # Step 1: Discover candidates
            find_idx = timeline.add_step(f"Finding tasks matching: {pattern}", show_bar=False)
            timeline.start_step(find_idx)
            client = flow_client or sdk_factory.create_client(auto_init=True)

            # Get cancellable tasks
            from flow.cli.utils.task_fetcher import TaskFetcher

            fetcher = TaskFetcher(client)
            all_tasks = fetcher.fetch_all_tasks(limit=1000, prioritize_active=True)
            cancellable = TaskFilter.cancellable(all_tasks)
            timeline.complete_step()

            if not cancellable:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn2

                warn = _tm_warn2.get_color("warning")
                timeline.finish()
                console.print(f"[{warn}]No running tasks to cancel[/{warn}]")
                return

            # Filter by pattern
            matching_tasks = []
            for task in cancellable:
                if task.name:
                    if use_regex:
                        # Use regex matching when requested
                        try:
                            if re.search(pattern, task.name):
                                matching_tasks.append(task)
                        except re.error as e:
                            from rich.markup import escape

                            from flow.cli.utils.theme_manager import theme_manager as _tm_err2

                            err = _tm_err2.get_color("error")
                            console.print(f"[{err}]Invalid regex pattern: {escape(str(e))}[/{err}]")
                            return
                    else:
                        # Default to wildcard matching
                        if fnmatch.fnmatch(task.name, pattern):
                            matching_tasks.append(task)

            if not matching_tasks:
                from flow.cli.ui.presentation.nomenclature import get_entity_labels
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn3

                labels = get_entity_labels()
                warn = _tm_warn3.get_color("warning")
                console.print(
                    f"[{warn}]No running {labels.empty_plural} match pattern '{pattern}'[/{warn}]"
                )

                # Help users debug common issues
                if "*" in pattern or "?" in pattern:
                    try:
                        from flow.cli.ui.presentation.next_steps import (
                            render_next_steps_panel as _ns,
                        )

                        _ns(
                            console,
                            [
                                "Quote your pattern: [accent]flow cancel -n 'pattern*'[/accent]",
                                f"List {labels.empty_plural}: [accent]flow status --all[/accent]",
                            ],
                            title="Tips",
                        )
                    except Exception:  # noqa: BLE001
                        console.print(
                            "\n[dim]Tip: Quote your pattern: flow cancel -n 'pattern*'[/dim]"
                        )

                # Show what tasks ARE available
                sample_names = [t.name for t in cancellable[:5] if t.name]
                if sample_names:
                    console.print(
                        f"\n[dim]Available {labels.singular} names: {', '.join(sample_names)}"
                        f"{' ...' if len(cancellable) > 5 else ''}[/dim]"
                    )
                return

            # Show matching tasks with owner information
            self._show_batch_cancellation_table(
                matching_tasks,
                f"Found {len(matching_tasks)} {labels.singular}(s) matching pattern '[accent]{pattern}[/accent]':",
            )

            # Confirm: finish live timeline before prompting to avoid hidden input
            if not yes:
                try:
                    timeline.finish()
                except Exception:  # noqa: BLE001
                    pass
                if not click.confirm(
                    f"Cancel {len(matching_tasks)} matching {labels.singular}(s)?"
                ):
                    console.print("[dim]Cancellation aborted[/dim]")
                    return
                # Recreate a fresh timeline for the cancellation phase
                timeline = StepTimeline(console, title="flow cancel", title_animation="auto")
                timeline.start()

            # Immediate feedback post-confirmation for consistency
            console.print(f"[dim]Cancelling {len(matching_tasks)} {labels.singular}(s)…[/dim]")

            # Cancel each task with a progress bar
            cancelled_count = 0
            failed_count = 0
            total = len(matching_tasks)
            plural = get_entity_labels().empty_plural
            cancel_idx = timeline.add_step(
                f"Canceling {total} matching {plural}", show_bar=True, estimated_seconds=None
            )
            timeline.start_step(cancel_idx)
            for i, task in enumerate(matching_tasks):
                task_name = task.name or task.task_id
                try:
                    client.cancel(task.task_id)
                    cancelled_count += 1
                except Exception as e:  # noqa: BLE001
                    from rich.markup import escape

                    from flow.cli.utils.theme_manager import theme_manager as _tm_err3

                    err = _tm_err3.get_color("error")
                    console.print(
                        f"[{err}]✗[/{err}] Failed to cancel {task_name}: {escape(str(e))}"
                    )
                    failed_count += 1
                finally:
                    pct = (i + 1) / float(total)
                    timeline.update_active(percent=pct, message=f"{i + 1}/{total} – {task_name}")
            timeline.complete_step(note=f"{cancelled_count} succeeded, {failed_count} failed")
            timeline.finish()

            # Invalidate task cache after batch cancellation
            if cancelled_count > 0:
                try:
                    from flow.adapters.http.client import HttpClientPool

                    for http_client in HttpClientPool._clients.values():
                        if hasattr(http_client, "invalidate_task_cache"):
                            http_client.invalidate_task_cache()
                except Exception:  # noqa: BLE001
                    pass

            # Summary
            console.print()
            if cancelled_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm3

                success_color = _tm3.get_color("success")
                console.print(
                    f"[{success_color}]✓[/{success_color}] Cancelled {cancelled_count} task(s)"
                )
            if failed_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm_err4

                err = _tm_err4.get_color("error")
                console.print(f"[{err}]✗[/{err}] Failed to cancel {failed_count} task(s)")

            # Show next actions
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow submit <config.yaml>[/accent]",
                ]
            )

        except click.Abort:
            try:
                timeline.finish()
            except Exception:  # noqa: BLE001
                pass
            console.print("[dim]Cancelled[/dim]")
            raise click.exceptions.Exit(130)
        except KeyboardInterrupt:
            try:
                timeline.finish()
            except Exception:  # noqa: BLE001
                pass
            console.print("[dim]Cancelled[/dim]")
            raise click.exceptions.Exit(130)
        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:  # noqa: BLE001
            self.handle_error(str(e))


# Export command instance
command = CancelCommand()
