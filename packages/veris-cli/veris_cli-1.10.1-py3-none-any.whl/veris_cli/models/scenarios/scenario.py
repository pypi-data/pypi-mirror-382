"""Scenario data models."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.models.agent_config import AgentConfig


class PersonaDetail(BaseModel):
    """Detailed information about a persona in a scenario."""

    name: str = Field(description="The persona's name")
    role: str = Field(description="Their role in this scenario")
    description: str = Field(
        description="1-2 paragraph detailed description including background, "
        "personality, current situation, and communication style"
    )
    characteristics: list[str] = Field(
        description="Key traits that affect the interaction", default_factory=list
    )


class ToolExpectation(BaseModel):
    """Expected tool usage in a scenario."""

    tool_name: str = Field(description="Name of the tool expected to be used")
    usage_context: str = Field(description="How and why this tool will be used")


class ScenarioSetting(BaseModel):
    """Environmental context for a scenario."""

    time_context: str = Field(description="When this is happening (time of day, day of week, etc.)")
    location: str = Field(description="Where this is happening")
    environment_description: str = Field(description="Environmental factors affecting the scenario")


class SkeletonMetadata(BaseModel):
    """Metadata about the skeleton pattern used to generate the scenario."""

    use_case_name: str
    tool_name: str | None
    urgency: str
    complexity: str


class ScenarioForLLMGeneration(BaseModel):
    """Scenario model for LLM generation (excludes scenario_id and max_turns)."""

    title: str = Field(description="Descriptive title for the scenario")
    description: str = Field(description="Brief overview of what's happening")
    initial_human_prompt: str = Field(
        description="The natural language prompt from the human that starts this scenario"
    )

    # Support both agent and agent_name (deprecated)
    agent: AgentConfig | None = Field(
        None,
        description="Agent configuration - either an agent_id string or full connection details",
    )
    agent_name: str | None = Field(None, description="DEPRECATED - use 'agent' instead")

    personas: list[PersonaDetail] = Field(description="All personas involved in this scenario")
    setting: ScenarioSetting = Field(description="Context and environment")
    expected_tools: list[ToolExpectation] = Field(description="Tools expected to be used")
    objectives: list[str] = Field(description="What the human wants to achieve")
    constraints: list[str] = Field(description="Limitations or requirements")
    skeleton_metadata: SkeletonMetadata | None = Field(
        description="Metadata about the skeleton pattern", default=None
    )

    @model_validator(mode="before")
    @classmethod
    def handle_agent_name_compatibility(cls, data: Any) -> Any:
        """Convert deprecated agent_name to agent field."""
        if isinstance(data, dict):
            # If agent is not set but agent_name is, use agent_name
            if data.get("agent") is None and data.get("agent_name"):
                data["agent"] = data["agent_name"]
                # Optionally remove agent_name to avoid confusion
                # But keep it for now to maintain full backward compatibility
        return data

    @model_validator(mode="after")
    def validate_agent_required(self):
        """Ensure we have either agent or agent_name."""
        if self.agent is None and self.agent_name is None:
            raise ValueError("Either 'agent' or 'agent_name' must be provided")
        return self


class ScenarioForGeneration(ScenarioForLLMGeneration):
    """Base scenario model with max_turns (but without scenario_id)."""

    max_turns: int | None = Field(15, description="Maximum number of turns in the scenario")


class SingleScenario(ScenarioForGeneration):
    """A single generated scenario with unique ID."""

    scenario_id: str = Field(description="Unique identifier for this scenario")
