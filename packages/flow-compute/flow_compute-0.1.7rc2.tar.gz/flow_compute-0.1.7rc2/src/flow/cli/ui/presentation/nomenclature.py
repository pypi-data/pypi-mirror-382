"""Centralized UI nomenclature helpers.

Provides consistent, contextual labels for entity nouns across CLI views
while keeping changes surgical and DRY. Compute-mode toggles host-centric
terminology without altering core domain APIs (which still use "task").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from flow.cli.utils.mode_config import Mode, get_current_mode


def is_compute_mode() -> bool:
    """Return True when host-centric terminology should be used.

    Determines mode based on CLI mode configuration:
    - INFRA mode → compute mode (instance terminology)
    - RESEARCH mode → task mode (task terminology)

    Fallback order:
    1. Check Click context for instance_mode flag (command-level override)
    2. Check mode from config file via get_current_mode()
    3. Default to task mode (False)
    """
    # First, check Click context for instance_mode flag
    try:
        import click

        ctx = click.get_current_context(silent=True)
        if ctx and ctx.obj and isinstance(ctx.obj, dict):
            instance_mode = ctx.obj.get("instance_mode")
            if instance_mode is not None:
                return instance_mode
    except Exception:  # noqa: BLE001
        pass

    # Fallback: check mode from config file
    return get_current_mode() == Mode.INFRA


@dataclass(frozen=True)
class EntityLabels:
    header: str  # Column header label for the primary entity (e.g., Task/Host)
    title_plural: str  # Title form used in panels (e.g., Tasks/Hosts)
    empty_plural: str  # Lowercase plural for empty states (e.g., tasks/hosts)
    singular: str  # Lowercase singular form (e.g., task/instance)
    article: str  # Indefinite article (e.g., a/an)


_DEFAULT_LABELS: Final[EntityLabels] = EntityLabels(
    header="Task", title_plural="Tasks", empty_plural="tasks", singular="task", article="a"
)

_COMPUTE_LABELS: Final[EntityLabels] = EntityLabels(
    header="Instance",
    title_plural="Instances",
    empty_plural="instances",
    singular="instance",
    article="an",
)


def get_entity_labels() -> EntityLabels:
    """Return contextual labels based on compute mode.

    Keeps wording centralized and avoids ad-hoc checks scattered around UI.
    """
    return _COMPUTE_LABELS if is_compute_mode() else _DEFAULT_LABELS


@dataclass(frozen=True)
class ActionVerbs:
    """Action verb forms for cancel/delete operations."""

    base: str  # Base form, capitalized (e.g., Cancel/Delete)
    base_lower: str  # Base form, lowercase (e.g., cancel/delete)
    present: str  # Present progressive (e.g., Canceling/Deleting)
    past: str  # Past tense (e.g., Cancelled/Deleted)
    noun: str  # Noun form (e.g., cancellation/deletion)


_CANCEL_VERBS: Final[ActionVerbs] = ActionVerbs(
    base="Cancel",
    base_lower="cancel",
    present="Canceling",
    past="Cancelled",
    noun="cancellation",
)

_DELETE_VERBS: Final[ActionVerbs] = ActionVerbs(
    base="Delete",
    base_lower="delete",
    present="Deleting",
    past="Deleted",
    noun="deletion",
)


def get_delete_verbs() -> ActionVerbs:
    """Return contextual action verbs based on compute mode.

    Provides consistent cancel/delete terminology throughout the CLI.
    """
    return _DELETE_VERBS if is_compute_mode() else _CANCEL_VERBS
