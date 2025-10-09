"""Centralized SSH utilities for Flow.

Single source of truth for:
- Building ssh commands with consistent options
- Checking SSH readiness
- Resolving private key path overrides (env/back-compat)

Providers and CLI should import and use this module to avoid duplicated logic.
"""

from __future__ import annotations

import logging as _logging
import os
import socket
import subprocess
import time as _t
from collections.abc import Iterable
from pathlib import Path

from flow.adapters.providers.builtin.mithril.remote.errors import (
    SshAuthenticationError,
)

logger = _logging.getLogger(__name__)


class SshStack:
    """Centralized helpers for SSH operations.

    This class deliberately avoids provider-specific behavior. Any provider
    that needs to scope API calls (e.g., project scoping) should do so before
    calling these helpers.
    """

    # Canonical SSH options used everywhere
    _BASE_OPTIONS: list[str] = [
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "PasswordAuthentication=no",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ServerAliveInterval=10",
        "-o",
        "ServerAliveCountMax=3",
    ]

    # Lightweight TTL cache for port responsiveness probes to avoid
    # repeated connects during a single status session.
    _PROBE_CACHE: dict[tuple[str, int], tuple[float, bool]] = {}

    @staticmethod
    def find_fallback_private_key() -> Path | None:
        """Return a fallback private key path if explicitly configured.

        Precedence:
        1) MITHRIL_SSH_KEY (path to private key)
        2) FLOW_SSH_KEY_PATH (legacy/back-compat)
        3) Standard ~/.ssh key names (id_ed25519, id_rsa, id_ecdsa)
        """
        # Env override (preferred; support legacy alias and .pub handling)
        try:
            from flow.core.keys.resolution import resolve_env_key_path as _env_resolve

            p = _env_resolve(("MITHRIL_SSH_KEY", "Mithril_SSH_KEY", "FLOW_SSH_KEY_PATH"))
            if p is not None:
                return p
        except Exception:  # noqa: BLE001
            # Fallback to direct checks
            env_key = os.environ.get("MITHRIL_SSH_KEY") or os.environ.get("FLOW_SSH_KEY_PATH")
            if env_key:
                p = Path(env_key).expanduser()
                if p.exists():
                    return p

        # Back-compat
        legacy = os.environ.get("FLOW_SSH_KEY_PATH")
        if legacy:
            p = Path(legacy).expanduser()
            if p.exists():
                return p

        # Common defaults
        ssh_dir = Path.home() / ".ssh"
        for name in ("id_ed25519", "id_rsa", "id_ecdsa"):
            p = ssh_dir / name
            if p.exists():
                return p
        return None

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
        """Build a canonical ssh command.

        Args:
            user: SSH username.
            host: Target hostname/IP.
            port: SSH port (default 22).
            key_path: Private key path, if any.
            prefix_args: Extra args preceding destination (e.g., -N -L ... for tunnels).
            remote_command: Optional command to execute remotely.
            use_mux: Whether to enable SSH connection multiplexing for this
                command. When None (default), defer to config/env defaults.
        """
        cmd: list[str] = ["ssh"]

        if prefix_args:
            cmd.extend(list(prefix_args))

        if port is None:
            port = 22
        cmd.extend(["-p", str(port)])

        if key_path:
            cmd.extend(["-i", str(Path(key_path).expanduser())])
            # Ensure only the provided key is used (avoid agent/other keys interfering)
            cmd.extend(["-o", "IdentitiesOnly=yes"])

        cmd.extend(SshStack._BASE_OPTIONS)

        # Prefer publickey auth and disable slow GSSAPI negotiation to reduce connection latency
        cmd.extend(
            [
                "-o",
                "PreferredAuthentications=publickey",
                "-o",
                "GSSAPIAuthentication=no",
            ]
        )

        # Enable connection multiplexing to speed subsequent SSH connects
        # Uses a safe ControlPath under /tmp to avoid user-home path issues.
        # Allow per-call override (use_mux) and global toggle via settings/env.
        def _mux_enabled_default() -> bool:
            try:
                from flow.application.config.runtime import settings as _settings  # local import

                cfg = _settings.ssh or {}
                if "mux" in cfg:
                    return bool(cfg.get("mux"))
            except Exception:  # noqa: BLE001
                pass
            try:
                env = os.environ.get("FLOW_SSH_MUX")
                if env is not None:
                    val = env.strip().lower()
                    if val in ("0", "false", "no", "off"):
                        return False
                    if val in ("1", "true", "yes", "on"):
                        return True
            except Exception:  # noqa: BLE001
                pass
            return True  # default: enabled for performance

        mux_on = _mux_enabled_default() if use_mux is None else bool(use_mux)
        if mux_on:
            cmd.extend(
                [
                    "-o",
                    "ControlMaster=auto",
                    "-o",
                    "ControlPersist=60s",
                    "-o",
                    "ControlPath=/tmp/flow-ssh-ctl-%r@%h:%p",
                    "-o",
                    "StreamLocalBindUnlink=yes",
                ]
            )

        # Lightweight compression can help on slower links
        cmd.extend(["-o", "Compression=yes"])

        cmd.append(f"{user}@{host}")

        if remote_command:
            # Non-interactive command execution should avoid TTY and interactive prompts
            # to suppress MOTD and banners from polluting the output and to ensure
            # predictable behavior in automation contexts.
            cmd.insert(1, "-T")  # disable pseudo-tty allocation
            cmd.insert(1, "-o")
            cmd.insert(2, "BatchMode=yes")
            cmd.append(remote_command)

        # Debug logging when requested (env > YAML)
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            _debug = bool((_settings.ssh or {}).get("debug", False))
        except Exception:  # noqa: BLE001
            _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
        if _debug:
            try:
                import logging as _logging

                _logging.getLogger(__name__).debug("SSH command argv: %s", " ".join(cmd))
            except Exception:  # noqa: BLE001
                pass

        return cmd

    @staticmethod
    def tcp_port_open(host: str, port: int, timeout_sec: float = 2.0) -> bool:
        """Lightweight TCP check before full SSH handshake."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout_sec)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:  # noqa: BLE001
            return False

    @staticmethod
    def has_ssh_banner(host: str, port: int, timeout_sec: float = 1.5) -> bool:
        """Return True if the endpoint responds with an SSH banner.

        Connects via TCP and attempts to read the initial server identification
        line (e.g., "SSH-2.0-OpenSSH_") within a short timeout. This avoids
        false-positives on generic TCP listeners (e.g., LBs/bastions) that keep
        port 22 open but are not running sshd for the target instance.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout_sec)
            sock.connect((host, port))
            # RFC 4253: server identification string is terminated by CRLF
            data = sock.recv(256)
            sock.close()
            try:
                line = (data or b"").decode("ascii", errors="ignore").strip()
            except Exception:  # noqa: BLE001
                line = ""
            return line.startswith("SSH-")
        except Exception:  # noqa: BLE001
            return False

    @staticmethod
    def is_endpoint_responsive(host: str, port: int, ttl_seconds: float | None = None) -> bool:
        """Return True if TCP port is open, with a tiny TTL cache.

        Keeps probes snappy and avoids spamming connections when rendering status
        for multiple tasks with the same endpoint within a short interval.
        """
        try:
            # Allow tuning via env; default 15s window
            if ttl_seconds is None:
                ttl_env = os.environ.get("FLOW_SSH_PROBE_TTL", "15")
                ttl_seconds = float(ttl_env)
        except Exception:  # noqa: BLE001
            ttl_seconds = 15.0

        key = (str(host), int(port))
        now = _t.time()
        try:
            cached = SshStack._PROBE_CACHE.get(key)
            if cached:
                ts, ok = cached
                if now - ts < float(ttl_seconds):
                    return bool(ok)
        except Exception:  # noqa: BLE001
            pass

        # Prefer SSH banner detection; fall back to bare TCP open
        ok = SshStack.has_ssh_banner(host, port) or SshStack.tcp_port_open(host, port)
        try:
            SshStack._PROBE_CACHE[key] = (now, ok)
        except Exception:  # noqa: BLE001
            pass
        return ok

    @staticmethod
    def is_ssh_ready(
        *,
        user: str,
        host: str,
        port: int,
        key_path: Path,
        prefix_args: list[str] | None = None,
    ) -> bool:
        """Return True if SSH responds to a BatchMode probe."""
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            debug = bool((_settings.ssh or {}).get("debug", False))
        except Exception:  # noqa: BLE001
            debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
        if not SshStack.tcp_port_open(host, port):
            if debug:
                import logging as _logging

                _logging.getLogger(__name__).debug("SSH tcp_port_open(%s:%s) -> closed", host, port)
            return False
        elif debug:
            import logging as _logging

            _logging.getLogger(__name__).debug("SSH tcp_port_open(%s:%s) -> open", host, port)

        # Build probe with BatchMode in prefix args so it's parsed before host
        # Merge caller-provided prefix args (e.g., ProxyJump) with probe flags
        probe_prefix: list[str] = []
        if prefix_args:
            probe_prefix.extend(list(prefix_args))
        probe_prefix.extend(
            [
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=4",
                "-o",
                "ConnectionAttempts=1",
            ]
        )

        test_cmd = SshStack.build_ssh_command(
            user=user,
            host=host,
            port=port,
            key_path=key_path,
            use_mux=False,  # Probes should not create/control multiplexed masters
            # Tighten probe timeouts to reduce perceived latency; include proxy if provided
            prefix_args=probe_prefix,
            remote_command="echo SSH_OK",
        )

        try:
            import os as _os

            probe_timeout = 4.0
            try:
                probe_timeout = float(_os.environ.get("FLOW_SSH_PROBE_TIMEOUT", "4"))
            except Exception:  # noqa: BLE001
                probe_timeout = 4.0
            result = subprocess.run(
                test_cmd, capture_output=True, text=True, timeout=int(probe_timeout)
            )
            if debug:
                import logging as _logging

                _logging.getLogger(__name__).debug(
                    "SSH probe exit=%s stdout=%r stderr=%r",
                    result.returncode,
                    result.stdout,
                    result.stderr,
                )
            if result.returncode == 255:
                stderr = (result.stderr or "").lower()
                if (
                    "connection reset by peer" in stderr
                    or "kex_exchange_identification" in stderr
                    or "connection closed" in stderr
                ):
                    return False
                # Authentication errors are permanent - raise exception to fail fast
                logger.debug(
                    f"SSH authentication failed for {user}@{host}:{port} with key {key_path}: {result.stderr}"
                )
                raise SshAuthenticationError(
                    f"SSH authentication failed: {result.stderr.strip()}",
                    key_path=key_path,
                    stderr=result.stderr,
                )
            return result.returncode == 0 and "SSH_OK" in (result.stdout or "")
        except subprocess.TimeoutExpired:
            return False
        except SshAuthenticationError:
            # Re-raise authentication errors to fail fast
            raise
        except Exception:  # noqa: BLE001
            return False
