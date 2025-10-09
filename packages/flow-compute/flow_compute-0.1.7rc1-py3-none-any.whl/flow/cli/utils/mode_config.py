from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from flow.application.config.manager import ConfigManager


class Mode(Enum):
    INFRA = "infra"
    RESEARCH = "research"


@dataclass(frozen=True)
class ModeConfig:
    """Configuration for a specific CLI mode."""

    name: str
    display_name: str
    description: str
    groups: dict[str, list[str]]  # Group name -> command names
    core_commands: set[str] = field(default_factory=set)  # Commands shown by default


MODE_CONFIGS: Final[dict[Mode, ModeConfig]] = {
    Mode.INFRA: ModeConfig(
        name="infra",
        display_name="Infrastructure",
        description="Manage clusters, GPUs, and resources.",
        groups={
            "Getting started": ["setup", "docs"],
            "Compute": ["instance", "volume", "ssh-key"],
            "Monitoring": ["status", "pricing"],
            "Utils": ["ssh", "ports"],
            "Settings": ["theme", "update", "completion"],
        },
        core_commands={
            "setup",
            "docs",
            "instance",
            "volume",
            "ssh-key",
            "status",
        },
    ),
    Mode.RESEARCH: ModeConfig(
        name="research",
        display_name="Research",
        description="Run experiments and train models.",
        groups={
            "Getting started": ["setup", "docs"],
            "Development": ["dev", "submit", "cancel", "status", "ssh", "logs", "upload-code"],
            "Resources": [
                "ssh-key",
                "volume",
            ],
            "Utils": [
                "jupyter",
                "ports",
                "mount",
                "template",
            ],
            "Learn": [
                "ask",
                "example",
            ],
            "Settings": [
                "theme",
                "update",
                "completion",
            ],
        },
        core_commands={
            "setup",
            "docs",
            "dev",
            "submit",
            "cancel",
            "status",
            "ssh",
        },
    ),
}


def get_mode_config(mode: Mode) -> ModeConfig:
    match mode:
        case Mode.INFRA:
            return MODE_CONFIGS[Mode.INFRA]
        case Mode.RESEARCH:
            return MODE_CONFIGS[Mode.RESEARCH]


def get_current_mode() -> Mode:
    """Get current CLI mode, defaulting to infra.

    Precedence:
    1. mode in config file
    2. Default to Mode.INFRA

    Returns:
        Current mode key
    """
    cfg_mode = ConfigManager().detect_existing_config().get("mode")
    try:
        return Mode(cfg_mode)
    except ValueError:
        pass

    return Mode.INFRA


def set_mode(mode: Mode) -> None:
    """Persist mode to config file using ConfigManager.

    Args:
        mode: Mode key to set

    Note:
        Fails silently if config cannot be written to avoid breaking CLI.
    """
    manager = ConfigManager()
    existing_config = manager.detect_existing_config()
    existing_config["mode"] = mode.value
    manager.save(existing_config)


def get_other_mode() -> Mode:
    # Assumes there are only two modes
    current_mode = get_current_mode()
    return next(m for m in Mode if m is not current_mode)
