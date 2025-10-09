"""Centralized UI nomenclature helpers.

Provides consistent, contextual labels for entity nouns across CLI views
while keeping changes surgical and DRY. Compute-mode toggles host-centric
terminology without altering core domain APIs (which still use "task").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


def is_compute_mode() -> bool:
    """Return True when host-centric terminology should be used.

    Reads Click context only to avoid leaking across invocations.
    """
    try:
        import click

        ctx = click.get_current_context(silent=True)
        if ctx is not None:
            data = getattr(ctx, "obj", None) or {}
            if isinstance(data, dict) and data.get("instance_mode"):
                return True
    except Exception:  # noqa: BLE001
        pass
    return False


@dataclass(frozen=True)
class EntityLabels:
    header: str  # Column header label for the primary entity (e.g., Task/Host)
    title_plural: str  # Title form used in panels (e.g., Tasks/Hosts)
    empty_plural: str  # Lowercase plural for empty states (e.g., tasks/hosts)


_DEFAULT_LABELS: Final[EntityLabels] = EntityLabels(
    header="Task", title_plural="Tasks", empty_plural="tasks"
)

_COMPUTE_LABELS: Final[EntityLabels] = EntityLabels(
    header="Instance", title_plural="Instances", empty_plural="instances"
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
