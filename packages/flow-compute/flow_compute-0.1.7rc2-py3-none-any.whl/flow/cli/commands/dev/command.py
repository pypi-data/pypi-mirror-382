"""Dev command - persistent development VM with optional isolated environments.

Provides a persistent VM for development with two modes:

1. Default mode: Direct VM execution (no containers)
2. Named environments: Container-isolated environments for different projects
"""

from __future__ import annotations

import logging
import shlex
import time
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

import click

from flow import DEFAULT_ALLOCATION_ESTIMATED_SECONDS
from flow.application.config.manager import ConfigManager
from flow.cli.commands.base import BaseCommand, console
from flow.cli.commands.dev.executor import DevContainerExecutor
from flow.cli.commands.dev.instance_utils import equivalent_instance_types
from flow.cli.commands.dev.upload_manager import DevUploadManager
from flow.cli.commands.dev.utils import sanitize_env_name
from flow.cli.commands.dev.vm_manager import DevVMManager, VMStopStatus
from flow.cli.commands.utils import wait_for_task
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.ssh_helpers import SshStack
from flow.cli.utils.ssh_key_messages import print_no_ssh_keys_guidance
from flow.cli.utils.ssh_launch_keys import resolve_launch_ssh_keys
from flow.cli.utils.step_progress import (
    AllocationProgressAdapter,
    SSHWaitProgressAdapter,
    StepTimeline,
    build_allocation_hint,
    build_provisioning_hint,
)
from flow.cli.utils.volume_creation import create_volume_interactive
from flow.errors import AuthenticationError, FlowError, TaskNotFoundError, ValidationError
from flow.sdk.client import Flow
from flow.sdk.models import TaskStatus
from flow.sdk.ssh_utils import DEFAULT_PROVISION_MINUTES, SSHNotReadyError

logger = logging.getLogger(__name__)


class InstanceOption(TypedDict):
    """Type definition for instance option configuration."""

    display_name: str
    instance_type: str
    description: str


INSTANCE_OPTIONS: list[InstanceOption] = [
    {
        "display_name": "1x A100 80GB",
        "instance_type": "1xa100",
        "description": "Single-GPU development, debugging, and small experiments",
    },
    {
        "display_name": "8x H100 80GB",
        "instance_type": "8xh100",
        "description": "Multi-GPU development on a single node; scale up training and iteration speed",
    },
]


@dataclass
class DevVMSpec:
    """Specification for dev VM setup."""

    instance_type: str
    region: str
    volume: object | None = None


def _prompt_create_volume(flow_client, console, region: str | None = None) -> object | None:
    """Prompt user to optionally create a volume for the dev environment.

    This is a thin wrapper around create_volume_interactive specific to
    the dev command workflow.

    Args:
        flow_client: Flow SDK client
        console: Rich console for output
        region: Region for the volume (should match dev VM region)

    Returns:
        Created Volume object or None if user cancels/skips
    """

    # Dev-specific context messaging
    console.print("\n[bold]Add persistent storage (optional)[/bold]")
    console.print(
        "Each instance includes ephemeral storage by default (cleared when the VM reboots)."
    )
    console.print(
        "For datasets, model checkpoints, or experiment outputs that you want retained across sessions, "
    )
    console.print("attach a persistent volume.\n")
    console.print("Create one now, or mount it later.\n")

    # Ask if user wants to create a volume
    if not click.confirm("Would you like to create a storage volume?", default=True):
        return None

    return create_volume_interactive(
        flow_client,
        console,
        region=region,
        interface=None,  # Let user choose
        skip_confirmation=False,
        use_step_timeline=False,
        output_json=False,
    )


