"""Allocation service: data fetching and shaping for the alloc view."""

from __future__ import annotations

import flow.sdk.factory as sdk_factory
from flow.sdk.client import Flow
from flow.sdk.models import Task


class AllocService:
    def __init__(self, flow_client: Flow | None = None) -> None:
        # Use factory to create client in CLI layer
        self._flow = flow_client or sdk_factory.create_client(auto_init=True)

    def list_tasks_for_allocation(self, *, limit: int = 30) -> list[Task]:
        from flow.cli.utils.task_fetcher import TaskFetcher

        fetcher = TaskFetcher(self._flow)
        return fetcher.fetch_for_display(show_all=False, limit=limit)
