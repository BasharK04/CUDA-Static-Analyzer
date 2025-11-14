from pathlib import Path

from cuda_static_analyzer.analyzer import Analyzer
from cuda_static_analyzer.models import AnalyzerResult


def write_tmp(tmp_path, content):
    path = tmp_path / "kernel.cu"
    path.write_text(content)
    return path


def test_out_of_bounds_detected(tmp_path):
    path = write_tmp(
        tmp_path,
        """
        __global__ void bad(float *input) {
            int idx = threadIdx.x;
            input[idx + threadIdx.x] = 1; // no guard
        }
        """,
    )
    analyzer = Analyzer()
    result = analyzer.scan([path])
    assert result.findings, "Expected synthetic kernel to trigger a finding"
    assert any(f.rule_id == "CUDA001" for f in result.findings)


def test_metrics_contains_features(tmp_path):
    path = write_tmp(
        tmp_path,
        """
        __global__ void good(float *input) {
            __shared__ float scratch[32];
            int idx = threadIdx.x;
            if (idx < 32) {
                scratch[idx] = input[idx];
            }
        }
        """,
    )
    analyzer = Analyzer()
    result: AnalyzerResult = analyzer.scan([path])
    assert "thread_divergence" in result.metrics
    assert result.metrics["finding_count"] >= 0
