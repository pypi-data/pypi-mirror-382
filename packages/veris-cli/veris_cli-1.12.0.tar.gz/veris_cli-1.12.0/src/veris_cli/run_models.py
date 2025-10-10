"""Models for the Veris CLI."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Model for run status."""

    pending = "PENDING"
    running = "IN_PROGRESS"
    completed = "COMPLETED"
    failed = "FAILED"


class SimulationStatus(str, Enum):
    """Model for simulation status."""

    pending = "PENDING"
    running = "IN_PROGRESS"
    completed = "COMPLETED"
    failed = "FAILED"


class EvaluationEntry(BaseModel):
    """Model for evaluation entry."""

    eval_id: str
    status: RunStatus
    results: dict[str, Any] | None = None


class SimulationEntry(BaseModel):
    """Model for simulation entry."""

    id: str
    scenario_id: str
    scenario_name: str | None = None
    simulation_id: str | None = None
    simulation_status: SimulationStatus = SimulationStatus.pending
    logs: list[dict[str, Any]] | None = None
    eval_id: str | None = None
    evaluation_status: RunStatus | None = None
    evaluation_results: dict[str, Any] | None = None


class Run(BaseModel):
    """Model for run."""

    run_id: str
    created_at: str
    status: RunStatus
    evaluations: list[EvaluationEntry] = Field(default_factory=list)
    sessions: list[SimulationEntry] = Field(default_factory=list)


# -----------------------------
# V3 run models
# -----------------------------


class V3SessionStatus(str, Enum):
    """Session status for V3 flows (mirrors server statuses)."""

    pending = "PENDING"
    in_progress = "IN_PROGRESS"
    completed = "COMPLETED"
    failed = "FAILED"


class V3SessionEntry(BaseModel):
    """Session entry tracked for V3 simulation runs."""

    session_id: str
    scenario_id: str
    status: V3SessionStatus
    logs: list[dict[str, Any]] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class V3Run(BaseModel):
    """Top-level run record for V3 end-to-end flow."""

    run_id: str
    created_at: str
    status: V3SessionStatus
    agent_id: str
    version_id: str
    scenario_set_id: str
    sessions: list[V3SessionEntry] = Field(default_factory=list)
