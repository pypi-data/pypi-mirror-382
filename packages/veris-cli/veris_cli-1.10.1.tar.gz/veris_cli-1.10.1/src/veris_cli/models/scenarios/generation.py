"""API models for scenario generation."""

from enum import Enum

from pydantic import BaseModel

from .agent_spec import AgentSpec
from .config import GeneratorConfig
from .scenario import SingleScenario


class GenerationStatus(str, Enum):
    """Status of a scenario generation job."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationRequest(BaseModel):
    """Request to generate scenarios."""

    agent_spec: AgentSpec
    config: GeneratorConfig | None = None


class GenerationStatusResponse(BaseModel):
    """Response for generation status check."""

    generation_id: str
    status: GenerationStatus
    scenarios_generated: int
    total_expected: int
    error: str | None = None


class ScenarioListResponse(BaseModel):
    """Response containing list of generated scenarios."""

    generation_id: str
    scenarios: list[SingleScenario]
    total_count: int
