"""Install uv on nodes by default.

This section injects the official curl-based installer for UV
    curl -LsSf https://astral.sh/uv/install.sh | sh

Behavior:
- Skips when `FLOW_SKIP_UV_INSTALL=1`.
- No-op if `uv` already exists on PATH.
- Ensures `curl` and CA certs are present using the cross-distro `install_pkgs` helper.
- Adds `$HOME/.local/bin` to PATH for the current script so `uv` is usable immediately.
- Best-effort: failures are logged but do not abort startup.
"""

from __future__ import annotations

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)


class UvInstallSection(ScriptSection):
    @property
    def name(self) -> str:
        return "uv_install"

    @property
    def priority(self) -> int:
        # Run right after header to make uv available to later sections if needed
        return 15

    def should_include(self, context: ScriptContext) -> bool:
        """Always include unless explicitly skipped by env."""
        return True

    def generate(self, context: ScriptContext) -> str:
        # Keep this inline for minimal dependencies; relies on header's install_pkgs()
        return (
            "# Install uv (best-effort)\n"
            'if [ "${FLOW_SKIP_UV_INSTALL:-0}" != "1" ]; then\n'
            "  # Ensure curl exists for the installer\n"
            "  if ! command -v curl >/dev/null 2>&1; then install_pkgs curl ca-certificates || true; fi\n"
            "  # Prefer ~/.local/bin for non-root installs; keep available in this script\n"
            '  export PATH="${HOME:-/home/ubuntu}/.local/bin:$PATH"\n'
            "  if ! command -v uv >/dev/null 2>&1; then\n"
            '    echo "Installing uv via official installer..."\n'
            '    (curl -LsSf https://astral.sh/uv/install.sh | sh) || echo "WARNING: uv installation failed (continuing)"\n'
            "  fi\n"
            "  # Source the installer-provided env to update PATH in current shell when present\n"
            '  if [ -f "${HOME:-/home/ubuntu}/.local/bin/env" ]; then . "${HOME:-/home/ubuntu}/.local/bin/env"; fi\n'
            "  # Persist PATH for future login shells (interactive/non-interactive)\n"
            "  if [ -w /etc/profile.d ] || ( command -v sudo >/dev/null 2>&1 && sudo -n test -w /etc/profile.d ); then\n"
            "    (\n"
            "      cat > /tmp/uv-path.sh <<'EOS'\n"
            "# Ensure uv is on PATH for shells; prefer official env file\n"
            'if [ -f "${HOME:-/home/ubuntu}/.local/bin/env" ]; then\n'
            '  . "${HOME:-/home/ubuntu}/.local/bin/env"\n'
            "else\n"
            '  case ":$PATH:" in *:"${HOME:-/home/ubuntu}/.local/bin:"*) ;; *) export PATH="${HOME:-/home/ubuntu}/.local/bin:$PATH" ;; esac\n'
            "fi\n"
            "EOS\n"
            "    )\n"
            "    if [ -w /etc/profile.d ]; then mv /tmp/uv-path.sh /etc/profile.d/uv.sh; chmod 0644 /etc/profile.d/uv.sh; else sudo mv /tmp/uv-path.sh /etc/profile.d/uv.sh && sudo chmod 0644 /etc/profile.d/uv.sh; fi\n"
            "  fi\n"
            "else\n"
            '  echo "Skipping uv install due to FLOW_SKIP_UV_INSTALL=1"\n'
            "fi\n"
        )


__all__ = ["UvInstallSection"]
