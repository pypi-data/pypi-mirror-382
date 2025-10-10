"""Agent specification models."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class Tool(BaseModel):
    """Tool definition from agent specification."""

    name: str
    description: str
    parameters: dict[str, Any] = {}


class ToolUse(BaseModel):
    """Tool use configuration."""

    tools: list[Tool]


class UseCase(BaseModel):
    """Use case definition within an agent specification."""

    name: str
    description: str


class AgentSpec(BaseModel):
    """Agent specification structure that we expect from customers.

    Agent specification structure that we expect from customers.
    This defines the contract for what fields we need.
    """

    # Required fields
    name: str
    description: str
    use_cases: list[UseCase]

    # Optional but commonly used fields
    tool_use: ToolUse | None = None
    preferences: list[str] = []
    policies: list[str] = []

    # Allow extra fields that we don't use but customer might include
    model_config = ConfigDict(extra="allow")
