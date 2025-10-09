"""Modular section exports.

This module re-exports section classes from the legacy `sections.py` to provide
a per-file structure while maintaining backward-compatible imports like:

    from flow.adapters.providers.builtin.mithril.runtime.startup.sections import HeaderSection

Sections are also available individually via submodules, e.g.:

    from flow.adapters.providers.builtin.mithril.runtime.startup.sections.header import HeaderSection
"""

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    IScriptSection,
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.code_upload import (
    CodeUploadSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.code_wait import (
    CodeWaitSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.completion import (
    CompletionSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.dev_vm_docker import (
    DevVMDockerSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.docker import DockerSection
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.environment import (
    EnvironmentSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.gpud_health import (
    GPUdHealthSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.header import HeaderSection
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.multinode import (
    MultinodeSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.port_forwarding import (
    PortForwardingSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.runtime_monitor import (
    RuntimeMonitorSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.s3 import S3Section
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.slurm_setup import (
    SlurmSetupSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.terminate_on_exit import (
    TerminateOnExitSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.user_script import (
    UserScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.uv import (
    UvInstallSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.volume import VolumeSection
from flow.adapters.providers.builtin.mithril.runtime.startup.sections.workload_resume import (
    WorkloadResumeSection,
)

__all__ = [
    "CodeUploadSection",
    "CodeWaitSection",
    "CompletionSection",
    "DevVMDockerSection",
    "DockerSection",
    "EnvironmentSection",
    "GPUdHealthSection",
    "HeaderSection",
    "IScriptSection",
    "MultinodeSection",
    "PortForwardingSection",
    "RuntimeMonitorSection",
    # Re-export modularized sections
    "S3Section",
    "ScriptContext",
    "ScriptSection",
    "SlurmSetupSection",
    "TerminateOnExitSection",
    "UserScriptSection",
    "UvInstallSection",
    "VolumeSection",
    "WorkloadResumeSection",
]
