"""Runs store."""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
import time

from .errors import ConfigurationError
from .fs import ensure_veris_dir
from .run_models import Run, RunStatus, SimulationEntry, SimulationStatus, V3Run


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class RunsStore:
    """Runs store."""

    def __init__(self, project_dir: Path):
        """Initialize the runs store."""
        self.project_dir = project_dir
        self.veris_dir = ensure_veris_dir(project_dir)
        self.runs_dir = self.veris_dir / "runs"
        self.runs_dir.mkdir(exist_ok=True)

    def _run_file(self, run_id: str) -> Path:
        """Get the path to the run file."""
        return self.runs_dir / f"{run_id}.json"

    def create_run(self, selected_scenarios: list[dict]) -> Run:
        """Create a run."""
        run_id = str(uuid.uuid4())
        run = Run(
            run_id=run_id,
            created_at=_now_iso(),
            status=RunStatus.pending,
            simulations=[
                SimulationEntry(
                    id=str(uuid.uuid4()),
                    scenario_id=sc["scenario_id"],
                    scenario_name=sc.get("title"),
                    simulation_status=SimulationStatus.pending,
                )
                for sc in selected_scenarios
            ],
        )
        self.save_run(run)
        return run

    def save_run(self, run: Run | V3Run) -> None:
        """Save a run."""
        path = self._run_file(run.run_id)
        data = run.model_dump_json(indent=2)
        # Atomic write to avoid truncated/partial JSON on concurrent writes or crashes
        runs_dir = path.parent
        runs_dir.mkdir(exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", dir=runs_dir, delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_name = tmp.name
        os.replace(tmp_name, path)

    def load_run(self, run_id: str) -> Run:
        """Load a run with small retries to handle transient FS races."""
        path = self._run_file(run_id)
        last_err: Exception | None = None
        for attempt in range(5):
            try:
                raw = path.read_text(encoding="utf-8")
                data = json.loads(raw)
                return Run.model_validate(data)
            except FileNotFoundError as e:
                last_err = e
                # If a concurrent writer is about to create/replace the file, wait briefly
                time.sleep(0.05 * (attempt + 1))
                continue
            except json.JSONDecodeError as e:
                last_err = e
                # If we raced with an atomic replace, a subsequent read should succeed
                time.sleep(0.05 * (attempt + 1))
                continue

        # Retries exhausted — surface a helpful, actionable error
        if isinstance(last_err, FileNotFoundError):
            raise ConfigurationError(
                message=f"Run not found: {run_id}.",
                hint="Check the run ID or relaunch with 'veris sim launch'.",
                file_path=str(path),
            ) from last_err
        raise ConfigurationError(
            message="Run file is corrupted or partially written after multiple attempts.",
            hint=(
                "Delete the run file and relaunch the simulation. This can happen if "
                "multiple commands write to the run file concurrently."
            ),
            file_path=str(path),
        ) from last_err

    def load_v3_run(self, run_id: str) -> V3Run:
        """Load a V3 run (agent-rooted) with retries and clear errors if shape mismatches."""
        path = self._run_file(run_id)
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return V3Run.model_validate(data)
