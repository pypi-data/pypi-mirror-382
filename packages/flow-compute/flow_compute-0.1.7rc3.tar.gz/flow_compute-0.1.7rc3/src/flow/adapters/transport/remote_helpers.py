"""Remote SSH helpers for safe path handling and directory preparation.

This module centralizes small, opinionated operations used by code transfer
to avoid brittle shell quoting and duplication across call sites.
"""

from __future__ import annotations

import subprocess

from .ssh.client import SSHConnectionInfo


def _to_remote_expr(path: str) -> str:
    """Return a path expression suitable for bash -lc with $HOME expansion.

    - "~"      -> "$HOME"
    - "~/foo"  -> "$HOME/foo"
    - other     -> unchanged
    """
    p = (path or "").strip()
    if p == "~":
        return "$HOME"
    if p.startswith("~/"):
        return "$HOME/" + p[2:]
    return p


def _ssh_bash(
    connection: SSHConnectionInfo, script: str, timeout: int = 30
) -> subprocess.CompletedProcess:
    """Execute a bash -lc script via SSH with hardened options.

    Returns the CompletedProcess for callers that need stdout/rc.
    """
    cmd = [
        "ssh",
        "-p",
        str(connection.port),
        "-i",
        str(connection.key_path),
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ServerAliveInterval=10",
        "-o",
        "ServerAliveCountMax=3",
        f"{connection.user}@{connection.host}",
        "bash",
        "-lc",
        script,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def ensure_dir(connection: SSHConnectionInfo, path: str, *, sudo: bool = False) -> None:
    """Create the directory if missing. Uses sudo -n when requested.

    Best-effort: errors are swallowed.
    """
    expr = _to_remote_expr(path)
    if not expr:
        return
    escaped_expr = expr.replace("\\", r"\\").replace('"', '\\"')
    mkdir = f'mkdir -p "{escaped_expr}"'
    if sudo and expr.startswith("/"):
        mkdir = f"sudo -n {mkdir}"
    try:
        _ssh_bash(connection, mkdir)
    except Exception:  # noqa: BLE001
        pass


def ensure_writable(
    connection: SSHConnectionInfo, path: str, *, user: str | None = None, sudo: bool = False
) -> None:
    """Ensure path is writable by user: chown/chmod when allowed.

    Only runs chown/chmod when sudo=True and path is absolute.
    """
    expr = _to_remote_expr(path)
    if not expr:
        return
    cmds = []
    if sudo and expr.startswith("/"):
        if user:
            cmds.append(f'sudo -n chown -R {user}:{user} "{expr}" || true')
        cmds.append(f'sudo -n chmod 777 "{expr}" || true')
    if not cmds:
        return
    script = " ; ".join(cmds)
    try:
        _ssh_bash(connection, script)
    except Exception:  # noqa: BLE001
        pass


def is_writable(connection: SSHConnectionInfo, path: str) -> bool:
    """Return True if path is writable by the SSH user.

    Creates the directory first (without sudo) to avoid false negatives.
    """
    expr = _to_remote_expr(path)
    if not expr:
        return False
    script = f'mkdir -p "{expr}" >/dev/null 2>&1 || true; test -w "{expr}" && echo OK || echo DENY'
    try:
        res = _ssh_bash(connection, script)
        return res.returncode == 0 and isinstance(res.stdout, str) and "OK" in res.stdout
    except Exception:  # noqa: BLE001
        return False
