"""Simulation commands."""

from __future__ import annotations

import asyncio
import os
import time

import typer
from rich import print as rprint
from rich.json import JSON
from rich.live import Live
from rich.text import Text

from veris_cli.api import ApiClient
from veris_cli.models.engine import AgentConnnection

simulation_app = typer.Typer(add_completion=False, no_args_is_help=True)


@simulation_app.command("launch")
def launch(
    scenario_set_id: str = typer.Option(..., "--scenario-set-id", help="Scenario set ID"),
    agent_id: str | None = typer.Option(None, "--agent-id", help="Agent ID"),
    max_turns: int = typer.Option(20, "--max-turns", help="Maximum turns per simulation"),
    agent_url: str | None = typer.Option(None, "--agent-url", help="Agent URL"),
    agent_transport: str | None = typer.Option("http", "--agent-transport", help="Agent transport"),
    agent_timeout: int | None = typer.Option(300, "--agent-timeout", help="Agent timeout"),
    watch: bool = typer.Option(False, "--watch", help="Watch simulation status"),
):
    """Launch a simulation using scenario set ID."""
    # Use provided agent_id or fall back to environment variable
    if agent_id is None:
        agent_id = os.environ.get("VERIS_AGENT_ID")
        if not agent_id:
            rprint("[red]Error:[/red] No agent ID provided.")
            rprint("Either pass --agent-id or set VERIS_AGENT_ID environment variable.")
            raise typer.Exit(1)

    agent_url = agent_url or os.environ.get("PUBLIC_AGENT_URL")
    if agent_url:
        agent_connection = AgentConnnection(
            agent_id=agent_id,
            mcp_url=agent_url,
            mcp_transport=agent_transport,
            timeout_seconds=agent_timeout,
        )
    else:
        agent_connection = None

    try:
        client = ApiClient(agent_id=agent_id)

        rprint("[cyan]Starting simulation...[/cyan]")
        rprint(f"  Agent ID: {agent_id}")
        rprint(f"  Scenario Set: {scenario_set_id}")
        rprint(f"  Max Turns: {max_turns}")

        simulation_result = asyncio.run(
            client.start_simulation(scenario_set_id, max_turns, agent_connection)
        )

        run_id = simulation_result.get("run_id")
        if not run_id:
            rprint("[red]Error:[/red] No run_id in response")
            raise typer.Exit(1)

        rprint("\n[green]✓[/green] Simulation started")
        rprint(f"  Run ID: [bold]{run_id}[/bold]")

        if watch:
            rprint("\n[cyan]Watching simulation status...[/cyan]")
            with Live("", refresh_per_second=2, transient=False) as live:
                while True:
                    time.sleep(2.0)
                    status_data = asyncio.run(client.get_simulation_status(run_id))

                    status = status_data.get("status", "UNKNOWN")
                    live.update(
                        Text.from_markup(f"[bold]Status:[/bold] {status}\nRun ID: {run_id}")
                    )

                    if status in ["COMPLETED", "FAILED", "CANCELLED"]:
                        rprint(f"\n[green]Simulation {status}[/green]")
                        rprint(JSON.from_data(status_data))
                        break
        else:
            rprint(f"\nCheck status with: veris simulation status --run-id {run_id}")

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@simulation_app.command("status")
def status(
    run_id: str = typer.Option(..., "--run-id", help="Run ID"),
    agent_id: str | None = typer.Option(None, "--agent-id", help="Agent ID"),
):
    """Get simulation status."""
    # Use provided agent_id or fall back to environment variable
    if agent_id is None:
        agent_id = os.environ.get("VERIS_AGENT_ID")
        if not agent_id:
            rprint("[red]Error:[/red] No agent ID provided.")
            rprint("Either pass --agent-id or set VERIS_AGENT_ID environment variable.")
            raise typer.Exit(1)

    try:
        client = ApiClient(agent_id=agent_id)
        status_data = asyncio.run(client.get_simulation_status(run_id))

        rprint("\n[bold]Simulation Status[/bold]")
        rprint(f"  Run ID: {run_id}")
        rprint(f"  Agent ID: {agent_id}\n")
        rprint(JSON.from_data(status_data))

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@simulation_app.command("sessions")
def sessions(
    run_id: str = typer.Option(..., "--run-id", help="Run ID"),
    agent_id: str | None = typer.Option(None, "--agent-id", help="Agent ID"),
):
    """Get sessions for a simulation."""
    # Use provided agent_id or fall back to environment variable
    if agent_id is None:
        agent_id = os.environ.get("VERIS_AGENT_ID")
        if not agent_id:
            rprint("[red]Error:[/red] No agent ID provided.")
            rprint("Either pass --agent-id or set VERIS_AGENT_ID environment variable.")
            raise typer.Exit(1)

    try:
        client = ApiClient(agent_id=agent_id)
        sessions_data = asyncio.run(client.get_simulation_sessions(run_id))

        rprint("\n[bold]Simulation Sessions[/bold]")
        rprint(f"  Run ID: {run_id}")
        rprint(f"  Agent ID: {agent_id}\n")
        rprint(JSON.from_data(sessions_data))

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@simulation_app.command("logs")
def logs(
    run_id: str = typer.Option(..., "--run-id", help="Run ID"),
    session_id: str | None = typer.Option(
        None, "--session-id", help="Session ID (optional, fetches all if not provided)"
    ),
    agent_id: str | None = typer.Option(None, "--agent-id", help="Agent ID"),
):
    """Get logs for a session or all sessions."""
    # Use provided agent_id or fall back to environment variable
    if agent_id is None:
        agent_id = os.environ.get("VERIS_AGENT_ID")
        if not agent_id:
            rprint("[red]Error:[/red] No agent ID provided.")
            rprint("Either pass --agent-id or set VERIS_AGENT_ID environment variable.")
            raise typer.Exit(1)

    async def fetch_logs():
        client = ApiClient(agent_id=agent_id)

        # If session_id provided, fetch logs for that session only
        if session_id:
            logs_data = await client.get_simulation_session_logs(run_id, session_id)

            rprint("\n[bold]Session Logs[/bold]")
            rprint(f"  Run ID: {run_id}")
            rprint(f"  Session ID: {session_id}")
            rprint(f"  Agent ID: {agent_id}\n")
            rprint(JSON.from_data(logs_data))
        else:
            # Fetch all sessions and loop through them
            sessions_data = await client.get_simulation_sessions(run_id)

            sessions = sessions_data.get("sessions", [])
            if not sessions:
                rprint("[yellow]No sessions found for this run.[/yellow]")
                return

            rprint("\n[bold]Logs for All Sessions[/bold]")
            rprint(f"  Run ID: {run_id}")
            rprint(f"  Agent ID: {agent_id}")
            rprint(f"  Total Sessions: {len(sessions)}\n")

            for idx, session in enumerate(sessions, 1):
                sess_id = session.get("session_id")
                if not sess_id:
                    continue

                scenario_id = session.get("scenario_id", "unknown")
                status = session.get("status", "unknown")

                rprint(f"\n[cyan]═══ Session {idx}/{len(sessions)} ═══[/cyan]")
                rprint(f"  Session ID: [bold]{sess_id}[/bold]")
                rprint(f"  Scenario ID: {scenario_id}")
                rprint(f"  Status: {status}\n")

                try:
                    logs_data = await client.get_simulation_session_logs(run_id, sess_id)
                    rprint(JSON.from_data(logs_data))
                except Exception as e:
                    rprint(f"  [red]Error fetching logs:[/red] {e}")

    try:
        asyncio.run(fetch_logs())
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@simulation_app.command("kill")
def kill(
    run_id: str = typer.Option(..., "--run-id", help="Run ID"),
    agent_id: str | None = typer.Option(None, "--agent-id", help="Agent ID"),
):
    """Kill a running simulation."""
    # Use provided agent_id or fall back to environment variable
    if agent_id is None:
        agent_id = os.environ.get("VERIS_AGENT_ID")
        if not agent_id:
            rprint("[red]Error:[/red] No agent ID provided.")
            rprint("Either pass --agent-id or set VERIS_AGENT_ID environment variable.")
            raise typer.Exit(1)

    try:
        client = ApiClient(agent_id=agent_id)
        result = asyncio.run(client.kill_simulation(run_id))

        rprint("\n[green]✓[/green] Simulation killed")
        rprint(f"  Run ID: {run_id}")
        rprint(f"  Agent ID: {agent_id}\n")
        rprint(JSON.from_data(result))

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@simulation_app.command("results")
def results(
    run_id: str = typer.Option(..., "--run-id", help="Run ID"),
    agent_id: str | None = typer.Option(None, "--agent-id", help="Agent ID"),
):
    """Get simulation results."""
    # Use provided agent_id or fall back to environment variable
    if agent_id is None:
        agent_id = os.environ.get("VERIS_AGENT_ID")
        if not agent_id:
            rprint("[red]Error:[/red] No agent ID provided.")
            rprint("Either pass --agent-id or set VERIS_AGENT_ID environment variable.")
            raise typer.Exit(1)

    try:
        client = ApiClient(agent_id=agent_id)
        results_data = asyncio.run(client.get_simulation_results(run_id))

        rprint("\n[bold]Simulation Results[/bold]")
        rprint(f"  Run ID: {run_id}")
        rprint(f"  Agent ID: {agent_id}\n")
        rprint(JSON.from_data(results_data))

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
