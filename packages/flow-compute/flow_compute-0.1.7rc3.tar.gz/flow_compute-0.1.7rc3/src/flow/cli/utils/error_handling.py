"""Centralized CLI error handling utilities.

Provides a lightweight decorator that commands can use to route exceptions
through the owning BaseCommand instance's error handlers. This allows us to
remove broad try/except blocks in command bodies and keep output consistent.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

import click

from flow.cli.utils.json_output import error_json, print_json
from flow.errors import AuthenticationError

if TYPE_CHECKING:
    from rich.console import Console

F = TypeVar("F", bound=Callable[..., Any])


def cli_error_guard(owner: Any) -> Callable[[F], F]:
    """Decorator factory that routes exceptions to a command owner's handlers.

    The owner is expected to expose `handle_error(Exception|str)` and
    `handle_auth_error()` methods (as provided by BaseCommand).
    """

    def _decorate(func: F) -> F:
        @functools.wraps(func)
        def _wrapped(*args: Any, **kwargs: Any):  # type: ignore[override]
            try:
                return func(*args, **kwargs)
            except click.Abort:
                # Graceful Ctrl+C/abort from Click prompts
                try:
                    from flow.cli.commands.base import console as _console  # lazy to avoid cycles

                    _console.print("[dim]Cancelled[/dim]")
                except Exception:  # noqa: BLE001
                    pass
                raise click.exceptions.Exit(130)
            except click.ClickException:
                # Let Click manage its own exceptions
                raise
            except click.exceptions.Exit:
                # Respect explicit exits from owners or Click
                raise
            except KeyboardInterrupt:
                # Graceful Ctrl+C
                try:
                    from flow.cli.commands.base import console as _console  # lazy to avoid cycles

                    _console.print("[dim]Cancelled[/dim]")
                except Exception:  # noqa: BLE001
                    pass
                raise click.exceptions.Exit(130)
            except AuthenticationError as e:
                # Only route AUTH_001 (no auth configured) to handle_auth_error
                # Let AUTH_003/AUTH_004 show their specific error messages
                error_code = getattr(e, "error_code", None)
                if error_code == "AUTH_001":
                    try:
                        owner.handle_auth_error()
                    finally:
                        raise click.exceptions.Exit(1)
                else:
                    # Route AUTH_003, AUTH_004 etc through normal error handler
                    owner.handle_error(e)
                    raise click.exceptions.Exit(1)
            except SystemExit as e:
                if e.code != 0:
                    raise click.exceptions.Exit(e.code)
                raise
            except Exception as e:  # noqa: BLE001
                # Default: rich error panel via owner
                owner.handle_error(e)
                # handle_error raises click.Exit; if it didn't, ensure exit
                raise click.exceptions.Exit(1)

        return _wrapped  # type: ignore[return-value]

    return _decorate


def handle_cli_exception(owner: Any | None, exc: Exception) -> None:
    """Best-effort top-level handler for wrapping CLI entry invocation.

    If an owner is provided, route through it; otherwise, convert to Click exit.
    Not strictly necessary when using the decorator on commands, but useful
    as a belt-and-suspenders around the CLI entrypoint.
    """
    if isinstance(exc, click.Abort):
        try:
            from flow.cli.commands.base import console as _console  # lazy to avoid cycles

            _console.print("[dim]Cancelled[/dim]")
        except Exception:  # noqa: BLE001
            pass
        raise click.exceptions.Exit(130)
    if isinstance(exc, click.ClickException | click.exceptions.Exit):
        raise exc
    if isinstance(exc, KeyboardInterrupt):
        try:
            from flow.cli.commands.base import console as _console  # lazy to avoid cycles

            _console.print("[dim]Cancelled[/dim]")
        except Exception:  # noqa: BLE001
            pass
        raise click.exceptions.Exit(130)
    if owner is not None and isinstance(exc, AuthenticationError):
        error_code = getattr(exc, "error_code", None)
        if error_code == "AUTH_001":
            owner.handle_auth_error()
        else:
            owner.handle_error(exc)
        raise click.exceptions.Exit(1)
    if owner is not None:
        owner.handle_error(exc)
        raise click.exceptions.Exit(1)
    # No owner to render with; fail with a simple message
    raise click.ClickException(str(exc))


def render_auth_required_message(console: Console, *, output_json: bool = False) -> None:
    """Display a friendly authentication required message.

    This is a standalone utility for commands that need to handle
    authentication errors without inheriting from BaseCommand.

    Args:
        console: Rich console instance to render the message to
        output_json: If True, output JSON error instead of console message

    Example:
        >>> from flow.cli.utils.error_handling import render_auth_required_message
        >>> from flow.errors import AuthenticationError
        >>> try:
        ...     flow = sdk_factory.create_client(auto_init=True)
        ... except AuthenticationError:
        ...     render_auth_required_message(console, output_json=output_json)
        ...     return
    """
    if output_json:
        print_json(
            error_json(
                "Authentication required",
                code="AUTH_001",
                hint="Run 'flow setup' to configure your API key",
            )
        )
    else:
        console.print("")
        console.print("[yellow]⚠ Authentication required[/yellow]")
        console.print("")
        console.print("To get started, run [accent]flow setup[/accent]")
        console.print("")
