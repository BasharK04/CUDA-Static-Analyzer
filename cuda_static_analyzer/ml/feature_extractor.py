# Feature extraction utilities used by the ML triage component.
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class FeatureVector:
    thread_divergence: float
    memory_coalescing: float
    warp_efficiency: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "thread_divergence": self.thread_divergence,
            "memory_coalescing": self.memory_coalescing,
            "warp_efficiency": self.warp_efficiency,
        }


class FeatureExtractor:
    # Produces simplified feature vectors with cheap heuristics.

    def extract(self, source: str) -> FeatureVector:
        warps = source.count("warp") or 1
        shared = source.count("__shared__")
        branches = source.count("if") + source.count("?:")
        syncs = source.count("__syncthreads") or 1

        divergence = min(1.0, branches / (warps * 4))
        coalescing = max(0.1, min(1.0, (shared + syncs) / (warps + 2)))
        warp_efficiency = max(0.1, 1 - (divergence / 2))

        return FeatureVector(
            thread_divergence=round(divergence, 3),
            memory_coalescing=round(coalescing, 3),
            warp_efficiency=round(warp_efficiency, 3),
        )
