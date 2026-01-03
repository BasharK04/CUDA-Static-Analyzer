# CUDA Security Static Analyzer

A CUDA kernel security scanner that analyzes `.cu` files for common vulnerabilities, outputs results in SARIF format, and uses ML-based scoring to prioritize findings.

## Features (Not all implemented yet)
- Rule-based analysis with three rules: bounds checking, synchronization issues, and shared memory races
- Command-line interface with SARIF export
- Feature extraction for divergence and coalescing patterns
- Logistic regression model for finding prioritization
- Sample kernels and test coverage

## Setup and Usage
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py scan samples/kernels --sarif-out reports/sample.sarif
```

Alternatively, run `demo.sh` for a quick demonstration.

## CLI Commands
- `python main.py scan <path>` – Scan a file or directory containing `.cu` files
- `python main.py rules` – List all registered rules

## Checklist
- [ ] Replace regex heuristics with Clang/LLVM AST traversal
- [ ] Train model on real CUDA kernel dataset
- [ ] Additional rules for warp divergence, memory fence misuse, and shared memory overflows
- [ ] GitHub Action workflow with SARIF upload
- [ ] Configuration options for severity filtering and suppressions
- [ ] Documentation for custom rule development

## Project Structure
- `cuda_static_analyzer/rules` – Rule definitions loaded dynamically
- `samples/kernels` – Example CUDA kernels for testing
- `tests/` – pytest test suite