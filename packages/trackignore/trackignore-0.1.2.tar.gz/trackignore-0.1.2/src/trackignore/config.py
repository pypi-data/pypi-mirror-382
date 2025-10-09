"""Loader utilities for `.trackignore` configurations."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Iterable, List, Optional

try:
    import pathspec
except ModuleNotFoundError as exc:  # pragma: no cover - dependency check
    raise RuntimeError(
        "pathspec is required for trackignore. Install it via "
        "`pip install pathspec` or reinstall trackignore to restore dependencies."
    ) from exc

from trackignore.warnings import TrackIgnoreWarning, WarningSeverity

DEFAULT_PATTERN = "__PRIVATE__/"
DEFAULT_TEMPLATE = """\
# trackignore configuration
# Add files or folders to strip from public history.
# Patterns follow gitignore syntax.
__PRIVATE__/
"""


@dataclass(slots=True)
class TrackIgnoreConfig:
    """Represents the parsed `.trackignore` file."""

    patterns: List[str]
    hash: str
    source_path: Path
    exists: bool
    warnings: List[TrackIgnoreWarning] = field(default_factory=list)
    raw_lines: List[str] = field(default_factory=list)
    env_overrides: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Export configuration details for diagnostics."""
        return {
            "patterns": self.patterns,
            "hash": self.hash,
            "source_path": str(self.source_path),
            "exists": self.exists,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "env_overrides": self.env_overrides,
        }


def load_trackignore(
    repo_root: Path | str = ".",
    *,
    include_env: bool = True,
    check_gitignore: bool = True,
) -> TrackIgnoreConfig:
    """
    Load and validate `.trackignore` from the given repository root.

    Parameters
    ----------
    repo_root:
        The repository directory containing `.trackignore`.
    include_env:
        Whether to append the legacy `PRIVATE_DIR` environment variable.
    check_gitignore:
        Whether to evaluate overlaps with `.gitignore`.
    """

    root = Path(repo_root).resolve()
    trackignore_path = root / ".trackignore"
    gitignore_path = root / ".gitignore"

    raw_lines, exists = _read_trackignore(trackignore_path)
    processed = _process_lines(trackignore_path, raw_lines)
    patterns = processed["patterns"]
    warnings = processed["warnings"]

    if include_env:
        warnings.extend(_append_env_override(patterns, trackignore_path))

    if check_gitignore and gitignore_path.exists():
        warnings.extend(_detect_gitignore_overlap(patterns, gitignore_path))

    pattern_hash = _hash_patterns(patterns)

    return TrackIgnoreConfig(
        patterns=patterns,
        hash=pattern_hash,
        source_path=trackignore_path,
        exists=exists,
        warnings=warnings,
        raw_lines=raw_lines,
    )


def generate_default_trackignore() -> str:
    """Return the default template for new `.trackignore` files."""
    return DEFAULT_TEMPLATE


# Internal helpers -----------------------------------------------------


def _read_trackignore(path: Path) -> tuple[list[str], bool]:
    if not path.exists():
        return [DEFAULT_PATTERN], False

    content = path.read_text(encoding="utf-8")
    # Strip UTF-8 BOM if present
    if content.startswith("\ufeff"):
        content = content.lstrip("\ufeff")
    return content.splitlines(), True


def _process_lines(
    source_path: Path,
    lines: Iterable[str],
) -> dict[str, list]:
    pathspec_module = pathspec
    normalized: list[str] = []
    warnings: list[TrackIgnoreWarning] = []

    for idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        is_negation = stripped.startswith("!")
        core = stripped[1:] if is_negation else stripped
        core = core.replace("\\", "/")

        if core.startswith("../"):
            warnings.append(
                TrackIgnoreWarning(
                    code="pattern-parent-reference",
                    message="Patterns must not traverse outside the repository.",
                    severity=WarningSeverity.ERROR,
                    suggestion="Remove leading '../' segments or relocate the file.",
                    path=source_path,
                    line_no=idx,
                )
            )
            continue

        if core.startswith("/"):
            warnings.append(
                TrackIgnoreWarning(
                    code="pattern-absolute-path",
                    message="Leading '/' is stripped; patterns are relative to repo root.",
                    severity=WarningSeverity.WARNING,
                    suggestion="Remove the leading slash unless you intend to match from root.",
                    path=source_path,
                    line_no=idx,
                )
            )
            core = core.lstrip("/")

        if core == "":
            warnings.append(
                TrackIgnoreWarning(
                    code="pattern-empty",
                    message="Pattern is empty after normalization and will be ignored.",
                    severity=WarningSeverity.WARNING,
                    path=source_path,
                    line_no=idx,
                )
            )
            continue

        normalized_core = core
        normalized_core = normalized_core.replace("//", "/")
        if normalized_core.startswith("./"):
            normalized_core = normalized_core[2:]

        candidate = f"!{normalized_core}" if is_negation else normalized_core
        normalized.append(candidate)

    compile_errors = _validate_patterns(pathspec_module, normalized, source_path)
    warnings.extend(compile_errors)

    return {"patterns": normalized, "warnings": warnings}


