from __future__ import annotations

from pathlib import Path

from flow.errors import FlowError


class RemoteExecutionError(FlowError):
    """Raised when remote command execution fails."""

    pass


class TaskNotFoundError(FlowError):
    """Raised when task cannot be found."""

    pass


class SshConnectionError(RemoteExecutionError):
    """Specific error for SSH connection/setup issues."""

    pass


class SshAuthenticationError(RemoteExecutionError):
    """Specific error for SSH authentication issues."""

    def __init__(self, message: str, key_path: Path, stderr: str):
        super().__init__(message)
        self.key_path = key_path
        self.stderr = stderr


def make_error(
    message: str,
    request_id: str,
    suggestions: list | None = None,
    cls: type[RemoteExecutionError] = RemoteExecutionError,
) -> RemoteExecutionError:
    """Create a FlowError-derived error object with an attached request ID.

    Attaches the correlation ID to the exception object for CLI surfacing.
    """
    err = cls(message, suggestions=suggestions)  # type: ignore[arg-type]
    try:
        err.request_id = request_id
    except Exception:  # noqa: BLE001
        pass
    return err
