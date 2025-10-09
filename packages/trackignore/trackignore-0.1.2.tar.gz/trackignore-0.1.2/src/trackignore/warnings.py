"""Structured warning definitions for trackignore configuration parsing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class WarningSeverity(str, Enum):
    """Severity levels emitted during trackignore parsing."""

    WARNING = "warning"
    ERROR = "error"


@dataclass(slots=True)
class TrackIgnoreWarning:
    """Warning returned by the loader."""

    code: str
    message: str
    severity: WarningSeverity = WarningSeverity.WARNING
    suggestion: Optional[str] = None
    path: Optional[Path] = None
    line_no: Optional[int] = None

    def to_dict(self) -> dict[str, object]:
        """Serialize warning for JSON output."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
            "path": str(self.path) if self.path else None,
            "line_no": self.line_no,
        }
