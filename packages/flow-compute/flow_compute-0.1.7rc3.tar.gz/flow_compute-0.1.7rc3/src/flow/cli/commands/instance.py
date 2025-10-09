"""Instance command group — host-centric aliases.

This module provides a `flow instance` command group that exposes
host/VM-centric verbs by reusing existing commands:

- flow instance create → flow submit
- flow instance delete → flow cancel
- flow instance list   → flow status
- flow instance info   → flow status <name> (with customized help text)

The subcommands are thin wrappers that forward all arguments and options
to the underlying implementations to stay DRY and SOLID, while offering
an intuitive surface familiar to Crusoe Cloud CLI users.
"""

from __future__ import annotations

import importlib

import click

from flow.cli.commands.base import BaseCommand


class InstanceCommand(BaseCommand):
    """Expose host-centric aliases under `flow instance`.

    This command group mirrors common VM/host verbs by delegating to
    existing task-centric commands, providing a familiar surface while
    keeping implementation DRY.
    """

    @property
    def name(self) -> str:
        return "instance"

    @property
    def help(self) -> str:
        return "Manage compute instances."

    def _resolve_base(self, target_module_name: str) -> click.Command | None:
        """Resolve a base command by importing its module directly.

        Avoids wrapper indirection; we attach the base command under a new name.
        """
        try:
            module = importlib.import_module(f"flow.cli.commands.{target_module_name}")
            return module.command.get_command()  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            return None

    def get_command(self) -> click.Command:
        """Build the Click command group and attach aliases."""

        @click.group(name=self.name, help=self.help, invoke_without_command=True)
        @click.pass_context
        def grp(ctx: click.Context) -> None:
            """Host-centric instance management commands."""
            # Mark instance-mode so downstream UIs can swap terminology (task→host)
            try:
                ctx.ensure_object(dict)
                ctx.obj["instance_mode"] = True
            except Exception:  # noqa: BLE001
                pass
            # If run without a subcommand, show group help and exit
            if ctx.invoked_subcommand is None:
                click.echo(ctx.get_help())
                ctx.exit(0)

        # Register subcommands as aliases to existing commands
        # create → run (most general; interactive when no command provided)
        _create = self._resolve_base("submit")
        if isinstance(_create, click.Command):
            # Override help text to match "create" semantics instead of "run"
            _create.help = "Create a new compute instance"
            grp.add_command(_create, name="create")

        # delete → cancel
        _delete = self._resolve_base("cancel")
        if isinstance(_delete, click.Command):
            # Override help text to match "delete" semantics instead of "cancel"
            _delete.help = """Delete compute instances - pattern matching uses wildcards by default

        Example: flow instance delete -n 'dev-*'"""

            # Also update the docstring to use instance delete examples
            if _delete.callback and _delete.callback.__doc__:
                original_doc = _delete.callback.__doc__
                # Replace all occurrences of "flow cancel" with "flow instance delete"
                updated_doc = original_doc.replace("flow cancel", "flow instance delete")
                # Update the first line to use "Delete" instead of "Cancel"
                updated_doc = updated_doc.replace(
                    "Cancel a running task.", "Delete a compute instance."
                )
                _delete.callback.__doc__ = updated_doc

            grp.add_command(_delete, name="delete")

        # list → status (list tasks/hosts)
        _list = self._resolve_base("status")
        if isinstance(_list, click.Command):
            # Also update the docstring to use instance list examples
            if _list.callback and _list.callback.__doc__:
                original_doc = _list.callback.__doc__
                # Replace all occurrences of "flow status" with "flow instance list"
                updated_doc = original_doc.replace("flow status", "flow instance list")
                _list.callback.__doc__ = updated_doc

            grp.add_command(_list, name="list")

        # info → status <name> (with corrected help text)
        _info = self._resolve_base("status")
        if isinstance(_info, click.Command):
            # Override help text to match "info" semantics instead of "list"
            _info.help = "Show detailed information about a specific instance"
            grp.add_command(_info, name="info")

        return grp


command = InstanceCommand()
