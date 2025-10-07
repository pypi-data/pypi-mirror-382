"""File system utilities."""

from __future__ import annotations

from pathlib import Path

VERIS_DIRNAME = ".veris"


def ensure_veris_dir(project_dir: Path) -> Path:
    """Ensure the .veris directory exists."""
    directory_path = project_dir / VERIS_DIRNAME
    directory_path.mkdir(exist_ok=True)
    return directory_path


def write_text_if_missing(path: Path, content: str, *, force: bool = False) -> None:
    """Write text to a file if it doesn't exist."""
    if not force and path.exists():
        return
    path.write_text(content, encoding="utf-8")
