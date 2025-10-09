"""Storage facet - handles volume and file transfer operations."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from flow.adapters.providers.builtin.mithril.api.handlers import handle_mithril_errors
from flow.adapters.providers.builtin.mithril.api.types import StorageType
from flow.adapters.providers.builtin.mithril.core.constants import DEFAULT_REGION, VOLUME_ID_PREFIX
from flow.sdk.models import TaskConfig, Volume

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext

logger = logging.getLogger(__name__)


class StorageFacet:
    """Handles storage operations - volumes and file transfers."""

    def __init__(self, ctx: MithrilContext) -> None:
        """Initialize storage facet.

        Args:
            ctx: Mithril context with all dependencies
        """
        self.ctx = ctx

    # ========== Region Operations ==========

    def get_regions_with_storage_type(
        self, storage_type: str | StorageType
    ) -> list[dict[str, Any]]:
        """Get regions that support a specific storage type.

        Args:
            storage_type: Storage type to filter by (StorageType.BLOCK or StorageType.FILE, or string)

        Returns:
            List of region dictionaries with name and supported storage_types

        Raises:
            ValueError: If region data is malformed or cannot be parsed
            RuntimeError: If API call fails
        """
        from flow.adapters.providers.builtin.mithril.api.types import RegionModel, StorageType

        # Normalize to StorageType enum
        if isinstance(storage_type, str):
            storage_type = StorageType(storage_type.lower())

        try:
            response = self.ctx.api.list_regions()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch regions from API: {e}") from e

        data = response.get("data", []) if isinstance(response, dict) else response

        if not isinstance(data, list):
            raise TypeError(f"Expected list of regions, got {type(data).__name__}")

        regions = []
        for idx, region_data in enumerate(data):
            if not isinstance(region_data, dict):
                raise TypeError(
                    f"Region at index {idx} is not a dict: {type(region_data).__name__}"
                )

            if not region_data.get("name"):
                raise ValueError(
                    f"Region at index {idx} missing required 'name' field: {region_data}"
                )

            try:
                region = RegionModel(**region_data)
            except Exception as e:
                raise ValueError(f"Failed to parse region '{region_data.get('name')}': {e}") from e

            # Filter by storage type (intentional filtering, not an error)
            if not region.supports_storage_type(storage_type):
                continue

            regions.append(
                {
                    "name": region.name,
                    "storage_types": region.supported_storage_types,
                }
            )

        if not regions:
            raise LookupError(f"No regions support storage type '{storage_type.value}'")

        return regions

    def get_available_regions(self, storage_type: str | StorageType) -> list[str]:
        """Get available regions for the specified storage type.

        Args:
            storage_type: Storage type to filter by (StorageType.BLOCK or StorageType.FILE, or string)

        Returns:
            List of region names
        """
        regions = self.get_regions_with_storage_type(storage_type)
        return [region["name"] for region in regions]

    def get_storage_types_for_region(self, region: str) -> list[str]:
        """Get available storage types for a specific region.

        Args:
            region: Region name

        Returns:
            List of storage type strings ("block" and/or "file")
        """
        from flow.adapters.providers.builtin.mithril.api.types import RegionModel

        try:
            response = self.ctx.api.list_regions()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch regions from API: {e}") from e

        data = response.get("data", []) if isinstance(response, dict) else response

        if not isinstance(data, list):
            raise TypeError(f"Expected list of regions, got {type(data).__name__}")

        for region_data in data:
            if region_data.get("name") == region:
                region_model = RegionModel(**region_data)
                return [st.value for st in region_model.supported_storage_types]

        # Region not found, return empty list
        return []

    # ========== Volume Operations ==========

    @handle_mithril_errors("Create volume")
    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: str | StorageType = "block",
        region: str | None = None,
    ) -> Volume:
        """Create a new volume.

        Args:
            size_gb: Size of volume in GB
            name: Optional volume name
            interface: Volume interface type (StorageType.BLOCK, StorageType.FILE, or string "block"/"file")
            region: Region to create volume in

        Returns:
            Created volume
        """
        # Normalize interface to string for API call
        if isinstance(interface, StorageType):
            interface = interface.value
        return self.ctx.volumes.create_volume(
            project_id=self.ctx.get_project_id(),
            size_gb=size_gb,
            name=name,
            interface=interface,
            region=region or self.ctx.mithril_config.region or DEFAULT_REGION,
        )

    def list_regions_for_storage_type(self, storage_type: str) -> list[str]:
        """List regions that support a specific storage type.

        Args:
            storage_type: Storage type ("block" or "file")

        Returns:
            List of region names that support the storage type
        """
        return self.get_available_regions(storage_type)

    def delete_volume(self, volume_id: str) -> bool:
        """Delete a volume.

        Args:
            volume_id: Volume ID to delete

        Returns:
            True if deletion successful

        Raises:
            RuntimeError: If volume deletion fails
        """
        try:
            return self.ctx.volumes.delete_volume(volume_id)
        except Exception as e:
            raise RuntimeError(f"Failed to delete volume {volume_id}: {e}") from e

    def list_volumes(self, limit: int = 100) -> list[Volume]:
        """List volumes in the project.

        Args:
            limit: Maximum number of volumes to return

        Returns:
            List of volumes
        """
        return self.ctx.volumes.list_volumes(
            project_id=self.ctx.get_project_id(), region=None, limit=limit
        )

    def mount_volume(self, task_id: str, volume_id: str, mount_path: str = "/mnt/volume") -> bool:
        """Mount a volume to a running task.

        Args:
            task_id: Task to mount volume to
            volume_id: Volume to mount
            mount_path: Path to mount volume at

        Returns:
            True if mount successful

        Raises:
            RuntimeError: If volume mounting fails
        """
        try:
            # VolumeAttachService API uses (volume_identifier, task_id, mount_point)
            self.ctx.volume_attach.mount_volume(
                volume_identifier=volume_id, task_id=task_id, mount_point=mount_path
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to mount volume {volume_id} to task {task_id}: {e}") from e

    def is_volume_id(self, identifier: str) -> bool:
        """Check if a string is a volume ID.

        Args:
            identifier: String to check

        Returns:
            True if identifier is a volume ID
        """
        return identifier.startswith(VOLUME_ID_PREFIX)

    def prepare_volume_attachments(
        self, volume_ids: list[str] | None, config: TaskConfig
    ) -> list[dict[str, Any]]:
        """Prepare volume attachment specifications using shared planner."""
        from flow.adapters.providers.builtin.mithril.domain.attachments import (
            VolumeAttachmentPlanner,
        )

        planner = VolumeAttachmentPlanner(self.ctx)
        return planner.prepare_volume_attachments(volume_ids, config, strict=True)

    # ========== File Transfer Operations ==========

    def upload_file(self, task_id: str, local_path: Path, remote_path: str = "~") -> bool:
        """Upload a file to a task.

        Args:
            task_id: Task to upload to
            local_path: Local file path
            remote_path: Remote destination path

        Returns:
            True if upload successful
        """
        try:
            import os as _os

            from flow.adapters.transport.code_transfer import (
                CodeTransferConfig,
                CodeTransferManager,
            )

            task = self.ctx.task_service.get_task(task_id)
            # Determine target directory from remote path
            target_dir = remote_path
            try:
                if remote_path and not remote_path.endswith("/"):
                    target_dir = _os.path.dirname(remote_path) or "~"
            except Exception:  # noqa: BLE001
                target_dir = "~"

            cfg = CodeTransferConfig(source_dir=local_path.parent, target_dir=target_dir)
            CodeTransferManager(provider=self.ctx).transfer_code_to_task(task, cfg)
            return True
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to upload file to task {task_id}: {e}")
            return False

    def download_file(self, task_id: str, remote_path: str, local_path: Path) -> bool:
        """Download a file from a task.

        Args:
            task_id: Task to download from
            remote_path: Remote file path
            local_path: Local destination path

        Returns:
            True if download successful
        """
        try:
            # Not yet implemented via shared transport layer
            logger.error("Download of single files is not supported by the current transport")
            return False
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to download file from task {task_id}: {e}")
            return False

    def upload_directory(
        self,
        task_id: str,
        local_dir: Path,
        remote_dir: str = "~",
        exclude_patterns: list[str] | None = None,
    ) -> bool:
        """Upload a directory to a task.

        Args:
            task_id: Task to upload to
            local_dir: Local directory path
            remote_dir: Remote destination directory
            exclude_patterns: Patterns to exclude from upload

        Returns:
            True if upload successful
        """
        try:
            from flow.adapters.transport.code_transfer import (
                CodeTransferConfig,
                CodeTransferManager,
            )

            task = self.ctx.task_service.get_task(task_id)
            cfg = CodeTransferConfig(source_dir=local_dir, target_dir=remote_dir)
            CodeTransferManager(provider=self.ctx).transfer_code_to_task(task, cfg)
            return True
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to upload directory to task {task_id}: {e}")
            return False

    def download_directory(
        self,
        task_id: str,
        remote_dir: str,
        local_dir: Path,
        exclude_patterns: list[str] | None = None,
    ) -> bool:
        """Download a directory from a task.

        Args:
            task_id: Task to download from
            remote_dir: Remote directory path
            local_dir: Local destination directory
            exclude_patterns: Patterns to exclude from download

        Returns:
            True if download successful
        """
        try:
            # Not yet implemented via shared transport layer
            logger.error("Download of directories is not supported by the current transport")
            return False
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to download directory from task {task_id}: {e}")
            return False
