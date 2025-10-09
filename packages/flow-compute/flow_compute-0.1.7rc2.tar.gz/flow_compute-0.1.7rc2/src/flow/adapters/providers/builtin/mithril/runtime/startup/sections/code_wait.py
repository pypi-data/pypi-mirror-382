from __future__ import annotations

import shlex
import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.utils.paths import WORKSPACE_DIR


class CodeWaitSection(ScriptSection):
    @property
    def name(self) -> str:
        return "code_wait"

    @property
    def priority(self) -> int:
        # Run after code_upload but before docker
        return 38

    def should_include(self, context: ScriptContext) -> bool:
        # Enabled when FLOW_WAIT_FOR_CODE=true is present in env
        env = getattr(context, "environment", {}) or {}
        return str(env.get("FLOW_WAIT_FOR_CODE", "")).lower() in {"1", "true", "yes", "on"}

    def generate(self, context: ScriptContext) -> str:
        env = getattr(context, "environment", {}) or {}
        target_dir = getattr(context, "working_directory", None) or WORKSPACE_DIR
        safe_dir = shlex.quote(str(target_dir))
        # Clamp timeout to 60..3600 seconds; default 900
        try:
            raw = int(env.get("FLOW_WAIT_FOR_CODE_TIMEOUT", 900))
            timeout = max(60, min(raw, 3600))
        except Exception:  # noqa: BLE001
            timeout = 900
        return textwrap.dedent(
            f"""
            echo "Waiting for code upload to appear at {target_dir} (up to {timeout}s)..."
            SECS=0
            until [ -f {safe_dir}/.flow-sync.json ] || [ "$SECS" -ge {timeout} ]; do
              if [ $((SECS % 10)) -eq 0 ]; then echo "[code-wait] {target_dir}/.flow-sync.json not found (t=${{SECS}}s)"; fi
              sleep 1; SECS=$((SECS+1))
            done
            if [ -f {safe_dir}/.flow-sync.json ]; then
              echo "Code upload detected at {target_dir} (t=${{SECS}}s)"
            else
              echo "[WARN] Code upload not detected after {timeout}s; continuing without blocking"
            fi
            """
        ).strip()


__all__ = ["CodeWaitSection"]
