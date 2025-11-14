"""Rule detecting out-of-bounds CUDA array access patterns."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List

from ..models import Finding, SourceLocation
from .base import Rule, RuleContext

_INDEX_PATTERN = re.compile(r"\[[^\]]*(threadIdx|blockIdx|warpSize)")
_GUARD_HINT = re.compile(r"if\s*\(.*(<|<=).*\)")


class OutOfBoundsAccessRule(Rule):
    id = "CUDA001"
    description = "Detects CUDA kernels indexing arrays using thread identifiers without bounds checks"
    severity = "high"

    def evaluate(self, context: RuleContext) -> Iterable[Finding]:
        findings: List[Finding] = []
        path = Path(context.path)
        lines = context.source.splitlines()

        for idx, line in enumerate(lines, start=1):
            if not _INDEX_PATTERN.search(line):
                continue

            window = " ".join(lines[max(0, idx - 3) : idx])
            if _GUARD_HINT.search(window):
                continue

            column = line.find("[") + 1 if "[" in line else 1
            findings.append(
                Finding(
                    rule_id=self.id,
                    severity=self.severity,
                    message=(
                        "Potential out-of-bounds access detected. Index uses thread identifiers "
                        "without nearby guard conditions."
                    ),
                    location=SourceLocation(path=path, line=idx, column=column),
                    metadata={"line_text": line.strip()},
                )
            )
        return findings
