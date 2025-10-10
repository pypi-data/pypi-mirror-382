"""Setup command for Flow SDK configuration.

Supports both interactive wizard and direct configuration via flags.

Examples:
    Interactive setup:
        $ flow setup

    Direct configuration:
        $ flow setup --provider mithril --api-key fkey_xxx --project myproject

    Dry run to preview:
        $ flow setup --provider mithril --dry-run
"""

import asyncio
import logging
import os
from pathlib import Path

import click
import yaml
from rich.markup import escape

from flow.cli.commands.base import BaseCommand
from flow.cli.utils.config_validator import ConfigValidator
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.lazy_imports import import_attr as _import_attr
from flow.cli.utils.theme_manager import theme_manager
from flow.sdk.helpers.masking import mask_api_key, mask_config_for_display
from flow.sdk.setup import get_adapter as _get_adapter
from flow.sdk.setup import list_providers as _list_providers
from flow.sdk.setup import register_providers as _register_providers

# Import private components
# Avoid static imports from core; import lazily where needed

logger = logging.getLogger(__name__)

# Create console instance
console = theme_manager.create_console()


def _load_existing_api_key() -> str | None:
    """Load existing API key from config if available.

    Returns:
        API key string if found and valid, None otherwise
    """
    ConfigLoader = _import_attr("flow.application.config.loader", "ConfigLoader", default=None)
    if ConfigLoader:
        loader = ConfigLoader()
        sources = loader.load_all_sources()
        existing_api_key = sources.api_key
        if existing_api_key and not existing_api_key.startswith("YOUR_"):
            return existing_api_key
    return None


