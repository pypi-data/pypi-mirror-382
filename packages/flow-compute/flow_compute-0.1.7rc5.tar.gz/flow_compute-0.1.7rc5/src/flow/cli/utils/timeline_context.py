"""Timeline context manager for avoiding prop drilling in CLI commands.

This module provides a way to access the current active timeline from anywhere
in the execution context without having to pass it through multiple function calls.
"""

import threading
from contextlib import contextmanager

from flow.cli.commands.base import console
from flow.cli.utils.step_progress import StepTimeline

# Thread-local storage for the current timeline
_timeline_context = threading.local()


def get_current_timeline() -> "StepTimeline | None":
    """Get the current active timeline for this thread.

    Returns:
        The active timeline or None if no timeline is set.
    """
    return getattr(_timeline_context, "timeline", None)


def set_current_timeline(timeline: "StepTimeline | None") -> None:
    """Set the current active timeline for this thread.

    Args:
        timeline: The timeline to set as current, or None to clear.
    """
    _timeline_context.timeline = timeline


@contextmanager
def timeline_context(timeline: StepTimeline):
    """Context manager to set a timeline as current for the duration of the block.

    Args:
        timeline: The timeline to set as current.

    Example:
        with timeline_context(my_timeline):
            # Code here can access the timeline via get_current_timeline()
            some_function_that_needs_timeline()
    """
    previous = get_current_timeline()
    set_current_timeline(timeline)
    try:
        yield timeline
    finally:
        set_current_timeline(previous)


def finish_current_timeline() -> StepTimeline | None:
    """Finish the current timeline and clear the timeline context.

    Returns:
        The finished timeline, or None if no timeline was active.
    """
    timeline = get_current_timeline()
    if timeline:
        timeline.finish()


def ensure_timeline() -> StepTimeline:
    """Ensure a timeline is set in the context."""
    timeline = get_current_timeline()
    if timeline:
        return timeline
    timeline = StepTimeline(console, title_animation="auto")
    set_current_timeline(timeline)
    return timeline
