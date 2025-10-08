"""Evaluation model for analyzing simulation conversations."""

from pydantic import BaseModel, Field


class ExampleInteraction(BaseModel):
    """Example interaction from a conversation."""

    user: str
    assistant: str


class MetricValue(BaseModel):
    """Individual metric with name and score."""

    name: str
    value: float = Field(ge=1.0, le=5.0)


class Evaluation(BaseModel):
    """Comprehensive evaluation of a simulation conversation."""

    conversation_id: str
    timestamp: str
    scenario: str
    use_case_name: str | None = None
    core_metrics: list[MetricValue]
    agent_specific_metrics: list[MetricValue]
    user_preference_metrics: list[MetricValue]
    tool_usage_metrics: list[MetricValue] | None = None
    overall_score: float = Field(ge=1.0, le=5.0)
    strengths: list[str]
    issues: list[str]
    improvement_suggestions: list[str]
    tool_usage_analysis: str | None = None
    examples: list[ExampleInteraction]
    conversation_turns: int = Field(
        default=0, description="Number of conversation turns (persona messages to agent)"
    )
    task_completed: bool = Field(
        description="Whether the agent successfully completed the requested task"
    )
    task_completion_reasoning: str = Field(
        description="Explanation of why the task was or wasn't completed"
    )
