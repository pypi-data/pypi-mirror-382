"""Helpers for composing help text for the Flow CLI.

Builds printable usage and command summaries from the active configuration.
"""

import click
from rich.markup import escape

from flow.cli.command_manifest import COMMANDS
from flow.cli.ui.presentation.terminal_adapter import TerminalAdapter
from flow.cli.utils.command_manager import (
    should_show_command,
)
from flow.cli.utils.icons import flow_icon
from flow.cli.utils.mode_config import Mode, get_current_mode, get_mode_config

# Layout constants for help text formatting
DEFAULT_INDENT = 2
DEFAULT_GAP = 2


def render_mode_indicator(mode: Mode) -> list[str]:
    """Render mode indicator with current mode and switch instructions.

    Args:
        mode: Mode to render indicator for (defaults to current mode)

    Returns:
        List of formatted lines showing current mode and how to switch
    """

    lines = []
    current_mode_cfg = get_mode_config(mode)
    lines.append(f"Active mode: [bold]{current_mode_cfg.display_name}[/bold]")
    lines.append("")

    return lines


def render_mode_commands(mode: Mode, show_more: bool = False) -> list[str]:
    """Render mode-specific commands as formatted lines.

    Args:
        mode: Mode to render commands for (defaults to current mode)
        show_more: Whether to show additional commands
        ctx: Click context for command access (optional, used for full CLI help)

    Returns:
        List of formatted lines ready for console output
    """
    lines = []
    listed = set()
    mode_config = get_mode_config(mode)
    all_commands = [spec.name for spec in COMMANDS]

    # Render groups defined in mode config
    for group_name, command_names in mode_config.groups.items():
        group_commands = []
        for cmd_name in command_names:
            should_show = should_show_command(cmd_name, mode, show_more)

            if should_show:
                listed.add(cmd_name)

                # Get help text and example
                cmd_spec = next((spec for spec in COMMANDS if spec.name == cmd_name), None)
                help_text = cmd_spec.summary if cmd_spec else ""
                if cmd_spec and cmd_spec.example:
                    help_text = f"{help_text}  e.g., {cmd_spec.example}"

                group_commands.append((cmd_name, help_text))

        if group_commands:
            lines.append(f"[muted]{flow_icon()} {group_name}[/muted]:")
            # Column-aware wrapping for command rows
            max_cmd_len = max(len(cmd_name) for cmd_name, _ in group_commands)
            rows: list[tuple[str, int, str]] = []
            for cmd_name, help_text in group_commands:
                left_disp = f"{cmd_name:<{max_cmd_len}}"
                right = escape(help_text) if help_text else ""
                rows.append((left_disp, len(left_disp), right))

            lines.extend(
                _render_columns(
                    rows,
                    prefix=f"{flow_icon()} ",
                    style=None,
                )
            )
            lines.append("")

    # Show more commands if requested
    if show_more:
        more_commands = []
        # Get all commands available to mode that are not core commands
        for cmd_name in all_commands:
            should_show = (
                should_show_command(cmd_name, mode, show_more=True)
                and cmd_name not in listed
                and cmd_name not in mode_config.core_commands
            )

            if should_show:
                cmd_spec = next((spec for spec in COMMANDS if spec.name == cmd_name), None)
                help_text = cmd_spec.summary if cmd_spec else ""
                if cmd_spec and cmd_spec.example:
                    help_text = f"{help_text}  e.g., {cmd_spec.example}"
                more_commands.append((cmd_name, help_text))

        if more_commands:
            lines.append(f"[muted]{flow_icon()} More[/muted]:")
            max_cmd_len = max(len(cmd_name) for cmd_name, _ in more_commands)
            rows: list[tuple[str, int, str]] = []
            for cmd_name, help_text in more_commands:
                left_disp = f"{cmd_name:<{max_cmd_len}}"
                right = escape(help_text) if help_text else ""
                rows.append((left_disp, len(left_disp), right))

            lines.extend(
                _render_columns(
                    rows,
                    prefix=f"{flow_icon()} ",
                    style=None,
                )
            )
            lines.append("")
    else:
        # Show hint about more commands
        more_for_mode = []
        # Get all commands available to mode that are not core commands
        for cmd_name in all_commands:
            should_show = (
                should_show_command(cmd_name, mode, show_more=True)
                and cmd_name not in listed
                and cmd_name not in mode_config.core_commands
            )
            if should_show:
                more_for_mode.append(cmd_name)

        if more_for_mode:
            lines.append(f"[muted]{flow_icon()} More commands[/muted]:")
            cmd_list = ", ".join(more_for_mode)
            lines.extend(_render_columns(rows=[("", 0, escape(cmd_list))], gap=0, style=None))
            lines.append("[muted]  Use --all to show the full command set.[/muted]")
            lines.append("")

    return lines


