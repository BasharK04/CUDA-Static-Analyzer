#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv >/dev/null 2>&1 || true
source .venv/bin/activate
pip install -r requirements.txt

python main.py scan samples/kernels --sarif-out reports/sample.sarif
