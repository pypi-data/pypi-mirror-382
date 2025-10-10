"""Top-level CLI configuration models.

This module defines the persisted configuration stored in ``.veris/config.json``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class VerisConfig(BaseModel):
    """Configuration for the Veris CLI.

    - ``public_agent_url``: Publicly reachable URL for your local agent (e.g., ngrok URL)
    """

    agent: AgentConnection | None = Field(
        default=None,
        description="Agent connection configuration",
    )
    agent_id: str | None = Field(
        default=None,
        description="Unique identifier for the agent being used",
    )


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
