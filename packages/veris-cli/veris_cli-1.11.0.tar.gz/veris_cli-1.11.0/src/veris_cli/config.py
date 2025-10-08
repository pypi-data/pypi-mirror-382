"""Helpers for loading and saving CLI configuration."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from veris_cli.fs import ensure_veris_dir
from veris_cli.models.config import VerisConfig

CONFIG_FILENAME = "config.json"


def get_config_path(project_dir: Path) -> Path:
    """Return the path to the config file under .veris/.

    Ensures the .veris directory exists.
    """
    veris_dir = ensure_veris_dir(project_dir)
    return veris_dir / CONFIG_FILENAME


def load_config(project_dir: Path) -> VerisConfig:
    """Load configuration from .veris/config.json or return defaults if missing/invalid."""
    config_path = get_config_path(project_dir)
    if not config_path.exists():
        return VerisConfig()
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        return VerisConfig.model_validate(data)
    except Exception:
        # Fall back to defaults on any parse/validation error
        return VerisConfig()


def save_config(project_dir: Path, config: VerisConfig, *, overwrite: bool = False) -> Path:
    """Save configuration to .veris/config.json.

    Will not overwrite an existing file unless ``overwrite`` is True.
    Returns the path to the saved (or existing) config file.
    """
    config_path = get_config_path(project_dir)
    if config_path.exists() and not overwrite:
        return config_path
    config_path.write_text(config.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return config_path


def derive_url_stub(url: str) -> str:
    """Derive a short, URL-based stub for naming purposes.

    Examples:
        https://abcd.ngrok.io -> abcd-ngrok-io
        http://localhost:8000 -> localhost-8000
    """
    parsed = urlparse(url)
    netloc = parsed.netloc or parsed.path
    # Replace separators with hyphens to form a stable stub
    stub = netloc.replace(":", "-").replace("/", "-").replace(".", "-").strip("-")
    if not stub:
        stub = "agent"
    return stub
