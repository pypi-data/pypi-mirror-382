"""API client for the Veris CLI."""

from __future__ import annotations

import os
from typing import Any

import httpx
from httpx import HTTPStatusError
from veris_cli.errors import UpstreamServiceError

from veris_cli.errors import ConfigurationError
from veris_cli.models.engine import AgentConnnection


class ApiClient:
    """API client for the Veris CLI."""

    def __init__(
        self, base_url: str | None = None, agent_id: str | None = None, *, timeout: float = 30.0
    ):
        """Initialize API client.

        This ensures .env file is loaded and validates API key is present.
        """
        # pdb.set_trace()
        # load_dotenv(override=True)

        if not os.environ.get("VERIS_API_KEY"):
            print(
                "VERIS_API_KEY environment variable is not set. Please set it in your environment or create a .env file with VERIS_API_KEY=your-key-here"
            )
            raise ConfigurationError(
                message="VERIS_API_KEY environment variable is not set. "
                "Please set it in your environment or create a .env file with VERIS_API_KEY=your-key-here"
            )
        # Resolve base URL precedence: constructor > VERIS_API_URL > default
        if base_url:
            self.base_url = base_url
        else:
            env_url = os.environ.get("VERIS_API_URL")
            if not env_url:
                env_url = "https://simulator.api.veris.ai"
                os.environ["VERIS_API_URL"] = env_url
            self.base_url = env_url

        # Read API key from environment variable
        api_key = os.environ.get("VERIS_API_KEY")

        # Validate API key
        if api_key is None:
            raise ValueError(
                "VERIS_API_KEY environment variable is not set. "
                "Please set it in your environment or create a .env file with VERIS_API_KEY=your-key-here"
            )

        if not api_key.strip():
            raise ValueError(
                "VERIS_API_KEY environment variable is empty. Please provide a valid API key."
            )

        if agent_id:
            self.agent_id = agent_id

        default_headers: dict[str, str] = {"X-API-Key": api_key}

        self._areclient = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=default_headers,
        )

    async def _arequest(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        user_message: str | None = None,
    ) -> httpx.Response:
        """Async request helper to standardize error handling."""
        try:
            response = await self._areclient.request(
                method, path, json=json, params=params, headers=headers
            )
            response.raise_for_status()
            return response
        except HTTPStatusError as exc:
            raise UpstreamServiceError.from_httpx_error(
                exc,
                endpoint=f"{method} {path}",
                user_message=user_message or "The upstream service returned an error.",
            ) from exc

    # -----------------------------
    # SIMPLE FLOW
    # -----------------------------

    async def fetch_agent(self) -> dict[str, Any]:
        """Fetch an agent."""
        response = await self._arequest(
            "GET",
            f"/v3/agents/{self.agent_id}",
        )
        return response.json()

    async def list_scenario_sets(self) -> dict[str, Any]:
        """List scenario sets."""
        response = await self._arequest(
            "GET",
            f"/v3/agents/{self.agent_id}/scenario-sets",
        )
        return response.json()

    async def start_simulation(
        self,
        scenario_set_id: str,
        max_turns: int = 20,
        agent_connection: AgentConnnection | None = None,
    ) -> dict[str, Any]:
        """Start a simulation."""
        response = await self._arequest(
            "POST",
            f"/v3/agents/{self.agent_id}/simulations",
            json={
                "scenario_set_id": scenario_set_id,
                "max_turns": max_turns,
                "agent_connection": agent_connection.model_dump() if agent_connection else None,
            },
        )
        return response.json()

    async def get_simulation_status(self, run_id: str) -> dict[str, Any]:
        """Get the status of a simulation."""
        response = await self._arequest(
            "GET",
            f"/v3/agents/{self.agent_id}/simulations/{run_id}",
        )
        return response.json()

    async def get_simulation_sessions(self, run_id: str) -> dict[str, Any]:
        """Get the logs of a simulation."""
        response = await self._arequest(
            "GET",
            f"/v3/agents/{self.agent_id}/simulations/{run_id}/sessions",
        )
        return response.json()

    async def get_simulation_session_logs(self, run_id: str, session_id: str) -> dict[str, Any]:
        """Get the logs of a simulation session."""
        response = await self._arequest(
            "GET",
            f"/v3/agents/{self.agent_id}/simulations/{run_id}/sessions/{session_id}/logs",
        )
        return response.json()

    async def kill_simulation(self, run_id: str) -> dict[str, Any]:
        """Kill a simulation."""
        response = await self._arequest(
            "POST",
            f"/v3/agents/{self.agent_id}/simulations/{run_id}/kill",
        )
        return response.json()

    async def get_simulation_results(self, run_id: str) -> dict[str, Any]:
        """Get the results of a simulation."""
        response = await self._arequest(
            "GET",
            f"/v3/agents/{self.agent_id}/simulations/{run_id}/results",
        )
        return response.json()