def render_rich_help(ctx: click.Context, show_more: bool = False) -> str:
    """Render help using Rich markup for proper styling."""

    lines = []

    # Usage line
    usage_raw = ctx.command.get_usage(ctx)
    lines.append(f"[muted]{escape(usage_raw.strip())}[/muted]")
    lines.append("")

    lines.extend(render_description(ctx))

    current_mode = get_current_mode()
    lines.extend(render_mode_indicator(current_mode))
    lines.extend(render_mode_commands(current_mode, show_more))
    lines.extend(render_options(ctx))

    return "\n".join(lines)


def render_description(ctx: click.Context) -> list[str]:
    """Render description from Click command help."""

    lines: list[str] = []
    cmd_help = getattr(ctx.command, "help", "") or ""
    if cmd_help.strip():
        desc_lines = [ln.strip() for ln in cmd_help.strip().splitlines()]
        if desc_lines:
            lines.append(escape(desc_lines[0]))
            lines.append("")
            for ln in desc_lines[1:]:
                if ln:
                    lines.append(f"[muted]{escape(ln)}[/muted]")
            lines.append("")

    return lines


def render_options(ctx: click.Context) -> list[str]:
    """Render options from Click command help."""

    lines: list[str] = ["[muted]Options:[/muted]"]

    rows: list[tuple[str, int, str]] = []
    seen: set[str] = set()

    for p in getattr(ctx.command, "params", []):
        if not isinstance(p, click.Option):
            continue
        if getattr(p, "hidden", False):
            continue

        rec = p.get_help_record(ctx)
        if not rec:
            continue

        names_str, help_text = rec
        if names_str in seen:
            continue
        seen.add(names_str)

        # Visible length taken from unescaped names; display text is escaped
        rows.append((escape(names_str), len(names_str), escape(help_text or "")))

    if not rows:
        return lines

    lines.extend(_render_columns(rows))

    return lines


def _render_columns(
    rows: list[tuple[str, int, str]],  # (left_display, left_visible_len, right_text_escaped)
    indent: int = DEFAULT_INDENT,
    gap: int = DEFAULT_GAP,
    prefix: str = "",
    style: str | None = "muted",
    max_width: int | None = None,
) -> list[str]:
    """Render columns with wrapped text.

    Args:
        rows: List of (left_display, left_visible_len, right_text_escaped) tuples
        indent: Left indentation in spaces
        gap: Gap between columns in spaces
        prefix: Prefix string for the right column
        style: Rich style to apply to the output
        max_width: Optional maximum total width; if provided, limits output even if terminal is wider

    Returns:
        List of formatted lines ready for output
    """

    try:
        total_width = int(TerminalAdapter.get_terminal_width())
    except Exception:  # noqa: BLE001
        total_width = 100

    # Apply max_width if specified
    if max_width is not None:
        total_width = min(total_width, max_width)

    left_width = max(v for _, v, _ in rows) if rows else 0
    prefix_len = indent + left_width + gap + len(prefix)
    from textwrap import wrap as _wrap

    out: list[str] = []
    for left_disp, vis_len, right in rows:
        pad = " " * (left_width - vis_len)
        avail = max(1, total_width - prefix_len)
        chunks = _wrap(right, width=avail, break_long_words=False) or [""]

        first = " " * indent + f"{left_disp}{pad}" + " " * gap + prefix + chunks[0]
        if style:
            first = f"[{style}]{first}[/{style}]"
        out.append(first)

        cont_indent = " " * prefix_len
        for extra in chunks[1:]:
            line = cont_indent + extra
            if style:
                line = f"[{style}]{line}[/{style}]"
            out.append(line)

    return out
