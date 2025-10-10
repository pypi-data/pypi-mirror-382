"""Telemetry settings management for Flow CLI.

Provides a small set of commands to enable/disable telemetry and view status.
Settings are persisted under ~/.flow/telemetry.yaml (preferred) with a fallback
to ~/.flow/config.yaml under the `telemetry:` key when reading. Amplitude keys
are non-secret identifiers; storing locally is safe.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import click
import yaml

from flow.cli.commands.base import BaseCommand


def _read_yaml(path: Path) -> dict[str, Any]:
    """Read a YAML file into a dictionary.

    Args:
        path: Path to the YAML file.

    Returns:
        A dict parsed from YAML, or an empty dict on errors.
    """
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _write_yaml_secure(path: Path, data: dict[str, Any]) -> None:
    """Write YAML atomically and harden file permissions on POSIX.

    Args:
        path: Destination file path.
        data: Mapping to serialize as YAML.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
    try:
        tmp.replace(path)
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass
    # Best-effort POSIX hardening
    try:
        if os.name == "posix":
            os.chmod(path, 0o600)
    except Exception:  # noqa: BLE001
        pass


def _merge_telemetry(
    base: dict[str, Any],
    enabled: bool | None = None,
    api_key: str | None = None,
    url: str | None = None,
) -> dict[str, Any]:
    """Merge telemetry knobs into a base config.

    Args:
        base: Existing config mapping.
        enabled: Optional enabled flag.
        api_key: Optional Amplitude API key.
        url: Optional Amplitude ingestion URL.

    Returns:
        New config mapping with merged telemetry settings.
    """
    cfg = dict(base)
    t = dict(cfg.get("telemetry") or {})
    if enabled is not None:
        t["enabled"] = bool(enabled)
    amp = dict(t.get("amplitude") or {})
    if api_key is not None:
        amp["api_key"] = str(api_key)
    if url is not None and url.strip():
        amp["url"] = str(url)
    if amp:
        t["amplitude"] = amp
    cfg["telemetry"] = t
    return cfg


class TelemetryCommand(BaseCommand):
    """Manage CLI telemetry settings (enable, disable, status)."""

    @property
    def name(self) -> str:
        return "telemetry"

    @property
    def help(self) -> str:
        return "Manage telemetry settings (enable, disable, status)"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        def telemetry_group() -> None:
            pass

        @telemetry_group.command("status", help="Show current telemetry status and settings source")
        def status_cmd() -> None:
            try:
                from flow.utils import analytics as _analytics

                enabled = bool(_analytics.telemetry_enabled())
                # Load raw settings to show the resolved Amplitude API key presence
                # (do not echo key value to avoid noise)
                # Access internal loader for rich status; fall back if not available
                try:
                    load = _analytics._load_telemetry_settings
                    settings = load()
                except Exception:  # noqa: BLE001
                    settings = {"enabled": enabled}
                api_key_set = bool(settings.get("amplitude", {}).get("api_key"))
                url = settings.get("amplitude", {}).get("url") or ""
                click.echo(
                    f"Telemetry: {'enabled' if enabled else 'disabled'}\n"
                    f"Amplitude key set: {'yes' if api_key_set else 'no'}\n"
                    f"Ingest URL: {url if api_key_set and url else '(default or unset)'}"
                )
            except Exception:  # noqa: BLE001
                click.echo("Telemetry: unknown (error loading settings)")

        @telemetry_group.command(
            "enable", help="Enable telemetry (optionally set Amplitude key and URL)"
        )
        @click.option("--amplitude-key", "amplitude_key", default=None, help="Amplitude API key")
        @click.option("--url", "url", default=None, help="Custom Amplitude ingestion URL")
        def enable_cmd(amplitude_key: str | None, url: str | None) -> None:
            path = Path.home() / ".flow" / "telemetry.yaml"
            current = _read_yaml(path)
            new_cfg = _merge_telemetry(current, enabled=True, api_key=amplitude_key, url=url)
            _write_yaml_secure(path, new_cfg)
            click.echo("Telemetry enabled.")

        @telemetry_group.command("disable", help="Disable telemetry")
        def disable_cmd() -> None:
            path = Path.home() / ".flow" / "telemetry.yaml"
            current = _read_yaml(path)
            new_cfg = _merge_telemetry(current, enabled=False)
            _write_yaml_secure(path, new_cfg)
            click.echo("Telemetry disabled.")

        return telemetry_group


command = TelemetryCommand()
