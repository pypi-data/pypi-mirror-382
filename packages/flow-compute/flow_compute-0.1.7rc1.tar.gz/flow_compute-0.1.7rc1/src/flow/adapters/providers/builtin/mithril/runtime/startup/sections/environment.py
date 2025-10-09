from __future__ import annotations

import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)


class EnvironmentSection(ScriptSection):
    name = "environment"
    priority = 20

    def should_include(self, context: ScriptContext) -> bool:
        # Only include if there are environment variables to export
        return bool(context.environment)

    def generate(self, context: ScriptContext) -> str:
        if not context.environment:
            return ""

        exports = []
        for key, value in context.environment.items():
            # Validate environment variable names
            if not key.replace("_", "").replace("-", "").isalnum():
                raise ValueError(f"Invalid environment variable name: {key}")
            # Safe shell quoting
            safe_value = str(value).replace("'", "'\"'\"'")
            exports.append(f"export {key}='{safe_value}'")

        if not exports:
            return ""

        exports_joined = "\n".join(exports)
        return textwrap.dedent(
            f"""
            # Export environment variables
            {exports_joined}
            echo "Exported {len(exports)} environment variables"
        """
        ).strip()

    def validate(self, context: ScriptContext) -> list[str]:
        errors = []
        if not context.environment:
            return errors

        for key, value in context.environment.items():
            if not key.replace("_", "").replace("-", "").isalnum():
                errors.append(f"Invalid environment variable name: {key}")
            if len(str(value)) > 32 * 1024:  # 32KB limit
                errors.append(f"Environment variable {key} value too large")

        return errors
