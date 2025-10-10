"""Task formatting utilities for CLI output (delegates to shared)."""

from __future__ import annotations

from flow.cli.ui.formatters.shared_task import TaskFormatter, format_task_duration
from flow.sdk.models import Task

__all__ = ["TaskFormatter", "format_task_duration"]


def format_task_summary(task: Task) -> str:
    name = task.name or "unnamed"
    if len(name) > 25:
        name = name[:22] + "..."
    return name


def get_capability_warnings(task: Task) -> list[str]:
    warnings: list[str] = []
    try:
        # Use get_display_status for consistency (e.g., "starting" vs "pending")
        from flow.cli.ui.formatters.shared_task import TaskFormatter as _TF

        status_val = _TF.get_display_status(task)

        if status_val in ["running", "completed", "failed"]:
            if not task.has_ssh_access and not getattr(task, "ssh_keys_configured", False):
                warnings.append("No SSH access - task was submitted without SSH keys")
            elif not task.has_ssh_access and getattr(task, "ssh_keys_configured", False):
                warnings.append("SSH keys configured but access not yet available")
        elif status_val in ["pending", "starting"] and not getattr(
            task, "ssh_keys_configured", False
        ):
            warnings.append("No SSH keys configured - logs won't be available")
    except Exception:  # noqa: BLE001
        pass
    return warnings


def format_capabilities(task: Task) -> str:
    caps = getattr(task, "capabilities", {}) or {}
    icons = {"ssh": "🔐" if caps.get("ssh") else "🚫", "logs": "📋" if caps.get("logs") else "🚫"}
    return f"SSH: {icons['ssh']}  Logs: {icons['logs']}"


def format_post_submit_info(task: Task) -> list[str]:
    lines: list[str] = []
    task_ref = task.name or task.task_id
    from flow.cli.utils.theme_manager import theme_manager as _tm

    ok = _tm.get_color("success")
    try:
        from flow.cli.ui.presentation.nomenclature import get_entity_labels as _labels

        noun = _labels().header
    except Exception:  # noqa: BLE001
        noun = "Task"
    lines.append(f"[{ok}]✓[/{ok}] {noun} submitted: {task_ref}")
    warnings = get_capability_warnings(task)
    if warnings:
        lines.append("")
        warn = _tm.get_color("warning")
        lines.append(f"[{warn}]⚠ Warning:[/{warn}]")
        for w in warnings:
            lines.append(f"  {w}")
        try:
            plural_noun = _labels().empty_plural
        except Exception:  # noqa: BLE001
            plural_noun = "tasks"
        lines.append(f"  Run 'flow setup' to configure SSH keys for future {plural_noun}")
    else:
        lines += [
            "",
            "Commands:",
            f"  [accent]flow status {task_ref}[/accent]",
            f"  [accent]flow logs {task_ref}[/accent] [--follow]",
            f"  [accent]flow ssh {task_ref}[/accent]",
        ]
    return lines


def format_post_submit_commands(task: Task) -> list[str]:
    task_ref = task.name or task.task_id
    return [
        f"  [accent]flow status {task_ref}[/accent]",
        f"  [accent]flow logs {task_ref} -f[/accent]",
        f"  [accent]flow ssh {task_ref}[/accent]",
    ]
