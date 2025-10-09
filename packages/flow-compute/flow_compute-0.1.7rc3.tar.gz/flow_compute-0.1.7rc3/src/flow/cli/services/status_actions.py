"""High-level status actions extracted from the status command.

These helpers encapsulate fetching, filtering, and presentation for the
snapshot view and the single-task resolution flow, keeping the command slim.
"""

from __future__ import annotations

import os as _os

import flow.sdk.factory as sdk_factory


def _make_client():
    try:
        if _os.environ.get("PYTEST_CURRENT_TEST"):
            from flow.sdk.client import Flow as _Flow

            return _Flow()
    except Exception:  # noqa: BLE001
        pass
    return sdk_factory.create_client(auto_init=True)


def present_single_or_interactive(
    console,
    task_identifier: str,
    *,
    state: str | None,
    interactive: bool | None,
    flow_client=None,
) -> bool:
    """Present a single task, with interactive fallback on ambiguous matches.

    Returns True when handled (rendered), False to allow caller fallback.
    """
    try:
        from flow.cli.utils.task_resolver import resolve_task_identifier as _resolve

        # Show AEP while resolving the identifier to improve perceived latency
        try:
            from flow.cli.ui.presentation.animated_progress import (
                AnimatedEllipsisProgress as _AEP,
            )
        except Exception:  # noqa: BLE001
            _AEP = None  # type: ignore

        if _AEP:
            with _AEP(console, "Looking up task", start_immediately=True):
                if flow_client is None:
                    flow_client = _make_client()
                task, error = _resolve(flow_client, task_identifier)
        else:
            flow_client = flow_client or _make_client()
            task, error = _resolve(flow_client, task_identifier)
        if error and error.strip().lower().startswith("multiple tasks match"):
            # Ambiguous; allow interactive resolution when in a TTY and not explicitly disabled
            try:
                import sys as _sys

                allow_interactive = interactive is True or (
                    interactive is None and _sys.stdin.isatty()
                )
            except Exception:  # noqa: BLE001
                allow_interactive = interactive is True
            if allow_interactive:
                from flow.cli.ui.components import select_task as _select
                from flow.cli.utils.task_fetcher import TaskFetcher as _Fetcher

                try:
                    from flow.sdk.models import TaskStatus as _TS

                    state_enum = _TS(state) if state else None
                except Exception:  # noqa: BLE001
                    state_enum = None
                fetcher = _Fetcher(flow_client)
                candidates = fetcher.fetch_for_resolution(limit=1000)
                if state_enum is not None:
                    candidates = [t for t in candidates if getattr(t, "status", None) == state_enum]
                ident = task_identifier

                def _match(t):
                    try:
                        if getattr(t, "task_id", "").startswith(ident):
                            return True
                        n = getattr(t, "name", None) or ""
                        return n.startswith(ident)
                    except Exception:  # noqa: BLE001
                        return False

                candidates = [t for t in candidates if _match(t)]
                if not candidates:
                    console.print(error)
                    return True
                selected = _select(
                    candidates, title="Multiple matches – select a task", allow_multiple=False
                )
                if not selected:
                    return True
                try:
                    from flow.cli.ui.facade import TaskPresenter

                    TaskPresenter(console, flow_client=flow_client).present_single_task(
                        getattr(selected, "task_id", task_identifier)
                    )
                except Exception:  # noqa: BLE001
                    console.print(getattr(selected, "task_id", ""))
                return True
            else:
                from flow.cli.utils.theme_manager import theme_manager as _tm

                console.print(
                    f"[{_tm.get_color('error')}]{{error}}[/{_tm.get_color('error')}]".replace(
                        "{error}", str(error)
                    )
                )
                return True
        elif error:
            from flow.cli.utils.theme_manager import theme_manager as _tm

            console.print(
                f"[{_tm.get_color('error')}]{{error}}[/{_tm.get_color('error')}]".replace(
                    "{error}", str(error)
                )
            )
            return True
        else:
            # Render directly from resolved Task to avoid double resolution
            # Prefer TaskDetailRenderer; gracefully fall back to TaskPresenter if unavailable
            try:
                from flow.cli.ui.facade import TaskDetailRenderer
            except Exception:  # noqa: BLE001
                TaskDetailRenderer = None  # type: ignore

            rendered = False
            if TaskDetailRenderer:
                try:
                    TaskDetailRenderer(console).render_task_details(task)  # type: ignore[arg-type]
                    rendered = True
                except Exception:  # noqa: BLE001
                    rendered = False

            if not rendered:
                try:
                    # Fallback: use TaskPresenter's detail renderer
                    from flow.cli.ui.facade import TaskPresenter

                    TaskPresenter(console).detail_renderer.render_task_details(task)  # type: ignore[attr-defined]
                    rendered = True
                except Exception:  # noqa: BLE001
                    rendered = False

            if not rendered:
                # As a last resort, print the task id
                console.print(getattr(task, "task_id", task_identifier))
            return True
    except Exception:  # noqa: BLE001
        # Let the caller fall through to default UI
        return False
