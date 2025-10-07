"""Agent configuration models for flexible agent setup."""

from typing import Literal

from pydantic import BaseModel, Field


class AgentConnection(BaseModel):
    """Full agent connection configuration.

    This model contains all the information needed to connect to an agent's
    MCP server. Authentication headers are always set automatically using
    the session_id in the PersonaService.
    """

    agent_id: str = Field(description="Unique identifier for the agent")
    name: str = Field(description="Display name for the agent")
    mcp_url: str = Field(description="MCP server URL for this agent")
    mcp_transport: Literal["http", "sse"] | None = Field(
        default="http", description="MCP transport protocol for this agent"
    )
    timeout_seconds: int = Field(default=300, description="Connection timeout in seconds")


# Union type allowing either string ID or full config
# When a string is provided, it will be resolved to a full AgentConnection
# using environment variables (backward compatible)
# When an AgentConnection is provided, it will be used directly
AgentConfig = str | AgentConnection
