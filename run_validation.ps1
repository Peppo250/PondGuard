$ErrorActionPreference = 'Stop'
python tools/run_full_validation.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host ""
Write-Host "Evidence: reports/m7_6/full_validation_report.md"
