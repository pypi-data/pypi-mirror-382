"""Mithril resource management.

This package manages Mithril resources:
- GPU specifications and capabilities
- Project name to ID resolution
- SSH key management
"""

from flow.adapters.providers.builtin.mithril.resources.gpu import GPU_SPECS, get_default_gpu_memory
from flow.adapters.providers.builtin.mithril.resources.projects import (
    ProjectNotFoundError,
    ProjectResolver,
)
from flow.adapters.providers.builtin.mithril.resources.ssh import (
    SSHKeyManager,
    SSHKeyNotFoundError,
)

__all__ = [
    # GPU
    "GPU_SPECS",
    "ProjectNotFoundError",
    # Projects
    "ProjectResolver",
    # SSH
    "SSHKeyManager",
    "SSHKeyNotFoundError",
    "get_default_gpu_memory",
]
