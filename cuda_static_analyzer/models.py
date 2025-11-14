"""Data models shared across the analyzer."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SourceLocation:
    """Represents a location in a source file."""

    path: Path
    line: int
    column: int

    def to_sarif(self) -> Dict[str, object]:
        return {
            "uri": str(self.path),
            "region": {"startLine": self.line, "startColumn": self.column},
        }


@dataclass
class Finding:
    """Security finding produced by a rule."""

    rule_id: str
    severity: str
    message: str
    location: SourceLocation
    metadata: Optional[Dict[str, object]] = None

    def to_dict(self) -> Dict[str, object]:
        payload = {
            "rule": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "location": {
                "file": str(self.location.path),
                "line": self.location.line,
                "column": self.location.column,
            },
        }
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload


@dataclass
class AnalyzerResult:
    """Result containing findings and derived metrics."""

    findings: List[Finding]
    metrics: Dict[str, float]
    sarif: Optional[Dict[str, object]] = None
