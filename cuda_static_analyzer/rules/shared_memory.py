"""Rule detecting suspicious shared memory access patterns indicative of races."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Iterable, List

from ..models import Finding, SourceLocation
from .base import Rule, RuleContext

_SHARED_ASSIGN = re.compile(r"__shared__\s+\w+\s+(\w+)")


class SharedMemoryRaceRule(Rule):
    id = "CUDA003"
    description = "Detects writes to shared arrays without synchronization"
    severity = "medium"

    def evaluate(self, context: RuleContext) -> Iterable[Finding]:
        findings: List[Finding] = []
        lines = context.source.splitlines()
        path = Path(context.path)

        shared_arrays = []
        for line in lines:
            match = _SHARED_ASSIGN.search(line)
            if match:
                shared_arrays.append(match.group(1))

        if not shared_arrays:
            return findings

        write_counter = Counter()
        write_locations = {}
        for idx, line in enumerate(lines, start=1):
            for name in shared_arrays:
                needle = f"{name}["
                if needle in line and "=" in line:
                    write_counter[name] += 1
                    write_locations[name] = idx

        for name, count in write_counter.items():
            if count > 1 and "__syncthreads" not in context.source:
                findings.append(
                    Finding(
                        rule_id=self.id,
                        severity=self.severity,
                        message=(
                            f"Shared memory array '{name}' is written {count} times without synchronization; "
                            "threads may race on shared state."
                        ),
                        location=SourceLocation(path=path, line=write_locations[name], column=1),
                        metadata={"writes": count},
                    )
                )
        return findings
