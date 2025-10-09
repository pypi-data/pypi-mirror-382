"""Update checker utility for Flow CLI.

This module provides functionality to check for and install Flow updates from PyPI.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx
from rich.markup import escape

from flow._version import get_version as get_sdk_version
from flow._version import is_stable_version, parse_version


@dataclass
class UpdateCheckResult:
    """Result of checking for updates.

    Attributes:
        current_version: Currently installed version
        latest_version: Latest version available on PyPI including pre-releases (None if check failed)
        latest_stable_version: Latest stable version available on PyPI (None if check failed)
        update_available: Whether an update is available
        release_url: URL to the PyPI release page (None if no update or check failed)
        error: Error message if check failed (None on success)
    """

    current_version: str
    latest_version: str | None
    latest_stable_version: str | None
    update_available: bool
    release_url: str | None = None
    error: str | None = None


class UpdateChecker:
    """Check for and install Flow updates.

    By default, this checker only considers stable releases for update notifications.
    Pre-release versions (alpha, beta, rc) are filtered out unless explicitly
    requested with include_unstable=True.

    Behavior:
        - Fetches all non-yanked versions from PyPI
        - By default, filters to only stable releases (no alpha/beta/rc suffixes)
        - When include_unstable=True, considers all versions including pre-releases
        - Reports the latest version based on the filter as available for update
        - If only pre-releases exist and include_unstable=False, reports no update

    Examples:
        - PyPI has: 1.0.0, 1.1.0, 1.2.0rc1 -> Reports 1.1.0 as latest (default)
        - PyPI has: 1.0.0, 1.1.0, 1.2.0rc1 -> Reports 1.2.0rc1 (with include_unstable=True)
        - User on 1.1.0, PyPI has 1.2.0rc1 -> No update (default, already on latest stable)
        - User on 1.2.0alpha1, stable is 1.1.0 -> No update (user ahead of stable)

    Args:
        quiet: If True, suppresses all console output so callers can
            implement their own output formatting (e.g., JSON mode).
        timeout: HTTP timeout in seconds for PyPI requests (default: 5.0)
    """

    PYPI_API_URL = "https://pypi.org/pypi/flow-compute/json"
    PACKAGE_NAME = "flow-compute"

    def __init__(self, quiet: bool = False, timeout: float = 5.0):
        self.current_version = self._get_current_version()
        self.latest_version: str | None = None
        self.available_versions: list[str] = []
        self.quiet = quiet
        self.timeout = timeout
        self.last_error: str | None = None

    def _get_current_version(self) -> str:
        """Get the currently installed version."""
        # Use the shared version helper for consistency across CLI and library
        return get_sdk_version()

    def check_for_updates(self, include_unstable: bool = False) -> UpdateCheckResult:
        """Check if updates are available.

        By default, only considers stable releases; pre-releases (alpha/beta/rc)
        are ignored unless include_unstable=True.

        Args:
            include_unstable: If True, include pre-release versions in the check.
                            If False (default), only stable versions are considered.

        Returns:
            UpdateCheckResult with check details. If no stable version is newer
            than current, update_available is False. If check fails, error field
            is populated.
        """
        try:
            response = httpx.get(self.PYPI_API_URL, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            # Get all non-yanked versions for compatibility checking
            non_yanked_versions = []
            for ver, releases in data["releases"].items():
                # Check if any release for this version is not yanked
                # (all releases for a version should have same yanked status)
                if releases and not releases[0].get("yanked", False):
                    non_yanked_versions.append(ver)

            self.available_versions = sorted(
                non_yanked_versions, key=lambda v: parse_version(v), reverse=True
            )

            # Determine latest_version (absolute latest including pre-releases)
            latest_version = self.available_versions[0] if self.available_versions else None

            # Determine latest_stable_version (only stable releases)
            stable_versions = [v for v in self.available_versions if is_stable_version(v)]
            latest_stable_version = stable_versions[0] if stable_versions else None

            # Choose which version to use for update comparison
            if include_unstable:
                # Use absolute latest (may be a pre-release)
                version_to_compare = latest_version
            else:
                # Use latest stable only
                version_to_compare = latest_stable_version

            # Cache for legacy compatibility
            self.latest_version = version_to_compare

            # If no version is available, return no update
            if not version_to_compare:
                return UpdateCheckResult(
                    current_version=self.current_version,
                    latest_version=latest_version,
                    latest_stable_version=latest_stable_version,
                    update_available=False,
                    release_url=None,
                    error=None,
                )

            # Compare versions
            current = parse_version(self.current_version)
            latest = parse_version(version_to_compare)

            # Get release URL
            release_url = f"https://pypi.org/project/{self.PACKAGE_NAME}/{version_to_compare}/"

            update_available = latest > current

            return UpdateCheckResult(
                current_version=self.current_version,
                latest_version=latest_version,
                latest_stable_version=latest_stable_version,
                update_available=update_available,
                release_url=release_url if update_available else None,
                error=None,
            )

        except httpx.HTTPError as e:
            self.last_error = str(e)
            error_msg = f"Error checking for updates: {e!s}"
            if not self.quiet:
                from flow.cli.utils.theme_manager import theme_manager

                console = theme_manager.create_console()
                console.print(f"[error]{escape(error_msg)}[/error]")

            return UpdateCheckResult(
                current_version=self.current_version,
                latest_version=None,
                latest_stable_version=None,
                update_available=False,
                release_url=None,
                error=error_msg,
            )
        except Exception as e:  # noqa: BLE001
            self.last_error = str(e)
            error_msg = f"Unexpected error: {e!s}"
            if not self.quiet:
                from flow.cli.utils.theme_manager import theme_manager

                console = theme_manager.create_console()
                console.print(f"[error]{escape(error_msg)}[/error]")

            return UpdateCheckResult(
                current_version=self.current_version,
                latest_version=None,
                latest_stable_version=None,
                update_available=False,
                release_url=None,
                error=error_msg,
            )

    def get_version_info(self, version_str: str) -> dict:
        """Get detailed info about a specific version."""
        try:
            response = httpx.get(self.PYPI_API_URL, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if version_str in data["releases"]:
                release = data["releases"][version_str]
                if release:
                    # Get the first distribution's info
                    dist = release[0]
                    return {
                        "version": version_str,
                        "upload_time": dist.get("upload_time", "Unknown"),
                        "size": dist.get("size", 0),
                        "python_version": dist.get("requires_python", "Unknown"),
                    }
            return {}
        except Exception:  # noqa: BLE001
            return {}

    def detect_environment(self) -> dict:
        """Detect the current Python environment."""
        env_info = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable": sys.executable,
            "is_virtual": False,
            "venv_path": None,
            "installer": None,
            "can_update": True,
            "update_command": None,
        }

        # Check if in virtual environment
        env_info["is_virtual"] = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

        if env_info["is_virtual"]:
            env_info["venv_path"] = sys.prefix

        # Detect installer (pip, uv, pipx, etc.)
        # Check if installed as a uv tool
        if "uv/tools" in sys.executable:
            env_info["installer"] = "uv-tool"
            env_info["update_command"] = f"uv tool install --upgrade {self.PACKAGE_NAME}"
        elif "uv" in sys.executable or Path(sys.executable).parent.name == "uv":
            env_info["installer"] = "uv"
            env_info["update_command"] = f"uv pip install --upgrade {self.PACKAGE_NAME}"
        elif (
            "/pipx/venvs/" in sys.executable
            or "/pipx/venvs/" in str(Path(sys.executable))
            or os.getenv("PIPX_HOME")
            or os.getenv("PIPX_BIN_DIR")
        ):
            env_info["installer"] = "pipx"
            env_info["update_command"] = f"pipx upgrade {self.PACKAGE_NAME}"
        else:
            env_info["installer"] = "pip"
            env_info["update_command"] = (
                f"{sys.executable} -m pip install --upgrade {self.PACKAGE_NAME}"
            )

        # Check write permissions only for system pip installs; uv and pipx manage user locations
        if env_info["installer"] == "pip":
            try:
                import site

                site_packages = site.getsitepackages()[0] if site.getsitepackages() else None
                if site_packages:
                    test_file = Path(site_packages) / ".flow_update_test"
                    try:
                        test_file.touch()
                        test_file.unlink()
                    except (PermissionError, OSError):
                        env_info["can_update"] = False
                        if not env_info["is_virtual"]:
                            env_info["update_command"] = f"sudo {env_info['update_command']}"
            except Exception:  # noqa: BLE001
                pass

        return env_info

    def perform_update(self, target_version: str | None = None, force: bool = False) -> bool:
        """Perform the actual update.

        Args:
            target_version: Specific version to install, or None for latest
            force: Force update even if already on latest version

        Returns:
            True if update succeeded
        """
        from flow.cli.utils.theme_manager import theme_manager

        console = theme_manager.create_console()

        env_info = self.detect_environment()

        if not env_info["can_update"] and not force:
            self.last_error = "Insufficient permissions to update"
            if not self.quiet:
                console.print("[error]Insufficient permissions to update.[/error]")
                console.print(f"[warning]Try running: {env_info['update_command']}[/warning]")
            return False

        # Build update command
        if target_version:
            package_spec = f"{self.PACKAGE_NAME}=={target_version}"
        else:
            package_spec = self.PACKAGE_NAME

        if env_info["installer"] == "uv-tool":
            cmd = ["uv", "tool", "install", "--upgrade", package_spec]
            if force:
                cmd.append("--force")
        elif env_info["installer"] == "uv":
            cmd = ["uv", "pip", "install", "--upgrade", package_spec]
            if force:
                cmd.append("--force-reinstall")
        elif env_info["installer"] == "pipx":
            if target_version:
                cmd = ["pipx", "install", "--force", package_spec]
            else:
                cmd = ["pipx", "upgrade", self.PACKAGE_NAME]
        else:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package_spec]
            if force:
                cmd.append("--force-reinstall")

        if not self.quiet:
            console.print(f"[accent]Running: {' '.join(cmd)}[/accent]")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                if not self.quiet:
                    success_color = theme_manager.get_color("success")
                    console.print(f"[{success_color}]✓ Update complete[/{success_color}]")
                return True
            else:
                self.last_error = result.stderr or f"Exit code {result.returncode}"
                if not self.quiet:
                    console.print(
                        f"[error]Update failed with exit code {escape(str(result.returncode))}[/error]"
                    )
                    if result.stderr:
                        console.print(f"[error]Error: {escape(result.stderr)}[/error]")
                return False

        except subprocess.SubprocessError as e:
            self.last_error = str(e)
            if not self.quiet:
                console.print(f"[error]Failed to run update command: {escape(str(e))}[/error]")
            return False
        except Exception as e:  # noqa: BLE001
            self.last_error = str(e)
            if not self.quiet:
                console.print(f"[error]Unexpected error during update: {escape(str(e))}[/error]")
            return False

    def create_backup(self) -> str | None:
        # Removed: legacy rollback backup support
        return None
