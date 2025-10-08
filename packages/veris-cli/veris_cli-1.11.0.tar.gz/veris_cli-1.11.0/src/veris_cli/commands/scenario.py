"""Scenario generation commands."""

from __future__ import annotations

import asyncio
import os

import typer
from rich import print as rprint
from rich.json import JSON

from veris_cli.api import ApiClient

scenario_app = typer.Typer(add_completion=False, no_args_is_help=False)


@scenario_app.command("list")
def list_scenario_sets(
    agent_id: str | None = typer.Option(None, "--agent-id", help="Agent ID"),
):
    """List scenario sets for an agent."""
    # Use provided agent_id or fall back to environment variable
    if agent_id is None:
        agent_id = os.environ.get("VERIS_AGENT_ID")
        if not agent_id:
            rprint("[red]Error:[/red] No agent ID provided.")
            rprint("Either pass --agent-id or set VERIS_AGENT_ID environment variable.")
            raise typer.Exit(1)

    try:
        client = ApiClient(agent_id=agent_id)
        scenario_sets_data = asyncio.run(client.list_scenario_sets())

        rprint(f"\n[bold]Scenario Sets for Agent: {agent_id}[/bold]\n")
        rprint(JSON.from_data(scenario_sets_data))
    except Exception as e:
        rprint(f"[red]Error listing scenario sets:[/red] {e}")
        raise typer.Exit(1)
