"""Shared task formatting utilities for CLI UI.

Single source of truth used by both presentation and components layers.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from flow.cli.utils.theme_manager import theme_manager
from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class TaskFormatter:
    """Handles task-related formatting for consistent display across CLI commands."""

    @staticmethod
    def format_task_display(task: Task) -> str:
        if task.name:
            if task.task_id and not task.task_id.startswith("bid_"):
                return f"{task.name} ({task.task_id})"
            return task.name
        return task.task_id

    @staticmethod
    def format_short_task_id(task_id: str, length: int = 16) -> str:
        if len(task_id) <= length:
            return task_id
        return task_id[:length] + "..."

    @staticmethod
    def get_status_config(status: str) -> dict[str, str]:
        status_configs = {
            "pending": {
                "symbol": "○",
                "color": theme_manager.get_color("status.pending"),
                "style": "",
            },
            "open": {
                "symbol": "○",
                "color": theme_manager.get_color("status.pending"),
                "style": "",
            },
            "starting": {
                "symbol": "●",
                "color": theme_manager.get_color("status.starting"),
                "style": "",
            },
            "preparing": {
                "symbol": "●",
                "color": theme_manager.get_color("status.preparing"),
                "style": "",
            },
            "running": {
                "symbol": "●",
                "color": theme_manager.get_color("status.running"),
                "style": "",
            },
            "paused": {
                "symbol": "⏸",
                "color": theme_manager.get_color("status.paused"),
                "style": "",
            },
            "preempting": {
                "symbol": "●",
                "color": theme_manager.get_color("status.preempting"),
                "style": "",
            },
            "completed": {
                "symbol": "●",
                "color": theme_manager.get_color("status.completed"),
                "style": "",
            },
            "failed": {
                "symbol": "●",
                "color": theme_manager.get_color("status.failed"),
                "style": "",
            },
            "cancelled": {
                "symbol": "○",
                "color": theme_manager.get_color("status.cancelled"),
                "style": "",
            },
            "unknown": {"symbol": "○", "color": theme_manager.get_color("muted"), "style": ""},
            # Extra labels used by selection/presentation views
            "available": {"symbol": "✓", "color": theme_manager.get_color("success"), "style": ""},
            "unavailable": {"symbol": "✖", "color": theme_manager.get_color("error"), "style": ""},
            "enabled": {"symbol": "✓", "color": theme_manager.get_color("success"), "style": ""},
            "disabled": {"symbol": "○", "color": theme_manager.get_color("muted"), "style": ""},
        }
        return status_configs.get(
            status.lower(),
            {"symbol": "?", "color": theme_manager.get_color("default"), "style": ""},
        )

    @staticmethod
    def get_status_style(status: str) -> str:
        return TaskFormatter.get_status_config(status)["color"]

    @staticmethod
    def format_status_with_color(status: str) -> str:
        config = TaskFormatter.get_status_config(status)
        try:
            if hasattr(theme_manager, "is_color_enabled") and not theme_manager.is_color_enabled():
                codes = {
                    "running": "RUN",
                    "pending": "PEN",
                    "open": "OPN",
                    "failed": "ERR",
                    "completed": "OK",
                    "starting": "ST",
                    "preparing": "PRP",
                    "paused": "PAU",
                    "preempting": "PRM",
                    "cancelled": "CAN",
                    "unknown": "UNK",
                }
                code = codes.get(str(status).lower(), str(status).upper()[:3])
                return f"{config['symbol']} {code}"
        except Exception:  # noqa: BLE001
            pass
        style_parts = [config["color"]]
        if config["style"]:
            style_parts.append(config["style"])
        style = " ".join(style_parts)
        return f"[{style}]{config['symbol']} {status}[/{style}]"

    @staticmethod
    def format_compact_status(status: str) -> str:
        config = TaskFormatter.get_status_config(status)
        try:
            if hasattr(theme_manager, "is_color_enabled") and not theme_manager.is_color_enabled():
                codes = {
                    "running": "RUN",
                    "pending": "PEN",
                    "open": "OPN",
                    "failed": "ERR",
                    "completed": "OK",
                    "starting": "ST",
                    "preparing": "PRP",
                    "paused": "PAU",
                    "preempting": "PRM",
                    "cancelled": "CAN",
                    "unknown": "UNK",
                }
                code = codes.get(str(status).lower(), str(status).upper()[:3])
                return f"{config['symbol']} {code}"
        except Exception:  # noqa: BLE001
            pass
        style_parts = [config["color"]]
        if config["style"]:
            style_parts.append(config["style"])
        style = " ".join(style_parts)
        return f"[{style}]{config['symbol']}[/{style}]"

    @staticmethod
    def get_display_status(task: Task) -> str:
        """Derive a user-facing status with practical 'open' and 'starting' semantics.

        Rules:
        - Terminal states (failed, cancelled) are shown as-is.
        - PENDING tasks are refined based on instance status:
          • "starting" - bid is allocated, instances are booting (initializing, starting, provisioning)
          • "open" - bid is open/unallocated, no instances yet (queued, scheduled)
        - RUNNING tasks are shown as "running" (instance status already reflected in task.status).

        This provides clear lifecycle visibility: open → starting → running
        """
        status_value = getattr(
            getattr(task, "status", None),
            "value",
            str(getattr(task, "status", "unknown")).lower(),
        )

        # 1) Terminal states are authoritative
        if status_value in {"failed", "cancelled"}:
            return status_value

        # 2) Refine display for PENDING tasks based on instance status
        # Distinguish "starting" (instances booting) from "open" (queued/scheduled, no instances yet)
        if status_value == "pending":
            instance_status_from_api = task.provider_metadata.get("instance_status", "")
            if instance_status_from_api:
                instance_status_lower = str(instance_status_from_api).lower()
                if instance_status_lower.startswith("status_"):
                    instance_status_lower = instance_status_lower.replace("status_", "")

                # Show "starting" for instance boot states (bid allocated, instances provisioning)
                if instance_status_lower in {
                    "starting",
                    "initializing",
                    "new",
                    "confirmed",
                    "provisioning",
                }:
                    return "starting"

            # Otherwise, show "open" (bid is open/unallocated, not yet fulfilled)
            return "open"

        # 3) For RUNNING tasks, simple passthrough
        # Instance status is already reflected in task.status, so "running" means truly running
        if status_value == "running":
            return "running"

        # Default: return the underlying status value
        return status_value


def format_task_duration(task: Task) -> str:
    """Format task duration or time since creation."""
    try:
        if task.started_at:
            start = task.started_at
            end = task.completed_at or datetime.now(timezone.utc)
            prefix = ""
        else:
            start = task.created_at
            end = datetime.now(timezone.utc)
            prefix = "created "
        if not isinstance(start, datetime):
            start = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
        if not isinstance(end, datetime):
            end = datetime.fromisoformat(str(end).replace("Z", "+00:00"))
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        duration = end - start
        if duration.days > 0:
            return f"{prefix}{duration.days}d {duration.seconds // 3600}h ago"
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        if hours > 0:
            return f"{prefix}{hours}h {minutes}m ago"
        elif minutes > 0:
            return f"{prefix}{minutes}m ago"
        else:
            return f"{prefix}just now"
    except Exception:  # noqa: BLE001
        return "unknown"
