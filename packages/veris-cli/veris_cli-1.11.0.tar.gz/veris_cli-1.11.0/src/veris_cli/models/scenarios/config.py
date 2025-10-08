"""Configuration models for scenario generation."""

from pydantic import BaseModel, Field


class GeneratorConfig(BaseModel):
    """Configuration for the scenario generator."""

    # Core parameters
    variations_per_skeleton: int = 2  # Number of scenarios to generate per skeleton
    random_subset: int | None = None  # If set, randomly sample this many skeletons

    # LLM parameters
    model: str = Field(...)
    temperature: float = 1.0  # gpt-4.1-nano only supports default temperature
    max_parallel_calls: int = 5
    max_retries: int = 3
    api_key: str | None = None
