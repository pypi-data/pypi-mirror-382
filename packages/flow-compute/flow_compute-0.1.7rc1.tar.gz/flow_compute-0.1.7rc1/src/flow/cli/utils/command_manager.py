"""CLI command management for Flow.

Manages user modes (infra vs research) that determine which commands are visible
and what default behaviors are applied. Modes are persisted in the user's
Flow configuration file."""

from __future__ import annotations

from flow.cli.command_manifest import COMMANDS
from flow.cli.utils.mode_config import Mode, get_mode_config, get_other_mode


def should_show_command(command_name: str, mode: Mode, show_more: bool = False) -> bool:
    """Check if a command should be shown in current mode.

    Args:
        command_name: Name of the command to check
        show_more: Whether more commands should be shown

    Returns:
        True if command should be visible in help
    """

    # Find command spec
    cmd_spec = None
    for spec in COMMANDS:
        if spec.name == command_name:
            cmd_spec = spec
            break

    if not cmd_spec:
        return False

    # Hidden commands are never shown in help
    if cmd_spec.hidden:
        return False

    # Check if command is available in current mode
    if mode not in cmd_spec.modes:
        return False

    # Show core commands
    mode_config = get_mode_config(mode)
    if command_name in mode_config.core_commands:
        return True

    # Show non-core commands only with --all flag
    return show_more


def get_switch_command() -> str:
    """Get command to switch to a different mode."""
    other_mode = get_other_mode()
    return f"flow --mode {other_mode.value}"
