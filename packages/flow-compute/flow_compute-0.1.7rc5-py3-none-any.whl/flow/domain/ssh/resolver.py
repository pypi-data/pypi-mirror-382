"""Domain-level SSH key reference parsing and local resolution utilities.

Implements resolver logic without depending on provider implementations.
Consumers should pass in an object implementing the SSHKeyLocatorProtocol to
handle platform-ID → local-private-key matching.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(slots=True)
class SSHKeyReference:
    """Represents a parsed SSH key reference.

    Attributes:
        type: One of "platform_id", "local", or "name".
        value: The original, user-supplied value.
    """

    type: str
    value: str

    @staticmethod
    def from_config_value(value: str) -> SSHKeyReference:
        """Parse a config/CLI value into a typed SSH key reference."""
        if not isinstance(value, str):
            return SSHKeyReference("name", str(value))

        v = value.strip()
        if v.startswith("sshkey_"):
            return SSHKeyReference("platform_id", v)
        if v.startswith("/") or v.startswith("~/") or ("/" in v):
            return SSHKeyReference("local", v)
        return SSHKeyReference("name", v)


class SSHKeyLocatorProtocol(Protocol):
    """Minimal protocol for locating local private keys for platform keys.

    Defined locally to avoid depending on the ports package from the domain layer.
    """

    def find_matching_local_key(
        self, api_key_id: str
    ) -> Path | None:  # pragma: no cover - protocol
        ...

    def list_keys(self) -> list[object]:  # pragma: no cover - protocol
        ...


class SmartSSHKeyResolver:
    """Resolves SSH key references to local private key paths.

    Depends only on the SSHKeyLocatorProtocol to avoid provider coupling.
    """

    def __init__(self, ssh_key_manager: SSHKeyLocatorProtocol):
        self._mgr = ssh_key_manager

    def resolve_ssh_key(self, ref: SSHKeyReference | str) -> Path | None:
        """Resolve a key reference (or raw string) to a local private key path."""
        if isinstance(ref, str):
            ref = SSHKeyReference.from_config_value(ref)

        if ref.type == "platform_id":
            # Prefer identity mapping cache for instant resolution
            try:
                from flow.core.keys.identity import get_local_key_private_path as _id_get

                mapped = _id_get(ref.value)
                if mapped is not None and mapped.exists():
                    return mapped
            except Exception:  # noqa: BLE001
                pass
            try:
                return self._mgr.find_matching_local_key(ref.value)
            except Exception:  # noqa: BLE001
                return None

        if ref.type in {"local", "name"}:
            path = self._resolve_local_path_candidate(ref.value)
            if path is not None:
                return path
            if ref.type == "name":
                return self._search_common_key_locations(ref.value)

        return None

    def _resolve_local_path_candidate(self, value: str) -> Path | None:
        try:
            p = Path(value).expanduser()
        except Exception:  # noqa: BLE001
            return None
        if p.suffix == ".pub":
            priv = p.with_suffix("")
            return priv if priv.exists() else None
        return p if p.exists() and p.is_file() else None

    def _search_common_key_locations(self, name: str) -> Path | None:
        for d in [Path.home() / ".ssh", Path.home() / ".flow" / "keys"]:
            try:
                candidate = d / name
                if candidate.exists() and candidate.is_file():
                    return candidate
            except Exception:  # noqa: BLE001
                continue
        return None
