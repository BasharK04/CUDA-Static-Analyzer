"""Core analyzer orchestration."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from .ml.feature_extractor import FeatureExtractor
from .ml.triage import FindingScore, LogisticRegressionTriage
from .models import AnalyzerResult, Finding
from .reports.sarif import SarifReportBuilder
from .rules import RuleRegistry, RuleContext, registry as default_registry


class Analyzer:
    """Coordinates rule execution, feature extraction, and triage."""

    def __init__(
        self,
        rule_registry: Optional[RuleRegistry] = None,
        feature_extractor: Optional[FeatureExtractor] = None,
        triage_model: Optional[LogisticRegressionTriage] = None,
    ) -> None:
        self._registry = rule_registry or default_registry
        self._feature_extractor = feature_extractor or FeatureExtractor()
        self._triage = triage_model or LogisticRegressionTriage()
        self._sarif = SarifReportBuilder()

    def scan(self, source_paths: Iterable[Path]) -> AnalyzerResult:
        paths = [Path(p) for p in source_paths]
        findings: List[Finding] = []
        for path in paths:
            findings.extend(self._evaluate_path(path))

        combined_source = "\n".join(path.read_text() for path in paths)
        features = self._feature_extractor.extract(combined_source).to_dict()
        prioritized = self._triage.rank(findings, features)

        sarif = self._sarif.build(findings)
        metrics = {
            "finding_count": len(findings),
            "avg_probability": round(
                sum(score.probability for score in prioritized) / max(len(prioritized), 1), 3
            ),
            **features,
        }
        self._annotate_findings(findings, prioritized)
        return AnalyzerResult(findings=findings, metrics=metrics, sarif=sarif)

    def _evaluate_path(self, path: Path) -> List[Finding]:
        source = path.read_text()
        context = RuleContext(source=source, path=str(path))
        file_findings: List[Finding] = []
        for rule in self._registry.rules:
            file_findings.extend(rule.evaluate(context))
        return file_findings

    @staticmethod
    def _annotate_findings(findings: Iterable[Finding], scores: List[FindingScore]) -> None:
        for score in scores:
            metadata = score.finding.metadata or {}
            metadata["exploit_probability"] = score.probability
            score.finding.metadata = metadata
