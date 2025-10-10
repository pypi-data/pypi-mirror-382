"""Core simulation models."""

import json
import logging
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AgentConnnection(BaseModel):
    """Agent connection."""

    agent_id: str
    name: str = "agent"
    mcp_url: str
    mcp_transport: str = "http"
    timeout_seconds: int = 300
    interaction_timeout_seconds: int = 300


class SimulatorOutput(BaseModel):
    """Model for simulator output."""

    message: str
    scenario_finished: bool


class ChatMessage(BaseModel):
    """Model for chat message."""

    channel: Literal["chat", "tool"]
    content: str


# TODO: add field descriptors for each field of SideEffect instead of soft prompting in the instructions # noqa: E501
class SideEffect(BaseModel):
    """Model for side effect."""

    side_effect: bool
    side_effect_reason: str
    scenario_finished: bool
    scenario_finished_reason: str


class TargetAgent(Enum):
    """Model for target agent."""

    FINANCIAL_AGENT = "financial_agent"
    SOURCING_AGENT = "sourcing_agent"
    WORKMATE_AGENT = "workmate_agent"
    SOURCING_COMMUNICATION_AGENT = "sourcing_communication_agent"
    PROPOSAL_FACILITATOR_AGENT = "proposal_facilitator_agent"


class ResponseExpectation(Enum):
    """Defines how the side effect engine should handle tool responses."""

    REQUIRED = "required"  # A response is explicitly required (e.g., user questions)
    NONE = "none"  # No response expected (e.g., status updates)
    AUTO = "auto"  # Let the side effect engine decide based on context


class SimluationLog(BaseModel):
    """Model for simulation log."""

    log_type: Literal["tool_call", "tool_response", "user", "agent", "other", "simulator"]
    log_content: Any
    log_time: str

    def model_dump_json(self) -> str:
        """Dump the simulation log to a JSON string."""
        try:
            return json.dumps(self.model_dump())
        except Exception as e:
            logger.error(f"Error dumping log: {e}")
            return json.dumps(
                {
                    "log_type": self.log_type,
                    "log_content": str(self.log_content),
                    "log_time": self.log_time,
                }
            )


class MCPServerParams(BaseModel):
    """Model for MCP server parameters."""

    name: str
    url: str
    client_session_timeout_seconds: int = (
        300  # Increased to 5 minutes for complex agent interactions
    )
    headers: dict[str, str] | None = None
