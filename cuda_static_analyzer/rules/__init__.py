"""Built-in rule implementations for the CUDA analyzer."""
from .base import Rule, RuleContext, RuleRegistry, registry
from .bounds import OutOfBoundsAccessRule
from .shared_memory import SharedMemoryRaceRule
from .synchronization import MissingSynchronizationRule

__all__ = [
    "Rule",
    "RuleContext",
    "RuleRegistry",
    "registry",
    "OutOfBoundsAccessRule",
    "MissingSynchronizationRule",
    "SharedMemoryRaceRule",
]

registry.extend(
    [
        OutOfBoundsAccessRule(),
        MissingSynchronizationRule(),
        SharedMemoryRaceRule(),
    ]
)
