"""Status presenter (core default UI).

Coordinates fetching, formatting, table rendering, header summary, tip bar,
and index cache saving for the default status UI.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from rich.console import Console
except Exception:  # pragma: no cover  # noqa: BLE001

    class Console:  # type: ignore
        pass


from pathlib import Path

import flow.sdk.factory as sdk_factory
from flow.cli.constants import DEFAULT_STATUS_LIMIT
from flow.cli.ui.presentation.next_steps import (
    build_status_recommendations,
    render_next_steps_panel,
)
from flow.cli.ui.presentation.nomenclature import get_entity_labels
from flow.cli.ui.presentation.status_table_renderer import StatusTableRenderer
from flow.cli.ui.presentation.time_formatter import TimeFormatter
from flow.cli.ui.runtime.owner_resolver import Me, OwnerResolver
from flow.cli.utils.icons import prefix_with_flow_icon
from flow.cli.utils.task_fetcher import TaskFetcher
from flow.cli.utils.task_index_cache import TaskIndexCache
from flow.cli.utils.theme_manager import theme_manager
from flow.sdk.client import Flow
from flow.sdk.models import Task


@dataclass
class StatusDisplayOptions:
    show_all: bool = False
    limit: int = DEFAULT_STATUS_LIMIT
    group_by_origin: bool = True
    # When set, indicates the list is filtered by a specific status (e.g., "completed")
    status_filter: str | None = None


class StatusPresenter:
    def __init__(self, console: Console | None = None, flow_client: Flow | None = None) -> None:
        self.console = console or theme_manager.create_console()
        # Prefer factory to construct the client in CLI layer; kept patchable
        self.flow = flow_client or sdk_factory.create_client(auto_init=True)
        self.fetcher = TaskFetcher(self.flow)
        self.time_fmt = TimeFormatter()
        self.table = StatusTableRenderer(self.console)
        self.owner_resolver = OwnerResolver(self.flow)

    def _dbg(self, msg: str) -> None:
        try:
            if os.environ.get("FLOW_STATUS_DEBUG"):
                logging.getLogger("flow.status.presenter").info(msg)
        except Exception:  # noqa: BLE001
            pass

    def present(
        self,
        options: StatusDisplayOptions,
        tasks: list[Task] | None = None,
        *,
        me: Me | None = None,
        owner_map: dict[str, str] | None = None,
        fast: bool = False,
    ) -> None:
        # Surface provider/project context early for scoping issues
        try:
            if os.environ.get("FLOW_STATUS_DEBUG"):
                provider = self.flow.provider
                prov = provider.__class__.__name__
                pid = getattr(provider, "project_id", None)
                self._dbg(
                    f"present: provider={prov} project_id={pid} show_all={options.show_all} status={options.status_filter} limit={options.limit}"
                )
        except Exception:  # noqa: BLE001
            pass

        if tasks is None:
            # Prefer active tasks first to speed up empty state and satisfy tests
            try:
                from flow.sdk.models import TaskStatus as _TS

                tasks = self.flow.list_tasks(status=[_TS.RUNNING, _TS.PENDING], limit=options.limit)
                self._dbg(f"present: fetched active-first list count={len(tasks) if tasks else 0}")
            except Exception as e:  # noqa: BLE001
                tasks = None
                self._dbg(f"present: active fetch error={e}")
            if not tasks:
                # Fall back to default list and then fetcher
                try:
                    tasks = self.flow.list_tasks(limit=options.limit)
                    self._dbg(f"present: fetched general list count={len(tasks) if tasks else 0}")
                except Exception as e:  # noqa: BLE001
                    tasks = None
                    self._dbg(f"present: general fetch error={e}")
                if tasks is None:
                    tasks = self.fetcher.fetch_for_display(
                        show_all=options.show_all, status_filter=None, limit=options.limit
                    )
                    self._dbg(f"present: fetcher provided list count={len(tasks) if tasks else 0}")
        if not tasks:
            try:
                self.console.print(f"[dim]No {get_entity_labels().empty_plural} found[/dim]")
            except Exception:  # noqa: BLE001
                self.console.print("[dim]No tasks found[/dim]")
            self._dbg(
                "present: empty after fetch — likely provider returned 0 or project scope mismatch"
            )
            return

        # Pre-table summary will be computed after filters are applied for clarity

        # Use provided identity context when available to avoid extra network calls
        me = me if me is not None else self.owner_resolver.get_me()
        owner_map = owner_map if owner_map is not None else self.owner_resolver.get_teammates_map()

        # Apply the same 24h time-window filtering in grouped view to keep behavior consistent
        # with the non-grouped path. When show_all is set, skip time filtering.
        tasks_for_display = list(tasks)
        showing_active_only = False
        if (not options.show_all) and (not options.status_filter):
            try:
                from flow.cli.utils.task_filter import TaskFilter as _TF

                before = len(tasks_for_display)
                tasks_for_display = _TF.filter_by_time_window(
                    tasks_for_display, hours=24, include_active=True
                )
                after = len(tasks_for_display)
                # Try to capture time range info (best-effort)
                try:
                    created = [getattr(t, "created_at", None) for t in tasks_for_display]
                    created = [c for c in created if c]
                    oldest = min(created).isoformat() if created else "n/a"
                    newest = max(created).isoformat() if created else "n/a"
                except Exception:  # noqa: BLE001
                    oldest = newest = "n/a"
                self._dbg(
                    f"present: 24h filter applied before={before} after={after} range=[{oldest}..{newest}]"
                )
            except Exception:  # noqa: BLE001
                # Fallback: keep original tasks on any error
                tasks_for_display = list(tasks)

            # If there are any active tasks, suppress non-active ones from the
            # default snapshot view. This preserves the long-standing behavior
            # that default 'flow status' shows only active tasks unless there
            # are none, in which case we show recent tasks.
            try:
                from flow.sdk.models import TaskStatus as _TS

                has_active = any(
                    getattr(t, "status", None) in (_TS.RUNNING, _TS.PENDING)
                    for t in tasks_for_display
                )
                if has_active:
                    before = len(tasks_for_display)
                    tasks_for_display = [
                        t
                        for t in tasks_for_display
                        if getattr(t, "status", None) in (_TS.RUNNING, _TS.PENDING)
                    ]
                    showing_active_only = True
                    self._dbg(
                        f"present: pruned non-active for snapshot before={before} after={len(tasks_for_display)}"
                    )
                else:
                    # No active tasks; we are showing recent window. Offer a small hint.
                    # Only show if we actually have recent tasks to display
                    if tasks_for_display:
                        try:
                            noun = get_entity_labels().empty_plural
                            self.console.print(
                                f"[dim]No active {noun} — showing recent (last 24h). Use --all for full history.[/dim]\n"
                            )
                        except Exception:  # noqa: BLE001
                            pass
            except Exception:  # noqa: BLE001
                pass

        # Apply status filter client-side when requested (covers provider gaps like 'preempting')
        if options.status_filter:
            try:
                from flow.cli.utils.task_filter import TaskFilter as _TF
                from flow.sdk.models import TaskStatus as _TS

                before = len(tasks_for_display)

                # Handle display statuses (open, starting) vs core TaskStatus enum values
                if options.status_filter in ["open", "starting"]:
                    # Filter by display status using TaskFormatter
                    from flow.cli.ui.formatters.shared_task import TaskFormatter

                    def _matches_display_status(t):
                        display_status = TaskFormatter.get_display_status(t)
                        return display_status == options.status_filter

                    tasks_for_display = [t for t in tasks_for_display if _matches_display_status(t)]
                else:
                    # For core TaskStatus enum values, apply the filter
                    status_enum = _TS(options.status_filter)
                    tasks_for_display = _TF.filter_by_status(tasks_for_display, status_enum)

                self._dbg(
                    f"present: status filter='{options.status_filter}' before={before} after={len(tasks_for_display)}"
                )
            except Exception:  # noqa: BLE001
                # If conversion fails, leave list unchanged
                pass

        # Best-effort: annotate visible RUNNING tasks with an SSH readiness hint.
        # Default disabled for snapshot mode to keep UX snappy; opt-in via env.
        try:
            enable_probe_val = (os.environ.get("FLOW_STATUS_SSH_PROBE") or "").strip().lower()
            enable_probe = enable_probe_val in {"1", "true", "yes", "on"}
        except Exception:  # noqa: BLE001
            enable_probe = False

        if enable_probe:
            try:
                from pathlib import Path as _Path

                from flow.adapters.transport.ssh.ssh_stack import SshStack as _S
                from flow.sdk.models import TaskStatus as _TS

                max_probe = 12
                probed = 0
                for t in tasks_for_display:
                    if probed >= max_probe:
                        break
                    try:
                        if getattr(t, "status", None) != _TS.RUNNING:
                            continue
                        host = getattr(t, "ssh_host", None)
                        port = int(getattr(t, "ssh_port", 22) or 22)
                        if not host:
                            continue
                        meta = getattr(t, "provider_metadata", {}) or {}
                        # Do not overwrite an existing hint; only fill gaps
                        if "ssh_ready_hint" in meta:
                            continue
                        ok: bool | None = None
                        # Attempt an auth-aware probe using the provider's quick key resolution
                        try:
                            key_path = self.flow.get_task_ssh_connection_info(
                                getattr(t, "task_id", "")
                            )
                            if isinstance(key_path, Path):
                                ok = _S.is_ssh_ready(
                                    user=getattr(t, "ssh_user", "ubuntu"),
                                    host=str(host),
                                    port=int(port),
                                    key_path=_Path(key_path),
                                )
                        except Exception:  # noqa: BLE001
                            ok = None
                        if ok is None:
                            # Fallback to a lightweight TCP probe when auth check isn't possible
                            ok = _S.is_endpoint_responsive(str(host), int(port))
                        try:
                            meta["ssh_ready_hint"] = bool(ok)
                            t.provider_metadata = meta
                        except Exception:  # noqa: BLE001
                            pass
                        probed += 1
                    except Exception:  # noqa: BLE001
                        continue
            except Exception:  # noqa: BLE001
                pass

        # Ground-truth enrichment: refresh a few RUNNING tasks without ssh_host.
        # In fast mode, skip this entirely to keep UX responsive.
        try:
            if fast:
                raise RuntimeError("skip_refresh_fast_mode")
            from flow.cli.ui.presentation.task_formatter import TaskFormatter as _TF
            from flow.sdk.models import TaskStatus as _TS

            refresh_indices: list[int] = []
            for idx, t in enumerate(tasks_for_display):
                if len(refresh_indices) >= 3:  # cap network calls
                    break
                try:
                    if (
                        getattr(t, "status", None) == _TS.RUNNING
                        and not getattr(t, "ssh_host", None)
                        and str(_TF.get_display_status(t)).lower() == "starting"
                    ):
                        refresh_indices.append(idx)
                except Exception:  # noqa: BLE001
                    continue

            for idx in refresh_indices:
                try:
                    tid = getattr(tasks_for_display[idx], "task_id", None) or getattr(
                        tasks_for_display[idx], "id", None
                    )
                    if not tid:
                        continue
                    updated = self.flow.get_task(str(tid))
                    if updated:
                        tasks_for_display[idx] = updated
                except Exception:  # noqa: BLE001
                    # Best-effort only; skip on any error
                    continue
        except Exception:  # noqa: BLE001
            pass

        # Summary line (based on filtered/time-windowed list for clarity)
        try:
            # Count by display status so "starting" isn't misreported as "running"
            from flow.cli.ui.presentation.task_formatter import (
                TaskFormatter as _TF,
            )

            counts = {"running": 0, "pending": 0, "starting": 0}
            for t in tasks_for_display:
                try:
                    s = _TF.get_display_status(t)
                except Exception:  # noqa: BLE001
                    s = getattr(getattr(t, "status", None), "value", str(getattr(t, "status", "")))
                key = str(s).lower()
                if key in counts:
                    counts[key] += 1

            parts: list[str] = []
            if counts["running"]:
                parts.append(f"{counts['running']} running")
            if counts["starting"]:
                parts.append(f"{counts['starting']} starting")
            if counts["pending"]:
                parts.append(f"{counts['pending']} pending")
            if parts:
                self.console.print("[dim]" + " · ".join(parts) + "[/dim]\n")
        except Exception:  # noqa: BLE001
            pass

        # Optional grouping by origin (Flow vs Other) using provider metadata
        if options.group_by_origin:
            flow_tasks: list[Task] = []
            other_tasks: list[Task] = []
            for t in tasks_for_display:
                try:
                    meta = getattr(t, "provider_metadata", {}) or {}
                    origin = str(meta.get("origin", "")).lower()
                    if origin in ("flow-cli", "flow-compute"):
                        flow_tasks.append(t)
                    else:
                        other_tasks.append(t)
                except Exception:  # noqa: BLE001
                    other_tasks.append(t)

            displayed_tasks: list[Task] = []

            # Compute a unified GPU column width across groups for visual alignment
            forced_gpu_width: int | None = None
            try:
                from flow.cli.ui.presentation.gpu_formatter import GPUFormatter as _GF

                desired = 0
                for group in (flow_tasks, other_tasks):
                    for t in group:
                        ni = getattr(t, "num_instances", 1)
                        try:
                            ni = max(1, int(ni))
                        except Exception:  # noqa: BLE001
                            ni = 1
                        s = _GF.format_ultra_compact(getattr(t, "instance_type", "") or "", ni)
                        desired = max(desired, len(s))
                # Match renderer's clamp logic (min width respected inside)
                forced_gpu_width = desired
            except Exception:  # noqa: BLE001
                forced_gpu_width = None

            if flow_tasks:
                # Brand the Flow group title with the CLI icon (same as --help)
                title_flow = prefix_with_flow_icon("Flow")
                panel_flow = self.table.render(
                    flow_tasks,
                    me=me,
                    owner_map=owner_map,
                    title=title_flow,
                    wide=False,
                    start_index=1,
                    return_renderable=True,
                    forced_gpu_width=forced_gpu_width,
                )
                self.console.print(panel_flow)
                displayed_tasks.extend(flow_tasks)

            if other_tasks:
                # Add spacing if both groups present
                if flow_tasks:
                    self.console.print("")
                # Inline hint so the panel is self-explanatory even without a footer legend
                title_other = "External · outside Flow"
                panel_other = self.table.render(
                    other_tasks,
                    me=me,
                    owner_map=owner_map,
                    title=title_other,
                    wide=False,
                    start_index=(len(flow_tasks) + 1),
                    return_renderable=True,
                    forced_gpu_width=forced_gpu_width,
                )
                self.console.print(panel_other)
                displayed_tasks.extend(other_tasks)

            if not flow_tasks and not other_tasks:
                try:
                    self.console.print(f"[dim]No {get_entity_labels().empty_plural} found[/dim]")
                except Exception:  # noqa: BLE001
                    self.console.print("[dim]No tasks found[/dim]")
        else:
            noun_plural = get_entity_labels().title_plural
            if not options.show_all:
                title = f"{noun_plural} (showing up to {options.limit}, last 24 hours)"
            else:
                title = f"{noun_plural} (showing up to {options.limit})"
            # Prefix non-grouped table title with icon for consistent branding
            title = prefix_with_flow_icon(title)
            displayed_tasks = list(tasks_for_display)
            panel = self.table.render(
                tasks_for_display,
                me=me,
                owner_map=owner_map,
                title=title,
                wide=False,
                start_index=1,
                return_renderable=True,
                avoid_network_owner_lookups=fast,
            )
            self.console.print(panel)

        if options.group_by_origin:
            legend = "External (launched outside Flow, e.g., provider console)"
            try:
                provider_name = getattr(getattr(self.flow, "config", None), "provider", None) or ""
                if not provider_name:
                    import os as _os

                    provider_name = (_os.environ.get("FLOW_PROVIDER") or "").lower()
                if (provider_name or "").lower() == "mithril":
                    legend = "External (launched outside Flow, e.g., Mithril Console)"
            except Exception:  # noqa: BLE001
                pass
            # Prefer plain language over UI-jargon; show only if both groups are present
            try:
                if flow_tasks and other_tasks:
                    self.console.print(f"\n[dim]Groups: Flow (CLI/SDK) · {legend}[/dim]")
            except Exception:  # noqa: BLE001
                # If group variables are unavailable, fall back to showing the legend
                self.console.print(f"\n[dim]Groups: Flow (CLI/SDK) · {legend}[/dim]")
        # Post-table context note: reflect whether we actually pruned to active-only
        # Only show this message if tasks were actually displayed
        if displayed_tasks and (not options.show_all) and not options.status_filter:
            # Add breathing room between the table and this context note
            try:
                noun = get_entity_labels().empty_plural
                if showing_active_only:
                    self.console.print(
                        f"\n[muted]Showing active {noun} only. Use --all to see all {noun}.[/muted]"
                    )
                else:
                    self.console.print(
                        f"\n[muted]Showing recent {noun} from the last 24 hours. Use --all to see all {noun}.[/muted]"
                    )
            except Exception:  # noqa: BLE001
                if showing_active_only:
                    self.console.print(
                        "\n[muted]Showing active tasks only. Use --all to see all tasks.[/muted]"
                    )
                else:
                    self.console.print(
                        "\n[muted]Showing recent tasks from the last 24 hours. Use --all to see all tasks.[/muted]"
                    )
        elif options.status_filter:
            # Provide a concise filter acknowledgement for clarity
            self.console.print(f"[dim]Filtered by status: {options.status_filter}[/dim]")

        # Only show tips and recommendations if tasks were displayed
        if not displayed_tasks:
            return

        # Condense index hint into a single, scannable line with an absolute expiry time
        # Replace inline tip with a compact tips panel
        try:
            ttl = getattr(TaskIndexCache, "CACHE_TTL_SECONDS", 300)
            expires_at = datetime.now() + timedelta(seconds=int(ttl))
            expires_local = expires_at.strftime("%H:%M")
            tips = [
                "Use index shortcuts: [accent]1[/accent], [accent]1-3[/accent], [accent]:1[/accent]",
                f"Run [accent]flow status[/accent] to refresh (valid until {expires_local})",
            ]
        except Exception:  # noqa: BLE001
            tips = [
                "Use index shortcuts: [accent]1[/accent], [accent]1-3[/accent], [accent]:1[/accent]",
                "Run [accent]flow status[/accent] to refresh",
            ]
        from flow.cli.ui.presentation.next_steps import render_next_steps_panel as _ns

        _ns(self.console, tips, title="Tips")

        # Save indices in the order displayed so shortcuts match UI numbering
        # Be resilient when tasks are mocks (tests) and may not be JSON serializable
        try:
            cache = TaskIndexCache()
            cache.save_indices(displayed_tasks)
        except Exception as e:  # noqa: BLE001
            # Log for debugging but don't fail the command
            logger = logging.getLogger(__name__)
            logger.debug(f"Failed to save task indices: {e}")
            # Skip caching silently; indices will not be available but display is intact

        count = min(len(displayed_tasks), options.limit)
        if count >= 7:
            multi_example = "1-3,5,7"
        elif count >= 5:
            multi_example = "1-3,5"
        elif count >= 3:
            multi_example = "1-3"
        elif count == 2:
            multi_example = "1-2"
        else:
            multi_example = "1"

        # Dynamic, context-aware next steps
        index_example_single = "1"
        recommendations = build_status_recommendations(
            displayed_tasks,
            max_count=6,
            index_example_single=index_example_single,
            index_example_multi=multi_example,
        )
        if recommendations:
            render_next_steps_panel(self.console, recommendations)
