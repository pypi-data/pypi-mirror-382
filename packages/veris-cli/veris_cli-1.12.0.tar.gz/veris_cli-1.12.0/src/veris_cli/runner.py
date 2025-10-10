"""Simulation runner."""

from __future__ import annotations

from typing import Any


from .errors import UpstreamServiceError

from .api import ApiClient
from .run_models import Run, RunStatus, SimulationStatus
from .runs import RunsStore


class SimulationRunner:
    """Simulation runner."""

    def __init__(self, store: RunsStore, api: ApiClient | None = None):
        """Initialize the simulation runner."""
        self.store = store
        # Lazily create ApiClient to avoid requiring env/config until needed
        self._api = api

    def _get_api(self) -> ApiClient:
        if self._api is None:  # pragma: no cover - trivial lazy init
            self._api = ApiClient()
        return self._api

    def launch(
        self,
        scenarios: list[dict],
        agent_name_override: str | None = None,
        *,
        agent: dict[str, Any] | None = None,
    ) -> Run:
        """Launch a simulation."""
        run = self.store.create_run(scenarios)
        run.status = RunStatus.running
        for sim in run.simulations:
            scenario = next(s for s in scenarios if s["scenario_id"] == sim.scenario_id)
            if agent is not None:
                scenario["agent_name"] = agent
            external_id = self._get_api().start_simulation(run.run_id, scenario)
            sim.simulation_id = external_id
            sim.simulation_status = SimulationStatus.pending
        self.store.save_run(run)
        return run

    def poll_once(self, run: Run) -> Run:
        """Poll the simulation once."""
        for sim in run.simulations:
            if not sim.simulation_id:
                continue
            status = self._get_api().get_simulation_status(sim.simulation_id)
            # Map API status to internal status
            status_map = {
                "PENDING": SimulationStatus.pending,
                "IN_PROGRESS": SimulationStatus.running,
                "COMPLETED": SimulationStatus.completed,
                "FAILED": SimulationStatus.failed,
            }
            sim.simulation_status = status_map.get(status.upper(), sim.simulation_status)
            try:
                logs = self._get_api().get_simulation_logs(sim.simulation_id)
            except Exception:
                logs = None
            sim.logs = logs if isinstance(logs, list) else sim.logs
            # Attempt evaluation once when the simulation reaches any terminal state
            is_terminal = sim.simulation_status in (
                SimulationStatus.completed,
                SimulationStatus.failed,
            )
            should_trigger_eval = (
                is_terminal
                and getattr(sim, "eval_id", None) is None
                and getattr(sim, "evaluation_status", None) is None
            )

            if should_trigger_eval:
                try:
                    eval_id = self._get_api().start_evaluation(sim.simulation_id)
                    sim.eval_id = eval_id
                    sim.evaluation_status = RunStatus.running
                except UpstreamServiceError as e:
                    # Degrade gracefully: mark evaluation as failed, record details, do not raise
                    sim.evaluation_status = RunStatus.failed
                    # Stash minimal error info in results so users can see context
                    body = e.response_body if hasattr(e, "response_body") else None
                    sim.evaluation_results = {
                        "error": e.message,
                        "endpoint": e.endpoint,
                        "status_code": e.status_code,
                        "response_body": body,
                    }
            if getattr(sim, "eval_id", None):
                eval_status = self._get_api().get_evaluation_status(sim.eval_id)
                status_map_eval = {
                    "PENDING": RunStatus.pending,
                    "IN_PROGRESS": RunStatus.running,
                    "COMPLETED": RunStatus.completed,
                    "FAILED": RunStatus.failed,
                }
                mapped = status_map_eval.get(
                    eval_status.upper(),
                    sim.evaluation_status,
                )
                sim.evaluation_status = mapped
                if (
                    mapped == RunStatus.completed
                    and getattr(sim, "evaluation_results", None) is None
                ):
                    sim.evaluation_results = self._get_api().get_evaluation_results(sim.eval_id)
        if all(
            s.simulation_status in (SimulationStatus.completed, SimulationStatus.failed)
            for s in run.simulations
        ):
            run.status = RunStatus.completed
        self.store.save_run(run)
        return run

    def format_status(self, run: Run) -> str:
        """Format the status of a run."""
        lines = [f"Run {run.run_id} - {run.status.value}"]
        for sim in run.simulations:
            lines.append(
                f"\n  Scenario {sim.scenario_id}"  # noqa: E501
            )
            lines.append(
                "    Simulation "
                f"{sim.simulation_id or '-'}: {sim.simulation_status.value} "
                f"({len(sim.logs or [])} logs)"
            )
            if getattr(sim, "eval_id", None) or getattr(sim, "evaluation_status", None):
                eval_status_readable = (
                    sim.evaluation_status.value if sim.evaluation_status else "unknown"
                )
                eval_id_display = sim.eval_id or "-"
                eval_line = f"      eval {eval_id_display}: {eval_status_readable}"
                lines.append(eval_line)
        return "\n".join(lines)
