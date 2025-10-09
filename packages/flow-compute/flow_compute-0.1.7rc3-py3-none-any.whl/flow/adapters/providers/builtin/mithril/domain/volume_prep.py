"""Volume preparation service.

Resolves/creates volumes declared in TaskConfig and returns updated specs and
resolved IDs. Centralizes logic used by submission/storage flows to keep them
thin and DRY, and to enable consistent validation behavior.
"""

from __future__ import annotations

from typing import Any

from flow.sdk.models import TaskConfig


class VolumePreparationService:
    """Resolves and ensures volumes exist before bidding.

    Responsibilities:
    - Resolve by ID or name (exact match in region)
    - Create when unresolved, using unique suffix on name conflicts
    - Return updated TaskConfig volume specs and list of resolved IDs
    """

    def __init__(self, ctx: Any) -> None:
        self._ctx = ctx

    def resolve_and_ensure_volumes(
        self, config: TaskConfig, *, region: str, project_id: str
    ) -> tuple[list[Any], list[str]]:
        """Resolve or create volumes declared in the config.

        Args:
            config: TaskConfig containing `volumes` specs
            region: Target region for volumes
            project_id: Project identifier

        Returns:
            (updated_volume_specs, resolved_volume_ids)
        """
        resolved_ids: list[str] = []
        updated_specs = list(getattr(config, "volumes", []) or [])

        if not updated_specs:
            return updated_specs, resolved_ids

        # Best-effort cache of existing volumes for name resolution
        try:
            existing = self._ctx.volumes.list_volumes(
                project_id=project_id, region=region, limit=1000
            )
        except Exception:  # noqa: BLE001
            existing = []

        for i, spec in enumerate(list(updated_specs)):
            try:
                vol_id = getattr(spec, "volume_id", None) or getattr(spec, "id", None)
                vol_name = getattr(spec, "name", None)
                iface_obj = getattr(spec, "interface", None)
                iface = (
                    (getattr(iface_obj, "value", None) if iface_obj is not None else None)
                    or (str(iface_obj).lower() if iface_obj else None)
                    or "block"
                )
                size_gb = int(getattr(spec, "size_gb", 1) or 1)

                # Try resolve by exact name in selected region
                name_conflict = False
                if not vol_id and vol_name and existing:
                    matches = [v for v in existing if getattr(v, "name", None) == vol_name]
                    if len(matches) == 1:
                        vol_id = matches[0].id
                    elif len(matches) > 1:
                        name_conflict = True

                # Create when unresolved
                created = None
                if not vol_id:
                    final_name = vol_name
                    try:
                        if vol_name:
                            conflict_exists = name_conflict or any(
                                getattr(v, "name", None) == vol_name for v in existing
                            )
                            if conflict_exists:
                                import uuid as _uuid

                                suffix = _uuid.uuid4().hex[:6]
                                final_name = f"{vol_name}-{suffix}"
                    except Exception:  # noqa: BLE001
                        final_name = vol_name

                    created = self._ctx.volumes.create_volume(
                        project_id=project_id,
                        size_gb=size_gb,
                        name=final_name,
                        interface=("file" if str(iface).lower() == "file" else "block"),
                        region=region,
                    )
                    vol_id = getattr(created, "volume_id", None) or getattr(created, "id", None)

                if vol_id:
                    # Update spec with resolved id and final name (if created)
                    updates = {"volume_id": vol_id}
                    try:
                        if created and getattr(created, "name", None):
                            updates["name"] = created.name
                        updated_specs[i] = spec.model_copy(update=updates)
                    except Exception:  # noqa: BLE001
                        try:
                            spec.volume_id = vol_id
                            if created and getattr(created, "name", None):
                                spec.name = created.name
                            updated_specs[i] = spec
                        except Exception:  # noqa: BLE001
                            pass
                    resolved_ids.append(str(vol_id))
            except Exception:  # noqa: BLE001
                # Skip problematic entries but continue with others
                continue

        return updated_specs, resolved_ids

    def wait_until_ready(self, volume_ids: list[str], *, timeout_s: int = 60) -> None:
        """Optional: wait for volumes to report 'available'. Best-effort noop for now."""
        # Future: poll provider API until ready; keep noop here for minimal blast radius.
        return None
