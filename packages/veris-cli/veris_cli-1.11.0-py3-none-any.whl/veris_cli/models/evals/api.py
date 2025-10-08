"""API request and response models for evaluation endpoints."""

from enum import Enum

from pydantic import BaseModel


class EvaluationStatus(str, Enum):
    """Status of an evaluation job."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationRequest(BaseModel):
    """Request to evaluate a simulation session."""

    session_id: str  # Redis session ID to fetch logs from


class EvaluationResponse(BaseModel):
    """Response for evaluation creation."""

    eval_id: str
    status: EvaluationStatus


class EvaluationStatusResponse(BaseModel):
    """Response for evaluation status check."""

    eval_id: str
    status: EvaluationStatus
    error: str | None = None


class SummaryRequest(BaseModel):
    """Request to generate summary from evaluations."""

    eval_ids: list[str]


class SummaryResponse(BaseModel):
    """Response for summary creation."""

    summary_id: str
    status: EvaluationStatus


class SummaryStatusResponse(BaseModel):
    """Response for summary status check."""

    summary_id: str
    status: EvaluationStatus
    error: str | None = None
