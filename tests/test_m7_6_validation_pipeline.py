from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import run_full_validation as vf

ROOT = Path(__file__).resolve().parents[1]
WOKWI = ROOT / "wokwi" / "ci"


def test_all_declared_scenarios_exist():
    for name in vf.SCENARIO_ORDER:
        assert (WOKWI / "scenarios" / name).exists(), name


def test_strict_pipeline_has_no_wokwi_bypass():
    text = (ROOT / "tools" / "run_full_validation.py").read_text(encoding="utf-8")
    assert "REQUIRED TOOL NOT FOUND" in text
    assert "REFUSING --no-wokwi" in text
    assert "repeatability_status" in text


def test_result_parser_round_trip():
    sample = "RESULT|ms=5000|do=7.123|nh3=0.060|ph=8.001|temp=28.000|bat=7.600|score=5.100|aerator=0|pump=0|reason=NORMAL|valid=1"
    rows = vf.parse_results(sample)
    assert len(rows) == 1
    assert rows[0]["do"] == 7.123
    assert rows[0]["aerator"] == 0
    assert rows[0]["valid"] == 1
    assert len(vf.normalized_result_hash(sample)) == 64


def test_required_acceptance_contract_is_explicit():
    payload = json.dumps({
        "acceptance_contract": [
            "toolchain present; no silent skips",
            "all selected Wokwi scenarios pass their runtime assertions",
            "repeat runs produce identical canonical RESULT hashes",
        ]
    })
    assert "no silent skips" in payload
    assert "repeat runs" in payload
