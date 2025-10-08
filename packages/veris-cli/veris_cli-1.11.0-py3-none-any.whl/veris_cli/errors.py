"""Custom error types for the Veris CLI."""

from __future__ import annotations

from dataclasses import dataclass

from httpx import HTTPStatusError


@dataclass
class ConfigurationError(Exception):
    """Represents a local configuration mistake by the user.

    Use this when the user has not configured the CLI correctly or is using
    commands out of order (e.g., missing fields in agent.json or missing
    agent endpoint in .veris/config.json). The error is intended to be
    actionable and guide the user to resolve the problem.
    """

    message: str
    hint: str | None = None
    file_path: str | None = None
    command_suggestion: str | None = None

    def __str__(self) -> str:  # pragma: no cover - string formatting only
        """Return a human-friendly, copyable error message for CLI display."""
        lines: list[str] = []
        lines.append("Configuration error detected.")
        if self.message:
            lines.append(f"Reason: {self.message}")
        if self.file_path:
            lines.append(f"File: {self.file_path}")
        if self.hint:
            lines.append(f"Hint: {self.hint}")
        if self.command_suggestion:
            lines.append(f"Try: {self.command_suggestion}")
        lines.append(
            "If you continue to have trouble, consult our documentation, otherwise please reach out to us at support@veris.ai."
        )
        return "\n".join(lines)


@dataclass
class UpstreamServiceError(Exception):
    """Represents a failure returned by the upstream Veris services.

    This error is designed to produce a clear, copyable message that users can
    paste to the Veris team for faster debugging. Prefer raising this instead of
    raw HTTP exceptions within the CLI.
    """

    message: str
    scenario_id: str | None = None
    run_id: str | None = None
    simulation_id: str | None = None
    endpoint: str | None = None
    status_code: int | None = None
    response_body: str | None = None

    def __str__(self) -> str:  # pragma: no cover - string formatting only
        """Return a human-friendly, copyable error message for CLI display."""
        lines: list[str] = []

        if self.response_body:
            lines.append("Response Body (for debugging):")
            lines.append(self.response_body)
        lines.append("Upstream service error while processing evaluation.")
        if self.message:
            lines.append(f"Reason: {self.message}")
        if self.status_code is not None:
            lines.append(f"HTTP Status: {self.status_code}")
        if self.endpoint:
            lines.append(f"Endpoint: {self.endpoint}")
        if self.run_id:
            lines.append(f"Run ID: {self.run_id}")
        if self.simulation_id:
            lines.append(f"Simulation ID: {self.simulation_id}")
        if self.scenario_id:
            lines.append(f"Scenario ID: {self.scenario_id}")
        lines.append(
            "Please copy this entire message and send it to the Veris team so we can investigate."
        )
        return "\n".join(lines)

    @classmethod
    def from_httpx_error(
        cls,
        exc: HTTPStatusError,
        *,
        scenario_id: str | None = None,
        run_id: str | None = None,
        simulation_id: str | None = None,
        endpoint: str | None = None,
        user_message: str | None = None,
    ) -> "UpstreamServiceError":
        """Create an UpstreamServiceError from an HTTPStatusError."""
        status_code: int | None = None
        response_body: str | None = None
        try:
            status_code = exc.response.status_code  # type: ignore[assignment]
            # Prefer text to preserve raw server message
            response_body = exc.response.text
        except Exception:
            # If the response object is missing or unreadable, ignore
            pass

        message = user_message or "The upstream service returned an error."
        return cls(
            message=message,
            scenario_id=scenario_id,
            run_id=run_id,
            simulation_id=simulation_id,
            endpoint=endpoint,
            status_code=status_code,
            response_body=response_body,
        )
