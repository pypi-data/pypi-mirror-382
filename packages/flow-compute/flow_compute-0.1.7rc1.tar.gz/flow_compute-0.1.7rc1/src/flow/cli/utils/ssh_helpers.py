from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from shlex import join as shlex_join


class SshStack:
    """CLI-facing wrapper around core SSH utilities.

    Keeps CLI imports decoupled from core by delegating at call time.
    """

    @staticmethod
    def find_fallback_private_key() -> Path | None:
        from flow.sdk.ssh import SshStack as _S

        return _S.find_fallback_private_key()

    @staticmethod
    def build_ssh_command(
        *,
        user: str,
        host: str,
        port: int | None = None,
        key_path: Path | None = None,
        prefix_args: Iterable[str] | None = None,
        remote_command: str | None = None,
        use_mux: bool | None = None,
    ) -> list[str]:
        from flow.sdk.ssh import SshStack as _S

        return _S.build_ssh_command(
            user=user,
            host=host,
            port=port,
            key_path=key_path,
            prefix_args=prefix_args,
            remote_command=remote_command,
            use_mux=use_mux,
        )

    @staticmethod
    def tcp_port_open(host: str, port: int, timeout_sec: float = 2.0) -> bool:
        from flow.sdk.ssh import SshStack as _S

        return _S.tcp_port_open(host, port, timeout_sec)

    @staticmethod
    def is_ssh_ready(
        *, user: str, host: str, port: int, key_path: Path, prefix_args: list[str] | None = None
    ) -> bool:
        from flow.sdk.ssh import SshStack as _S

        return _S.is_ssh_ready(
            user=user, host=host, port=port, key_path=key_path, prefix_args=prefix_args
        )


def build_ssh_argv(
    user: str,
    host: str,
    port: int,
    key_path: str | None,
    extra_ssh_args: list[str] | None = None,
    remote_command: list[str] | None = None,
    known_hosts_path: str | None = None,
) -> list[str]:
    """Build an ssh argv list with safe ordering and defaults.

    Rules:
    - Place all options before destination (`user@host`).
    - Include IdentitiesOnly=yes when a key is specified.
    - Support additional ssh flags via `extra_ssh_args`.
    - Append the remote command tokens after destination, if provided.
    - Never rely on a shell for quoting.
    """
    argv: list[str] = ["ssh"]

    # Conservative base options to avoid long hangs and reduce noise
    # Align broadly with adapters' SshStack defaults for consistency
    argv += [
        "-p",
        str(port),
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ServerAliveInterval=10",
        "-o",
        "ServerAliveCountMax=3",
        "-o",
        "PasswordAuthentication=no",
        "-o",
        "PreferredAuthentications=publickey",
        "-o",
        "GSSAPIAuthentication=no",
    ]

    if key_path:
        argv += ["-i", key_path, "-o", "IdentitiesOnly=yes"]

    # Favor accept-new to avoid prompting while still persisting new hosts.
    argv += ["-o", "StrictHostKeyChecking=accept-new"]

    if known_hosts_path:
        argv += ["-o", f"UserKnownHostsFile={known_hosts_path}"]

    if extra_ssh_args:
        argv += list(extra_ssh_args)

    argv.append(f"{user}@{host}")

    if remote_command:
        argv += list(remote_command)

    return argv


def ssh_command_string(argv: list[str]) -> str:
    """Return a shell-quoted command string (for logging/JSON only)."""
    return shlex_join(argv)
