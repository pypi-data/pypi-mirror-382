"""Helpers for parsing index/range selections.

Shared by multiple commands (logs/ssh/cancel/volumes) to keep selection
parsing and cache-mapping logic consistent and DRY.
"""

from __future__ import annotations

import re

from flow.cli.utils.help_snippets import selection_cache_miss_message
from flow.cli.utils.selection import Selection, SelectionParseError
from flow.cli.utils.task_index_cache import TaskIndexCache
from flow.cli.utils.volume_index_cache import VolumeIndexCache


def _parse_selection_to_ids(
    expr: str, idx_map: dict[str, str], no_cache_message: str
) -> tuple[list[str] | None, str | None]:
    """Core helper: parse selection grammar and map to IDs via index map.

    Returns (ids, error_msg). If expr doesn't look like selection grammar,
    returns (None, None) so callers can treat input as a name/ID.
    """
    expression = expr.strip()
    # Accept digits, commas, ranges, with optional legacy leading colon
    if not re.fullmatch(r":?[0-9,\-\s]+", expression):
        return None, None  # Not a selection grammar

    try:
        if expression.startswith(":"):
            expression = expression[1:]
        selection = Selection.parse(expression)
    except SelectionParseError as e:
        return None, f"Selection error: {e}"

    if not idx_map:
        return None, no_cache_message

    ids, errors = selection.to_task_ids(idx_map)
    if errors:
        return None, errors[0]

    return ids, None


def parse_selection_to_task_ids(expr: str) -> tuple[list[str] | None, str | None]:
    """Parse an index/range expression to concrete task IDs via cache.

    Accepts bare numbers and ranges (preferred), e.g. "1-3,5", and the legacy
    leading-colon form, e.g. ":1-3,5".

    Returns (task_ids, error_msg). On error, (None, message).
    """
    cache = TaskIndexCache()
    idx_map = cache.get_indices_map()
    return _parse_selection_to_ids(expr, idx_map, selection_cache_miss_message("tasks"))


def parse_selection_to_volume_ids(expr: str) -> tuple[list[str] | None, str | None]:
    """Parse an index/range expression to concrete volume IDs via cache.

    Accepts bare numbers and ranges (preferred), e.g. "1-3,5", and the legacy
    leading-colon form, e.g. ":1-3,5".

    Returns (volume_ids, error_msg). On error, (None, message).
    """
    cache = VolumeIndexCache()
    idx_map = cache.get_indices_map()
    return _parse_selection_to_ids(expr, idx_map, selection_cache_miss_message("volumes"))
