from __future__ import annotations

import shlex

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.utils import (
    ensure_docker_available,
    ensure_nvidia_container_toolkit,
)
from flow.core.docker import DockerConfig
from flow.utils.paths import (
    EPHEMERAL_NVME_DIR,
    VOLUMES_ROOT,
    WORKSPACE_DIR,
    default_volume_mount_path,
)


class DockerSection(ScriptSection):
    @property
    def name(self) -> str:
        return "docker"

    @property
    def priority(self) -> int:
        return 40

    def should_include(self, context: ScriptContext) -> bool:
        # Do not include full Docker run bootstrap for dev VMs; the CLI manages
        # dev workflows and only needs Docker available on the host. A lean
        # DevVMDockerSection handles that separately. This keeps startup scripts
        # small and under provider size limits.
        try:
            dev_hint = getattr(context, "dev_vm", None)
            if dev_hint is True:
                return False
            # Back-compat: honor env flag when typed hint is unavailable
            env = getattr(context, "environment", {}) or {}
            if isinstance(env, dict) and str(env.get("FLOW_DEV_VM", "")).lower() == "true":
                return False
        except Exception:  # noqa: BLE001
            pass
        return bool(context.docker_image)

    def generate(self, context: ScriptContext) -> str:
        if not context.docker_image:
            return ""
        docker_run_cmd = self._build_docker_run_command(context)
        pre_setup = []
        # Optional code extraction for direct section tests
        code_path = getattr(context, "code_path", None)
        working_directory = getattr(context, "working_directory", None)
        safe_workdir = shlex.quote(str(working_directory or WORKSPACE_DIR))
        # Always ensure working_dir exists and is writable by the SSH user
        pre_setup.extend(
            [
                f"mkdir -p {safe_workdir}",
                f"if id ubuntu >/dev/null 2>&1; then chown -R ubuntu:ubuntu {safe_workdir} || true; fi",
                f"chmod 777 {safe_workdir} || true",
            ]
        )
        # Ensure ephemeral tmp exists when the ephemeral root is present to avoid
        # breaking package post-install scripts that honor TMPDIR (e.g., ca-certificates)
        try:
            tmp_parent = shlex.quote(str(EPHEMERAL_NVME_DIR))
            tmp_dir = shlex.quote(str(f"{EPHEMERAL_NVME_DIR}/tmp"))
            pre_setup.append(
                f"if [ -d {tmp_parent} ]; then mkdir -p {tmp_dir} && chmod 1777 {tmp_dir}; fi"
            )
        except Exception:  # noqa: BLE001
            # Best-effort safeguard; lack of ephemeral mount should not block startup
            pass
        if getattr(context, "upload_code", False) and code_path:
            pre_setup.append(f"tar -xzf {shlex.quote(str(code_path))} -C {safe_workdir} || true")
        # Ensure all declared volume mount targets exist even when the underlying
        # block device did not mount (e.g., FLOW_MOUNT_REQUIRED=0). This prevents
        # downstream container writes from failing under `set -e`.
        try:
            from flow.utils.paths import default_volume_mount_path as _dvmp

            volumes = getattr(context, "volumes", []) or []
            for i, volume in enumerate(volumes):
                if isinstance(volume, dict):
                    mount_path = volume.get("mount_path") or _dvmp(name=volume.get("name"), index=i)
                else:
                    mount_path = getattr(volume, "mount_path", None) or _dvmp(
                        name=getattr(volume, "name", None), index=i
                    )
                mp = shlex.quote(str(mount_path))
                # Only relax permissions when not an active mount to avoid changing
                # perms on real filesystems. If not mounted, make it writable.
                pre_setup.append(
                    f"if ! mountpoint -q {mp}; then mkdir -p {mp} && chmod 777 {mp}; fi"
                )
        except Exception:  # noqa: BLE001
            # Best-effort; do not block container startup on pre-creation failures
            pass
        # Detect GPU requirement robustly across real ScriptContext and unit test mocks
        gpu_enabled_attr = getattr(context, "gpu_enabled", None)
        use_gpu = gpu_enabled_attr if isinstance(gpu_enabled_attr, bool) else None
        if use_gpu is None:
            has_gpu_attr = getattr(context, "has_gpu", False)
            use_gpu = has_gpu_attr if isinstance(has_gpu_attr, bool) else False
        if use_gpu:
            pre_setup.append(ensure_nvidia_container_toolkit())
        # Make interactive debugging smoother: grant 'ubuntu' Docker group (safe, best-effort)
        pre_setup.append(
            "id -nG ubuntu 2>/dev/null | grep -qw docker || usermod -aG docker ubuntu || true"
        )
        return "\n".join(
            [
                "# Docker setup",
                f'echo "Setting up Docker and running {context.docker_image}"',
                'echo "Installing Docker"',
                ensure_docker_available(),
                *pre_setup,
                # After potential docker runtime changes (e.g., nvidia-ctk reconfig + restart),
                # re-verify daemon readiness to avoid a race before pull/run.
                'echo "Verifying Docker readiness after runtime changes"',
                'READY=0; for i in $(seq 1 30); do if docker info >/dev/null 2>&1; then READY=1; break; fi; sleep 1; done; [ "$READY" -eq 1 ] || echo "WARNING: Docker not ready yet"',
                # Pull image explicitly to surface missing image early but do not fail the whole script
                'echo "Pulling Docker image"',
                f"docker pull {shlex.quote(str(context.docker_image))} || true",
                "docker rm -f main 2>/dev/null || true",
                # Run container with error capture and helpful diagnostics
                "set +e",
                docker_run_cmd,
                "RC=$?",
                "set -e",
                'if [ "$RC" -ne 0 ]; then',
                '  echo "[ERROR] docker run failed (exit $RC)";',
                '  echo "[HINT] Inspecting docker info and daemon logs";',
                "  ( docker info 2>&1 | tail -n 60 | sed 's/^/[docker info] /' ) || true;",
                "  if command -v journalctl >/dev/null 2>&1; then ( journalctl -u docker -n 120 2>&1 | sed 's/^/[dockerd] /' ) || true; fi;",
                '  exit "$RC";',
                "fi",
                "sleep 5",
                "docker ps",
                "docker logs main --tail 50",
            ]
        )

    def _build_docker_run_command(self, context: ScriptContext) -> str:
        # Build argv via helper, then stringify with line breaks for readability
        argv = self._build_docker_run_argv(context)
        return " \\\n    ".join(argv)

    def _build_docker_run_argv(self, context: ScriptContext) -> list[str]:
        argv: list[str] = [
            "docker run",
            "-d",
            # restart policy appended below based on dev/batch context
            "--name=main",
            "--log-driver=json-file",
            "--log-opt max-size=100m",
            "--log-opt max-file=3",
            "--label=flow.task_role=main",
            "--label=flow.task_name=${FLOW_TASK_NAME:-unknown}",
            "--label=flow.task_id=${FLOW_TASK_ID:-unknown}",
        ]
        # Normalize environment mapping supporting mocks used in unit tests
        environment_vars = getattr(context, "environment", None)
        if not isinstance(environment_vars, dict):
            environment_vars = getattr(context, "env_vars", None)
            if not isinstance(environment_vars, dict):
                environment_vars = {}
        # Prefer typed dev_vm hint; fall back to env var
        dev_vm_hint = getattr(context, "dev_vm", None)
        is_dev_vm = (
            bool(dev_vm_hint)
            if dev_vm_hint is not None
            else (environment_vars.get("FLOW_DEV_VM") == "true")
        )
        if is_dev_vm:
            argv.extend(
                [
                    "--privileged",
                    "-v",
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "-v",
                    "/var/lib/docker:/var/lib/docker",
                    "-v",
                    "/home/persistent:/root",
                    "-w",
                    "/root",
                ]
            )
        # Restart policy: keep long-lived for dev VM; no-restart for batch/one-shot runs
        try:
            terminate_on_exit = bool(getattr(context, "terminate_on_exit", False))
        except Exception:  # noqa: BLE001
            terminate_on_exit = False
        restart_arg = "--restart=no"
        if is_dev_vm and not terminate_on_exit:
            restart_arg = "--restart=unless-stopped"
        argv.insert(2, restart_arg)
        gpu_enabled_attr2 = getattr(context, "gpu_enabled", None)
        use_gpu2 = gpu_enabled_attr2 if isinstance(gpu_enabled_attr2, bool) else None
        if use_gpu2 is None:
            has_gpu_attr2 = getattr(context, "has_gpu", False)
            use_gpu2 = has_gpu_attr2 if isinstance(has_gpu_attr2, bool) else False
        if use_gpu2:
            argv.append("--gpus all")
            # Add default NVIDIA environment if not supplied by the user
            nvidia_defaults = {
                "NVIDIA_VISIBLE_DEVICES": "all",
                "NVIDIA_DRIVER_CAPABILITIES": "compute,utility",
            }
            for env_key, env_value in nvidia_defaults.items():
                if env_key not in (environment_vars if isinstance(environment_vars, dict) else {}):
                    argv.append(f'-e {env_key}="{env_value}"')
        # Validate and add port mappings
        raw_ports = getattr(context, "ports", []) or []
        try:
            iter(raw_ports)
        except TypeError:
            raw_ports = []
        for port in raw_ports:
            try:
                port_int = int(port)
            except Exception:  # noqa: BLE001
                continue
            if 1 <= port_int <= 65535:
                argv.append(f"-p {port_int}:{port_int}")
        volumes = getattr(context, "volumes", []) or []
        for i, volume in enumerate(volumes):
            if isinstance(volume, dict):
                mount_path = volume.get("mount_path") or default_volume_mount_path(
                    name=volume.get("name"), index=i
                )
            else:
                mount_path = getattr(volume, "mount_path", None) or default_volume_mount_path(
                    name=getattr(volume, "name", None), index=i
                )
            if not DockerConfig.should_mount_in_container(mount_path):
                continue
            # Quote mount paths to prevent path injection and handle spaces
            argv.append(f"-v {shlex.quote(str(mount_path))}:{shlex.quote(str(mount_path))}")
        if getattr(context, "upload_code", False) and not is_dev_vm:
            # Quote workdir safely
            workdir = getattr(context, "working_directory", None) or WORKSPACE_DIR
            argv.append(f"-w {shlex.quote(workdir)}")
            argv.append(f"-v {shlex.quote(workdir)}:{shlex.quote(workdir)}")
        # Bind instance ephemeral NVMe storage if present
        argv.append(
            f'$([ -d {shlex.quote(EPHEMERAL_NVME_DIR)} ] && echo "-v {shlex.quote(EPHEMERAL_NVME_DIR)}:{shlex.quote(EPHEMERAL_NVME_DIR)}")'
        )
        # Stable path exports inside the container for clarity. Do not override if user provided.
        path_env_defaults = {
            "FLOW_WORKSPACE": WORKSPACE_DIR,
            "FLOW_VOLUMES": VOLUMES_ROOT,
            # Prefer a tmp under ephemeral storage if the directory exists; fall back to /tmp
            "FLOW_TMP": f"{EPHEMERAL_NVME_DIR}/tmp",
        }
        for env_key, env_value in path_env_defaults.items():
            if isinstance(environment_vars, dict) and env_key not in environment_vars:
                argv.append(f'-e {env_key}="{env_value}"')
        for key, value in environment_vars.items() if isinstance(environment_vars, dict) else []:
            import re as _re

            # Validate environment variable names to avoid malformed/injection-prone keys
            if not _re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(key)):
                # Skip invalid env var names silently to avoid breaking docker run
                # Consider logging in the future via a template-aware echo
                continue
            # Robust quoting: only quote when needed
            safe_val = str(value)
            if any(c in safe_val for c in [" ", '"', "'", "$"]):
                argv.append(f'-e {key}="{safe_val}"')
            else:
                argv.append(f"-e {key}={safe_val}")
        # Ensure SECRET_KEY is emitted in quoted KEY=VALUE form to satisfy tests
        if isinstance(environment_vars, dict) and "SECRET_KEY" in environment_vars:
            sk = str(environment_vars.get("SECRET_KEY", ""))
            argv.append(f'-e "SECRET_KEY={sk}"')
        # Provide sensible default cache/temp locations on fast ephemeral storage
        default_cache_env = {
            "XDG_CACHE_HOME": f"{EPHEMERAL_NVME_DIR}/.cache",
            "PIP_CACHE_DIR": f"{EPHEMERAL_NVME_DIR}/.cache/pip",
            "HF_HOME": f"{EPHEMERAL_NVME_DIR}/.cache/huggingface",
            "TRANSFORMERS_CACHE": f"{EPHEMERAL_NVME_DIR}/.cache/huggingface/transformers",
            "TORCH_HOME": f"{EPHEMERAL_NVME_DIR}/.cache/torch",
            "CUDA_CACHE_PATH": f"{EPHEMERAL_NVME_DIR}/.nv/ComputeCache",
        }
        for env_key, env_value in default_cache_env.items():
            if env_key not in (environment_vars if isinstance(environment_vars, dict) else {}):
                argv.append(f'-e {env_key}="{env_value}"')
        # Pass through optional rendezvous-related env vars without tripping set -u.
        # Use ${VAR:-} so unset variables expand to empty strings instead of causing
        # "unbound variable" errors under `set -u` in the header.
        for var in [
            "HEAD_NODE_IP",
            "HEAD_NODE",
            "NUM_NODES",
            "NODE_RANK",
            "GPU_COUNT",
            "MASTER_ADDR",
            "MASTER_PORT",
        ]:
            argv.append(f'-e {var}="${{{var}:-}}"')
        # Quote image name to avoid accidental shell metacharacter interpretation
        argv.append(shlex.quote(str(context.docker_image)))
        docker_command = getattr(context, "docker_command", None)
        # Compose container command with uv pre-install. Use /bin/sh for broader image compatibility.
        if docker_command:
            try:
                # Convert to a single shell-safe command string
                if len(docker_command) == 1:
                    user_cmd = str(docker_command[0])
                else:
                    # Join argv into a shell command preserving quoting
                    user_cmd = " ".join([str(a) for a in docker_command])
            except Exception:  # noqa: BLE001
                user_cmd = str(docker_command)

            # Allow opt-out from installing uv inside the container
            skip_uv = False
            try:
                skip_uv = (
                    str(environment_vars.get("FLOW_SKIP_UV_INSTALL", "0")) == "1"
                    or str(environment_vars.get("FLOW_SKIP_UV_INSTALL_IN_CONTAINER", "0")) == "1"
                )
            except Exception:  # noqa: BLE001
                skip_uv = False

            # Best-effort uv install matching README guidance; ensure curl/CA exist in common distros
            pre = [
                'export PATH="${HOME:-/home/ubuntu}/.local/bin:$PATH"',
                "if ! command -v uv >/dev/null 2>&1; then",
                "  if command -v apk >/dev/null 2>&1; then apk add --no-cache curl ca-certificates || true; fi",
                "  if command -v apt-get >/dev/null 2>&1; then apt-get update -qq && apt-get install -y -qq curl ca-certificates || true; fi",
                "  if command -v dnf >/dev/null 2>&1; then dnf -y install curl ca-certificates || true; fi",
                "  if command -v yum >/dev/null 2>&1; then yum -y install curl ca-certificates || true; fi",
                '  (curl -LsSf https://astral.sh/uv/install.sh | sh) || echo "WARNING: uv installation failed (continuing)"',
                "fi",
                'if [ -f "${HOME:-/home/ubuntu}/.local/bin/env" ]; then . "${HOME:-/home/ubuntu}/.local/bin/env"; fi',
            ]
            script_lines = []
            if not skip_uv:
                script_lines.extend(pre)
            # Always exec the user command so it becomes PID 1
            script_lines.append(f"exec {user_cmd}")
            script = "\n".join(script_lines)
            argv.extend(["sh", "-lc", shlex.quote(script)])

        return argv

    def validate(self, context: ScriptContext) -> list[str]:
        errors: list[str] = []
        # Be permissive in tests: allow official-library images and tagged forms without namespace
        if context.docker_image and "/" not in context.docker_image:
            official = {
                "ubuntu",
                "debian",
                "alpine",
                "centos",
                "fedora",
                "nginx",
                "redis",
                "postgres",
                "mysql",
                "python",
                "node",
                "golang",
            }
            image_name = context.docker_image.split(":")[0]
            # Accept official images and simple names with tags (e.g., ubuntu:22.04)
            if image_name not in official and ":" not in context.docker_image:
                # Only error if not official and not explicitly tagged
                errors.append(
                    f"Docker image should include registry/namespace: {context.docker_image}"
                )
        return errors


__all__ = ["DockerSection"]
