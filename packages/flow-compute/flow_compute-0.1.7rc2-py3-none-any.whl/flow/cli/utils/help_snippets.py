"""Small, shared help snippets for consistent CLI guidance.

These helpers centralize brief, repeatable copy fragments so that
commands use the same wording for selection grammar and related tips.
"""

from __future__ import annotations


def selection_help_lines_for(entity: str = "tasks") -> list[str]:
    """Return standardized lines describing selection grammar.

    Args:
        entity: Domain entity, e.g., "tasks" or "volumes".

    Returns:
        A list of short, formatted lines suitable for direct printing.
    """
    ent = (entity or "tasks").strip().lower()
    if ent == "volumes":
        return [
            "  • Run 'flow volume list' to refresh the index cache (valid for 5 minutes).",
            "  • Then use '1' to reference a row, or ranges like '1-3,5'.",
        ]
    # Default: tasks
    return [
        "  • Run 'flow status' to refresh the index cache (valid for 5 minutes).",
        "  • Then use '1' to reference a row, or ranges like '1-3,5'.",
        "  • Use ':dev' to target your dev VM directly.",
    ]


def selection_cache_miss_message(entity: str = "tasks") -> str:
    """One-line cache-miss message for index selection.

    Args:
        entity: Domain entity ("tasks" or "volumes").
    """
    ent = (entity or "tasks").strip().lower()
    if ent == "volumes":
        return "No cached indices available. Run 'flow volume list' first."
    return "No cached indices available. Run 'flow status' first."
