"""Volumes command group - manage persistent storage volumes for GPU tasks.

Provides creation, deletion, listing, and bulk operations for volumes used by
GPU tasks.

Command Usage:
    flow volume SUBCOMMAND [OPTIONS]

Subcommands:
    list        List all volumes with region and interface info
    info        Show detailed information for a specific volume
    create      Create a new volume
    delete      Delete a volume by ID or name
    delete-all  Delete multiple volumes

Examples:
    List all volumes:
        $ flow volume list

    Create a 100GB block volume:
        $ flow volume create --size 100

    Create a named file storage volume:
        $ flow volume create --size 50 --name training-data --interface file

    Delete by volume ID:
        $ flow volume delete vol_abc123def456

    Delete by volume name (exact or partial match):
        $ flow volume delete training-data
        $ flow volume delete training  # Works if only one match

    Delete without confirmation:
        $ flow volume delete training-data --yes

    Delete all volumes (with confirmation):
        $ flow volume delete-all

    Delete volumes matching pattern:
        $ flow volume delete-all --pattern "test-*"

    Preview deletion without executing:
        $ flow volume delete-all --dry-run

Volume properties:
- ID: Unique identifier (e.g., vol_abc123...)
- Name: Optional human-readable name (can be used instead of ID)
- Region: Where the volume is located (must match task region)
- Size: Storage capacity in GB
- Interface: Storage type (block or file)
- Status: Available or attached (with count)
- Created: Timestamp of creation

The commands will:
- Support both volume IDs and names for operations
- Show region constraints for better planning
- Validate size limits per region
- Handle volume lifecycle operations
- Manage volume attachments to tasks

Note:
    Volumes can only be deleted when not attached to running tasks.
    Volumes must be in the same region as the tasks that use them.
    Both volume IDs and names can be used in task configurations.

    Name Resolution:
    - You can use either volume ID (vol_xxx) or volume name in commands
    - Exact name matches are preferred over partial matches
    - If multiple volumes match a name, you'll be prompted to use the ID
    - Partial name matching works if there's only one match
"""

from datetime import datetime

import click

import flow.sdk.factory as sdk_factory
from flow.adapters.metrics.telemetry import Telemetry
from flow.adapters.providers.builtin.mithril.api.types import StorageType
from flow.cli.app import OrderedDYMGroup
from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.facade.views import TerminalAdapter
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
from flow.cli.ui.presentation.nomenclature import get_entity_labels
from flow.cli.ui.presentation.table_styles import (
    add_centered_column,
    add_left_aligned_column,
    add_right_aligned_column,
    create_flow_table,
    wrap_table_in_panel,
)
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.selection_helpers import parse_selection_to_volume_ids
from flow.cli.utils.theme_manager import theme_manager
from flow.cli.utils.volume_creation import create_volume_interactive
from flow.cli.utils.volume_index_cache import VolumeIndexCache
from flow.cli.utils.volume_operations import VolumeOperations
from flow.cli.utils.volume_resolver import get_volume_display_name, resolve_volume_identifier
from flow.errors import AuthenticationError
from flow.sdk.client import Flow


