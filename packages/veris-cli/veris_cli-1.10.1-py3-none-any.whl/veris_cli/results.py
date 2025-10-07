"""Results aggregation and formatting."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .run_models import Run, RunStatus


def is_run_complete(run: Run) -> bool:
    """Check if a run is complete."""
    for sim in run.simulations:
        if sim.evaluation_status not in (RunStatus.completed, RunStatus.failed):
            return False
    return True


class FailureEntry(BaseModel):
    """Model for failure entry."""

    scenario_id: str
    simulation_id: str | None = None
    eval_id: str | None = None
    error: str | None = None


class ResultsAggregate(BaseModel):
    """Model for results aggregate."""

    run_id: str
    per_scenario: dict[str, dict[str, float]] = Field(default_factory=dict)
    overall: dict[str, float] = Field(default_factory=dict)
    failures: list[FailureEntry] = Field(default_factory=list)


def _extract_metric_map(results: dict[str, Any]) -> dict[str, float]:
    """Normalize various evaluation_results shapes to a flat metric map.

    Supported shapes:
    - { "metrics": { id: number, ... } }
    - { "core_metrics": [ { name: str, value: number }, ... ], "overall_score": number? }
    """
    metrics = results.get("metrics")
    if isinstance(metrics, dict):
        return {str(k): float(v) for k, v in metrics.items() if isinstance(v, int | float)}

    core_list = results.get("core_metrics")
    out: dict[str, float] = {}
    if isinstance(core_list, list):
        for item in core_list:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            value = item.get("value")
            if isinstance(name, str) and isinstance(value, int | float):
                out[name] = float(value)
    overall_score = results.get("overall_score")
    if isinstance(overall_score, int | float):
        out.setdefault("overall_score", float(overall_score))
    return out


def aggregate_results(run: Run) -> ResultsAggregate:
    """Aggregate per-simulation evaluation_results into per-scenario and overall metrics.

    Expected evaluation_results shape (minimal): { "metrics": { metricId: number, ... }, ... }
    """
    per_scenario: dict[str, dict[str, float]] = {}
    counts: dict[str, int] = {}

    for sim in run.simulations:
        metrics = _extract_metric_map(sim.evaluation_results or {})
        sid = sim.scenario_id
        if sid not in per_scenario:
            per_scenario[sid] = {}
            counts[sid] = 0
        if metrics:
            for k, v in metrics.items():
                per_scenario[sid][k] = per_scenario[sid].get(k, 0.0) + float(v)
            counts[sid] += 1

    # Average per scenario
    for sid, total_by_metric in per_scenario.items():
        c = max(counts.get(sid, 1), 1)
        for k in list(total_by_metric.keys()):
            total_by_metric[k] = total_by_metric[k] / c

    # Overall averages across scenarios
    overall: dict[str, float] = {}
    scenario_count = max(len(per_scenario) or 1, 1)
    for _sid, totals in per_scenario.items():
        for k, v in totals.items():
            overall[k] = overall.get(k, 0.0) + v
    for k in list(overall.keys()):
        overall[k] = overall[k] / scenario_count

    failures: list[FailureEntry] = []
    for sim in run.simulations:
        if sim.evaluation_status == RunStatus.failed:
            failures.append(
                FailureEntry(
                    scenario_id=sim.scenario_id,
                    simulation_id=sim.simulation_id,
                    eval_id=sim.eval_id,
                    error=(sim.evaluation_results or {}).get("error"),
                )
            )

    return ResultsAggregate(
        run_id=run.run_id,
        per_scenario=per_scenario,
        overall=overall,
        failures=failures,
    )


def format_results_table(agg: ResultsAggregate) -> str:
    """Format the results table."""
    lines: list[str] = []
    lines.append(f"Run {agg.run_id} results")
    lines.append("")
    lines.append("Per-scenario averages:")
    for sid, metrics in agg.per_scenario.items():
        metric_str = ", ".join(f"{k}: {v:.3f}" for k, v in metrics.items()) or "(no metrics)"
        lines.append(f"  {sid}: {metric_str}")
    lines.append("")
    lines.append("Overall averages:")
    overall_str = ", ".join(f"{k}: {v:.3f}" for k, v in agg.overall.items()) or "(no metrics)"
    lines.append(f"  {overall_str}")
    if agg.failures:
        lines.append("")
        lines.append("Failures:")
        for f in agg.failures:
            lines.append(f"  {f.scenario_id} (sim={f.simulation_id}, eval={f.eval_id}): {f.error}")
    return "\n".join(lines)
