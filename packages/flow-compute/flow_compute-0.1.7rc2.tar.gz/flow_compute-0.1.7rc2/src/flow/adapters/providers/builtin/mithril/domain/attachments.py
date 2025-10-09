"""Volume attachment planner service.

Resolves provided identifiers (IDs or names) to volume IDs and builds
attachment specifications for the bid payload using mount paths from config or
defaults.
"""

from __future__ import annotations

from typing import Any

from flow.adapters.providers.builtin.mithril.bidding.builder import BidBuilder
from flow.sdk.models import TaskConfig
from flow.utils.paths import default_volume_mount_path


class VolumeAttachmentPlanner:
    """Plan volume attachments for bids."""

    def __init__(self, ctx: Any) -> None:
        self._ctx = ctx

    def prepare_volume_attachments(
        self, volume_ids: list[str] | None, config: TaskConfig, *, strict: bool = False
    ) -> list[dict[str, Any]]:
        """Resolve identifiers and build attachment specs.

        Args:
            volume_ids: List of volume IDs or names
            config: Task configuration (for mount_path defaults)
            strict: When True, raise on ambiguous or missing names; otherwise skip them
        """
        if not volume_ids:
            return []

        # Resolve names to IDs
        resolved: list[str] = []
        all_vols = self._safe_list_volumes()

        def _is_volume_id(identifier: str) -> bool:
            return str(identifier).startswith("vol_")

        for ident in volume_ids:
            if _is_volume_id(ident):
                resolved.append(ident)
                continue
            # Exact name match
            matches = [v for v in all_vols if getattr(v, "name", None) == ident]
            if len(matches) == 1:
                resolved.append(matches[0].id)
                continue
            if len(matches) > 1:
                if strict:
                    from flow.errors import ValidationError

                    raise ValidationError(f"Multiple volumes named '{ident}'. Use the volume ID.")
                # Skip ambiguous
                continue
            # Partial match
            partial = [
                v for v in all_vols if getattr(v, "name", "").lower().find(ident.lower()) != -1
            ]
            if len(partial) == 1:
                resolved.append(partial[0].id)
            elif strict:
                from flow.errors import ValidationError

                raise ValidationError(f"No volume found matching '{ident}'.")
            # else skip silently

        # Build attachments
        attachments: list[dict[str, Any]] = []
        cfg_vols = list(getattr(config, "volumes", []) or [])
        for i, vid in enumerate(resolved):
            if i < len(cfg_vols) and getattr(cfg_vols[i], "mount_path", None):
                mount_path = cfg_vols[i].mount_path
            else:
                name = getattr(cfg_vols[i], "name", None) if i < len(cfg_vols) else None
                mount_path = default_volume_mount_path(name=name, volume_id=vid)
            attachments.append(
                BidBuilder.format_volume_attachment(volume_id=vid, mount_path=mount_path, mode="rw")
            )
        return attachments

    def _safe_list_volumes(self):
        try:
            return self._ctx.volumes.list_volumes(
                project_id=self._ctx.get_project_id(), region=None, limit=1000
            )
        except Exception:  # noqa: BLE001
            return []
