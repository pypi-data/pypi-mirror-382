"""Template command - generate YAML task templates for editing.

Provides a minimal or full (commented) Task YAML skeleton.

- Minimal: programmatically generated, with concise inline hints interwoven
  above key fields for quick editing.
- Full: curated, comment-rich template with light substitutions that preserve
  comments.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import click
import yaml

from flow.application.config.config import Config
from flow.cli.commands.base import BaseCommand, console
from flow.sdk.models.task_config import TaskConfig


def _parse_env(items: Iterable[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for it in items:
        if "=" not in it:
            # Ignore malformed items silently to keep UX forgiving; user can edit YAML
            continue
        k, v = it.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k:
            env[k] = v
    return env


def _write_output(text: str, output: str | None, force: bool) -> None:
    if output:
        path = Path(output)
        if path.exists() and not force:
            raise click.ClickException(
                f"Output file already exists: {path}. Use --force to overwrite."
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        console.print(f"[success]✓[/success] Wrote template to [repr.path]{path}[/repr.path]")
    else:
        # Print raw text to stdout (avoid rich formatting)
        click.echo(text, nl=False)


def _generate_minimal_yaml(
    name: str | None,
    unique_name: bool,
    instance_type: str | None,
    min_gpu_memory_gb: int | None,
    command: str | None,
    image: str | None,
    env_items: Iterable[str],
    ports: Iterable[int],
    priority: str | None,
    max_price_per_hour: float | None,
    default_ssh_keys: list[str] | None = None,
) -> str:
    data: dict[str, object] = {}

    data["name"] = name or "flow-task"
    # For deterministic template output, avoid auto-suffixing the name during model validation.
    # We'll set unique_name in the emitted YAML, but instantiate with False to keep the base name.
    output_unique = bool(unique_name)
    data["unique_name"] = False

    if instance_type and min_gpu_memory_gb:
        # Fall back to instance_type
        min_gpu_memory_gb = None
    if instance_type:
        data["instance_type"] = instance_type
    elif min_gpu_memory_gb:
        data["min_gpu_memory_gb"] = int(min_gpu_memory_gb)
    else:
        data["instance_type"] = "8xh100"

    data["command"] = (
        command
        or 'echo "Hello from Flow!"\nnvidia-smi\necho "Edit this command to run your workload"'
    )
    data["image"] = image or "nvidia/cuda:12.1.0-runtime-ubuntu22.04"

    env_map = _parse_env(env_items)
    if env_map:
        data["env"] = env_map

    ps = [int(p) for p in ports]
    if ps:
        data["ports"] = ps

    if priority:
        data["priority"] = priority
    if max_price_per_hour is not None:
        data["max_price_per_hour"] = float(max_price_per_hour)

    # If a default SSH key is configured globally, seed it into the template
    if default_ssh_keys:
        # Keep the values as provided (platform IDs or local paths)
        try:
            keys = [str(k).strip() for k in default_ssh_keys if str(k).strip()]
            if keys:
                data["ssh_keys"] = keys
        except Exception:  # noqa: BLE001
            pass

    # Validate through TaskConfig to ensure we emit a valid minimal config
    cfg = TaskConfig(**data)
    out_data = cfg.model_dump(exclude_none=True)
    out_data["unique_name"] = output_unique
    # Omit select optional fields from minimal template for clarity
    for _k in ("allocation_mode", "upload_strategy", "upload_timeout"):
        out_data.pop(_k, None)
    yaml_body = yaml.safe_dump(out_data, sort_keys=False)

    # Header for minimal template — clarify core runtime semantics to avoid confusion
    header = (
        "# Save as task.yaml. Validate with: flow submit -d task.yaml\n"
        "# Submit when ready: flow submit task.yaml\n"
        "#\n"
        "# Runtime semantics:\n"
        "#  • Code upload: upload_code: true syncs your local project into the container working_dir\n"
        "#    (default /workspace). Use working_dir to change. Files appear at the same path inside\n"
        "#    the container and on the host.\n"
        "#  • Volumes vs data_mounts:\n"
        "#      volumes: create/attach persistent storage and mount it read-write at mount_path\n"
        "#      data_mounts: mount external sources (e.g., volume://NAME or s3://bucket/path) to a\n"
        "#                  target path (S3 mounts are read-only).\n"
        "#  • Logs: flow logs <task> -f follows container logs; use --source startup for instance\n"
        "#    startup logs while the container is launching.\n"
        "#  • Lifetime: the main container runs detached (restart=unless-stopped). Use\n"
        "#    max_run_time_hours to auto-cancel after a deadline, or set terminate_on_exit: true\n"
        "#    to cancel as soon as the main container exits.\n"
    )

    # Interleave detailed, field-scoped hints above common keys.
    # Use Required/Optional/Recommended labels and concise constraints/examples.
    comments: dict[str, list[str]] = {
        "name": [
            "# Optional: Identifier used in status/logs/ssh. Letters/digits/._-",
        ],
        "unique_name": [
            "# Optional: Append -xxxxxx for conflict-free names (recommended)",
        ],
        "instance_type": [
            "# Required (choose one with min_gpu_memory_gb): GPU selector",
            "#   Values: h100 | 8xh100 | a100-40gb | 4xa100 | <vendor/family>",
        ],
        "min_gpu_memory_gb": [
            "# Required (alternative to instance_type): any GPU with this memory",
            "#   Integer GB, e.g., 24 | 40 | 80",
        ],
        "command": [
            "# Recommended: What to run (string/list/block). Examples:",
            '#   command: "nvidia-smi"',
            "#   command: [python, train.py, --epochs, '10']",
            '#   command: |\n#     echo "hello"\n#     nvidia-smi',
        ],
        "image": [
            "# Optional: Docker image reference (registry/owner/name:tag).",
            "#   Example: nvidia/cuda:12.1.0-runtime-ubuntu22.04",
            "#   Private registries require credentials (pre-configured or pre-pulled)",
        ],
        "working_dir": [
            "# Optional: Working directory inside the container (defaults to /workspace)",
        ],
        "upload_code": [
            "# Optional: Upload local project to the working directory (true by default)",
        ],
        "code_root": [
            "# Optional: Override local project directory to upload (path)",
        ],
        "env": [
            "# Optional: Environment variables (key: value). Quote values with spaces/secrets.",
            "#   Examples:",
            "#   env:",
            "#     DATASET: imagenet",
            '#     SECRET_KEY: "${MY_SECRET}"',
        ],
        "ports": [
            "# Optional: Exposed ports (>=1024, <=65535). Unique; duplicates removed.",
            "#   Example: ports: [6006, 8888]",
        ],
        "priority": [
            "# Optional: Priority tier (low | med | high). Influences default limit price.",
        ],
        "max_price_per_hour": [
            "# Optional: Limit price (USD) to cap bids. Omit/null to use priority-based defaults.",
        ],
        "volumes": [
            "# Optional: Persistent volumes:",
            "#   - Create new: name + size_gb (+ interface: block|file) → mounted at mount_path",
            "#   - Attach existing: volume_id + mount_path",
            "#   - Mounted read-write at the same mount_path inside host and container",
            "#   - Block volumes are single-node only; use file interface (if available) for multi-attach",
            "#   - Avoid mounting at working_dir when upload_code: true; avoid system paths.",
            "# Example (create new volume):",
            "# volumes:",
            "#   - name: training-data",
            "#     size_gb: 100",
            "#     interface: block   # or: file",
            "#     mount_path: /volumes/data",
            "# Example (attach existing volume):",
            "#   - volume_id: vol_abc123",
            "#     mount_path: /volumes/existing",
        ],
        "data_mounts": [
            "# Optional: External data mounts:",
            "#   - volume://<name-or-id>  with target: /data         # persistent volume by name/ID",
            "#   - s3://bucket/path       with target: /mnt/s3/path  # read-only (requires AWS creds)",
        ],
        # Reserved-capacity fields intentionally omitted from minimal output
        "num_instances": [
            "# Optional: Instance count (multi-node when >1)",
        ],
        "distributed_mode": [
            "# Optional (multi-node): auto assigns ranks; manual expects FLOW_* envs",
        ],
        "internode_interconnect": [
            "# Optional: Preferred inter-node network (e.g., IB_3200, Ethernet)",
        ],
        "intranode_interconnect": [
            "# Optional: Preferred intra-node interconnect (e.g., SXM5, PCIe)",
        ],
        "region": [
            "# Optional: Preferred region/zone (provider dependent)",
        ],
        "ssh_keys": [
            "# Optional: Authorized SSH keys. Forms:",
            "#   - sshkey_abc123  (provider key ID)",
            "#   - ~/.ssh/id_ed25519  (private or .pub; resolves to private)",
            "#   - id_ed25519  (name in ~/.ssh or ~/.flow/keys)",
            "#   Examples:",
            "#   ssh_keys:",
            "#     - sshkey_abc123def456",
            "#     - ~/.ssh/id_ed25519.pub",
            "#     - id_ed25519",
        ],
        "allow_docker_cache": [
            "# Optional (advanced): Persist /var/lib/docker (single-node only)",
        ],
        "max_run_time_hours": [
            "# Optional: Max runtime hours (<=168). A systemd timer inside the instance cancels\n#   the task at the deadline (robust to restarts). Use 0/null to disable.",
        ],
        "min_run_time_hours": [
            "# Optional: Min guaranteed runtime hours (<=168)",
        ],
        "deadline_hours": [
            "# Optional: Time budget hours (FUTURE FEATURE).",
            "#   Not yet supported; must be >= max_run_time_hours when available.",
            "#   Like this? Please mention it in Slack to upvote.",
        ],
        "retries": [
            "# Optional: Retry policy (object): max_retries, backoff_coefficient, initial_delay, max_delay",
        ],
        "terminate_on_exit": [
            "# Optional: Auto-cancel when the main container exits (batch-friendly; default: false)",
        ],
    }

    lines = yaml_body.splitlines()
    out_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Only consider top-level keys (no leading spaces)
        if line and not line.startswith(" ") and ":" in line:
            key = line.split(":", 1)[0].strip()
            if key in comments:
                out_lines.extend(comments[key])
            # Ensure multi-line commands render as a YAML block scalar for readability
            if key == "command":
                cmd_val = out_data.get("command")
                if isinstance(cmd_val, str) and "\n" in cmd_val:
                    out_lines.append("command: |")
                    for cmd_line in cmd_val.splitlines():
                        out_lines.append(f"  {cmd_line}")
                    # Skip any original YAML-rendered command value lines
                    i += 1
                    while i < len(lines):
                        nxt = lines[i]
                        if nxt and not nxt.startswith(" "):
                            break
                        i += 1
                    continue
        out_lines.append(line)
        i += 1

    body_with_hints = "\n".join(out_lines) + (
        "\n" if out_lines and not out_lines[-1].endswith("\n") else ""
    )
    # Optional advanced appendix to enable power users (commented only)
    advanced = (
        "\n"
        "# Advanced (optional): uncomment to use\n"
        "# allocation_mode: spot     # spot | reserved | auto\n"
        "# upload_strategy: auto     # auto | embedded (~10KB) | scp | none\n"
        "# upload_timeout: 600       # 60..3600 seconds\n"
        "# max_run_time_hours: 12   # 0 or null disables monitoring (<=168)\n"
        "# min_run_time_hours: 1    # <=168\n"
        "# deadline_hours: 24       # FUTURE FEATURE: not yet supported; must be >= max_run_time_hours\n"
        "#                          # Like this? Please mention it in Slack.\n"
        "# retries:\n"
        "#   max_retries: 3\n"
        "#   backoff_coefficient: 2.0\n"
        "#   initial_delay: 1.0\n"
        "#   max_delay: 60.0\n"
        "# region: us-central1-b\n"
        "# reservation_id: reservation_abc123\n"
        '# scheduled_start_time: "2025-09-01T12:00:00Z"\n'
        "# reserved_duration_hours: 24\n"
        "# code_root: ./subdir    # override project directory to upload\n"
    )
    return header + body_with_hints + advanced


def _load_full_template_text() -> str:
    # Use importlib.resources to resolve packaged template path
    from importlib.resources import files

    try:
        pkg = files("flow.resources.templates")
        p = pkg.joinpath("config/task_full.yaml")
        return p.read_text(encoding="utf-8")
    except Exception as e:  # pragma: no cover - defensive  # noqa: BLE001
        raise click.ClickException(f"Failed to load full template: {e}")


def _apply_full_seeds(
    text: str,
    name: str | None,
    unique_name: bool | None,
    instance_type: str | None,
    min_gpu_memory_gb: int | None,
    command: str | None,
    image: str | None,
    env_items: Iterable[str],
    ports: Iterable[int],
    priority: str | None,
    max_price_per_hour: float | None,
    default_ssh_keys: list[str] | None = None,
) -> str:
    # Perform simple, line-oriented substitutions to preserve comments.
    lines = text.splitlines()
    out: list[str] = []

    env_map = _parse_env(env_items)
    ports_list = [int(p) for p in ports]

    i = 0
    while i < len(lines):
        line = lines[i]

        def set_scalar(prefix: str, value: object) -> str:
            return f"{prefix}: {value}"

        trimmed = line.strip()
        if trimmed.startswith("name:") and name is not None:
            leading = line[: line.index("n")]
            out.append(f"{leading}name: {name}")
            i += 1
            continue
        if trimmed.startswith("unique_name:") and unique_name is not None:
            leading = line[: line.index("u")]
            out.append(f"{leading}unique_name: {'true' if unique_name else 'false'}")
            i += 1
            continue
        if trimmed.startswith("instance_type:") and (
            instance_type or min_gpu_memory_gb is not None
        ):
            leading = line[: line.index("i")]
            if instance_type:
                out.append(f"{leading}instance_type: {instance_type}")
                i += 1
                continue
            else:
                # Switch to min_gpu_memory_gb: remove/keep commented alt line below if present
                out.append(
                    f"{leading}# instance_type: 8xh100  # replaced by min_gpu_memory_gb below"
                )
                i += 1
                # Insert or replace the next occurrence of 'min_gpu_memory_gb:' if present; else inject line
                inserted = False
                j = i
                while j < len(lines):
                    if lines[j].strip().startswith("min_gpu_memory_gb:"):
                        leading2 = lines[j][: lines[j].index("m")]
                        out.append(f"{leading2}min_gpu_memory_gb: {int(min_gpu_memory_gb or 0)}")
                        i = j + 1
                        inserted = True
                        break
                    j += 1
                if not inserted:
                    out.append(f"{leading}min_gpu_memory_gb: {int(min_gpu_memory_gb or 0)}")
                continue
        if trimmed.startswith("min_gpu_memory_gb:") and min_gpu_memory_gb is not None:
            leading = line[: line.index("m")]
            out.append(f"{leading}min_gpu_memory_gb: {int(min_gpu_memory_gb)}")
            i += 1
            continue
        if trimmed.startswith("image:") and image is not None:
            leading = line[: line.index("i")]
            out.append(f"{leading}image: {image}")
            i += 1
            continue
        if trimmed.startswith("priority:") and priority is not None:
            leading = line[: line.index("p")]
            out.append(f"{leading}priority: {priority}")
            i += 1
            continue
        if trimmed.startswith("max_price_per_hour:") and max_price_per_hour is not None:
            leading = line[: line.index("m")]
            # Ensure floats render cleanly
            out.append(f"{leading}max_price_per_hour: {float(max_price_per_hour)}")
            i += 1
            continue
        if trimmed.startswith("ports:") and ports_list:
            leading = line[: line.index("p")]
            # Render inline list for compactness
            items = ", ".join(str(p) for p in ports_list)
            out.append(f"{leading}ports: [{items}]")
            i += 1
            continue
        if trimmed.startswith("env:") and env_map:
            leading = line[: line.index("e")]
            out.append(f"{leading}env:")
            for k, v in env_map.items():
                out.append(f"{leading}  {k}: {v}")
            # Skip any immediate "env: {}" placeholder on the next line(s)
            i += 1
            # Swallow a simple '{}' mapping body that might follow
            if i < len(lines) and lines[i].strip() == "{}":
                i += 1
            continue
        if trimmed.startswith("command:") and command is not None:
            # Replace entire block scalar under command: |
            # Detect if current line uses block scalar; if not, write one.
            leading = line[: line.index("c")]
            out.append(f"{leading}command: |")
            # Write command lines indented by two spaces beyond leading
            indent = leading + "  "
            for cmd_line in command.splitlines() or [""]:
                out.append(f"{indent}{cmd_line}")
            # Skip existing block
            i += 1
            # If next line is a block indicator or indented content, consume until unindented or blank line separating next key
            while i < len(lines):
                nxt = lines[i]
                if nxt.startswith(leading + "  "):
                    i += 1
                    continue
                # Stop at the next top-level key or comment; keep it for normal processing
                break
            continue

        # Seed ssh_keys when a default is available: convert commented example into live config
        if default_ssh_keys and trimmed.startswith("# ssh_keys:"):
            leading = line[: line.index("#")] if "#" in line else ""
            out.append(f"{leading}ssh_keys:")
            for k in default_ssh_keys:
                try:
                    kv = str(k).strip()
                    if kv:
                        out.append(f"{leading}  - {kv}")
                except Exception:  # noqa: BLE001
                    continue
            # Skip the following commented example lines if present
            i += 1
            while i < len(lines) and lines[i].strip().startswith("#   -"):
                i += 1
            continue

        # Default: passthrough
        out.append(line)
        i += 1

    # If we had no max_price_per_hour key in template but user supplied one, append it near priority
    if max_price_per_hour is not None and "max_price_per_hour:" not in "\n".join(out):
        # Try to insert after priority if present
        inserted = False
        for idx, ln in enumerate(out):
            if ln.strip().startswith("priority:"):
                leading = ln[: ln.index("p")]
                out.insert(idx + 1, f"{leading}max_price_per_hour: {float(max_price_per_hour)}")
                inserted = True
                break
        if not inserted:
            out.append(f"max_price_per_hour: {float(max_price_per_hour)}")

    # If switching to min_gpu_memory_gb and template didn't have it, ensure it's present near selector section
    if min_gpu_memory_gb is not None and not any(
        ln.strip().startswith("min_gpu_memory_gb:") for ln in out
    ):
        # Insert after instance_type commented line
        for idx, ln in enumerate(out):
            if ln.strip().startswith("# instance_type:") or ln.strip().startswith("instance_type:"):
                leading = ln[: ln.index(ln.strip()[0])]
                out.insert(idx + 1, f"{leading}min_gpu_memory_gb: {int(min_gpu_memory_gb)}")
                break

    # If name provided but unique_name not specified, leave template's default as-is
    return "\n".join(out) + ("\n" if not out or not out[-1].endswith("\n") else "")


class TemplateCommand(BaseCommand):
    """Generate YAML templates for tasks."""

    @property
    def name(self) -> str:
        return "template"

    @property
    def help(self) -> str:
        return "Generate editable YAML templates (minimal or full)"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        def template() -> None:
            """Template operations group."""

        @template.command(name="task", help="Generate a Task YAML template")
        @click.option("--full", is_flag=True, help="Generate full, commented template")
        @click.option("-o", "--output", type=click.Path(dir_okay=False), help="Write to file")
        @click.option("--force", is_flag=True, help="Overwrite existing output file")
        @click.option("--name", type=str, help="Seed task name")
        @click.option("--no-unique", is_flag=True, help="Set unique_name: false")
        @click.option("--instance", "-i", type=str, help="Seed instance_type (e.g., h100, 8xh100)")
        @click.option(
            "--min-gpu-mem",
            type=int,
            help="Seed min_gpu_memory_gb (mutually exclusive with --instance)",
        )
        @click.option("--command", "-c", type=str, help="Seed command (multi-line supported)")
        @click.option("--image", type=str, help="Seed image")
        @click.option(
            "--env",
            "env_items",
            multiple=True,
            help="Seed environment variables as KEY=VALUE (repeatable)",
        )
        @click.option(
            "--port",
            type=int,
            multiple=True,
            help="Seed ports (repeatable, high ports only)",
        )
        @click.option(
            "--priority",
            type=click.Choice(["low", "med", "high"], case_sensitive=False),
            help="Seed priority",
        )
        @click.option("--max-price-per-hour", type=float, help="Seed max_price_per_hour (USD)")
        def task(
            full: bool,
            output: str | None,
            force: bool,
            name: str | None,
            no_unique: bool,
            instance: str | None,
            min_gpu_mem: int | None,
            command: str | None,
            image: str | None,
            env_items: tuple[str, ...],
            port: tuple[int, ...],
            priority: str | None,
            max_price_per_hour: float | None,
        ) -> None:
            """Generate a Task YAML template to stdout or file.

            Examples:
                flow template task > task.yaml
                flow template task --full -o task.yaml
                flow template task -o train.yaml -i h100 --name my-train --command 'python train.py'
            """
            if instance and min_gpu_mem:
                raise click.ClickException("--instance and --min-gpu-mem are mutually exclusive")

            unique_name = not no_unique

            # Detect default SSH keys from config or local environment
            default_ssh_keys: list[str] | None = None
            try:
                cfg = Config.from_env(require_auth=False)
                keys_val = (
                    cfg.provider_config.get("ssh_keys")
                    if isinstance(cfg.provider_config, dict)
                    else None
                )
                if isinstance(keys_val, list) and keys_val:
                    default_ssh_keys = [str(k).strip() for k in keys_val if str(k).strip()]
                # If not configured, try common local keys for convenience (id_ed25519, id_rsa)
                if not default_ssh_keys:
                    from pathlib import Path as _Path

                    candidates = [
                        _Path.home() / ".ssh" / "id_ed25519",
                        _Path.home() / ".ssh" / "id_rsa",
                        _Path.home() / ".flow" / "keys" / "id_ed25519",
                        _Path.home() / ".flow" / "keys" / "id_rsa",
                    ]
                    found: list[str] = []
                    for p in candidates:
                        try:
                            if p.exists() and p.is_file():
                                found.append(str(p))
                        except Exception:  # noqa: BLE001
                            continue
                    if found:
                        default_ssh_keys = [found[0]]
            except Exception:  # noqa: BLE001
                default_ssh_keys = None

            if not full:
                text = _generate_minimal_yaml(
                    name,
                    unique_name,
                    instance,
                    min_gpu_mem,
                    command,
                    image,
                    env_items,
                    port,
                    priority,
                    max_price_per_hour,
                    default_ssh_keys=default_ssh_keys,
                )
            else:
                base = _load_full_template_text()
                text = _apply_full_seeds(
                    base,
                    name=name,
                    unique_name=unique_name,
                    instance_type=instance,
                    min_gpu_memory_gb=min_gpu_mem,
                    command=command,
                    image=image,
                    env_items=env_items,
                    ports=port,
                    priority=priority,
                    max_price_per_hour=max_price_per_hour,
                    default_ssh_keys=default_ssh_keys,
                )

            _write_output(text, output, force)

        return template


command = TemplateCommand()
