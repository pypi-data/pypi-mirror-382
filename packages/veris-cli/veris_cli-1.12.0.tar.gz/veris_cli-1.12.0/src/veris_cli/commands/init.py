"""Initialize a Veris project."""

from __future__ import annotations

import os
from pathlib import Path

import typer
import yaml
from rich import print as rprint

from veris_cli.fs import ensure_veris_dir

init_app = typer.Typer(add_completion=False, no_args_is_help=False)


@init_app.callback(invoke_without_command=True)
def init(
    veris_api_key: str = typer.Option(..., "--veris-api-key", help="Veris API key"),
    veris_agent_id: str = typer.Option(..., "--veris-agent-id", help="Veris agent ID"),
    veris_api_url: str = typer.Option(
        "https://simulator.api.veris.ai/", "--veris-api-url", help="Veris API URL"
    ),
):
    """Initialize Veris configuration with API key, agent ID, and API URL."""
    project_dir = Path.cwd()
    veris_dir = ensure_veris_dir(project_dir)
    config_path = veris_dir / "config.yaml"

    # Load existing config if it exists
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # Set all config values
    config["VERIS_API_KEY"] = veris_api_key
    os.environ["VERIS_API_KEY"] = veris_api_key

    config["VERIS_AGENT_ID"] = veris_agent_id
    os.environ["VERIS_AGENT_ID"] = veris_agent_id

    config["VERIS_API_URL"] = veris_api_url
    os.environ["VERIS_API_URL"] = veris_api_url

    # Save config to .veris/config.yaml
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

    rprint("[green]✓[/green] Configuration saved to [bold].veris/config.yaml[/bold]")
    rprint(f"  [green]✓[/green] VERIS_API_KEY: {veris_api_key[:8]}...")
    rprint(f"  [green]✓[/green] VERIS_AGENT_ID: {veris_agent_id}")
    rprint(f"  [green]✓[/green] VERIS_API_URL: {veris_api_url}")

    rprint("\n[yellow]Note:[/yellow] Environment variables set for current session.")
    rprint("To persist across sessions, add to your shell profile:")
    rprint(f"  export VERIS_API_KEY={veris_api_key}")
    rprint(f"  export VERIS_AGENT_ID={veris_agent_id}")
    rprint(f"  export VERIS_API_URL={veris_api_url}")
