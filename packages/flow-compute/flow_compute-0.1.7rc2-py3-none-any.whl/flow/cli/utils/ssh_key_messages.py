"""Standardized messaging for missing SSH keys across commands.

Provides a single helper to render a concise, shell‑aware set of fixes
when no SSH keys are configured for launches or interactive sessions.
"""

from __future__ import annotations

import os
from typing import Literal

from flow.cli.utils.theme_manager import theme_manager


def _export_example() -> str:
    """Return a shell‑aware one‑liner to set MITHRIL_SSH_KEY.

    Mirrors the detection style used elsewhere in BaseCommand.
    """
    try:
        shell = os.environ.get("SHELL", "").lower()
        if "fish" in shell:
            return 'set -x MITHRIL_SSH_KEY "~/.ssh/id_ed25519"'
        if "powershell" in shell or "pwsh" in shell:
            return '$env:MITHRIL_SSH_KEY = "~/.ssh/id_ed25519"'
        if os.name == "nt":
            return 'set MITHRIL_SSH_KEY="%USERPROFILE%\\.ssh\\id_ed25519"'
        return 'export MITHRIL_SSH_KEY="~/.ssh/id_ed25519"'
    except Exception:  # noqa: BLE001
        return 'export MITHRIL_SSH_KEY="~/.ssh/id_ed25519"'


def print_no_ssh_keys_guidance(
    context: str | None = None,
    *,
    level: Literal["error", "warning"] = "error",
) -> None:
    """Print a concise, consistent guidance block for missing SSH keys.

    Args:
        context: Optional string to include after the headline (e.g., "for dev VM").
        level: Visual emphasis (error vs warning) without altering control‑flow.
    """
    console = theme_manager.create_console()
    color = theme_manager.get_color("error" if level == "error" else "warning")
    suffix = f" {context}" if context else ""
    console.print(f"[{color}]No SSH keys configured{suffix}[/{color}]")
    console.print("[dim]Fix:[/dim] ")
    console.print(
        "  1) Upload your public key: [accent]flow ssh-key upload ~/.ssh/id_ed25519.pub[/accent]"
    )
    console.print(f"  2) Set env for private key: [accent]{_export_example()}[/accent]")
