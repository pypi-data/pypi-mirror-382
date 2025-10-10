"""Ask command for Flow CLI.

Calls the Mithril Wizard backend (/v2/wizard/ask) which performs server-side reasoning
over live market data and returns recommendations.

Examples:
    flow ask "What are the cheapest H100 instances available?"
    flow ask "Show me all active auctions for A100 GPUs"
    flow ask "What regions have the best pricing for spot instances?"

No Anthropic API key required - the server performs model inference.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from typing import Any

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.theme_manager import theme_manager


class AskCommand(BaseCommand):
    """Ask questions about Mithril marketplace via Wizard."""

    @property
    def name(self) -> str:
        return "ask"

    @property
    def help(self) -> str:
        return "Ask questions about the Mithril marketplace via Wizard backend."

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.argument("question", required=True)
        @click.option(
            "--verbose",
            is_flag=True,
            help="Show detailed execution information",
        )
        @click.option(
            "--json",
            "output_json",
            is_flag=True,
            help="Output response as JSON",
        )
        def ask_command(
            question: str,
            verbose: bool,
            output_json: bool,
        ) -> None:
            """Ask a question using the Mithril Wizard backend."""
            try:
                # Use the proper SDK client
                import flow.sdk.factory as sdk_factory

                if verbose:
                    console.print("[dim]Initializing Flow client...[/dim]")

                client = sdk_factory.create_client(auto_init=True)

                # Show loading animation while waiting for response
                from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console, "Asking Mithril Agent", start_immediately=True
                ):
                    data = client.ask_wizard(question=question)

                # Build next actions from structured recs (if present)
                recs = data.get("recommendations") or []
                next_actions = self._build_next_actions(recs)

                if output_json:
                    enriched = {**data, "next_actions": next_actions}
                    console.print(json.dumps(enriched, indent=2))
                    return

                content = data.get("content", "")
                accent = theme_manager.get_color("accent")
                console.print(f"\n[{accent}]Mithril Agent Response:[/{accent}]")
                console.print(content or "[yellow]No content[/yellow]")

                if recs:
                    console.print("\nRecommendations:")
                    for r in recs:
                        price = r.get("price", 0) or 0
                        price_dollars = (price or 0) / 100.0
                        inst = r.get("instanceType", "Unknown")
                        qty = r.get("quantity", 0)
                        rtype = (r.get("type", "") or "").upper()
                        region = r.get("region", "Unknown")
                        console.print(
                            f" - {inst} × {qty} · {rtype} · {region} · ${price_dollars:.2f}/hr"
                        )

                if next_actions:
                    console.print("\nNext steps (copy/paste):")
                    for a in next_actions:
                        console.print(f"  $ {a['cmd']}")
                    # Offer interactive menu if in TTY
                    try:
                        if sys.stdin.isatty() and sys.stdout.isatty():
                            self._present_actions_interactive(next_actions)
                    except Exception:  # noqa: BLE001
                        pass

            except Exception as e:  # noqa: BLE001
                self.handle_error(f"Failed to process request: {e}")

        return ask_command

    def _normalize_gpu_token(self, instance_type_name: str) -> str:
        """Best-effort normalization from 'H100-80GB' -> 'h100', 'A100' -> 'a100', 'L40S' -> 'l40s'."""
        if not instance_type_name:
            return ""
        upper = instance_type_name.upper()
        for token in ["H100", "A100", "V100", "L40S", "L40", "A10", "A30", "T4", "L4"]:
            if token in upper:
                return token.lower()
        # Fallback: alphanum prefix
        out = []
        for ch in upper:
            if ch.isalnum():
                out.append(ch)
            elif out:
                break
        return ("".join(out) or upper).lower()

    def _build_next_actions(self, recs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Build suggested CLI commands from structured recommendations."""
        actions: list[dict[str, Any]] = []
        for rec in recs or []:
            try:
                r_type = (rec.get("type") or "spot").lower()
                instance_type = rec.get("instanceType") or ""
                region = rec.get("region") or ""
                qty = int(rec.get("quantity") or 1)
                duration = rec.get("duration")  # hours for reserved
                price_cents = int(rec.get("price") or 0)
                price_dollars = price_cents / 100.0 if price_cents else None
                cfg = rec.get("config") or {}
                region_id = cfg.get("regionId") or cfg.get("clusterId") or ""
                instance_type_id = cfg.get("instanceTypeId") or ""

                gpu_token = self._normalize_gpu_token(instance_type)

                # Prefer a grab command for spot
                if r_type == "spot":
                    # Omit --max-price to avoid per-GPU vs per-instance ambiguity
                    cmd = f"flow grab {qty} {gpu_token}".strip()
                    if region:
                        cmd += f' --region "{region}"'
                    actions.append(
                        {
                            "kind": "grab",
                            "cmd": cmd,
                            "notes": "Interactive spot capacity",
                            "instanceType": instance_type,
                            "region": region,
                            "quantity": qty,
                            "priceDollarsPerHour": price_dollars,
                            "regionId": region_id,
                            "instanceTypeId": instance_type_id,
                        }
                    )
                else:
                    # Reserved → suggest submit with reservation flags
                    cmd = "flow submit"
                    # If a simple token is available, suggest via -i
                    if gpu_token:
                        cmd += f" -i {gpu_token}"
                    if region:
                        cmd += f' -r "{region}"'
                    cmd += " --allocation reserved"
                    if duration:
                        cmd += f" --duration {int(duration)}"
                    actions.append(
                        {
                            "kind": "run",
                            "cmd": cmd,
                            "notes": "Reserved capacity submission",
                            "instanceType": instance_type,
                            "region": region,
                            "quantity": qty,
                            "priceDollarsPerHour": price_dollars,
                            "regionId": region_id,
                            "instanceTypeId": instance_type_id,
                        }
                    )
            except Exception:  # noqa: BLE001
                continue
        return actions

    def _copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard using OS utilities if available."""
        try:
            if sys.platform == "darwin":
                p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                p.communicate(input=text.encode("utf-8"))
                return p.returncode == 0
            if sys.platform.startswith("win"):
                p = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
                p.communicate(input=text.encode("utf-8"))
                return p.returncode == 0
            # Linux: try xclip or xsel
            if shutil.which("xclip"):
                p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
                p.communicate(input=text.encode("utf-8"))
                return p.returncode == 0
            if shutil.which("xsel"):
                p = subprocess.Popen(["xsel", "--clipboard", "--input"], stdin=subprocess.PIPE)
                p.communicate(input=text.encode("utf-8"))
                return p.returncode == 0
        except Exception:  # noqa: BLE001
            return False
        return False

    def _present_actions_interactive(self, actions: list[dict[str, Any]]) -> None:
        """Interactive picker to execute or copy suggested commands."""
        if not actions:
            return
        accent = theme_manager.get_color("accent")
        console.print(f"\n[{accent}]Next steps (interactive):[/{accent}]")
        for idx, a in enumerate(actions, start=1):
            console.print(f"  {idx}. {a['cmd']}")
        console.print("  q. Quit")

        while True:
            choice = click.prompt("Select an option to execute/copy (number or 'q')", default="q")
            if isinstance(choice, str) and choice.lower().strip() == "q":
                return
            try:
                idx = int(choice)
            except Exception:  # noqa: BLE001
                console.print("[red]Invalid choice[/red]")
                continue
            if idx < 1 or idx > len(actions):
                console.print("[red]Out of range[/red]")
                continue

            selected = actions[idx - 1]
            console.print(f"\nSelected: [bold]{selected['cmd']}[/bold]")
            do_exec = click.confirm("Execute now?", default=True)
            if do_exec:
                # Ensure 'flow' is available
                if not shutil.which("flow"):
                    console.print("[red]'flow' command not found on PATH[/red]")
                else:
                    try:
                        proc = subprocess.run(selected["cmd"], shell=True)
                        if proc.returncode != 0:
                            console.print(f"[red]Command exited with code {proc.returncode}[/red]")
                    except Exception as e:  # noqa: BLE001
                        console.print(f"[red]Failed to execute command: {e}[/red]")
                return

            do_copy = click.confirm("Copy to clipboard instead?", default=True)
            if do_copy:
                if self._copy_to_clipboard(selected["cmd"]):
                    console.print("[green]Copied to clipboard[/green]")
                else:
                    console.print(
                        "[yellow]Could not copy to clipboard. Please copy manually.[/yellow]"
                    )
                return
            # If neither, loop back


# Export the command
command = AskCommand()
