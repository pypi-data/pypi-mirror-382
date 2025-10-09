"""Centralized task fetching for the CLI.

Provides task fetching without caching - makes direct API calls.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import flow.sdk.factory as sdk_factory
from flow.errors import AuthenticationError
from flow.sdk.client import Flow
from flow.sdk.models import Task, TaskStatus


class TaskFetcher:
    """Centralized service for fetching tasks."""

    def __init__(self, flow_client: Flow | None = None):
        """Initialize with optional Flow client.

        Args:
            flow_client: Optional Flow client instance. Creates one if not provided.
        """
        self.flow_client = flow_client or sdk_factory.create_client(auto_init=True)

    def _dbg(self, msg: str) -> None:
        try:
            if os.environ.get("FLOW_STATUS_DEBUG"):
                logging.getLogger("flow.status.fetcher").info(msg)
        except Exception:  # noqa: BLE001
            pass

    def fetch_all_tasks(
        self,
        limit: int = 1000,
        prioritize_active: bool = True,
        status_filter: TaskStatus | None = None,
    ) -> list[Task]:
        """Fetch tasks directly from API.

        Args:
            limit: Maximum number of tasks to return
            prioritize_active: Whether to prioritize active tasks in results
            status_filter: Optional status filter for tasks

        Returns:
            List of tasks with active tasks prioritized if requested
        """
        # If filtering by specific status, just fetch those
        if status_filter:
            tasks = self.flow_client.list_tasks(status=status_filter, limit=limit)
            self._dbg(
                f"fetch_all: provider returned {len(tasks) if tasks else 0} for status={getattr(status_filter, 'value', status_filter)}"
            )
            return tasks

        tasks_by_id: dict[str, Task] = {}

        if prioritize_active:
            # Fetch active tasks first to ensure they're included
            try:
                # Prefer provider-side batching if supported: request both RUNNING and PENDING
                try:
                    batched = self.flow_client.list_tasks(
                        status=[TaskStatus.RUNNING, TaskStatus.PENDING],
                        limit=min(200, max(100, limit)),
                    )
                    self._dbg(
                        f"fetch_all(active): provider batched returned {len(batched) if batched else 0}"
                    )
                    for task in batched:
                        tasks_by_id[task.task_id] = task
                except Exception:  # noqa: BLE001
                    # Fallback to parallel individual calls
                    with ThreadPoolExecutor(max_workers=2) as ex:
                        futures = [
                            ex.submit(
                                self.flow_client.list_tasks,
                                status=TaskStatus.RUNNING,
                                limit=min(100, limit),
                            ),
                            ex.submit(
                                self.flow_client.list_tasks,
                                status=TaskStatus.PENDING,
                                limit=min(100, limit),
                            ),
                        ]
                        for f in as_completed(futures, timeout=1.0):
                            try:
                                active_tasks = f.result()
                                for task in active_tasks:
                                    tasks_by_id[task.task_id] = task
                            except Exception:  # noqa: BLE001
                                pass
            except Exception:  # noqa: BLE001
                pass

        # Fetch general task list
        remaining_limit = limit - len(tasks_by_id)
        if remaining_limit > 0:
            try:
                general_tasks = self.flow_client.list_tasks(limit=remaining_limit)
                self._dbg(
                    f"fetch_all(general): remaining_limit={remaining_limit} provider_count={len(general_tasks) if general_tasks else 0}"
                )
                for task in general_tasks:
                    tid = getattr(task, "task_id", getattr(task, "id", None))
                    if tid and tid not in tasks_by_id:
                        tasks_by_id[tid] = task
            except Exception as e:
                # Re-raise authentication errors - these should fail loudly
                if isinstance(e, AuthenticationError):
                    raise
                # If general fetch fails, at least return active tasks
                self._dbg(f"fetch_all(general): error={e}")

        # Return as list, sorted by created_at (newest first)
        all_tasks = list(tasks_by_id.values())

        # Always sort by created_at in descending order (newest first)
        all_tasks.sort(key=lambda t: t.created_at, reverse=True)

        final = all_tasks[:limit]
        self._dbg(f"fetch_all: final_count={len(final)}")
        return final

    def fetch_for_display(
        self, show_all: bool = False, status_filter: str | None = None, limit: int = 100
    ) -> list[Task]:
        """Fetch tasks for display commands (status, list).

        Args:
            show_all: Whether to show all tasks or apply time filtering
            status_filter: Optional status string to filter by
            limit: Maximum number of tasks to return

        Returns:
            List of tasks ready for display
        """
        # Convert status string to enum if provided (skip display statuses)
        self._dbg(
            f"fetch_for_display: show_all={show_all} status_filter={status_filter} limit={limit}"
        )
        # Don't use API status filtering - fetch all tasks and filter client-side
        # This is because the API's status filtering is not working correctly
        status_enum = None

        if not show_all and not status_filter:
            # Default view: Show only running/pending tasks
            # If none exist, fall back to showing all recent tasks

            # First, try to fetch only active (running/pending) tasks
            active_tasks = []
            tasks_by_id = {}

            # Prefer provider-side batching for RUNNING and PENDING
            try:
                batched_active = self.flow_client.list_tasks(
                    status=[TaskStatus.RUNNING, TaskStatus.PENDING],
                    limit=min(200, max(100, limit)),
                )
                self._dbg(
                    f"fetch_for_display(active): provider batched returned {len(batched_active) if batched_active else 0}"
                )
                for task in batched_active:
                    if task.task_id not in tasks_by_id:
                        tasks_by_id[task.task_id] = task
                        active_tasks.append(task)
            except Exception as e:
                # Re-raise authentication errors - these should fail loudly
                if isinstance(e, AuthenticationError):
                    raise
                # Fallback: fetch RUNNING and PENDING concurrently
                try:
                    with ThreadPoolExecutor(max_workers=2) as ex:
                        futures = [
                            ex.submit(
                                self.flow_client.list_tasks,
                                status=TaskStatus.RUNNING,
                                limit=min(100, limit),
                            ),
                            ex.submit(
                                self.flow_client.list_tasks,
                                status=TaskStatus.PENDING,
                                limit=min(100, limit),
                            ),
                        ]
                        for f in as_completed(futures, timeout=1.5):
                            try:
                                status_tasks = f.result()
                                for task in status_tasks:
                                    if task.task_id not in tasks_by_id:
                                        tasks_by_id[task.task_id] = task
                                        active_tasks.append(task)
                            except Exception:  # noqa: BLE001
                                pass
                except Exception:  # noqa: BLE001
                    pass
                self._dbg(f"fetch_for_display(active): batched error={e}")

            # If we found active tasks, return only those
            if active_tasks:
                # Sort by created_at (newest first)
                active_tasks.sort(key=lambda t: t.created_at, reverse=True)
                return active_tasks[:limit]

            # No active tasks found - perform a single provider call and return empty if also empty
            try:
                general = self.flow_client.list_tasks(limit=limit)
                self._dbg(
                    f"fetch_for_display(general): provider_count={len(general) if general else 0}"
                )
                if not general:
                    return []
                # Else, sort and return most recent general list
                general = sorted(general, key=lambda t: getattr(t, "created_at", 0), reverse=True)
                return general[:limit]
            except Exception as e:
                # Re-raise authentication errors - these should fail loudly
                if isinstance(e, AuthenticationError):
                    raise
                # Fallback to prior behavior
                self._dbg(f"fetch_for_display(general): error={e}")
                return self.fetch_all_tasks(limit=limit, prioritize_active=True, status_filter=None)
        else:
            # Specific status filter or --all flag
            return self.fetch_all_tasks(
                limit=limit, prioritize_active=False, status_filter=status_enum
            )

    def fetch_for_resolution(self, limit: int = 1000) -> list[Task]:
        """Fetch tasks for name/ID resolution (cancel, ssh, logs).

        This method prioritizes active tasks since those are most likely
        to be the target of user actions.

        Args:
            limit: Maximum number of tasks to fetch

        Returns:
            List of tasks with active tasks prioritized
        """
        return self.fetch_all_tasks(limit=limit, prioritize_active=True, status_filter=None)
