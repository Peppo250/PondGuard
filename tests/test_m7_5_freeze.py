from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulation.m7_5.finalize import main

ROOT = Path(__file__).resolve().parents[1]


def test_m7_5_manifest_generation():
    assert main() == 0
    p = ROOT / "reports" / "m7_5" / "design_freeze_manifest.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["milestone"] == "M7.5"
    assert data["status"] == "DESIGN_FREEZE_CANDIDATE"
    assert len(data["artifacts"]) >= 10


def test_m7_5_freeze_candidates():
    data = json.loads((ROOT / "reports" / "m7_5" / "design_freeze_manifest.json").read_text(encoding="utf-8"))
    f = data["freeze_decisions"]
    assert f["gsm_bulk_cap_uF_candidate"] == 4700
    assert f["gsm_min_robust_cap_uF_modeled"] == 3300
    assert f["bms_continuous_rating_A_target"] >= 5.0
    assert f["aerator_fail_safe"] == "ON"
    assert f["do_pump_fail_safe"] == "OFF"


def test_m7_5_open_holds_are_explicit():
    data = json.loads((ROOT / "reports" / "m7_5" / "design_freeze_manifest.json").read_text(encoding="utf-8"))
    assert data["open_holds"]
    assert any("BMS" in x for x in data["open_holds"])
    assert any("PV" in x for x in data["open_holds"])


def test_connection_freeze_contains_final_gpio_map():
    p = ROOT / "hardware" / "freeze" / "M7_5_CONNECTION_FREEZE.txt"
    text = p.read_text(encoding="utf-8")
    for token in ["GPIO0", "GPIO1", "GPIO3", "GPIO4", "GPIO5", "GPIO6", "GPIO7", "GPIO10", "GPIO18", "GPIO19", "GPIO20", "GPIO21"]:
        assert token in text
    assert "AIN0 -> PH_SIGNAL" in text
    assert "AIN1 -> DO_SIGNAL" in text
    assert "AIN2 -> BATTERY_DIVIDER" in text
    assert "AIN3 -> PH_BIAS" in text
