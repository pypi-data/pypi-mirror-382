from __future__ import annotations

import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.utils import (
    ensure_curl_available,
)


class TerminateOnExitSection(ScriptSection):
    @property
    def name(self) -> str:
        return "terminate_on_exit"

    @property
    def priority(self) -> int:
        # After Docker/UserScript sections; before completion
        return 88

    def should_include(self, context: ScriptContext) -> bool:
        return bool(getattr(context, "terminate_on_exit", False))

    def generate(self, context: ScriptContext) -> str:
        if not self.should_include(context):
            return ""

        # Seed a minimal runtime config so the cancel helper has credentials
        config_block = self._build_config_block(context)

        cancel_script = self._build_cancel_script_inline()
        service_unit = self._build_service_unit_inline()

        ensure_curl = ensure_curl_available()

        return textwrap.dedent(
            f"""
            # Terminate-on-exit: cancel task when main container exits
            mkdir -p /var/log/flow
            {config_block}
            {ensure_curl}
            # Install cancel helper if missing (shared with runtime monitor)
            if [ ! -x /usr/local/bin/flow-runtime-cancel.sh ]; then
              cat > /usr/local/bin/flow-runtime-cancel.sh << 'CANCEL_EOF'
{cancel_script}
CANCEL_EOF
              chmod +x /usr/local/bin/flow-runtime-cancel.sh
            fi
            # Install watcher service
            cat > /usr/local/sbin/flow-terminate-on-exit.sh <<'WATCH_EOF'
#!/bin/bash
set -euo pipefail
CN="main"
if ! command -v docker >/dev/null 2>&1; then exit 0; fi
# Wait until container exists
for i in $(seq 1 900); do
  if docker ps -a --format '{{{{.Names}}}}' | grep -q "^$CN$"; then break; fi
  sleep 1
done
# Wait for container exit; then cancel the task
docker wait "$CN" >/dev/null 2>&1 || true
/usr/local/bin/flow-runtime-cancel.sh || true
WATCH_EOF
            chmod +x /usr/local/sbin/flow-terminate-on-exit.sh

            cat > /etc/systemd/system/flow-terminate-on-exit.service <<'SERVICE_EOF'
{service_unit}
SERVICE_EOF
            if command -v systemctl >/dev/null 2>&1; then
              systemctl daemon-reload
              systemctl enable flow-terminate-on-exit.service
              systemctl restart flow-terminate-on-exit.service || systemctl start flow-terminate-on-exit.service
            else
              nohup /usr/local/sbin/flow-terminate-on-exit.sh >/var/log/flow/terminate-on-exit.log 2>&1 &
            fi
            """
        ).strip()

    def _build_config_block(self, context: ScriptContext) -> str:
        """Write a minimal /var/lib/flow/task-runtime.conf if missing.

        This ensures terminate_on_exit works even when max_run_time_hours is not set.
        """
        # Pull provider env injected during submission; fall back to defaults conservatively
        env = getattr(context, "environment", {}) or {}
        api_key = env.get("MITHRIL_API_KEY", "")
        api_url = env.get("MITHRIL_API_URL", "https://api.mithril.ai")
        project = env.get("MITHRIL_PROJECT", "")

        # If we lack required values, emit a noop (script still functions but remote cancel may be skipped)
        if not api_key or not project:
            return "# No provider credentials available for terminate_on_exit"

        task_name = getattr(context, "task_name", None) or "unknown"
        return textwrap.dedent(
            f"""
            # Seed task runtime config if not present
            CONFIG_PATH="/var/lib/flow/task-runtime.conf"
            umask 077
            if [ ! -f "$CONFIG_PATH" ]; then
              mkdir -p /var/lib/flow
              cat > "$CONFIG_PATH" <<EOF
TASK_NAME="{task_name}"
MITHRIL_API_KEY="{api_key}"
MITHRIL_API_URL="{api_url}"
MITHRIL_PROJECT="{project}"
EOF
            fi
            """
        ).strip()

    def _build_cancel_script_inline(self) -> str:
        # Reuse the same cancellation logic as runtime monitor (inline to avoid import coupling)
        return textwrap.dedent(
            """
            #!/bin/bash
            set -euo pipefail
            CONFIG="/var/lib/flow/task-runtime.conf"
            [ -f "$CONFIG" ] && source "$CONFIG" || true
            log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [terminate_on_exit] $*"; }

            # Distinct runtime UA for observability (overridable)
            FLOW_RUNTIME_UA="${FLOW_RUNTIME_UA:-flow-runtime/$(uname -s)-$(uname -m)}"

            # Fallback to submission-provided env if config lacks values
            : "${MITHRIL_API_KEY:=${MITHRIL_API_KEY:-}}"
            : "${MITHRIL_API_URL:=${MITHRIL_API_URL:-https://api.mithril.ai}}"
            : "${MITHRIL_PROJECT:=${MITHRIL_PROJECT:-}}"

            # Try to stop main container quickly
            docker stop -t 10 main 2>/dev/null || true
            sleep 5

            INSTANCE_ID=$(curl -s --max-time 5 http://169.254.169.254/latest/meta-data/instance-id || hostname)
            JSON=$(curl -sS --max-time 20 -H "Authorization: Bearer $MITHRIL_API_KEY" -H "User-Agent: $FLOW_RUNTIME_UA" "$MITHRIL_API_URL/v2/spot/bids?project=$MITHRIL_PROJECT" || true)

            TASK_ID="unknown"
            if command -v jq >/dev/null 2>&1; then
              TASK_ID=$(echo "$JSON" | jq -r --arg IID "$INSTANCE_ID" --arg NAME "${TASK_NAME:-}" '
                (.. | objects | select(has("instances")))? as $x |
                ($x.instances[]? | select(.instance_id == $IID) | $x.fid) //
                ((.data // .)[]? | select(.name == $NAME and .fid != null) | .fid) //
                "unknown"
              ')
            else
              TASK_ID=$( INSTANCE_ID="$INSTANCE_ID" TASK_NAME="${TASK_NAME:-}" python3 - <<'PY' 2>/dev/null || echo unknown
import os,sys,json
try:
  data=json.load(sys.stdin)
except Exception:
  print("unknown"); sys.exit(0)
items=data if isinstance(data,list) else data.get("data",[])
iid=os.environ.get("INSTANCE_ID","")
name=os.environ.get("TASK_NAME","")
fid="unknown"
for x in items:
  for inst in (x.get("instances") or []):
    if inst.get("instance_id")==iid:
      fid = x.get("fid") or "unknown"
      break
  if fid!="unknown":
    break
if fid=="unknown" and name:
  for x in items:
    if x.get("name")==name:
      fid = x.get("fid") or "unknown"
      break
print(fid)
PY
              )
            fi

            if [ "$TASK_ID" != "unknown" ]; then
              log "Cancelling task $TASK_ID due to container exit"
              for attempt in 1 2 3 4 5; do
                CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X DELETE \
                  -H "Authorization: Bearer $MITHRIL_API_KEY" \
                  -H "User-Agent: $FLOW_RUNTIME_UA" \
                  -H "Content-Type: application/json" \
                  "$MITHRIL_API_URL/v2/spot/bids/$TASK_ID" --max-time 30 || true)
                if [ "$CODE" = "200" ] || [ "$CODE" = "204" ] || [ "$CODE" = "202" ]; then
                  log "Cancelled task $TASK_ID successfully"
                  break
                fi
                sleep $((attempt * attempt))
              done
            else
              log "Could not resolve TASK_ID from provider API; skipping remote cancel"
            fi
            """
        ).strip()

    def _build_service_unit_inline(self) -> str:
        return textwrap.dedent(
            """
            [Unit]
            Description=Flow Terminate On Exit
            After=network-online.target docker.service
            Wants=network-online.target

            [Service]
            Type=simple
            ExecStart=/usr/local/sbin/flow-terminate-on-exit.sh
            Restart=no

            [Install]
            WantedBy=multi-user.target
            """
        ).strip()


__all__ = ["TerminateOnExitSection"]
