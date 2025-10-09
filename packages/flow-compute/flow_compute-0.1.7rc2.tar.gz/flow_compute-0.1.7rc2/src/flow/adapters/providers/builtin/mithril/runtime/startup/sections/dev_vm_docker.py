from __future__ import annotations

import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.utils import ensure_docker_available


class DevVMDockerSection(ScriptSection):
    @property
    def name(self) -> str:
        return "dev_vm_docker"

    @property
    def priority(self) -> int:
        return 38

    def should_include(self, context: ScriptContext) -> bool:
        env = getattr(context, "environment", None)
        if not isinstance(env, dict):
            env = (
                getattr(context, "env_vars", {})
                if isinstance(getattr(context, "env_vars", None), dict)
                else {}
            )
        # Prefer typed hint; fall back to env var for backward compatibility
        hint = getattr(context, "dev_vm", None)
        is_dev_vm = bool(hint) if hint is not None else (env.get("FLOW_DEV_VM") == "true")
        # Accept optional test-only is_dev_vm flag
        is_dev_vm_flag = bool(getattr(context, "is_dev_vm", False))
        has_image = bool(getattr(context, "docker_image", None))
        return has_image and (is_dev_vm or is_dev_vm_flag)

    def generate(self, context: ScriptContext) -> str:
        return textwrap.dedent(
            f"""
            echo "Ensuring Docker is available on host for dev VM"
            {ensure_docker_available()}
            mkdir -p /home/persistent
            chmod 755 /home/persistent
            echo "Docker and persistent storage ready for dev VM"
        """
        ).strip()


__all__ = ["DevVMDockerSection"]
