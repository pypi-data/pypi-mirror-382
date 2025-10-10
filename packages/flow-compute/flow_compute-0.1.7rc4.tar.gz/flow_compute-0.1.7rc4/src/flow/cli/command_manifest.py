"""Centralized manifest for Flow CLI commands.

Provides a single source of truth used by the root CLI loader and
the legacy commands registry to prevent drift between different
command listings.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Final

from flow.cli.utils.mode_config import Mode


@dataclass(frozen=True)
class CommandSpec:
    """Specification for a concrete CLI command backed by a module."""

    name: str
    module: str
    summary: str
    example: str | None = None
    hidden: bool = False
    modes: set[Mode] = field(default_factory=lambda: {Mode.INFRA, Mode.RESEARCH})


@dataclass(frozen=True)
class AliasSpec:
    """Alias mapping to an existing command module.

    The loader will import the target module and expose a wrapper command
    registered under `alias` that forwards all options/args.

    For parameterized aliases, use target_args to specify arguments to pass
    to the target command.
    """

    alias: str
    target_module: str
    summary: str | None = None
    example: str | None = None
    hidden: bool = True
    target_args: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StubSpec:
    """Lightweight placeholder for deferred/coming-soon commands."""

    name: str
    note: str
    summary: str = "(coming soon)"
    hidden: bool = True


# Canonical command list (in desired help order)
COMMANDS: Final[list[CommandSpec]] = [
    CommandSpec(
        "setup",
        "setup",
        "Configure credentials and environment",
    ),
    CommandSpec("docs", "docs", "Show documentation links", "flow docs --verbose"),
    CommandSpec(
        "instance",
        "instance",
        "Manage compute instances",
        "flow instance create -i h100 -N 8",
        modes={Mode.INFRA},
    ),
    CommandSpec("volume", "volumes", "Manage volumes", "flow volume list"),
    CommandSpec(
        "ssh-key",
        "ssh_keys",
        "Manage SSH keys",
        "flow ssh-key list",
    ),
    CommandSpec(
        "pricing",
        "pricing",
        "Market prices and recommendations",
        "flow pricing --gpu h100",
        modes={Mode.INFRA},
    ),
    CommandSpec(
        "submit",
        "submit",
        "Submit task from YAML or command",
        "flow submit 'nvidia-smi'",
        modes={Mode.RESEARCH},
    ),
    CommandSpec("cancel", "cancel", "Cancel tasks", "flow cancel 1", modes={Mode.RESEARCH}),
    CommandSpec("ssh", "ssh", "SSH into task", "flow ssh 1"),
    CommandSpec(
        "dev",
        "dev",
        "Launch a GPU workstation for interactive debugging and experimentation",
        "flow dev",
        modes={Mode.RESEARCH},
    ),
    CommandSpec("logs", "logs", "View task logs", "flow logs 1 -f", modes={Mode.RESEARCH}),
    CommandSpec(
        "upload-code",
        "upload_code",
        "Upload code to task",
        "flow upload-code 1",
        modes={Mode.RESEARCH},
    ),
    CommandSpec(
        "jupyter",
        "jupyter",
        "Start Jupyter on remote task",
        "flow jupyter my-task",
        modes={Mode.RESEARCH},
    ),
    CommandSpec(
        "grab",
        "grab",
        "Quick resource selection",
        "flow grab 8 h100 | flow grab 2 8xa100",
        hidden=True,
    ),
    CommandSpec(
        "reserve", "reserve", "Manage capacity reservations", "flow reserve list", hidden=True
    ),
    CommandSpec("alloc", "alloc", "Compact allocation view", "flow alloc --watch", hidden=True),
    CommandSpec(
        "ask",
        "ask",
        "Ask questions about available resources",
        'flow ask "What are the cheapest H100 instances?"',
        modes={Mode.RESEARCH},
    ),
    CommandSpec("finops", "finops", "FinOps pricing config and tiers", "flow finops", hidden=True),
    CommandSpec(
        "status", "status", "List and monitor tasks", "flow status --watch", modes={Mode.RESEARCH}
    ),
    CommandSpec(
        "template",
        "template",
        "Generate YAML templates",
        "flow template task -o task.yaml",
        modes={Mode.RESEARCH},
    ),
    CommandSpec(
        "mount", "mount", "Attach volumes", "flow mount vol_abc123 task-name", modes={Mode.RESEARCH}
    ),
    CommandSpec(
        "ports",
        "port_forward",
        "Manage ports and tunnels",
        "flow ports open 1 --port 8080,8888,3000-3002",
        hidden=True,
    ),
    CommandSpec("theme", "theme", "Manage CLI color themes", "flow theme set modern"),
    CommandSpec("update", "update", "Update Flow SDK", "flow update"),
    CommandSpec(
        "telemetry", "telemetry", "Manage telemetry settings", "flow telemetry status", hidden=True
    ),
    CommandSpec(
        "example",
        "example",
        "Run or show starters",
        "flow example gpu-test",
        modes={Mode.RESEARCH},
    ),
    CommandSpec(
        "completion",
        "completion",
        "Shell completion helpers",
        "flow completion install",
        hidden=True,
    ),
]


# Aliases for familiarity and convenience
ALIASES: Final[list[AliasSpec]] = [
    AliasSpec(
        alias="delete",
        target_module="cancel",
        summary="Cancel tasks (alias of 'cancel')",
        example="flow delete 1",
        hidden=True,
    ),
    AliasSpec(
        alias="port-forward",
        target_module="port_forward",
        summary="Manage ports and tunnels (alias of 'ports')",
        example="flow port-forward open 1 --port 8080",
        hidden=True,
    ),
    AliasSpec(
        alias="reservations",
        target_module="reserve",
        summary="Manage capacity reservations (alias of 'reserve')",
        example="flow reservations list",
        hidden=True,
    ),
    AliasSpec(
        alias="volumes",
        target_module="volumes",
        summary="Manage volumes (alias of 'volume')",
        example="flow volumes list",
        hidden=True,
    ),
    AliasSpec(
        alias="ssh-keys",
        target_module="ssh_keys",
        summary="Manage SSH keys (alias of 'ssh-key')",
        example="flow ssh-key list",
        hidden=True,
    ),
]


# Deferred surfaces that should present a friendly placeholder
STUBS: Final[list[StubSpec]] = [
    StubSpec("tutorial", "Run 'flow setup' to get started."),
    StubSpec("demo", "Demo mode will ship later."),
    StubSpec("slurm", "Slurm integration is coming soon; follow updates in release notes."),
    StubSpec("colab", "Colab local runtime integration is coming soon."),
]


def iter_modules_from_commands(commands: Iterable[CommandSpec]) -> list[str]:
    """Return unique module names from command specs preserving order."""
    seen: set[str] = set()
    out: list[str] = []
    for c in commands:
        if c.module not in seen:
            out.append(c.module)
            seen.add(c.module)
    return out


__all__ = [
    "ALIASES",
    "COMMANDS",
    "STUBS",
    "AliasSpec",
    "CommandSpec",
    "StubSpec",
    "iter_modules_from_commands",
]
