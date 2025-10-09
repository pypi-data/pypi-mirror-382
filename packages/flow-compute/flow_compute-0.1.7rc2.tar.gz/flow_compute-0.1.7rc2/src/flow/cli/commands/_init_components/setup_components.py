"""Setup components for configuration UI.

Provides UI components for interactive configuration including intelligent
option selection for projects, SSH keys, and other configuration items.
"""

from typing import Any

from rich.console import Console
from rich.prompt import Prompt

from flow.cli.ui.components import InteractiveSelector, SelectionItem
from flow.cli.ui.presentation.visual_constants import get_status_display


def select_from_options(
    console: Console,
    options: list[dict[str, Any]],
    name_key: str = "name",
    id_key: str = "id",
    title: str = "Select an option",
    show_ssh_table: bool = False,
    extra_header_html: str | None = None,
    breadcrumbs: list[str] | None = None,
    preferred_viewport_size: int | None = None,
) -> dict[str, Any] | None:
    """Intelligently select from options using appropriate UI pattern.

    Uses simple prompt for few options, interactive selector for many.

    Args:
        console: Console for output
        options: List of option dictionaries
        name_key: Key for display name in option dict
        id_key: Key for ID in option dict
        title: Title for selection interface

    Returns:
        Selected option dict or None if cancelled
    """
    if not options:
        return None

    # Single option: auto-select with confirmation
    if len(options) == 1:
        option = options[0]
        name = option.get(name_key, "Unknown")
        console.print(f"{get_status_display('configured', f'Selected project: {name}')}")
        return option

    # Show SSH keys in a table format if requested
    if show_ssh_table and any("created_at" in opt for opt in options):
        # Separate generation options from existing keys
        gen_options = [opt for opt in options if opt.get(id_key, "").startswith("GENERATE_")]
        ssh_keys = [opt for opt in options if not opt.get(id_key, "").startswith("GENERATE_")]

        # Create formatted options for interactive selector
        formatted_options = []

        # Add generation options first
        for i, opt in enumerate(gen_options):
            formatted_options.append(
                {**opt, "display_name": opt.get(name_key, "Unknown"), "index": i + 1}
            )

        # Add SSH keys
        for i, key in enumerate(ssh_keys):
            idx = len(gen_options) + i + 1
            formatted_options.append(
                {**key, "display_name": key.get("name", "Unknown"), "index": idx}
            )

        # Use interactive selector with custom formatting
        def ssh_option_to_selection(option: dict[str, Any]) -> SelectionItem[dict[str, Any]]:
            if option.get(id_key, "").startswith("GENERATE_"):
                # Action item
                return SelectionItem(
                    value=option, id="", title=option["display_name"], subtitle="", status=""
                )
            else:
                # SSH key with metadata
                subtitle_parts = []
                if option.get("created_at"):
                    subtitle_parts.append(f"Created: {option['created_at']}")
                # Provide an explicit hint when we detect a matching local private key
                try:
                    display_name = option.get("display_name") or option.get("name") or ""
                    if "(local)" in str(display_name):
                        subtitle_parts.append("local private key found")
                except Exception:  # noqa: BLE001
                    pass

                return SelectionItem(
                    value=option,
                    id="",
                    title=option["display_name"],
                    subtitle=" • ".join(subtitle_parts),
                    status="",
                )

        selector = InteractiveSelector(
            items=formatted_options,
            item_to_selection=ssh_option_to_selection,
            title=title,  # Use the provided title
            allow_multiple=False,
            allow_back=True,
            show_preview=False,
            breadcrumbs=breadcrumbs,
            extra_header_html=extra_header_html,
            preferred_viewport_size=preferred_viewport_size,
        )

        result = selector.select()
        if result is InteractiveSelector.BACK_SENTINEL:
            return None
        return result if result else None

        # Always try interactive selector first for better UX
    try:

        def option_to_selection(option: dict[str, Any]) -> SelectionItem[dict[str, Any]]:
            name = option.get(name_key, "Unknown")
            option_id = option.get(id_key, str(hash(str(option))))

            # Special handling for SSH keys - cleaner display
            if "ssh" in title.lower() and option_id.startswith("sshkey_"):
                # For existing SSH keys, include metadata in subtitle
                subtitle_parts = []
                if "created_at" in option:
                    subtitle_parts.append(option["created_at"])
                try:
                    name_or_disp = option.get(name_key, option.get("name", ""))
                    if "(local)" in str(name_or_disp):
                        subtitle_parts.append("local private key found")
                except Exception:  # noqa: BLE001
                    pass

                return SelectionItem(
                    value=option,
                    id="",  # Don't show ID separately
                    title=name,
                    subtitle=" • ".join(subtitle_parts) if subtitle_parts else "",
                    status="",  # Don't show redundant status
                )
            elif option_id == "GENERATE_SERVER":
                # For generation options, show as actions
                return SelectionItem(value=option, id="", title=name, subtitle="", status="")
            else:
                # Default behavior for other options
                return SelectionItem(
                    value=option, id=option_id, title=name, subtitle="", status="Available"
                )

        selector = InteractiveSelector(
            items=options,
            item_to_selection=option_to_selection,
            title=title,
            allow_multiple=False,
            allow_back=True,
            show_preview=False,
            breadcrumbs=breadcrumbs,
            extra_header_html=extra_header_html,
            preferred_viewport_size=preferred_viewport_size,
        )

        result = selector.select()
        if result is InteractiveSelector.BACK_SENTINEL:
            return None
        if result is not None:
            return result

    except Exception:  # noqa: BLE001
        # Fall back to numbered selection if interactive fails
        pass

    # Fallback: numbered prompt
    console.print(f"\n[bold]{title}:[/bold]")
    for i, option in enumerate(options, 1):
        name = option.get(name_key, "Unknown")
        console.print(f"  {i}. {name}")

    while True:
        choice = Prompt.ask("\nSelect number", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                console.print("[error]Invalid selection[/error]")
        except ValueError:
            console.print("[error]Please enter a number[/error]")
