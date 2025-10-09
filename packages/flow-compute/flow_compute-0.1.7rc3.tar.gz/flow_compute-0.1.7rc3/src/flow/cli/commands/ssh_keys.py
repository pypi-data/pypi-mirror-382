"""SSH key management commands for Flow CLI.

Commands to list, sync, and manage SSH keys between the local system and the
Provider's platform.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, TypedDict

import click
from rich.console import Console

import flow.sdk.factory as sdk_factory
from flow.adapters.metrics.telemetry import Telemetry
from flow.adapters.providers.builtin.mithril.domain.models import PlatformSSHKey
from flow.cli.app import OrderedDYMGroup
from flow.cli.commands.base import BaseCommand
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
from flow.cli.ui.presentation.next_steps import render_next_steps_panel
from flow.cli.ui.presentation.nomenclature import get_entity_labels
from flow.cli.ui.presentation.table_styles import create_flow_table, wrap_table_in_panel
from flow.cli.ui.runtime.shell_completion import complete_ssh_key_identifiers as _complete_ssh_keys
from flow.cli.utils.error_handling import cli_error_guard, render_auth_required_message
from flow.cli.utils.json_output import error_json, iso_z, print_json
from flow.cli.utils.ssh_key_index_cache import SSHKeyIndexCache
from flow.cli.utils.step_progress import StepTimeline
from flow.cli.utils.theme_manager import theme_manager as _tm
from flow.cli.utils.user_utils import UserInfoError, get_sanitized_username
from flow.core.keys.identity import (
    _load_all as load_all_key_metadata,
)
from flow.core.keys.identity import (
    get_local_key_private_path as _id_get_local,
)
from flow.core.keys.identity import (
    store_key_metadata,
)
from flow.core.utils.ssh_key import (
    LocalSSHKey,
    discover_local_ssh_keys,
    match_local_key_to_platform,
    normalize_public_key,
)
from flow.domain.ssh.resolver import SmartSSHKeyResolver
from flow.errors import AuthenticationError

logger = logging.getLogger(__name__)

# Constants
AUTO_KEY_PREFIX = "flow-auto-"
FLOW_PREFIX = "flow:"
PLATFORM_ID_PREFIX = "sshkey_"
AUTO_SENTINEL = "_auto_"


def truncate_platform_id(platform_id: str, max_len: int = 10) -> str:
    """Truncate platform ID for display, keeping prefix intact."""
    if not platform_id or len(platform_id) <= max_len:
        return platform_id

    # Keep the sshkey_ prefix and first few chars of the actual ID
    if platform_id.startswith("sshkey_"):
        return f"sshkey_{platform_id[7 : 7 + max_len - 7]}…"
    return f"{platform_id[: max_len - 1]}…"


def truncate_key_name(name: str, max_len: int = 26) -> str:
    """Truncate key name for consistent display using center-ellipsis.

    If the name starts with the active bullet ("● "), preserve it and
    center-truncate the remainder so the overall length does not exceed
    max_len.
    """
    if not name or len(name) <= max_len:
        return name

    ellipsis = "…"
    bullet_prefix = "● "

    # Preserve leading bullet if present
    if name.startswith(bullet_prefix):
        core = name[len(bullet_prefix) :]
        remaining_len = max_len - len(bullet_prefix)
        if remaining_len <= len(ellipsis):
            return f"{bullet_prefix}{ellipsis}"

        available = remaining_len - len(ellipsis)
        left_len = (available + 1) // 2
        right_len = available // 2

        if len(core) <= available:
            return f"{bullet_prefix}{core}"

        right_part = core[-right_len:] if right_len > 0 else ""
        return f"{bullet_prefix}{core[:left_len]}{ellipsis}{right_part}"

    # Generic center truncation
    if max_len <= len(ellipsis):
        return ellipsis

    available = max_len - len(ellipsis)
    left_len = (available + 1) // 2
    right_len = available // 2

    right_part = name[-right_len:] if right_len > 0 else ""
    return f"{name[:left_len]}{ellipsis}{right_part}"


# ============================================================================
# Helper Functions for SSH Key List Command
# ============================================================================


def _fetch_ssh_key_data(flow) -> tuple[list, list[LocalSSHKey], list[PlatformSSHKey]]:
    """Fetch SSH key data from config, local system, and platform.

    Returns:
        tuple: (configured_keys, local_keys, platform_keys)
    """
    configured_keys = flow.config.provider_config.get("ssh_keys", [])
    local_keys = discover_local_ssh_keys()

    # Get platform keys via provider
    raw_keys = flow.list_platform_ssh_keys()
    platform_keys = [PlatformSSHKey.from_api(rk) for rk in raw_keys]

    return configured_keys, local_keys, platform_keys


class EnrichedKeyMapping(TypedDict):
    """Result of enriching and mapping local SSH keys with platform data.

    Attributes:
        user_keys: List of (name, path) tuples for user-provided keys
        auto_keys: List of (name, path) tuples for auto-generated keys
        key_tuple_to_platform: Maps (key_name, path_str) tuples to platform_id strings
    """

    user_keys: list[tuple[str, Path]]
    auto_keys: list[tuple[str, Path]]
    key_tuple_to_platform: dict[tuple[str, str], str]


def _enrich_and_map_keys(
    local_keys: list[LocalSSHKey],
    platform_keys: list[PlatformSSHKey],
    metadata: dict[str, Any],
) -> EnrichedKeyMapping:
    """Enrich local keys with platform data and create mappings.

    This consolidates key enrichment and platform mapping into a single pass:
    1. Starts with raw filesystem scan (e.g., "id_ed25519")
    2. Uses metadata to enrich with platform names and build platform_id mappings
    3. Does cryptographic matching (pubkey/fingerprint) for any unmapped keys
    4. Categorizes into user_keys vs auto_keys for display

    Args:
        local_keys: List of LocalSSHKey objects from discover_local_ssh_keys()
        platform_keys: List of PlatformSSHKey objects from platform API
        metadata: Metadata dict from ~/.flow/ identity store

    Returns:
        EnrichedKeyMapping with:
            - user_keys: List of (name, path) tuples for user keys (enriched names)
            - auto_keys: List of (name, path) tuples for auto-generated keys (enriched names)
            - key_tuple_to_platform: Dict mapping (name, path) -> platform_id

    Example:
        Input:  local_keys=[("id_ed25519", Path)]
        Output: {"user_keys": [("production-key", Path), ("staging-key", Path)],
                 "key_tuple_to_platform": {("production-key", "..."): "sshkey_111", ...},
                 ...}
    """

    user_keys = []
    auto_keys = []
    key_tuple_to_platform = {}

    # Phase 1: Enrich keys using metadata (authoritative source)
    # ============================================================
    # Metadata provides: platform names, platform IDs, auto-generated flags
    # This replaces generic filenames with meaningful platform names

    # Track which file paths we've processed (one file can have multiple platform IDs)
    metadata_processed_paths = set()

    # Initially categorize scanned keys by prefix (will be replaced by metadata)
    scanned_user_keys = []
    scanned_auto_keys = []
    for key_pair in local_keys:
        if key_pair.name.startswith(AUTO_KEY_PREFIX):
            scanned_auto_keys.append((key_pair.name, key_pair.private_key_path))
        else:
            scanned_user_keys.append((key_pair.name, key_pair.private_key_path))

    # Build a set of valid platform IDs for validation
    platform_key_ids = {k.fid for k in platform_keys}

    # Process metadata to enrich names and build platform mappings
    for platform_id, info in metadata.items():
        if not isinstance(info, dict) or "private_key_path" not in info:
            continue

        private_path = Path(info["private_key_path"])
        file_exists = private_path.exists()

        # Normalize path for consistent comparison (only if file exists)
        if file_exists:
            private_path = private_path.resolve()

        path_str = str(private_path)
        key_name = info.get("key_name", private_path.stem)
        is_auto = info.get("auto_generated", False) or key_name.startswith(AUTO_KEY_PREFIX)

        # Remove scanned entries for this path (only if file exists and once per unique file)
        if file_exists and path_str not in metadata_processed_paths:
            scanned_user_keys = [(n, p) for n, p in scanned_user_keys if str(p) != path_str]
            scanned_auto_keys = [(n, p) for n, p in scanned_auto_keys if str(p) != path_str]
            metadata_processed_paths.add(path_str)

        # Add enriched entry with platform name (even if file doesn't exist - for visibility)
        if is_auto:
            display_name = (
                f"{FLOW_PREFIX}{key_name}" if not key_name.startswith(FLOW_PREFIX) else key_name
            )
            auto_keys.append((display_name, private_path))
        else:
            user_keys.append((key_name, private_path))

        # Exclude stale metadata from platform mappings
        # ===============================================
        # When keys are deleted from the platform, their local metadata persists.
        # We must exclude these stale platform_ids from key_tuple_to_platform to
        # prevent incorrectly indicating platform presence.
        #
        # The key is still displayed (added to lists above) but without a platform
        # mapping, downstream code correctly shows it as "local only" rather than
        # falsely showing it as synced to the platform.
        if platform_id in platform_key_ids:
            key_tuple_to_platform[(key_name, str(private_path))] = platform_id
        else:
            logger.debug(
                f"Key {key_name} has stale metadata (platform_id={platform_id} not on platform)"
            )

    # Phase 2: Cryptographic matching for unmapped keys
    # ==================================================
    # For keys not in metadata, try to find their platform ID using:
    # 1. Public key content matching (most reliable)
    # 2. Fingerprint matching (fallback)
    # 3. Name matching (last resort)
    # Only add these keys to the lists if they match a platform key

    for key_pair in local_keys:
        # Skip if already processed via metadata
        path_resolved = str(key_pair.private_key_path.resolve())
        if (key_pair.name, path_resolved) in key_tuple_to_platform:
            continue

        # Use shared matching utility (tries content, fingerprint, name in order)
        platform_id = match_local_key_to_platform(
            key_pair.private_key_path, platform_keys, match_by_name=True
        )

        # Record the match and add to appropriate list
        if platform_id:
            key_tuple_to_platform[(key_pair.name, path_resolved)] = platform_id

            # Add to the appropriate key list
            if key_pair.name.startswith(AUTO_KEY_PREFIX):
                display_name = (
                    f"{FLOW_PREFIX}{key_pair.name}"
                    if not key_pair.name.startswith(FLOW_PREFIX)
                    else key_pair.name
                )
                auto_keys.append((display_name, key_pair.private_key_path))
            else:
                user_keys.append((key_pair.name, key_pair.private_key_path))

    return {
        "user_keys": user_keys,
        "auto_keys": auto_keys,
        "key_tuple_to_platform": key_tuple_to_platform,
    }


def _aggregate_all_keys(
    configured_keys,
    user_keys,
    auto_keys,
    platform_keys,
    key_tuple_to_platform,
    metadata,
    show_auto,
) -> list[dict]:
    """Aggregate all keys from all sources into a unified list with computed properties.

    Returns a list of dicts with keys: key_id, name, path, platform_id, has_local,
    on_platform, is_default, is_auto, is_required.
    """
    # Build lookups
    platform_keys_by_id = {pkey.fid: pkey for pkey in platform_keys}
    required_key_ids = {pkey.fid for pkey in platform_keys if getattr(pkey, "required", False)}

    # Build set of configured platform IDs for fast lookup
    configured_platform_ids = {
        ck for ck in configured_keys if isinstance(ck, str) and ck.startswith(PLATFORM_ID_PREFIX)
    }

    # Collect all unique keys (keyed by platform_id or path)
    all_keys = {}  # key_id -> {name, path, platform_id, is_auto}

    # From user_keys (local files from metadata or matched cryptographically)
    for name, path in user_keys:
        platform_id = key_tuple_to_platform.get((name, str(path)), "")
        is_auto = name.startswith(FLOW_PREFIX) or name.startswith(AUTO_KEY_PREFIX)

        # Skip auto keys unless --show-auto
        if is_auto and not show_auto:
            continue

        # Use platform_id as key if available, otherwise use path
        key_id = platform_id if platform_id else str(path)

        if key_id not in all_keys:
            all_keys[key_id] = {
                "name": name,
                "path": path,
                "platform_id": platform_id,
                "is_auto": is_auto,
            }

    # From auto_keys (explicitly marked as auto-generated)
    if show_auto:
        for name, path in auto_keys:
            platform_id = key_tuple_to_platform.get((name, str(path)), "")
            key_id = platform_id if platform_id else str(path)

            if key_id not in all_keys:
                all_keys[key_id] = {
                    "name": name,
                    "path": path,
                    "platform_id": platform_id,
                    "is_auto": True,
                }

    # From platform_keys (keys on platform that may not have local files)
    for pkey in platform_keys:
        is_auto = getattr(pkey, "name", "").startswith(AUTO_KEY_PREFIX)

        # Skip auto keys unless --show-auto
        if is_auto and not show_auto:
            continue

        if pkey.fid not in all_keys:
            all_keys[pkey.fid] = {
                "name": getattr(pkey, "name", pkey.fid),
                "path": None,  # No local file
                "platform_id": pkey.fid,
                "is_auto": is_auto,
            }

    # From configured_keys (ensure configured keys always show, even if missing)
    for ck in configured_keys:
        if (
            isinstance(ck, str)
            and ck.startswith(PLATFORM_ID_PREFIX)
            # This is a platform ID - check if it's already in all_keys or metadata
            and ck not in all_keys
        ):
            # Check if this platform_id is in metadata (key might be local but deleted from platform)
            metadata_info = metadata.get(ck, {})
            local_path = None
            key_name = ck

            if metadata_info and "private_key_path" in metadata_info:
                # This configured platform_id has local metadata (key was once on platform)
                # The key may still exist locally even if deleted from platform
                local_path = Path(metadata_info["private_key_path"])
                key_name = metadata_info.get("key_name", ck)

                # Check for duplicate entry: if we already added this key by its path
                # (from user_keys processing), we need to merge it with this config entry
                # to avoid showing the same key twice (once by path, once by platform_id)
                path_key = str(local_path)
                if path_key in all_keys:
                    # Merge: add the platform_id to the existing path-based entry
                    # This ensures the entry is marked as "default" and has platform info
                    all_keys[path_key]["platform_id"] = ck
                    continue  # Skip creating a duplicate entry

            # Key is configured but missing from both local and platform (or not yet in all_keys)
            all_keys[ck] = {
                "name": key_name,
                "path": local_path,
                "platform_id": ck,
                "is_auto": False,
            }
        # Note: local path configured keys are already in all_keys from user_keys

    # Compute display properties for each key
    rows = []
    for key_id, key_info in all_keys.items():
        # Compute three column booleans
        has_local = False
        if key_info["path"]:
            path_obj = (
                key_info["path"]
                if isinstance(key_info["path"], Path)
                else Path(str(key_info["path"]))
            )
            has_local = path_obj.exists()

        # Check if key actually exists on platform (not just has a platform_id)
        on_platform = (
            key_info["platform_id"] in platform_keys_by_id if key_info["platform_id"] else False
        )
        is_default = (
            key_info["platform_id"] in configured_platform_ids if key_info["platform_id"] else False
        )

        # Get display name - prefer platform name when key exists on platform
        if on_platform:
            platform_key = platform_keys_by_id[key_info["platform_id"]]
            display_name = getattr(platform_key, "name", key_info["name"])
        else:
            display_name = key_info["name"]

        if key_info["is_auto"]:
            # Strip flow: prefix for display
            display_name = display_name.replace(FLOW_PREFIX, "")

        # Check if required
        is_required = (
            key_info["platform_id"] in required_key_ids if key_info["platform_id"] else False
        )

        rows.append(
            {
                "key_id": key_id,
                "name": display_name,
                "path": key_info["path"],
                "platform_id": key_info["platform_id"],
                "has_local": has_local,
                "on_platform": on_platform,
                "is_default": is_default,
                "is_auto": key_info["is_auto"],
                "is_required": is_required,
            }
        )

    # Sort (default keys first, then local keys, then platform-only, all alphabetically)
    rows.sort(key=lambda r: (not r["is_default"], not r["has_local"], r["name"].lower()))

    return rows


def _render_json_output(
    configured_keys,
    user_keys,
    auto_keys,
    platform_keys,
    key_tuple_to_platform,
    metadata,
    show_auto,
) -> None:
    """Render JSON output for automation."""
    # Aggregate all keys using shared logic
    all_keys = _aggregate_all_keys(
        configured_keys,
        user_keys,
        auto_keys,
        platform_keys,
        key_tuple_to_platform,
        metadata,
        show_auto,
    )

    # Convert to simple output format
    output = []
    for key in all_keys:
        output.append(
            {
                "id": key["platform_id"],
                "name": key["name"],
                "local_path": str(key["path"]) if key["path"] else None,
                "is_local": key["has_local"],
                "is_platform": key["on_platform"],
                "is_default": key["is_default"],
            }
        )

    print_json(output)


def _compute_statistics(
    configured_keys, user_keys, platform_keys, key_tuple_to_platform
) -> tuple[int, int]:
    """Compute statistics about local-only and platform-only keys.

    Returns:
        tuple: (local_only_count, platform_only_count)
    """
    local_platform_ids = set(key_tuple_to_platform.values())
    # Count local-only keys (not uploaded)
    local_only_count = 0
    for key_reference in configured_keys:
        if not isinstance(key_reference, str) or key_reference.startswith(PLATFORM_ID_PREFIX):
            continue

        p = Path(key_reference).expanduser().resolve()
        has_platform = any(
            pid for (name, path), pid in key_tuple_to_platform.items() if path == str(p)
        )
        if p.exists() and not has_platform:
            local_only_count += 1

    # Add user keys not in config and not on platform
    for name, path in user_keys:
        if not key_tuple_to_platform.get((name, str(path)), ""):
            local_only_count += 1

    # Count platform-only keys (missing locally)
    platform_only_count = sum(1 for pkey in platform_keys if pkey.fid not in local_platform_ids)

    return local_only_count, platform_only_count


def _sync_keys_to_platform(console, user_keys, key_tuple_to_platform, ssh_key_manager) -> int:
    """Sync local user keys to platform.

    Returns:
        int: Number of keys synced
    """
    from rich.text import Text

    synced_count = 0
    timeline = None

    try:
        timeline = StepTimeline(console, title="flow ssh-key", title_animation="auto")
        timeline.start()
        idx_sync = timeline.add_step("Uploading SSH keys", show_bar=True)
        timeline.start_step(idx_sync)

        # Show interrupt hint
        accent = _tm.get_color("accent")
        hint = Text()
        hint.append("  Press ")
        hint.append("Ctrl+C", style=accent)
        hint.append(" to stop syncing. Keys already uploaded remain on platform.")
        timeline.set_active_hint_text(hint)
    except Exception:  # noqa: BLE001
        logger.debug("Failed to initialize timeline", exc_info=True)
        timeline = None

    try:
        for name, path in user_keys:
            pub_path = path.with_suffix(".pub")
            if not pub_path.exists():
                continue

            # Check if already synced
            if (name, str(path)) in key_tuple_to_platform:
                console.print(f"  - {name} already synced")
                continue

            try:
                result = ssh_key_manager.get_or_create_key_if_file_path([str(path)])
                if result:
                    console.print(f"  ✓ Uploaded {name}")
                    synced_count += 1
            except Exception as e:  # noqa: BLE001
                from rich.markup import escape

                console.print(f"  ✗ Failed to upload {name}: {escape(str(e))}")
                logger.debug(f"Upload failed for {name}", exc_info=True)
    finally:
        if timeline is not None:
            timeline.complete_step()
            timeline.finish()

    return synced_count


def _render_table_output(
    console,
    configured_keys,
    user_keys,
    auto_keys,
    platform_keys,
    key_tuple_to_platform,
    metadata,
    show_auto,
    verbose,
) -> tuple[int, list[dict[str, str]]]:
    """Render the SSH keys table.

    Returns:
        tuple: (default_key_count, displayed_refs)
    """

    # Helper functions
    def checkmark(is_true: bool) -> str:
        return "[success]✓[/success]" if is_true else "[dim]-[/dim]"

    def default_dot(is_default: bool) -> str:
        return "●" if is_default else ""

    # Create table
    table = create_flow_table(show_borders=False, expand=False)
    table.add_column("#", style="white", width=4, header_style="bold white", justify="right")
    table.add_column("Name", style="white", width=26, header_style="bold white", justify="left")
    table.add_column("Local", style="white", width=8, header_style="bold white", justify="center")
    table.add_column(
        "Platform", style="white", width=10, header_style="bold white", justify="center"
    )
    table.add_column("Default", style="white", width=8, header_style="bold white", justify="center")
    if verbose:
        table.add_column(
            "ID",
            style=_tm.get_color("warning"),
            width=14,
            header_style="bold white",
            justify="left",
        )

    # Use shared aggregation logic
    rows_to_display = _aggregate_all_keys(
        configured_keys,
        user_keys,
        auto_keys,
        platform_keys,
        key_tuple_to_platform,
        metadata,
        show_auto,
    )

    # Display all rows
    default_key_count = 0
    displayed_refs: list[dict[str, str]] = []

    for row_index, row in enumerate(rows_to_display, start=1):
        # Build display name with annotations
        display_name = truncate_key_name(row["name"])
        if row["is_required"]:
            display_name = f"{display_name} [dim](required)[/dim]"

        # Style for auto keys
        if row["is_auto"]:
            name_col = f"[dim]{display_name}[/dim]"
            local_col = f"[dim]{checkmark(row['has_local'])}[/dim]"
            platform_col = f"[dim]{checkmark(row['on_platform'])}[/dim]"
            default_col = f"[dim]{default_dot(row['is_default'])}[/dim]"
        else:
            name_col = display_name
            local_col = checkmark(row["has_local"])
            platform_col = checkmark(row["on_platform"])
            default_col = default_dot(row["is_default"])

        # Build table row
        table_row = [str(row_index), name_col, local_col, platform_col, default_col]
        if verbose:
            platform_id_display = (
                truncate_platform_id(row["platform_id"]) if row["platform_id"] else ""
            )
            if row["is_auto"]:
                platform_id_display = f"[dim]{platform_id_display}[/dim]"
            table_row.append(platform_id_display)

        table.add_row(*table_row)

        # Track for index cache
        if row["platform_id"]:
            displayed_refs.append({"ref": row["platform_id"], "type": "platform_id"})
        else:
            displayed_refs.append({"ref": str(row["path"]), "type": "local"})

        # Count defaults
        if row["is_default"]:
            default_key_count += 1

    # Display table
    wrap_table_in_panel(table, "SSH Keys", console)

    # Save indices for quick reference
    SSHKeyIndexCache().save_indices(displayed_refs)

    return default_key_count, displayed_refs


@click.command()
@click.option("--sync", is_flag=True, hidden=True, help="Upload local SSH keys to platform")
@click.option("--show-auto", is_flag=True, help="Show auto-generated keys (hidden by default)")
@click.option("--legend", is_flag=True, help="Show a legend explaining columns and icons")
@click.option("--verbose", "-v", is_flag=True, help="Show file paths and detailed information")
@click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
def list(sync: bool, show_auto: bool, legend: bool, verbose: bool, output_json: bool) -> None:
    """List SSH keys and their state in a simplified, intuitive view.

    \b
    Common Workflows:
      1. Check default keys:
         $ flow ssh-key list                # Default keys show ● in the Default column
    \b
      2. Clean up unused keys:
         $ flow ssh-key list --show-auto    # Include auto-generated keys
         $ flow ssh-key delete sshkey_XXX   # Remove from platform
    """
    try:
        console = _tm.create_console()
    except Exception:  # noqa: BLE001
        console = Console()

    # Fetch data with progress indicator (skip in JSON mode)
    try:
        if output_json:
            flow = sdk_factory.create_client(auto_init=True)
            configured_keys, local_keys, platform_keys = _fetch_ssh_key_data(flow)
        else:
            with AnimatedEllipsisProgress(console, "Loading SSH keys", start_immediately=True):
                flow = sdk_factory.create_client(auto_init=True)
                configured_keys, local_keys, platform_keys = _fetch_ssh_key_data(flow)
    except AuthenticationError:
        render_auth_required_message(console, output_json=output_json)
        return

    # Load metadata and enrich keys with platform data
    metadata = load_all_key_metadata()

    # Single consolidated pass: enrich names, categorize, and build platform mappings
    enriched = _enrich_and_map_keys(local_keys, platform_keys, metadata)
    user_keys = enriched["user_keys"]
    auto_keys = enriched["auto_keys"]
    key_tuple_to_platform = enriched["key_tuple_to_platform"]

    # JSON output (early return)
    if output_json:
        _render_json_output(
            configured_keys,
            user_keys,
            auto_keys,
            platform_keys,
            key_tuple_to_platform,
            metadata,
            show_auto,
        )
        Telemetry().log_event(
            "ssh_keys.get",
            {"sync": sync, "show_auto": show_auto, "legend": legend, "verbose": verbose},
        )
        return

    # Show initial explanation if no keys configured
    if not configured_keys:
        labels = get_entity_labels()
        console.print(
            f"\n[warning]ℹ️  No SSH keys configured for Flow {labels.empty_plural}.[/warning]"
        )
        if user_keys:
            console.print("   You have local SSH keys that can be used.")
        console.print()

    # Render table
    default_key_count, displayed_refs = _render_table_output(
        console,
        configured_keys,
        user_keys,
        auto_keys,
        platform_keys,
        key_tuple_to_platform,
        metadata,
        show_auto,
        verbose,
    )

    # Compute and display statistics
    local_only_count, platform_only_count = _compute_statistics(
        configured_keys, user_keys, platform_keys, key_tuple_to_platform
    )

    if default_key_count > 0:
        labels = get_entity_labels()
        console.print(
            f"\n[success]✓ {default_key_count} key{'s' if default_key_count > 1 else ''} default for Flow {labels.empty_plural}.[/success]"
        )

    if local_only_count or platform_only_count:
        parts = []
        if local_only_count:
            parts.append(
                f"{local_only_count} local key{'s' if local_only_count != 1 else ''} need upload"
            )
        if platform_only_count:
            parts.append(
                f"{platform_only_count} platform key{'s' if platform_only_count != 1 else ''} missing locally"
            )
        console.print(f"[warning]! {'; '.join(parts)}.[/warning]")

    if auto_keys and not show_auto:
        console.print(
            f"[dim]ℹ {len(auto_keys)} auto-generated key{'s' if len(auto_keys) != 1 else ''} hidden. Use --show-auto to show.[/dim]"
        )

    # Show helpful tips
    from flow.cli.ui.presentation.next_steps import render_next_steps_panel as _ns

    tips: list[str] = [
        "flow ssh-key info 1",
        "flow ssh-key delete 1",
    ]

    # Suggest linking unmapped platform IDs
    platform_keys_by_id = {pkey.fid: pkey for pkey in platform_keys}
    unmapped_ids = [
        key_reference
        for key_reference in configured_keys
        if isinstance(key_reference, str)
        and key_reference.startswith(PLATFORM_ID_PREFIX)
        and key_reference not in platform_keys_by_id
        and _id_get_local(key_reference) is None
    ]
    if unmapped_ids:
        tips.insert(0, f"flow ssh-key link {unmapped_ids[0]} ~/.ssh/id_ed25519")

    render_next_steps_panel(console, tips, title="Tips")

    if legend:
        console.print(
            "\n[dim]Legend:[/dim]\n"
            "[dim]- Local: ✓ present on this machine (private key exists)[/dim]\n"
            "[dim]- Platform: ✓ uploaded to current provider (public key on platform)[/dim]\n"
            "[dim]- Default: ● default keys for new tasks when none specified (listed in ~/.flow/config.yaml)[/dim]\n"
            "[dim]- History: 'flow ssh-key info <key>' shows past launches (may be empty even if Active)[/dim]"
        )

    # Sync keys if requested
    if sync:
        console.print("\n[bold]Syncing local keys to platform...[/bold]")
        try:
            ssh_key_manager = flow.get_ssh_key_manager()
        except AttributeError:
            console.print("[warning]SSH key management not supported by current provider[/warning]")
            return

        synced_count = _sync_keys_to_platform(
            console, user_keys, key_tuple_to_platform, ssh_key_manager
        )

        if synced_count > 0:
            console.print(
                f"\n[success]Synced {synced_count} key{'s' if synced_count != 1 else ''}[/success]"
            )
        else:
            console.print("\n[warning]All user keys already synced[/warning]")

    # Show actionable next steps if no keys configured
    if not configured_keys:
        console.print("\n[warning]⚠️  No SSH keys configured for Flow tasks[/warning]")

        synced_user_keys = [(n, p) for n, p in user_keys if (n, str(p)) in key_tuple_to_platform]

        if synced_user_keys:
            name, path = synced_user_keys[0]
            platform_id = key_tuple_to_platform[(name, str(path))]
            console.print("\n[dim]Add to ~/.flow/config.yaml:[/dim]")
            console.print(f"[dim]ssh_keys:\n  - {platform_id}[/dim]")
        elif user_keys:
            try:
                from flow.cli.ui.presentation.next_steps import render_next_steps_panel as _ns

                _ns(console, ["flow ssh-key list"], title="Next steps")
            except Exception:  # noqa: BLE001
                console.print("\nNext: [accent]flow ssh-key upload[/accent] to upload your keys")
        else:
            render_next_steps_panel(console, ["ssh-keygen -t ed25519"], title="Next steps")

    Telemetry().log_event(
        "ssh_keys.get", {"sync": sync, "show_auto": show_auto, "legend": legend, "verbose": verbose}
    )


# ============================================================================
# SSH Key Info/Details Command - Helper Functions
# ============================================================================


class KeyLookupResult(TypedDict):
    """Result of looking up a key across all sources."""

    platform_key: PlatformSSHKey | None  # Key object if exists on platform
    platform_id: str | None  # Platform ID (from metadata, config, or platform)
    local_path: Path | None  # Local private key path
    display_name: str  # Name to show in UI
    is_configured: bool  # In config.yaml
    in_metadata: bool  # Has entry in metadata.json


def _resolve_key_lookup(key_id: str, flow, ssh_key_manager, console) -> KeyLookupResult | None:
    """Resolve user input and fetch all relevant key data.

    Returns None if index resolution fails (early exit with error shown).
    """
    from pathlib import Path as _Path

    # Step 1: Handle index lookup
    resolved_id = key_id
    local_path_hint = None

    if key_id.isdigit() or key_id.startswith(":"):
        ref, err = SSHKeyIndexCache().resolve_index(key_id)
        if err:
            console.print(f"\n[error]{err}[/error]")
            try:
                render_next_steps_panel(
                    console,
                    [
                        "flow ssh-key list  [muted]— refresh indices[/muted]",
                        "Use index shortcuts: [accent]:N[/accent] or [accent]N[/accent]",
                    ],
                    title="Tips",
                )
            except Exception:  # noqa: BLE001
                console.print("[dim]Tip: Re-run 'flow ssh-key list' to refresh indices[/dim]")
            return None

        if ref:
            rtype = ref.get("type")
            rval = ref.get("ref", "")
            if rtype == "platform_id" or (isinstance(rval, str) and rval.startswith("sshkey_")):
                resolved_id = rval
            elif rtype == "local":
                lp = _Path(rval).expanduser().resolve()
                if lp.exists():
                    local_path_hint = lp
                    resolved_id = lp.stem

    # Step 2: Fetch platform keys (with error handling)
    platform_keys = []
    try:
        raw = flow.list_platform_ssh_keys()
        platform_keys = [PlatformSSHKey.from_api(rk) for rk in raw]
    except Exception as e:  # noqa: BLE001
        logger.debug(f"Failed to fetch platform keys: {e}")
        if ssh_key_manager:
            platform_keys = ssh_key_manager.list_keys()

    platform_keys_by_id = {k.fid: k for k in platform_keys}

    # Step 3: Load metadata and config
    metadata = load_all_key_metadata()
    configured_keys = flow.config.provider_config.get("ssh_keys", [])

    # Step 4: Find the key
    platform_key = None
    platform_id = None
    local_path = local_path_hint
    display_name = resolved_id

    # Try direct platform ID match
    if resolved_id.startswith("sshkey_"):
        platform_key = platform_keys_by_id.get(resolved_id)
        platform_id = resolved_id
        if platform_key:
            display_name = getattr(platform_key, "name", resolved_id)

    # Try metadata lookup (by name or ID)
    if not platform_key:
        for pid, meta in metadata.items():
            if meta.get("key_name") == resolved_id or pid == resolved_id:
                platform_id = pid
                display_name = meta.get("key_name", resolved_id)
                platform_key = platform_keys_by_id.get(pid)
                if "private_key_path" in meta:
                    p = _Path(meta["private_key_path"])
                    if p.exists():
                        local_path = p
                break

    # Try platform name match
    if not platform_key:
        matches = [k for k in platform_keys if getattr(k, "name", "") == resolved_id]
        if len(matches) == 1:
            platform_key = matches[0]
            platform_id = platform_key.fid
            display_name = platform_key.name
        elif len(matches) > 1:
            console.print(f"\n[warning]Multiple keys found with name '{resolved_id}':[/warning]")
            for m in matches[:10]:
                console.print(f"  • {m.name} ({m.fid})")
            console.print("\n[dim]Please use the platform ID (sshkey_xxx)[/dim]")
            return None

    # Try local key resolution
    if not platform_key and ssh_key_manager:
        local_resolver = SmartSSHKeyResolver(ssh_key_manager)
        resolved_path = local_resolver.resolve_ssh_key(resolved_id)
        if resolved_path and resolved_path.exists():
            local_path = resolved_path
            display_name = resolved_path.stem
            # Try to match to platform by content
            if local_path:
                pub_path = local_path.with_suffix(".pub")
                if pub_path.exists():
                    for pk in platform_keys:
                        matched_id = match_local_key_to_platform(
                            local_path, [pk], match_by_name=True
                        )
                        if matched_id:
                            platform_key = pk
                            platform_id = pk.fid
                            break

    # Step 5: Try to find local path if we have platform key but no path yet
    if platform_key and not local_path:
        # Check identity store
        mapped = _id_get_local(platform_key.fid)
        if mapped and mapped.exists():
            local_path = mapped
        else:
            # Try cryptographic matching
            local_keys = discover_local_ssh_keys()
            for lk in local_keys:
                matched_id = match_local_key_to_platform(
                    lk.private_key_path, [platform_key], match_by_name=True
                )
                if matched_id:
                    local_path = lk.private_key_path
                    break

    # Step 6: Check if configured
    is_configured = False
    if platform_id:
        is_configured = platform_id in configured_keys
    elif local_path:
        is_configured = str(local_path) in configured_keys or display_name in configured_keys

    return {
        "platform_key": platform_key,
        "platform_id": platform_id,
        "local_path": local_path,
        "display_name": display_name,
        "is_configured": is_configured,
        "in_metadata": platform_id in metadata if platform_id else False,
    }


def _render_key_details(result: KeyLookupResult, console, flow, verbose: bool) -> None:
    """Render details for a key that exists on platform."""
    from rich.panel import Panel
    from rich.table import Table

    key = result["platform_key"]
    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column(style="bold")
    info_table.add_column()

    info_table.add_row("Platform ID", key.fid)
    info_table.add_row("Name", result["display_name"])
    if hasattr(key, "created_at") and key.created_at:
        info_table.add_row("Created", str(key.created_at))

    if result["local_path"]:
        info_table.add_row("Local key", str(result["local_path"]))
    else:
        info_table.add_row("Local key", "[dim]Not found[/dim]")

    if result["is_configured"]:
        info_table.add_row("Status", "[success]● Default[/success] (in ~/.flow/config.yaml)")
    elif getattr(key, "required", False):
        info_table.add_row("Status", "[warning]Required[/warning] (project setting)")
    else:
        info_table.add_row("Status", "Available")

    console.print(Panel(info_table, title="SSH Key Details", border_style="dim"))

    # Show tasks
    console.print("\n[bold]Tasks launched with this key:[/bold]")
    try:
        init_interface = flow.get_provider_init()
        records = init_interface.list_tasks_by_ssh_key(key.fid, limit=20)
        if records:
            for rec in records[:10]:
                console.print(
                    f"  • {rec.get('name') or rec.get('task_id')}  "
                    f"[{rec.get('status', '?')}]  {rec.get('instance_type', '')}  {iso_z(rec.get('created_at'))}"
                )
        else:
            console.print("No tasks found using this key")
    except Exception as e:  # noqa: BLE001
        logger.debug(f"Failed to list tasks: {e}")
        console.print("No tasks found using this key")

    # Configuration hint
    if not result["is_configured"]:
        console.print("\n[dim]To use this key, add it to ~/.flow/config.yaml:[/dim]")
        console.print(f"[dim]ssh_keys:\n  - {key.fid}[/dim]")
        console.print(
            f"[dim]Command (with yq): yq -i '.ssh_keys += [\"{key.fid}\"]' ~/.flow/config.yaml[/dim]"
        )
        console.print(
            f"[dim]Fallback (append): printf '\\nssh_keys:\\n  - {key.fid}\\n' >> ~/.flow/config.yaml[/dim]"
        )


def _render_deleted_key(result: KeyLookupResult, console) -> None:
    """Render details for a key that was deleted from platform."""
    from rich.panel import Panel
    from rich.table import Table

    t = Table(show_header=False, box=None, expand=False)
    t.add_column("f1", style="muted")
    t.add_column("f2")
    t.add_row("ID", result["platform_id"])
    t.add_row("Configured", "yes" if result["is_configured"] else "no")

    if result["local_path"]:
        t.add_row("Local key", str(result["local_path"]))
    else:
        t.add_row("Local key", "unknown")

    if result["in_metadata"]:
        t.add_row("Platform", "[warning]⚠ No longer on platform[/warning]")
        t.add_row("", "[dim]Key was deleted or removed from platform[/dim]")
    else:
        t.add_row("Platform", "[dim]Not found[/dim]")

    console.print(Panel(t, title="SSH Key", border_style="dim"))

    # Next steps
    if result["in_metadata"] and result["local_path"]:
        next_steps = [
            "flow ssh-key upload       [muted]— re-upload this key to platform[/muted]",
            "flow ssh-key list -v      [muted]— verify platform ID[/muted]",
        ]
    else:
        next_steps = [
            "flow ssh-key list         [muted]— upload local keys[/muted]",
            "flow ssh-key list -v      [muted]— verify platform ID[/muted]",
        ]

    render_next_steps_panel(console, next_steps, title="Next steps")
    console.print("\n[dim]Tip: Run 'flow ssh-key list' to re-upload this key[/dim]")


def _render_local_only_key(result: KeyLookupResult, console) -> None:
    """Render details for a local-only key."""
    from rich.panel import Panel
    from rich.table import Table

    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column(style="bold")
    info_table.add_column()

    info_table.add_row("Name", result["display_name"])
    info_table.add_row("Local key", str(result["local_path"]))
    info_table.add_row("Platform", "[dim]Not uploaded[/dim]")

    if result["is_configured"]:
        info_table.add_row("Status", "[success]● Default[/success] (in ~/.flow/config.yaml)")

    console.print(Panel(info_table, title="SSH Key (Local Only)", border_style="dim"))

    try:
        render_next_steps_panel(
            console,
            [
                "flow ssh-key upload  [muted]— upload this key to platform[/muted]",
                f"flow ssh-key set-default {result['display_name']}  [muted]— make default[/muted]",
            ],
            title="Next steps",
        )
    except Exception:  # noqa: BLE001
        console.print("\n[dim]Tip: Run 'flow ssh-key upload' to upload this key[/dim]")


def _render_not_found(key_id: str, console) -> None:
    """Render error for key not found."""
    console.print(f"\n[error]SSH key '{key_id}' not found[/error]")
    try:
        render_next_steps_panel(
            console,
            [
                "flow ssh-key list -v  [muted]— show platform IDs[/muted]",
                "flow ssh-key info <sshkey_ID>",
            ],
            title="Tips",
        )
    except Exception:  # noqa: BLE001
        console.print("[dim]Tip: Run 'flow ssh-key list -v' to see platform IDs[/dim]")


@click.command()
@click.argument("key_reference", shell_complete=_complete_ssh_keys)
@click.option("--verbose", "-v", is_flag=True, help="Show full public key")
def details(key_reference: str, verbose: bool) -> None:
    """Show detailed information about an SSH key.

    KEY_REFERENCE: Platform SSH key ID (e.g., sshkey_abc123), key name, or an index (N or :N) from the last 'flow ssh-key list' output

    Shows:
    - Key metadata (name, creation date)
    - Tasks that launched with this key
    - Local key mapping
    """
    try:
        console = _tm.create_console()
    except Exception:  # noqa: BLE001
        console = Console()

    try:
        try:
            Telemetry().log_event("ssh_keys.describe", {"verbose": verbose})
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Failed to log telemetry: {e}")

        # Initialize Flow client and manager
        flow = sdk_factory.create_client(auto_init=True)
        try:
            ssh_key_manager = flow.get_ssh_key_manager()
        except AttributeError:
            ssh_key_manager = None

        # Phase 1: Resolve and fetch key data
        with AnimatedEllipsisProgress(console, "Fetching SSH key details"):
            result = _resolve_key_lookup(key_reference, flow, ssh_key_manager, console)
            if result is None:
                return  # Error already shown

        # Phase 2: Determine key state and render appropriate output
        if result["platform_key"]:
            # Key exists on platform
            _render_key_details(result, console, flow, verbose)
        elif result["platform_id"] and (result["is_configured"] or result["in_metadata"]):
            # Key was deleted from platform
            _render_deleted_key(result, console)
        elif result["local_path"]:
            # Local-only key
            _render_local_only_key(result, console)
        else:
            # Not found
            _render_not_found(key_reference, console)

    except AuthenticationError:
        render_auth_required_message(console)
        raise click.exceptions.Exit(1)
    except Exception as e:
        from rich.markup import escape

        console.print(f"[error]Error: {escape(str(e))}[/error]")
        raise click.ClickException(str(e)) from e


@click.command()
@click.argument("key_reference", shell_complete=_complete_ssh_keys)
@click.option("--unset", is_flag=True, help="Unset required (make key optional)")
def require(key_reference: str, unset: bool) -> None:
    """Mark an SSH key as required (admin only).

    KEY_REFERENCE: Platform SSH key ID (e.g., sshkey_abc123) or key name

    Requires project admin privileges. When a key is required, Mithril expects
    it to be included in launches for the project. Flow also auto-includes
    required keys during launches.
    """
    try:
        console = _tm.create_console()
    except Exception:  # noqa: BLE001
        console = Console()

    try:
        flow = sdk_factory.create_client(auto_init=True)
        try:
            ssh_key_manager = flow.get_ssh_key_manager()
        except AttributeError:
            console.print("[warning]SSH key management not supported by current provider[/warning]")
            return

        # Validate key exists - try by FID first, then by name
        logger.debug(f"Looking up SSH key: {key_reference}")
        key = ssh_key_manager.get_key(key_reference)

        if not key:
            logger.debug(f"Key not found by FID, trying by name: {key_reference}")
            key = ssh_key_manager.find_key_by_name(key_reference)

        if not key:
            logger.debug("Key not found by FID or name. Listing all keys:")
            all_keys = ssh_key_manager.list_keys()
            for k in all_keys:
                logger.debug(f"  - FID: {k.fid}, Name: {k.name}")

            # Check if the key exists in local metadata but not on platform (stale metadata)
            metadata = load_all_key_metadata()
            stale_key_found = False
            stale_platform_id = None

            for platform_id, info in metadata.items():
                if isinstance(info, dict):
                    stored_name = info.get("key_name", "")
                    if stored_name == key_reference or platform_id == key_reference:
                        stale_key_found = True
                        stale_platform_id = platform_id
                        logger.debug(f"Found stale metadata entry: {platform_id} -> {stored_name}")
                        break

            if stale_key_found:
                console.print(f"[error]SSH key '{key_reference}' not found on platform[/error]")
                console.print(
                    "[warning]This key exists in local metadata but has been deleted from the platform.[/warning]"
                )
                console.print(
                    "[dim]The key may have been deleted via the web console or another machine.[/dim]"
                )
                if stale_platform_id:
                    console.print(f"[dim]Stale SSH Key ID: {stale_platform_id}[/dim]")
            else:
                console.print(f"[error]SSH key '{key_reference}' not found[/error]")

            console.print("[dim]Tip: Run 'flow ssh-key list' to see all available keys[/dim]")
            return

        # Use the resolved key's FID for the actual operation
        logger.debug(f"Found key - FID: {key.fid}, Name: {key.name}")
        resolved_key_id = key.fid

        # Update required flag
        set_required = not unset
        try:
            ok = ssh_key_manager.set_key_required(resolved_key_id, set_required)
            if ok:
                label = "required" if set_required else "optional"
                console.print(
                    f"[success]✓[/success] Marked {key.name} ({resolved_key_id}) as {label}"
                )
            else:
                console.print("[error]Failed to update key requirement[/error]")
        except Exception as e:
            if isinstance(e, AuthenticationError):
                console.print(
                    "[error]Access denied.[/error] You must be a project administrator to change required keys."
                )
                try:
                    render_next_steps_panel(
                        console,
                        [
                            "flow ssh-key require <sshkey_FID>  [muted]— ask a project admin[/muted]",
                        ],
                        title="Next steps",
                    )
                except Exception:  # noqa: BLE001
                    console.print(
                        "[dim]Tip: Ask a project admin to run: flow ssh-key require <sshkey_FID>[/dim]"
                    )
                return
            raise

    except AuthenticationError:
        render_auth_required_message(console)
        raise click.exceptions.Exit(1)
    except Exception as e:
        from rich.markup import escape

        console.print(f"[error]Error: {escape(str(e))}[/error]")
        raise click.ClickException(str(e)) from e


@click.command()
@click.argument("key_reference", shell_complete=_complete_ssh_keys)
def delete(key_reference: str) -> None:
    """Delete an SSH key from the platform.

    KEY_REFERENCE: Platform SSH key ID (e.g., sshkey_abc123) or key name
    """
    try:
        console = _tm.create_console()
    except Exception:  # noqa: BLE001
        console = Console()

    try:
        # Get provider and optional manager from Flow instance
        flow = sdk_factory.create_client(auto_init=True)
        try:
            ssh_key_manager = flow.get_ssh_key_manager()
        except AttributeError:
            ssh_key_manager = None

        # Resolve key identifier to platform ID: support index (:N/N), ID, name, or local path
        key_id = key_reference
        # 0) Try index cache
        try:
            if key_reference.isdigit() or key_reference.startswith(":"):
                ref, err = SSHKeyIndexCache().resolve_index(key_reference)
                if err:
                    console.print(f"[error]{err}[/error]")
                    try:
                        render_next_steps_panel(
                            console,
                            [
                                "flow ssh-key list  [muted]— refresh indices[/muted]",
                                "Use index shortcuts: [accent]:N[/accent] or [accent]N[/accent]",
                            ],
                            title="Tips",
                        )
                    except Exception:  # noqa: BLE001
                        console.print(
                            "[dim]Tip: Re-run 'flow ssh-key list' to refresh indices, then use :N or N[/dim]"
                        )
                    return
                if ref:
                    resolved_local_path = None
                    if ref.get("type") == "platform_id":
                        key_id = ref.get("ref", key_reference)
                    elif ref.get("type") == "local":
                        # If the cached ref looks like a platform ID, promote it.
                        promote = ref.get("ref")
                        if isinstance(promote, str) and promote.startswith("sshkey_"):
                            key_id = promote
                        # Map local path by pubkey to platform ID (best-effort)
                        from pathlib import Path as _Path

                        lp = _Path(ref.get("ref", "")).expanduser().resolve()
                        resolved_local_path = lp if lp.exists() else None
                        pub = lp.with_suffix(".pub")
                        if pub.exists():
                            content = pub.read_text().strip()
                            for k in ssh_key_manager.list_keys():
                                if getattr(k, "public_key", None) and normalize_public_key(
                                    content
                                ) == normalize_public_key(k.public_key):
                                    key_id = k.fid
                                    break
                    # If still not a platform id and we had a local index, it's local-only
                    if not key_id.startswith("sshkey_") and ref.get("type") == "local":
                        path_hint = (
                            str(resolved_local_path)
                            if resolved_local_path
                            else ref.get("ref", "local key")
                        )
                        console.print(
                            f"[warning]This key exists only locally ({path_hint}). Nothing to delete on platform.[/warning]"
                        )
                        try:
                            render_next_steps_panel(
                                console,
                                [
                                    "flow ssh-key upload <path>",
                                    "rm -i <path> <path>.pub  [muted]— remove locally[/muted]",
                                ],
                                title="Next steps",
                            )
                        except Exception:  # noqa: BLE001
                            console.print(
                                "[dim]To upload to platform: flow ssh-key upload <path>  ·  To remove locally: rm -i <path> <path>.pub[/dim]"
                            )
                        return
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Failed to resolve index for delete command: {e}")

        # Load platform keys via provider (preferred), fallback to manager
        platform_keys: list
        raw = flow.list_platform_ssh_keys()
        platform_keys = [PlatformSSHKey.from_api(rk) for rk in raw]
        if not platform_keys and ssh_key_manager is None:
            console.print("[warning]SSH key management not supported by current provider[/warning]")
            return
        if not platform_keys and ssh_key_manager is not None:
            platform_keys = ssh_key_manager.list_keys()

        # 1) If not a platform ID yet, try name → ID
        if not key_id.startswith("sshkey_"):
            matching_keys = [k for k in platform_keys if getattr(k, "name", "") == key_reference]

            if not matching_keys:
                console.print(f"[error]SSH key '{key_reference}' not found[/error]")
                console.print("\n[dim]Available keys:[/dim]")
                all_keys = ssh_key_manager.list_keys()
                for key in all_keys[:10]:  # Show first 10 keys
                    console.print(f"  • {key.name} ({key.fid})")
                if len(all_keys) > 10:
                    console.print(f"  [dim]... and {len(all_keys) - 10} more[/dim]")
                return

            if len(matching_keys) > 1:
                console.print(
                    f"[warning]Multiple keys found with name '{key_reference}':[/warning]"
                )
                for key in matching_keys:
                    console.print(f"  • {key.name} ({key.fid})")
                console.print(
                    "\n[dim]Please use the platform ID (sshkey_xxx) to delete a specific key[/dim]"
                )
                return

            key_id = getattr(matching_keys[0], "fid", key_reference)
            console.print(f"[dim]Found key: {matching_keys[0].name} ({key_id})[/dim]")

        # Confirm deletion
        if not click.confirm(f"Delete SSH key {key_id}?"):
            return

        try:
            # Try provider delete first (via Flow facade)
            if flow.delete_platform_ssh_key(key_id):
                console.print(f"[success]✓[/success] Deleted SSH key {key_id}")
                return
            # If deletion returned False, it might be a "not found" error
            console.print(f"[error]SSH key {key_id} not found[/error]")
            console.print("[dim]The key may have already been deleted[/dim]")
            return
        except Exception as e:
            # Normalize common provider errors without importing provider-specific types
            msg = str(e).lower()
            if "not found" in msg:
                console.print(f"[error]SSH key {key_id} not found[/error]")
                console.print("[dim]The key may have already been deleted[/dim]")
                return
            from rich.markup import escape

            console.print(f"[error]{escape(str(e))}[/error]")
            raise click.ClickException(str(e)) from e

    except click.ClickException:
        raise
    except AuthenticationError:
        render_auth_required_message(console)
        raise click.exceptions.Exit(1)
    except Exception as e:
        from rich.markup import escape

        console.print(f"[error]Error: {escape(str(e))}[/error]")
        raise click.ClickException(str(e)) from e


@click.command(hidden=True)
@click.argument("key_id")
@click.argument("private_key_path")
def link(key_id: str, private_key_path: str) -> None:
    """Link a platform SSH key ID to a local private key.

    Stores a local mapping so runs and details can find your key even
    when the provider cannot list it in the current project.

    Example:
      flow ssh-key link sshkey_abc123 ~/.ssh/id_ed25519
    """
    try:
        console = _tm.create_console()
    except Exception:  # noqa: BLE001
        console = Console()

    try:
        if not isinstance(key_id, str) or not key_id.startswith("sshkey_"):
            console.print("[error]KEY_ID must look like sshkey_…[/error]")
            raise click.ClickException("Invalid KEY_ID")

        priv = Path(private_key_path).expanduser().resolve()
        if priv.suffix == ".pub":
            priv = priv.with_suffix("")
        if not priv.exists():
            console.print(f"[error]Private key not found: {priv}")
            raise click.ClickException("Private key not found")
        pub = priv.with_suffix(".pub")
        if not pub.exists():
            console.print(f"[error]Missing public key: {pub}")
            raise click.ClickException("Missing public key")

        from flow.sdk.helpers.security import check_ssh_key_permissions as _check

        _check(priv)

        try:
            store_key_metadata(
                key_id=key_id,
                key_name=priv.stem,
                private_key_path=priv,
                project_id=None,
                auto_generated=False,
            )
        except Exception as e:
            from rich.markup import escape

            console.print(f"[error]Failed to store mapping: {escape(str(e))}[/error]")
            raise click.ClickException("Failed to store mapping") from e

        console.print(f"[success]✓[/success] Linked {key_id} → {priv}")
        try:
            render_next_steps_panel(
                console,
                ["flow ssh-key list -v  [muted]— verify mapping[/muted]"],
                title="Next steps",
            )
        except Exception:  # noqa: BLE001
            pass

    except click.ClickException:
        raise
    except AuthenticationError:
        render_auth_required_message(console)
        raise click.exceptions.Exit(1)
    except Exception as e:
        from rich.markup import escape

        console.print(f"[error]Error: {escape(str(e))}[/error]")
        raise click.ClickException(str(e)) from e


class SSHKeysCommand(BaseCommand):
    """SSH keys management command."""

    @property
    def name(self) -> str:
        """Command name."""
        return "ssh-key"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Manage SSH keys"

    def get_command(self) -> click.Command:
        """Return the ssh-key command group."""

        @click.group(name="ssh-key", cls=OrderedDYMGroup, invoke_without_command=True)
        @click.option(
            "--verbose", "-v", is_flag=True, help="Show detailed SSH key management guide"
        )
        @cli_error_guard(self)
        def ssh_keys_group(verbose: bool):
            """Manage SSH keys.

            \b
            Examples:
                flow ssh-key list                      # Show all SSH keys
                flow ssh-key upload ~/.ssh/id_rsa.pub  # Upload new key
                flow ssh-key delete sshkey_xxx         # Remove key

            Run 'flow ssh-key' alone to see the complete SSH setup guide.
            """
            # Get the Click context to check if a subcommand was invoked
            ctx = click.get_current_context()

            # Show the SSH Key Management Guide if no subcommand was provided
            if ctx.invoked_subcommand is None:
                try:
                    console = _tm.create_console()
                except Exception:  # noqa: BLE001
                    console = Console()
                lines = [
                    "[bold]Initial setup:[/bold]",
                    "  flow ssh-key upload               # Upload local keys",
                    "  flow ssh-key list                 # View all keys",
                    "  # Copy platform ID (sshkey_xxx) and add to ~/.flow/config.yaml",
                    "",
                    "[bold]Key locations:[/bold]",
                    "  ~/.ssh/                           # Standard SSH keys",
                    "  ~/.flow/keys/                     # Flow-specific keys",
                    "  ~/.flow/config.yaml               # Active key configuration",
                    "",
                    "[bold]Common patterns:[/bold]",
                    "  # Use existing GitHub key",
                    "  flow ssh-key upload ~/.ssh/id_ed25519.pub",
                    "",
                    "  # Generate new key for Flow",
                    "  ssh-keygen -t ed25519 -f ~/.ssh/flow_key",
                    "  flow ssh-key upload ~/.ssh/flow_key.pub",
                    "",
                    "[bold]Configuration in ~/.flow/config.yaml:[/bold]",
                    "  ssh_keys:",
                    "    - sshkey_abc123                 # Platform ID",
                    "    - ~/.ssh/id_rsa                 # Local path",
                    "",
                    "[bold]Troubleshooting:[/bold]",
                    "  • Permission denied → Check key is added: flow ssh-key list",
                    "  • Key not found → Run: flow ssh-key upload",
                    "  • Multiple keys → Configure in ~/.flow/config.yaml",
                ]
                try:
                    from flow.cli.commands.feedback import feedback as _fb

                    _fb.info("\n".join(lines), title="SSH Key Management Guide", neutral_body=True)
                except Exception:  # noqa: BLE001
                    # Fallback to simple prints if feedback panel fails
                    console.print("\nSSH Key Management Guide\n")
                    for ln in lines:
                        console.print(ln)

        @click.command()
        @click.argument("key_path", shell_complete=_complete_ssh_keys)
        @click.option("--name", help="Name for the SSH key on platform (skips interactive prompt)")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @cli_error_guard(self)
        def upload(key_path: str, name: str | None, output_json: bool):
            """Upload a specific SSH key to the platform.

            \b
            KEY_PATH: Path to your SSH key file. Accepts either:
              - Private key (e.g., ~/.ssh/id_ed25519) – Flow will read or generate the corresponding .pub
              - Public key (e.g., ~/.ssh/id_ed25519.pub)

            If --name is not provided, you'll be prompted to enter a name for the key,
            with the filename (without extension) as the default.
            """
            path = Path(key_path).expanduser().resolve()
            logger.debug(f"Resolved key path: {path}, exists: {path.exists()}")

            if not path.is_file():
                raise FileNotFoundError(f"Key file not found: {path}")

            logger.debug(
                f"Starting SSH key upload: key_path={key_path}, name={name}, output_json={output_json}"
            )

            try:
                console = _tm.create_console()
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to create themed console, using default: {e}")
                console = Console()

            # Get provider and optional SSH key manager
            logger.debug("Creating SDK client and getting provider")
            flow = sdk_factory.create_client(auto_init=True)
            provider = flow.provider
            logger.debug(f"Provider created: {type(provider).__name__}")

            # Determine key name - prompt if not provided
            if name:
                key_name = name
                logger.debug(f"Using provided key name: {key_name}")
            else:
                # Get username prefix for default name
                try:
                    username = get_sanitized_username(flow)[:10]
                    username_prefix = f"{username}-"
                    logger.debug(f"Using username prefix: {username_prefix}")
                except UserInfoError as e:
                    logger.debug(f"Could not get username: {e}, using key name without prefix")
                    username_prefix = ""

                default_name = f"{username_prefix}{path.stem}"
                logger.debug(f"Generated default name: {default_name}")
                if not output_json:
                    # Interactive prompt for key name
                    try:
                        key_name = click.prompt(
                            "Enter a name for this key",
                            default=default_name,
                            show_default=True,
                            type=str,
                        ).strip()
                        if not key_name:
                            key_name = default_name
                        logger.debug(f"User provided key name: {key_name}")
                    except (click.Abort, KeyboardInterrupt):
                        console.print("\n[warning]Upload cancelled[/warning]")
                        return
                    except Exception as e:  # noqa: BLE001
                        logger.debug(f"Prompt failed, using default: {e}")
                        key_name = default_name
                else:
                    # Non-interactive mode (JSON output) - use default
                    key_name = default_name
                    logger.debug(f"Using default key name (JSON mode): {key_name}")

            # Upload the key - handle errors for JSON output
            try:
                uploaded_id = provider.upload_ssh_key(path, key_name, deduplicate=False)
                logger.info(f"Successfully uploaded SSH key with ID: {uploaded_id}")
            except Exception as e:
                logger.debug(f"Upload failed: {e}")
                if output_json:
                    print_json(error_json(str(e)))
                    sys.exit(1)
                raise

            if output_json:
                print_json({"status": "uploaded", "id": uploaded_id, "name": key_name})
                return

            console.print(
                f"[success]✓[/success] Uploaded SSH key to platform as {key_name} ({uploaded_id})"
            )

        ssh_keys_group.add_command(list, name="list")
        ssh_keys_group.add_command(upload, name="upload")
        ssh_keys_group.add_command(details, name="info")
        ssh_keys_group.add_command(link, name="link")
        ssh_keys_group.add_command(repair, name="repair")
        ssh_keys_group.add_command(delete)
        ssh_keys_group.add_command(require)

        return ssh_keys_group


@click.command(hidden=True)
@click.option(
    "--all", "scan_all", is_flag=True, help="Scan all project keys, not just configured ones"
)
@click.option("--json", "output_json", is_flag=True, help="Output JSON with repair results")
def repair(scan_all: bool, output_json: bool) -> None:
    """Repair SSH key mappings by linking platform IDs to local private keys.

    By default, this scans only the SSH keys configured in your Flow config and
    attempts to find matching local private keys. Use --all to scan all keys in
    your Mithril project.
    """
    try:
        console = _tm.create_console()
    except Exception:  # noqa: BLE001
        console = Console()

    try:
        flow = sdk_factory.create_client(auto_init=True)
        try:
            ssh_key_manager = flow.get_ssh_key_manager()
        except AttributeError:
            ssh_key_manager = None

        # Determine target platform key IDs
        target_ids: list[str] = []
        configured = []
        cfg = flow.config.provider_config or {}
        configured = cfg.get("ssh_keys", [])
        default_key = cfg.get("default_ssh_key")
        if default_key:
            configured.append(default_key)

        if scan_all:
            # All project keys via provider/manager
            raw = flow.list_platform_ssh_keys()
            target_ids = [rk.get("id") or rk.get("fid") for rk in raw]
        else:
            # Configured platform IDs only
            target_ids = [k for k in configured if isinstance(k, str) and k.startswith("sshkey_")]

        target_ids = [tid for tid in target_ids if isinstance(tid, str) and tid]
        target_ids = list(dict.fromkeys(target_ids))  # stable dedup

        results = []
        fixed_count = 0
        already_count = 0
        unresolved: list[str] = []

        # Resolve each ID
        for key_id in target_ids:
            # Skip if mapping already exists
            existing_path = _id_get_local(key_id)
            if existing_path is not None:
                already_count += 1
                results.append(
                    {"id": key_id, "status": "already_mapped", "path": str(existing_path)}
                )
                continue

            # Try manager-based local match (uses pubkey/fingerprint logic)
            matched_path = None
            if ssh_key_manager is not None:
                matched_path = ssh_key_manager.find_matching_local_key(key_id)

            if matched_path is not None and matched_path.exists():
                # Persist mapping via identity service
                try:
                    store_key_metadata(
                        key_id=key_id,
                        key_name=matched_path.stem,
                        private_key_path=matched_path,
                        project_id=None,
                        auto_generated=False,
                    )
                    fixed_count += 1
                    results.append({"id": key_id, "status": "mapped", "path": str(matched_path)})
                except Exception:  # noqa: BLE001
                    results.append(
                        {"id": key_id, "status": "error", "error": "failed_to_store_mapping"}
                    )
            else:
                unresolved.append(key_id)
                results.append({"id": key_id, "status": "unresolved"})

        if output_json:
            print_json(
                {
                    "scanned": len(target_ids),
                    "fixed": fixed_count,
                    "already": already_count,
                    "unresolved": unresolved,
                    "results": results,
                }
            )
            return

        # Human-readable output
        console.print(
            f"[accent]Scanned:[/accent] {len(target_ids)}  [success]Fixed:[/success] {fixed_count}  [muted]Already:[/muted] {already_count}  [warning]Unresolved:[/warning] {len(unresolved)}"
        )
        for r in results:
            status = r.get("status")
            if status == "mapped":
                console.print(f"  [success]✓[/success] {r['id']} → {r['path']}")
            elif status == "already_mapped":
                console.print(f"  [dim]- already[/dim] {r['id']} → {r['path']}")
            elif status == "unresolved":
                console.print(f"  [warning]![/warning] {r['id']} (no local private key found)")
            else:
                console.print(f"  [error]✗[/error] {r['id']} — {r.get('error', 'error')}")

        if unresolved:
            console.print("\n[warning]Some keys are unresolved.[/warning] Suggestions:")
            console.print("  • Ensure your local ~/.ssh contains the matching private key")
            console.print("  • Or set MITHRIL_SSH_KEY=/path/to/private/key for runs")
            console.print("  • Or upload your local key: flow ssh-key upload ~/.ssh/<key>.pub")

    except AuthenticationError:
        render_auth_required_message(console)
        raise click.exceptions.Exit(1)
    except Exception as e:
        from rich.markup import escape

        console.print(f"[error]Error: {escape(str(e))}[/error]")
        raise click.ClickException(str(e)) from e


# Export command instance
command = SSHKeysCommand()
