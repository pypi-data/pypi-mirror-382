"""Setup local commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import typer
import yaml
from pyngrok import ngrok
from rich import print as rprint

setup_local_app = typer.Typer(add_completion=False, no_args_is_help=True)


@setup_local_app.command("start")
def start(
    local_url: str = typer.Option(
        ..., "--local-url", help="Local URL to tunnel (e.g., http://localhost:8000)"
    ),
    agent_pathname: Optional[str] = typer.Option(
        None, "--agent-pathname", help="Pathname for agent endpoint (e.g., /mcp)"
    ),
    background: bool = typer.Option(
        True, "--background/--foreground", help="Run tunnel in background"
    ),
):
    """Start ngrok tunnel and save public endpoint to config."""
    try:
        rprint(f"[cyan]Starting ngrok tunnel for {local_url}...[/cyan]")

        # Create ngrok tunnel
        http_tunnel = ngrok.connect(local_url, bind_tls=True)
        public_url = http_tunnel.public_url
        if agent_pathname:
            public_url = urljoin(public_url.rstrip("/"), agent_pathname)

        rprint("[green]✓[/green] Ngrok tunnel established")
        rprint(f"  Local URL: {local_url}")
        rprint(f"  Public URL: [bold]{public_url}[/bold]")

        # Save to config.yaml
        config_path = Path.cwd() / ".veris" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}

        # Update public URL
        config["PUBLIC_AGENT_URL"] = public_url

        # Save config
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        rprint("\n[green]✓[/green] Saved to .veris/config.yaml")
        rprint(f"  public_agent_url: {public_url}")

        if background:
            rprint("\n[green]✓[/green] Tunnel is running in the background")
        else:
            rprint("\n[yellow]Note:[/yellow] Press Ctrl+C to stop the tunnel")
            try:
                import signal

                signal.pause()
            except KeyboardInterrupt:
                rprint("\n[yellow]Stopping ngrok tunnel...[/yellow]")
                ngrok.disconnect(public_url)
                rprint("[green]✓[/green] Tunnel stopped")

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@setup_local_app.command("stop")
def stop():
    """Stop all ngrok tunnels."""
    try:
        tunnels = ngrok.get_tunnels()
        if not tunnels:
            rprint("[yellow]No active tunnels found[/yellow]")
            return

        rprint(f"[cyan]Stopping {len(tunnels)} tunnel(s)...[/cyan]")
        ngrok.kill()
        rprint("[green]✓[/green] All tunnels stopped")

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
