"""Shared utilities for Jupyter functionality."""

import signal
import subprocess
import sys
import time
import webbrowser
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from flow.cli.commands.base import console


def wait_for_jupyter_ready(url: str, timeout: int = 60) -> bool:
    """Poll the Jupyter URL until it responds or timeout is reached.

    Args:
        url: The Jupyter server URL to check
        timeout: Maximum time to wait in seconds (default: 60)

    Returns:
        True if server responds within timeout, False otherwise
    """
    start_time = time.time()
    console.print("Waiting for Jupyter server to respond...")

    while time.time() - start_time < timeout:
        try:
            # Try to connect to the server
            request = Request(url)
            with urlopen(request, timeout=2) as response:
                if response.status == 200:
                    elapsed = time.time() - start_time
                    console.print(f"[green]✓ Jupyter server ready (took {elapsed:.2f}s)[/green]")
                    return True
        except (URLError, OSError):
            # Server not ready yet, continue polling
            pass

        time.sleep(0.1)

    return False


def create_jupyter_tunnel(
    task: Any,
    host: str,
    ssh_key_path: str,
    username: str,
    local_port: int,
    jupyter_port: int,
    token: str | None,
    no_open: bool,
    raise_on_timeout: bool = False,
) -> None:
    """Create SSH tunnel and optionally open browser.

    Args:
        task: The task object
        host: SSH host
        ssh_key_path: Path to SSH key
        username: SSH username
        local_port: Local port for tunnel
        jupyter_port: Remote Jupyter port
        token: Jupyter authentication token
        no_open: Whether to skip opening browser
        raise_on_timeout: Whether to raise RuntimeError on timeout (vs return)
    """
    # Build the URL
    url = f"http://localhost:{local_port}"
    if token:
        url += f"/?token={token}"

    console.print("Creating SSH tunnel...")

    # SSH tunnel command
    tunnel_cmd = [
        "ssh",
        "-i",
        ssh_key_path,
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "LogLevel=ERROR",  # Suppress SSH connection messages
        f"{username}@{host}",
        "-N",
        "-L",
        f"{local_port}:localhost:{jupyter_port}",
    ]

    try:
        # Start the tunnel in background
        tunnel_process = subprocess.Popen(tunnel_cmd, stderr=subprocess.DEVNULL)

        console.print("[green]✓ SSH tunnel established[/green]")

        # Wait for Jupyter to be accessible through the tunnel
        if not wait_for_jupyter_ready(url, timeout=60):
            console.print("[red]Jupyter server did not respond within 60 seconds[/red]")
            console.print(
                "[yellow]The tunnel is still active, but the server may not be ready[/yellow]"
            )
            console.print(f"[blue]You can try opening manually: {url}[/blue]")
            tunnel_process.terminate()
            if raise_on_timeout:
                raise RuntimeError("Jupyter server did not respond within 60 seconds")
            return

        # Open browser if requested
        if not no_open:
            try:
                webbrowser.open(url)
                console.print("[green]✓ Opened Jupyter in browser[/green]")
            except Exception:  # noqa: BLE001
                console.print("[yellow]Could not open browser automatically[/yellow]")
                console.print(f"[blue]Please open: {url}[/blue]")
        else:
            console.print(f"[blue]Copy and open this URL: {url}[/blue]")

        # Clean status display
        console.print("\n" + "─" * 60)
        console.print("[bold green]🚀 Jupyter Notebook is running![/bold green]")
        console.print(f"[dim]Task: {task.task_id}[/dim]")
        console.print(f"[dim]Local URL: {url}[/dim]")
        console.print("─" * 60)
        console.print("\n[bold]Press Ctrl+C to stop the tunnel and exit[/bold]")

        # Set up signal handler for clean shutdown
        def signal_handler(signum, frame):
            console.print("\n[yellow]Shutting down tunnel...[/yellow]")
            tunnel_process.terminate()
            try:
                tunnel_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                tunnel_process.kill()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Wait for the tunnel process
        tunnel_process.wait()

    except KeyboardInterrupt:
        console.print("\n[yellow]Tunnel stopped by user[/yellow]")
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]Error with SSH tunnel: {e}[/red]")
