"""Embedded template assets used by trackignore commands."""

from __future__ import annotations

from importlib import resources
from pathlib import Path


def read_text(name: str) -> str:
    """Return the text content of a template file."""
    return resources.files(__package__).joinpath(name).read_text(encoding="utf-8")


def export_to(path: Path, name: str, *, mode: int | None = None) -> None:
    """Write the named template to ``path`` and optionally set permissions."""
    content = read_text(name)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)
