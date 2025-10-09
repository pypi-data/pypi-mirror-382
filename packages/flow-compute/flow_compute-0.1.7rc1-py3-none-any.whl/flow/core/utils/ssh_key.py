"""SSH key utilities.

This module provides utilities for discovering, matching, and validating SSH keys
across local filesystem and platform APIs.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import os
import shutil
import subprocess
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from flow.adapters.providers.builtin.mithril.domain.models import PlatformSSHKey

# ============================================================================
# Type Definitions
# ============================================================================

# Type aliases for simple types
PlatformKeyID: TypeAlias = str  # Platform SSH key identifier (e.g., "sshkey_abc123")
Fingerprint: TypeAlias = str  # SSH key fingerprint


@dataclass(frozen=True, slots=True)
class LocalSSHKey:
    """Immutable representation of a local SSH key.

    Attributes:
        name: Display name of the key (typically the filename without extension)
        private_key_path: Absolute path to the private key file
    """

    name: str
    private_key_path: Path

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.name} ({self.private_key_path})"


# Public API exports
__all__ = [
    "SSH_KEY_SEARCH_LOCATIONS",
    "Fingerprint",
    "LocalSSHKey",
    "PlatformKeyID",
    "check_ssh_keygen_available",
    "discover_local_ssh_keys",
    "generate_public_key_from_private",
    "looks_like_ssh_key_file",
    "match_local_key_to_platform",
    "md5_fingerprint_from_public_key",
    "normalize_public_key",
    "sha256_fingerprint_from_public_key",
]


# Standard locations to search for SSH private keys
# Paths can be absolute or relative (relative paths are resolved from home directory)
SSH_KEY_SEARCH_LOCATIONS: Sequence[Path] = [
    Path.home() / ".ssh",  # Standard SSH directory
    Path.home() / ".flow" / "keys",  # Flow-managed keys (auto-generated, etc.)
    Path.home() / "Downloads",  # Common location for downloaded keys
]


def normalize_public_key(public_key: str) -> str:
    """Normalize SSH public key for comparison.

    Extracts the key type and base64 data, ignoring comments.

    Args:
        public_key: Raw public key content

    Returns:
        Normalized key string (type + base64 data)
    """
    # SSH public keys format: <type> <base64-data> [comment]
    parts = public_key.strip().split()
    if len(parts) >= 2:
        # Return type and key data only
        return f"{parts[0]} {parts[1]}"
    return public_key.strip()


def discover_local_ssh_keys(
    search_locations: Sequence[str | Path] = SSH_KEY_SEARCH_LOCATIONS,
) -> list[LocalSSHKey]:
    """Discover SSH private keys on the local filesystem.

    Scans standard locations and environment variables for SSH private keys.
    Returns only keys that exist and are readable.

    Args:
        search_locations: Directory paths to search. Can be absolute paths,
                         relative paths (resolved from home), or Path objects.
                         Defaults to SSH_KEY_SEARCH_LOCATIONS.

    Returns:
        List of LocalSSHKey objects for private keys that exist and are readable.
        All returned paths are guaranteed to exist at the time of the call.
    """
    results: list[LocalSSHKey] = []

    # Optional environment override (widely used in the codebase)
    try:
        env_key = os.environ.get("MITHRIL_SSH_KEY") or os.environ.get("Mithril_SSH_KEY")
        if env_key:
            p = Path(env_key).expanduser().resolve()
            if p.exists() and p.is_file() and p.suffix != ".pub":
                results.append(LocalSSHKey(name=p.name, private_key_path=p))
    except Exception:  # noqa: BLE001
        pass

    # Scan each configured location
    candidates: list[Path] = []
    for location in search_locations:
        # Convert to Path and handle both absolute and relative paths
        if isinstance(location, str):
            search_path = Path(location).expanduser()
            # If relative, resolve from home directory
            if not search_path.is_absolute():
                search_path = Path.home() / search_path
        else:
            search_path = location.expanduser()

        candidates.extend(_iter_private_keys(search_path))

    seen: set[Path] = set()
    for p in candidates:
        # Only include paths that exist and haven't been seen
        # This handles race conditions and broken symlinks
        if p not in seen and p.exists():
            seen.add(p)
            results.append(LocalSSHKey(name=p.name, private_key_path=p))

    return results


def _iter_private_keys(directory: Path) -> Iterable[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    ignored = {"known_hosts", "authorized_keys", "config", "metadata.json"}
    results: list[Path] = []

    # More selective filtering for Downloads directory
    is_downloads = directory.name == "Downloads"

    try:
        for p in directory.glob("*"):
            if not p.is_file() or p.suffix == ".pub" or p.name in ignored:
                continue

            # For Downloads, only include files that look like SSH keys
            if is_downloads and not looks_like_ssh_key_file(p):
                continue

            # Normalize paths for consistent comparison
            try:
                normalized = p.resolve()
            except Exception:  # noqa: BLE001
                # If resolve() fails, skip this path (likely broken symlink or permission issue)
                continue

            results.append(normalized)
    except Exception:  # noqa: BLE001
        return []
    return results


def looks_like_ssh_key_file(path: Path) -> bool:
    """Check if a file looks like it could be an SSH key."""
    name = path.name.lower()

    # Common SSH key file patterns
    return any(
        pattern in name
        for pattern in ["id_", "ssh", "key", "rsa", "ed25519", "ecdsa", "dsa", ".pem"]
    )


def md5_fingerprint_from_public_key(public_key: str) -> Fingerprint | None:
    """Return MD5 fingerprint (colon-delimited) of an SSH public key string.

    Args:
        public_key: SSH public key content in authorized_keys format

    Returns:
        Fingerprint like "aa:bb:..." or None if parsing fails.
    """
    try:
        parts = (public_key or "").strip().split()
        if len(parts) >= 2:
            b64 = parts[1]
            # Tolerate missing padding commonly seen in SSH public keys
            pad_len = (-len(b64)) % 4
            if pad_len:
                b64 = b64 + ("=" * pad_len)
            decoded = base64.b64decode(b64.encode())
            md5_hex = hashlib.md5(decoded).hexdigest()  # nosec - fingerprint only
            return ":".join(md5_hex[i : i + 2] for i in range(0, len(md5_hex), 2))
    except Exception:  # noqa: BLE001
        return None
    return None


def sha256_fingerprint_from_public_key(public_key: str) -> Fingerprint | None:
    """Return OpenSSH SHA256 fingerprint (base64) for a public key string.

    Args:
        public_key: SSH public key content in authorized_keys format

    Returns:
        Fingerprint like "SHA256:abc..." or None if parsing fails.
    """
    try:
        parts = (public_key or "").strip().split()
        if len(parts) >= 2:
            b64 = parts[1]
            pad_len = (-len(b64)) % 4
            if pad_len:
                b64 = b64 + ("=" * pad_len)
            decoded = base64.b64decode(b64.encode())
            sha256 = hashlib.sha256(decoded).digest()
            b64 = base64.b64encode(sha256).decode("utf-8").rstrip("=")
            return f"SHA256:{b64}"
    except Exception:  # noqa: BLE001
        return None
    return None


def generate_public_key_from_private(private_path: Path) -> str | None:
    """Generate public key from existing private key using ssh-keygen.

    Args:
        private_path: Path to the private key file.

    Returns:
        The public key content as a string, or None if generation fails.
    """
    if not private_path.exists() or not private_path.is_file():
        return None

    # Check if ssh-keygen is available first
    if not check_ssh_keygen_available():
        return None

    # Build ssh-keygen command to extract public key
    cmd = [
        "ssh-keygen",
        "-y",  # Extract public key
        "-f",
        str(private_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None

        public_key_content = result.stdout.strip()
        return public_key_content if public_key_content else None

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        return None


def check_ssh_keygen_available() -> bool:
    """Check if ssh-keygen is available on the system.

    Returns:
        bool: True if ssh-keygen is found in PATH, False otherwise.
    """
    if shutil.which("ssh-keygen"):
        return True

    logger = logging.getLogger(__name__)
    logger.warning(
        "ssh-keygen not found. SSH keys cannot be auto-generated. "
        "Install OpenSSH or manually create keys."
    )
    return False


# ============================================================================
# SSH Key Matching Utilities
# ============================================================================


def match_local_key_to_platform(
    local_key_path: Path,
    platform_keys: Sequence[PlatformSSHKey],
    *,
    match_by_name: bool = True,
) -> PlatformKeyID | None:
    """Find platform key matching a local private key.

    Tries multiple strategies in order of reliability:
    1. Public key content match (cryptographically certain)
    2. Fingerprint match (when public key not available on platform)
    3. Name match (fallback, only if match_by_name=True)

    Args:
        local_key_path: Path to local private key
        platform_keys: Sequence of platform key objects implementing PlatformSSHKey protocol
        match_by_name: Whether to fall back to name matching

    Returns:
        Platform key ID (fid) if match found, None otherwise
    """
    # Try public key content match first, but only if this looks like an SSH key file
    if looks_like_ssh_key_file(local_key_path):
        platform_id = _match_by_public_key_content(local_key_path, platform_keys)
        if platform_id:
            return platform_id

    # Fall back to fingerprint match
    platform_id = _match_by_fingerprint(local_key_path, platform_keys)
    if platform_id:
        return platform_id

    # Fall back to name match if enabled
    if match_by_name:
        platform_id = _match_by_name(local_key_path, platform_keys)
        if platform_id:
            return platform_id

    return None


def _match_by_public_key_content(
    local_key_path: Path, platform_keys: Sequence[PlatformSSHKey]
) -> PlatformKeyID | None:
    """Match local key to platform key by comparing public key content."""
    pub_path = local_key_path.with_suffix(".pub")
    local_pub = None

    # Try to read existing .pub file first
    if pub_path.exists():
        local_pub = pub_path.read_text().strip()

    # If no .pub file exists or couldn't read it, try to generate public key from private key
    if not local_pub:
        local_pub = generate_public_key_from_private(local_key_path)
        if not local_pub:
            return None

    local_pub_normalized = normalize_public_key(local_pub)

    for pkey in platform_keys:
        if not pkey.public_key:
            continue

        if normalize_public_key(pkey.public_key) == local_pub_normalized:
            return pkey.fid

    return None


def _match_by_fingerprint(
    local_key_path: Path, platform_keys: Sequence[PlatformSSHKey]
) -> PlatformKeyID | None:
    """Match local key to platform key by comparing MD5 fingerprints."""
    pub_path = local_key_path.with_suffix(".pub")
    if not pub_path.exists():
        return None

    try:
        local_pub = pub_path.read_text().strip()
        local_fp = md5_fingerprint_from_public_key(local_pub)
        if not local_fp:
            return None
        local_fp_normalized = local_fp.replace(":", "").lower()
    except Exception:  # noqa: BLE001
        return None

    for pkey in platform_keys:
        if not pkey.fingerprint:
            continue

        try:
            platform_fp_normalized = pkey.fingerprint.replace(":", "").lower()
            if local_fp_normalized == platform_fp_normalized:
                return pkey.fid
        except Exception:  # noqa: BLE001
            continue

    return None


def _match_by_name(
    local_key_path: Path, platform_keys: Sequence[PlatformSSHKey]
) -> PlatformKeyID | None:
    """Match local key to platform key by name (after stripping common extensions)."""
    # Strip common key file extensions for comparison
    key_name = local_key_path.stem
    clean_name = key_name
    for ext in [".pem", ".key", ".private"]:
        if clean_name.endswith(ext):
            clean_name = clean_name[: -len(ext)]
            break

    for pkey in platform_keys:
        if pkey.name and clean_name == pkey.name:
            return pkey.fid

    return None
