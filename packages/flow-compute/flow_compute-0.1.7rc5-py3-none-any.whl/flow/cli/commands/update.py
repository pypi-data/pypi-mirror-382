"""Self-update command for Flow CLI.

This command allows users to update the Flow SDK to the latest version
or check for available updates without installing them.
"""

import json

import click
from rich.panel import Panel
from rich.table import Table

from flow._version import get_version as get_sdk_version
from flow._version import is_stable_version, parse_version
from flow.cli.commands.base import BaseCommand
from flow.cli.utils.theme_manager import theme_manager
from flow.cli.utils.update_checker import UpdateChecker
from flow.cli.utils.update_notifier import RELEASE_TRACK_UNSTABLE, UpdateNotifier

console = theme_manager.create_console()


class UpdateCommand(BaseCommand):
    """Update command implementation."""

    @property
    def name(self) -> str:
        return "update"

    @property
    def help(self) -> str:
        return "Update Flow to the latest version"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option("--check", is_flag=True, help="Check for updates without installing")
        @click.option("--force", is_flag=True, help="Force update even if on latest version")
        @click.option("--version", help="Install specific version")
        @click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
        @click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
        @click.option(
            "--unstable", is_flag=True, help="Include pre-release versions (alpha, beta, rc)"
        )
        def update(
            check: bool,
            force: bool,
            version: str | None,
            yes: bool,
            output_json: bool,
            unstable: bool,
        ):
            """Update Flow to the latest version.

            \b
            Examples:
                flow update              # Update to latest version
                flow update --check      # Check for updates only
                flow update --check --unstable  # Check including pre-releases
                flow update --version 0.0.5  # Install specific version
                flow update --force      # Force reinstall
            """
            from rich.markup import escape

            checker = UpdateChecker(quiet=output_json)

            # If current version is unstable, check includes unstable updates by default
            # This ensures users on pre-release versions hear about newer pre-releases
            current_is_unstable = not is_stable_version(checker.current_version)
            should_check_unstable = unstable or current_is_unstable

            # Check for updates
            result = checker.check_for_updates(include_unstable=should_check_unstable)

            if check:
                # Just check, don't update
                if output_json:
                    env_info = checker.detect_environment()
                    output = {
                        "current_version": result.current_version,
                        "latest_version": result.latest_version,
                        "latest_stable_version": result.latest_stable_version,
                        "update_available": result.update_available,
                        "release_url": result.release_url,
                        "environment": {
                            "installer": env_info.get("installer"),
                            "can_update": env_info.get("can_update"),
                            "update_command": env_info.get("update_command"),
                            "is_virtual": env_info.get("is_virtual"),
                            "python_version": env_info.get("python_version"),
                        },
                    }
                    if result.error:
                        output["error"] = result.error
                    print(json.dumps(output, indent=2))
                else:
                    # Use the appropriate version based on unstable flag or current version
                    display_version = (
                        result.latest_version
                        if should_check_unstable
                        else result.latest_stable_version
                    )
                    self._display_version_info(
                        checker,
                        result.update_available,
                        display_version,
                        include_unstable=should_check_unstable,
                    )
                return

            # Perform update
            if version:
                # Install specific version
                # Validate the requested version exists on PyPI
                ver_info = checker.get_version_info(version)
                if not ver_info:
                    if output_json:
                        print(
                            json.dumps(
                                {
                                    "success": False,
                                    "error": f"Version '{version}' not found on PyPI",
                                    "previous_version": checker.current_version,
                                },
                                indent=2,
                            )
                        )
                        raise click.exceptions.Exit(1)
                    else:
                        console.print(
                            f"[error]Requested version '{escape(version)}' not found on PyPI[/error]"
                        )
                        raise click.exceptions.Exit(1)

                target = version
                if not output_json:
                    console.print(f"[accent]Installing Flow version {target}...[/accent]")
            elif not result.update_available and not force:
                if output_json:
                    print(
                        json.dumps(
                            {
                                "current_version": result.current_version,
                                "latest_version": result.latest_version,
                                "latest_stable_version": result.latest_stable_version,
                                "message": "Already on latest version",
                            }
                        )
                    )
                else:
                    success_color = theme_manager.get_color("success")
                    console.print(
                        f"[{success_color}]✓ You're already on the latest version ({result.current_version})[/{success_color}]"
                    )
                return
            else:
                # Use the appropriate version based on unstable flag or current version
                target = (
                    result.latest_version if should_check_unstable else result.latest_stable_version
                )

            # Show update info and confirm
            if not yes and not output_json:
                env_info = checker.detect_environment()

                # Display update details
                table = Table(title="Update Details", show_header=False)
                from flow.cli.utils.theme_manager import theme_manager as _tm

                table.add_column("Property", style=_tm.get_color("accent"))
                table.add_column("Value")

                table.add_row("Current Version", checker.current_version)
                table.add_row("Target Version", target or "latest")
                table.add_row("Python Version", env_info["python_version"])
                table.add_row("Environment", "Virtual" if env_info["is_virtual"] else "System")
                table.add_row("Installer", env_info["installer"] or "pip")

                console.print(table)

                if not click.confirm("\nProceed with update?"):
                    console.print("[warning]Update cancelled[/warning]")
                    return

            # Legacy rollback backups removed; users can revert with --version <previous>

            # If PyPI check failed and no explicit version was requested, bail unless forced
            # Check the appropriate version field based on unstable flag or current version
            relevant_version = (
                result.latest_version if should_check_unstable else result.latest_stable_version
            )
            if not version and relevant_version is None and not force:
                if output_json:
                    print(
                        json.dumps(
                            {
                                "success": False,
                                "error": "Unable to determine latest version from PyPI; use --force or specify --version",
                                "previous_version": checker.current_version,
                            },
                            indent=2,
                        )
                    )
                else:
                    console.print(
                        "[error]Unable to determine latest version from PyPI. Use --force or specify --version.[/error]"
                    )
                raise click.exceptions.Exit(1)

            # Perform update
            success = checker.perform_update(target_version=target, force=force)

            # Update release track preference only if user explicitly chose a version or unstable track
            if success and (version or unstable):
                # After successful update, get the actual installed version
                # This ensures we capture what was really installed, not what we thought should be
                actual_installed_version = get_sdk_version()
                notifier = UpdateNotifier()

                # If --unstable was used, explicitly set unstable track regardless of version
                if unstable:
                    notifier.set_preferred_release_track(
                        actual_installed_version, explicit_track=RELEASE_TRACK_UNSTABLE
                    )
                else:
                    # User specified a version - infer track from the actual version
                    notifier.set_preferred_release_track(actual_installed_version)

            if output_json:
                # Use the appropriate version based on unstable flag or current version
                fallback_version = (
                    result.latest_version if should_check_unstable else result.latest_stable_version
                )
                output_result = {
                    "success": success,
                    "previous_version": checker.current_version,
                    "target_version": target or fallback_version,
                }
                if not success and checker.last_error:
                    output_result["error"] = checker.last_error
                print(json.dumps(output_result, indent=2))
                if not success:
                    raise click.exceptions.Exit(1)
            elif success:
                success_color = theme_manager.get_color("success")
                console.print(f"\n[{success_color}]✓ Update complete[/{success_color}]")
                console.print(
                    "[accent]Restart your terminal or run 'flow --version' to verify[/accent]"
                )
                console.print(
                    f"[dim]To rollback: flow update --version {checker.current_version}[/dim]"
                )
            else:
                console.print("\n[error]✗ Update failed[/error]")
                console.print("[warning]Try running the update command manually:[/warning]")
                env_info = checker.detect_environment()
                console.print(f"[accent]{env_info['update_command']}[/accent]")
                raise click.exceptions.Exit(1)

        return update

    def _display_version_info(
        self,
        checker: UpdateChecker,
        update_available: bool,
        latest_version: str | None,
        include_unstable: bool = False,
    ) -> None:
        """Display version information in a nice format."""
        # Get both stable and unstable versions from checker
        result = checker.check_for_updates(include_unstable=True)
        latest_stable = result.latest_stable_version
        latest_unstable = result.latest_version

        # Determine the actual latest version by comparing stable and unstable
        actual_latest = None
        if latest_stable and latest_unstable:
            # Compare which is newer
            if parse_version(latest_unstable) > parse_version(latest_stable):
                actual_latest = latest_unstable
            else:
                actual_latest = latest_stable
        elif latest_unstable:
            actual_latest = latest_unstable
        elif latest_stable:
            actual_latest = latest_stable

        current_version = checker.current_version
        is_current_stable = is_stable_version(current_version)

        # Determine status and message
        if update_available:
            status = "[warning]🔄 Update Available[/warning]"
            message = f"A new version of Flow is available: {latest_version}"
            action = "Run 'flow update' to upgrade"
        else:
            # More nuanced messaging when no update is available
            status = "[success]✓ Up to Date[/success]"

            # Parse current version once for comparisons
            current_parsed = parse_version(current_version)

            # Check version status with clear, ordered logic
            is_on_absolute_latest = actual_latest and current_parsed >= parse_version(actual_latest)
            is_on_latest_stable = latest_stable and current_parsed == parse_version(latest_stable)

            if is_on_absolute_latest:
                message = "You're running the latest version."
            elif is_on_latest_stable:
                message = "You're running the latest stable version."
            elif is_current_stable:
                message = f"You're running a stable version: {current_version}."
            else:
                message = f"You're running a pre-release version: {current_version}."

            action = "No action needed."

        panel_content = f"""{status}

Current:        {current_version}
Latest:         {latest_unstable or "Unknown"}
Latest Stable:  {latest_stable or "Unknown"}

{message}

{action}"""

        console.print(Panel(panel_content, title="Flow Version Check"))

        # Show recent versions if available
        if checker.available_versions:
            # Filter to stable versions only unless --unstable is specified
            versions_to_show = checker.available_versions
            if not include_unstable:
                versions_to_show = [v for v in versions_to_show if is_stable_version(v)]

            recent = versions_to_show[:5]
            if recent:
                version_type = "Recent Versions" if include_unstable else "Recent Stable Versions"
                console.print(f"\n[bold]{version_type}:[/bold]")
                for v in recent:
                    if v == checker.current_version:
                        console.print(f"  • {v} [success](current)[/success]")
                    elif v == latest_version:
                        console.print(f"  • {v} [warning](latest)[/warning]")
                    else:
                        console.print(f"  • {v}")

                # Show hint about --unstable flag when showing stable versions only
                if not include_unstable:
                    console.print(
                        "\n[dim]Use --unstable to include pre-release versions (alpha, beta, rc)[/dim]"
                    )


# Export command instance
command = UpdateCommand()
