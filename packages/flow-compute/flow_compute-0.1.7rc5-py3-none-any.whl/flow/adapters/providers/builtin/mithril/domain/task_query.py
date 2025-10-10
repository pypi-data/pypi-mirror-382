"""Task query service for Mithril provider.

Encapsulates listing and pagination logic for tasks (bids), including
cursor-based pagination, deduplication, and light status filtering.
"""

from __future__ import annotations

import logging
import os
import random
import time
from collections import defaultdict
from typing import Any

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.domain.tasks import TaskService
from flow.sdk.models import Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskQueryService:
    def __init__(
        self,
        api: MithrilApiClient,
        task_service: TaskService,
        get_project_id: callable,
    ) -> None:
        self._api = api
        self._task_service = task_service
        self._get_project_id = get_project_id

    def list_tasks(
        self,
        status: TaskStatus | list[TaskStatus] | None = None,
        limit: int = 100,
        *,
        force_refresh: bool = False,
    ) -> list[Task]:
        """List tasks newest-first with pagination and deduplication."""

        # Map Flow TaskStatus to Mithril bid status filter values used by the API (v2).
        # Per OpenAPI `/v2/spot/bids` the allowed query values are:
        #   status ∈ {"Open", "Allocated", "Preempting", "Terminated", "Paused"}
        # We collapse Flow's terminal states into "Terminated" for filtering purposes.
        status_map = {
            TaskStatus.PENDING: "Open",
            TaskStatus.RUNNING: "Allocated",
            TaskStatus.PREEMPTING: "Preempting",
            TaskStatus.PAUSED: "Paused",
            TaskStatus.COMPLETED: "Terminated",
            TaskStatus.FAILED: "Terminated",
            TaskStatus.CANCELLED: "Terminated",
        }

        requested_statuses: list[str] | None
        if status is None:
            requested_statuses = None
        elif isinstance(status, list):
            mapped = [status_map.get(s) for s in status if s in status_map]
            requested_statuses = sorted({s for s in mapped if s})  # type: ignore[arg-type]
        else:
            mith = status_map.get(status)
            requested_statuses = [mith] if mith else None

        try:
            if os.environ.get("FLOW_STATUS_DEBUG"):
                pid = self._get_project_id()
                logging.getLogger("flow.status.provider").info(
                    f"mithril.task_query.list_tasks: project_id={pid} statuses={requested_statuses} limit={limit} force_refresh={force_refresh}"
                )
        except Exception:  # noqa: BLE001
            pass

        seen_task_ids: set[str] = set()
        unique_tasks: list[Task] = []
        page_count = 0
        max_pages = 10
        api_time = 0.0
        build_time = 0.0

        def _fetch_page(params: dict) -> tuple[list[dict], str | None, float]:
            """Fetch a page of bids with safe fallbacks for param compatibility.

            If the API rejects our params with a 422 (validation), retry with a
            reduced set of parameters to avoid noisy errors (e.g., drop status/sort).
            """
            start_api = time.time()
            try:
                response = self._api.list_bids(params)
            except Exception as e:  # noqa: BLE001
                # Retry on validation errors with minimal params: project, limit, next_cursor
                try:
                    from flow.errors import ValidationAPIError  # local import

                    if isinstance(e, ValidationAPIError):
                        minimal = {
                            k: v
                            for k, v in params.items()
                            if k in {"project", "limit", "next_cursor"}
                        }
                        response = self._api.list_bids(minimal)
                    else:
                        raise
                except Exception:
                    raise
            elapsed = time.time() - start_api
            # Support both dict responses (with pagination) and raw list responses
            if isinstance(response, list):
                bids = response
                next_cur = None
            else:
                bids = response.get("data", [])
                next_cur = response.get("next_cursor")
            return bids, next_cur, elapsed

        status_groups = requested_statuses or [None]
        for status_group in status_groups:
            next_cursor = None
            last_cursor = None
            pages_remaining = max_pages
            attempted_without_status = False  # fallback when server-side filter yields nothing

            while pages_remaining > 0 and len(unique_tasks) < limit * 2:
                pages_remaining -= 1
                page_count += 1
                params: dict[str, Any] = {
                    "project": self._get_project_id(),
                    "limit": 100,
                    # Request newest-first so active/recent tasks appear early.
                    # Aligns with single-task lookups which already use this ordering.
                    "sort_by": "created_at",
                    "sort_dir": "desc",
                }
                if status_group:
                    params["status"] = status_group
                if next_cursor:
                    # Use API-consistent pagination parameter name
                    params["next_cursor"] = next_cursor
                if force_refresh:
                    params["_cache_bust"] = f"{int(time.time())}-{random.randint(1000, 9999)}"

                bids, next_cursor_val, elapsed = _fetch_page(params)
                # Fallback: some API deployments accept the 'status' param but
                # return 0 rows. If the first page is empty, retry without the
                # server-side status filter and filter client-side instead.
                if not bids and status_group and not attempted_without_status and not next_cursor:
                    minimal = {k: v for k, v in params.items() if k != "status"}
                    bids, next_cursor_val, elapsed = _fetch_page(minimal)
                    attempted_without_status = True
                try:
                    if os.environ.get("FLOW_STATUS_DEBUG") and page_count == 1:
                        logging.getLogger("flow.status.provider").info(
                            f"mithril.task_query.page: status={status_group} bids={len(bids)} cursor={bool(next_cursor_val)}"
                        )
                except Exception:  # noqa: BLE001
                    pass
                api_time += elapsed

                if not bids:
                    break

                start_build = time.time()
                for bid in bids:
                    task_id = bid.get("fid", "")
                    if task_id and task_id not in seen_task_ids:
                        seen_task_ids.add(task_id)
                        task = self._task_service.build_task(bid, fetch_instance_details=False)
                        unique_tasks.append(task)
                build_time += time.time() - start_build

                next_cursor = next_cursor_val
                if next_cursor and next_cursor == last_cursor:
                    break
                last_cursor = next_cursor
                if not next_cursor:
                    break

        # Newest-first sort to ensure order if API misorders
        unique_tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Defensive filtering: if a status filter was requested, ensure the
        # returned tasks actually match it even if the upstream API returns
        # mixed results. This keeps CLI expectations consistent (e.g.,
        # "active" views only show running/pending).
        if requested_statuses:
            # Defensive: ensure returned tasks match the requested filter even
            # if the upstream API returns mixed results. Since the API exposes
            # bid lifecycle states (Open/Allocated/Terminated/Paused/Preempting)
            # and our TaskStatus is different, map TaskStatus -> bid filter bucket.
            try:
                allowed = set(requested_statuses)

                def _to_bid_bucket(ts: TaskStatus | None) -> str | None:
                    if ts is None:
                        return None
                    if ts == TaskStatus.PENDING:
                        return "Open"
                    if ts == TaskStatus.RUNNING:
                        return "Allocated"
                    if ts == TaskStatus.PREEMPTING:
                        return "Preempting"
                    if ts == TaskStatus.PAUSED:
                        return "Paused"
                    # Terminal buckets
                    if ts in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                        return "Terminated"
                    return None

                unique_tasks = [
                    t for t in unique_tasks if _to_bid_bucket(getattr(t, "status", None)) in allowed
                ]
            except Exception:  # noqa: BLE001
                # If anything goes wrong, fall back to unfiltered list
                pass

        # Log debug timing for observability
        logger.info(
            "task_query.list_tasks: pages=%s api_time=%ss build_time=%ss tasks=%s",
            page_count,
            f"{api_time:.3f}",
            f"{build_time:.3f}",
            len(unique_tasks),
        )

        # Step 2: Fetch instance statuses for accurate status determination
        if unique_tasks:
            logger.info(f"Fetching instance statuses for {len(unique_tasks)} tasks")
            instance_statuses = self._fetch_instance_statuses_for_tasks(unique_tasks, force_refresh)
            logger.info(f"Got instance statuses for {len(instance_statuses)} bids")
            # Update tasks with instance status information
            unique_tasks = self._update_tasks_with_instance_status(unique_tasks, instance_statuses)
            logger.info(f"Updated {len(unique_tasks)} tasks with instance status")

        return unique_tasks[:limit]

    def _fetch_instance_statuses_for_tasks(
        self, tasks: list[Task], force_refresh: bool = False
    ) -> dict[str, dict]:
        """Fetch instance statuses for a list of tasks using /v2/instances API."""
        if not tasks:
            return {}

        # Extract unique bid IDs from tasks
        bid_ids = []
        for task in tasks:
            bid_id = task.task_id
            if bid_id:
                bid_ids.append(bid_id)

        if not bid_ids:
            return {}

        project_id = self._get_project_id()

        # Use bid_fid_in parameter to filter instances by bid IDs
        params = {
            "project": project_id,
            "bid_fid_in": ",".join(bid_ids),
            "limit": min(100, len(bid_ids) * 2),  # Allow for multiple instances per bid
            "sort_by": "created_at",
            "sort_dir": "desc",
        }

        if force_refresh:
            import random

            params["_cache_bust"] = f"{int(time.time())}-{random.randint(1000, 9999)}"

        logger.debug(f"Fetching instance statuses for {len(bid_ids)} bids")
        response = self._api.list_instances(params)

        instances = response.get("data", []) if isinstance(response, dict) else response
        logger.debug(f"Retrieved {len(instances)} instances from API")

        # Group instances by bid ID
        bid_to_instances = defaultdict(list)
        for instance in instances:
            bid_id = instance.get("bid")
            if bid_id:
                bid_to_instances[bid_id].append(instance)

        return bid_to_instances

    def _update_tasks_with_instance_status(
        self, tasks: list[Task], instance_statuses: dict[str, list[dict]]
    ) -> list[Task]:
        """Update tasks with instance status information."""
        updated_tasks = []

        for task in tasks:
            bid_id = task.task_id
            instances = instance_statuses.get(bid_id, [])

            if instances:
                # Check for any running instance first, otherwise use the most recent instance
                running_instance = next(
                    (inst for inst in instances if inst.get("status") == "running"), None
                )

                if running_instance:
                    # Use the running instance for status determination
                    selected_instance = running_instance
                    instance_status = "running"
                else:
                    # No running instances, use the most recent instance
                    selected_instance = max(instances, key=lambda x: x.get("created_at", ""))
                    instance_status = selected_instance.get("status") or "unknown"

                # Enrich task with comprehensive instance data
                updated_task = self._task_service.enrich_task_with_instance_data(
                    task, selected_instance, instance_status
                )
                updated_tasks.append(updated_task)
            else:
                # No instance data available, keep original task
                updated_tasks.append(task)

        return updated_tasks

    def list_active_tasks(self, limit: int = 100) -> list[Task]:
        return self.list_tasks(status=TaskStatus.RUNNING, limit=limit)

    def get_task(self, task_id: str) -> Task | None:
        """Get a single task by ID by paging over bids.

        Returns None if not found.
        """
        project_id = self._get_project_id()

        def _page(next_cursor: str | None = None):
            params: dict[str, Any] = {
                "project": project_id,
                "limit": 100,
                "sort_by": "created_at",
                "sort_dir": "desc",
            }
            if next_cursor:
                params["next_cursor"] = next_cursor
            return self._api.list_bids(params)

        bid = None
        next_cursor: str | None = None
        for _ in range(3):
            response = _page(next_cursor)
            if isinstance(response, list):
                bids = response
                next_cursor = None
            else:
                bids = response.get("data", [])
                next_cursor = response.get("next_cursor")
            bid = next((b for b in bids if (b.get("fid") or b.get("id")) == task_id), None)
            if bid or not next_cursor:
                break

        if not bid:
            return None

        # Single-task fetch can afford enrichment to resolve SSH and owner info accurately
        return self._task_service.build_task(bid, fetch_instance_details=True)

    def get_task_status(self, task_id: str) -> TaskStatus | None:
        """Get the current status of a task by scanning recent bids.

        Returns None if not found.
        """
        # Retry logic to handle eventual consistency for newly created tasks
        max_retries = 3
        for attempt in range(max_retries):
            project_id = self._get_project_id()

            params: dict[str, Any] = {
                "project": project_id,
                "limit": 100,
                "sort_by": "created_at",
                "sort_dir": "desc",
            }

            response = self._api.list_bids(params)
            next_cursor = None
            pages_checked = 0
            bid = None
            while pages_checked < 3:
                pages_checked += 1
                if isinstance(response, list):
                    bids = response
                    next_cursor = None
                else:
                    if response is None:
                        bids = []
                        next_cursor = None
                    else:
                        bids = response.get("data", [])
                        next_cursor = response.get("next_cursor")

                bid = next((b for b in bids if (b.get("fid") or b.get("id")) == task_id), None)
                if bid or not next_cursor:
                    break

                response = self._api.list_bids({**params, "next_cursor": next_cursor})

            if bid:
                mithril_status = bid.get("status", "Pending")
                return self._task_service.map_mithril_status_to_enum(mithril_status)

            # If not found and we have more retries, wait a bit for eventual consistency
            if attempt < max_retries - 1:
                logger.debug(
                    f"Task {task_id} not found on attempt {attempt + 1}, retrying after delay..."
                )
                time.sleep(1.0)  # Wait 1 second before retrying

        # Task not found after all retries
        return None

    def get_bid_dict(self, task_id: str) -> dict | None:
        """Return the raw bid dict for a given task id or None if not found.

        This centralizes the pagination and search logic so provider code
        does not duplicate try/except scaffolding.
        """
        project_id = self._get_project_id()

        def _page(next_cursor: str | None = None):
            params: dict[str, Any] = {
                "project": project_id,
                "limit": 100,
                "sort_by": "created_at",
                "sort_dir": "desc",
            }
            if next_cursor:
                params["next_cursor"] = next_cursor
            return self._api.list_bids(params)

        next_cursor = None
        for _ in range(3):
            response = _page(next_cursor)
            if isinstance(response, list):
                bids = response
                next_cursor = None
            else:
                bids = response.get("data", [])
                next_cursor = response.get("next_cursor")
            bid = next((b for b in bids if (b.get("fid") or b.get("id")) == task_id), None)
            if bid:
                return bid
            if not next_cursor:
                break

        return None
