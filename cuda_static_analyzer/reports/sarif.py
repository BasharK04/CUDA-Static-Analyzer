"""Minimal SARIF v2.1.0 output builder."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Iterable

from ..models import Finding


class SarifReportBuilder:
    version = "2.1.0"

    def build(self, findings: Iterable[Finding]) -> Dict[str, object]:
        runs = [
            {
                "tool": {
                    "driver": {
                        "name": "CUDA Security Static Analyzer",
                        "informationUri": "https://github.com/your-org/cuda-static-analyzer",
                        "rules": self._rules(findings),
                    }
                },
                "results": [self._result(finding) for finding in findings],
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "endTimeUtc": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            }
        ]

        return {"version": self.version, "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0.json", "runs": runs}

    @staticmethod
    def _rules(findings: Iterable[Finding]):
        seen = {}
        for finding in findings:
            if finding.rule_id not in seen:
                seen[finding.rule_id] = {
                    "id": finding.rule_id,
                    "defaultConfiguration": {"level": finding.severity},
                    "shortDescription": {"text": finding.message[:60]},
                }
        return list(seen.values())

    @staticmethod
    def _result(finding: Finding):
        return {
            "ruleId": finding.rule_id,
            "level": finding.severity,
            "message": {"text": finding.message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": str(finding.location.path)},
                        "region": {
                            "startLine": finding.location.line,
                            "startColumn": finding.location.column,
                        },
                    }
                }
            ],
            "properties": finding.metadata or {},
        }
