"""Types for the Veris CLI."""

from __future__ import annotations

from pydantic import BaseModel


class EvaluationMetric(BaseModel):
    """Model for evaluation metric."""

    id: str
    name: str
    description: str
