"""API request and response models."""

from typing import Any, Literal

from pydantic import BaseModel

from app.models.engine import ResponseExpectation

SimulationStatus = Literal["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED"]


class StatusResponse(BaseModel):
    """Response model for simulation status."""

    session_id: str
    status: SimulationStatus
    timestamp: str | None = None
    message: str | None = None
    error: str | None = None


class StatusUpdateRequest(BaseModel):
    """Request model for updating simulation status."""

    status: SimulationStatus
    message: str | None = None
    error: str | None = None


class ToolMock(BaseModel):
    """Model for tool mock."""

    function_name: str
    parameters: dict[str, Any]
    return_type: str
    docstring: str


class ToolMockRequest(BaseModel):
    """Request model for tool mock."""

    tool_call: ToolMock
    session_id: str
    response_expectation: ResponseExpectation | None = ResponseExpectation.AUTO
    cache_response: bool | None = False


class SearchResponse(BaseModel):
    """Response model for trace search results."""

    traces: list[dict] = []
    total_count: int = 0
    has_more: bool = False
