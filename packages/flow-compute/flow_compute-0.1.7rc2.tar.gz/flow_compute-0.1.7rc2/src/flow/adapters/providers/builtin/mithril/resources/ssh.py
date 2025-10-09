"""SSH key management component for the Mithril provider.

Provides SSH key operations including automatic provisioning and error handling.
"""

import json
import logging
import os
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.api.types import SSHKeyModel as SSHKey
from flow.cli.utils.user_utils import get_sanitized_username_from_api
from flow.core.events.key_events import SSH_KEYS_CHANGED, KeyEventBus
from flow.core.keys.identity import (
    find_key_metadata,
    friendly_path_name,
    get_last_auto_generated_key,
    get_local_key_private_path,
    store_key_metadata,
)
from flow.core.keys.identity import (
    get_local_key_private_path as get_local_key_private_path_via_identity,
)
from flow.core.utils.ssh_key import (
    check_ssh_keygen_available,
    discover_local_ssh_keys,
    match_local_key_to_platform,
)
from flow.core.utils.ssh_key_cache import SSHKeyCache
from flow.domain.ssh import SSHKeyError, SSHKeyNotFoundError
from flow.errors import AuthenticationError
from flow.sdk.helpers.security import check_ssh_key_permissions

logger = logging.getLogger(__name__)


