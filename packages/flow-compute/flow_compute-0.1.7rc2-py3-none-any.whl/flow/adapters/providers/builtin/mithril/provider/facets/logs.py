"""Logs facet - handles task log retrieval and streaming."""

from __future__ import annotations

import logging
import time
from collections import deque
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

from flow.adapters.providers.builtin.mithril.adapters.remote import RemoteExecutionError
from flow.adapters.providers.builtin.mithril.api.handlers import handle_mithril_errors
from flow.errors.messages import TASK_INSTANCE_NOT_ACCESSIBLE, format_error

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext
    from flow.adapters.providers.builtin.mithril.provider.provider import MithrilProvider

logger = logging.getLogger(__name__)


class LogsFacet:
    """Handles log operations for tasks."""

    def __init__(
        self, ctx: MithrilContext, get_remote_ops: Callable, provider: MithrilProvider
    ) -> None:
        """Initialize logs facet.

        Args:
            ctx: Mithril context with all dependencies
            get_remote_ops: Callable to get remote operations handler
            provider: Mithril provider instance
        """
        self.ctx = ctx
        self._logger = getattr(ctx, "logger", logger)
        self.get_remote_ops = get_remote_ops
        self.provider = provider

        # Connect LogService to remote ops
        if hasattr(self.ctx.log_service, "_remote"):
            self.ctx.log_service._remote = None  # Clear legacy internal

    @handle_mithril_errors("Get task logs")
    def get_task_logs(
        self, task_id: str, tail: int = 100, log_type: str = "stdout", *, node: int | None = None
    ) -> str:
        """Get recent logs for a task.

        Args:
            task_id: Task ID
            tail: Number of lines to retrieve
            log_type: Type of logs ("stdout" or "stderr")
            node: Node index for multi-instance tasks (defaults to 0)

        Returns:
            Log contents as string
        """
        # For snapshot 'auto' requests, prefer container logs if the container
        # becomes available shortly. This avoids returning only startup output
        # for short-running tasks where the container appears a few seconds
        # after instance boot. The wait window is small and configurable via
        # FLOW_LOGS_CONTAINER_WAIT_SECS (default: 12 seconds).
        wait_secs = 12
        try:
            import os as _os

            v = _os.getenv("FLOW_LOGS_CONTAINER_WAIT_SECS")
            if v is not None:
                wait_secs = max(0, min(60, int(v)))
        except Exception:  # noqa: BLE001
            wait_secs = 12

        if str(log_type).lower() == "auto" and wait_secs > 0:
            try:
                remote = self.get_remote_ops()
                if remote is not None:
                    check_cmd = (
                        "docker ps -a --format '{{.Names}}' 2>/dev/null || "
                        "sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null"
                    )
                    deadline = time.time() + float(wait_secs)
                    while time.time() < deadline:
                        try:
                            names = remote.execute_command(
                                task_id, f"{check_cmd} | head -n1", node=node
                            )
                            if isinstance(names, bytes):
                                names = names.decode("utf-8", errors="ignore")
                            if str(names).strip():
                                # Container is present; fetch container stdout snapshot
                                cmd = self.ctx.log_service.build_command(task_id, tail, "stdout")
                                output = remote.execute_command(task_id, cmd, node=node).strip()
                                self.ctx.log_service.set_cache(task_id, tail, "stdout", output)
                                return output if output else "No logs available"
                        except Exception:  # noqa: BLE001
                            # Continue until deadline; SSH may not be fully ready yet
                            pass
                        time.sleep(1)
            except Exception:  # noqa: BLE001
                # Fall back to normal path
                pass

        # Get bid data for status checking and gating (after the quick auto-wait)
        try:
            from flow.adapters.providers.builtin.mithril.provider.facets.tasks import TasksFacet

            tasks = TasksFacet(self.ctx, self.provider)
            bid = tasks.get_bid_dict(task_id)
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Failed to get bid for task {task_id}: {e}")
            bid = None

        # Check if logs are available (handles pending/cancelled states)
        if hasattr(self.ctx.log_service, "get_recent"):
            gated = self.ctx.log_service.get_recent(
                task_id=task_id, bid=bid, tail=tail, log_type=log_type, execute=False
            )

            # If gated response indicates logs aren't available, return it
            if isinstance(gated, str) and (
                gated.startswith("Task ")
                or gated.startswith("Failed")
                or gated.endswith("available")
            ):
                return gated

        # Build log retrieval command (normal path)
        cmd = self.ctx.log_service.build_command(task_id, tail, log_type)

        # Check cache first
        cached = self.ctx.log_service.get_cached(task_id, tail, log_type)
        if cached is not None:
            return cached

        # Execute command to get logs
        try:
            remote = self.get_remote_ops()
            if remote is not None:
                output = remote.execute_command(task_id, cmd, node=node).strip()
            else:
                output = self.ctx.log_service.execute_via_remote(task_id, cmd)

            # Cache the result
            self.ctx.log_service.set_cache(task_id, tail, log_type, output.strip())

            return output.strip() if output else "No logs available"

        except RemoteExecutionError as e:
            msg = str(e).lower()
            # Treat common endpoint/SSH-not-ready signals as a not-accessible-yet case
            if (
                "no ssh access" in msg
                or "no public endpoint available" in msg
                or "ssh setup failed" in msg
                or "ssh connection error" in msg
            ):
                return format_error(TASK_INSTANCE_NOT_ACCESSIBLE, task_id=task_id)
            return f"Failed to retrieve logs: {e}"
        except Exception as e:  # noqa: BLE001
            return f"Failed to retrieve logs: {e}"

    def stream_task_logs(
        self,
        task_id: str,
        log_type: str = "stdout",
        follow: bool = True,
        tail: int = 10,
        *,
        node: int | None = None,
    ) -> Iterator[str]:
        """Stream logs from a task.

        Args:
            task_id: Task ID
            log_type: Type of logs ("stdout", "stderr", "combined", "startup", "host", "auto")
            follow: Whether to follow log output
            tail: Initial number of lines to retrieve
            node: Node index for multi-instance tasks (defaults to 0)

        Yields:
            Log lines as they become available
        """
        # If not following, just return recent logs via snapshot helper
        if not follow:
            for line in self.get_task_logs(task_id, tail=tail, log_type=log_type, node=node).split(
                "\n"
            ):
                if line:
                    yield line
            return

        # Build a streaming-friendly remote command (includes initial tail)
        try:
            cmd = self.ctx.log_service.build_command(task_id, tail, log_type, follow=True)
        except Exception as e:  # noqa: BLE001
            # Fallback to simple polling if command construction fails
            logger.debug(f"Failed to build follow command for logs: {e}")
            initial_logs = self.get_task_logs(task_id, tail=tail, log_type=log_type, node=node)
            if initial_logs and not initial_logs.startswith("Failed"):
                for line in initial_logs.split("\n"):
                    if line:
                        yield line
            # Minimal polling loop
            last_size = len(initial_logs) if initial_logs else 0
            while True:
                time.sleep(2)
                logs = self.get_task_logs(task_id, tail=1000, log_type=log_type, node=node)
                if not logs or logs.startswith("Failed"):
                    continue
                if len(logs) > last_size:
                    for line in logs[last_size:].split("\n"):
                        if line:
                            yield line
                    last_size = len(logs)
            return

        remote = self.get_remote_ops()
        if remote is None:
            yield "Failed to stream logs: remote operations unavailable"
            return

        # Simple, bounded de-dupe to avoid duplicate head after reconnect
        recent = deque(maxlen=max(10, tail))
        attempts = 0
        backoff = 1.0
        max_attempts = 4

        while True:
            try:
                for line in remote.stream_command(task_id, cmd, node=node):
                    if line and (line not in recent):
                        yield line
                        recent.append(line)
                # Process exited normally; stop retrying
                return
            except KeyboardInterrupt:
                return
            except Exception as e:  # noqa: BLE001
                attempts += 1
                if attempts >= max_attempts:
                    yield f"Failed to stream logs: {e}"
                    return
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 8.0)
