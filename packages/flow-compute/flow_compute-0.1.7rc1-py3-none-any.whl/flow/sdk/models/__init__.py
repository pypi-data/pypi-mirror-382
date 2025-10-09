"""Flow API models package (backwards-compatible facade).

This package provides a stable import surface compatible with
``from flow.sdk.models import ...``. During the PR-1.1 refactor, models
are being split into submodules. We re-export lightweight symbols
and lazily load the remaining symbols from a legacy module to keep
cold imports fast.

Additionally, this module re-exports IR (Intermediate Representation) models
as the canonical platform contract.
"""

from __future__ import annotations

from typing import Any  # noqa: F401 - kept for public API context

from flow.domain.ir import (
    MountSpec as IRMountSpec,
)
from flow.domain.ir import (
    ResourceSpec as IRResourceSpec,
)
from flow.domain.ir import (
    RunParams as IRRunParams,
)

# Re-export IR models as the canonical platform contract
from flow.domain.ir import (
    TaskSpec as IRTaskSpec,
)

# Avoid importing heavy pydantic symbols here to keep import light
from flow.sdk.models.config import FlowConfig, Project, ValidationResult
from flow.sdk.models.enums import (
    InstanceStatus,
    ReservationStatus,
    StorageInterface,
    TaskStatus,
)
from flow.sdk.models.hardware import (
    CPUSpec,
    GPUSpec,
    InstanceMatch,
    InstanceType,
    MemorySpec,
    NetworkSpec,
    StorageSpec,
)
from flow.sdk.models.instance import AvailableInstance, Instance
from flow.sdk.models.requests import (
    ListTasksRequest,
    ListTasksResponse,
    SubmitTaskRequest,
    SubmitTaskResponse,
)
from flow.sdk.models.reservations import Reservation, ReservationSpec
from flow.sdk.models.retry import Retries
from flow.sdk.models.task import Task
from flow.sdk.models.task_config import TaskConfig
from flow.sdk.models.users import User
from flow.sdk.models.volume import MountSpec, VolumeSpec
from flow.sdk.models.volume import Volume as VolumeModel

# All public symbols are re-exported above; no legacy fallback remains.
__all__ = (
    "AvailableInstance",
    "CPUSpec",
    "FlowConfig",
    "GPUSpec",
    "IRMountSpec",
    "IRResourceSpec",
    "IRRunParams",
    # IR models (canonical platform contract)
    "IRTaskSpec",
    "Instance",
    "InstanceMatch",
    "InstanceStatus",
    "InstanceType",
    "ListTasksRequest",
    "ListTasksResponse",
    "MemorySpec",
    "MountSpec",
    "NetworkSpec",
    "Project",
    "Reservation",
    "ReservationSpec",
    "ReservationStatus",
    "Resources",
    "Retries",
    "RunParams",
    "StorageInterface",
    "StorageSpec",
    "SubmitTaskRequest",
    "SubmitTaskResponse",
    "Task",
    "TaskConfig",
    # Backwards-compat synonyms
    "TaskSpec",
    # SDK models
    "TaskStatus",
    "User",
    "ValidationResult",
    "Volume",  # backward-compat alias for volume entities if needed by callers
    "VolumeSpec",
)


class Volume(VolumeModel):
    """Backwards-compatible alias to the canonical Volume model.

    Kept for import stability of the legacy Volume class while delegating to
    the real implementation in the volume module, which supports
    both persistent volumes and bind mounts (local/remote/read_only).
    """

    pass


# Backwards-compatible type aliases to IR models
TaskSpec = IRTaskSpec
Resources = IRResourceSpec
RunParams = IRRunParams


# __all__ is defined above to enumerate public symbols
