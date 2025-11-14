# CUDA Security Static Analyzer

Rough draft of a CUDA kernel security scanner. It walks `.cu` files, runs a few heuristics for sketchy reads/writes, spits out SARIF, and adds a tiny ML-based priority score so noisy findings bubble up.

## Current features
- basic rule registry + three rules (bounds, missing sync, shared memory races)
- Typer CLI with Rich tables and SARIF export
- feature extraction that counts divergence / coalescing hints
- logistic regression stub (train-once synthetic data with heuristic fallback)
- sample kernels + demo script so the repo looks alive
- pytest smoke coverage for the analyzer/metrics plumbing

## checklist
- [x] Rule engine scaffolded and hot-loaded from `cuda_static_analyzer/rules`
- [x] Analyzer wiring with feature extraction, ML triage, SARIF builder
- [x] CLI (`scan`, `rules`) and Rich output
- [x] Sample kernels + `demo.sh` wiring for quick run
- [x] Pytest smoke tests + dependency pins in `requirements.txt`
- [ ] Real Clang/LLVM AST traversal instead of regex heuristics
- [ ] Shared model artifact trained on real CUDA kernels
- [ ] More rules (warp divergence, memory fence misuse, shared memory overflows)
- [ ] GitHub Action + SARIF upload for CI
- [ ] Docs showing how to build custom rules and plug in LibTooling

## Running the static analyzer
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py scan samples/kernels --sarif-out reports/sample.sarif
```
`demo.sh` does the same thing automatically.

## CLI guide
- `python main.py scan <path>` – scan a file or directory full of `.cu` files.
- `python main.py rules` – print whatever rules are currently registered.


## Notes
- swap regex heuristics for libclang AST visitors
- persist a trained classifier so CI runs don’t re-fit
- add config knobs (severity filters, suppressions, ignore files)
- Add GitHub SARIF upload + Action workflow for viewing in security tab
