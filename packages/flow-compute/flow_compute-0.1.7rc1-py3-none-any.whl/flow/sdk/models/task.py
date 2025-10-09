from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path as _Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from flow.adapters.providers.builtin.mithril.domain.models import PlatformSSHKey
from flow.errors import FlowError
from flow.sdk.models.enums import TaskStatus
from flow.sdk.models.instance import Instance
from flow.sdk.models.task_config import TaskConfig


class Task(BaseModel):
    """Task handle with lifecycle control (status, logs, wait, cancel, ssh)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_id: str = Field(..., description="Task UUID")
    name: str = Field(..., description="Human-readable name")
    status: TaskStatus = Field(..., description="Execution state")
    config: TaskConfig | None = Field(None, description="Original configuration")

    # Timestamps
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    instance_created_at: datetime | None = Field(
        None, description="Creation time of current instance (for preempted/restarted tasks)"
    )

    # Resources
    instance_type: str
    num_instances: int
    region: str

    # Cost information
    cost_per_hour: str = Field(..., description="Hourly cost")
    total_cost: str | None = Field(None, description="Accumulated cost")

    # User information
    created_by: str | None = Field(None, description="Creator user ID")

    # Access information
    ssh_host: str | None = Field(None, description="SSH endpoint")
    ssh_hosts: list[str] = Field(default_factory=list, description="SSH hosts")
    ssh_port: int | None = Field(22, description="SSH port")
    ssh_user: str = Field("ubuntu", description="SSH user")
    shell_command: str | None = Field(None, description="Complete shell command")

    # Endpoints and runtime info
    endpoints: dict[str, str] = Field(default_factory=dict, description="Exposed service URLs")
    instances: list[str] = Field(default_factory=list, description="Instance identifiers")
    message: str | None = Field(None, description="Human-readable status")

    # Provider-specific metadata
    provider_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific state and metadata (e.g., Mithril bid status, preemption reasons)",
    )

    # Provider reference (for method implementations)
    _provider: object | None = PrivateAttr(default=None)

    # Cached user information
    _user: Any | None = PrivateAttr(default=None)

    @property
    def is_running(self) -> bool:
        return self.status == TaskStatus.RUNNING

    @property
    def instance_status(self) -> str | None:
        return self.provider_metadata.get("instance_status")

    @property
    def instance_age_seconds(self) -> float | None:
        now = datetime.now(timezone.utc)
        if self.instance_created_at:
            return (now - self.instance_created_at).total_seconds()
        if self.created_at:
            return (now - self.created_at).total_seconds()
        return None

    @property
    def is_terminal(self) -> bool:
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]

    @property
    def has_ssh_access(self) -> bool:
        return bool(self.ssh_host and self.shell_command)

    @property
    def ssh_keys_configured(self) -> bool:
        return bool(self.config and self.config.ssh_keys) if self.config else False

    @property
    def capabilities(self) -> dict[str, bool]:
        return {
            "ssh": self.has_ssh_access,
            "logs": self.has_ssh_access,
            "interactive": self.has_ssh_access,
        }

    def copy_with_updates(self, **updates: Any) -> Task:
        """Create a copy of this task with updated fields.

        This is a safer alternative to manual deepcopy operations that ensures
        proper copying of all fields while allowing selective updates.

        ## Usage Patterns:

        **Use copy_with_updates() when:**
        - Task object is stored/shared (providers)
        - Creating new task variants (enrichment)
        - Building task objects for return
        - Multi-threaded environments

        **Use direct assignment when:**
        - Temporary local modifications (CLI commands)
        - Single-threaded, short-lived updates
        - Immediate UX feedback updates

        Args:
            **updates: Field updates to apply to the copied task

        Returns:
            A new Task instance with the specified updates applied

        Example:
            # Provider updating stored task
            updated_task = task.copy_with_updates(
                status=TaskStatus.RUNNING,
                provider_metadata={"instance_status": "running"}
            )
            self.tasks[task_id] = updated_task  # Store the updated copy

            # CLI temporary update
            task.status = TaskStatus.CANCELLED  # Direct assignment is fine
        """
        # Use Pydantic's model_copy method for safe copying
        return self.model_copy(deep=True, update=updates)

    def host(self, node: int | None = None) -> str | None:
        if not self.ssh_hosts:
            return self.ssh_host

        if node is None or node >= len(self.ssh_hosts):
            node = 0

        return self.ssh_hosts[node]

    def logs(
        self,
        follow: bool = False,
        tail: int = 100,
        stderr: bool = False,
        *,
        source: str | None = None,
        stream: str | None = None,
        node: int | None = None,
    ) -> str | Iterator[str]:
        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        # Determine log type preference
        if follow:
            if source in {"startup", "host"}:
                log_type = source
            elif source in {"both", "all"}:
                log_type = "all"
            else:
                log_type = "stderr" if stderr else (stream or "stdout")
        else:
            if source in {"startup", "host"}:
                log_type = "host" if source == "host" else "startup"
            elif (stream or "").lower() in {"combined"} or (source or "").lower() in {
                "both",
                "all",
            }:
                log_type = "both"
            else:
                log_type = "stderr" if stderr else (stream or "stdout")

        # Prefer logs facet when available; fall back to provider methods
        try:
            from flow.adapters.providers.registry import ProviderRegistry  # local import

            facets = ProviderRegistry.facets_for_instance(self._provider)
            if facets and getattr(facets, "logs", None) is not None:
                if follow:
                    return facets.logs.stream_task_logs(self.task_id, log_type=log_type, node=node)
                return facets.logs.get_task_logs(
                    self.task_id, tail=tail, log_type=log_type, node=node
                )
        except Exception:  # noqa: BLE001
            pass

        # Fallback to provider methods (may not support node parameter)
        if follow:
            return self._provider.stream_task_logs(self.task_id, log_type=log_type)
        return self._provider.get_task_logs(self.task_id, tail=tail, log_type=log_type)

    def wait(self, timeout: int | None = None) -> None:
        import time

        start_time = time.time()
        while not self.is_terminal:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {self.task_id} did not complete within {timeout} seconds")
            time.sleep(2)
            if self._provider:
                self.refresh()

    def refresh(self) -> None:
        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        updated = self._provider.get_task(self.task_id)
        for field in self.model_fields:
            if hasattr(updated, field) and field != "_provider":
                setattr(self, field, getattr(updated, field))

    def stop(self) -> None:
        if not self._provider:
            raise RuntimeError("Task not connected to provider")
        self._provider.stop_task(self.task_id)
        self.status = TaskStatus.CANCELLED

    def cancel(self) -> None:
        self.stop()

    @property
    def public_ip(self) -> str | None:
        if self.ssh_host and self._is_ip_address(self.ssh_host):
            return self.ssh_host
        return None

    def _is_ip_address(self, host: str) -> bool:
        try:
            import ipaddress

            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False

    def get_instances(self) -> list[Instance]:
        if not self._provider:
            raise FlowError("No provider available for instance resolution")
        return self._provider.get_task_instances(self.task_id)

    def get_user(self) -> Any | None:
        if not self.created_by:
            return None
        if self._user:
            return self._user
        if not self._provider:
            return None
        # Try multiple shapes for provider/context to fetch user info robustly
        try:
            prov = self._provider
            # 1) Provider facade exposing get_user()
            if hasattr(prov, "get_user") and callable(prov.get_user):
                self._user = prov.get_user(self.created_by)  # type: ignore[attr-defined]
                return self._user
            # 2) Context shape exposing users.get_user()
            users = getattr(prov, "users", None)
            if users is not None and hasattr(users, "get_user"):
                self._user = users.get_user(self.created_by)
                return self._user
            # 3) Provider/api client exposing _api_client.get_user()
            api_client = getattr(prov, "_api_client", None)
            if api_client is not None and hasattr(api_client, "get_user"):
                resp = api_client.get_user(self.created_by)
                self._user = resp.get("data", resp) if isinstance(resp, dict) else resp
                return self._user
            # 4) Raw HTTP adapter available: GET /v2/users/{id}
            http = getattr(prov, "http", None)
            if http is not None and hasattr(http, "request"):
                resp = http.request(method="GET", url=f"/v2/users/{self.created_by}")
                self._user = resp.get("data", resp) if isinstance(resp, dict) else resp
                return self._user
        except Exception:  # noqa: BLE001
            pass
        return None

    def get_ssh_keys(self) -> list[PlatformSSHKey]:
        """Get SSH keys configured for this task.

        Returns:
            List of PlatformSSHKey objects for each SSH key
        """
        if not self._provider:
            raise FlowError("No provider available for SSH key resolution")

        # Delegate to provider's task-specific SSH key method
        if hasattr(self._provider, "get_task_ssh_keys"):
            return self._provider.get_task_ssh_keys(self.task_id)
        else:
            raise FlowError(
                f"Provider {self._provider.name} does not support task-specific SSH key retrieval"
            )

    def result(self) -> Any:
        import json

        if not self.is_terminal:
            raise FlowError(
                f"Cannot retrieve result from task in {self.status} state",
                suggestions=[
                    "Wait for task to complete with task.wait()",
                    "Check task status with task.status",
                    "Results are only available after task completes",
                ],
            )

        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        try:
            remote_ops = self._provider.get_remote_operations()
        except (AttributeError, NotImplementedError):
            remote_ops = None
        if not remote_ops:
            raise FlowError(
                "Provider does not support remote operations",
                suggestions=[
                    "This provider does not support result retrieval",
                    "Use a provider that implements remote operations",
                    "Store results in cloud storage or volumes instead",
                ],
            )

        try:
            from flow.utils.paths import RESULT_FILE

            result_data = remote_ops.retrieve_file(self.task_id, RESULT_FILE)
            result_json = json.loads(result_data.decode("utf-8"))
            success = result_json.get("success")
            has_error_field = "error" in result_json
            if success is False or has_error_field:
                error_field = result_json.get("error")
                if isinstance(error_field, dict):
                    err_type = error_field.get("type") or error_field.get("error_type") or "Unknown"
                    message = error_field.get("message") or error_field.get("error") or "No message"
                    tb = error_field.get("traceback")
                else:
                    message = str(error_field) if error_field is not None else "Unknown error"
                    err_type = result_json.get("error_type", "Unknown")
                    tb = result_json.get("traceback")
                suggestions = [
                    "Check the full traceback in task logs",
                    "Use task.logs() to see the complete error",
                ]
                if tb:
                    try:
                        tail = "\n".join(tb.strip().splitlines()[-5:])
                        suggestions.append(f"Traceback (last lines):\n{tail}")
                    except Exception:  # noqa: BLE001
                        pass
                raise FlowError(
                    f"Remote function failed: {err_type}: {message}", suggestions=suggestions
                )
            return result_json.get("result")
        except FileNotFoundError:
            raise FlowError(
                "Result file not found on remote instance",
                suggestions=[
                    "The function may not have completed successfully",
                    "Check task logs with task.logs() for errors",
                    "Ensure your function is wrapped with @app.function decorator",
                ],
            ) from None
        except json.JSONDecodeError as e:
            raise FlowError(
                "Failed to parse result JSON",
                suggestions=[
                    "The result file may be corrupted",
                    "Check task logs for errors during execution",
                    "Ensure the function returns JSON-serializable data",
                ],
            ) from e

    def shell(
        self,
        command: str | None = None,
        node: int | None = None,
        progress_context=None,
        record: bool = False,
        *,
        capture_output: bool = False,
    ) -> str | None:
        # Debug logging for Task.shell
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(
            "Task.shell: task_id=%r, command=%r, node=%r, record=%r",
            getattr(self, "task_id", "unknown"),
            command,
            node,
            record,
        )

        if node is not None and hasattr(self, "instances") and isinstance(self.instances, list):
            total = len(self.instances)
            if node < 0:
                node = None
            elif node >= total:
                raise ValueError(f"Invalid node index {node}; task has {total} nodes")

        logger.debug(
            "Task.shell: Checking provider: self._provider=%s",
            type(self._provider).__name__ if self._provider else None,
        )
        if self._provider:
            logger.debug("Task.shell: Using provider path, getting remote operations")
            try:
                remote_ops = self._provider.get_remote_operations()
                logger.debug("Task.shell: Got remote_ops: %r", remote_ops)
            except Exception as e:
                logger.debug("Task.shell: Exception getting remote operations: %r", e)
                raise

            if not remote_ops:
                logger.debug("Task.shell: No remote operations available from provider")
                raise FlowError(
                    "Provider does not support shell access",
                    suggestions=[
                        "This provider does not support remote shell access",
                        "Use a provider that implements remote operations",
                        "Check provider documentation for supported features",
                    ],
                )
            # Use execute_command for output capture, open_shell for interactive/immediate output
            if command and capture_output:
                logger.debug("Task.shell: Using execute_command for output capture")
                try:
                    # All providers now support node parameter via protocol
                    output = remote_ops.execute_command(self.task_id, command, node=node)
                    logger.debug("Task.shell: execute_command completed successfully")
                    return output
                except Exception as e:
                    logger.debug("Task.shell: Exception in execute_command: %r", e)
                    raise
            else:
                logger.debug("Task.shell: Using open_shell for interactive/immediate output")
                try:
                    remote_ops.open_shell(
                        self.task_id,
                        command=command,
                        node=node,
                        progress_context=progress_context,
                        record=record,
                    )
                    logger.debug("Task.shell: open_shell completed successfully")
                except Exception as e:
                    logger.debug("Task.shell: Exception in remote_ops.open_shell: %r", e)
                    raise
            return None

        logger.debug("Task.shell: No provider, checking ssh_host fallback")
        ssh_host = getattr(self, "ssh_host", None)
        logger.debug("Task.shell: ssh_host=%r", ssh_host)
        if not ssh_host:
            logger.debug("Task.shell: No ssh_host available, raising FlowError")
            from flow.errors import FlowError as _FlowError

            raise _FlowError(
                "Provider does not support shell access",
                suggestions=[
                    "This provider does not support remote shell access",
                    "Use a provider that implements remote operations",
                    "Check provider documentation for supported features",
                ],
            )

        from flow.sdk.ssh import SshStack

        ssh_cmd = SshStack.build_ssh_command(
            user=getattr(self, "ssh_user", "ubuntu"),
            host=self.ssh_host,
            port=getattr(self, "ssh_port", 22),
            key_path=(
                _Path(getattr(self, "ssh_key_path", ""))
                if getattr(self, "ssh_key_path", None)
                else None
            ),
            remote_command=command,
        )
        if command is None:
            import subprocess

            subprocess.run(ssh_cmd)
            return None
        else:
            import subprocess

            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            if capture_output:
                # Return output instead of printing it
                return result.stdout or ""
            else:
                # Existing behavior: print output immediately
                if result.stdout:
                    print(result.stdout, end="")
                return None
