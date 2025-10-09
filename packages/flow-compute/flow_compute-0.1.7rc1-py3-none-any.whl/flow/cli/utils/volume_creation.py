"""Reusable volume creation utilities for CLI commands.

This module provides interactive volume creation flows that can be reused
across different CLI commands (e.g., dev, volume create).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from flow.sdk.client import Flow
    from flow.sdk.models import Volume

logger = logging.getLogger(__name__)

COST_PER_GB = 0.08


def create_volume_interactive(
    flow_client: Flow,
    console,
    *,
    size: int | None = None,
    name: str | None = None,
    interface: str | None = None,
    region: str | None = None,
    skip_confirmation: bool = False,
    use_step_timeline: bool = False,
    output_json: bool = False,
) -> Volume | None:
    """Create a volume with interactive prompts for missing parameters.

    This is a comprehensive helper that can be used by both 'flow volume create'
    and other commands that want to offer volume creation.

    The caller should handle any initial prompting (e.g., "Do you want to create a volume?")
    before calling this function. This function assumes the user wants to create a volume
    and proceeds with gathering the necessary parameters.

    Args:
        flow_client: Flow SDK client
        console: Rich console for output
        size: Volume size in GB (prompts if None)
        name: Volume name (generates default if None)
        interface: Storage type "block" or "file" (prompts if None)
        region: Region name (prompts if None)
        skip_confirmation: Skip final confirmation prompt
        use_step_timeline: Use StepTimeline for progress instead of AnimatedProgress
        output_json: Output JSON format

    Returns:
        Created Volume object or None if user cancels
    """
    try:
        # Prompt for storage type if not provided
        if interface is None:
            from rich.text import Text

            from flow.cli.utils.help_manual import _render_columns

            console.print("\n[bold]Storage type[/bold]")

            # If region is specified, get available storage types for that region
            if region is not None:
                available_storage_types = _get_available_storage_types(flow_client, region)
                if not available_storage_types:
                    console.print(f"[error]No storage types available in region '{region}'[/error]")
                    return None
            else:
                available_storage_types = ["block", "file"]

            # Format storage type descriptions using column renderer
            # Always show both types, but indicate if not available
            all_storage_types = [
                (
                    "file",
                    "File share storage provides you with a preformatted disk for file storage. This option is best for most use cases.",
                ),
                (
                    "block",
                    "Block storage is an advanced option which provides you with a raw disk volume, giving you complete control over the filesystem.",
                ),
            ]

            # Render each storage type separately to handle dimming correctly.
            # We need to apply [dim] tags to complete rendered lines rather than to the
            # description text itself, because _render_columns uses textwrap.wrap which
            # can break Rich markup tags mid-tag when wrapping long descriptions.
            for storage_type, description in all_storage_types:
                is_available = storage_type in available_storage_types

                if is_available:
                    label = f"• [accent]{storage_type}[/accent]"
                    final_description = description
                else:
                    label = f"• {storage_type}"
                    final_description = f"{description} (not available for this region)"

                # Render this storage type's row
                rows = [(label, len(Text.from_markup(label).plain), final_description)]
                rendered_lines = _render_columns(rows, indent=0, gap=2, style=None, max_width=80)

                # Print with dimming if unavailable
                for line in rendered_lines:
                    if is_available:
                        console.print(line)
                    else:
                        console.print(f"[dim]{line}[/dim]")

            # Set default based on availability
            default_choice = (
                "file" if "file" in available_storage_types else available_storage_types[0]
            )

            interface = click.prompt(
                "Choose storage type",
                type=click.Choice(available_storage_types),
                default=default_choice,
                show_choices=False,
            )

        # Prompt for region if not provided
        if region is None:
            # Get available regions for the storage type
            available_regions = _get_available_regions(flow_client, interface)
            if not available_regions:
                console.print(f"[error]No regions available for {interface} storage[/error]")
                return None

            console.print("\n[bold]Region[/bold]")
            console.print(f"Choose a region that supports [accent]{interface}[/accent] storage:")

            for region_name in available_regions:
                console.print(f"• [accent]{region_name}[/accent]")

            region = click.prompt(
                f"\nChoose region for {interface} storage",
                type=click.Choice(available_regions),
                default=available_regions[0],
                show_choices=False,
            )

        # Prompt for size if not provided
        if size is None:
            console.print("\n[bold]Volume size[/bold]")
            console.print(
                "Storage is priced at [accent]$0.08/GB[/accent] per month for both block and file storage."
            )

            size = click.prompt("\nEnter volume size in GB", type=int, default=100)

        # Prompt for name if not provided
        if name is None:
            console.print("\n[bold]Volume name[/bold]")
            console.print("Names help identify volumes and can be used in task configs.")

            from flow.cli.utils.name_generator import generate_unique_name

            suggested_name = generate_unique_name("vol", add_unique=True)

            name = click.prompt("\nEnter volume name", default=suggested_name)

        # Show pricing and confirmation
        monthly_cost = size * COST_PER_GB
        console.print("\n[bold]Volume configuration summary[/bold]")
        console.print(f"Name: [accent]{name}[/accent]")
        console.print(f"Size: [accent]{size} GB[/accent]")
        console.print(f"Type: [accent]{interface}[/accent]")
        console.print(f"Region: [accent]{region}[/accent]")
        console.print(f"Monthly cost: [accent]${monthly_cost:.2f}[/accent] (${size} GB × $0.08/GB)")

        if not skip_confirmation and not click.confirm("\nCreate this volume?", default=True):
            console.print("[dim]Volume creation cancelled[/dim]")
            return None

        # Create the volume with appropriate progress indicator
        if use_step_timeline:
            from flow.cli.utils.step_progress import StepTimeline

            timeline = StepTimeline(console, title="flow volume", title_animation="auto")
            timeline.start()
            step_suffix = f" in {region}" if region else ""
            step_idx = timeline.add_step(
                f"Creating {size}GB {interface} volume{step_suffix}", show_bar=False
            )
            timeline.start_step(step_idx)
            try:
                volume = flow_client.create_volume(
                    size_gb=size, name=name, interface=interface, region=region
                )
                timeline.complete_step()
            except Exception as e:
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
        else:
            from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

            with AnimatedEllipsisProgress(
                console, f"Creating {size}GB {interface} volume", start_immediately=True
            ):
                volume = flow_client.create_volume(
                    size_gb=size, name=name, interface=interface, region=region
                )

        # Output results
        if output_json:
            from flow.cli.utils.json_output import print_json, volume_to_json

            print_json({"status": "created", "volume": volume_to_json(volume)})
        else:
            console.print(
                f"\n[success]✓[/success] Volume created: [accent]{volume.volume_id}[/accent]"
            )
            if name:
                console.print(f"Name: [accent]{name}[/accent]")
            if region:
                console.print(f"Region: [accent]{region}[/accent]")

        return volume

    except (click.Abort, KeyboardInterrupt):
        # User interrupted - propagate to caller who can decide how to handle it
        raise
    except Exception as e:
        logger.exception("Failed to create volume")
        if not output_json:
            console.print(f"[error]Failed to create volume: {e}[/error]")
        raise


def _get_available_regions(flow_client: Flow, storage_type: str) -> list[str]:
    """Get available regions for the specified storage type.

    Args:
        flow_client: Flow SDK client
        storage_type: Storage type ("block" or "file")

    Returns:
        List of region names that support the storage type
    """
    try:
        provider = flow_client._ensure_provider()
        if not hasattr(provider, "list_regions_for_storage"):
            # Fallback to common regions if provider doesn't support the query
            logger.debug("Provider doesn't support list_regions_for_storage, using defaults")
            return ["us-central1-b", "us-central2-a", "us-west1-a"]

        return provider.list_regions_for_storage(storage_type)
    except Exception as e:  # noqa: BLE001
        logger.debug(f"Failed to get available regions: {e}")
        # Fallback to common regions
        return ["us-central1-b", "us-central2-a", "us-west1-a"]


def _get_available_storage_types(flow_client: Flow, region: str) -> list[str]:
    """Get available storage types for the specified region.

    Args:
        flow_client: Flow SDK client
        region: Region name

    Returns:
        List of storage types ("block" and/or "file") that are available in the region
    """
    provider = flow_client._ensure_provider()
    facets = flow_client._get_facets_for_provider(provider)

    # Use the storage facet's dedicated method
    if facets and getattr(facets, "storage", None) is not None:
        storage_types = facets.storage.get_storage_types_for_region(region)
        if storage_types:
            return storage_types

    # Fallback: return both types
    logger.debug(f"Could not determine storage types for region {region}, using defaults")
    return ["block", "file"]
