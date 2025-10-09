"""Manages the lifecycle of development VMs for the flow dev command."""

import hashlib
import logging
import os
import time
from enum import Enum

from flow.application.config.manager import ConfigManager
from flow.errors import FlowOperationError
from flow.sdk.client import Flow, TaskConfig
from flow.sdk.models import Task, TaskStatus

logger = logging.getLogger(__name__)


class VMStopStatus(Enum):
    """Status of VM stop operation."""

    PAUSED = "paused"
    ALREADY_PAUSED = "already_paused"
    TERMINAL = "terminal"
    NOT_FOUND = "not_found"


class DevVMManager:
    """Manages the lifecycle of development VMs."""

    def __init__(self, flow_client: Flow):
        """Initialize VM manager.

        Args:
            flow_client: Flow SDK client instance
        """
        self.flow_client = flow_client
        self.dev_vm_prefix = "flow-dev"

    def get_dev_vm_name(self, force_unique: bool = False) -> str:
        """Generate consistent dev VM name for current user.

        Args:
            force_unique: If True, append a unique suffix to ensure uniqueness

        Returns:
            Unique dev VM name based on username
        """
        from flow.cli.utils.name_generator import generate_unique_name

        user = os.environ.get("USER", "default")
        # Create a short hash to ensure uniqueness
        name_hash = hashlib.md5(f"{user}-dev".encode()).hexdigest()[:6]
        base_name = f"dev-{name_hash}"

        # Use shared utility for consistent unique name generation
        if force_unique:
            vm_name = generate_unique_name(prefix="dev", base_name=base_name, add_unique=True)
        else:
            vm_name = base_name

        logger.debug(f"Generated dev VM name: {vm_name} for user: {user}")
        return vm_name

    def find_dev_vm(
        self,
        include_not_ready: bool = False,
        region: str | None = None,
        desired_instance_type: str | None = None,
    ):
        """Find existing dev VM for the current user.

        First checks if there's a saved dev_task_id in config. If that task is still
        active (not terminated), it will be returned. Otherwise, falls back to searching
        by name prefix.

        Args:
            include_not_ready: When True, also consider VMs that are still provisioning
                (no SSH access yet) if they match other filters.
            region: Optional region to constrain the search.
            desired_instance_type: Optional instance type (case-insensitive). When set,
                only VMs whose ``instance_type`` exactly matches are eligible for reuse.

        Returns:
            The most recent matching Task if found; otherwise ``None``.
        """
        # First, check if we have a saved dev task_id
        config_mgr = ConfigManager()
        dev_task_id = config_mgr.get_dev_task_id()

        if dev_task_id:
            task = self.flow_client.get_task(dev_task_id)
            # Check if task is still active (not terminated)
            if not task.is_terminal:
                # Apply the same filters as below
                if region and task.region != region:
                    logger.debug(
                        f"Saved dev VM {dev_task_id} is in wrong region: {task.region} != {region}"
                    )
                elif desired_instance_type:
                    if task.instance_type != desired_instance_type:
                        logger.debug(
                            f"Saved dev VM {dev_task_id} has wrong instance type: "
                            f"{task.instance_type} != {desired_instance_type}"
                        )
                    else:
                        logger.info(f"Using saved dev VM: {task.name} (ID: {task.task_id})")
                        return task
                else:
                    logger.info(f"Using saved dev VM: {task.name} (ID: {task.task_id})")
                    return task
            else:
                logger.debug(f"Saved dev VM {dev_task_id} is terminated")

        # Build the expected dev VM prefix for this user
        user = os.environ.get("USER", "default")
        # The prefix matches our new naming pattern
        name_hash = hashlib.md5(f"{user}-dev".encode()).hexdigest()[:6]
        vm_prefix = f"dev-{name_hash}"

        # Also check for legacy naming pattern
        legacy_prefix = f"flow-dev-{user}"

        # Discover tasks (include provisioning if requested)
        logger.debug(f"Searching for existing dev VM with prefix: {vm_prefix} or {legacy_prefix}")
        if include_not_ready:
            tasks = self.flow_client.tasks.list()
        else:
            tasks = self.flow_client.tasks.list(status=TaskStatus.RUNNING)

        logger.debug(f"Found {len(tasks)} tasks to inspect")

        # Find all tasks that match our dev VM naming patterns (old and new)
        # Since we can't reliably check config.env (it's not returned by list_tasks),
        # we rely on the naming convention which is unique per user
        dev_vm_candidates = []
        not_ready_vms = []

        # Normalize desired instance type for comparison (case-insensitive)
        desired_type_norm = desired_instance_type.lower().strip() if desired_instance_type else None

        for task in tasks:
            # Check both new and legacy naming patterns
            if task.name.startswith(vm_prefix) or task.name.startswith(legacy_prefix):
                # Filter by region when specified
                try:
                    if region and getattr(task, "region", None) and task.region != region:
                        continue
                except Exception:  # noqa: BLE001
                    # If region not present on task, don't filter it out
                    pass
                # If a specific instance type was requested, skip mismatches
                if desired_type_norm is not None:
                    try:
                        task_type_norm = (
                            (getattr(task, "instance_type", None) or "").lower().strip()
                        )
                        if task_type_norm != desired_type_norm:
                            continue
                    except Exception:  # noqa: BLE001
                        # If instance_type is unavailable on task, be conservative and skip
                        continue

                if task.is_terminal:
                    continue

                logger.debug(f"Found potential dev VM: {task.name} (ID: {task.task_id})")
                # Separate ready and not-ready VMs
                if task.ssh_host:
                    dev_vm_candidates.append(task)
                    logger.debug(f"  - Has SSH access: {task.ssh_host}:{task.ssh_port}")
                else:
                    # Include any non-terminal VM without SSH (provisioning, paused, etc.)
                    not_ready_vms.append(task)
                    logger.debug(f"  - No SSH access yet (status: {task.status})")

        # If we only have not-ready VMs and include_not_ready is True, return the newest
        if include_not_ready and not dev_vm_candidates and not_ready_vms:
            not_ready_vms.sort(key=lambda t: t.created_at, reverse=True)
            logger.info(f"Found {len(not_ready_vms)} dev VM(s) still provisioning")
            return not_ready_vms[0]

        if not dev_vm_candidates:
            logger.debug("No ready dev VMs found")
            return None

        # If we have multiple dev VMs, use the most recent one
        if len(dev_vm_candidates) > 1:
            logger.info(f"Found {len(dev_vm_candidates)} ready dev VMs - selecting most recent")
            # Sort by created_at timestamp (newest first)
            dev_vm_candidates.sort(key=lambda t: t.created_at, reverse=True)

        selected_vm = dev_vm_candidates[0]
        logger.info(f"Using existing dev VM: {selected_vm.name} (ID: {selected_vm.task_id})")
        return selected_vm

    def create_dev_vm(
        self,
        instance_type: str | None = None,
        region: str | None = None,
        ssh_keys: list | None = None,
        max_price_per_hour: float | None = None,
        no_unique: bool = False,
        image: str | None = None,
        volume: object | None = None,
    ) -> Task:
        """Create a new dev VM.

        Args:
            instance_type: GPU/CPU instance type
            region: Region for the VM
            ssh_keys: SSH keys for access
            max_price_per_hour: Maximum hourly price in USD
            no_unique: If True, don't add unique suffix on name conflict
            image: Docker image to use
            volume: Optional volume to attach to the VM

        Returns:
            Task object for the new VM

        Notes:
            If a name conflict occurs and an existing dev VM has a different
            ``instance_type`` than requested, this method will by default create a
            uniquely named dev VM (preserving the existing one). If ``no_unique`` is
            True in that scenario, a ``RuntimeError`` is raised so callers can choose
            to stop the old VM (e.g., via ``--force-new``) or retry without
            ``--no-unique``.
        """
        # First try with consistent name
        vm_name = self.get_dev_vm_name()

        # Default instance type for dev
        if not instance_type:
            instance_type = os.environ.get("FLOW_DEV_INSTANCE_TYPE", "h100")

        # Create VM configuration
        # For dev VMs, we use a startup script that prepares the environment
        # Note: Since TaskConfig doesn't support Docker socket mounts or privileged mode,
        # the dev VM runs containers directly on the host VM, not nested inside another container
        dev_startup_script = """#!/bin/bash
set -e

# Ensure a sane TMPDIR (some images set it to non-existent paths)
export TMPDIR="${TMPDIR:-/tmp}"
if [ ! -d "$TMPDIR" ]; then
  mkdir -p "$TMPDIR" && chmod 1777 "$TMPDIR" || true
fi

# Install essential dev tools
apt-get update -qq
apt-get install -y -qq git vim htop curl wget python3-pip ca-certificates

# Install uv for the interactive user and persist PATH
if id ubuntu >/dev/null 2>&1; then
  # Install as the ubuntu user so it's in their home
  su -l ubuntu -c 'export PATH="$HOME/.local/bin:$PATH"; \
    if ! command -v uv >/dev/null 2>&1; then \
      echo "Installing uv via official installer..."; \
      (curl -LsSf https://astral.sh/uv/install.sh | sh) || echo "WARNING: uv installation failed (continuing)"; \
    fi; \
    if [ -f "$HOME/.local/bin/env" ]; then . "$HOME/.local/bin/env"; fi'
  # Make uv/uvx discoverable in non-login shells
  if [ -x /home/ubuntu/.local/bin/uv ]; then ln -sf /home/ubuntu/.local/bin/uv /usr/local/bin/uv || true; fi
  if [ -x /home/ubuntu/.local/bin/uvx ]; then ln -sf /home/ubuntu/.local/bin/uvx /usr/local/bin/uvx || true; fi
else
  # Fallback: install for the current user (often root)
  export PATH="$HOME/.local/bin:$PATH"
  if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv via official installer..."
    (curl -LsSf https://astral.sh/uv/install.sh | sh) || echo "WARNING: uv installation failed (continuing)"
  fi
  if [ -f "$HOME/.local/bin/env" ]; then . "$HOME/.local/bin/env"; fi
fi

# Persist PATH and sourcing behavior for all shells
cat >/etc/profile.d/uv.sh <<'EOS'
# Ensure uv is on PATH for shells; prefer official env file
if [ -f "$HOME/.local/bin/env" ]; then
  . "$HOME/.local/bin/env"
else
  case ":$PATH:" in *:"$HOME/.local/bin":*) ;; *) export PATH="$HOME/.local/bin:$PATH" ;; esac
fi
EOS
chmod 0644 /etc/profile.d/uv.sh

# Install Docker in a more robust way
if ! command -v docker >/dev/null 2>&1; then
    echo "Installing Docker..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get install -y -qq docker.io || true
    elif command -v yum >/dev/null 2>&1; then
        yum install -y docker || true
        systemctl enable docker || true
        systemctl start docker || true
    fi
fi

# Ensure standard dev directories exist and are writable
mkdir -p /workspace /envs || true
# Prefer a common non-root user when present; otherwise, make writable to all
if id ubuntu >/dev/null 2>&1; then
    chown -R ubuntu:ubuntu /workspace /envs || true
fi
chmod 777 /workspace /envs || true

# Verify Docker works
docker info >/dev/null 2>&1 || echo "Docker may not be ready yet"

# Keep VM running
exec sleep infinity
"""

        config_dict = {
            "name": vm_name,
            "unique_name": False,  # We handle uniqueness ourselves with get_dev_vm_name
            "instance_type": instance_type,
            # Use Docker image to trigger DockerSection which handles dev VM setup
            "image": image or os.environ.get("FLOW_DEV_IMAGE", "ubuntu:22.04"),
            "command": ["bash", "-c", dev_startup_script],
            # Dev VMs sync code via the CLI (rsync); do not inline or provider-upload code here.
            "upload_code": False,
            "upload_strategy": "none",
            # Prefer typed hint over env for dev VM semantics (env still set for compatibility)
            "dev_vm": True,
            "env": {
                "FLOW_DEV_VM": "true",
                "FLOW_DEV_USER": os.environ.get("USER", "default"),
                "DEBIAN_FRONTEND": "noninteractive",
            },
            "ssh_keys": ssh_keys or [],
            "priority": "high",  # High priority for dev VMs
        }

        # Respect explicit region preference when provided
        if region is not None:
            config_dict["region"] = region

        # Add max_price_per_hour if specified
        if max_price_per_hour is not None:
            config_dict["max_price_per_hour"] = max_price_per_hour

        # Add volume if specified
        if volume is not None:
            # Extract volume_id from the volume object
            volume_id = getattr(volume, "volume_id", None)
            if volume_id:
                # Create a VolumeSpec dict to attach the existing volume
                # VolumeSpec will auto-generate a mount_path if not specified
                config_dict["volumes"] = [{"volume_id": volume_id}]

        config = TaskConfig(**config_dict)

        # Submit task
        logger.info(f"Creating dev VM with instance type: {instance_type}")
        try:
            return self.flow_client.run(config)
        except Exception as e:
            # Check if it's a name conflict - providers should raise NameConflictError
            # but also handle legacy string matching for backward compatibility
            error_msg = str(e)
            if "Name already used" in error_msg or "already exists" in error_msg.lower():
                # If a dev VM exists but with a different instance type than requested,
                # don't silently reuse it. Either error (when --no-unique) or create a uniquely named VM.
                logger.info("Dev VM name already in use; inspecting existing VM shape")
                existing_any = self.find_dev_vm(include_not_ready=True)
                try:
                    existing_type = (
                        getattr(existing_any, "instance_type", None) if existing_any else None
                    )
                except Exception:  # noqa: BLE001
                    existing_type = None

                requested_type_norm = (instance_type or "").lower().strip()
                existing_type_norm = (existing_type or "").lower().strip()

                if (
                    requested_type_norm
                    and existing_type_norm
                    and requested_type_norm != existing_type_norm
                ):
                    if no_unique:
                        # Surface a clear error so the caller can decide to --force-new
                        raise RuntimeError(
                            "A dev VM with a different instance type already exists. "
                            f"Existing: '{existing_type}', requested: '{instance_type}'. "
                            "Use --force-new to stop the old VM, or omit --no-unique to create an additional dev VM."
                        )
                    logger.info(
                        "Existing dev VM has mismatched instance type; creating a uniquely named dev VM"
                    )
                    vm_name = self.get_dev_vm_name(force_unique=True)
                    config.name = vm_name
                    return self.flow_client.run(config)

                # Prefer attaching to the existing dev VM rather than creating a new uniquely named one
                logger.info("Dev VM name already in use; attempting to use the existing VM")
                existing = self.find_dev_vm(
                    include_not_ready=True, desired_instance_type=instance_type
                )
                if existing:
                    return existing
                # Briefly wait and retry once to account for eventual consistency
                time.sleep(2)
                existing = self.find_dev_vm(
                    include_not_ready=True, desired_instance_type=instance_type
                )
                if existing:
                    return existing
                if no_unique:
                    # User explicitly doesn't want a uniquely-suffixed name
                    raise
                # As a last resort, generate a unique suffix to avoid blocking the user
                logger.info("Existing VM not discoverable; generating unique dev VM name")
                vm_name = self.get_dev_vm_name(force_unique=True)
                config.name = vm_name
                return self.flow_client.run(config)
            else:
                # Re-raise other errors
                raise

    def unpause_task(self, task_id: str) -> None:
        """Unpause a task by calling the provider's unpause method.

        Args:
            task_id: Task ID to unpause

        Raises:
            Exception: If unpause fails
        """
        try:
            provider = self.flow_client.provider
            success = provider.unpause_task(task_id)
            if success:
                logger.info(f"Successfully unpaused task {task_id}")
            else:
                raise FlowOperationError(
                    operation="unpause task",
                    resource_id=task_id,
                    cause=RuntimeError("Unpause operation returned False"),
                )
        except FlowOperationError:
            raise
        except Exception as e:
            logger.error(f"Failed to unpause task {task_id}: {e}")
            raise FlowOperationError(
                operation="unpause task",
                resource_id=task_id,
                cause=e,
            ) from e

    def stop_dev_vm(self) -> VMStopStatus:
        """Pause the current user's dev VM.

        Always pauses the VM (preserving state) unless it's already paused or terminated.
        This works for running, pending, and provisioning VMs.

        Returns:
            VMStopStatus: Status indicating what happened
        """
        # Look for any active dev VM (including not-ready states)
        vm = self.find_dev_vm(include_not_ready=True)
        if vm:
            # Skip if already paused
            if vm.status == TaskStatus.PAUSED:
                logger.info(f"Dev VM {vm.task_id} is already paused")
                return VMStopStatus.ALREADY_PAUSED

            # Skip if in terminal state
            if vm.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                logger.info(f"Dev VM {vm.task_id} is in terminal state: {vm.status}")
                return VMStopStatus.TERMINAL

            # Pause the VM regardless of state (running, pending, provisioning, etc.)
            try:
                self._pause_task(vm.task_id)
                logger.info(f"Paused dev VM {vm.task_id}")
                return VMStopStatus.PAUSED
            except Exception as e:
                logger.warning(f"Could not pause dev VM: {e}")
                # Don't fall back to cancel - just report failure
                raise
        return VMStopStatus.NOT_FOUND

    def _pause_task(self, task_id: str) -> None:
        """Pause a task by calling the provider's pause method.

        Args:
            task_id: Task ID to pause

        Raises:
            Exception: If pause fails
        """
        try:
            provider = self.flow_client.provider
            success = provider.pause_task(task_id)
            if success:
                logger.info(f"Successfully paused task {task_id}")
            else:
                raise FlowOperationError(
                    operation="pause task",
                    resource_id=task_id,
                    cause=RuntimeError("Pause operation returned False"),
                )
        except FlowOperationError:
            raise
        except Exception as e:
            logger.error(f"Failed to pause task {task_id}: {e}")
            raise FlowOperationError(
                operation="pause task",
                resource_id=task_id,
                cause=e,
            ) from e