class VolumesCommand(BaseCommand):
    """Manage storage volumes."""

    @property
    def name(self) -> str:
        return "volume"

    @property
    def help(self) -> str:
        return "Manage persistent storage volumes."

    def _get_available_regions(
        self, flow_client: Flow, storage_type: str | StorageType
    ) -> list[str]:
        """Get available regions for the specified storage type.

        Args:
            storage_type: Storage type (StorageType.BLOCK, StorageType.FILE, or string "block"/"file")

        Raises:
            RuntimeError: If provider doesn't support storage region queries or API call fails
            ValueError: If region data is malformed
        """
        provider = flow_client._ensure_provider()
        if not hasattr(provider, "list_regions_for_storage"):
            raise NotImplementedError(
                f"Provider '{provider.name}' does not support storage region queries. "
                f"Volume management requires MithrilProvider."
            )

        try:
            return provider.list_regions_for_storage(storage_type)
        except Exception as e:
            # Wrap unexpected errors with context
            raise RuntimeError(
                f"Failed to fetch available regions for storage type '{storage_type}': {e}"
            ) from e

    def _build_instance_task_map(self, flow_client: Flow) -> dict[str, tuple[str, str]]:
        """Build mapping of instance_id -> (task_name, task_id).

        Returns empty dict on error to gracefully degrade.
        """
        try:
            # Fetch recent tasks to find volume associations
            tasks = flow_client.tasks.list(limit=500)
            instance_map = {}
            for task in tasks:
                # Map each instance to its task
                for instance_id in task.instances:
                    instance_map[instance_id] = (task.name, task.task_id)
            return instance_map
        except Exception:  # noqa: BLE001
            # Graceful degradation - volumes still display without task info
            return {}

    def get_command(self) -> click.Group:
        """Return the volumes command group."""

        # from flow.cli.utils.mode import demo_aware_command

        @click.group(
            name=self.name, help=self.help, cls=OrderedDYMGroup, invoke_without_command=True
        )
        # @demo_aware_command()
        @click.pass_context
        @cli_error_guard(self)
        def volumes(ctx):
            """Manage storage volumes.

            \b
            Examples:
                flow volume list            # List all volumes
                flow volume create --size 100  # Create 100GB volume
                flow volume create --size 50 --region us-central2-a  # Create in specific region
                flow volume delete vol-123  # Delete volume

            Run 'flow volume' alone to see the complete volume management guide.
            """
            # Show the Storage Volume Management Guide if no subcommand was provided
            if ctx.invoked_subcommand is None:
                console.print("\n[bold]Storage Volume Management:[/bold]\n")
                console.print("Volume types:")
                console.print("  • block - High-performance block storage (default)")
                console.print("  • file  - Shared file storage (NFS-like)\n")

                console.print("Creating volumes:")
                console.print("  flow volume create --size 100                # 100GB block volume")
                console.print("  flow volume create --size 50 --interface file # 50GB file storage")
                console.print("  flow volume create --size 200 --name datasets # Named volume")
                console.print(
                    "  flow volume create --size 500 --region us-central2-a # Specific region\n"
                )

                console.print("Listing and filtering:")
                console.print("  flow volume list                    # All volumes")
                console.print("  flow volume list -d                 # Show task attachments")
                console.print("  flow volume list | grep available   # Filter by status\n")

                console.print("Deleting volumes:")
                console.print("  flow volume delete vol_abc123       # By ID")
                console.print("  flow volume delete training-data    # By name")
                console.print("  flow volume delete-all --pattern 'test-*'  # Pattern matching")
                console.print("  flow volume delete-all --dry-run    # Preview deletions\n")

                console.print("Using volumes in tasks:")
                console.print("  # In YAML config:")
                console.print("  volumes:")
                console.print("    - volume_id: vol_abc123")
                console.print("      mount_path: /data")
                console.print("  # Or by name:")
                console.print("    - volume_name: training-data")
                console.print("      mount_path: /datasets\n")

                console.print("Important constraints:")
                console.print("  • Volumes are region-specific")
                console.print("  • Can't delete volumes attached to running tasks")
                console.print("  • Size limits vary by region (check provider docs)")
                console.print("  • File volumes support multiple concurrent attachments\n")

                console.print("Common workflows:")
                console.print("  # Create and use dataset volume")
                console.print("  flow volume create --size 500 --name imagenet")
                console.print("  flow submit <config.yaml>  # References volume by name")
                console.print("  ")
                console.print("  # Share data between tasks")
                console.print("  flow mount shared-data task1")
                console.print("  flow mount shared-data task2\n")
            # Initialize a single Flow client in context for this invocation
            try:
                ctx.ensure_object(dict)
                if (ctx.obj or {}).get("flow_client") is None:
                    ctx.obj["flow_client"] = sdk_factory.create_client(auto_init=True)
            except AuthenticationError:
                ctx.ensure_object(dict)
                ctx.obj["flow_client"] = None

        volumes.add_command(self._list_command(), name="list")
        volumes.add_command(self._create_command())
        volumes.add_command(self._describe_command(), name="info")
        volumes.add_command(self._delete_command())
        volumes.add_command(self._delete_all_command())

        # Lightweight alias: `flow volume mount <vol> <task>` delegates to top-level `flow mount`
        try:
            import click as _click

            from flow.cli.commands.mount import command as _mount_cmd_obj  # type: ignore

            # Get the underlying click command from our BaseCommand wrapper
            mount_click_command = _mount_cmd_obj.get_command()

            from flow.cli.ui.presentation.nomenclature import get_entity_labels

            labels = get_entity_labels()

            @_click.command(
                name="mount",
                help=f"Alias for 'flow mount' – attach a volume to {labels.article} {labels.singular}",
            )
            @_click.argument("volume_identifier", required=False)
            @_click.argument("task_identifier", required=False)
            @_click.pass_context
            def volumes_mount(ctx, volume_identifier: str | None, task_identifier: str | None):
                # Re-invoke the top-level mount command, relying on its default options
                args: list[str] = []
                if volume_identifier:
                    args.append(volume_identifier)
                if task_identifier:
                    args.append(task_identifier)
                # Use click's command re-entry to preserve option defaults
                try:
                    return mount_click_command.main(args=args, standalone_mode=False)
                except SystemExit as e:  # pragma: no cover - click control flow
                    # Propagate click's intended exit codes in CLI context
                    if e.code not in (0, None):
                        raise
                    return None

            volumes.add_command(volumes_mount)
        except Exception:  # noqa: BLE001
            # If mount command is unavailable for any reason, skip alias silently
            pass

        return volumes

    def _describe_command(self) -> click.Command:
        # Import completion/helpers lazily to keep startup light
        from flow.cli.ui.runtime.shell_completion import (
            complete_volume_ids as _complete_volume_ids,
        )

        @click.command(name="info")
        @click.argument("volume_identifier", shell_complete=_complete_volume_ids)
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--details",
            "-d",
            is_flag=True,
            help="Also show tasks that reference this volume in their config",
        )
        @click.option(
            "--scan-limit",
            type=int,
            default=None,
            help="Max tasks to scan for --details (default: 200; override via env FLOW_VOLUMES_DETAILS_LIMIT)",
        )
        @click.option(
            "--scan-timeout",
            type=float,
            default=None,
            help="Max seconds to spend scanning for --details (default: 3.0; override via env FLOW_VOLUMES_DETAILS_TIMEOUT)",
        )
        @click.pass_context
        @cli_error_guard(self)
        def volumes_describe(
            ctx,
            volume_identifier: str,
            output_json: bool,
            details: bool,
            scan_limit: int | None,
            scan_timeout: float | None,
        ):
            """Show detailed information about a volume.

            Identifies the volume by ID, name, or recent list index (e.g., 1 or :1).
            Includes attachments with task names when available.
            """
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or sdk_factory.create_client(auto_init=True)

                # Resolve user reference → concrete volume (show AEP during network lookup)
                if not output_json:
                    with AnimatedEllipsisProgress(
                        console,
                        f"Resolving volume {volume_identifier}",
                        start_immediately=True,
                    ):
                        volume, error = resolve_volume_identifier(flow_client, volume_identifier)
                else:
                    volume, error = resolve_volume_identifier(flow_client, volume_identifier)
                if error:
                    console.print(f"[error]Error:[/error] {error}")
                    return

                # Best-effort refresh to get most up-to-date attachment state
                try:
                    if not output_json:
                        with AnimatedEllipsisProgress(
                            console, "Refreshing volume state", start_immediately=True
                        ):
                            _all = flow_client.volumes.list()
                    else:
                        _all = flow_client.volumes.list()
                    _vid = getattr(volume, "volume_id", None) or getattr(volume, "id", None)
                    _fresh = next(
                        (
                            v
                            for v in _all
                            if (getattr(v, "volume_id", None) or getattr(v, "id", None)) == _vid
                        ),
                        None,
                    )
                    if _fresh is not None:
                        volume = _fresh
                except Exception:  # noqa: BLE001
                    pass

                # Build attachments → task mapping for richer display
                # Fetch tasks when we have attachments (to resolve names) or when --details is requested
                instance_task_map: dict[str, tuple[str, str]] = {}
                tasks_for_scan = []
                _need_tasks = bool(getattr(volume, "attached_to", None)) or details
                if _need_tasks and not output_json:
                    try:
                        _fetch_msg = f"Fetching {get_entity_labels().empty_plural}"
                    except Exception:  # noqa: BLE001
                        _fetch_msg = "Fetching tasks"
                    with AnimatedEllipsisProgress(console, _fetch_msg, start_immediately=True):
                        instance_task_map = self._build_instance_task_map(flow_client)
                        try:
                            # Bound the fetch size for responsiveness
                            import os as _os

                            default_limit = 200
                            env_limit = _os.environ.get("FLOW_VOLUMES_DETAILS_LIMIT")
                            eff_limit = scan_limit or (
                                int(env_limit)
                                if env_limit and env_limit.isdigit()
                                else default_limit
                            )
                            tasks_for_scan = flow_client.tasks.list(
                                limit=max(10, min(1000, eff_limit))
                            )
                        except Exception:  # noqa: BLE001
                            tasks_for_scan = []
                elif _need_tasks:
                    instance_task_map = self._build_instance_task_map(flow_client)
                    try:
                        import os as _os

                        default_limit = 200
                        env_limit = _os.environ.get("FLOW_VOLUMES_DETAILS_LIMIT")
                        eff_limit = scan_limit or (
                            int(env_limit) if env_limit and env_limit.isdigit() else default_limit
                        )
                        tasks_for_scan = flow_client.tasks.list(limit=max(10, min(1000, eff_limit)))
                    except Exception:  # noqa: BLE001
                        tasks_for_scan = []

                attachments: list[dict[str, str]] = []
                for inst_id in getattr(volume, "attached_to", []) or []:
                    t_name, t_id = instance_task_map.get(inst_id, (None, None))
                    attachments.append(
                        {
                            "instance_id": inst_id,
                            **({"task_id": t_id} if t_id else {}),
                            **({"task_name": t_name} if t_name else {}),
                        }
                    )
                # JSON output path
                if output_json:
                    from flow.cli.utils.json_output import print_json, volume_to_json

                    print_json(volume_to_json(volume, attachments=attachments))
                    return

                # When details requested, also collect tasks that reference this volume
                # Prefer provider's bid data embedded in volume ('bids') when available
                referenced_tasks: list[dict[str, str]] = []
                volume_bid_ids = []
                try:
                    volume_bid_ids = list(getattr(volume, "bids", []) or [])
                except Exception:  # noqa: BLE001
                    volume_bid_ids = []

                if details and (tasks_for_scan or volume_bid_ids):
                    # Normalize the volume ID for cross-referencing with bids/tasks
                    try:
                        _vid2 = str(
                            getattr(volume, "volume_id", None) or getattr(volume, "id", None) or ""
                        )
                    except Exception:  # noqa: BLE001
                        _vid2 = ""

                    # Helper to check bid dict shapes safely
                    def _bid_references_volume(bid: dict, vol_id: str) -> bool:
                        try:
                            # Newer APIs: nested under launch_specification
                            ls = bid.get("launch_specification") if isinstance(bid, dict) else None
                            if isinstance(ls, dict):
                                vols = ls.get("volumes")
                                if isinstance(vols, list) and vol_id in vols:
                                    return True
                            # Legacy: top-level volumes array
                            vols2 = bid.get("volumes") if isinstance(bid, dict) else None
                            if isinstance(vols2, list) and vol_id in vols2:
                                return True
                        except Exception:  # noqa: BLE001
                            pass
                        return False

                    try:
                        provider = getattr(flow_client, "provider", None)
                        get_bid = None
                        if provider is not None:
                            try:
                                tasks_facet = getattr(provider, "tasks", None)
                                if tasks_facet is not None and hasattr(tasks_facet, "get_bid_dict"):
                                    get_bid = tasks_facet.get_bid_dict  # type: ignore[attr-defined]
                            except Exception:  # noqa: BLE001
                                get_bid = None

                        # If the API provided direct bid IDs, prefer those for quick resolution
                        if volume_bid_ids:
                            # Resolve tasks referenced by bid IDs with user feedback
                            if not output_json:
                                with AnimatedEllipsisProgress(
                                    console,
                                    "Resolving task references",
                                    start_immediately=True,
                                ):
                                    for bid_id in volume_bid_ids:
                                        try:
                                            t = flow_client.tasks.get(bid_id)
                                            if t:
                                                referenced_tasks.append(
                                                    {
                                                        "task_id": getattr(t, "task_id", ""),
                                                        "task_name": getattr(t, "name", ""),
                                                        "status": getattr(t, "status", ""),
                                                    }
                                                )
                                        except Exception:  # noqa: BLE001
                                            continue
                            else:
                                for bid_id in volume_bid_ids:
                                    try:
                                        t = flow_client.tasks.get(bid_id)
                                        if t:
                                            referenced_tasks.append(
                                                {
                                                    "task_id": getattr(t, "task_id", ""),
                                                    "task_name": getattr(t, "name", ""),
                                                    "status": getattr(t, "status", ""),
                                                }
                                            )
                                    except Exception:  # noqa: BLE001
                                        continue
                        else:
                            # Time-bounded scan to avoid perceived hangs
                            import os as _os
                            import time as _time

                            default_timeout = 3.0
                            env_timeout = _os.environ.get("FLOW_VOLUMES_DETAILS_TIMEOUT")
                            try:
                                eff_timeout = (
                                    float(env_timeout)
                                    if env_timeout
                                    else float(scan_timeout or default_timeout)
                                )
                            except Exception:  # noqa: BLE001
                                eff_timeout = default_timeout

                            start = _time.monotonic()
                            scanned = 0
                            if not output_json:
                                with AnimatedEllipsisProgress(
                                    console,
                                    "Scanning tasks for references",
                                    start_immediately=True,
                                ):
                                    for _t in tasks_for_scan:
                                        if (_time.monotonic() - start) > max(0.5, eff_timeout):
                                            break
                                        scanned += 1
                                        matched = False
                                        if get_bid is not None:
                                            try:
                                                bid = get_bid(getattr(_t, "task_id", ""))
                                                if isinstance(bid, dict) and _bid_references_volume(
                                                    bid, _vid2
                                                ):
                                                    matched = True
                                            except Exception:  # noqa: BLE001
                                                matched = False
                                        if not matched:
                                            _cfg = getattr(_t, "config", None)
                                            _vols = getattr(_cfg, "volumes", None) if _cfg else None
                                            if _vols:
                                                for _vs in _vols:
                                                    try:
                                                        if getattr(_vs, "volume_id", None) == _vid2:
                                                            matched = True
                                                            break
                                                    except Exception:  # noqa: BLE001
                                                        continue
                                        if matched:
                                            referenced_tasks.append(
                                                {
                                                    "task_id": getattr(_t, "task_id", ""),
                                                    "task_name": getattr(_t, "name", ""),
                                                    "status": getattr(_t, "status", ""),
                                                }
                                            )
                            else:
                                for _t in tasks_for_scan:
                                    if (_time.monotonic() - start) > max(0.5, eff_timeout):
                                        break
                                    scanned += 1
                                    matched = False
                                    if get_bid is not None:
                                        try:
                                            bid = get_bid(getattr(_t, "task_id", ""))
                                            if isinstance(bid, dict) and _bid_references_volume(
                                                bid, _vid2
                                            ):
                                                matched = True
                                        except Exception:  # noqa: BLE001
                                            matched = False
                                    if not matched:
                                        _cfg = getattr(_t, "config", None)
                                        _vols = getattr(_cfg, "volumes", None) if _cfg else None
                                        if _vols:
                                            for _vs in _vols:
                                                try:
                                                    if getattr(_vs, "volume_id", None) == _vid2:
                                                        matched = True
                                                        break
                                                except Exception:  # noqa: BLE001
                                                    continue
                                    if matched:
                                        referenced_tasks.append(
                                            {
                                                "task_id": getattr(_t, "task_id", ""),
                                                "task_name": getattr(_t, "name", ""),
                                                "status": getattr(_t, "status", ""),
                                            }
                                        )

                            # If time-bounded scan truncated results, annotate in UI via panel note
                            if not output_json and scanned < len(tasks_for_scan):
                                try:
                                    from rich.text import Text as _Text

                                    _dim = theme_manager.get_color("muted")
                                    note = _Text(
                                        f"Scan limited to {scanned}/{len(tasks_for_scan)} tasks (use --scan-limit/--scan-timeout or env FLOW_VOLUMES_DETAILS_LIMIT/TIMEOUT)",
                                        style=_dim,
                                    )
                                    _details_scan_note = note
                                except Exception:  # noqa: BLE001
                                    pass
                    except Exception:  # noqa: BLE001
                        # Gracefully skip if provider API not available
                        referenced_tasks = []

                # Build a normalized record dict for downstream display/telemetry
                try:
                    _vol_id = str(getattr(volume, "volume_id", None) or getattr(volume, "id", ""))
                except Exception:  # noqa: BLE001
                    _vol_id = ""
                try:
                    _iface = getattr(volume, "interface", "block")
                    if hasattr(_iface, "value"):
                        _iface = _iface.value
                    _iface = str(_iface)
                except Exception:  # noqa: BLE001
                    _iface = "block"
                record = {
                    "id": _vol_id,
                    "name": getattr(volume, "name", None) or None,
                    "region": getattr(volume, "region", "") or "",
                    "size_gb": getattr(volume, "size_gb", None),
                    "interface": _iface,
                    "created_at": getattr(volume, "created_at", None),
                    "status": "available" if not attachments else "attached",
                }

                # Telemetry: describe usage
                try:
                    Telemetry().log_event(
                        "volumes.describe",
                        {
                            "id": record.get("id", ""),
                            "has_attachments": bool(attachments),
                        },
                    )
                except Exception:  # noqa: BLE001
                    pass

                if output_json:
                    try:
                        import json as _json

                        console.print(_json.dumps(record, default=str, indent=2))
                    except Exception:  # noqa: BLE001
                        # Fallback to repr if JSON serialization fails
                        console.print(str(record))
                    return

                # Human-friendly tables -------------------------------------------------
                from rich.text import Text as _Text

                summary = create_flow_table(show_borders=False, expand=False)
                add_left_aligned_column(summary, "Field", width=14)
                add_left_aligned_column(summary, "Value", ratio=1, overflow="fold")

                vid = str(record.get("id") or "")
                vname = str(record.get("name") or vid)
                vregion = record.get("region") or ""
                vsize = record.get("size_gb")
                vinterface = record.get("interface") or "block"
                vcreated = record.get("created_at")

                # Status badge
                if record.get("status") == "available":
                    color = theme_manager.get_color("status.running")
                    status_str = f"[{color}]● available[/{color}]"
                else:
                    color = theme_manager.get_color("status.pending")
                    count = len(attachments)
                    status_str = f"[{color}]● attached ({count})[/{color}]"

                def _add_row(label: str, value: object | None) -> None:
                    summary.add_row(label, "" if value is None else str(value))

                _add_row("Name", vname)
                _add_row("ID", vid)
                _add_row("Region", vregion)
                _add_row("Size (GB)", vsize)
                _add_row("Interface", vinterface)
                if vcreated:
                    try:
                        # Standardize timestamp display
                        ts = str(vcreated)
                        _add_row("Created", ts[:19])
                    except Exception:  # noqa: BLE001
                        _add_row("Created", vcreated)
                _add_row("Status", _Text.from_markup(status_str))

                wrap_table_in_panel(summary, f"Volume: {vname}", console)

                # Attachments table – show only when provider exposes attachments
                if bool(getattr(volume, "attachments_supported", False)):
                    from flow.cli.ui.presentation.nomenclature import get_entity_labels

                    labels = get_entity_labels()
                    atable = create_flow_table(show_borders=False, expand=False)
                    add_left_aligned_column(atable, labels.header, width=24)
                    add_left_aligned_column(atable, f"{labels.header} ID", width=14)
                    add_left_aligned_column(atable, "Instance ID", ratio=1, overflow="fold")

                    if attachments:
                        for att in attachments:
                            atable.add_row(
                                str(att.get("task_name") or ""),
                                str(att.get("task_id") or ""),
                                str(att.get("instance_id") or ""),
                            )
                    else:
                        from rich.text import Text as _Text

                        _dim = theme_manager.get_color("muted")
                        atable.add_row(_Text("No current attachments", style=_dim), "", "")

                    wrap_table_in_panel(
                        atable,
                        f"Attachments ({len(attachments)})",
                        console,
                    )

                # Referenced-by table (only when --details and matches found)
                if details and referenced_tasks:
                    from flow.cli.ui.presentation.nomenclature import get_entity_labels

                    labels = get_entity_labels()
                    # Derive which referenced tasks are currently attached (via instance_id → task_id map)
                    attached_task_ids: set[str] = set()
                    try:
                        for _inst_id in getattr(volume, "attached_to", []) or []:
                            _pair = instance_task_map.get(_inst_id)
                            if _pair and _pair[1]:
                                attached_task_ids.add(str(_pair[1]))
                    except Exception:  # noqa: BLE001
                        attached_task_ids = set()
                    rtable = create_flow_table(show_borders=False, expand=False)
                    add_left_aligned_column(rtable, labels.header, width=24)
                    add_left_aligned_column(rtable, f"{labels.header} ID", width=14)
                    add_left_aligned_column(rtable, "Status", width=10)
                    add_centered_column(rtable, "Attached", width=9)
                    for _rt in referenced_tasks:
                        # Status may be enum; show name when available
                        _status = _rt.get("status")
                        _status_str = getattr(_status, "name", None) or str(_status or "")
                        _attached = (
                            "Yes" if str(_rt.get("task_id") or "") in attached_task_ids else ""
                        )
                        rtable.add_row(
                            str(_rt.get("task_name") or ""),
                            str(_rt.get("task_id") or ""),
                            _status_str,
                            _attached,
                        )
                    panel = wrap_table_in_panel(
                        rtable, f"Referenced By Tasks ({len(referenced_tasks)})", console
                    )
                    # If we created a scan note above, best-effort print beneath
                    try:
                        if (
                            "_details_scan_note" in locals()
                            and locals()["_details_scan_note"] is not None
                        ):
                            console.print(locals()["_details_scan_note"])
                    except Exception:  # noqa: BLE001
                        pass
                    # Brief clarification to prevent confusion between referenced vs current attachments
                    try:
                        from rich.text import Text as _Text

                        _muted = theme_manager.get_color("muted")
                        _note = _Text(
                            "Referenced shows tasks that request this volume in config; Attachments shows instances currently attached.",
                            style=_muted,
                        )
                        console.print(_note)
                    except Exception:  # noqa: BLE001
                        pass

                # If provider does not expose instance attachments (common), and the volume has
                # bid references or running tasks referencing it, make it explicit to avoid confusion.
                try:
                    if not getattr(volume, "attached_to", None) and (
                        volume_bid_ids or referenced_tasks
                    ):
                        from rich.text import Text as _Text

                        _muted = theme_manager.get_color("muted")
                        console.print(
                            _Text(
                                "Provider API does not expose current instance attachments in volumes; 'Attachments' may be unavailable.",
                                style=_muted,
                            )
                        )
                except Exception:  # noqa: BLE001
                    pass

                # Next actions for ergonomics
                from flow.cli.ui.presentation.nomenclature import get_entity_labels

                labels = get_entity_labels()
                tips: list[str] = [
                    f"Attach to {labels.article} {labels.singular}: [accent]flow mount <volume> <{labels.singular}>[/accent]",
                    "List volumes: [accent]flow volume list[/accent]",
                ]
                try:
                    from flow.cli.ui.presentation.next_steps import (
                        render_next_steps_panel as _ns,
                    )

                    _ns(console, tips, title="Next steps")
                except Exception:  # noqa: BLE001
                    for t in tips:
                        console.print(t)

            except AuthenticationError:
                self.handle_auth_error()
            except Exception as e:  # noqa: BLE001
                self.handle_error(e)

        return volumes_describe

    def _list_command(self) -> click.Command:
        @click.command(name="list")
        @click.option("--details", "-d", is_flag=True, help="Show which tasks use each volume")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option("--region", "region", help="Filter volumes by region (default: all)")
        @click.pass_context
        @cli_error_guard(self)
        def volumes_list(ctx, details: bool, region: str | None, output_json: bool):
            """List all volumes."""
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or sdk_factory.create_client(auto_init=True)

                # Clarify region in the AEP message when filtered
                _msg = f"Fetching volumes{f' (region: {region})' if region else ''}"
                with AnimatedEllipsisProgress(console, _msg, start_immediately=True):
                    # If region filter is requested and provider supports it,
                    # fetch and filter via provider; otherwise filter client-side.
                    volumes = flow_client.volumes.list()
                    if region:
                        try:
                            volumes = [v for v in volumes if getattr(v, "region", None) == region]
                        except Exception:  # noqa: BLE001
                            pass

                # Sort by creation time (newest first) for consistent, useful ordering
                try:
                    volumes = sorted(
                        volumes,
                        key=lambda v: getattr(v, "created_at", None) or datetime.min,
                        reverse=True,
                    )
                except Exception:  # noqa: BLE001
                    # If sorting fails for any reason, fall back to provider order
                    pass

                # Telemetry: capture usage and filters
                try:
                    Telemetry().log_event(
                        "volumes.get",
                        {
                            "details": bool(details),
                            "region": str(region or ""),
                            "count": len(volumes) if isinstance(volumes, list) else None,
                        },
                    )
                except Exception:  # noqa: BLE001
                    pass

                if not volumes:
                    console.print("\nNo volumes found.")
                    self.show_next_actions(
                        [
                            "Create a new volume: [accent]flow volume create --size 100[/accent] [dim]# size in GB[/dim]",
                            "Create a named volume: [accent]flow volume create --size 50 --name training-data[/accent]",
                            "Create file storage: [accent]flow volume create --size 200 --interface file[/accent]",
                            "Create in specific region: [accent]flow volume create --size 100 --region us-central2-a[/accent]",
                        ]
                    )
                    return

                # Build instance-to-task mapping if details requested or JSON output (for attachments)
                instance_task_map = {}
                if details or output_json:
                    try:
                        from flow.cli.ui.presentation.nomenclature import get_entity_labels

                        _assoc_msg = f"Fetching {get_entity_labels().singular} associations"
                    except Exception:  # noqa: BLE001
                        _assoc_msg = "Fetching task associations"
                    with AnimatedEllipsisProgress(console, _assoc_msg, start_immediately=True):
                        instance_task_map = self._build_instance_task_map(flow_client)

                # JSON output
                if output_json:
                    from flow.cli.utils.json_output import print_json, volume_to_json

                    items = []
                    for v in volumes:
                        attachments: list[dict[str, str]] = []
                        for inst_id in getattr(v, "attached_to", []) or []:
                            t_name, t_id = instance_task_map.get(inst_id, (None, None))
                            attachments.append(
                                {
                                    "instance_id": inst_id,
                                    **({"task_id": t_id} if t_id else {}),
                                    **({"task_name": t_name} if t_name else {}),
                                }
                            )
                        items.append(
                            volume_to_json(v, attachments=attachments if details else None)
                        )
                    print_json(items)
                    return

                # Get terminal width for responsive layout
                terminal_width = TerminalAdapter.get_terminal_width()

                # Create table with Flow standard styling
                table = create_flow_table(
                    show_borders=False,
                    expand=False,
                )  # No borders since we'll wrap in panel

                # Always show core columns: center-align everything except Name
                add_centered_column(table, "#", width=3)

                # Show additional columns based on terminal width
                show_interface = terminal_width >= 80
                show_status = terminal_width >= 90
                show_created = terminal_width >= 100

                # Move Status next to index for quick scanning
                if show_status:
                    add_centered_column(table, "Status", width=14)

                add_left_aligned_column(
                    table,
                    "Name",
                    style=theme_manager.get_color("task.name"),
                    ratio=1,  # Gets remaining space
                    overflow="ellipsis",
                    min_width=20,  # Ensure reasonable minimum
                )
                add_centered_column(
                    table,
                    "Region",
                    style=theme_manager.get_color("accent"),
                    width=15,  # Fixed width for regions like "us-central1-b"
                    overflow="crop",  # Never wrap
                )
                add_centered_column(
                    table,
                    "Size\n(GB)",
                    width=10,  # Enough for header and values like "10000"
                )

                if show_interface:
                    add_centered_column(
                        table,
                        "Interface",
                        style=theme_manager.get_color("muted"),
                        width=9,  # Fixed for "block"/"file"
                    )
                if show_created:
                    add_right_aligned_column(
                        table,
                        "Created",
                        style=theme_manager.get_color("task.time"),
                        width=16,  # Fixed for "2025-07-29 20:32"
                    )

                # Estimate available width for the Name column to support middle truncation
                try:
                    # Fixed widths for known columns
                    used_fixed = 3  # index column '#'
                    if show_status:
                        used_fixed += 14
                    used_fixed += 15  # Region
                    used_fixed += 10  # Size (GB)
                    if show_interface:
                        used_fixed += 9
                    if show_created:
                        used_fixed += 16

                    # Number of visible columns in the table row
                    visible_cols = 4 + int(show_status) + int(show_interface) + int(show_created)

                    # Approximate inter-column spacing/padding and panel overhead
                    spacing_overhead = 2 * (visible_cols - 1) + 1
                    panel_overhead = 4
                    overhead = spacing_overhead + panel_overhead

                    # Remaining width for Name cell content
                    name_max_width = max(12, terminal_width - used_fixed - overhead)
                except Exception:  # noqa: BLE001
                    # Fallback to a sensible default when calculation fails
                    name_max_width = 24

                for idx, volume in enumerate(volumes, start=1):
                    # Format status with color
                    status_color_available = theme_manager.get_color("status.running")
                    status_color_attached = theme_manager.get_color("status.pending")
                    status = f"[{status_color_available}]● available[/{status_color_available}]"
                    task_names = []

                    if hasattr(volume, "attached_to") and volume.attached_to:
                        # Collect task names if details requested
                        if details and instance_task_map:
                            for instance_id in volume.attached_to:
                                if instance_id in instance_task_map:
                                    task_name, _ = instance_task_map[instance_id]
                                    task_names.append(task_name)

                        # Format status based on whether we have task details
                        if task_names and details:
                            # Show task names (limit to 2 for space)
                            task_list = ", ".join(task_names[:2])
                            if len(task_names) > 2:
                                task_list += f" +{len(task_names) - 2}"
                            status = (
                                f"[{status_color_attached}]● {task_list}[/{status_color_attached}]"
                            )
                        else:
                            status = f"[{status_color_attached}]● attached ({len(volume.attached_to)})[/{status_color_attached}]"

                    # Get interface type
                    interface = getattr(volume, "interface", "block")
                    if hasattr(interface, "value"):
                        interface = interface.value

                    # Use volume ID as name if no name is set
                    display_name = volume.name or volume.volume_id
                    # Middle-truncate long names so both prefix and suffix remain visible
                    try:
                        display_name = TerminalAdapter.intelligent_truncate(
                            str(display_name),
                            max_width=name_max_width,
                            priority="middle",
                            suffix="…",
                        )
                    except Exception:  # noqa: BLE001
                        # If truncation fails for any reason, keep original
                        display_name = str(display_name)

                    # Build row data based on visible columns in order: #, Status?, Name, Region, Size, Interface?, Created?
                    row_data = [str(idx)]
                    if show_status:
                        row_data.append(status)
                    row_data.append(display_name)
                    row_data.append(volume.region)
                    row_data.append(str(volume.size_gb))

                    if show_interface:
                        row_data.append(interface)
                    if show_created:
                        row_data.append(
                            volume.created_at.strftime("%Y-%m-%d %H:%M")
                            if volume.created_at
                            else "-"
                        )

                    table.add_row(*row_data)

                    # Add detail rows if requested and volume has attachments
                    if details and task_names and terminal_width >= 100:
                        for i, (instance_id, task_name) in enumerate(
                            (inst_id, instance_task_map.get(inst_id, ("Unknown", ""))[0])
                            for inst_id in volume.attached_to
                            if inst_id in instance_task_map
                        ):
                            if i >= 3:  # Limit detail rows
                                remaining = len(volume.attached_to) - 3
                                # Order: #, Status?, Name, Region, Size, Interface?, Created?
                                detail_row = [""]
                                if show_status:
                                    detail_row.append(f"[dim]+{remaining} more[/dim]")
                                detail_row += ["  └─ ...", "", ""]
                                if show_interface:
                                    detail_row.append("")
                                if show_created:
                                    detail_row.append("")
                                table.add_row(*detail_row)
                                break

                            task_id = instance_task_map[instance_id][1]
                            # Order: #, Status?, Name, Region, Size, Interface?, Created?
                            detail_row = [""]
                            if show_status:
                                detail_row.append(f"[dim]{task_id[:8]}[/dim]")
                            detail_row += [f"  └─ {task_name}", "", ""]
                            if show_interface:
                                detail_row.append("")
                            if show_created:
                                detail_row.append("")
                            table.add_row(*detail_row)

                # Save indices for quick reference
                cache = VolumeIndexCache()
                cache.save_indices(volumes)

                # Wrap in panel like flow status does
                panel_title = (
                    f"Volumes ({len(volumes)} total)"
                    if not region
                    else f"Volumes [{region}] ({len(volumes)} total)"
                )
                wrap_table_in_panel(table, panel_title, console)

                # Post-table legend and tips (mirrors flow status structure)
                # Legend + Tips in a single compact block
                dim = theme_manager.get_color("task.time")
                from flow.cli.ui.presentation.nomenclature import get_entity_labels

                labels = get_entity_labels()
                console.print(
                    f"[{dim}]Legend: available = not attached · attached = in-use (shows {labels.singular} names with --details)[/{dim}]"
                )
                try:
                    from flow.cli.ui.presentation.next_steps import (
                        render_next_steps_panel as _ns,
                    )

                    _ns(
                        console,
                        [
                            "Use index shortcuts: [accent]1[/accent],[accent]1-3[/accent],[accent]:1[/accent] (no spaces)",
                            "Re-run: [accent]flow volume list[/accent] to refresh indices",
                        ],
                        title="Tips",
                    )
                except Exception:  # noqa: BLE001
                    pass

                # Show next actions with index support
                volume_count = min(len(volumes), 5)  # Show up to 5 index examples
                index_help = f"1-{volume_count}" if volume_count > 1 else "1"

                self.show_next_actions(
                    [
                        "Create a new volume: [accent]flow volume create --size 100[/accent] [dim]# size in GB[/dim]",
                        "Create in specific region: [accent]flow volume create --size 100 --region us-central2-a[/accent]",
                        f"Delete a volume: [accent]flow volume delete <volume-name-or-id>[/accent] or [accent]flow volume delete {index_help}[/accent]",
                    ]
                )

            except AuthenticationError:
                self.handle_auth_error()
            except Exception as e:  # noqa: BLE001
                self.handle_error(e)

        return volumes_list

    def _create_command(self) -> click.Command:
        @click.command(name="create")
        @click.option("--size", "-s", type=int, help="Volume size in GB")
        @click.option("--name", "-n", help="Optional name for the volume")
        @click.option(
            "--interface",
            "-i",
            type=click.Choice(["block", "file"]),
            help="Storage interface type (block or file)",
        )
        @click.option("--region", help="Region to create the volume in")
        @click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.pass_context
        @cli_error_guard(self)
        def volumes_create(
            ctx,
            size: int | None,
            name: str | None,
            interface: str | None,
            region: str | None,
            yes: bool,
            output_json: bool,
        ):
            """Create a new volume.

            Creates a persistent storage volume that can be attached to tasks.
            You'll be prompted for missing parameters interactively.

            Examples:
                flow volumes create --size 100 --name my-data
                flow volumes create --size 50 --interface file --region us-central2-a
            """
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or sdk_factory.create_client(auto_init=True)

                # Handle non-interactive mode requirements
                if output_json or yes:
                    # Non-interactive mode: validate required parameters
                    if size is None:
                        raise click.ClickException(
                            "--size is required when not running interactively"
                        )
                    if interface is None:
                        interface = "block"
                    if region is None:
                        # Use first available region as default
                        available_regions = self._get_available_regions(flow_client, interface)
                        if available_regions:
                            region = available_regions[0]
                        else:
                            raise click.ClickException("No regions available for volume creation")

                    # Validate region is available
                    available_regions = self._get_available_regions(flow_client, interface)
                    if region not in available_regions:
                        raise click.ClickException(
                            f"Region '{region}' is not available for '{interface}' storage. "
                            f"Available regions: {', '.join(available_regions)}"
                        )

                # Create the volume using the helper
                # User invoked the command explicitly, so no need to ask if they want to create
                volume = create_volume_interactive(
                    flow_client,
                    console,
                    size=size,
                    name=name,
                    interface=interface,
                    region=region,
                    skip_confirmation=yes,  # Skip confirmation if --yes flag
                    use_step_timeline=True,  # Use StepTimeline for volumes command
                    output_json=output_json,
                )

                # If user cancelled, return early
                if volume is None:
                    return

                # Show next actions (not in JSON mode)
                if not output_json:
                    self.show_next_actions(
                        [
                            "List all volumes: [accent]flow volume list[/accent]",
                            "All sizes are specified in GB (gigabytes)",
                            "Use in task config: Add to YAML under storage.volumes",
                        ]
                    )

            except AuthenticationError:
                self.handle_auth_error()
            except Exception as e:  # noqa: BLE001
                self.handle_error(e)

        return volumes_create

    def _delete_command(self) -> click.Command:
        # Import completion function
        from flow.cli.ui.runtime.shell_completion import complete_volume_ids

        @click.command(name="delete")
        @click.argument("volume_identifier", shell_complete=complete_volume_ids)
        @click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.pass_context
        @cli_error_guard(self)
        def volumes_delete(ctx, volume_identifier: str, yes: bool, output_json: bool):
            """Delete a volume by ID, name, or 'all'.

            \b
            Examples:
                flow volume delete vol_abc123def456
                flow volume delete training-data
                flow volume delete 1
                flow volume delete all
                flow volume delete training --yes
            """
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or sdk_factory.create_client(auto_init=True)

                # Special handling for "all"
                if volume_identifier.lower() == "all":
                    volumes = flow_client.volumes.list()
                    if not volumes:
                        console.print("No volumes found.")
                        return

                    console.print(f"Found {len(volumes)} volume(s) to delete:")
                    for volume in volumes:
                        display_name = get_volume_display_name(volume)
                        console.print(f"  - {display_name}")

                    if not yes:
                        confirm = click.confirm(f"\nDelete all {len(volumes)} volume(s)?")
                        if not confirm:
                            console.print("Cancelled")
                            return

                    # Delete all volumes
                    from flow.cli.utils.step_progress import StepTimeline

                    deleted_count = 0
                    total = len(volumes)
                    timeline = StepTimeline(console, title="flow volume", title_animation="auto")
                    timeline.start()
                    step_idx = timeline.add_step(
                        f"Deleting {total} volume(s)", show_bar=True, estimated_seconds=None
                    )
                    timeline.start_step(step_idx)
                    for i, volume in enumerate(volumes):
                        volume_name = get_volume_display_name(volume)
                        try:
                            flow_client.volumes.delete(volume.volume_id)
                            deleted_count += 1
                        except Exception as e:  # noqa: BLE001
                            from rich.markup import escape

                            console.print(
                                f"[error]✗[/error] Failed to delete {volume_name}: {escape(str(e))}"
                            )
                        finally:
                            pct = (i + 1) / float(total)
                            timeline.update_active(
                                percent=pct, message=f"{i + 1}/{total} – {volume_name}"
                            )
                    timeline.complete_step(note=f"Deleted {deleted_count}/{total}")
                    timeline.finish()

                    # Invalidate volume cache after deletion
                    if deleted_count > 0:
                        try:
                            from flow.adapters.http.client import HttpClientPool

                            for http_client in HttpClientPool._clients.values():
                                if hasattr(http_client, "invalidate_volume_cache"):
                                    http_client.invalidate_volume_cache()
                        except Exception:  # noqa: BLE001
                            pass

                    if output_json:
                        from flow.cli.utils.json_output import print_json

                        print_json({"status": "deleted", "deleted_count": deleted_count})
                    else:
                        console.print(f"\nDeleted {deleted_count} volume(s)")

                else:
                    # First, attempt multi-select via indices/ranges (e.g., "1-3,5")
                    selection_ids, sel_error = parse_selection_to_volume_ids(volume_identifier)
                    if sel_error:
                        console.print(f"[error]Error:[/error] {sel_error}")
                        return

                    if selection_ids:
                        # Bulk delete selected volumes by indices
                        volumes_all = flow_client.volumes.list()
                        # Map IDs to display names when possible
                        id_to_volume = {}
                        for v in volumes_all:
                            vid = getattr(v, "volume_id", None) or getattr(v, "id", None)
                            if vid:
                                id_to_volume[str(vid)] = v

                        to_delete: list[tuple[str, str]] = []  # (id, display)
                        for vid in selection_ids:
                            vobj = id_to_volume.get(str(vid))
                            if vobj is not None:
                                to_delete.append((str(vid), get_volume_display_name(vobj)))
                            else:
                                # Fallback to raw ID if not present in current list
                                to_delete.append((str(vid), str(vid)))

                        if not to_delete:
                            console.print("No volumes match the provided selection.")
                            return

                        # Preview and confirm
                        if not output_json:
                            console.print(f"Found {len(to_delete)} volume(s) to delete:")
                            for _, disp in to_delete:
                                console.print(f"  - {disp}")

                        if not yes:
                            confirm = click.confirm(f"\nDelete {len(to_delete)} volume(s)?")
                            if not confirm:
                                console.print("Cancelled")
                                return

                        from flow.cli.utils.step_progress import StepTimeline

                        deleted_count = 0
                        total = len(to_delete)
                        timeline = StepTimeline(
                            console, title="flow volume", title_animation="auto"
                        )
                        timeline.start()
                        step_idx = timeline.add_step(
                            f"Deleting {total} volume(s)", show_bar=True, estimated_seconds=None
                        )
                        timeline.start_step(step_idx)

                        from rich.markup import escape as _escape

                        for i, (vid, disp) in enumerate(to_delete):
                            try:
                                flow_client.volumes.delete(vid)
                                deleted_count += 1
                            except Exception as e:  # noqa: BLE001
                                console.print(
                                    f"[error]✗[/error] Failed to delete {_escape(disp)}: {_escape(str(e))}"
                                )
                            finally:
                                pct = (i + 1) / float(total)
                                timeline.update_active(
                                    percent=pct, message=f"{i + 1}/{total} – {disp}"
                                )

                        timeline.complete_step(note=f"Deleted {deleted_count}/{total}")
                        timeline.finish()

                        # Invalidate volume cache after deletion
                        if deleted_count > 0:
                            try:
                                from flow.adapters.http.client import HttpClientPool

                                for http_client in HttpClientPool._clients.values():
                                    if hasattr(http_client, "invalidate_volume_cache"):
                                        http_client.invalidate_volume_cache()
                            except Exception:  # noqa: BLE001
                                pass

                        if output_json:
                            from flow.cli.utils.json_output import print_json

                            print_json(
                                {
                                    "status": "deleted",
                                    "deleted": deleted_count,
                                    "failed": total - deleted_count,
                                }
                            )
                        else:
                            if deleted_count == total:
                                console.print(f"\nDeleted {deleted_count} volume(s)")
                            else:
                                console.print(
                                    f"\nDeleted {deleted_count} volume(s); [error]{total - deleted_count} failed[/error]"
                                )
                    else:
                        # Single delete path (ID/name or single index)
                        volume, error = resolve_volume_identifier(flow_client, volume_identifier)
                        if error:
                            console.print(f"[error]Error:[/error] {error}")
                            return

                        # Get display name for confirmation
                        display_name = get_volume_display_name(volume)

                        if not yes:
                            confirm = click.confirm(f"Delete volume {display_name}?")
                            if not confirm:
                                console.print("Cancelled")
                                return

                        from flow.cli.utils.step_progress import StepTimeline

                        timeline = StepTimeline(
                            console, title="flow volume", title_animation="auto"
                        )
                        timeline.start()
                        step_idx = timeline.add_step(
                            f"Deleting volume {display_name}", show_bar=False
                        )
                        timeline.start_step(step_idx)
                        try:
                            flow_client.volumes.delete(volume.volume_id)
                            timeline.complete_step()

                            # Invalidate volume cache after successful deletion
                            try:
                                from flow.adapters.http.client import HttpClientPool

                                for http_client in HttpClientPool._clients.values():
                                    if hasattr(http_client, "invalidate_volume_cache"):
                                        http_client.invalidate_volume_cache()
                            except Exception:  # noqa: BLE001
                                pass

                        except Exception as e:
                            # Include request ID when available
                            message = str(e)
                            try:
                                req_id = getattr(e, "request_id", None)
                                if req_id:
                                    from rich.markup import escape as _escape

                                    message = f"{message}\nRequest ID: {_escape(str(req_id))}"
                            except Exception:  # noqa: BLE001
                                pass
                            timeline.fail_step(message)
                            timeline.finish()
                            raise
                        finally:
                            try:
                                timeline.finish()
                            except Exception:  # noqa: BLE001
                                pass
                        if output_json:
                            from flow.cli.utils.json_output import print_json

                            vid = getattr(volume, "volume_id", None) or getattr(volume, "id", None)
                            print_json(
                                {
                                    "status": "deleted",
                                    "id": vid,
                                    "name": getattr(volume, "name", None),
                                }
                            )
                        else:
                            console.print(f"[success]✓[/success] Volume {display_name} deleted")

                if not output_json:
                    # Show next actions
                    self.show_next_actions(
                        [
                            "List remaining volumes: [accent]flow volume list[/accent]",
                            "Create a new volume: [accent]flow volume create --size 100[/accent]",
                        ]
                    )

            except AuthenticationError:
                self.handle_auth_error()
            except Exception as e:  # noqa: BLE001
                self.handle_error(e)

        return volumes_delete

    def _delete_all_command(self) -> click.Command:
        @click.command(name="delete-all")
        @click.option("--pattern", "-p", help="Only delete volumes matching pattern")
        @click.option("--dry-run", is_flag=True, help="Show what would be deleted")
        @click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.pass_context
        @cli_error_guard(self)
        def volumes_delete_all(
            ctx, pattern: str | None, dry_run: bool, yes: bool, output_json: bool
        ):
            """Delete all volumes (with optional pattern matching)."""
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or sdk_factory.create_client(auto_init=True)
                volume_ops = VolumeOperations(flow_client)

                # Find volumes matching pattern
                matching_volumes, _ = volume_ops.find_volumes_by_pattern(pattern)

                if not matching_volumes:
                    if pattern:
                        console.print(f"No volumes found matching pattern: {pattern}")
                    else:
                        console.print("No volumes found.")
                    return

                # Show what will be deleted
                console.print(f"Found {len(matching_volumes)} volume(s) to delete:")
                for volume_str in volume_ops.format_volume_summary(matching_volumes):
                    console.print(f"  - {volume_str}")

                if dry_run:
                    console.print("\n[warning]Dry run - no volumes deleted[/warning]")
                    return

                # Confirm deletion
                if not yes:
                    confirm = click.confirm(f"\nDelete {len(matching_volumes)} volume(s)?")
                    if not confirm:
                        console.print("Cancelled")
                        return

                # Delete volumes with progress callback
                def progress_callback(result):
                    if result.success:
                        console.print(f"[success]✓[/success] Deleted {result.volume_id}")
                    else:
                        console.print(
                            f"[error]✗[/error] Failed to delete {result.volume_id}: {result.error}"
                        )

                results = volume_ops.delete_volumes(matching_volumes, progress_callback)

                # Summary
                if output_json:
                    from flow.cli.utils.json_output import print_json

                    print_json(
                        {
                            "status": "deleted",
                            "deleted": results.succeeded,
                            "failed": results.failed,
                        }
                    )
                else:
                    console.print(f"\nDeleted {results.succeeded} volume(s)")
                    if results.failed > 0:
                        console.print(f"[error]Failed to delete {results.failed} volume(s)[/error]")

                if not output_json:
                    # Show next actions
                    self.show_next_actions(
                        [
                            "List remaining volumes: [accent]flow volume list[/accent]",
                            "Create a new volume: [accent]flow volume create --size 100[/accent]",
                        ]
                    )

            except AuthenticationError:
                self.handle_auth_error()
            except Exception as e:  # noqa: BLE001
                self.handle_error(str(e))

        return volumes_delete_all


# Export command instance
command = VolumesCommand()
