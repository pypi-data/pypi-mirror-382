"""Mithril provider setup adapter.

Extracts Mithril-specific logic from the wizard to keep the wizard provider-agnostic
while preserving the UI and functionality.
"""

import os
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markup import escape

from flow.adapters.http.client import HttpClient
from flow.application.config.manager import ConfigManager
from flow.cli.ui.runtime.shell_completion import CompletionCommand
from flow.core.setup_adapters import ConfigField, FieldType, ProviderSetupAdapter, ValidationResult
from flow.sdk.helpers.masking import mask_api_key
from flow.utils.links import WebLinks


class MithrilSetupAdapter(ProviderSetupAdapter):
    """Mithril provider setup adapter."""

    def __init__(self, console: Console | None = None):
        """Initialize Mithril setup adapter.

        Args:
            console: Rich console for output (creates one if not provided)
        """
        # Use themed console so markup tags like [accent] follow the active theme
        if console is not None:
            self.console = console
        else:
            try:
                from flow.cli.utils.theme_manager import theme_manager as _tm

                self.console = _tm.create_console()
            except Exception:  # noqa: BLE001
                # Fallback to plain console if theme manager is unavailable
                self.console = Console()
        # Canonical API URL env var; allow FLOW_API_URL as a last-resort dev fallback
        from flow.adapters.providers.builtin.mithril.core.constants import (
            MITHRIL_API_PRODUCTION_URL,
        )

        self.api_url = os.environ.get(
            "MITHRIL_API_URL", os.environ.get("FLOW_API_URL", MITHRIL_API_PRODUCTION_URL)
        )
        # Use environment-specific config path if set, otherwise default to production
        env_config_path = os.environ.get("FLOW_CONFIG_PATH")
        if env_config_path:
            self.config_path = Path(env_config_path)
        else:
            self.config_path = Path.home() / ".flow" / "config.yaml"
        self._current_context = {}  # Store current wizard context

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "mithril"

    def get_configuration_fields(self) -> list[ConfigField]:
        """Get Mithril configuration fields."""
        return [
            ConfigField(
                name="api_key",
                field_type=FieldType.PASSWORD,
                required=True,
                mask_display=True,
                help_url=WebLinks.api_keys(),
                help_text="Get your API key from Mithril",
                default=None,
                display_name="API Key",
            ),
            ConfigField(
                name="project",
                field_type=FieldType.CHOICE,
                required=True,
                dynamic_choices=True,
                help_text="Select your Mithril project",
                depends_on=["api_key"],
                empty_choices_hint="Requires API key to list projects",
            ),
            ConfigField(
                name="default_ssh_key",
                field_type=FieldType.CHOICE,
                required=False,  # Optional: auto-handled at runtime with fallbacks
                dynamic_choices=True,
                help_url=WebLinks.ssh_keys(),
                help_text=(
                    "Pick an existing project key or generate one on Mithril (recommended). "
                    "Keys marked '(local copy)' have a matching local private key. "
                    "Private keys are never uploaded."
                ),
                display_name="Default SSH Key",
                depends_on=["api_key", "project"],
                empty_choices_hint="Requires API key and project to list SSH keys",
            ),
        ]

    def validate_field(
        self, field_name: str, value: str, context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Validate a single field value."""
        # Update current context if provided
        if context:
            self._current_context.update(context)

        if field_name == "api_key":
            return self._validate_api_key(value)
        elif field_name == "project":
            return self._validate_project(value)
        elif field_name == "default_ssh_key":
            return self._validate_ssh_key(value)
        else:
            return ValidationResult(is_valid=False, message=f"Unknown field: {field_name}")

    def get_dynamic_choices(self, field_name: str, context: dict[str, Any]) -> list[str]:
        """Get dynamic choices for a field."""
        # Store the current context for use in validation
        self._current_context = context

        if field_name == "project":
            return self._get_project_choices(context.get("api_key"))
        elif field_name == "default_ssh_key":
            return self._get_ssh_key_choices(context.get("api_key"), context.get("project"))
        else:
            return []

    def detect_existing_config(self) -> dict[str, Any]:
        """Detect existing configuration from environment, files, etc."""
        # Use centralized manager for consistent detection/normalization
        manager = ConfigManager(self.config_path)
        detected = manager.detect_existing_config()

        return detected

    def save_configuration(self, config: dict[str, Any]) -> bool:
        """Save the final configuration using centralized ConfigWriter."""
        try:
            manager = ConfigManager(self.config_path)
            # Normalize and save using centralized manager
            payload = dict(config)
            payload.setdefault("provider", "mithril")
            saved = manager.save(payload)

            # Write canonical env script (no API key by default)
            manager.write_env_script(saved, include_api_key=False)

            # Set up shell completion automatically
            try:
                completion_cmd = CompletionCommand()
                shell = completion_cmd._detect_shell()
                if shell:
                    # Minimal: let the installer render a single, compact summary panel
                    completion_cmd._install_completion(shell, None)
            except Exception:  # noqa: BLE001
                pass

            return True

        except Exception:  # noqa: BLE001
            return False

    def verify_configuration(self, config: dict[str, Any]) -> tuple[bool, str | None]:
        """Verify that the configuration works end-to-end."""
        try:
            # Set environment from config
            if "api_key" in config:
                os.environ["MITHRIL_API_KEY"] = config["api_key"]
            if "project" in config:
                os.environ["MITHRIL_PROJECT"] = config["project"]

            # Test API operation
            from flow.sdk.client import Flow

            client = Flow()
            client.list_tasks(limit=1)

            # Check billing status (non-blocking)
            try:
                from flow.adapters.http.client import HttpClient

                http_client = HttpClient(
                    base_url=self.api_url,
                    headers={"Authorization": f"Bearer {config.get('api_key')}"},
                    in_setup_context=True,
                )
                billing_status = http_client.request("GET", "/v2/account/billing")
                if not billing_status.get("configured", False):
                    # Store billing status for completion message
                    # Expose as public attribute for UI to read without private access
                    self.billing_not_configured = True
                    self.console.print(
                        "\n[warning]Note: Billing not configured yet. Set it up at:[/warning]"
                    )
                    from flow.utils.links import WebLinks

                    self.console.print(f"[accent]{WebLinks.billing_settings()}[/accent]")
            except Exception:  # noqa: BLE001
                # Don't fail setup for billing check
                pass

            return True, None

        except Exception as e:  # noqa: BLE001
            return False, str(e)

    def get_welcome_message(self) -> tuple[str, list[str]]:
        """Get Mithril-specific welcome message."""
        return (
            "Welcome to Flow Setup",
            [
                "Get and validate your API key",
                "Select your project",
                "Configure SSH access",
                "Verify everything works",
            ],
        )

    def get_completion_message(self) -> str:
        """Get Mithril-specific completion message."""
        return "Setup Complete. Flow is configured and ready for GPU workloads."

    # Private helper methods

    def _validate_api_key(self, api_key: str) -> ValidationResult:
        """Validate API key format and with API."""
        # Basic format validation
        if not api_key.startswith("fkey_") or len(api_key) < 20:
            return ValidationResult(
                is_valid=False,
                message="Invalid API key format. Expected: fkey_XXXXXXXXXXXXXXXXXXXXXXXX",
            )

        # API validation
        try:
            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
                in_setup_context=True,
            )
            from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient as _Api

            _ = _Api(client).list_projects()
            masked_key = mask_api_key(api_key)
            return ValidationResult(is_valid=True, display_value=masked_key)
        except Exception as e:  # noqa: BLE001
            return ValidationResult(is_valid=False, message=f"API validation failed: {e}")

    def _validate_project(self, project: str) -> ValidationResult:
        """Validate project name against available projects."""
        if not project or len(project.strip()) == 0:
            return ValidationResult(is_valid=False, message="Project name cannot be empty")

        # Validate against API if we have an API key in context
        api_key = self._current_context.get("api_key")
        if not api_key:
            # CLI should check for this first, but return error for safety
            return ValidationResult(
                is_valid=False,
                message="API key is required to validate project. Provide --api-key or configure via 'flow setup'.",
            )

        available_projects = self._get_project_choices(api_key)
        if available_projects and project not in available_projects:
            from rich.markup import escape

            msg = f"Project '{escape(project)}' not found in your account."
            if available_projects:
                msg += f"\n\nAvailable projects: {', '.join(available_projects)}"
            return ValidationResult(is_valid=False, message=msg)

        return ValidationResult(is_valid=True, display_value=project)

    def _validate_ssh_key(self, ssh_key: str) -> ValidationResult:
        """Validate SSH key ID or handle generation requests."""
        if not ssh_key or len(ssh_key.strip()) == 0:
            return ValidationResult(is_valid=False, message="SSH key ID cannot be empty")

        # Handle platform auto-generation (recommended)
        if ssh_key == "_auto_":
            generated_key_id = self._generate_server_side_key()
            if generated_key_id:
                return ValidationResult(
                    is_valid=True, display_value=generated_key_id, processed_value=generated_key_id
                )
            return ValidationResult(is_valid=False, message="Failed to generate SSH key")

        # Handle generation options
        if ssh_key == "GENERATE_SERVER":
            generated_key_id = self._generate_server_side_key()
            if generated_key_id:
                try:
                    from rich.panel import Panel as _Panel

                    from flow.cli.utils.theme_manager import theme_manager as _tm
                    from flow.utils.links import WebLinks as _Links

                    body = [
                        f"  [muted]ID:[/muted] {generated_key_id}",
                        "  [muted]Private key:[/muted] [repr.path]~/.flow/keys/[/repr.path]",
                        f"  [muted]Manage keys:[/muted] [link]{_Links.ssh_keys()}[/link]",
                    ]
                    panel = _Panel(
                        "\n".join(body),
                        title="[accent][bold]SSH Key Generated[/bold][/accent]",
                        border_style=_tm.get_color("table.border"),
                        expand=False,
                    )
                    self.console.print("")
                    self.console.print(panel)
                except Exception:  # noqa: BLE001
                    # Minimal fallback if Rich panel/theming is unavailable
                    self.console.print(
                        f"[success]✓[/success] SSH key generated: {generated_key_id} — private key saved to ~/.flow/keys/"
                    )
                return ValidationResult(
                    is_valid=True, display_value=generated_key_id, processed_value=generated_key_id
                )
            else:
                return ValidationResult(is_valid=False, message="Failed to generate SSH key")

        # Handle skip
        if ssh_key == "none":
            return ValidationResult(
                is_valid=True, display_value="Skip SSH configuration", processed_value="_skip_"
            )

        # Regular SSH key ID
        if ssh_key.startswith("sshkey_"):
            # Non-blocking, metadata-only hint about local private key presence
            suffix = ""
            try:
                import json as _json
                from pathlib import Path as _Path

                meta_path = _Path.home() / ".flow" / "keys" / "metadata.json"
                if meta_path.exists():
                    data = _json.loads(meta_path.read_text()) or {}
                    info = data.get(ssh_key)
                    if info:
                        p = _Path(info.get("private_key_path", ""))
                        if p.exists():
                            suffix = " (local)"
            except Exception:  # noqa: BLE001
                pass

            display_value = f"Platform key ({ssh_key[:14]}...){suffix}"
        elif ssh_key == "_auto_":
            display_value = "Deprecated (_auto_)"
        else:
            display_value = "Configured"
        return ValidationResult(is_valid=True, display_value=display_value)

    def _get_project_choices(self, api_key: str | None) -> list[str]:
        """Get available projects from API."""
        if not api_key:
            return []

        try:
            from flow.adapters.http.client import HttpClient

            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
                in_setup_context=True,
            )

            # Clear project cache to ensure fresh data
            client.invalidate_project_cache()

            from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient as _Api

            projects = _Api(client).list_projects()
            return [proj["name"] for proj in projects if isinstance(projects, list)]
        except Exception:  # noqa: BLE001
            return []

    def _get_ssh_key_choices(self, api_key: str | None, project: str | None) -> list[str]:
        """Get available SSH keys from API plus generation options."""
        choices = []

        # Add generation options first
        choices.extend(
            [
                "GENERATE_SERVER|Generate new SSH key",
                "none|Skip SSH key configuration",
            ]
        )

        if not api_key or not project:
            return choices

        try:
            from flow.adapters.http.client import HttpClient

            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
                in_setup_context=True,
            )

            # Clear caches to ensure fresh data
            client.invalidate_project_cache()
            client.invalidate_ssh_keys_cache()

            from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient as _Api

            api = _Api(client)
            projects = api.list_projects()
            project_id = None
            for proj in projects:
                if proj.get("name") == project:
                    # Accept either 'fid' (preferred) or 'id'/'project_id' from API
                    project_id = proj.get("fid") or proj.get("id") or proj.get("project_id")
                    break

            if not project_id:
                return choices

            # Get existing SSH keys via manager (normalized + cached)
            ssh_manager = None
            try:
                from flow.adapters.providers.builtin.mithril.api.client import (
                    MithrilApiClient as _Api,
                )
                from flow.adapters.providers.builtin.mithril.resources.ssh import (
                    SSHKeyManager as _SSHKeyManager,
                )

                api_client = _Api(client)
                ssh_manager = _SSHKeyManager(api_client, get_project_id=lambda: project_id)
                ssh_keys = ssh_manager.list_keys()
            except Exception:  # noqa: BLE001
                # Fallback to raw API if manager import fails
                ssh_keys = client.request(
                    "GET", "/v2/ssh-keys", params={"project": project_id}, timeout_seconds=10.0
                )

            # Build a set of platform key IDs that have a matching local private key
            local_ids: set[str] = set()
            try:
                import json as _json
                from pathlib import Path as _Path

                meta_path = _Path.home() / ".flow" / "keys" / "metadata.json"
                if meta_path.exists():
                    data = _json.loads(meta_path.read_text())
                    if isinstance(data, dict):
                        for _kid, _info in data.items():
                            p = _Path((_info or {}).get("private_key_path", ""))
                            if p.exists():
                                local_ids.add(_kid)
            except Exception:  # noqa: BLE001
                pass

            # Iterate keys (supports dicts and SSHKeyModel instances)
            if isinstance(ssh_keys, list):
                for key in ssh_keys:
                    # Normalize fields for both dict and model cases
                    if isinstance(key, dict):
                        created_at = key.get("created_at", "")
                        public_key = key.get("public_key", "")
                        required = key.get("required") or key.get("is_required")
                        fid = key.get("fid")
                        key_name = key.get("name", "")
                    else:
                        # Pydantic model (SSHKeyModel)
                        created_at = getattr(key, "created_at", "")
                        public_key = getattr(key, "public_key", "")
                        required = getattr(key, "required", None) or getattr(
                            key, "is_required", None
                        )
                        fid = getattr(key, "fid", None)
                        key_name = getattr(key, "name", "")

                    fingerprint = self._extract_fingerprint(public_key or "")
                    required_flag = " (required)" if required else ""

                    # Determine if there is a matching local private key
                    has_local = False
                    try:
                        if fid:
                            if fid in local_ids:
                                has_local = True
                            elif ssh_manager is not None:
                                try:
                                    if ssh_manager.find_matching_local_key(fid):
                                        has_local = True
                                except Exception:  # noqa: BLE001
                                    has_local = False
                    except Exception:  # noqa: BLE001
                        has_local = False

                    name_display = f"{key_name}{required_flag}"
                    if has_local:
                        name_display = f"{name_display} (local)"

                    if fid:
                        choices.append(f"{fid}|{name_display}|{created_at}|{fingerprint}")

            return choices
        except Exception:  # noqa: BLE001
            return choices

    def _generate_server_side_key(self) -> str | None:
        """Generate SSH key server-side."""
        try:
            # Get current config for API access
            config = self.detect_existing_config()
            # Check wizard context first (from get_dynamic_choices), then detected config, then env vars
            api_key = (
                self._current_context.get("api_key")
                or config.get("api_key")
                or os.environ.get("MITHRIL_API_KEY")
            )
            project = (
                self._current_context.get("project")
                or config.get("project")
                or os.environ.get("MITHRIL_PROJECT")
            )

            if not api_key or not project:
                self.console.print(
                    "[error]API key and project required for SSH key generation[/error]"
                )
                return None

            # Set up client
            from flow.adapters.http.client import HttpClient

            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
                in_setup_context=True,
            )

            # Clear caches to ensure fresh data
            client.invalidate_project_cache()
            client.invalidate_ssh_keys_cache()

            # Get project ID
            from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient as _Api

            projects = _Api(client).list_projects()
            project_id = None
            for proj in projects:
                if proj.get("name") == project:
                    # Accept either 'fid' (preferred) or 'id'/'project_id' from API
                    project_id = proj.get("fid") or proj.get("id") or proj.get("project_id")
                    break

            if not project_id:
                self.console.print("[error]Could not resolve project ID[/error]")
                return None

            # Import SSH manager
            from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient as _Api
            from flow.adapters.providers.builtin.mithril.resources.ssh import SSHKeyManager

            ssh_manager = SSHKeyManager(_Api(client), get_project_id=lambda: project_id)

            # Generate server-side key
            key_id = ssh_manager.generate_server_key()
            return key_id

        except Exception as e:  # noqa: BLE001
            self.console.print(
                f"[error]Error generating SSH key: {escape(type(e).__name__)}: {escape(str(e))}[/error]"
            )
            if hasattr(e, "response"):
                self.console.print(
                    f"[error]API Response: {escape(str(getattr(e, 'response', 'N/A')))}[/error]"
                )
            return None

    def _create_env_script(self, config: dict[str, Any]):
        """Create shell script with clean provider-specific environment variables.

        Clean, decisive approach: MITHRIL_* variables only.
        No legacy compatibility - users adapt to the right way.
        """
        env_script = self.config_path.parent / "env.sh"

        with open(env_script, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Flow SDK Mithril provider environment variables\n")
            f.write("# Source this file: source ~/.flow/env.sh\n\n")

            # Project - provider-specific canonical naming only
            if "project" in config:
                f.write(f'export MITHRIL_PROJECT="{config["project"]}"\n')

            # SSH keys - provider-specific naming only
            if "default_ssh_key" in config:
                f.write(f'export MITHRIL_SSH_KEYS="{config["default_ssh_key"]}"\n')

        env_script.chmod(0o600)

    def _extract_fingerprint(self, public_key: str) -> str:
        """Extract a short SHA256 fingerprint for display."""
        if not public_key:
            return ""
        try:
            from flow.core.utils.ssh_key import (
                sha256_fingerprint_from_public_key as _fp_sha256,
            )

            full = _fp_sha256(public_key) or ""
            if not full:
                return ""
            # full is "SHA256:..." — trim body for compact list display
            try:
                body = full.split(":", 1)[1]
            except Exception:  # noqa: BLE001
                body = full
            return f"SHA256:{body[:8]}..."
        except Exception:  # noqa: BLE001
            return ""

    def _load_existing_config(self) -> dict[str, Any]:
        """Load existing configuration from file."""
        if not self.config_path.exists():
            return {}

        try:
            import yaml

            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        except Exception:  # noqa: BLE001
            return {}