class DevCommand(BaseCommand):
    """Development environment command implementation."""

    @property
    def name(self) -> str:
        return "dev"

    @property
    def help(self) -> str:
        return "Persistent dev VM with isolated container environments"

    def _run_interactive_setup(self, force_new: bool = False) -> DevVMSpec | None:
        """Run interactive setup for first-time dev users.

        Args:
            force_new: If True, skip the existing VM check and always run setup

        Returns:
            DevVMSpec with instance_type, region, and optional volume, or None if skipped
        """
        # Check if this is first time setup (unless forcing new)
        config_mgr = ConfigManager()
        if not force_new:
            dev_task_id = config_mgr.get_dev_task_id()

            # Skip if dev VM already exists (we have a saved task_id)
            if dev_task_id:
                return None

        try:
            console.print("\n[bold]=== Development Workstation ===[/bold]")
            console.print("Persistent GPU VM (state preserved across sessions)")
            console.print("Ready for: iterative work, debugging, experimentation")
            console.print("-----------------------------------------------------")
            console.print("Configure your development VM before launch.\n")

            # Question 1: Instance type
            console.print("[bold]What instance type would you like?[/bold]")
            for i, option in enumerate(INSTANCE_OPTIONS, 1):
                console.print(f"  {i}. {option['display_name']} - {option['description']}")

            # Create choice mapping with indices
            index_choices = [str(i) for i in range(1, len(INSTANCE_OPTIONS) + 1)]
            choice = click.prompt(
                "\nChoose instance type",
                type=click.Choice(index_choices),
                default="1",
                show_default=True,
            )

            # Map choice back to instance option
            selected_option = INSTANCE_OPTIONS[int(choice) - 1]
            selected_instance = selected_option["instance_type"]
            selected_display_name = selected_option["display_name"]

            # Question 2: Region - use RegionSelector to find available regions
            console.print(
                f"\n[bold]Checking region availability for {selected_display_name}...[/bold]"
            )

            # Get available regions from RegionSelector
            available_regions = []
            flow_client = Flow()
            provider = flow_client.provider

            # Access RegionSelector from MithrilProvider context
            if not (hasattr(provider, "ctx") and hasattr(provider.ctx, "region")):
                raise RuntimeError(
                    "Provider context not available. Cannot determine region availability."
                )

            region_selector = provider.ctx.region
            instance_type_resolver = provider.ctx.instance_types

            # Resolve instance type to Mithril ID
            instance_fid = instance_type_resolver.resolve(selected_instance)

            # Check availability across regions
            availability = region_selector.check_availability(instance_fid)
            available_regions = list(availability.keys())

            if available_regions:
                console.print(
                    f"[green]Found {len(available_regions)} region(s) with availability[/green]\n"
                )
            else:
                console.print(
                    f"[yellow]No regions currently available for {selected_display_name}[/yellow]"
                )
                raise SystemExit(1)

            console.print("[bold]What region would you like?[/bold]")
            for i, region in enumerate(available_regions, 1):
                console.print(f"  {i}. {region}")

            # Create choice mapping with indices
            region_index_choices = [str(i) for i in range(1, len(available_regions) + 1)]
            choice = click.prompt(
                "\nChoose region",
                type=click.Choice(region_index_choices),
                default="1",
                show_default=True,
            )
            selected_region = available_regions[int(choice) - 1]

            # Optional: Prompt to create a volume
            created_volume = None
            # Use the Flow client we already created if available, otherwise create one
            vol_client = flow_client if "flow_client" in locals() else Flow()
            created_volume = _prompt_create_volume(vol_client, console, region=selected_region)

            # Note: We'll save the task_id after VM creation, not here
            return DevVMSpec(
                instance_type=selected_instance, region=selected_region, volume=created_volume
            )
        except (click.Abort, KeyboardInterrupt):
            console.print("\n[yellow]Setup cancelled[/yellow]")
            raise SystemExit(0)

    def get_command(self) -> click.Group:
        """Return the dev command group."""

        @click.group(
            name=self.name,
            help=self.help,
            invoke_without_command=True,
            context_settings={"ignore_unknown_options": True, "allow_interspersed_args": False},
        )
        @click.option(
            "--env",
            "-e",
            default="default",
            help="Environment: 'default' (VM) or named (container)",
        )
        @click.option(
            "--instance-type",
            "-i",
            help=(
                "Instance type for dev VM (e.g., a100, h100). If an existing dev VM"
                " has a different instance type, a new dev VM is created instead of reusing."
            ),
        )
        @click.option(
            "--region", "-r", help="Preferred region for the dev VM (e.g., us-central1-b)"
        )
        @click.option("--image", help="Docker image for container execution")
        @click.option(
            "--ssh-keys",
            "-k",
            multiple=True,
            help=(
                "Authorized SSH keys (repeatable). Accepts: platform key ID like 'sshkey_ABC123', "
                "a local private key path like '~/.ssh/id_ed25519', or a key name like 'id_ed25519'. "
                "Repeat -k/--ssh-keys for multiple values. Example: "
                "-k ~/.ssh/id_ed25519 -k sshkey_ABC123 -k work_laptop"
            ),
        )
        @click.option("--force-new", is_flag=True, help="Force creation of new dev VM")
        @click.option("--max-price-per-hour", "-m", type=float, help="Maximum hourly price in USD")
        @click.option(
            "--upload/--no-upload",
            default=True,
            help="Upload current directory to VM (default: upload)",
        )
        @click.option(
            "--upload-path", default=".", help="Path to upload (default: current directory)"
        )
        @click.option(
            "--no-unique", is_flag=True, help="Don't append unique suffix to VM name on conflict"
        )
        @click.option(
            "--flat/--nested",
            "flat",
            default=False,
            help=(
                "Place current dir contents directly into parent (flat). Default uploads into '~/<dir>'."
            ),
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed examples and workflows")
        @click.pass_context
        @cli_error_guard(self)
        def dev_group(
            ctx: click.Context,
            env: str,
            instance_type: str | None,
            region: str | None,
            image: str | None,
            ssh_keys: tuple,
            force_new: bool,
            max_price_per_hour: float | None,
            upload: bool,
            upload_path: str,
            flat: bool,
            no_unique: bool,
            verbose: bool,
        ) -> None:
            """Persistent dev VM - upload code and SSH into VM.

            \b
            Examples:
                flow dev                         # SSH into VM
                flow dev -- nvidia-smi           # Run command on VM
                flow dev stop                    # Stop the VM
                flow dev info                    # Show VM status
            """
            # Skip execution during help/resilient parsing
            if ctx.resilient_parsing:
                return

            # If a subcommand was invoked, don't run the main logic
            if ctx.invoked_subcommand is not None:
                return

            # No subcommand - run default behavior (SSH/upload)
            if verbose:
                console.print("\n[bold]Flow Dev - Architecture & Usage:[/bold]\n")
                console.print("[underline]Two Modes:[/underline]")
                console.print("1. DEFAULT: Direct VM execution (no containers)")
                console.print("   • Commands run directly on persistent VM")
                console.print("   • Packages install to /root")
                console.print("   • Zero overhead, maximum speed")
                console.print("   • Like SSH but with auto code upload\n")
                console.print("2. NAMED ENVS: Container isolation")
                console.print("   • Each env gets isolated container")
                console.print("   • Packages install to /envs/NAME")
                console.print("   • Clean separation between projects")
                console.print("   • Read-only access to /root as /shared\n")
                console.print("[underline]Examples:[/underline]")
                console.print("# Default environment (direct VM):")
                console.print("flow dev                            # SSH to VM")
                console.print("flow dev -- pip install numpy       # Install on VM")
                console.print("flow dev -- python train.py         # Uses numpy")
                console.print("flow dev -- nvidia-smi              # Check GPUs\n")
                console.print("# Named environments (containers):")
                console.print("flow dev -e ml -- pip install tensorflow")
                console.print("flow dev -e web -- npm install express")
                console.print("flow dev -e ml -- python app.py    # Has TF, not express\n")
                console.print("# Management:")
                console.print("flow dev info                      # Check VM & environments")
                console.print("flow dev stop                      # Stop VM completely\n")
                console.print("[underline]File Structure:[/underline]")
                console.print("/root/           # Default env & shared data")
                console.print("/envs/ml/        # Named env 'ml'")
                console.print("/envs/web/       # Named env 'web'\n")
                console.print("[underline]Key Points:[/underline]")
                console.print("• Code auto-uploads on each run (rsync - only changes)")
                console.print(
                    "• Code sync is owned by CLI; provider background uploads are disabled for dev VMs"
                )
                console.print("• VM persists until you --stop")
                console.print("• Default env = your persistent workspace")
                console.print("• Named envs = isolated project spaces\n")
                return

            # Parse command from remaining args (after --)
            command = None
            if ctx.args:
                command = " ".join(ctx.args)

            self._execute(
                command=command,
                env_name=env,
                instance_type=instance_type,
                region=region,
                image=image,
                ssh_keys=ssh_keys,
                reset=False,
                stop=False,
                status=False,
                force_new=force_new,
                max_price_per_hour=max_price_per_hour,
                upload=upload,
                upload_path=upload_path,
                flat=flat,
                no_unique=no_unique,
                output_json=False,
            )

        # Add management subcommands
        dev_group.add_command(self._stop_command())
        dev_group.add_command(self._info_command())
        dev_group.add_command(self._reset_command())

        return dev_group

    def _stop_command(self) -> click.Command:
        """Create the stop subcommand."""

        @click.command(name="stop", help="Pause the dev VM (preserves boot disk)")
        @cli_error_guard(self)
        def stop():
            """Pause the current user's dev VM.

            Pauses the VM (preserving state for quick resume) regardless of whether
            it's running, pending, or provisioning. Use 'flow cancel <task-id>' to
            fully terminate a VM.
            """
            flow_client = Flow()
            vm_manager = DevVMManager(flow_client)

            with AnimatedEllipsisProgress(console, "Pausing dev VM", start_immediately=True):
                status = vm_manager.stop_dev_vm()
                if status == VMStopStatus.PAUSED:
                    console.print("[success]✓[/success] Dev VM paused")
                elif status == VMStopStatus.ALREADY_PAUSED:
                    console.print("[info]ℹ[/info] Dev VM is already paused")
                elif status == VMStopStatus.TERMINAL:
                    console.print(
                        "[warning]Dev VM is in terminal state and cannot be paused[/warning]"
                    )
                else:  # VMStopStatus.NOT_FOUND
                    console.print("[warning]No active dev VM found[/warning]")

        return stop

    def _info_command(self) -> click.Command:
        """Create the info subcommand - delegates to flow status."""

        @click.command(name="info", help="Show dev environment status")
        @click.pass_context
        @cli_error_guard(self)
        def info(ctx: click.Context):
            """Show detailed information about the dev VM - delegates to flow status."""
            flow_client = Flow()
            vm_manager = DevVMManager(flow_client)

            # Find the dev VM
            vm = vm_manager.find_dev_vm(include_not_ready=True)
            if not vm:
                console.print("[warning]No dev VM available[/warning]")
                console.print("\nStart a dev VM with: [accent]flow dev[/accent]")
                return

            # Import and invoke the status command with the dev VM's task ID
            try:
                from flow.cli.commands.status import command as status_command

                status_cmd = status_command.get_command()
                # Invoke status with the dev VM's task ID
                ctx.invoke(status_cmd, task_identifier=vm.task_id)
            except Exception as e:
                console.print(f"[red]Error showing dev VM status: {e}[/red]")
                raise

        return info

    def _reset_command(self) -> click.Command:
        """Create the reset subcommand."""

        @click.command(name="reset", help="Reset all dev containers")
        @cli_error_guard(self)
        def reset():
            """Reset all containers in the dev VM."""
            flow_client = Flow()
            vm_manager = DevVMManager(flow_client)

            # Find the VM
            vm = vm_manager.find_dev_vm()
            if not vm:
                console.print("[warning]No dev VM found[/warning]")
                console.print("\nStart a dev VM with: [accent]flow dev ssh[/accent]")
                return

            executor = DevContainerExecutor(flow_client, vm)
            with AnimatedEllipsisProgress(
                console, "Resetting all dev containers", start_immediately=True
            ):
                executor.reset_containers()
            console.print("[bold green]✓[/bold green] Containers reset successfully")

        return reset

    def _execute(
        self,
        command: str | None,
        env_name: str,
        instance_type: str | None,
        region: str | None,
        image: str | None,
        ssh_keys: tuple,
        reset: bool,
        stop: bool,
        status: bool,
        force_new: bool,
        max_price_per_hour: float | None,
        upload: bool,
        upload_path: str,
        flat: bool,
        no_unique: bool,
        output_json: bool,
    ) -> None:
        progress = None
        printed_existing_msg = False

        initial_msg = "Starting flow dev"
        if command:
            cmd_preview = command if len(command) <= 30 else command[:27] + "..."
            initial_msg = f"Preparing to run: {cmd_preview}"
        progress = AnimatedEllipsisProgress(
            console, initial_msg, transient=True, start_immediately=True
        )

        try:
            # Skip interactive setup when --help is requested
            ctx = click.get_current_context()
            in_help_mode = ctx.resilient_parsing

            flow_client = Flow()
            vm_manager = DevVMManager(flow_client)

            # Interactive setup for first-time users or when --force-new is used
            setup_volume = None
            vm = None
            timeline = None
            ran_interactive_setup = False

            should_run_setup = not in_help_mode and (
                (not instance_type and not region) or (force_new and not (instance_type and region))
            )

            # Check for existing VM before prompting user with interactive setup
            if should_run_setup and not force_new:
                if progress:
                    progress.__exit__(None, None, None)
                    progress = None

                timeline = StepTimeline(console, title_animation="auto")
                timeline.start()
                timeline.reserve_total(4)
                step_idx = timeline.add_step("Checking for existing dev VM", show_bar=False)
                timeline.start_step(step_idx)

                try:
                    vm = vm_manager.find_dev_vm(include_not_ready=True)
                    if vm:
                        # Found existing VM - skip setup and continue with this VM
                        should_run_setup = False
                        timeline.complete_step(f"found: {vm.name or ':dev'}")
                    else:
                        timeline.complete_step("none found")
                except Exception:  # noqa: BLE001
                    timeline.complete_step("check failed")

                if should_run_setup:
                    # No existing VM - run interactive setup
                    timeline.finish()
                    timeline = None  # Will start fresh after setup

            # Run interactive setup if needed
            if should_run_setup:
                if progress:
                    progress.__exit__(None, None, None)
                    progress = None

                setup_result = self._run_interactive_setup(force_new=force_new)
                if setup_result:
                    instance_type = setup_result.instance_type
                    region = setup_result.region
                    setup_volume = setup_result.volume
                    ran_interactive_setup = True

            # Load dev configuration to get saved task_id (used by find_dev_vm)
            # Instance type and region come from CLI args or interactive setup, not config
            config_volume = None

            # SSH keys preflight: unify with flow ssh behavior via shared helper.
            try:
                effective_keys = resolve_launch_ssh_keys(flow_client, ssh_keys)
            except Exception:  # noqa: BLE001
                # Fallback: treat CLI tuple directly to avoid blocking execution
                effective_keys = list(ssh_keys) if ssh_keys else []

            if not effective_keys:
                print_no_ssh_keys_guidance("for dev VM", level="error")
                raise SystemExit(1)
            else:
                keys_preview = ", ".join(effective_keys[:3])
                if len(effective_keys) > 3:
                    keys_preview += f" (+{len(effective_keys) - 3} more)"
                console.print(f"[dim]Using SSH keys:[/dim] {keys_preview}")

            # Start main timeline if not already started
            if progress:
                progress.__exit__(None, None, None)
                progress = None

            if timeline is None:
                timeline = StepTimeline(console, title_animation="auto")
                timeline.start()
                timeline.reserve_total(4)

            # Look up dev VM if we don't already have one
            # Skip the lookup if we just ran interactive setup (we already checked and found no VM)
            if vm is None and not ran_interactive_setup:
                step_idx_lookup = timeline.add_step("Checking for existing dev VM", show_bar=False)
                timeline.start_step(step_idx_lookup)

                vm = vm_manager.find_dev_vm(
                    include_not_ready=True, region=region, desired_instance_type=instance_type
                )

                if vm is None:
                    timeline.complete_step("no VM")
                else:
                    vm_name = getattr(vm, "name", None) or ":dev"
                    if getattr(vm, "ssh_host", None):
                        timeline.complete_step(f"found: {vm_name}")
                    else:
                        timeline.complete_step(f"found: {vm_name} (provisioning)")

            # If a different-shape dev VM exists and a specific instance type was requested,
            # note it for messaging and (optionally) stopping when --force-new is set.
            existing_any_vm = None
            if instance_type:
                existing_any_vm = vm_manager.find_dev_vm(include_not_ready=True, region=region)
                if existing_any_vm and not vm:
                    existing_type = getattr(existing_any_vm, "instance_type", None)
                    # Compare instance types using utility function
                    if existing_type and not equivalent_instance_types(
                        existing_type, instance_type, flow_client
                    ):
                        console.print(
                            f"Existing dev VM has instance '{existing_type}', requested '{instance_type}'. Creating a new dev VM."
                        )

            # Handle force_new - stop and clear VM (will create new one below)
            if force_new and (vm or existing_any_vm):
                # Clear any pending output before starting progress indicator
                console.print()  # Add a blank line for separation

                # Temporarily pause timeline to avoid interference with AnimatedEllipsisProgress
                timeline_was_active = timeline is not None
                if timeline_was_active:
                    timeline.finish()
                    timeline = None

                with AnimatedEllipsisProgress(
                    console, "Force stopping existing dev VM", start_immediately=True
                ):
                    vm_manager.stop_dev_vm()  # Ignore return value for force_new
                    vm = None

                # Restart timeline if it was active
                if timeline_was_active:
                    timeline = StepTimeline(console, title_animation="auto")
                    timeline.start()
                    timeline.reserve_total(4)

            # If we have a VM and it's paused, unpause it
            elif vm and vm.status == TaskStatus.PAUSED:
                step_idx_unpause = timeline.add_step("Resuming paused dev VM", show_bar=False)
                timeline.start_step(step_idx_unpause)
                vm_manager.unpause_task(vm.task_id)
                timeline.complete_step("resumed")

            # Wait for provisioning if necessary
            if vm and not vm.ssh_host:
                try:
                    # Quick step to cover endpoint resolution/API refresh which can take a moment
                    step_idx_prepare = timeline.add_step("Preparing SSH endpoint", show_bar=False)
                    timeline.start_step(step_idx_prepare)

                    # Fast-path: refresh single task to populate SSH fields (list() may omit)
                    with suppress(FlowError):
                        vm_ref = flow_client.get_task(vm.task_id)
                        if getattr(vm_ref, "ssh_host", None):
                            vm = vm_ref

                    # Fast-path 2: directly resolve endpoint via provider
                    if not getattr(vm, "ssh_host", None):
                        try:
                            host, port = flow_client.resolve_ssh_endpoint(vm.task_id)
                            if host:
                                vm.ssh_host = host
                                vm.ssh_port = port
                        except (FlowError, AttributeError, ValueError):
                            pass

                    # Close the quick prepare step with a succinct note
                    if getattr(vm, "ssh_host", None):
                        timeline.complete_step("resolved")
                    else:
                        timeline.complete_step("waiting")

                    try:
                        baseline = int(getattr(vm, "instance_age_seconds", 0) or 0)
                    except (TypeError, ValueError):
                        baseline = 0

                    if not getattr(vm, "ssh_host", None):
                        # Use the standard provisioning window (~20m)
                        step_idx_provision = timeline.add_step(
                            f"Provisioning instance (up to {DEFAULT_PROVISION_MINUTES}m)",
                            show_bar=True,
                            estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
                            baseline_elapsed_seconds=baseline,
                        )
                        ssh_adapter = SSHWaitProgressAdapter(
                            timeline,
                            step_idx_provision,
                            DEFAULT_PROVISION_MINUTES * 60,
                            baseline_elapsed_seconds=baseline,
                        )
                        in_ssh_wait = True
                        with ssh_adapter:
                            hint = build_provisioning_hint("VM", "flow dev")
                            with suppress(Exception):
                                timeline.set_active_hint_text(hint)
                            if getattr(flow_client.config, "provider", "") == "mock":
                                time.sleep(1.0)
                                vm = flow_client.get_task(vm.task_id)
                            else:
                                try:
                                    vm = flow_client.wait_for_ssh(
                                        task_id=vm.task_id,
                                        timeout=DEFAULT_PROVISION_MINUTES * 60,
                                        show_progress=False,
                                        progress_adapter=ssh_adapter,
                                    )
                                except (SSHNotReadyError, KeyboardInterrupt):
                                    timeline.finish()
                                    console.print("\n[accent]✗ SSH wait interrupted[/accent]")
                                    console.print(
                                        "\nThe dev VM should still be provisioning. You can check later with:"
                                    )
                                    console.print("  [accent]flow dev[/accent]")
                                    console.print(
                                        f"  [accent]flow status {vm.name or vm.task_id}[/accent]"
                                    )
                                    raise SystemExit(1)
                        in_ssh_wait = False
                        # If endpoint is already available at this point, give a tiny nudge of feedback
                        with suppress(FlowError):
                            ssh_key_path = flow_client.get_task_ssh_connection_info(vm.task_id)
                            if isinstance(ssh_key_path, Path) and getattr(vm, "ssh_host", None):
                                start_wait = time.time()
                                while not SshStack.is_ssh_ready(
                                    user=getattr(vm, "ssh_user", "ubuntu"),
                                    host=vm.ssh_host,
                                    port=getattr(vm, "ssh_port", 22),
                                    key_path=ssh_key_path,
                                ):
                                    if time.time() - start_wait > 90:
                                        break
                                    with suppress(Exception):  # UI nicety only
                                        ssh_adapter.update_eta()
                                    time.sleep(1)
                    else:
                        # Endpoint is already available; provide a concise confirmation
                        vm_name = getattr(vm, "name", None) or ":dev"
                        console.print(f"Using existing dev VM: {vm_name}")
                        printed_existing_msg = True
                        if progress:
                            progress.update_message(f"Using existing dev VM: {vm.name}")
                            progress.__exit__(None, None, None)
                            progress = None
                except Exception as e:
                    timeline.fail_step(str(e))
                    raise

            config_mgr = ConfigManager()
            # Track whether we're creating a new VM (vs reusing existing)
            creating_new_vm = vm is None
            if not vm:
                # Dev VM creation proceeds without the global real-provider guard
                # to keep the flow streamlined. The starters command handles
                # user confirmation for billable launches.

                # Show a lightweight spinner while we submit the allocation request.
                # This avoids a perceived "hang" between discovery and allocation steps.
                step_idx_request = timeline.add_step(
                    "Submitting allocation request", show_bar=False
                )
                timeline.start_step(step_idx_request)
                try:
                    # Use setup_volume from interactive setup
                    vm = vm_manager.create_dev_vm(
                        instance_type=instance_type,
                        region=region,
                        ssh_keys=effective_keys,
                        max_price_per_hour=max_price_per_hour,
                        no_unique=no_unique,
                        volume=setup_volume,
                    )

                    # Save the task_id for future runs
                    try:
                        config_mgr.set_dev_task_id(task_id=vm.task_id)
                        logger.debug(f"Saved dev VM task_id: {vm.task_id}")
                    except Exception as e:  # noqa: BLE001
                        logger.debug(f"Could not save dev task_id: {e}")

                    timeline.complete_step("submitted")
                except Exception as e:
                    # Mark the step as failed with a concise message, then re-raise
                    timeline.fail_step(str(e))
                    raise

                step_idx_allocate = timeline.add_step(
                    "Allocating instance",
                    show_bar=True,
                    estimated_seconds=DEFAULT_ALLOCATION_ESTIMATED_SECONDS,
                )
                alloc_adapter = AllocationProgressAdapter(
                    timeline,
                    step_idx_allocate,
                    estimated_seconds=DEFAULT_ALLOCATION_ESTIMATED_SECONDS,
                )
                with alloc_adapter:
                    # Provide a standardized allocation hint
                    timeline.set_active_hint_text(
                        build_allocation_hint("flow dev", subject="allocation")
                    )
                    final_status = wait_for_task(
                        flow_client,
                        vm.task_id,
                        watch=False,
                        task_name=vm.name,
                        show_submission_message=False,
                        progress_adapter=alloc_adapter,
                    )
                if final_status != "running":
                    task = flow_client.get_task(vm.task_id)
                    msg = getattr(task, "message", None) or f"status: {final_status}"
                    timeline.steps[step_idx_allocate].note = msg
                    timeline.fail_step("Allocation did not reach running state")

                    # Surface the error to the user before cancelling
                    error_details = f"Dev VM allocation failed with status: {final_status}"
                    try:
                        task = flow_client.get_task(vm.task_id)
                        if hasattr(task, "message") and task.message:
                            error_details = f"{error_details}\nDetails: {task.message}"
                    except Exception:  # noqa: BLE001
                        pass

                    # Only cancel if the task is truly stuck/failed (not just pending)
                    # Pending tasks may still be waiting for capacity
                    if final_status not in ["pending", "preparing"]:
                        console.print(f"[warning]{error_details}[/warning]")
                        console.print("[dim]Cancelling failed allocation...[/dim]")
                        try:
                            flow_client.cancel(vm.task_id)
                        except Exception as cancel_err:  # noqa: BLE001
                            console.print(f"[dim]Note: Failed to cancel task: {cancel_err}[/dim]")

                        # Raise FlowError with detailed information and suggestions
                        raise FlowError(
                            f"Allocation failed: {error_details}",
                            suggestions=[
                                "Check task status with: flow status " + vm.task_id,
                                "View logs with: flow logs " + vm.task_id,
                                "Try a different region or instance type",
                            ],
                        )
                    else:
                        # Task is still pending - don't cancel, just inform user and raise error
                        console.print(f"[warning]{error_details}[/warning]")
                        console.print(
                            f"\n[accent]The dev VM ({vm.name or vm.task_id}) is still pending allocation.[/accent]"
                        )
                        console.print("You can check status with:")
                        console.print(f"  [accent]flow status {vm.name or vm.task_id}[/accent]")
                        console.print("Or cancel it with:")
                        console.print(f"  [accent]flow cancel {vm.name or vm.task_id}[/accent]")

                baseline = 0
                try:
                    baseline = int(getattr(vm, "instance_age_seconds", None) or 0)
                except Exception:  # noqa: BLE001
                    baseline = 0
                # Use the standard provisioning window (~20m)
                step_idx_provision = timeline.add_step(
                    f"Provisioning instance (up to {DEFAULT_PROVISION_MINUTES}m)",
                    show_bar=True,
                    estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
                    baseline_elapsed_seconds=baseline,
                )
                ssh_adapter = SSHWaitProgressAdapter(
                    timeline,
                    step_idx_provision,
                    DEFAULT_PROVISION_MINUTES * 60,
                    baseline_elapsed_seconds=baseline,
                )
                in_ssh_wait = True
                with ssh_adapter:
                    timeline.set_active_hint_text(build_provisioning_hint("VM", "flow dev"))
                    if getattr(flow_client.config, "provider", "") == "mock":
                        time.sleep(1.0)
                        vm = flow_client.get_task(vm.task_id)
                    else:
                        try:
                            vm = flow_client.wait_for_ssh(
                                task_id=vm.task_id,
                                timeout=DEFAULT_PROVISION_MINUTES * 60,
                                show_progress=False,
                                progress_adapter=ssh_adapter,
                            )
                        except (SSHNotReadyError, KeyboardInterrupt):
                            timeline.finish()
                            console.print("\n[accent]✗ SSH wait interrupted[/accent]")
                            console.print(
                                "\nThe dev VM should still be provisioning. You can check later with:"
                            )
                            console.print("  [accent]flow dev[/accent]")
                            console.print(f"  [accent]flow status {vm.name or vm.task_id}[/accent]")
                            raise SystemExit(1)
                    # Keep the provisioning step active until an initial SSH handshake succeeds
                    # to avoid advancing to code-sync while the host isn't actually reachable yet.
                    ssh_key_path = flow_client.get_task_ssh_connection_info(vm.task_id)
                    if isinstance(ssh_key_path, Path) and getattr(vm, "ssh_host", None):
                        start_wait = time.time()
                        # Bound the stabilization window to avoid masking truly slow boots
                        max_wait = 120  # seconds
                        while not SshStack.is_ssh_ready(
                            user=getattr(vm, "ssh_user", "ubuntu"),
                            host=vm.ssh_host,
                            port=getattr(vm, "ssh_port", 22),
                            key_path=ssh_key_path,
                        ):
                            if time.time() - start_wait > max_wait:
                                break
                            ssh_adapter.update_eta()
                            time.sleep(1)
                    in_ssh_wait = False
            else:
                if progress:
                    progress.update_message(f"Using existing dev VM: {vm.name}")
                    progress.__exit__(None, None, None)
                    progress = None
                # Avoid duplicate prints if we already confirmed earlier
                if not printed_existing_msg:
                    console.print(f"Using existing dev VM: {vm.name}")

                # Save the task_id when reusing an existing VM too
                config_mgr.set_dev_task_id(task_id=vm.task_id)
                logger.debug(f"Saved existing dev VM task_id: {vm.task_id}")

            # Normalize env name early to avoid leaky path formation and double slashes
            sanitized_env = sanitize_env_name(env_name)

            # Upload code
            workdir_for_command: str | None = None
            if upload:
                upload_manager = DevUploadManager(
                    flow_client, vm, timeline, upload_mode=("flat" if flat else "nested")
                )
                # Refresh VM task to get latest SSH endpoint info for upload
                if getattr(vm, "ssh_host", None):
                    step_idx_prepare = timeline.add_step("Preparing SSH endpoint", show_bar=False)
                    timeline.start_step(step_idx_prepare)
                    # Get the latest task view to reflect any endpoint changes
                    provider = flow_client.get_remote_operations().provider  # type: ignore[attr-defined]
                    vm = provider.get_task(vm.task_id)
                    timeline.complete_step(note="ready")

                vm_dir, container_dir = upload_manager.upload(upload_path, sanitized_env)
                workdir_for_command = container_dir if sanitized_env != "default" else vm_dir

            executor = DevContainerExecutor(flow_client, vm)

            if command:
                interactive_commands = [
                    "bash",
                    "sh",
                    "zsh",
                    "fish",
                    "python",
                    "ipython",
                    "irb",
                    "node",
                ]
                original_command = command
                is_interactive = original_command.strip() in interactive_commands
                # If we performed an upload and resolved a working directory, run the command from there
                if workdir_for_command:
                    # Use $HOME for any leading '~' so expansion still occurs when quoted
                    wd = workdir_for_command
                    if wd == "~":
                        wd_expr = '"$HOME"'
                    elif wd.startswith("~/"):
                        # Preserve the remainder and allow HOME expansion; quote for spaces
                        remainder = wd[2:]
                        # Double-quote the argument so spaces are safe
                        wd_expr = '"$HOME/' + remainder.replace('"', '\\"') + '"'
                    else:
                        # Safe path without HOME expansion
                        wd_expr = shlex.quote(wd)
                    command = f"cd {wd_expr} && {original_command}"
                else:
                    command = original_command

                if progress:
                    progress.update_message("Preparing container environment")
                    time.sleep(0.3)
                    progress.__exit__(None, None, None)
                    progress = None

                # Close the step timeline before attaching or running commands to avoid UI overlap
                timeline.finish()

                if is_interactive:
                    console.print(f"Starting interactive session: {original_command}")
                else:
                    console.print(f"Executing: {original_command}")

                exit_code = executor.execute_command(
                    command, image=image, interactive=is_interactive, env_name=sanitized_env
                )

                if exit_code != 0 and not is_interactive:
                    raise SystemExit(exit_code)
            else:
                if sanitized_env != "default":
                    console.print(f"[dim]Connecting to environment '{sanitized_env}'[/dim]")
                else:
                    console.print(
                        "[dim]Once connected, you'll have a persistent Ubuntu environment[/dim]"
                    )

                if sanitized_env != "default":
                    env_dir = f"/envs/{sanitized_env}"
                    remote_ops = flow_client.get_remote_operations()
                    setup_cmd = f"mkdir -p {env_dir}"
                    remote_ops.execute_command(vm.task_id, setup_cmd)

                timeline.finish()

                shell_cmd = None
                if sanitized_env != "default":
                    shell_cmd = f'bash -lc "mkdir -p /envs/{sanitized_env} && cd /envs/{sanitized_env} && exec bash -l"'
                else:
                    # If we uploaded code and resolved a working directory, start the shell there
                    if upload and "vm_dir" in locals() and vm_dir:
                        # Build a robust cd target: convert leading '~' to $HOME and quote for spaces
                        wd = vm_dir
                        if wd == "~":
                            path_expr = "$HOME"
                        elif wd.startswith("~/"):
                            path_expr = "$HOME/" + wd[2:].replace('"', '\\"')
                        else:
                            path_expr = wd.replace('"', '\\"')
                        # Wrap the path in double-quotes inside the bash -lc string (escape quotes)
                        shell_cmd = f'bash -lc "cd "{path_expr}" && exec bash -l"'

                # Use provider remote operations directly to avoid relying on Task._provider
                try:
                    remote_ops = flow_client.get_remote_operations()
                except NotImplementedError:
                    remote_ops = None
                if not remote_ops:
                    raise FlowError(
                        "Provider does not support shell access",
                        suggestions=[
                            "This provider does not support remote shell access",
                            "Use a provider that implements remote operations",
                            "Check provider documentation for supported features",
                        ],
                    )

                remote_ops.open_shell(
                    vm.task_id, command=shell_cmd, node=None, progress_context=None, record=False
                )

            # Next actions hints
            if not command or command in [
                "bash",
                "sh",
                "zsh",
                "fish",
                "python",
                "ipython",
                "irb",
                "node",
            ]:
                if env_name == "default":
                    self.show_next_actions(
                        [
                            "Run a command on your VM: [accent]flow dev -- python <your_script>.py[/accent]",
                            "Create an isolated env: [accent]flow dev -e <env-name> -- pip install <deps>[/accent]",
                            "Check dev VM status: [accent]flow dev info[/accent]",
                        ]
                    )
                else:
                    self.show_next_actions(
                        [
                            f"Work in {env_name}: [accent]flow dev -e {env_name} -- python <your_script>.py[/accent]",
                            "Switch to default: [accent]flow dev -- python <your_script>.py[/accent]",
                            "Check environments: [accent]flow dev info[/accent]",
                        ]
                    )

        except AuthenticationError:
            if timeline is not None:
                timeline.finish()
            self.handle_auth_error()
        except TaskNotFoundError as e:
            if timeline is not None:
                timeline.finish()
            self.handle_error(f"Dev VM not found: {e}")
        except ValidationError as e:
            if timeline is not None:
                timeline.finish()
            self.handle_error(f"Invalid configuration: {e}")
        except KeyboardInterrupt:
            # If interrupted while waiting for SSH, show context-aware hint
            in_wait = bool(locals().get("in_ssh_wait", False))
            if in_wait:
                if timeline is not None:
                    timeline.finish()
                console.print("\n[accent]✗ SSH wait interrupted[/accent]")
                console.print(
                    "\nThe dev VM should still be provisioning. You can check later with:"
                )
                vm_name = (vm.name if vm else None) or ":dev"
                console.print("  [accent]flow dev[/accent]")
                console.print(f"  [accent]flow status {vm_name}[/accent]")
            else:
                console.print("\n[warning]Operation cancelled by user[/warning]")
            raise SystemExit(1)
        except Exception as e:  # noqa: BLE001
            # Finish timeline before displaying error to prevent screen overwrites
            if timeline is not None:
                try:
                    timeline.finish()
                except Exception:  # noqa: BLE001
                    pass

            # Log exception details for debugging
            logger.debug(f"Exception type: {type(e).__name__}")
            logger.debug(f"Exception message: {e!s}")
            logger.debug(f"Exception repr: {e!r}")

            error_msg = str(e)
            if not error_msg:
                # Exception has no message - show type and repr
                error_msg = f"{type(e).__name__}: {e!r}"

            if "connection refused" in error_msg.lower():
                self.handle_error(
                    "Cannot connect to Docker daemon. Ensure Docker is installed and running on the dev VM.\n"
                    "You may need to SSH into the VM and install Docker: [accent]flow dev[/accent]"
                )
            elif "no such image" in error_msg.lower():
                self.handle_error(
                    f"Docker image not found: {image or 'default'}\n"
                    "The image will be pulled automatically on first use."
                )
            else:
                self.handle_error(error_msg)
        finally:
            # Always finish timeline on exit
            if timeline is not None:
                try:
                    timeline.finish()
                except Exception as finish_error:  # noqa: BLE001
                    # Don't let timeline cleanup swallow the original exception
                    logger.error(f"Error finishing timeline: {finish_error}")


# Export command instance
command = DevCommand()
