"""Veris CLI package."""

__all__ = ["__version__"]

__version__ = "0.1.0"

# Re-export commonly used types for convenience in tests
try:  # pragma: no cover - convenience only
    from veris_cli.models.scenarios.agent_spec import AgentSpec  # type: ignore # noqa: F401
    from veris_cli.models.scenarios.scenario import SingleScenario  # type: ignore # noqa: F401

    from .loaders import (  # type: ignore # noqa: F401
        load_agent_spec,
        load_evaluation_metrics,
        load_scenarios,
    )
    from .types import EvaluationMetric  # type: ignore # noqa: F401
except Exception:
    pass
