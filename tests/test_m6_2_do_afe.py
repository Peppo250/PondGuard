from pathlib import Path
import math
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_do_has_two_non_combined_branches():
    text = (ROOT / "hardware/do_afe/README.md").read_text()
    assert "Branch A" in text
    assert "Branch B" in text
    assert "Do not add the custom current TIA" in text or "Do not place the custom TIA" in text
    assert "DO NOT CONNECT BRANCH A AND BRANCH B IN SERIES" in (
        ROOT / "hardware/do_afe/kicad/PondGuard_M6_2_DO_AFE_notes.sch"
    ).read_text()


def test_do_configuration():
    hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text())
    do = hw["analog_inputs"]["do"]
    assert do["mcu_pin"] is None
    assert do["ads1115_channel"] == 1
    assert do["conditioner_output_min_v"] == 0.0
    assert do["conditioner_output_max_v"] == 3.0
    assert do["custom_tia_rf_ohm"] == 47000


def test_tia_outputs():
    rf = 47000.0
    assert math.isclose(1e-6 * rf, 0.047, abs_tol=1e-9)
    assert math.isclose(3e-6 * rf, 0.141, abs_tol=1e-9)


def test_feedback_pole():
    fc = 1.0 / (2.0 * math.pi * 47000.0 * 100e-9)
    assert 33.0 < fc < 35.0


def test_artifacts_exist():
    assert (ROOT / "hardware/do_afe/spice/do_tia_baseline.cir").exists()
    assert (ROOT / "hardware/do_afe/kicad/PondGuard_M6_2_DO_AFE_notes.sch").exists()
    assert (ROOT / "hardware/bom/do_afe_bom.csv").exists()
