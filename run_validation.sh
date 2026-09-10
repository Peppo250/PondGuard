#!/usr/bin/env bash
set -euo pipefail
python tools/run_full_validation.py
printf '\nEvidence: reports/m7_6/full_validation_report.md\n'