def run_setup_wizard(provider: str | None = None, environment: str = "production") -> bool:
    """Run the setup wizard for the resolved provider.

    If provider is None, attempt to detect from existing config or prompt.

    Args:
        provider: Provider name to use
        environment: Environment to configure (production or staging)
    """
    from flow.cli.utils.lazy_imports import import_attr as _import_attr

    GenericSetupWizard = _import_attr(
        "flow.core.generic_setup_wizard", "GenericSetupWizard", default=None
    )

    # Register providers first (lazy import)
    # Ensure providers are registered via SDK shim (no-op when not available)
    _register_providers()

    resolved_provider = provider

    # Validate explicitly provided provider
    if resolved_provider:
        adapter = _get_adapter(resolved_provider)
        if not adapter:
            available_providers = _list_providers()
            if not available_providers:
                raise RuntimeError("Unexpected error: no providers available.")

            console.print(
                f"[error]Error:[/error] Unknown or unavailable provider: {escape(str(resolved_provider))}"
            )
            console.print(f"\n[dim]Available providers:[/dim] {', '.join(available_providers)}")
            return False

    if not resolved_provider:
        # Try to detect from existing config
        from flow.cli.utils.lazy_imports import import_attr as _import_attr

        try:
            ConfigLoader = _import_attr(
                "flow.application.config.loader", "ConfigLoader", default=None
            )
            loader = ConfigLoader() if ConfigLoader else None
            current = loader.load_all_sources()
            resolved_provider = current.provider or None
        except Exception:  # noqa: BLE001
            resolved_provider = None

    # If resolved provider is 'mock' but demo adapter is disabled, treat as unresolved
    try:
        import os as _os

        if (resolved_provider or "").strip().lower() == "mock":
            demo_enabled = str(_os.environ.get("FLOW_ENABLE_DEMO_ADAPTER", "")).strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
            if not demo_enabled:
                resolved_provider = None
    except Exception:  # noqa: BLE001
        pass

    if not resolved_provider:
        # If still not resolved, and only one adapter exists, use it; otherwise list providers
        providers = _list_providers() or ["mithril"]
        if len(providers) == 1:
            resolved_provider = providers[0]
        elif len(providers) > 1:
            # Prompt user to select a provider (fallback to first if non-interactive)
            try:
                from flow.cli.ui.components import InteractiveSelector, SelectionItem

                options = [
                    SelectionItem(value=p, id=p, title=p.title(), subtitle="", status="")
                    for p in providers
                ]
                selector = InteractiveSelector(
                    options,
                    lambda x: x,
                    title="Select provider",
                    breadcrumbs=["Flow Setup", "Provider"],
                    preferred_viewport_size=5,
                )
                choice = selector.select()
                resolved_provider = choice if isinstance(choice, str) else None
            except Exception:  # noqa: BLE001
                resolved_provider = providers[0]

    # Set environment variables before creating the adapter so it picks up the correct API URL
    original_api_url = os.environ.get("MITHRIL_API_URL")
    original_config_path = os.environ.get("FLOW_CONFIG_PATH")

    try:
        # Import API URL constants
        from flow.adapters.providers.builtin.mithril.core.constants import (
            MITHRIL_API_PRODUCTION_URL,
            MITHRIL_API_STAGING_URL,
        )

        if environment == "staging":
            os.environ["MITHRIL_API_URL"] = MITHRIL_API_STAGING_URL
            os.environ["FLOW_CONFIG_PATH"] = str(Path.home() / ".flow" / "config-staging.yaml")
        else:  # production (default)
            os.environ["MITHRIL_API_URL"] = MITHRIL_API_PRODUCTION_URL
            os.environ["FLOW_CONFIG_PATH"] = str(Path.home() / ".flow" / "config.yaml")

        # Resolve adapter, with a direct-import fallback for Mithril to avoid
        # registry fragility on some environments.
        adapter = _get_adapter(resolved_provider or "")

        if not adapter:
            console.print(f"[error]Error: Provider not available: {resolved_provider}[/error]")
            # If multiple providers are available, try first available as a fallback
            try:
                providers = _list_providers()
                if providers:
                    alt = providers[0]
                    alt_adapter = _get_adapter(alt)
                    if alt_adapter:
                        console.print(
                            f"[warning]Hint:[/warning] Falling back to provider '{alt}'. Run 'flow setup --provider mithril' once the Mithril adapter is available."
                        )
                        adapter = alt_adapter
                    else:
                        return False
                else:
                    return False
            except Exception:  # noqa: BLE001
                return False

        if GenericSetupWizard is None:
            console.print("[error]Setup wizard is unavailable in this environment[/error]")
            return False

        wizard = GenericSetupWizard(console, adapter)
        success = wizard.run()

        # If wizard succeeded, save the environment setting for persistent switching
        if success:
            from flow.application.config.config import _set_current_environment

            _set_current_environment(environment)

        return success
    except KeyboardInterrupt:
        console.print("\n\n[warning]Setup cancelled[/warning]")
        return False
    except Exception as e:
        console.print(f"\n\n[error]Setup error:[/error] {escape(str(e))}")
        logger.exception("Setup wizard error")
        return False
    finally:
        # Restore original environment variables
        if original_api_url is not None:
            os.environ["MITHRIL_API_URL"] = original_api_url
        else:
            os.environ.pop("MITHRIL_API_URL", None)

        if original_config_path is not None:
            os.environ["FLOW_CONFIG_PATH"] = original_config_path
        else:
            os.environ.pop("FLOW_CONFIG_PATH", None)


