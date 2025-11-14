"""Lightweight ML triage stub to prioritize findings."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List

from ..models import Finding

try:
    from sklearn.linear_model import LogisticRegression
    import numpy as np
except Exception:  # pragma: no cover - environment without sklearn
    LogisticRegression = None
    np = None


@dataclass
class FindingScore:
    finding: Finding
    probability: float


class LogisticRegressionTriage:
    """Wraps a scikit-learn logistic regression for ranking.

    The implementation falls back to a deterministic hand-tuned scoring model
    when scikit-learn is unavailable so the CLI still produces output.
    """

    def __init__(self) -> None:
        self._model = None
        if LogisticRegression and np is not None:
            self._model = LogisticRegression()
            # Train with synthetic dataset representing CUDA dominant patterns.
            X = np.array(
                [
                    [0.8, 0.3, 0.5],  # high divergence, low coalescing
                    [0.2, 0.9, 0.9],  # optimized
                    [0.6, 0.4, 0.6],
                    [0.4, 0.7, 0.8],
                ]
            )
            y = np.array([1, 0, 1, 0])
            self._model.fit(X, y)

    def rank(self, findings: Iterable[Finding], features: Dict[str, float]) -> List[FindingScore]:
        vector = [
            features.get("thread_divergence", 0.5),
            features.get("memory_coalescing", 0.5),
            features.get("warp_efficiency", 0.5),
        ]
        scores: List[FindingScore] = []

        for finding in findings:
            if self._model is not None:
                probability = float(self._model.predict_proba([vector])[0][1])
            else:
                probability = self._heuristic_probability(finding.severity, vector)

            scores.append(FindingScore(finding=finding, probability=round(probability, 3)))
        return sorted(scores, key=lambda item: item.probability, reverse=True)

    @staticmethod
    def _heuristic_probability(severity: str, vector: List[float]) -> float:
        base = {"low": 0.2, "medium": 0.55, "high": 0.8}.get(severity, 0.5)
        divergence, coalescing, warp_eff = vector
        risk = base + (divergence * 0.3) - (coalescing * 0.2) - (warp_eff * 0.1)
        return max(0.05, min(0.99, 1 / (1 + math.exp(-4 * (risk - 0.5)))))