def _validate_patterns(pathspec_module, patterns: list[str], source_path: Path) -> list[TrackIgnoreWarning]:
    if not patterns:
        return []

    util_module = getattr(pathspec_module, "util", None)
    gitwild_error = getattr(util_module, "GitWildMatchError", None)

    try:
        pathspec_module.PathSpec.from_lines("gitwildmatch", patterns)
    except Exception as exc:  # noqa: BLE001
        if gitwild_error and isinstance(exc, gitwild_error):
            line_no = getattr(exc, "lineno", None)
            return [
                TrackIgnoreWarning(
                    code="pattern-invalid",
                    message=str(exc),
                    severity=WarningSeverity.ERROR,
                    suggestion="Review the pattern and ensure it follows gitignore syntax.",
                    path=source_path,
                    line_no=line_no,
                )
            ]
        line_no = getattr(exc, "lineno", None)
        return [
            TrackIgnoreWarning(
                code="pattern-compile-error",
                message=f"Unexpected error compiling patterns: {exc}",
                severity=WarningSeverity.ERROR,
                suggestion="Report this issue with the offending pattern.",
                path=source_path,
                line_no=line_no,
            )
        ]
    return []


def _append_env_override(patterns: list[str], source_path: Path) -> list[TrackIgnoreWarning]:
    env_value = _read_env_private_dir()
    if not env_value:
        return []

    normalized = env_value.replace("\\", "/").strip("/")
    if not normalized:
        return [
            TrackIgnoreWarning(
                code="env-private-dir-empty",
                message="PRIVATE_DIR environment variable is set but empty.",
                severity=WarningSeverity.WARNING,
                suggestion="Unset PRIVATE_DIR or provide a valid directory name.",
            )
        ]

    if normalized not in patterns:
        patterns.append(normalized)

    return [
        TrackIgnoreWarning(
            code="env-private-dir-used",
            message=f"Legacy PRIVATE_DIR override applied: '{normalized}'.",
            severity=WarningSeverity.WARNING,
            suggestion="Migrate the value into .trackignore and remove PRIVATE_DIR.",
            path=source_path,
        )
    ]


def _read_env_private_dir() -> Optional[str]:
    import os

    return os.environ.get("PRIVATE_DIR")


def _detect_gitignore_overlap(patterns: list[str], gitignore_path: Path) -> list[TrackIgnoreWarning]:
    gitignore_lines = gitignore_path.read_text(encoding="utf-8").splitlines()
    gitignore_normalized = {
        line.strip().lstrip("!")  # remove negation to compare base patterns
        for line in gitignore_lines
        if line.strip() and not line.strip().startswith("#")
    }

    overlaps = []
    for pattern in patterns:
        core = pattern[1:] if pattern.startswith("!") else pattern
        if core in gitignore_normalized:
            overlaps.append(core)

    if not overlaps:
        return []

    overlap_list = ", ".join(sorted(set(overlaps)))
    return [
        TrackIgnoreWarning(
            code="gitignore-overlap",
            message=f"Patterns also found in .gitignore: {overlap_list}",
            severity=WarningSeverity.WARNING,
            suggestion="Ensure sensitive content already tracked in history is cleaned up manually.",
            path=gitignore_path,
        )
    ]


def _hash_patterns(patterns: Iterable[str]) -> str:
    serialized = "\n".join(patterns)
    return sha256(serialized.encode("utf-8")).hexdigest()
