"""Mithril-specific Jupyter tunnel manager with foundrypf support."""

from __future__ import annotations

from typing import Any

from flow.cli.utils.jupyter_utils import create_jupyter_tunnel


class MithrilJupyterTunnelManager:
    """Mithril-specific tunnel manager that uses foundrypf when available."""

    def create_jupyter_tunnel(
        self,
        task: Any,
        host: str,
        ssh_key_path: str,
        username: str,
        local_port: int,
        jupyter_port: int,
        token: str | None,
        no_open: bool,
    ) -> None:
        """Create SSH tunnel with Mithril-specific optimizations (foundrypf).

        This method preserves the exact functionality of the original jupyter command
        but encapsulates the Mithril-specific logic.
        """
        create_jupyter_tunnel(
            task,
            host,
            ssh_key_path,
            username,
            local_port,
            jupyter_port,
            token,
            no_open,
            raise_on_timeout=True,
        )

    def generate_jupyter_binary(self) -> str:
        """Generate the foundry-jupyter binary script content with foundrypf support.

        This preserves the original Mithril-specific foundrypf logic.
        """
        return "\n".join(
            [
                "#!/bin/bash",
                "set -euo pipefail",
                "PORT=${1:-8888}",
                'TOKEN_FILE="/etc/foundry/jupyter_token"',
                "",
                "# Ensure venv support",
                "if ! python3 -m venv --help >/dev/null 2>&1; then",
                "  apt-get update || true",
                "  apt-get install -y python3-venv || true",
                "fi",
                "",
                "mkdir -p /etc/foundry",
                'if [ ! -f "$TOKEN_FILE" ] || [ ! -s "$TOKEN_FILE" ]; then',
                '  TOKEN="$(openssl rand -hex 32)"',
                '  echo "$TOKEN" > "$TOKEN_FILE"',
                '  chmod 0644 "$TOKEN_FILE"',
                "fi",
                "RUN_USER=${SUDO_USER:-ubuntu}",
                'if ! id "$RUN_USER" >/dev/null 2>&1; then',
                "  RUN_USER=\"$(getent passwd | awk -F: '$3>=1000 && $6 ~ /^\\/home\\// {print $1; exit}')\"",
                "fi",
                'if [ -z "$RUN_USER" ]; then RUN_USER=ubuntu; fi',
                'USER_HOME="$(getent passwd "$RUN_USER" | cut -d: -f6)"',
                'VENV="$USER_HOME/.jupyter-venv"',
                'LOGFILE="$USER_HOME/jupyter.log"',
                'if [ ! -d "$VENV" ]; then',
                '  sudo -u "$RUN_USER" python3 -m venv "$VENV"',
                "fi",
                'sudo -u "$RUN_USER" bash -c "source \\"$VENV/bin/activate\\" && python -m pip show jupyterlab >/dev/null 2>&1 || python -m pip install --upgrade pip wheel jupyterlab"',
                "",
                "# Start Jupyter if not already running",
                'if ! pgrep -u "$RUN_USER" -f "jupyter.*--port[= ]$PORT" >/dev/null 2>&1; then',
                '  TOKEN=$(cat "$TOKEN_FILE")',
                '  sudo -u "$RUN_USER" bash -c "cd \\"$USER_HOME\\" && source \\"$VENV/bin/activate\\" && jupyter lab --ip=127.0.0.1 --no-browser --ServerApp.token=\\"$TOKEN\\" --port=\\"$PORT\\" --ServerApp.root_dir=\\"$USER_HOME\\" >\\"$LOGFILE\\" 2>&1 &"',
                '  chown "$RUN_USER":"$RUN_USER" "$LOGFILE" || true',
                "fi",
                "",
                "# Wait for Jupyter to be ready",
                "echo 'Waiting for Jupyter to start...'",
                "for i in {1..30}; do",
                '  if curl -s --connect-timeout 2 "http://127.0.0.1:$PORT" >/dev/null 2>&1; then',
                "    echo 'Jupyter is ready'",
                "    break",
                "  fi",
                "  sleep 1",
                "done",
                "",
                "# Keep process in foreground with reverse tunnel if available",
                "# This is the Mithril-specific foundrypf integration",
                "if command -v foundrypf >/dev/null 2>&1; then",
                '  exec foundrypf "$PORT"',
                "elif [ -x /usr/local/bin/foundrypf ]; then",
                '  exec /usr/local/bin/foundrypf "$PORT"',
                "elif [ -x /var/lib/foundry/foundrypf ]; then",
                '  exec /var/lib/foundry/foundrypf "$PORT"',
                "else",
                "  echo 'foundrypf not found; running without reverse tunnel. Use local SSH tunnel.'",
                "  while true; do sleep 3600; done",
                "fi",
            ]
        )
