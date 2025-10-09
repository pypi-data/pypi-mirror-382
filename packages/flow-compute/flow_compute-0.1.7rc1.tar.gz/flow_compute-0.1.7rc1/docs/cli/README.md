### CLI documentation index

- Command reference: command-reference.md
- Adding CLI commands (for contributors): adding-commands.md
- Demo mode catalog and architecture: demo-mode-catalog.md
- Update command: update-command.md (if present)
- Getting started: see docs/getting-started/

# CLI Reference

Command-line usage for Flow. Each command shows purpose, common flags, and examples. For full help, run `flow <command> --help`.

- Note on `flow dev` uploads: By default, `flow dev` uploads your current dir into a same-named dir on the VM (parent `$HOME`) and starts the shell there. Use `--flat` to expand contents directly into the parent.

## run

- Purpose: Submit a task from YAML or a direct command
- Common flags:
  - `-i, --instance-type`: GPU type (e.g., `a100`, `8xa100`, `h100`)
  - `-k, --ssh-keys`: Inject SSH keys (repeatable). Accepts a platform key ID like `sshkey_ABC123`, a local private key path like `~/.ssh/id_ed25519`, or a key name resolvable in `~/.ssh` or `~/.flow/keys`. Repeat `-k` to include multiple keys.
  - `--image`: Docker image (default: `nvidia/cuda:12.1.0-runtime-ubuntu22.04`)
  - `--code-root`: Local project directory to upload (defaults to CWD). By default Flow maps code to `/workspace/<project>` (nested) unless you explicitly set `working_dir`.
  - `-n, --name`: Task name
  - `-m, --max-price-per-hour`: Limit price in USD/hr
  - `-N, --num-instances`: Multi-node count
  - `--mount`: Data mount (e.g., `s3://bucket/path`)
  - `--port`: Expose a high port (>=1024) on the instance public IP (repeatable)
  - `--watch`: Watch progress
- Examples:
  ```bash
  flow submit "python train.py" -i a100
  flow submit <config.yaml> --watch
  flow submit -i 8xh100 -- torchrun --nproc_per_node=8 train.py
  # Multiple SSH keys
  flow submit -i a100 -k ~/.ssh/id_ed25519 -k sshkey_ABC123 -k work_laptop
  # Expose a simple HTTP server on port 8080
  flow submit "python -m http.server 8080" --port 8080
  # Reserved capacity (coming soon)
  # Reservations are being finalized; use `flow reserve create` for previews
  # Upload only a subdirectory and use a specific image
  flow submit -i a100 --code-root ./src --image pytorch/pytorch:2.2.2-cuda12.1-cudnn8 -- python tasks/train.py
  ```

## status

- Purpose: Show task status (optionally all tasks)
- Examples:
  ```bash
  flow status
  flow status my-task-name
  flow status --all
  ```

## logs

- Purpose: View task logs
- Examples:
  ```bash
  flow logs my-task-name
  flow logs my-task-name --follow
  ```

## cancel

- Purpose: Cancel a running task
- Examples:
  ```bash
  flow cancel my-task-name
  ```

## ssh

- Purpose: Open an SSH shell or run a remote command
- Examples:
  ```bash
  flow ssh my-task-name
  flow ssh my-task-name -- nvidia-smi
  ```

## ssh-keys

- Purpose: Manage SSH keys with the provider
- Examples:
  ```bash
  flow ssh-keys get
  flow ssh-keys upload ~/.ssh/id_ed25519.pub
  flow ssh-keys require sshkey_ABC123         # Mark a key as required (admin)
  flow ssh-keys require --unset sshkey_ABC123 # Clear required flag (admin)
  ```

Notes:
- SSH keys are project-scoped. Project administrators may set required keys; these are automatically included in launches and shown with a "(required)" tag in listings.

## ssh-keys

- Purpose: Manage SSH keys with the provider
- Examples:
  ```bash
  flow ssh-keys get
  flow ssh-keys upload ~/.ssh/id_ed25519.pub
  flow ssh-keys require sshkey_ABC123         # Mark a key as required (admin)
  flow ssh-keys require --unset sshkey_ABC123 # Clear required flag (admin)
  ```

## reservations

- Purpose: Manage capacity reservations (create/list/show)
- Examples:
  ```bash
  # Create a reservation window (supports relative --start)
  flow reserve create \
    --instance-type 8xh100 \
    --region us-central1-b \
    --quantity 4 \
    --start +2h \
    --duration 12 \
    --name my-window

  # List reservations
  flow reserve list

  # Show details
  flow reserve show rsv_abc123

  # Explore availability and reserve the recommended slot (try --local-time)
  flow reserve availability \
    --instance-type 8xh100 \
    --region us-central1-b \
    --earliest now \
    --latest +12h \
    --qty 4 \
    --duration 6 \
    --local-time
  ```

## volumes

- Purpose: Manage persistent volumes
- Examples:
  ```
  # See `flow volumes --help` for full usage
  ```

## Telemetry (opt-in)

- Local metrics: set `FLOW_TELEMETRY=1` to write CLI usage events to `~/.flow/metrics.jsonl` (command name, success/failure, duration, timestamp). Never blocks or raises.
- Amplitude forwarding (optional): also set `FLOW_AMPLITUDE_API_KEY=<api-key>` to forward the same events asynchronously to Amplitude. Optionally override the endpoint with `FLOW_AMPLITUDE_URL` for testing.
- Identification: events use a random, anonymous `device_id` stored in `~/.flow/analytics_id` and do not include command arguments or secrets.
