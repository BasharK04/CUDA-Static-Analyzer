"""Rule primitives and registry used by the analyzer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Protocol

from ..models import Finding


@dataclass
class RuleContext:
    """Bundle of data passed to rules when evaluating a file."""

    source: str
    path: str


class Rule(Protocol):
    """Protocol that every rule implementation must follow."""

    id: str
    description: str
    severity: str

    def evaluate(self, context: RuleContext) -> Iterable[Finding]:
        ...


class RuleRegistry:
    """Simple plugin registry used to discover rule implementations."""

    def __init__(self) -> None:
        self._rules: List[Rule] = []

    def register(self, rule: Rule) -> None:
        self._rules.append(rule)

    def extend(self, rules: Iterable[Rule]) -> None:
        for rule in rules:
            self.register(rule)

    @property
    def rules(self) -> List[Rule]:
        return list(self._rules)


registry = RuleRegistry()
"""Global registry instance used by default CLI commands."""
