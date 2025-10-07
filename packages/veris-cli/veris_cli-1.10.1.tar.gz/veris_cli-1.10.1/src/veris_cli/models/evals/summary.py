"""Summary model for aggregating evaluation results."""

from pydantic import BaseModel

from .evaluation import ExampleInteraction


class UseCaseSummary(BaseModel):
    """Summary of findings for a specific use case."""

    use_case_name: str
    findings: list[str]
    example_interactions: list[ExampleInteraction]


class Summary(BaseModel):
    """Aggregated summary of multiple evaluations grouped by use case."""

    use_case_summaries: list[UseCaseSummary]
