"""Compute facet: task submission and lifecycle operations.

This protocol defines the minimal surface area providers expose for compute
workflows. It focuses on submitting tasks, querying status, listing tasks,
and performing lifecycle operations like stop/cancel.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ComputeProtocol(Protocol):
    """Compute operations for submitting and managing tasks.

    Providers implementing this protocol should return their native task
    representations, while maintaining stable semantics for arguments and
    return types across implementations.
    """

    def submit_task(
        self,
        instance_type: str,
        config: Any,
        volume_ids: list[str] | None = None,
        allow_partial_fulfillment: bool = False,
        chunk_size: int | None = None,
    ) -> Any:
        """Submit a task for execution.

        Args:
            instance_type: Instance or GPU shape to target (e.g., "h100", "8xa100").
            config: Provider-specific task configuration object.
            volume_ids: Optional list of volume IDs to attach.
            allow_partial_fulfillment: Allow fewer resources than requested when True.
            chunk_size: Optional chunk size for sharded submissions, when supported.

        Returns:
            Provider-specific task object/handle representing the submitted task.
        """
        ...

    def get_task(self, task_id: str) -> Any:
        """Fetch a task by identifier.

        Args:
            task_id: Unique task identifier.

        Returns:
            Provider-specific task model with current fields populated.
        """
        ...

    def get_task_status(self, task_id: str) -> Any:
        """Return the current status for a task.

        Args:
            task_id: Unique task identifier.

        Returns:
            Status value or small status payload, provider-dependent.
        """
        ...

    def list_tasks(
        self,
        status: str | None = None,
        limit: int = 100,
        force_refresh: bool = False,
    ) -> list[Any]:
        """List recent tasks with optional server-side filtering.

        Args:
            status: Optional status filter (e.g., "running", "pending").
            limit: Maximum number of tasks to return.
            force_refresh: Bypass caches and fetch fresh data if True.

        Returns:
            A list of provider-specific task objects.
        """
        ...

    def stop_task(self, task_id: str) -> bool:
        """Request a graceful stop of a running task.

        Args:
            task_id: Unique task identifier.

        Returns:
            True if the stop request was accepted, False otherwise.
        """
        ...

    def cancel_task(self, task_id: str) -> None:
        """Cancel/terminate a task immediately.

        Args:
            task_id: Unique task identifier.
        """
        ...