class SetupCommand(BaseCommand):
    """Setup command implementation.

    Handles both interactive wizard mode and direct configuration
    via command-line options.
    """

    def __init__(self):
        """Initialize setup command."""
        super().__init__()
        self.validator = ConfigValidator()

    @property
    def name(self) -> str:
        return "setup"

    @property
    def help(self) -> str:
        return "Configure credentials and provider settings"

    def get_command(self) -> click.Command:
        # Demo mode removed; no demo-aware decorations needed

        @click.command(name=self.name, help=self.help)
        @click.option("--provider", envvar="FLOW_PROVIDER", help="Provider to use")
        # Demo mode disabled for initial release
        # @click.option("--demo", is_flag=True, help="Enable demo mode: configure mock provider (no real provisioning)")
        # NOTE: Using simple environment flag (production/staging) as a temporary solution.
        # A more flexible approach using profiles or API URL anchoring would require
        # config.yaml redesign.
        @click.option(
            "--environment",
            type=click.Choice(["production", "staging"]),
            default="production",
            help="Environment to configure (production or staging)",
            hidden=True,
        )
        @click.option("--api-key", help="API key for authentication")
        @click.option("--project", help="Project name")
        @click.option("--api-url", help="API endpoint URL")
        @click.option("--dry-run", is_flag=True, help="Show configuration without saving")
        @click.option(
            "--output",
            type=click.Path(dir_okay=False),
            help="Write dry-run YAML to file (with --dry-run)",
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed setup information")
        @click.option("--reset", is_flag=True, help="Reset configuration to start fresh")
        @click.option("--show", is_flag=True, help="Print current resolved configuration and exit")
        @click.option("--yes", is_flag=True, help="Non-interactive; answer yes to prompts (CI)")
        # @demo_aware_command(flag_param="demo")
        @cli_error_guard(self)
        def setup(
            provider: str | None,
            # demo: bool,
            environment: str,
            api_key: str | None,
            project: str | None,
            api_url: str | None,
            dry_run: bool,
            output: str | None,
            verbose: bool,
            reset: bool,
            show: bool,
            yes: bool,
        ):
            """Configure Flow.

            \b
            Examples:
                flow setup                              # Interactive setup wizard (production)
                flow setup --environment staging       # Configure for staging environment
                flow setup --dry-run                   # Preview configuration
                flow setup --show                      # Show current configuration
                flow setup --provider mithril --api-key xxx  # Direct setup

            Environment switching:
                flow setup --environment staging       # All future commands use staging
                flow setup --environment production    # All future commands use production

            Use 'flow setup --verbose' for detailed configuration options.
            """
            # Demo path removed

            if verbose and not any([provider, api_key, project, api_url, dry_run]):
                # Detailed, read-only explainer for init and SSH keys.
                self._print_verbose_help()
                return

            # Handle --show
            if show:
                try:
                    import importlib

                    import yaml as _yaml

                    ConfigManager = importlib.import_module(
                        "flow.application.config.manager"
                    ).ConfigManager
                    manager = ConfigManager()
                    sources = manager.load_sources()
                    # Build a user-facing view and mask sensitive values
                    from flow.application.config.config import _get_current_environment

                    show_dict = {
                        "environment": _get_current_environment(),
                        "provider": sources.provider,
                        "api_key": mask_api_key(sources.api_key),
                        "mithril": sources.get_mithril_config(),
                    }
                    console.print(_yaml.safe_dump(show_dict, default_flow_style=False))
                except Exception as e:  # noqa: BLE001
                    console.print(f"[error]Error loading configuration:[/error] {escape(str(e))}")
                    raise click.exceptions.Exit(1)
                return

            # Run async function safely in or out of an existing loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                try:
                    import nest_asyncio  # type: ignore

                    try:
                        nest_asyncio.apply()
                    except Exception:  # noqa: BLE001
                        pass
                except Exception:  # noqa: BLE001
                    pass
                loop.run_until_complete(
                    self._init_async(
                        provider,
                        environment,
                        api_key,
                        project,
                        api_url,
                        dry_run,
                        verbose,
                        reset,
                        output_path=output,
                        assume_yes=yes,
                    )
                )
            else:
                asyncio.run(
                    self._init_async(
                        provider,
                        environment,
                        api_key,
                        project,
                        api_url,
                        dry_run,
                        verbose,
                        reset,
                        output_path=output,
                        assume_yes=yes,
                    )
                )

        return setup

    def _print_verbose_help(self) -> None:
        """Print detailed, read-only help for `flow setup --verbose`.

        This explains what init configures, where files live, SSH key behavior,
        configuration precedence, canonical environment variables, and useful
        follow-up commands. It does not mutate any state.
        """
        from rich.panel import Panel as _Panel

        from flow.cli.utils.icons import flow_icon as _flow_icon
        from flow.cli.utils.theme_manager import theme_manager as _tm

        console.print("")
        bullet = "[muted]•[/muted]"
        border = _tm.get_color("table.border")

        # Header panel
        header = _Panel(
            f"[bold]{_flow_icon()} Flow — Detailed Guide[/bold]\n[muted]Setup configures your environment; it never provisions resources.[/muted]",
            border_style=border,
            expand=False,
        )
        console.print(header)
        console.print("")

        # What this configures
        body1 = "\n".join(
            [
                f"  {bullet} Provider (backend)",
                f"  {bullet} API key (verified)",
                f"  {bullet} Default project",
                f"  {bullet} Default SSH key behavior",
            ]
        )
        console.print(
            _Panel(
                body1,
                title="[accent][bold]What This Configures[/bold][/accent]",
                border_style=border,
                expand=False,
            )
        )
        console.print("")

        # Where configuration is saved
        body2 = "\n".join(
            [
                f"  {bullet} [repr.path]~/.flow/config.yaml[/repr.path]  [muted]— user config[/muted]",
                f"  {bullet} [repr.path]./.flow/config.yaml[/repr.path]  [muted]— project override[/muted]",
                f"  {bullet} [repr.path]~/.flow/env.sh[/repr.path]  [muted]— optional env script (source it)[/muted]",
            ]
        )
        console.print(
            _Panel(
                body2,
                title="[accent][bold]Where It’s Saved[/bold][/accent]",
                border_style=border,
                expand=False,
            )
        )
        console.print("")

        # SSH keys
        body3 = "\n".join(
            [
                f"  {bullet} Recommended: Generate on Mithril",
                f"  {bullet} Saves private key under [repr.path]~/.flow/keys/[/repr.path] with secure permissions",
                f"  {bullet} Private keys are never uploaded (only public keys are uploaded when needed)",
                f"  {bullet} Existing local keys: [repr.path]~/.ssh/[/repr.path] (id_ed25519, id_rsa, id_ecdsa)",
                f"  {bullet} Configure once in YAML (provider, api_key, project, ssh_keys)",
            ]
        )
        console.print(
            _Panel(
                body3,
                title="[accent][bold]SSH Keys[/bold][/accent]",
                border_style=border,
                expand=False,
            )
        )
        console.print("")

        # Precedence and env
        body4 = "\n".join(
            [
                f"  {bullet} Precedence: Environment → Config files → Interactive init",
                f"  {bullet} MITHRIL_API_KEY",
                f"  {bullet} MITHRIL_PROJECT",
                f"  {bullet} MITHRIL_SSH_KEYS  [muted]— comma-separated IDs or paths[/muted]",
                f"  {bullet} MITHRIL_SSH_KEY   [muted]— absolute private key path[/muted]",
            ]
        )
        console.print(
            _Panel(
                body4,
                title="[accent][bold]Configuration & Environment[/bold][/accent]",
                border_style=border,
                expand=False,
            )
        )
        console.print("")

        # Useful commands
        body5 = "\n".join(
            [
                f"  {bullet} List known keys: [accent]flow ssh-key list [/accent]",
                f"  {bullet} Upload a local key: [accent]flow ssh-key upload ~/.ssh/id_ed25519.pub[/accent]",
                f"  {bullet} Inspect a key:      [accent]flow ssh-key info <sshkey_id>[/accent]",
                f"  {bullet} Health check:       [accent]flow health[/accent]",
            ]
        )
        console.print(
            _Panel(
                body5,
                title="[accent][bold]Useful Commands[/bold][/accent]",
                border_style=border,
                expand=False,
            )
        )
        console.print("")

        # Provider specifics
        body6 = "\n".join(
            [
                f"  {bullet} SSH keys are per-project; admin-required keys are auto-included on launch",
            ]
        )
        console.print(
            _Panel(
                body6,
                title="[accent][bold]Provider Specifics (Mithril)[/bold][/accent]",
                border_style=border,
                expand=False,
            )
        )
        console.print("")

        # Next steps panel (reuse shared renderer)
        self.show_next_actions(
            [
                "flow health",
                "flow example gpu-test    # GPU check starter",
                "flow status",
            ]
        )

    async def _init_async(
        self,
        provider: str | None,
        environment: str,
        api_key: str | None,
        project: str | None,
        api_url: str | None,
        dry_run: bool,
        verbose: bool = False,
        reset: bool = False,
        output_path: str | None = None,
        assume_yes: bool = False,
    ):
        """Execute setup command.

        Args:
            provider: Provider name
            api_key: API key for authentication
            project: Project name
            api_url: Custom API endpoint
            dry_run: Preview without saving
            reset: Reset existing configuration first
        """
        # Handle reset flag first
        if reset:
            if await self._reset_configuration():
                from flow.cli.utils.theme_manager import theme_manager as _tm

                success_color = _tm.get_color("success")
                console.print(
                    f"[{success_color}]✓[/{success_color}] Configuration reset successfully"
                )
                if not (provider or api_key or project or api_url):
                    console.print("\nStarting fresh setup...")
                    console.print("")  # Add blank line before wizard
            else:
                return  # User cancelled or error occurred

        # Demo mode removed: no special fast-paths for 'mock' provider

        # Treat as non-interactive only when actual configuration flags are provided.
        # Having only a provider value (e.g., from demo mode env default) should not
        # force non-interactive mode; users expect the interactive wizard in that case.
        explicit_non_interactive = bool(api_key or project or api_url or dry_run)

        if explicit_non_interactive:
            # Non-interactive mode with provided options
            success = await self._configure_with_options(
                provider, environment, api_key, project, api_url, dry_run, output_path
            )
        else:
            # Interactive mode
            if assume_yes:
                console.print(
                    "[error]Error:[/error] --yes requires non-interactive options. Provide --provider and related flags."
                )
                return False
            # Pass provider and environment if given; otherwise let wizard resolve
            success = run_setup_wizard(provider, environment)
            if success:
                # The wizard already displays a provider-specific completion panel.
                # Show only next steps here to avoid duplicate success banners.
                self.show_next_actions(
                    [
                        "Run the GPU check starter: [accent]flow example gpu-test[/accent]",
                        "Create an instance: [accent]flow instance create -i h100 -N 8[/accent]",
                        "Monitor instances: [accent]flow instance list[/accent]",
                        "Generate a template: [accent]flow template task -o task.yaml[/accent]",
                    ],
                    max_items=4,
                )

        # Set up shell completion after successful configuration (not on dry run)
        if success and not dry_run:
            self._setup_shell_completion()

        if not success:
            raise click.exceptions.Exit(1)

    async def _configure_with_options(
        self,
        provider: str | None,
        environment: str,
        api_key: str | None,
        project: str | None,
        api_url: str | None,
        dry_run: bool,
        output_path: str | None,
    ) -> bool:
        """Configure using command-line options.

        Prompts for missing required values if needed.
        Validates provider and saves configuration.

        Returns:
            bool: True if configuration was successful, False otherwise
        """
        # Import API URL constants
        from flow.adapters.providers.builtin.mithril.core.constants import (
            MITHRIL_API_PRODUCTION_URL,
            MITHRIL_API_STAGING_URL,
        )

        # Register providers (lazy import)
        from flow.cli.utils.lazy_imports import import_attr as _import_attr

        _reg = _import_attr("flow.core.setup_registry", "register_providers", default=None)
        try:
            if _reg:
                _reg()
        except Exception:  # noqa: BLE001
            pass

        # Resolve provider for non-interactive path with sensible defaults
        if not provider:
            adapters = _list_providers() or ["mithril"]
            if len(adapters) == 1:
                provider = adapters[0]
            elif "mithril" in adapters:
                provider = "mithril"
            else:
                console.print(
                    "[error]Error:[/error] Provider must be specified with --provider in non-interactive mode"
                )
                return False

        # Resolve adapter via SDK setup registry
        adapter = _get_adapter(provider)
        if not adapter:
            console.print(
                f"[error]Error:[/error] Unknown or unavailable provider: {escape(str(provider))}"
            )
            return False

        # Check required fields early in non-interactive mode
        if not dry_run:
            required_fields = [f.name for f in adapter.get_configuration_fields() if f.required]
            provided_fields = {"provider"}  # provider is always set
            if api_key:
                provided_fields.add("api_key")
            if project:
                provided_fields.add("project")
            if api_url:
                provided_fields.add("api_url")

            missing = [name for name in required_fields if name not in provided_fields]
            if missing:
                console.print(
                    f"[error]Missing required fields for non-interactive setup:[/error] {', '.join(missing)}"
                )
                console.print(
                    "\n[dim]Hint:[/dim] Provide all required fields or run [accent]flow setup[/accent] interactively"
                )
                return False

        # Build config from provided options only (no prompts in non-interactive path)
        config: dict = {"provider": provider}

        # Validate all fields first (don't show success messages until all pass)
        if not dry_run:
            validation_context = {}

            # Validate API key
            if api_key:
                vr = adapter.validate_field("api_key", api_key)
                if not vr.is_valid:
                    console.print(f"[error]Invalid API key:[/error] {escape(str(vr.message))}")
                    return False
                validation_context["api_key"] = api_key

            # Validate project (only if we have an API key to validate with)
            if project:
                # If no API key provided via flag, try to load from existing config
                if not validation_context.get("api_key"):
                    existing_api_key = _load_existing_api_key()
                    if existing_api_key:
                        # Validate the existing API key before using it
                        vr = adapter.validate_field("api_key", existing_api_key)
                        if not vr.is_valid:
                            console.print(
                                f"[error]Existing API key is invalid:[/error] {escape(str(vr.message))}"
                            )
                            console.print(
                                "\n[dim]Hint:[/dim] Provide a valid --api-key or run 'flow setup' to reconfigure."
                            )
                            return False
                        validation_context["api_key"] = existing_api_key

                # Check if we have an API key for validation
                if not validation_context.get("api_key"):
                    console.print(
                        "[error]Cannot validate project:[/error] API key is required. "
                        "Provide --api-key or run 'flow setup' to configure authentication first."
                    )
                    return False

                vr = adapter.validate_field("project", project, validation_context)
                if not vr.is_valid:
                    console.print(f"[error]Invalid project:[/error] {escape(str(vr.message))}")
                    return False

            # All validations passed - show success messages
            if api_key:
                from flow.cli.utils.theme_manager import theme_manager as _tm2

                success_color = _tm2.get_color("success")
                console.print(
                    f"[{success_color}]✓[/{success_color}] API key validated: {mask_api_key(api_key)}"
                )

            if project:
                from flow.cli.utils.theme_manager import theme_manager as _tm3

                success_color = _tm3.get_color("success")
                console.print(f"[{success_color}]✓[/{success_color}] Project: {project}")

            # Cost awareness warning
            if provider == "mithril" and api_key:
                console.print(
                    "\n[dim]Note:[/dim] Running tasks provisions real infrastructure and may incur costs."
                )
                console.print("Use [accent]--dry-run[/accent] to preview.")

        # Build final config
        if api_key:
            config["api_key"] = api_key
        if project:
            config["project"] = project

        # Set API URL based on environment if not explicitly provided
        if api_url:
            config["api_url"] = api_url
        elif environment == "staging":
            config["api_url"] = MITHRIL_API_STAGING_URL
        else:  # production (default)
            config["api_url"] = MITHRIL_API_PRODUCTION_URL

        # Set environment-specific config path temporarily for saving
        original_config_path = os.environ.get("FLOW_CONFIG_PATH")
        try:
            if environment == "staging":
                os.environ["FLOW_CONFIG_PATH"] = str(Path.home() / ".flow" / "config-staging.yaml")
            else:  # production (default)
                os.environ["FLOW_CONFIG_PATH"] = str(Path.home() / ".flow" / "config.yaml")

            if dry_run:
                console.print("\n[bold]Configuration (dry run)[/bold]")
                console.print("─" * 50)
                # Create masked config for display based on field specs
                display_config = mask_config_for_display(config, adapter.get_configuration_fields())
                console.print(yaml.safe_dump(display_config, default_flow_style=False))
                if output_path:
                    try:
                        with open(output_path, "w") as f:
                            yaml.safe_dump(display_config, f, default_flow_style=False)
                        from flow.cli.utils.theme_manager import theme_manager as _tm3

                        success_color = _tm3.get_color("success")
                        console.print(
                            f"\n[{success_color}]✓[/{success_color}] Wrote masked preview to {output_path}"
                        )
                    except Exception as e:  # noqa: BLE001
                        console.print(f"[error]Error writing output file:[/error] {escape(str(e))}")
                        return False
                return True

            # Save via adapter (which uses ConfigManager) to ensure consistent behavior
            saved = adapter.save_configuration(config)
            if not saved:
                console.print("[error]Failed to save configuration[/error]")
                return False

            # Save the current environment setting for persistent environment switching
            from flow.application.config.config import _set_current_environment

            _set_current_environment(environment)

            from flow.cli.utils.theme_manager import theme_manager as _tm4

            success_color = _tm4.get_color("success")
            config_file_name = "config-staging.yaml" if environment == "staging" else "config.yaml"
            console.print(
                f"\n[{success_color}]✓[/{success_color}] Configuration saved to ~/.flow/{config_file_name}"
            )
            if environment == "staging":
                console.print(
                    f"[{success_color}]✓[/{success_color}] Environment set to staging - all future flow commands will use staging"
                )
            self.show_next_actions(
                [
                    "Test your setup: [accent]flow health[/accent]",
                    "Run GPU test: [accent]flow example gpu-test[/accent]",
                    "View examples: [accent]flow example[/accent]",
                    "Submit your first task: [accent]flow submit <config.yaml>[/accent]",
                    "(Optional) Upload existing SSH key: [accent]flow ssh-keys upload ~/.ssh/id_ed25519.pub[/accent]",
                ]
            )
            return True
        finally:
            # Restore original config path
            if original_config_path is not None:
                os.environ["FLOW_CONFIG_PATH"] = original_config_path
            else:
                os.environ.pop("FLOW_CONFIG_PATH", None)

    async def _prompt_for_value(
        self, name: str, password: bool = False, default: str | None = None
    ) -> str | None:
        """Prompt user for configuration value.

        Args:
            name: Value name to prompt for
            password: Hide input for sensitive values
            default: Default value if none provided

        Returns:
            User input or None
        """
        from rich.prompt import Prompt

        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: Prompt.ask(name, password=password, default=default)
        )

    # Legacy method removed in favor of mask_utils.mask_api_key

    async def _reset_configuration(self) -> bool:
        """Reset Flow configuration to initial state.

        Removes configuration files with a safety prompt that lists what will be
        deleted and asks for confirmation.

        Returns:
            bool: True if reset, False if cancelled
        """
        from rich.prompt import Confirm

        flow_dir = Path.home() / ".flow"
        files_to_clear = []

        # Check what files exist
        if flow_dir.exists():
            config_file = flow_dir / "config.yaml"
            if config_file.exists():
                files_to_clear.append(config_file)

            # Check for provider-specific credential files
            for cred_file in flow_dir.glob("credentials.*"):
                files_to_clear.append(cred_file)

        if not files_to_clear:
            console.print("[warning]No configuration files found to reset[/warning]")
            return True

        # Show what will be deleted
        console.print("\n[bold]The following files will be removed:[/bold]")
        for file in files_to_clear:
            console.print(f"  • {file}")

        # Safety prompt before deletion
        console.print("")
        confirm = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: Confirm.ask("[warning]Are you sure you want to reset configuration?[/warning]"),
        )

        if not confirm:
            console.print("[dim]Reset cancelled[/dim]")
            return False

        # Perform deletion
        for file in files_to_clear:
            try:
                file.unlink()
            except Exception as e:  # noqa: BLE001
                console.print(f"[error]Error deleting {file}: {escape(str(e))}[/error]")
                return False

        return True

    def _setup_shell_completion(self):
        """Set up shell completion after successful init.

        Adds a guarded completion line to the user's shell config when
        possible. Skips silently if the shell cannot be detected.
        """
        try:
            import shutil
            from pathlib import Path

            # Check if flow command is available
            flow_cmd = shutil.which("flow")
            if not flow_cmd:
                return  # Command not in PATH yet

            # Detect user's shell
            shell_path = os.environ.get("SHELL", "")
            shell_name = os.path.basename(shell_path)

            if shell_name not in ["bash", "zsh", "fish"]:
                # Try to detect from parent process
                try:
                    import psutil

                    parent = psutil.Process(os.getppid())
                    parent_name = parent.name()
                    for shell in ["bash", "zsh", "fish"]:
                        if shell in parent_name:
                            shell_name = shell
                            break
                except Exception:  # noqa: BLE001
                    pass

            if shell_name not in ["bash", "zsh", "fish"]:
                return  # Can't detect shell, skip completion setup

            # Determine shell config file
            shell_configs = {
                "bash": "~/.bashrc",
                "zsh": "~/.zshrc",
                "fish": "~/.config/fish/config.fish",
            }

            config_file = Path(shell_configs.get(shell_name, "")).expanduser()
            if not config_file or not config_file.parent.exists():
                return

            # Check if completion is already installed (robust detection)
            completion_marker = "# Flow CLI completion"
            if config_file.exists():
                content = config_file.read_text()
                try:
                    from flow.cli.ui.runtime.shell_completion import (
                        CompletionCommand as _CompletionCommand,
                    )

                    if _CompletionCommand()._is_completion_present(shell_name, content):
                        return  # Already installed or equivalent present
                except Exception:  # noqa: BLE001
                    if completion_marker in content:
                        return  # Conservative check

            # Generate appropriate, shell-guarded completion line
            try:
                from flow.cli.ui.runtime.shell_completion import (
                    CompletionCommand as _CompletionCommand,
                )

                completion_line = _CompletionCommand()._get_completion_line(shell_name)
            except Exception:  # noqa: BLE001
                # Fallback to conservative guarded lines
                if shell_name == "bash":
                    completion_line = 'if [ -n "${BASH_VERSION-}" ]; then eval "$(_FLOW_COMPLETE=bash_source flow)"; fi'
                elif shell_name == "zsh":
                    completion_line = 'if [ -n "${ZSH_VERSION-}" ]; then eval "$(_FLOW_COMPLETE=zsh_source flow)"; fi'
                elif shell_name == "fish":
                    completion_line = (
                        'if test -n "$FISH_VERSION"; _FLOW_COMPLETE=fish_source flow | source; end'
                    )
                else:
                    return

            # Add completion to shell config
            with open(config_file, "a") as f:
                f.write(f"\n{completion_marker}\n{completion_line}\n")

            from rich.panel import Panel as _Panel

            from flow.cli.utils.theme_manager import theme_manager as _tm5

            # Compact summary panel for consistency
            body_lines = []
            body_lines.append(f"  [muted]Shell:[/muted] {shell_name}")
            body_lines.append(
                f"  [muted]Updated:[/muted] [repr.path]{config_file}[/repr.path] [muted]— activation line added[/muted]"
            )
            body_lines.append(
                f"  [muted]Activate now:[/muted] [accent]source {config_file}[/accent]"
            )
            body_lines.append("  [muted]Tip:[/muted] Restart your shell to persist")
            panel = _Panel(
                "\n".join(body_lines),
                title="[accent][bold]Shell Completion[/bold][/accent]",
                border_style=_tm5.get_color("table.border"),
                expand=False,
            )
            console.print("")
            console.print(panel)

        except Exception:  # noqa: BLE001
            # Silently skip if completion setup fails
            pass


# Export command instance
command = SetupCommand()