class SSHKeyManager:
    """Manages SSH keys with automatic provisioning and caching."""

    def __init__(
        self,
        api_client: MithrilApiClient | None = None,
        get_project_id: Callable | None = None,
        **kwargs,
    ):
        """Initialize SSH key manager.

        Args:
            api_client: API client for requests
            get_project_id: Function to get project ID for scoped operations
        """
        # Accept either MithrilApiClient via 'api_client' or raw HttpClientPort via legacy 'http_client'
        if api_client is None and "http_client" in kwargs:
            http_client = kwargs.get("http_client")
            # Wrap legacy http client
            from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient as _Api

            api_client = _Api(http_client)  # type: ignore[arg-type]

        assert api_client is not None, "api_client or http_client is required"
        # Keep both references when possible for centralized operations
        self._api: MithrilApiClient = api_client  # type: ignore[assignment]
        self.http = getattr(api_client, "_http", None) or api_client  # type: ignore[assignment]
        self._get_project_id = get_project_id
        self._keys_cache: list[SSHKey] | None = None
        # Determine environment from API URL to store keys separately
        api_url = (
            getattr(api_client, "_config", {}).get("api_url", "")
            if hasattr(api_client, "_config")
            else ""
        )
        if not api_url:
            try:
                from flow.application.config.loader import ConfigLoader

                loader = ConfigLoader()
                sources = loader.load_all_sources()
                mithril_config = sources.get_mithril_config()
                api_url = mithril_config.get("api_url", "https://api.mithril.ai")
            except Exception:  # noqa: BLE001
                api_url = "https://api.mithril.ai"

        # Use environment-specific key directory
        if "staging.mithril.ai" in api_url:
            self._key_dir = Path.home() / ".flow" / "keys" / "staging"
        else:
            self._key_dir = Path.home() / ".flow" / "keys" / "production"

    def _resolve_project_id(self) -> str | None:
        """Get project ID using the provided getter.

        Returns:
            Project ID if available, None otherwise
        """
        if self._get_project_id:
            try:
                return self._get_project_id()
            except Exception:  # noqa: BLE001
                return None
        return None

    def ensure_keys(self, requested_keys: list[str] | None = None) -> list[str]:
        """Ensure SSH keys are available for use.

        This method follows a fallback strategy:
        1. Use explicitly provided key IDs if given
        2. Use existing keys from the project
        3. Optionally create a default key if none exist

        Args:
            requested_keys: Optional list of specific SSH key IDs to use

        Returns:
            List of SSH key IDs ready for use

        Raises:
            SSHKeyNotFoundError: If no keys can be obtained
        """
        # Use explicitly provided keys if given
        if requested_keys:
            logger.debug(f"Using {len(requested_keys)} explicitly provided SSH keys")
            return requested_keys

        # Get existing keys
        existing_keys = self.list_keys()
        if existing_keys:
            key_ids = [key.fid for key in existing_keys]
            logger.debug(f"Using {len(key_ids)} existing SSH keys from project")
            return key_ids

        # No keys available
        logger.debug("No SSH keys available for the project")

        # Optionally try to create a default key from environment
        if default_key := self._try_create_default_key():
            return [default_key]

        # Return empty list - let the caller decide if this is an error
        return []

    def list_keys(self) -> list[SSHKey]:
        """List all SSH keys for the project.

        Returns:
            List of SSHKey objects
        """
        if self._keys_cache is not None:
            return self._keys_cache

        try:
            params = {}
            if project_id := self._resolve_project_id():
                params["project"] = project_id  # API expects 'project', not 'project_id'

            response = self._api.list_ssh_keys(params)

            # API returns list directly
            keys_data = response if isinstance(response, list) else []

            # Normalize optional fields like `required` which some APIs expose
            normalized_keys: list[SSHKey] = []
            for k in keys_data:
                if "fid" not in k or "name" not in k:
                    continue
                try:
                    normalized_keys.append(SSHKey.from_api(k))
                except Exception:  # noqa: BLE001
                    # Fallback minimal mapping if shape drifts
                    normalized_keys.append(
                        SSHKey(
                            fid=k.get("fid", ""),
                            name=k.get("name", ""),
                            public_key=k.get("public_key", ""),
                            fingerprint=k.get("fingerprint"),
                            created_at=k.get("created_at"),
                            required=k.get("required"),
                        )
                    )

            self._keys_cache = normalized_keys

            logger.debug(f"Loaded {len(self._keys_cache)} SSH keys from API")
            return self._keys_cache

        except Exception as e:  # noqa: BLE001
            # Never surface low-level provider validation noise to CLI display.
            # Log at debug level and return empty to trigger graceful fallbacks.
            try:
                msg = str(e)
            except Exception:  # noqa: BLE001
                msg = "<unknown error>"
            logger.debug(f"Fetching SSH keys failed; continuing without keys: {msg}")
            return []

    def create_key(self, name: str, public_key: str | None = None) -> str:
        """Create a new SSH key.

        Args:
            name: Key name
            public_key: SSH public key content (optional - if not provided, Mithril generates one)

        Returns:
            ID of the created key

        Raises:
            SSHKeyError: If key creation fails
        """
        payload = {
            "name": name,
        }

        # Only include public_key if provided
        if public_key:
            payload["public_key"] = public_key.strip()

        if project_id := self._resolve_project_id():
            payload["project"] = project_id

        try:
            response = self._api.create_ssh_key(payload)

            key_id = response.get("fid")
            if not key_id:
                raise SSHKeyError(f"No key ID returned in response: {response}")

            # Invalidate cache (API + task key-path cache)
            self.invalidate_cache()

            logger.info(f"Created SSH key '{name}' with ID: {key_id}")
            return key_id

        except Exception as e:
            raise SSHKeyError(f"Failed to create SSH key '{name}': {e}") from e

    def delete_key(self, key_id: str) -> bool:
        """Delete an SSH key.

        Args:
            key_id: SSH key ID to delete

        Returns:
            True if successful, False otherwise

        Raises:
            SSHKeyNotFoundError: If the key doesn't exist
            SSHKeyError: For other deletion failures
        """
        try:
            self._api.delete_ssh_key(key_id)

            # Invalidate cache (API + task key-path cache)
            self.invalidate_cache()

            logger.info(f"Deleted SSH key: {key_id}")
            return True

        except Exception as e:
            # Preserve the original error for better debugging
            error_msg = str(e)
            if "not found" in error_msg.lower():
                # Log as debug since this is an expected condition handled by CLI
                logger.debug(f"SSH key {key_id} not found during deletion: {e}")
                raise SSHKeyNotFoundError(f"SSH key {key_id} not found") from e
            # Log actual errors at error level
            logger.error(f"Failed to delete SSH key {key_id}: {e}")
            raise SSHKeyError(f"Failed to delete SSH key {key_id}: {error_msg}") from e

    def get_key(self, key_id: str) -> SSHKey | None:
        """Get a specific SSH key by ID.

        Args:
            key_id: SSH key ID

        Returns:
            SSHKey if found, None otherwise
        """
        keys = self.list_keys()
        for key in keys:
            if key.fid == key_id:
                return key
        return None

    def find_key_by_name(self, name: str) -> SSHKey | None:
        """Find SSH keys by name.

        Args:
            name: Key name to search for

        Returns:
            Matching SSH key (may be None)
        """
        keys = self.list_keys()
        for key in keys:
            if key.name == name:
                return key
        return None

    def invalidate_cache(self):
        """Clear the cache, forcing fresh lookups."""
        self._keys_cache = None
        try:
            # Also clear the task-id → key-path cache to prevent stale SSH keys
            # being used after key create/delete operations.
            SSHKeyCache().clear()
        except Exception as e:  # noqa: BLE001
            # Best-effort: cache invalidation should never hard-fail operations
            logger.debug(f"Failed to clear SSHKeyCache: {e}")
        # Higher-level caches should subscribe to events; no direct coupling here
        logger.debug("SSH key caches invalidated")
        # Emit decoupled event for listeners interested in key changes
        try:
            KeyEventBus.emit(SSH_KEYS_CHANGED, payload={"source": "SSHKeyManager.invalidate_cache"})
        except Exception:  # noqa: BLE001
            pass

    def ensure_one_local_key(self, platform_key_ids: list[str]) -> list[str]:
        """Ensure there is at least one local key in the list or auto-generate one"""
        for key_id in platform_key_ids:
            key_metadata = get_local_key_private_path(key_id)
            if key_metadata:
                logger.debug(f"ensure_one_local_key: Found local key: {key_id}")
                return platform_key_ids

        # No local key found, add an auto-generated one
        platform_key_ids.append(self.ensure_auto_generated_key())
        logger.debug(f"ensure_one_local_key: Added auto-generated key: {platform_key_ids[-1]}")
        return platform_key_ids

    def ensure_platform_keys(self, key_references: list[str]) -> list[str]:
        """Ensure local SSH keys are uploaded to platform.

        This method handles different key reference types:
        - Platform IDs (sshkey_*): Used directly
        - Key names: Resolved locally and uploaded if needed
        - Paths: Read and uploaded if needed

        Note: _auto_ is handled at a higher level in the provider's _get_ssh_keys method.

        Args:
            key_references: List of key references (names, paths, or platform IDs)

        Returns:
            List of platform SSH key IDs (sshkey_*)
        """
        platform_key_ids = []

        for key_ref in key_references:
            # Skip _auto_ - it should be handled at provider level
            # TODO(oliviert): It's unclear if _auto_ is still a thing.
            logger.debug(f"ensure_platform_keys: Checking key: {key_ref}")
            if key_ref == "_auto_":
                logger.debug(
                    "Skipping '_auto_' in ensure_platform_keys - should be handled at provider level"
                )
                continue

            # Platform SSH key IDs are already resolved
            if key_ref.startswith("sshkey_"):
                logger.debug(f"ensure_platform_keys: Found platform key: {key_ref}")
                platform_key_ids.append(key_ref)
                continue

            # Check if we already have metadata (key is on platform)
            key_metadata = find_key_metadata(key_ref=str(key_ref))
            if key_metadata:
                logger.debug(f"ensure_platform_keys: Found key metadata: {key_metadata}")
                platform_key_ids.append(key_metadata["key_id"])
                continue

            # Try to resolve as local file path first
            resolved_key_id = self.get_or_create_key_if_file_path(key_ref)
            if resolved_key_id:
                logger.debug(f"ensure_platform_keys: Found resolved key: {resolved_key_id}")
                platform_key_ids.append(resolved_key_id)
                continue

            # Fall back to API lookup by name
            found_key = self.find_key_by_name(key_ref)
            if found_key:
                logger.debug(f"ensure_platform_keys: Found key by name: {found_key.fid}")
                # Use the first matching key (there should typically be only one)
                platform_key_ids.append(found_key.fid)
                continue

            # If nothing worked, raise error
            raise SSHKeyNotFoundError(
                f"Could not resolve SSH key '{key_ref}'\n"
                f"  - Not found locally in ~/.ssh/\n"
                f"  - Not found on platform (check 'flow ssh-key list')\n"
                f"  - May have different format (RSA vs ED25519)"
            )

        return list(set(platform_key_ids))

    def append_required_keys(self, key_ids: list[str]) -> list[str]:
        """Add required keys to the list of keys."""
        required_keys = [k for k in self.list_keys() if getattr(k, "required", False)]
        required_key_ids = [k.fid for k in required_keys]
        return list(set(required_key_ids + key_ids))

    def append_mithril_env_key(self, key_ids: list[str]) -> list[str]:
        """Adds MITHRIL_SSH_KEY to the list of keys if it is set."""
        env_key_path = os.environ.get("MITHRIL_SSH_KEY")
        if not env_key_path:
            return key_ids
        env_path = Path(env_key_path).expanduser()
        if env_path.is_file():
            ensured = self.ensure_platform_keys([str(env_path)])
            logger.info("Using SSH key from MITHRIL_SSH_KEY for launch")
            return list(set(key_ids + ensured))
        else:
            return key_ids

    def get_or_create_key_if_file_path(self, key_ref: str, name: str | None = None) -> str | None:
        """Try to resolve key_ref as a file path and upload if needed.

        Returns:
            Platform key ID if successful, None if not a valid file path
        """

        # Early exit if this doesn't look like a file path at all
        logger.debug(
            f"get_or_create_key_if_file_path: Checking if {key_ref} looks like a file path"
        )
        if not self._looks_like_file_path(key_ref):
            logger.debug(
                f"get_or_create_key_if_file_path: {key_ref} does not look like a file path"
            )
            return None

        return self.upload_key(Path(key_ref), name, deduplicate=True)

    def upload_key(
        self, path: Path, name: str | None = None, deduplicate: bool = True
    ) -> str | None:
        """Upload a key to the platform."""

        path = path.expanduser()
        if path.suffix == ".pub":
            private_path, public_path = path.with_suffix(""), path
        else:
            private_path, public_path = path, Path(str(path) + ".pub")

        if not private_path.is_file():
            raise SSHKeyNotFoundError(
                f"Cannot find private key at {private_path}.\n"
                f"  - Ensure both private and public keys exist\n"
                f"  - Run 'ssh-keygen -y -f {private_path} > {private_path}.pub' to regenerate"
            )

        if public_path.is_file():
            logger.debug(f"get_or_create_key_if_file_path: Found public key for {private_path}")
            public_key_content = public_path.read_text().strip()
        else:
            logger.debug(
                f"get_or_create_key_if_file_path: No public key found for {private_path}, generating..."
            )
            if check_ssh_keygen_available():
                logger.debug(
                    f"get_or_create_key_if_file_path: Generating public key for {private_path}"
                )
                public_key_content = self._generate_public_key_from_private(private_path)
            else:
                raise SSHKeyNotFoundError(
                    f"Cannot find public key at {public_path}.\n"
                    f"  - Ensure both private and public keys exist\n"
                    f"  - Run 'ssh-keygen -y -f {private_path} > {private_path}.pub' to regenerate"
                )

        key_name = name or friendly_path_name(private_path)

        # Check if key already exists on platform
        if deduplicate:
            existing_key_id = self._find_existing_key_by_content(public_key_content)
            if existing_key_id:
                logger.info(f"SSH key '{path}' already exists on platform as {existing_key_id}")
                self._store_key_mapping(existing_key_id, key_name, private_path)
                return existing_key_id

        # Upload new key
        try:
            platform_key_id = self.create_key(key_name, public_key_content)
            logger.info(f"Uploaded SSH key '{path}' to platform as {platform_key_id}")
            self._store_key_mapping(platform_key_id, key_name, private_path)
            return platform_key_id
        except Exception as e:
            raise SSHKeyError(f"Failed to upload SSH key '{path}': {e}") from e

    def _store_key_mapping(self, platform_key_id: str, key_name: str, private_path: Path) -> None:
        """Store key metadata and invalidate cache."""
        store_key_metadata(
            key_id=platform_key_id,
            key_name=key_name,
            private_key_path=private_path,
            project_id=self._resolve_project_id(),
            auto_generated=False,
        )
        self.invalidate_cache()

    def ensure_public_key(self, public_key: str, name: str | None = None) -> str:
        """Ensure a given public key exists on the platform and return its ID.

        Args:
            public_key: SSH public key content
            name: Optional display name to use if creating

        Returns:
            Platform SSH key ID
        """
        existing = self._find_existing_key_by_content(public_key)
        if existing:
            return existing
        key_name = name or "flow-key"
        return self.create_key(key_name, public_key)

    def _find_existing_key_by_content(self, public_key_content: str) -> str | None:
        """Find platform key with matching public key content.

        Args:
            public_key_content: SSH public key content

        Returns:
            Platform key ID if found, None otherwise
        """
        existing_keys = self.list_keys()

        # Normalize the key content for comparison
        normalized_content = public_key_content.strip()

        for key in existing_keys:
            if (
                hasattr(key, "public_key")
                and key.public_key
                and key.public_key.strip() == normalized_content
            ):
                return key.fid

        return None

    def _try_create_default_key(self) -> str | None:
        """Try to create a default SSH key for Mithril use.

        Selection order:
        1) MITHRIL_SSH_PUBLIC_KEY (content) -> create_key("flow-env-key", ...)
        2) MITHRIL_SSH_KEY (path)
           - if private key with secure perms and .pub exists -> create_key("flow-mithril-key", ...)
           - if .pub directly -> create_key("flow-mithril-key", ...)
           - if private key with insecure perms -> call auto_generate_key()
        3) Default local key ~/.ssh/id_rsa (secure perms and .pub exist) -> create_key("flow-default-id_rsa", ...)
        4) Previously auto-generated key (metadata cache)
        5) Auto-generate a fresh key (server/local)

        Returns:
            Key ID if created, or "ssh-key_auto" when a new key is auto-generated.
        """
        # 1) Public key content env
        env_pub = os.environ.get("MITHRIL_SSH_PUBLIC_KEY")
        if not env_pub:
            legacy_env_pub = os.environ.get("Mithril_SSH_PUBLIC_KEY")
            if legacy_env_pub:
                logger.warning(
                    "Environment variable 'Mithril_SSH_PUBLIC_KEY' is deprecated. Use 'MITHRIL_SSH_PUBLIC_KEY'."
                )
                env_pub = legacy_env_pub
        if env_pub:
            return self.create_key("flow-env-key", env_pub)

        # 2) File path env
        env_key = os.environ.get("MITHRIL_SSH_KEY")
        if not env_key:
            legacy_env_key = os.environ.get("Mithril_SSH_KEY")
            if legacy_env_key:
                logger.warning(
                    "Environment variable 'Mithril_SSH_KEY' is deprecated. Use 'MITHRIL_SSH_KEY'."
                )
                env_key = legacy_env_key
        if env_key:
            key_path = Path(env_key)
            if key_path.exists():
                if key_path.suffix == ".pub":
                    public_key = key_path.read_text().strip()
                    return self.create_key("flow-mithril-key", public_key)
                else:
                    pub_key = key_path.with_suffix(".pub")
                    if not pub_key.exists():
                        return self.auto_generate_key()
                    try:
                        check_ssh_key_permissions(key_path)
                    except Exception:  # noqa: BLE001
                        # Insecure permissions → fall back to auto generation
                        return self.auto_generate_key()
                    public_key = pub_key.read_text().strip()
                    return self.create_key("flow-mithril-key", public_key)
            # Missing file → auto-generate per tests
            return self.auto_generate_key()

        # 3) Default local key ~/.ssh/id_rsa (only when secure)
        default_priv = Path.home() / ".ssh" / "id_rsa"
        default_pub = default_priv.with_suffix(".pub")
        if default_priv.exists() and default_pub.exists():
            try:
                check_ssh_key_permissions(default_priv)
                public_key = default_pub.read_text().strip()
                return self.create_key("flow-default-id_rsa", public_key)
            except Exception:  # noqa: BLE001
                # Insecure default key → fall back to auto generation
                return self.auto_generate_key()

        # 4) Previously auto-generated key (reuse only if local private exists and platform key is present)
        return self.ensure_auto_generated_key()

    def ensure_auto_generated_key(self) -> str:
        """Ensure an auto-generated key exists for the project."""
        auto_generated_key = get_last_auto_generated_key(self._resolve_project_id())
        if auto_generated_key:
            return auto_generated_key
        return self.auto_generate_key()

    def auto_generate_key(self) -> str:
        """Auto-generate an SSH key

        Returns:
            SSH key ID
        """
        # Prevent duplicate generation in concurrent runs via a simple file lock
        lock_path: Path | None = None
        try:
            lock_path = self._acquire_autogen_lock(timeout=10.0)
            return self.generate_server_key(auto_generated=True)
        finally:
            if lock_path is not None:
                self._release_autogen_lock(lock_path)

    def generate_server_key(self, *, auto_generated: bool = False) -> str:
        """Generate SSH key server-side using Mithril API.

        This is simpler than local generation as it doesn't require ssh-keygen.
        Mithril returns both public and private keys which we save locally.

        Returns:
            SSH key ID
        """
        try:
            # Generate unique name with timestamp
            import random

            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            user_name = self._get_user_name_for_key()
            key_name = f"flow-auto-{user_name or timestamp}-{random_suffix}"

            logger.info("Generating SSH key server-side...")

            # Make direct API call to get full response including private key
            # Validate project ID
            project_id = self._resolve_project_id()
            if not project_id:
                raise ValueError("Project ID is required for SSH key generation")

            request_payload = {
                "name": key_name,
                "project": project_id,
                # No public_key - server will generate both keys
            }
            logger.info(f"SSH key generation request: name={key_name}, project={project_id}")

            # TODO(oliviert): add pydantic validation
            response = self._api.create_ssh_key(request_payload)

            key_id = response.get("fid")
            if not key_id:
                raise SSHKeyError("No key ID in server response")

            logger.debug(f"Generated SSH key: {key_id} ({response.get('name')})")

            # Save private key locally if returned
            if "private_key" in response:
                logger.info("Saving private key locally...")

                # Ensure key directory exists
                self._key_dir.mkdir(parents=True, exist_ok=True)

                # Save private key
                private_path = self._key_dir / key_name
                private_path.write_text(response["private_key"])
                private_path.chmod(0o600)  # Set proper permissions

                # Save public key if available
                if "public_key" in response:
                    public_path = self._key_dir / f"{key_name}.pub"
                    public_path.write_text(response["public_key"])
                    public_path.chmod(0o644)

                store_key_metadata(
                    key_id=key_id,
                    key_name=key_name,
                    private_key_path=private_path,
                    project_id=self._resolve_project_id(),
                    auto_generated=auto_generated,
                )

                logger.info(f"Server-generated SSH key: {key_id}")
                logger.info(f"Private key saved to: {private_path}")
                return key_id

            raise SSHKeyError("No private key in server response")

        except Exception as e:
            raise SSHKeyError(
                f"Failed to generate SSH key server-side: {type(e).__name__}: {e}"
            ) from e

    def _generate_public_key_from_private(self, private_path: Path) -> str:
        """Generate public key from existing private key using ssh-keygen.

        Args:
            private_path: Path to the private key file.

        Returns:
            The public key content as a string.

        Raises:
            SSHKeyError: If ssh-keygen fails or returns non-zero exit code.
        """

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
                raise SSHKeyError(
                    f"Failed to generate public key from {private_path}: {result.stderr}"
                )

            public_key_content = result.stdout.strip()
            return public_key_content

        except subprocess.TimeoutExpired as e:
            raise SSHKeyError(
                f"ssh-keygen timed out while generating public key from {private_path}"
            ) from e

    def _acquire_autogen_lock(self, timeout: float = 10.0) -> Path | None:
        """Acquire a simple lock to serialize auto-generation across processes.

        Creates a lock file in the key directory, waiting up to timeout seconds.

        Returns:
            Path to the lock file if acquired, otherwise None (lock not acquired).
        """
        try:
            self._key_dir.mkdir(parents=True, exist_ok=True)
        except Exception:  # noqa: BLE001
            pass

        lock_file = self._key_dir / ".autogen.lock"
        deadline = time.time() + max(0.0, float(timeout))
        while time.time() < deadline:
            try:
                # Exclusive create; fails if file exists
                with open(lock_file, "x") as f:
                    f.write(str(os.getpid()))
                return lock_file
            except FileExistsError:
                # If stale (>60s), remove
                try:
                    if lock_file.exists():
                        mtime = lock_file.stat().st_mtime
                        if time.time() - mtime > 60:
                            lock_file.unlink(missing_ok=True)
                except Exception:  # noqa: BLE001
                    pass
                time.sleep(0.2)
            except Exception:  # noqa: BLE001
                break
        # Could not acquire; continue without lock to avoid blocking indefinitely
        return None

    def _release_autogen_lock(self, lock_path: Path) -> None:
        """Release the auto-generation lock if we own it."""
        try:
            if lock_path.exists():
                lock_path.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass

    def find_matching_local_key(self, api_key_id: str) -> Path | None:
        """Find local private key that matches an API SSH key.

        Searches standard SSH locations and cached metadata to find
        a local private key corresponding to the given API key ID.

        Args:
            api_key_id: Mithril SSH key ID to match

        Returns:
            Path to matching private key if found, None otherwise
        """
        # Get API key details
        api_key = self.get_key(api_key_id)
        if not api_key:
            logger.debug(f"API key {api_key_id} not found")
            return None

        # Check identity graph/metadata cache first
        try:
            cached_key = get_local_key_private_path_via_identity(api_key_id)
            if cached_key and cached_key.exists():
                logger.debug(
                    f"Resolved private key via identity mapping for {api_key_id} -> {cached_key}"
                )
                return cached_key
        except Exception:  # noqa: BLE001
            # Fallback to legacy metadata lookup
            cached_key = self._check_metadata_for_key(api_key_id)
            if cached_key and cached_key.exists():
                logger.debug(f"Resolved private key via metadata for {api_key_id} -> {cached_key}")
                return cached_key

        local_keys = discover_local_ssh_keys()
        logger.debug(f"Found {len(local_keys)} local SSH keys to check")

        # Try to match each local key against the platform key
        # match_local_key_to_platform expects a list of platform keys, so wrap in a list
        # Note: discover_local_ssh_keys guarantees all returned paths exist
        for key_pair in local_keys:
            # Try matching this local key to the platform key
            logger.debug(
                f"Comparing local key {key_pair.private_key_path} against platform key {api_key_id}"
            )
            matched_id = match_local_key_to_platform(
                key_pair.private_key_path, [api_key], match_by_name=True
            )
            if matched_id == api_key_id:
                logger.debug(
                    f"Matched platform key {api_key_id} ({api_key.name}) to local private key {key_pair.private_key_path}"
                )
                return key_pair.private_key_path

        logger.debug(f"No matching local key found for {api_key_id} ({api_key.name})")
        return None

    def _check_metadata_for_key(self, api_key_id: str) -> Path | None:
        """Check metadata cache for auto-generated key.

        Args:
            api_key_id: Mithril SSH key ID

        Returns:
            Path to private key if found in metadata, None otherwise
        """
        metadata_path = Path.home() / ".flow" / "keys" / "metadata.json"
        if not metadata_path.exists():
            return None

        try:
            metadata = json.loads(metadata_path.read_text())
            if api_key_id in metadata:
                key_info = metadata[api_key_id]
                private_path = Path(key_info.get("private_key_path", ""))
                if private_path.exists():
                    return private_path
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Error reading metadata: {e}")

        return None

    # --- Admin operations ---
    def set_key_required(self, key_id: str, required: bool) -> bool:
        """Set or clear the 'required' flag on an SSH key.

        Requires project admin privileges on Mithril. When a key is marked as
        required, the platform expects it to be included in all new launches
        for the project. Flow also auto-includes required keys for convenience.

        Args:
            key_id: Platform SSH key ID (e.g., sshkey_abc123)
            required: True to mark as required, False to clear required flag

        Returns:
            True if the update succeeded, False otherwise
        """
        try:
            self._api.patch_ssh_key(key_id, {"required": bool(required)})
            # Invalidate cache so list_keys reflects latest state
            self.invalidate_cache()
            return True
        except AuthenticationError:
            # Bubble up explicit auth/permission errors so CLI can show actionable text
            raise
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to update required flag for SSH key {key_id}: {e}")
            return False

    def _get_user_name_for_key(self) -> str:
        """Get current user's name for SSH key naming.

        Returns a sanitized username

        Raises:
            SSHKeyError: If unable to fetch or sanitize username
        """
        try:
            username = get_sanitized_username_from_api(self._api)
            return username[:10]
        except Exception as e:
            raise SSHKeyError("Could not fetch current user info for SSH key naming") from e

    def _looks_like_file_path(self, key_ref: str) -> bool:
        """Check if key_ref looks like a file path pattern."""
        # Common file path indicators
        path_indicators = [
            "/",  # Unix path separator
            "\\",  # Windows path separator
            "~",  # Home directory
            "./",  # Current directory
            "../",  # Parent directory
            ".pub",  # SSH public key extension
        ]

        # Common SSH key file name patterns
        ssh_key_patterns = [
            "id_rsa",
            "id_dsa",
            "id_ecdsa",
            "id_ed25519",
            "ssh_host_",
            "authorized_keys",
            "known_hosts",
        ]

        key_ref_lower = key_ref.lower()

        # Check for path indicators
        if any(indicator in key_ref for indicator in path_indicators):
            return True

        # Check for SSH key name patterns
        if any(pattern in key_ref_lower for pattern in ssh_key_patterns):
            return True

        # Check if it starts with common path prefixes
        return key_ref.startswith(("~", "/", "./", "../"))
