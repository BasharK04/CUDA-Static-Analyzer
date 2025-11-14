"""Rule detecting missing synchronization barriers around shared memory."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from ..models import Finding, SourceLocation
from .base import Rule, RuleContext


class MissingSynchronizationRule(Rule):
    id = "CUDA002"
    description = "Detects shared memory usage without __syncthreads()"
    severity = "medium"

    def evaluate(self, context: RuleContext) -> Iterable[Finding]:
        findings: List[Finding] = []
        path = Path(context.path)
        lines = context.source.splitlines()
        has_shared = any("__shared__" in line for line in lines)
        has_barrier = "__syncthreads" in context.source

        if has_shared and not has_barrier:
            line = next((idx for idx, text in enumerate(lines, start=1) if "__shared__" in text), 1)
            findings.append(
                Finding(
                    rule_id=self.id,
                    severity=self.severity,
                    message="Shared memory declared without thread synchronization barrier",
                    location=SourceLocation(path=path, line=line, column=1),
                    metadata={"hint": "Insert __syncthreads() after populating shared memory"},
                )
            )
        return findings
